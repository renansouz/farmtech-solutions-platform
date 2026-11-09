"""Histórico de detecções reais YOLO (Fase 6) persistido no Oracle (Fase 3)."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

try:
    from .conexao import garantir_tabelas
except ImportError:
    from conexao import garantir_tabelas


def salvar_deteccoes(conn, arquivo_imagem: str, deteccoes: list[dict], modelo: str) -> int:
    """Grava as caixas produzidas por uma inferência real, numa transação."""
    if not deteccoes:
        return 0
    execucao_id = str(uuid4())
    linhas = []
    for det in deteccoes:
        x1, y1, x2, y2 = det["box"]
        confianca = float(det["confianca"])
        if not 0 <= confianca <= 1 or x2 < x1 or y2 < y1:
            raise ValueError("Detecção inválida para persistência")
        linhas.append({
            "execucao_id": execucao_id,
            "arquivo_imagem": Path(arquivo_imagem).name[:255],
            "classe": str(det["classe"])[:80],
            "confianca": confianca,
            "x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2),
            "modelo": str(Path(modelo).name)[:255],
        })
    sql = """
    INSERT INTO DETECCOES_FARMTECH
        (execucao_id, arquivo_imagem, classe, confianca, x1, y1, x2, y2, modelo)
    VALUES
        (:execucao_id, :arquivo_imagem, :classe, :confianca,
         :x1, :y1, :x2, :y2, :modelo)
    """
    try:
        with conn.cursor() as cursor:
            cursor.executemany(sql, linhas)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return len(linhas)


def listar_deteccoes(conn, limite: int = 30) -> list[dict]:
    limite = max(1, min(100, int(limite)))
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT ts_deteccao, arquivo_imagem, classe, confianca, "
            "x1, y1, x2, y2, modelo, execucao_id "
            "FROM DETECCOES_FARMTECH ORDER BY id DESC "
            f"FETCH FIRST {limite} ROWS ONLY"
        )
        nomes = [c[0].lower() for c in cursor.description]
        return [dict(zip(nomes, row)) for row in cursor.fetchall()]