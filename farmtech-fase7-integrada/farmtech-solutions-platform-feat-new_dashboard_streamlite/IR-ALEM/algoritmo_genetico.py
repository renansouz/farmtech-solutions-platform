import json
import time
import random
from pathlib import Path

# Fixar semente para garantir reprodutibilidade exigida pela FIAP
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_ENTRADA = BASE_DIR / "recursos_agricolas.json"


def carregar_dados():
    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return dados["capacidade_orcamento_litros"], dados["talhoes"]


CAPACIDADE_MAXIMA, TALHOES = carregar_dados()
NUM_GENES = len(TALHOES)


def calcular_fitness(individuo):
    """Calcula o ganho total de produtividade respeitando o limite de insumo."""
    peso_total = sum(gene * TALHOES[i]["demanda_insumo_L"] for i, gene in enumerate(individuo))
    valor_total = sum(gene * TALHOES[i]["ganho_produtividade"] for i, gene in enumerate(individuo))

    if peso_total > CAPACIDADE_MAXIMA:
        return 0, peso_total  # Penalização estrita para soluções que estouram o limite
    return valor_total, peso_total


def criar_populacao(tamanho):
    return [[random.randint(0, 1) for _ in range(NUM_GENES)] for _ in range(tamanho)]


# --- ESTRATÉGIAS DE SELEÇÃO PARA COMPARAÇÃO ---
def selecao_roleta(populacao, fitnesses):
    soma_fitness = sum(fitnesses)
    if soma_fitness == 0:
        return random.choice(populacao)
    ponto = random.uniform(0, soma_fitness)
    acumulado = 0
    for ind, fit in zip(populacao, fitnesses):
        acumulado += fit
        if acumulado >= ponto:
            return ind
    return populacao[-1]


def selecao_torneio(populacao, fitnesses, k=3):
    competidores = random.sample(list(zip(populacao, fitnesses)), k)
    vencedor = max(competidores, key=lambda item: item[1])
    return vencedor[0]


# --- CROSSOVER E MUTAÇÃO ---
def crossover_ponto_simples(pai1, pai2, taxa=0.8):
    if random.random() > taxa:
        return pai1[:], pai2[:]
    ponto = random.randint(1, NUM_GENES - 1)
    filho1 = pai1[:ponto] + pai2[ponto:]
    filho2 = pai2[:ponto] + pai1[ponto:]
    return filho1, filho2


def mutacao(individuo, taxa=0.05):
    for i in range(NUM_GENES):
        if random.random() < taxa:
            individuo[i] = 1 - individuo[i]
    return individuo


def executar_algoritmo_genetico(tipo_selecao="torneio", geracoes=60, tam_populacao=30):
    """Executa o AG e retorna melhor solução, métricas e tempo."""
    inicio = time.time()
    populacao = criar_populacao(tam_populacao)
    melhor_solucao = None
    melhor_fitness = -1
    melhor_peso = 0

    for _ in range(geracoes):
        avaliacoes = [calcular_fitness(ind) for ind in populacao]
        fitnesses = [av[0] for av in avaliacoes]

        for ind, (fit, peso) in zip(populacao, avaliacoes):
            if fit > melhor_fitness:
                melhor_fitness = fit
                melhor_peso = peso
                melhor_solucao = ind[:]

        nova_populacao = []
        while len(nova_populacao) < tam_populacao:
            if tipo_selecao == "torneio":
                p1 = selecao_torneio(populacao, fitnesses)
                p2 = selecao_torneio(populacao, fitnesses)
            else:
                p1 = selecao_roleta(populacao, fitnesses)
                p2 = selecao_roleta(populacao, fitnesses)

            f1, f2 = crossover_ponto_simples(p1, p2)
            nova_populacao.append(mutacao(f1))
            if len(nova_populacao) < tam_populacao:
                nova_populacao.append(mutacao(f2))

        populacao = nova_populacao

    tempo_total = (time.time() - inicio) * 1000  # em ms
    return {
        "tipo_selecao": tipo_selecao,
        "melhor_individuo": melhor_solucao,
        "produtividade_otima": melhor_fitness,
        "consumo_insumo_L": melhor_peso,
        "tempo_ms": round(tempo_total, 2),
    }


def main():
    print("=" * 65)
    print(" FARMTECH SOLUTIONS — OTIMIZAÇÃO GENÉTICA DE RECURSOS (IR ALÉM 2)")
    print("=" * 65)
    print(f"Capacidade de Insumo Limite: {CAPACIDADE_MAXIMA} Litros")
    print(f"Total de Talhões Candidatos: {NUM_GENES}\n")

    # Comparação experimental exigida pelo enunciado
    exp_torneio = executar_algoritmo_genetico(tipo_selecao="torneio")
    exp_roleta = executar_algoritmo_genetico(tipo_selecao="roleta")

    print(f"{'Métrica / Estratégia':<30} | {'Seleção Torneio':<15} | {'Seleção Roleta':<15}")
    print("-" * 65)
    print(f"{'Produtividade Obtida':<30} | {exp_torneio['produtividade_otima']:<15} | {exp_roleta['produtividade_otima']:<15}")
    print(f"{'Consumo Insumo (L)':<30} | {exp_torneio['consumo_insumo_L']:<15} | {exp_roleta['consumo_insumo_L']:<15}")
    print(f"{'Tempo de Execução (ms)':<30} | {exp_torneio['tempo_ms']:<15} | {exp_roleta['tempo_ms']:<15}")
    print("=" * 65)

    print("\n✅ Alocação de Talhões Recomendada (Solução Ótima - Torneio):")
    for i, alocado in enumerate(exp_torneio["melhor_individuo"]):
        t = TALHOES[i]
        status = "🟢 ALOCAR INSUMO" if alocado == 1 else "⚪ NÃO ALOCAR"
        print(f"Talhão {t['id']} ({t['cultura']}): {status} | Demanda: {t['demanda_insumo_L']}L | Ganho: +{t['ganho_produtividade']}")


if __name__ == "__main__":
    main()