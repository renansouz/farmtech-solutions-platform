"""Regras de alerta demonstrativas da FarmTech sobre dados reais do CSV IoT.

Usa os mesmos limiares exibidos na dashboard, sem prescrever doses agronômicas.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV_PADRAO = ROOT / "data" / "sensores_farmtech_v2.csv"


def ultima_leitura_csv(caminho: str | Path = CSV_PADRAO) -> dict:
    """Seleciona a maior data; não assume que a última linha física é a mais recente."""
    caminho = Path(caminho)
    with caminho.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        faltantes = {
            "timestamp", "umidade", "ph", "nitrogenio", "fosforo",
            "potassio", "chuva", "irrigacao",
        } - set(reader.fieldnames or [])
        if faltantes:
            raise ValueError(f"Colunas ausentes em {caminho.name}: {', '.join(sorted(faltantes))}")
        dados = list(reader)
    if not dados:
        raise ValueError(f"CSV sem leituras: {caminho}")
    ultima = max(dados, key=lambda r: datetime.fromisoformat(r["timestamp"]))
    leitura = {"timestamp": ultima["timestamp"]}
    for nome in ("umidade", "ph", "nitrogenio", "fosforo", "potassio"):
        leitura[nome] = float(ultima[nome])
    for nome in ("chuva", "irrigacao"):
        leitura[nome] = int(ultima[nome])
    return leitura


def avaliar_leitura(leitura: dict) -> list[dict]:
    """Gera eventos determinísticos: só emite alerta se um limiar é ultrapassado."""
    resultado = []
    umidade, ph = float(leitura["umidade"]), float(leitura["ph"])
    chuva = int(leitura["chuva"])
    origem = "Sensores IoT (telemetria da lavoura)"

    def evento(codigo: str, nivel: str, detalhes: str, acao: str) -> None:
        resultado.append({
            "codigo": codigo, "nivel": nivel, "origem": origem,
            "timestamp": str(leitura["timestamp"]),
            "detalhes": detalhes, "acao_corretiva": acao,
        })

    if umidade < 60 and chuva == 0:
        evento(
            "umidade_baixa", "Crítico",
            f"Umidade do solo em {umidade:.1f}% (referência acadêmica: 60%), sem chuva registrada.",
            "Conferir sensor, disponibilidade hídrica e necessidade de irrigação antes de acionar a bomba.",
        )
    elif umidade > 80:
        evento(
            "umidade_alta", "Atenção",
            f"Umidade do solo em {umidade:.1f}% (referência acadêmica superior: 80%).",
            "Verificar drenagem, funcionamento dos sensores e programação da irrigação.",
        )
    if not 5.5 <= ph <= 7.0:
        evento(
            "ph_fora_faixa", "Atenção",
            f"pH do solo em {ph:.2f}, fora do intervalo demonstrativo de 5,5 a 7,0.",
            "Repetir medição e solicitar análise do solo antes de definir qualquer correção química.",
        )
    referencias = {"nitrogenio": 80, "fosforo": 30, "potassio": 100}
    deficientes = [
        f"{nome.capitalize()} {float(leitura[nome]):.1f} mg/kg (< {referencia} mg/kg)"
        for nome, referencia in referencias.items()
        if float(leitura[nome]) < referencia
    ]
    if deficientes:
        evento(
            "npk_baixo", "Atenção", "; ".join(deficientes) + ".",
            "Validar amostragem e consultar responsável agronômico sobre o manejo nutricional.",
        )
    return resultado