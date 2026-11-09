<div align="center">

# 🌱 FarmTech Solutions — Plataforma Integrada de Agricultura 4.0

### _Ecossistema Cognitivo para Sensoriamento IoT, Inteligência Preditiva e Governança em Nuvem_

[![FIAP](https://img.shields.io/badge/FIAP-Intelig%C3%AAncia%20Artificial-0066FF?style=for-the-badge&logo=target&logoColor=white)](https://www.fiap.com.br/)
[![Fase 7](https://img.shields.io/badge/Fase%207-Consolida%C3%A7%C3%A3o%20de%20Sistemas-00B074?style=for-the-badge)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Hub%20Executivo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![AWS](https://img.shields.io/badge/AWS-Cloud%20Messaging-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)

</div>

---

## 👨‍🎓 Integrantes da Equipe

| Nome Completo                |   RM   |
| :--------------------------- | :----: |
| **Renan de Souza Silva**     | 568958 |
| **João Vitor Justino**       | 572969 |
| **Talles Duran das Virgens** | 572772 |
| **Thiese Barros de Novaes**  | 572659 |
| **Kevin Souza Santiago**     | 573808 |

## 👩‍🏫 Corpo Docente & Coordenação

- **Coordenador Geral:** [Prof. André Godoi Chiovato](https://www.linkedin.com/in/andregodoichiovato/)
- **Corpo Docente:** Equipe de Tutoria e Avaliação de IA — FIAP

---

## 📜 Visão Geral

A **FarmTech Solutions** nasceu como uma iniciativa de engenharia para enfrentar os maiores desafios do agronegócio moderno: **eficiência hídrica, precisão na aplicação de defensivos e previsibilidade de safra**.

Ao longo de sete ciclos evolutivos, a plataforma integrou hardware de borda, esteiras analíticas de dados e modelos neurais de ponta a ponta:

```text
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                      ARQUITETURA CONSOLIDADA — FARMTECH SOLUTIONS                       │
 └────────────────────────────────────────────────────────────────────────────────────────┘

  [ CAMADA DE BORDA (IoT) ]             [ BANCO DE DADOS ]            [ CAMADA COGNITIVA ]
   ESP32 + Sensores NPK/pH                Oracle Database               Machine Learning
   DHT22 + Relé de Irrigação  ──(SQL)──▶  SENSORES_FARMTECH_IOT  ────▶   Random Forest Regressor
            │                                                                      │
            ▼                                                                      ▼
  [ TELEMETRIA CLIMÁTICA ]                                            [ VISÃO COMPUTACIONAL ]
   OpenWeather API (Chuva)                                             YOLOv5 / CNN
            │                                                          Detecção de Objetos/Campo
            │                                                                      │
            └───────────────────────────────┬──────────────────────────────────────┘
                                            ▼
                           ┌─────────────────────────────────┐
                           │   HUB CENTRAL EXECUTIVO (UI)    │
                           │       Streamlit Dashboard       │
                           │   Disparo & Controle em 1 Clique│
                           └────────────────┬────────────────┘
                                            ▼
                           ┌─────────────────────────────────┐
                           │     AWS CLOUD MESSAGING (SNS)   │
                           │  Alertas Automáticos SMS/Email  │
                           │     com Ações Agronômicas       │
                           └─────────────────────────────────┘
```

---

## 🚀 Módulos Integrados da Plataforma

1. **Gestão de Manejo e Geometria Agrícola (Fase 1):** Motor em Python para cálculo dinâmico de áreas de plantio e volumetria de insumos (Fosfato para Café e Defensivos para Soja).
2. **Sensoriamento IoT e Irrigação Inteligente (Fase 2):** Firmware ESP32 com leitura multissensorial (NPK via botões, pH simulado por LDR e umidade por DHT22), integrando previsão meteorológica da OpenWeather para suspensão de bomba em caso de chuva.
3. **Persistência Oracle & Ingestão de Histórico (Fase 3):** Carga idempotente `MERGE` de leituras CSV no banco Oracle e consulta dos dados gravados; não há sensor ao vivo conectado ao banco.
4. **Inteligência Preditiva & Recomendações (Fases 4 e 5):** Modelagem de regressão supervisionada (Scikit-Learn) prevendo umidade e rendimento (`Yield`), acoplada a um motor de regras agronômicas para tomada de decisão.
5. **Visão Computacional na Fazenda (Fase 6):** Inferência via YOLOv5 customizada para `garrafa` e `caneca`, condicionada ao fornecimento de `best.pt` treinado; sem esse arquivo, o sistema informa a ausência em vez de simular resultados.
6. **Mensageria em Nuvem & Alertas Críticos (Fase 7):** Regras sobre a última leitura do CSV, prévia local e publicação explícita de notificações em tópico Amazon SNS, com recomendações e proteção básica contra reenvio.

---

## 📁 Estrutura do Repositório (Padrão Oficial FIAP)

```text
farmtech-solutions-platform/
├── data/                    # Datasets estruturados (crop_yield, sensores_farmtech, produtos)
├── docs/                    # Manuais técnicos, arquitetura e guias para os integrantes
├── IR-ALEM/                 # Módulo Opcional: Algoritmo Genético de Otimização Agrícola
├── notebooks/               # Jupyter Notebooks de EDA, Regressão, Clusterização e YOLO
├── src/                     # Código-fonte unificado da aplicação
│   ├── fase1_planejamento/  # Módulo de cálculo de insumos e geometria
│   ├── fase2_iot/           # Firmware ESP32 e bridge de telemetria
│   ├── fase3_database/      # Conectores e ingestão Oracle DB
│   ├── fase4_ml/            # Modelos preditivos, pipelines e exportações
│   ├── fase6_vision/        # Inferência de Visão Computacional (YOLO)
│   ├── fase7_alerts/        # Serviço de mensageria AWS (SNS / Alertas SMS/Email)
│   └── dashboard/           # Hub Executivo Integrado (Streamlit Central)
├── .env.example             # Modelo seguro de variáveis de ambiente
├── .gitignore               # Configurações de exclusão de artefatos temporários
├── LICENSE                  # Licença MIT
├── README.md                # Documentação técnica e institucional
└── requirements.txt         # Dependências unificadas do sistema
```

---

---

## 🔗 Integração real adicionada na Fase 7

**Documentação completa:** [docs/INTEGRACAO_FASE7.md](docs/INTEGRACAO_FASE7.md). O documento detalha instalações, dados, comandos, fluxo entre módulos, testes, limitações e evidências necessárias.

| Serviço         | Como acioná-lo                                                         | Dependência para executar de verdade                                |
| --------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Fase 1 e Fase 2 | Dashboard → Planejamento / Serviços                                    | Scripts existentes; dados IoT do CSV são históricos                 |
| Fase 3 Oracle   | Dashboard → Serviços → Oracle                                          | `ORACLE_USER` e `ORACLE_PASSWORD` válidos no `.env`                 |
| Fase 6 YOLO     | Dashboard → **Visão computacional** → enviar imagem                    | YOLOv5 local + pesos **`best.pt` treinados**                        |
| Fase 6 → Fase 3 | Checkbox **Persistir caixas detectadas no Oracle**                     | YOLO real e Oracle conectados                                       |
| Fase 7 AWS      | Dashboard → **Alertas** → escolher CSV ou Oracle, confirmar e publicar | ARN SNS real, credenciais válidas e assinatura de e-mail confirmada |

### Testes locais sem serviços externos

```bash
python -m unittest discover -s tests -v
python src/fase3_database/ingestao_oracle.py --validar
python src/fase7_alerts/mensageria_aws.py
```

O último comando faz **somente uma prévia**; para publicar de verdade no SNS com fonte CSV, é preciso usar `--enviar` ou o botão autorizado na dashboard. O arquivo `data/sensores_farmtech_v2.csv` contém amostras antigas; o grupo precisará conectar uma fonte atualizada e agendar a rotina para um monitoramento contínuo real.

**Pendente de validação no ambiente da equipe:** credenciais Oracle, execução com o checkpoint YOLO da Fase 6, e-mail/SMS SNS após autorização e gravação de vídeo. Não disponibilizamos senhas, checkpoints nem URLs fictícias como evidência real.

## 📎 Links do Projeto

- 🎥 **Vídeo Demonstrativo Geral (YouTube):** _(Link não-listado a ser incluído)_
- 🚀 **Dashboard em Produção:** _(Link Streamlit)_
- 🧠 **Repositório Modelo da Coordenação:** [FIAP-PORTFOLIO-AI](https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI)

---

## 🧠 Decisões Técnicas & Arquitetura

- **Centralização em Hub Único:** Em vez de scripts isolados, a aplicação unifica todos os serviços em uma interface Streamlit intuitiva, capaz de disparar subprocessos no terminal ou simular a telemetria em tempo real com um clique.
- **Configuração AWS por ambiente:** A prova de conceito SNS do laboratório utiliza **`us-east-1`**; a região deve corresponder ao ARN do tópico configurado. A região, por si só, não demonstra conformidade com a LGPD.
- **Tratamento de Exceções e Resiliência:** A validação local e a prévia SNS podem funcionar sem serviços externos; falhas reais de Oracle, AWS ou YOLO são reportadas, sem afirmar sucesso simulado.

---

## 🔧 Como Executar a Plataforma

### 1. Pré-requisitos

- Python 3.10 ou superior instalado.
- Conta ou simulador configurado para AWS / Oracle (opcional para testes locais).

### 2. Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/farmtech-solutions-platform.git
cd farmtech-solutions-platform

# 2. Crie e ative o ambiente virtual
# No macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate

# No Windows:
# python -m venv .venv
# .venv\Scripts\activate

# 3. Atualize o pip e instale as dependências
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure o arquivo de variáveis de ambiente
cp .env.example .env
# (Edite o .env com suas credenciais se desejar testar a nuvem/banco)

# 5. Execute o Hub Central da FarmTech
streamlit run src/dashboard/app.py
```

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI">TEMPLATE - FIAP PORTFÓLIO AI</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
