"""Ingestão REAL e idempotente de data/sensores_farmtech_v2.csv no Oracle.

    python src/fase3_database/ingestao_oracle.py --validar
    python src/fase3_database/ingestao_oracle.py --persistir

Sem credenciais, o modo padrão valida o CSV e explica que não houve persistência.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from datetime import datetime
from pathlib import Path

try:
    from .conexao import (ConfiguracaoOracleError, conectar_oracle,
                          credenciais_configuradas, garantir_tabelas)
except ImportError:  # Execução direta: python src/fase3_database/ingestao_oracle.py
    from conexao import (ConfiguracaoOracleError, conectar_oracle,
                         credenciais_configuradas, garantir_tabelas)

ROOT = Path(__file__).resolve().parents[2]
CSV_PADRAO = ROOT / "data" / "sensores_farmtech_v2.csv"
COLUNAS = ("timestamp", "umidade", "ph", "nitrogenio", "fosforo", "potassio", "chuva", "irrigacao")

MERGE_SQL = """
MERGE INTO SENSORES_FARMTECH_IOT dst
USING (SELECT :ts_leitura AS ts_leitura FROM dual) src
ON (dst.ts_leitura = src.ts_leitura)
WHEN MATCHED THEN UPDATE SET
    dst.umidade = :umidade,
    dst.ph = :ph,
    dst.nitrogenio = :nitrogenio,
    dst.fosforo = :fosforo,
    dst.potassio = :potassio,
    dst.chuva = :chuva,
    dst.irrigacao = :irrigacao
WHEN NOT MATCHED THEN INSERT
    (ts_leitura, umidade, ph, nitrogenio, fosforo, potassio, chuva, irrigacao)
VALUES
    (:ts_leitura, :umidade, :ph, :nitrogenio, :fosforo, :potassio, :chuva, :irrigacao)
"""


def ler_leituras_csv(arquivo: Path | str = CSV_PADRAO) -> list[dict]:
    """Lê o dataset da Fase 2, rejeitando colunas ausentes e valores inválidos."""
    arquivo = Path(arquivo)
    with arquivo.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        faltantes = set(COLUNAS) - set(reader.fieldnames or [])
        if faltantes:
            raise ValueError(f"CSV sem colunas obrigatórias: {', '.join(sorted(faltantes))}")
        registros: list[dict] = []
        for numero, row in enumerate(reader, start=2):
            try:
                data = datetime.fromisoformat(row["timestamp"].strip())
                if data.tzinfo is not None:
                    raise ValueError("timestamp deve estar no fuso local, sem offset")
                registro = {"ts_leitura": data}
                for campo in ("umidade", "ph", "nitrogenio", "fosforo", "potassio"):
                    valor = float(row[campo])
                    if not math.isfinite(valor):
                        raise ValueError(f"{campo} não é número finito")
                    registro[campo] = valor
                for campo in ("chuva", "irrigacao"):
                    flag = int(row[campo])
                    if flag not in (0, 1):
                        raise ValueError(f"{campo} deve ser 0 ou 1")
                    registro[campo] = flag
                registros.append(registro)
            except (TypeError, ValueError, KeyError) as exc:
                raise ValueError(f"Linha {numero} inválida em {arquivo.name}: {exc}") from exc
    if not registros:
        raise ValueError(f"CSV está vazio: {arquivo}")
    datas = [r["ts_leitura"] for r in registros]
    if len(datas) != len(set(datas)):
        raise ValueError("CSV contém timestamps duplicados; resolva antes da ingestão.")
    return registros


def importar_leituras(conn, registros: list[dict]) -> int:
    """MERGE por timestamp. Reexecutar o CSV não duplica leituras."""
    if not registros:
        return 0
    try:
        with conn.cursor() as cursor:
            cursor.executemany(MERGE_SQL, registros)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return len(registros)


def listar_ultimas_leituras(conn, limite: int = 10) -> list[dict]:
    limite = max(1, min(100, int(limite)))
    sql = f"""SELECT id, ts_leitura, umidade, ph, nitrogenio, fosforo,
                      potassio, chuva, irrigacao
               FROM SENSORES_FARMTECH_IOT
               ORDER BY ts_leitura DESC FETCH FIRST {limite} ROWS ONLY"""
    with conn.cursor() as cursor:
        cursor.execute(sql)
        nomes = [c[0].lower() for c in cursor.description]
        return [dict(zip(nomes, row)) for row in cursor.fetchall()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida CSV e importa medições no Oracle FIAP.")
    parser.add_argument("--csv", type=Path, default=CSV_PADRAO)
    parser.add_argument("--validar", action="store_true", help="Somente validar o arquivo local")
    parser.add_argument("--persistir", action="store_true", help="Exigir gravação real no Oracle")
    args = parser.parse_args(argv)
    try:
        registros = ler_leituras_csv(args.csv)
        print(f"[CSV VALIDADO] {len(registros)} leituras de {args.csv.name}")
        print(f"Período: {min(r['ts_leitura'] for r in registros)} a {max(r['ts_leitura'] for r in registros)}")
        print(f"Umidade média: {sum(r['umidade'] for r in registros) / len(registros):.2f}%")
        if args.validar:
            print("[SOMENTE VALIDAÇÃO] Nenhum registro foi enviado ao Oracle.")
            return 0
        if not credenciais_configuradas():
            if args.persistir:
                raise ConfiguracaoOracleError("Credenciais não configuradas. Ajuste o .env.")
            print("[SEM PERSISTÊNCIA] Configure ORACLE_USER e ORACLE_PASSWORD para ativar o banco.")
            return 0
        with conectar_oracle() as conn:
            criadas = garantir_tabelas(conn)
            print("Tabelas criadas:", ", ".join(criadas) if criadas else "nenhuma (já existentes)")
            total = importar_leituras(conn, registros)
            print(f"[ORACLE REAL] MERGE confirmado para {total} leituras (inserção ou atualização).")
            recentes = listar_ultimas_leituras(conn, limite=3)
            print("Últimas leituras consultadas diretamente no banco:")
            for linha in recentes:
                print(f"  {linha['ts_leitura']} | umidade={linha['umidade']} | pH={linha['ph']}")
        return 0
    except Exception as exc:
        # Não ocultar falha do banco ou afirmar que houve persistência após erro.
        print(f"[ERRO] Ingestão não concluída: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())