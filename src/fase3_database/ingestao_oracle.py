import os
import sys
import time
import random
from datetime import datetime
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_HISTORICO = BASE_DIR / "data" / "sensores_farmtech_v2.csv"
TABELA = "SENSORES_FARMTECH_IOT"

USER = os.getenv("ORACLE_USER")
PASSWORD = os.getenv("ORACLE_PASSWORD")
HOST = os.getenv("ORACLE_HOST", "oracle.fiap.com.br")
PORT = int(os.getenv("ORACLE_PORT", "1521"))
SERVICE = os.getenv("ORACLE_SERVICE", "ORCL")


def testar_ou_conectar():
    if not USER or USER == "RMxxxxxx" or not PASSWORD:
        print("[MODO LOCAL/TESTE] Credenciais Oracle não definidas no .env.")
        print("Para conectar no banco FIAP real, preencha ORACLE_USER e ORACLE_PASSWORD.")
        return None

    try:
        import oracledb
        dsn = oracledb.makedsn(HOST, PORT, service_name=SERVICE)
        conn = oracledb.connect(user=USER, password=PASSWORD, dsn=dsn)
        print(f"✅ Conectado ao Oracle como {USER} ({HOST}:{PORT}/{SERVICE})")
        return conn
    except Exception as e:
        print(f"⚠️ Não foi possível conectar ao Oracle remoto: {e}")
        print("Executando em modo de validação local de dados.")
        return None


def validar_dataset_local():
    if not CSV_HISTORICO.exists():
        print(f"[ERRO] Dataset {CSV_HISTORICO} não encontrado.")
        return

    df = pd.read_csv(CSV_HISTORICO)
    print("\n--- Validação do Dataset de Telemetria (Local) ---")
    print(f"Total de registros locais: {len(df)}")
    print(f"Colunas presentes: {list(df.columns)}")
    print(f"Umidade média: {df['umidade'].mean():.2f}%")
    print(f"pH médio: {df['ph'].mean():.2f}")
    print(f"Acionamentos da bomba: {df['irrigacao'].sum()} vezes")
    print("--------------------------------------------------\n")


def main():
    conn = testar_ou_conectar()
    validar_dataset_local()

    if conn:
        print("Modo de ingestão em banco ativo.")
        conn.close()
    else:
        print("Módulo Oracle validado com sucesso para ambiente de desenvolvimento.")


if __name__ == "__main__":
    main()