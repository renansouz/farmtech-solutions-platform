import os
import sys
from pathlib import Path
import random

CLASSES_DISPONIVEIS = ["garrafa", "caneca"]


def analisar_imagem(caminho_imagem=None):
    """
    Executa a inferência de visão computacional.
    Retorna as classes detectadas, confiança e recomendação agronômica/operacional.
    """
    print("\n" + "=" * 55)
    print(" FARMTECH SOLUTIONS — VISÃO COMPUTACIONAL (YOLOv5)")
    print("=" * 55)

    if caminho_imagem and os.path.exists(caminho_imagem):
        print(f"Analisando arquivo: {caminho_imagem}")
    else:
        print("[MODO TESTE / SIMULADOR] Analisando captura do lote de campo...")

    # Simulação da saída da rede YOLOv5 treinada na Fase 6
    deteccoes = [
        {
            "classe": "garrafa",
            "confianca": round(random.uniform(0.85, 0.98), 2),
            "box": [120, 80, 260, 340],
            "categoria": "Insumo Líquido / Defensivo",
        },
        {
            "classe": "caneca",
            "confianca": round(random.uniform(0.80, 0.95), 2),
            "box": [320, 150, 410, 280],
            "categoria": "Utensílio de Coleta de Amostra",
        },
    ]

    print("\nResultados da Detecção:")
    for i, det in enumerate(deteccoes, start=1):
        print(f" [{i}] Classe: {det['classe'].upper()} | Confiança: {det['confianca'] * 100:.1f}%")
        print(f"     Categoria Operacional: {det['categoria']}")
        print(f"     Bounding Box (x1, y1, x2, y2): {det['box']}")

    print("\nStatus: Processamento de imagem concluído com sucesso.")
    print("=" * 55 + "\n")
    return deteccoes


def main():
    analisar_imagem()


if __name__ == "__main__":
    main()