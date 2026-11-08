# 🧬 Otimização de Recursos Agrícolas com Algoritmos Genéticos (Ir Além 2)

## 1. Contexto do Problema

No agronegócio, a alocação de insumos agrícolas (fertilizantes e defensivos) e recursos hídricos é restrita por tetos orçamentários e capacidade de bombeamento.

Este módulo adapta a formulação clássica do **Problema da Mochila Binária (0/1 Knapsack Problem)** para o contexto da fazenda FarmTech Solutions:

- **Objetivo:** Maximizar a produtividade total da lavoura.
- **Restrição Rígida:** Não ultrapassar a cota de **2.500 Litros** de insumo disponível.
- **Espaço de Busca:** $2^{10} = 1.024$ combinações possíveis de talhões (Café e Soja).

---

## 2. Reprodutibilidade e Entrada de Dados

Conforme exigido pelo enunciado, os dados de entrada estão desacoplados em formato estruturado no arquivo [`recursos_agricolas.json`](./recursos_agricolas.json), garantindo reprodutibilidade experimental através da semente pseudoaleatória fixa (`seed = 42`).

---

## 3. Parametrização do Algoritmo Genético

- **Tamanho da População:** 30 indivíduos
- **Critério de Parada:** 60 gerações
- **Taxa de Crossover (Ponto Simples):** 80%
- **Taxa de Mutação Genética:** 5% por gene
- **Função Fitness:** Somatório de ganhos de produtividade, com penalização estrita ($Fitness = 0$) em caso de extrapolação da capacidade hídrica/insumo.

---

## 4. Comparação Experimental das Funções Estruturantes

Foram implementadas e comparadas duas abordagens distintas de seleção:

| Métrica / Estratégia           | Seleção por Torneio ($k=3$) | Seleção por Roleta Viciada |
| :----------------------------- | :-------------------------: | :------------------------: |
| **Produtividade Ótima Obtida** |       **521 pontos**        |       **521 pontos**       |
| **Consumo Total de Insumo**    | **2.500 L (100% da cota)**  | **2.500 L (100% da cota)** |
| **Tempo de Execução**          |          ~10.8 ms           |          ~8.3 ms           |

### Conclusão Técnica da Comparação:

Ambas as abordagens convergiram para a fronteira de Pareto ótima sem violação de restrições. A **Seleção por Torneio** apresentou maior pressão seletiva e consistência de indivíduos de alta aptidão ao longo das gerações intermediárias, sendo adotada como a solução padrão para tomada de decisão no campo.

---

## 5. Como Executar

```bash
python IR-ALEM/algoritmo_genetico.py
```
