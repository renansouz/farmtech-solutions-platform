# FarmTech Solutions — Fase 7

## Relatório técnico de desenvolvimento, arquitetura e integração da Dashboard

**Frente:** Integrante 2 — Dashboard, visualização de dados e integração dos serviços  
**Projeto acadêmico:** FIAP — A Consolidação de um Sistema  
**Componente principal:** `src/dashboard/app.py`  
**Estado do trabalho:** versão consolidada implementada em código; interface e execução da Fase 1 vistas em capturas enviadas pelo integrante; validação sistemática e integração ponta a ponta ainda pendentes  
**Responsável:** preencher nome completo e RM para a entrega oficial  
**Referência da versão:** dashboard consolidada com cinco abas, três temas e central de serviços simplificada (08/11/2026)

> **Nota de transparência:** “implementado” significa que a funcionalidade foi programada no arquivo. Não significa que tenha sido demonstrada funcionando no ambiente completo do grupo. A compilação de sintaxe Python (`py_compile`) foi aprovada. Capturas enviadas pelo integrante mostram a interface Streamlit aberta e resultados da Fase 1, mas não equivalem a uma bateria de testes documentada. Não houve, neste ambiente, validação direta de ESP32, Oracle, YOLO real ou Amazon SNS real.

---

# 1. Visão executiva

A Fase 7 reúne os componentes construídos nas fases anteriores da FarmTech Solutions em uma única solução de gestão agrícola. O Integrante 2 desenvolve a **camada de interface**: transforma leituras e resultados técnicos em informação compreensível e oferece um ponto de acesso aos módulos do grupo.

A dashboard atual foi consolidada a partir de duas implementações: uma com seções independentes por fase, calculadora de plantio, simulador de solo e formulário AWS; outra com um explorador flexível de sensores, apresentação estruturada dos resultados e controles de execução mais seguros. A versão resultante incorpora os recursos complementares das duas.

**O que ela é hoje:** uma interface Streamlit de exploração de dados históricos, simulação de cenários, cálculo agrícola e disparo controlado de scripts.  
**O que ela ainda não é:** uma prova de comunicação contínua com o ESP32, ingestão real no Oracle, inferência neural real do YOLO e entrega confirmada de notificações AWS. Essas integrações dependem da conclusão e dos testes dos serviços da equipe.

## 1.1 Entregas contempladas

| Entrega do Integrante 2                       | Implementação atual                                   | Validação necessária                          |
| --------------------------------------------- | ----------------------------------------------------- | --------------------------------------------- |
| Evoluir a dashboard da Fase 4                 | Interface consolidada com cinco abas                  | Abrir e navegar no Streamlit                  |
| Criar botões para diferentes serviços         | Central de serviços com execução e logs               | Executar cada módulo do repositório           |
| Integrar análises de dados                    | Telemetria, resumos, recomendações e simulações       | Comparar resultados com entradas reais        |
| Exibir sensores                               | Sete variáveis com filtros e séries temporais         | Conferir CSV e gráficos no navegador          |
| Exibir dados do banco e visão computacional   | Painéis associados às saídas dos scripts              | Validar Oracle e substituir detector simulado |
| Testar comunicação entre interface e serviços | Mecanismo de chamadas e captura de erros implementado | Testes de ponta a ponta em ambiente integrado |

## 1.2 Relação com os critérios oficiais de avaliação

O enunciado atribui **3,0 pontos** ao Sistema Integrado e Dashboard Final e **3,0 pontos** ao Serviço de Alertas na AWS. Há ainda 1,0 ponto para documentação, 1,0 para organização e boas práticas, 1,0 para repositório/entrega e 1,0 para vídeo, além de 1,0 extra pelo trabalho em equipe conforme as condições da atividade.

O Integrante 2 contribui diretamente para o critério da dashboard e indiretamente para documentação, vídeo e organização. O serviço AWS é uma integração de equipe; a interface deve permitir demonstrá-lo, mas não declarar envio quando só houve simulação.

O requisito obrigatório é **acessar ou disparar os diferentes módulos numa estrutura única de projeto**, com demonstração verificável — não apenas exibir botões.

---

# 2. Arquitetura e funcionamento geral

## 2.1 Componentes

```text
Usuário no navegador
       |
       v
Dashboard Streamlit — src/dashboard/app.py
       |
       +-- CSV de telemetria --------> Pandas --> métricas, filtros e Plotly
       |
       +-- CSV da fazenda -----------> tabela, gráfico e calculadora de manejo
       |
       +-- Módulo de recomendações --> regras com os parâmetros escolhidos
       |
       +-- Central de serviços ------> subprocess --> scripts das fases
       |                                      |
       |                                      +--> stdout / stderr / código de retorno
       |                                      +--> visualização por fase + log técnico
       |
       +-- Prévia de alertas --------> formatador local de mensagem
                                              |
                                              +--> prévia de e-mail e SMS (sem envio)
```

O Streamlit executa a interface em Python e reage às alterações dos controles. O Pandas lê, organiza e filtra as tabelas. O Plotly gera gráficos interativos. O `subprocess` permite iniciar scripts das fases anteriores como processos separados. O `st.session_state` preserva os resultados de serviços enquanto a sessão da interface permanece ativa.

## 2.2 Estrutura de pastas esperada

```text
farmtech-solutions-platform/
├── data/
│   ├── sensores_farmtech_v2.csv
│   └── dados_fazenda.csv
├── docs/
│   └── assets/
│       └── logo.png                    (opcional)
├── src/
│   ├── dashboard/
│   │   └── app.py                      (este componente)
│   ├── fase1_planejamento/
│   │   ├── manejo_insumos.py
│   │   └── analise_estatistica.R      (se disponível)
│   ├── fase2_iot/
│   │   └── clima.py                    (arquivo esperado; conferir nome final)
│   ├── fase3_database/
│   │   └── ingestao_oracle.py
│   ├── fase4_ml/
│   │   └── recomendacoes.py
│   ├── fase6_vision/
│   │   └── detector.py
│   └── fase7_alerts/
│       └── mensageria_aws.py
├── requirements.txt
└── README.md
```

**Por que a estrutura importa?** O arquivo da dashboard calcula a raiz com `Path(__file__).resolve().parents[2]`. Isso permite localizar `src/` e `data/` sem depender do diretório a partir do qual o usuário iniciou o comando. Em compensação, os nomes e posições devem corresponder aos caminhos previstos. Se a equipe renomear pastas ou scripts, os atalhos precisam ser atualizados.

## 2.3 Bibliotecas e responsabilidades

| Tecnologia           | Utilização                                           | Justificativa                                                                   |
| -------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------- |
| Python               | Aplicação principal e integração dos módulos         | Linguagem utilizada nas fases do projeto                                        |
| Streamlit            | Abas, formulários, seleção, controles e mensagens    | Interface web simples sem frontend separado                                     |
| Pandas               | CSV, datas, médias, filtros e tabelas                | Manipulação consistente dos dados tabulares                                     |
| Plotly Express       | Séries históricas, barras de insumos e confiança     | Gráficos navegáveis e fáceis de interpretar                                     |
| Plotly Graph Objects | Distribuição da irrigação em gráfico circular        | Controle sobre gráfico de composição                                            |
| `pathlib`            | Caminhos do projeto                                  | Portabilidade entre ambientes                                                   |
| `subprocess`         | Execução isolada dos scripts                         | Mantém módulos separados, sem reescrevê-los                                     |
| `importlib`          | Carregamento de funções Python por caminho           | Permite usar recomendações e formatador sem reestruturar os módulos             |
| `re`                 | Extração de informações da saída textual do detector | Adaptador temporário enquanto não existe retorno estruturado                    |
| `st.session_state`   | Retenção do último resultado                         | Evita perder saídas em reprocessamentos da interface                            |
| CSS temático         | Identidade visual e contraste                        | Aparência consistente entre três temas, sem modificar as regras dos serviços    |
| HTML escapado        | Cartões e tabelas                                    | Exibição controlada de dados textuais sem tratá-los como código HTML executável |

---

# 3. O que foi implementado, função por função

## 3.1 Carregamento e validação de telemetria

O método `read_telemetry(path)` abre o CSV, verifica se todas as colunas obrigatórias existem, converte `timestamp` em data/hora e tenta transformar os demais campos em números. Registros com data inválida são descartados. O conjunto é ordenado cronologicamente.

Colunas esperadas:

| Campo        | Interpretação               | Unidade / domínio |
| ------------ | --------------------------- | ----------------- |
| `timestamp`  | Instante da medição         | Data/hora         |
| `umidade`    | Umidade do solo             | %                 |
| `ph`         | Acidez/alcalinidade do solo | pH                |
| `nitrogenio` | Nitrogênio                  | mg/kg             |
| `fosforo`    | Fósforo                     | mg/kg             |
| `potassio`   | Potássio                    | mg/kg             |
| `chuva`      | Indicador de chuva          | 0 ou 1            |
| `irrigacao`  | Estado da irrigação         | 0 ou 1            |

**Por que validar antes de plotar?** Um arquivo ausente, com coluna incorreta ou data desordenada pode produzir gráficos enganosos ou derrubar a interface. A checagem mostra erro compreensível quando falta uma coluna. Ordenar por data torna a “última leitura” a mais recente cronologicamente, e não simplesmente a última linha física do arquivo.

**Cache:** o `@st.cache_data(ttl=30)` evita releituras desnecessárias por um curto período. Isso não cria atualização em tempo real; o usuário ainda depende de o arquivo de origem receber dados novos.

**Limitação:** conversões inválidas de campos numéricos podem resultar em valores ausentes (`NaN`). Uma versão futura poderá incluir relatório de qualidade de dados e política de descarte de linhas incompletas.

## 3.2 Aba 1 — Sensores

### Indicadores de visão geral

O topo exibe quatro métricas: umidade da última leitura, pH da última leitura, estado da irrigação e quantidade de registros. Um gráfico circular apresenta a distribuição dos registros com irrigação ligada e desligada.

**Por que esses indicadores?** Permitem interpretar o estado mais recente e a frequência de acionamento da bomba antes de examinar o histórico. A distribuição é calculada a partir do dataset disponível, não de uma conexão ao atuador físico.

### Explorador de sensores

O usuário pode selecionar simultaneamente qualquer combinação das **sete variáveis**: umidade, pH, N, P, K, chuva e irrigação. As cinco variáveis contínuas principais iniciam selecionadas; chuva e irrigação também estão disponíveis.

Cada variável selecionada é apresentada em **seu próprio gráfico** com:

- Última medição válida dentro do período filtrado.
- Média aritmética no período.
- Menor e maior valor observado.
- Série temporal com data e hora.

Para chuva e irrigação, o eixo vertical usa estados 0 e 1 e o traçado é em degraus. Para outras variáveis, o Plotly gera uma curva temporal normal. Os gráficos não colocam pH, porcentagem e mg/kg no mesmo eixo.

**Motivo dessa escolha:** misturar unidades no mesmo gráfico pode induzir comparação visual sem significado físico. Gráficos separados tornam a leitura mais fiel, enquanto a seleção múltipla permite comparar visualmente padrões temporais.

### Filtro temporal

`st.date_input` recebe uma data inicial e uma final, restritas ao intervalo do arquivo. O Pandas filtra o campo `timestamp`. O número de registros filtrados é exibido. Com intervalo vazio, a aplicação apresenta aviso em vez de gráfico sem dados.

### Tabela de inspeção

A seção **“Ver dados detalhados do período”** apresenta as 100 linhas finais do período filtrado e apenas as colunas escolhidas, além da data/hora. Ela auxilia a conferência de pontos específicos e a validação dos gráficos.

### Recomendações sobre a última leitura

Se `src/fase4_ml/recomendacoes.py` existe e disponibiliza `gerar_recomendacoes_agronomicas`, a dashboard passa os seis parâmetros da leitura mais recente: umidade, pH, N, P, K e chuva. As recomendações aparecem abaixo dos gráficos.

**Distinção essencial:** o script recebido usa **regras fixas**, por exemplo limites de umidade e nutrientes. Isso não deve ser descrito como uma previsão de modelo treinado. As ações e doses mostradas são exemplos acadêmicos e exigiriam validação agronômica em uma aplicação real.

## 3.3 Aba 2 — Planejamento agrícola

Esta aba incorpora recursos que estavam na versão alternativa da dashboard do grupo.

### Calculadora de café

Entradas: comprimento da lavoura, largura, número de ruas de plantio e dosagem em mL por metro de rua.

Fórmulas:

\[
\text{Área}\_{café}\;(m^2) = \text{comprimento}\;(m) \times \text{largura}\;(m)
\]

\[
\text{Insumo}\_{café}\;(L) = \frac{\text{comprimento}\;(m)\times\text{ruas}\times\text{dosagem}\;(mL/m)}{1000}
\]

### Calculadora de soja

Entradas: raio do pivô circular e dosagem em mL por m².

\[
\text{Área}\_{soja}\;(m^2)=\pi r^2
\]

\[
\text{Insumo}_{soja}\;(L)=\frac{\text{Área}_{soja}\;(m^2)\times\text{dosagem}\;(mL/m^2)}{1000}
\]

A calculadora mostra a área e o volume estimado nos cartões de métricas. **Não grava novos registros**: sua finalidade é permitir experimentação e comparação sem alterar o cadastro oficial.

### Histórico de culturas

Se `data/dados_fazenda.csv` existir, a aba mostra a tabela cadastrada e um gráfico de barras com o volume de insumos por cultura. O arquivo recebido tem colunas `Cultura`, `Area_m2` e `Insumo_L`.

### Execução de R

O botão **“Executar script R”** procura `src/fase1_planejamento/analise_estatistica.R`. Caso o arquivo não esteja presente, o botão fica inativo. Caso `Rscript` não esteja instalado, o sistema informa a indisponibilidade. A execução possui limite de 25 segundos, apresenta status e preserva o relatório textual em uma seção recolhível.

**Por que integrar R?** A Fase 1 contempla análises em Python e R. Esse botão dá acesso ao componente analítico sem exigir que o usuário saia da plataforma. Ainda é preciso confirmar a compatibilidade do arquivo e do ambiente R do grupo.

## 3.4 Aba 3 — Simular cenários

Essa aba oferece uma análise hipotética _what-if_ para explorar como as recomendações mudam quando os valores dos sensores variam.

Controles: sliders de umidade, pH, nitrogênio, fósforo e potássio, além de opção de chuva (sim/não).

Fluxo:

1. Usuário define valores hipotéticos.
2. A dashboard procura o módulo `recomendacoes.py`.
3. Chama `gerar_recomendacoes_agronomicas(...)` com os valores escolhidos.
4. Exibe cada orientação em cartão informativo.

**Por que isso é útil?** Permite demonstrar o comportamento das regras sem esperar por uma medição crítica real. Também ajuda a conferir se as condições de chuva, umidade e NPK afetam a lógica como esperado.

**O que não foi feito:** não há treinamento, carregamento de modelo serializado ou avaliação de predição de Machine Learning nessa aba. Se a Fase 4 do grupo tiver um modelo preditivo real, o integrante responsável precisa fornecer função de inferência e artefato treinado para conexão.

## 3.5 Aba 4 — Serviços integrados

Essa é a camada de **orquestração**. Ela lista seis scripts, informa quais arquivos estão disponíveis e oferece botão de execução para cada um.

| Fase | Caminho configurado                    | Entrada/resultado esperado                                              |
| ---- | -------------------------------------- | ----------------------------------------------------------------------- |
| 1    | `fase1_planejamento/manejo_insumos.py` | Entra com `2` (relatório) e `5` (sair); apresenta dados de culturas     |
| 2    | `fase2_iot/clima.py`                   | Resumo da resposta textual do serviço de clima, se o script existir     |
| 3    | `fase3_database/ingestao_oracle.py`    | Status do script e métricas locais; verifica mensagem de conexão        |
| 4    | `fase4_ml/recomendacoes.py`            | Orientações textuais organizadas em cartões                             |
| 6    | `fase6_vision/detector.py`             | Tabela de classes e confiança, com gráfico                              |
| 7    | `fase7_alerts/mensageria_aws.py`       | Status do teste e log; separação entre simulação e publicação informada |

### Execução e captura de erros

`execute_service` inicia o script por `subprocess.run` usando o interpretador Python atual, diretório raiz como contexto e tempo limite de 25 segundos. A função captura a saída padrão (`stdout`), os erros (`stderr`) e o código de retorno. Um código diferente de zero aparece como falha, com o log disponível.

O usuário não digita comandos arbitrários: os scripts constam em uma lista definida pelo projeto. Entretanto, executar um script ainda pode produzir efeitos externos, como chamadas ao banco ou publicação AWS. O teste da Fase 7 deve ser coordenado com o responsável.

### Apresentação por fase

**Fase 1:** depois da execução, a interface lê o cadastro de culturas e mostra quantidade de culturas, área total, volume total de insumos, tabela e gráfico por cultura. É uma visualização do CSV, não o resultado de uma nova operação de cadastro.

**Fase 2:** como ainda não foi fornecido o script definitivo `clima.py`, a interface está preparada para mostrar um resumo das mensagens retornadas quando o componente estiver disponível. O formato final depende do Integrante 3.

**Fase 3:** mostra número de registros locais, umidade média e acionamentos de irrigação calculados do CSV. Também indica se o script informou conexão com Oracle. **Esses indicadores locais não provam que a tabela Oracle recebeu os dados.**

**Fase 4:** extrai as linhas de recomendações do texto do módulo e as apresenta em cartões. É uma integração provisória baseada no formato atual da saída.

**Fase 6:** identifica no texto do detector linhas com classe e confiança; monta tabela, maior confiança, total de detecções e gráfico. O arquivo `detector.py` recebido **simula** duas classes (`garrafa` e `caneca`) com valores pseudoaleatórios. Portanto, a visualização ainda não comprova reconhecimento por imagem com YOLO.

**Fase 7:** apresenta status conforme as mensagens devolvidas pelo script. O código AWS recebido possui fallback local; a dashboard evita afirmar que uma simulação foi entregue. Mesmo quando o SNS informa publicação, é necessário confirmar inscrição válida e recebimento da notificação.

### Logs técnicos e estado de sessão

Cada serviço apresenta o resultado em elementos visuais, mantendo uma opção **“Mostrar log técnico completo”** para investigar os detalhes originais. O último resultado fica em `st.session_state` durante a sessão corrente do Streamlit.

**Motivo da melhoria:** a saída bruta de terminal é útil para desenvolvedores, mas tem legibilidade limitada em demonstração. A separação entre resumo visual e log preserva rastreabilidade sem prejudicar a apresentação.

## 3.6 Aba 5 — Alertas

Esta aba permite **preparar uma prévia**, com origem, severidade, diagnóstico e ação corretiva. Ao clicar em “Pré-visualizar mensagem”, ela procura o módulo `mensageria_aws.py` e chama `formatar_mensagem_alerta(...)`. São mostrados assunto, corpo do e-mail e resumo do SMS.

**Nenhum envio ocorre por esse formulário.** Isso foi uma decisão intencional: a versão alternativa exibia sucesso mesmo quando a função de mensageria podia ter executado somente uma simulação. Agora a prévia e a publicação real são tarefas claramente distintas.

O disparo do script de mensageria continua acessível na aba Serviços; o responsável AWS deve controlar os testes e comprovar o recebimento externo.

## 3.7 Identidade visual, três temas e acessibilidade

Na evolução visual, foram implementados três temas selecionáveis na barra lateral:

| Tema         | Fundo principal | Superfície dos cartões | Texto principal | Cor de destaque |
| ------------ | --------------- | ---------------------- | --------------- | --------------- |
| Azul-marinho | `#0B1730`       | `#142642`              | `#EAF3FF`       | `#59B8FF`       |
| Escuro       | `#10151D`       | `#1C2631`              | `#F2F5F9`       | `#5CE0AC`       |
| Claro        | `#F2F7FB`       | `#FFFFFF`              | `#18304D`       | `#146BAD`       |

O seletor `st.radio` guarda a preferência visual da sessão. Um dicionário `PALETTES` centraliza as cores, aplicadas por CSS aos fundos, indicadores, barra lateral, formulários, botões e expansores. A função `themed_chart(fig)` aplica a paleta diretamente aos gráficos Plotly, incluindo fundo, fontes, eixos e grades. Isso foi necessário porque alterar apenas o template padrão do Plotly não personalizava todos os gráficos já instanciados.

### Legibilidade dos avisos

Avisos nativos do Streamlit apresentaram conflito de contraste em algumas combinações de tema. Foi criada a função `notice(message, kind)`, que gera um cartão temático com ícone, cor de borda e texto. As opções são `info`, `warning`, `success` e `error`. O conteúdo textual é escapado antes da renderização para não ser interpretado como marcação HTML.

### Tabelas e logs

O helper `themed_table(frame)` cria tabelas HTML com cabeçalho, linhas, bordas e área rolável seguindo a paleta. Sua finalidade é tornar a aparência das tabelas previsível nos três modos. Já o **log técnico usa novamente o componente nativo `st.code(..., language="text")`**, pois ele preserva a saída original do terminal (quebras de linha, espaços e colunas). A legibilidade desse bloco é mais importante do que forçar nele a mesma cor dos cartões.

### Central de serviços simplificada

O nome de cada fase aparece **uma única vez no cabeçalho expansível**. O caminho técnico do script foi removido da apresentação para evitar texto de baixo contraste e informação repetitiva. Ele continua configurado internamente na lista `SERVICES`; o usuário visualiza o nome funcional e o botão **“Executar e visualizar”**.

### Por que essas decisões?

1. O público avaliador precisa reconhecer rapidamente a finalidade de cada serviço.
2. Os modos escuros e claro devem manter contraste suficiente nos elementos essenciais.
3. Gráficos, tabelas e avisos precisam manter padrão visual coerente, sem confundir com os dados.
4. O terminal deve permanecer acessível para rastreabilidade, mas não dominar a tela principal.

**Estado de validação visual:** foram realizados ajustes iterativos a partir de capturas do navegador enviadas pelo integrante. A versão final ainda requer conferência completa em todos os temas e abas; não há medição formal de contraste WCAG nem teste automatizado de interface.

---

# 4. Comparação entre as duas versões e decisões tomadas

| Recurso identificado                   | Origem principal            | Decisão na versão consolidada                              |
| -------------------------------------- | --------------------------- | ---------------------------------------------------------- |
| Organização visual por áreas e sidebar | Código alternativo do grupo | Incorporar navegação e identificação institucional         |
| Calculadora de área e insumos          | Código alternativo do grupo | Incorporar como simulador sem gravação                     |
| Execução de R                          | Código alternativo do grupo | Incorporar com existência do arquivo e timeout             |
| Simulador agronômico                   | Código alternativo do grupo | Incorporar com identificação explícita de regras           |
| Formulário AWS                         | Código alternativo do grupo | Transformar em prévia local, sem falsa confirmação         |
| Seleção múltipla de sensores           | Nossa implementação         | Preservar integralmente                                    |
| Filtragem temporal e estatísticas      | Nossa implementação         | Preservar integralmente                                    |
| Séries separadas por unidade           | Nossa implementação         | Preservar para evitar comparação enganosa                  |
| Resultados visuais específicos         | Nossa implementação         | Preservar e manter log opcional                            |
| Tratamento de script ausente/timeout   | Nossa implementação         | Preservar controles de disponibilidade e erros             |
| Três temas com cores coordenadas       | Evolução posterior          | Adicionar seletor na barra lateral e paletas centralizadas |
| Logs alinhados                         | Ajuste após testes visuais  | Preservar saída original no componente nativo do Streamlit |
| Nome das fases                         | Ajuste após testes visuais  | Exibir título único e ocultar caminho interno do script    |

**Por que a consolidação é melhor do que substituir uma versão pela outra?** Ambas possuíam recursos complementares. A nova versão mantém a demonstração interativa do colega e a capacidade de analisar todos os sensores e executar serviços de nossa implementação, sem apagar essas funcionalidades.

---

# 5. Dependências dos outros integrantes — contratos de integração

Este é o ponto mais importante para finalizar a responsabilidade do Integrante 2. Cada integração deve fornecer **dados verificáveis**, um formato estável e um modo de distinguir sucesso, falha e simulação.

## 5.1 Integrante 1 — arquitetura e organização

**O que precisa entregar ou confirmar:**

1. Estrutura definitiva do repositório e nomes das pastas.
2. Localização de todos os scripts e datasets.
3. `requirements.txt` consolidado, incluindo Streamlit, Pandas, Plotly e dependências específicas.
4. Padronização do comando de inicialização na raiz do projeto.
5. Organização de variáveis de ambiente sem publicar senhas, tokens ou chaves.
6. Versão estável dos módulos após alterações de outros integrantes.

**O que o Integrante 2 fará depois:** ajustar caminhos que mudarem, executar o painel no repositório completo e registrar os testes. Coordenar alterações via branch/Pull Request para evitar sobrescrever a dashboard.

**Critério de aceite:** todos os botões encontram os arquivos que devem executar e o Streamlit inicia a partir da raiz sem dependência de caminhos locais do computador de um integrante.

## 5.2 Integrante 3 — IoT, ESP32 e irrigação

**O que precisa entregar:**

1. Código definitivo do ESP32 e instruções de execução/simulação.
2. Fonte de leituras consumível pela dashboard: CSV atualizado, API ou função Python.
3. Significado das variáveis e respectivas unidades.
4. Política de timestamp e atualização (intervalo, fuso horário e histórico).
5. Estado verificável da bomba e regra de irrigação.
6. Se houver múltiplos equipamentos, `sensor_id` e setor/talhão para cada leitura.
7. Arquivo ou função de clima, caso seja mantido o botão `fase2_iot/clima.py`.

**Formato sugerido para uma futura integração** (exemplo de contrato, não dados já recebidos):

```json
{
  "timestamp": "2026-11-08T14:30:00-03:00",
  "sensor_id": "esp32_cafe_01",
  "setor": "Cafe_A1",
  "umidade": 58.2,
  "ph": 6.2,
  "nitrogenio": 85.0,
  "fosforo": 32.0,
  "potassio": 110.0,
  "chuva": 0,
  "irrigacao": 1
}
```

**O que o Integrante 2 fará:** ligar a fonte real à leitura do painel, incluir seletor de dispositivo/setor se esses identificadores forem fornecidos, sinalizar idade da última medição e tratar falhas de comunicação.

**Critério de aceite:** demonstrar que uma nova leitura do ESP32 chega à fonte de dados e aparece no painel, com data/hora correta. O CSV histórico recebido **não satisfaz sozinho** esse teste.

## 5.3 Integrante 4 — Oracle e visão computacional YOLO

### Oracle: o que precisa entregar

1. Configuração de conexão sem credenciais no repositório.
2. Script que efetivamente insira ou consulte registros.
3. Nome da tabela e estrutura final das colunas.
4. Função que retorne resultados em formato tabular/JSON.
5. Tratamento de indisponibilidade e confirmação de sucesso/erro.
6. Evidência de dados consultados no banco real.

**O que o Integrante 2 fará:** acrescentar uma fonte `Oracle` à dashboard, renderizar resultados de consulta, mostrar registros e estado da conexão. Se desejado, oferecer alternância explícita entre `CSV local` e `Oracle`.

**Critério de aceite:** os mesmos registros podem ser conferidos na consulta do Oracle e na tela, sem utilizar apenas médias do CSV como suposta prova de conexão.

### YOLO: o que precisa entregar

1. Pesos treinados e instruções para carregar o modelo.
2. Função de inferência real a partir de um caminho de imagem ou bytes.
3. Classes, confidências e caixas delimitadoras em formato estruturado.
4. Imagem anotada ou caminho do resultado visual.
5. Documentação de requisitos e tempo esperado para inferência.
6. Exemplos de entrada e saída verificáveis.

**Formato sugerido** (contrato desejado, não saída atual):

```json
{
  "modo": "modelo_real",
  "imagem": "amostra_01.jpg",
  "deteccoes": [
    { "classe": "garrafa", "confianca": 0.93, "box": [10, 30, 140, 270] }
  ]
}
```

**O que o Integrante 2 fará:** permitir upload de imagem, chamar a função real, exibir imagem anotada, quantidade por classe e confiança, indicar ausência de detecções ou erro de inferência.

**Critério de aceite:** a execução usa imagem fornecida e pesos reais; resultados mudam de acordo com a imagem. A simulação atual não atende esse critério.

## 5.4 Integrante 5 — Amazon SNS e alertas

**O que precisa entregar:**

1. Tópico SNS efetivamente configurado na conta autorizada.
2. Inscrição/assinatura confirmada do destinatário.
3. Origem de alerta conectada a sensores ou resultado visual.
4. Condições de disparo e ações corretivas definidas e documentadas.
5. Função com retorno explícito, sem considerar fallback local como envio real.
6. Identificador da publicação (quando existente), erro e modo de operação.
7. Evidência de e-mail ou SMS efetivamente recebido.

**Formato sugerido para retorno** (não implementado pelo módulo recebido):

```json
{
  "status": "publicado",
  "modo": "aws_real",
  "message_id": "identificador-retornado-pelo-SNS",
  "destino_confirmado": false
}
```

**O que o Integrante 2 fará:** adaptar o painel de alertas para mostrar o retorno estruturado, impedir mensagens falsas de sucesso e permitir consulta ao histórico de alertas, se existir armazenamento apropriado.

**Critério de aceite:** os dados causam um alerta real de forma rastreável, e o grupo comprova publicação e recebimento. Não basta imprimir o texto da mensagem localmente.

---

# 6. Instalação e execução passo a passo

## 6.1 Preparar o ambiente

Abrir o terminal do VS Code na raiz do projeto:

```bash
cd /caminho/para/farmtech-solutions-platform
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Para executar a análise em R, também é necessário ter `Rscript` instalado e disponível no PATH. As integrações de Oracle, AWS e YOLO podem exigir pacotes ou configurações adicionais.

## 6.2 Iniciar

```bash
streamlit run src/dashboard/app.py
```

O Streamlit normalmente informa um endereço local como `http://localhost:8501`. Abrir o endereço no navegador. Encerrar com `Ctrl+C` no terminal.

## 6.3 Conferir a organização

Verificar que os arquivos CSV estão em `data/` e que os scripts correspondem exatamente aos caminhos da seção 3.5. Um botão desabilitado pode indicar ausência do arquivo esperado, mesmo que um serviço equivalente exista com outro nome.

## 6.4 Integrar na branch com segurança

Como houve alterações de outro integrante no mesmo componente, não sobrescrever cegamente arquivos do repositório. Primeiro:

```bash
git branch --show-current
git status
git fetch origin
```

Se houver mudanças não commitadas, salvá-las de modo seguro antes de incorporar a `main`. Com a árvore limpa, pode-se integrar `origin/main` na branch atual, resolver conflitos e testar. O arquivo consolidado deve ser revisado e incorporado na **branch de trabalho**, seguido de Pull Request para a `main`. Não enviar alterações de outros serviços como se fossem autoria do Integrante 2.

---

# 7. Testes: implementação versus comprovação

## 7.1 Verificação já realizada

| Verificação                                          | Resultado                                                                                      |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Compilação de sintaxe Python do `app.py` consolidado | **Aprovada**                                                                                   |
| Renderização efetiva do Streamlit                    | Capturas do integrante mostram abertura da interface; não executada diretamente neste ambiente |
| Execução do relatório de manejo da Fase 1            | Resultado exibido em captura; faltam comparação formal com CSV e registro do teste             |
| Funcionalidades interativas no navegador             | Testes sistemáticos ainda não registrados                                                      |
| Comunicação com ESP32, Oracle e AWS                  | Não verificada                                                                                 |
| Inferência real com YOLO                             | Não verificada                                                                                 |

## 7.2 Casos de teste exemplificados

| Caso                 | Entrada                              | Resultado esperado                                          |
| -------------------- | ------------------------------------ | ----------------------------------------------------------- |
| Área retangular      | 100 m × 50 m                         | 5.000 m²                                                    |
| Insumo café          | 100 m, 25 ruas, 100 mL/m             | 250 L                                                       |
| Área circular        | Raio de 10 m                         | Aproximadamente 314,16 m²                                   |
| Umidade e chuva      | Solo seco e chuva = 1                | Regra deve priorizar suspensão da irrigação conforme módulo |
| CSV ausente          | Renomear apenas uma cópia de teste   | Aviso de arquivo indisponível                               |
| Script ausente       | Caminho não existente                | Botão desabilitado                                          |
| Falha de subprocesso | Processo termina com código não zero | Mensagem de erro e log                                      |

---

# 8. Pendências técnicas priorizadas

## Prioridade alta — bloqueiam validação final

1. **Executar a dashboard de verdade** com as dependências instaladas e resolver problemas de renderização.
2. **Conferir os caminhos definitivos** dos módulos com o Integrante 1.
3. **Conectar a origem real dos sensores** fornecida pelo Integrante 3.
4. **Conectar consulta real ao Oracle** e inferência real ao YOLO do Integrante 4.
5. **Validar publicação e recebimento AWS** junto ao Integrante 5.
6. **Registrar evidências** das integrações em execução.

## Prioridade média — robustez e qualidade

1. Padronizar respostas dos módulos em dicionários/JSON para reduzir dependência de texto e expressões regulares.
2. Acrescentar uma seleção de fonte de dados: histórico CSV, sensores em tempo real e Oracle.
3. Acrescentar seletor de dispositivo e setor se o ESP32 fornecer `sensor_id` e `setor`.
4. Melhorar tratamento de valores numéricos ausentes no CSV e exceções de módulos importados.
5. Mostrar carimbo de data/hora da última atualização e sinalizar dados defasados.
6. Evitar execução repetida de operações externas, incluindo envios AWS, sem confirmação e registro de status.
7. Adicionar testes automatizados de funções puras e validação de contratos de dados.
8. Revisar os contrastes finais dos três temas em todas as abas, especialmente componentes nativos do Streamlit.

## Limitações que não devem ser escondidas na apresentação

- O CSV disponibilizado representa histórico local e não prova telemetria ao vivo.
- Sete variáveis medidas não significam sete ESP32 distintos.
- As recomendações atuais são **regras**, não um modelo preditivo validado.
- O `detector.py` recebido devolve **detecções simuladas**.
- O script Oracle recebido pode apenas validar o arquivo local quando não conecta ao banco.
- O módulo AWS recebido pode retornar sucesso após fallback de simulação.
- O painel pode renderizar saídas baseadas nos formatos atuais, mas precisará de ajustes se os outros integrantes alterarem esses formatos.

---

# 9. Plano de demonstração para a FIAP

Uma demonstração curta e objetiva da parte da dashboard pode seguir esta sequência:

1. Mostrar a tela inicial e explicar que os dados atuais são históricos.
2. Selecionar umidade, depois NPK, depois chuva/irrigação, demonstrando o filtro de período.
3. Mostrar como área e insumos são calculados para café/soja.
4. Ajustar umidade e chuva no simulador e observar a mudança das recomendações.
5. Abrir a central, executar a Fase 1 e mostrar os indicadores e log opcional.
6. Demonstrar Oracle, YOLO e AWS reais somente depois de validados pelos responsáveis, diferenciando qualquer modo de simulação.
7. Encerrar mostrando o papel da interface: integração, visualização e apoio à decisão.

Capturas sugeridas para o README: visão geral dos sensores, seleção múltipla, gráfico binário, calculadora, simulador, execução de serviço com saída visual, exemplo de log técnico e alertas com evidência externa quando disponível.

## 9.1 Entrega global exigida pelo enunciado

Estes itens não são todos responsabilidade exclusiva do Integrante 2, mas devem estar concluídos pelo grupo:

- [ ] Repositório GitHub **privado**, organizado segundo o modelo da coordenação.
- [ ] Repositório compartilhado com o perfil `fiap-tutoria`.
- [ ] Pastas dos serviços das Fases 1, 2, 3 e 6, dashboard da Fase 4 evoluída e serviço de alertas da Fase 7.
- [ ] README integrado com explicação do sistema, instruções para execução, nome completo e RM de todos os integrantes.
- [ ] Prints do console da AWS e comentários sobre mensageria no README.
- [ ] Vídeo principal de **até 10 minutos**, publicado como **não listado** no YouTube, demonstrando a solução integrada e os alertas.
- [ ] Link do vídeo também incluído no README.
- [ ] **Um único arquivo `.txt`** para a plataforma, contendo o link do repositório privado e o link do vídeo.
- [ ] Verificação final dos links, acessos e prazo antes da submissão.

Os desafios **Ir Além 1 (AWS Rekognition)** e **Ir Além 2 (algoritmos genéticos)** são opcionais e possuem evidências/pastas específicas. Sua eventual integração à dashboard é melhoria adicional, não substitui os requisitos obrigatórios descritos acima.

---

# 10. Texto resumido pronto para o README geral

> **Dashboard e Integração de Serviços — Integrante 2.** A equipe consolidou uma interface Streamlit que permite explorar o histórico de sete variáveis agrícolas (umidade, pH, nitrogênio, fósforo, potássio, chuva e irrigação), selecionar métricas, filtrar períodos e consultar estatísticas e gráficos temporais. A aplicação oferece calculadoras de área e insumos para café e soja, acesso à análise em R, simulador de cenários baseado nas regras agronômicas da Fase 4 e uma central que executa os módulos Python das Fases 1, 2, 3, 4, 6 e 7. Os resultados são organizados em indicadores, tabelas e gráficos, com logs técnicos preservados. A seção de alertas permite preparar mensagens antes do envio. A integração real com ESP32, Oracle, inferência YOLO e recebimento AWS depende da validação dos serviços respectivos; a dashboard não apresenta simulações como comprovação de funcionamento real.

---

# 11. Conclusão e responsabilidades finais

A contribuição do Integrante 2 já reúne a **estrutura da interface, os cálculos, a exploração dos dados, o simulador e a orquestração visual**. A arquitetura foi preparada para permitir que outros integrantes concluam seus módulos sem reescrever a interface inteira.

Ainda assim, a conclusão acadêmica desta frente requer **teste funcional e evidência de integração**, não apenas a presença dos botões. O próximo marco é executar o Streamlit no repositório atualizado, corrigir problemas observados e fechar, com cada colega, os contratos de dados descritos neste relatório.

**Responsabilidade do Integrante 2:** interface, visualização, orquestração e testes de integração.  
**Responsabilidade compartilhada:** fontes reais, credenciais, modelos, dispositivos, configurações AWS, evidências e revisão final do repositório.
