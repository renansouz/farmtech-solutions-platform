from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_SENSORES = BASE_DIR / "data" / "sensores_farmtech_v2.csv"


def gerar_recomendacoes_agronomicas(umidade, ph, n, p, k, chuva):
    """Gera ações corretivas práticas baseadas nas variáveis de solo e clima."""
    acoes = []

    # 1. Recomendação hídrica
    if chuva == 1:
        acoes.append("🌧️ Chuva detectada/prevista: SUSPENDER irrigação automatizada.")
    elif umidade < 60:
        deficit = 60 - umidade
        volume = round(deficit * 0.8, 1)
        acoes.append(f"💧 Solo seco ({umidade:.1f}%): IRRIGAR IMEDIATAMENTE. Volume estimado: {volume} L/m².")
    elif umidade > 80:
        acoes.append(f"⚠️ Solo saturado ({umidade:.1f}%): NÃO IRRIGAR. Risco de asfixia radicular.")
    else:
        acoes.append(f"✅ Umidade ideal ({umidade:.1f}%): Manter monitoramento regular.")

    # 2. Correção de acidez (pH)
    if ph < 5.5:
        acoes.append(f"🧪 Solo excessivamente ácido (pH {ph:.2f}): Realizar calagem com calcário dolomítico.")
    elif ph > 7.0:
        acoes.append(f"🧪 Solo alcalino (pH {ph:.2f}): Aplicar gesso ou enxofre elementar para reduzir pH.")
    else:
        acoes.append(f"✅ pH em faixa ideal para Café (pH {ph:.2f}).")

    # 3. Nutrientes NPK
    deficiencias = []
    if n < 80:
        deficiencias.append(f"Nitrogênio ({n:.1f} mg/kg - mín 80) -> Aplicar ureia")
    if p < 30:
        deficiencias.append(f"Fósforo ({p:.1f} mg/kg - mín 30) -> Aplicar superfosfato simples")
    if k < 100:
        deficiencias.append(f"Potássio ({k:.1f} mg/kg - mín 100) -> Aplicar cloreto de potássio")

    if deficiencias:
        for d in deficiencias:
            acoes.append(f"🌿 Correção nutricional: {d}.")
    else:
        acoes.append("✅ Níveis de NPK balanceados.")

    return acoes


def main():
    print("=" * 60)
    print(" FARMTECH SOLUTIONS — MOTOR DE RECOMENDAÇÕES AGRONÔMICAS")
    print("=" * 60)

    # Teste com cenário crítico
    teste_umidade = 54.0
    teste_ph = 5.2
    teste_n = 65.0
    teste_p = 22.0
    teste_k = 90.0
    teste_chuva = 0

    print(f"Cenário de Teste: Umidade={teste_umidade}% | pH={teste_ph} | N={teste_n} | P={teste_p} | K={teste_k}\n")
    recomendacoes = gerar_recomendacoes_agronomicas(
        teste_umidade, teste_ph, teste_n, teste_p, teste_k, teste_chuva
    )

    for r in recomendacoes:
        print(f"• {r}")
    print("=" * 60)


if __name__ == "__main__":
    main()