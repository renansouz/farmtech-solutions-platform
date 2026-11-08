"""Monitoramento do CSV IoT + alertas AWS SNS usando eventos verificados.

Modo seguro (não envia): python src/fase7_alerts/mensageria_aws.py
Publicação REAL:        python src/fase7_alerts/mensageria_aws.py --enviar
Reenvio autorizado:     python src/fase7_alerts/mensageria_aws.py --enviar --forcar

O SNS utiliza as assinaturas já confirmadas no tópico (ex.: e-mail); publish não
comprova entrega no destinatário. Não há fallback que simule sucesso.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.fase7_alerts.regras_alerta import CSV_PADRAO, avaliar_leitura, ultima_leitura_csv

load_dotenv(ROOT / ".env")
LEDGER_PADRAO = ROOT / "data" / "alertas_sns_enviados.json"


def formatar_mensagem_alerta(origem: str, nivel: str, detalhes: str, acao_corretiva: str):
    """Mantém a interface do formulário de prévia da dashboard existente."""
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    assunto = f"[FarmTech {nivel.upper()}] Alerta da lavoura"[:100]
    corpo = (
        "FARMTECH SOLUTIONS — ALERTA AGRÍCOLA\n"
        f"Emitido em: {timestamp}\n"
        f"Origem: {origem}\n"
        f"Severidade: {nivel.upper()}\n\n"
        f"DIAGNÓSTICO:\n{detalhes}\n\n"
        f"AÇÃO CORRETIVA SUGERIDA:\n{acao_corretiva}\n\n"
        "Aviso: limiares acadêmicos; confirme condições de campo antes de agir.\n"
    )
    sms = f"FarmTech [{nivel.upper()}] {detalhes} Ação: {acao_corretiva}"[:160]
    return assunto, corpo, sms


def enviar_alerta_aws(origem: str, nivel: str, detalhes: str, acao_corretiva: str, *,
                      publicar: bool = False) -> dict:
    """Publica de fato somente com autorização explícita publicar=True.

    Retorna {'publicado':bool, 'message_id':...}; simulação nunca indica envio.
    """
    assunto, corpo, sms = formatar_mensagem_alerta(origem, nivel, detalhes, acao_corretiva)
    if not publicar:
        return {"publicado": False, "modo": "prévia local", "assunto": assunto,
                "corpo": corpo, "sms_preview": sms}

    topico = os.getenv("AWS_SNS_TOPIC_ARN", "").strip()
    regiao = os.getenv("AWS_REGION", "us-east-1").strip()
    if not topico or "123456789012" in topico or not topico.startswith(f"arn:aws:sns:{regiao}:"):
        raise ValueError("Configure AWS_SNS_TOPIC_ARN real na região AWS_REGION do .env.")
    for env_var, placeholder in (("AWS_ACCESS_KEY_ID", "sua_access_key"),
                                 ("AWS_SECRET_ACCESS_KEY", "sua_secret_key"),
                                 ("AWS_SESSION_TOKEN", "seu_token_se_usar_learner_lab")):
        if os.getenv(env_var) == placeholder:
            raise ValueError(f"Substitua o placeholder {env_var} do .env (ou remova para usar IAM Role).")

    import boto3
    # Provider padrão usa env, ~/.aws/credentials ou IAM Role/SSO; suporta token temporário Learner Lab.
    sns = boto3.Session(region_name=regiao).client("sns")
    resposta = sns.publish(TopicArn=topico, Subject=assunto, Message=corpo)
    message_id = resposta.get("MessageId")
    if not message_id:
        raise RuntimeError("SNS não retornou MessageId: publicação sem confirmação")
    return {"publicado": True, "modo": "SNS", "message_id": message_id,
            "topico": topico, "assunto": assunto}


def chave_alerta(evento: dict) -> str:
    dados = f"{evento['timestamp']}|{evento['codigo']}|{evento['detalhes']}"
    return hashlib.sha256(dados.encode("utf-8")).hexdigest()


def carregar_historico(caminho: Path = LEDGER_PADRAO) -> dict:
    if caminho.exists():
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        if not isinstance(dados, dict):
            raise ValueError("Histórico de alertas possui formato inválido")
        return dados
    return {}


def salvar_historico(caminho: Path, historico: dict) -> None:
    """Escrita atômica após cada publicação bem-sucedida; evita reenvios básicos."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_name(caminho.name + ".tmp")
    temporario.write_text(json.dumps(historico, ensure_ascii=False, indent=2), encoding="utf-8")
    temporario.replace(caminho)


def processar_leitura(leitura: dict, *, enviar: bool = False, forcar: bool = False,
                      historico_path: Path = LEDGER_PADRAO) -> list[dict]:
    """Avalia eventos; publica apenas os ainda não enviados, salvo --forcar."""
    eventos = avaliar_leitura(leitura)
    historico = carregar_historico(historico_path) if enviar else {}
    resultados = []
    for evento in eventos:
        chave = chave_alerta(evento)
        if enviar and chave in historico and not forcar:
            resultados.append({"evento": evento, "status": "já publicado", "chave": chave,
                               "message_id": historico[chave]["message_id"]})
            continue
        resposta = enviar_alerta_aws(
            evento["origem"], evento["nivel"], evento["detalhes"],
            evento["acao_corretiva"], publicar=enviar,
        )
        if enviar:
            historico[chave] = {"message_id": resposta["message_id"],
                                "registrado_em": datetime.now().isoformat(timespec="seconds")}
            salvar_historico(historico_path, historico)
            status = "publicado SNS"
        else:
            status = "prévia; nada enviado"
        resultados.append({"evento": evento, "status": status, "chave": chave,
                           "message_id": resposta.get("message_id")})
    return resultados


def ultima_leitura_oracle() -> dict:
    """Alternativa real à fonte CSV: usa o registro mais recente persistido no Oracle."""
    from src.fase3_database.conexao import conectar_oracle
    from src.fase3_database.ingestao_oracle import listar_ultimas_leituras
    with conectar_oracle() as conn:
        linhas = listar_ultimas_leituras(conn, limite=1)
    if not linhas:
        raise ValueError("Nenhuma leitura encontrada na tabela SENSORES_FARMTECH_IOT")
    linha = linhas[0]
    return {
        "timestamp": linha["ts_leitura"].isoformat(sep=" ", timespec="seconds"),
        **{nome: float(linha[nome]) for nome in
           ("umidade", "ph", "nitrogenio", "fosforo", "potassio")},
        "chuva": int(linha["chuva"]), "irrigacao": int(linha["irrigacao"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Avalia sensores e notifica por AWS SNS")
    parser.add_argument("--csv", type=Path, default=CSV_PADRAO)
    parser.add_argument("--fonte", choices=("csv", "oracle"), default="csv",
                        help="Fonte de telemetria a avaliar (CSV histórico ou Oracle real)")
    parser.add_argument("--enviar", action="store_true", help="Publicar de verdade no SNS")
    parser.add_argument("--forcar", action="store_true", help="Reenviar eventos já publicados")
    args = parser.parse_args(argv)
    try:
        leitura = ultima_leitura_oracle() if args.fonte == "oracle" else ultima_leitura_csv(args.csv)
        print(f"[FONTE {args.fonte.upper()}] Última leitura: {leitura['timestamp']}")
        resultados = processar_leitura(leitura, enviar=args.enviar, forcar=args.forcar)
        if not resultados:
            print("[SEM ALERTAS] Nenhum limiar acadêmico foi ultrapassado na última leitura.")
            return 0
        for item in resultados:
            evento = item["evento"]
            print(f"\n[{item['status'].upper()}] {evento['codigo']} ({evento['nivel']})")
            print(f"Diagnóstico: {evento['detalhes']}")
            print(f"Ação corretiva: {evento['acao_corretiva']}")
            if item["message_id"]:
                print(f"SNS MessageId: {item['message_id']}")
        if not args.enviar:
            print("\n[SEGURANÇA] Prévia apenas. Use --enviar para publicação real no AWS SNS.")
        else:
            print("\nPublicação SNS registrada; verifique assinaturas e entrega no console AWS/e-mail.")
        return 0
    except Exception as exc:
        print(f"[ERRO] Serviço AWS não concluído: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
