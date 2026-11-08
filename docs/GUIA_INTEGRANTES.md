# Guia de Operação e Divisão de Tarefas — FarmTech Solutions (Fase 7)

Este documento orienta os integrantes do grupo na execução, testes e finalização da entrega da Fase 7, garantindo alinhamento técnico e divisão equilibrada de responsabilidades.

---

## 👥 Divisão de Responsabilidades

### Integrante 1 — Renan de Souza Silva (Arquitetura e Integração)

- [x] Configuração inicial do repositório no modelo oficial da coordenação FIAP.
- [x] Padronização de pastas (`data/`, `docs/`, `src/`, `notebooks/`, `IR-ALEM/`).
- [x] Migração e organização dos serviços das Fases 1 a 6 em subpastas dentro de `src/`.
- [x] Construção do Hub Central da Dashboard Streamlit (`src/dashboard/app.py`).
- [x] Implementação da mensageria AWS (`src/fase7_alerts/mensageria_aws.py`).

### Integrante 2 — Talles Duran (Dashboard e Validação de Interface)

- [ ] Executar o Dashboard localmente via `streamlit run src/dashboard/app.py`.
- [ ] Testar todos os botões da aba "Central de Execução de Serviços" e validar saídas de tela.
- [ ] Auxiliar no refinamento visual dos cards de telemetria e gráficos Plotly.

### Integrante 3 — Kevin Souza Santiago (IoT e Simulação ESP32)

- [ ] Abrir o Wokwi e colar o código atualizado de `src/fase2_iot/sketch.ino`.
- [ ] Validar o acionamento da bomba garantindo que Nitrogênio, Fósforo e Potássio estão ativos em conjunto (`estadoN && estadoP && estadoK`).
- [ ] Testar envio de `0` e `1` via Serial Monitor para simular previsão de chuva da API.

### Integrante 4 — João Vitor Justino (Visão Computacional e Banco de Dados)

- [ ] Validar execução do módulo de detecção `python src/fase6_vision/detector.py`.
- [ ] Executar o script `src/fase3_database/ingestao_oracle.py` contra o banco da FIAP e verificar criação da tabela `SENSORES_FARMTECH_IOT`.
- [ ] Revisar os scripts analíticos em `src/fase3_database/consultas.sql`.

### Integrante 5 — Thiese Barros de Novaes (Mídia, Vídeo e Entrega)

- [ ] Roteirizar a gravação de tela demonstrativa (duração máxima de 10 minutos, conforme enunciado).
- [ ] Gravar a navegação pelo Dashboard executando os botões de cada serviço e o envio de alertas AWS.
- [ ] Publicar o vídeo no YouTube como "Não Listado" e compartilhar o link com o grupo para inclusão no `README.md` e no arquivo de entrega `.txt`.

---

## 🚀 Como Executar o Projeto Localmente

1. Clonar o repositório privado:

   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd farmtech-solutions-platform
   ```

2. Criar e ativar o ambiente virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # .venv\Scripts\activate   # Windows
   ```

3. Instalar as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Executar o Dashboard:
   ```bash
   streamlit run src/dashboard/app.py
   ```
