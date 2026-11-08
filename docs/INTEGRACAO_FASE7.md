# Integração Fase 7 — Oracle, YOLOv5, AWS SNS e Streamlit

Este guia descreve **os componentes efetivamente implementados nesta revisão** sobre a branch `feat-new_dashboard_streamlite`, preservando a dashboard já desenvolvida. Conforme o enunciado, o foco é ligar serviços das Fases 1, 2, 3 e 6 e enviar alertas de sensores com uma ação corretiva. A detecção YOLO e o sensor IoT ao vivo **não podem ser demonstrados como reais** até que os respectivos recursos estejam disponíveis.

## 1. Pré-requisitos e ambiente

Na raiz do projeto, com Python 3.10+:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run src/dashboard/app.py
```

No Linux/macOS, use `source .venv/bin/activate` e `cp .env.example .env`. A instalação de YOLOv5 e PyTorch é **adicional** à das bibliotecas básicas. Evite incluir credenciais no GitHub, mesmo que o repositório seja privado.

## 2. Fase 3 — ingestão em Oracle

Dados de origem: `data/sensores_farmtech_v2.csv`. Nome da tabela: `SENSORES_FARMTECH_IOT`. O carregamento faz `MERGE` pela coluna `ts_leitura`; reexecutar o mesmo CSV atualiza linhas, sem duplicá-las. A tabela `DETECCOES_FARMTECH` é usada para preservar os resultados da visão computacional.

Arquivos:

- `src/fase3_database/conexao.py`: credenciais em `.env`, conexão e criação das tabelas ausentes.
- `src/fase3_database/schema.sql`: DDL para criação manual (Oracle 12c+).
- `src/fase3_database/ingestao_oracle.py`: validação de CSV, `MERGE`, `COMMIT`, consulta das últimas leituras.
- `src/fase3_database/deteccoes_oracle.py`: `INSERT` e leitura do histórico de detecções.
- `src/fase3_database/consultas.sql`: consultas analíticas que já existiam.

### Comandos

```powershell
# Valida o CSV sem modificar o banco
python src/fase3_database/ingestao_oracle.py --validar

# Exige conexão ao Oracle e gravação real
python src/fase3_database/ingestao_oracle.py --persistir

# Execução sem parâmetros: grava somente quando há credenciais; caso contrário, somente valida
python src/fase3_database/ingestao_oracle.py
```

Preencha `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_HOST`, `ORACLE_PORT`, `ORACLE_SERVICE`. A conta Oracle precisa de permissão para criar tabelas (se ausentes), selecionar e inserir/atualizar. Caso as tabelas já existam com estrutura incompatível, é preciso alinhar o schema; **não** há migração destrutiva.

Os seis registros do CSV fornecido estão datados de **2025**, portanto não são leituras ao vivo do ESP32; a dashboard os identifica como histórico.

## 3. Fase 6 — inferência YOLOv5 real

O notebook `notebooks/fase6/FIAP_FASE6_ENTREGA_PRINCIPAL.ipynb` usa YOLOv5 customizada com as classes `0=garrafa` e `1=caneca`, `--img 320` e experimentos de 30 e 60 épocas. O repositório **não** contém dataset YOLO, código da biblioteca YOLOv5 nem `best.pt`.

Para reproduzir o treinamento original, recupere o dataset `dataset_yolo` e o ambiente do notebook. Para executar **inferência**, recupere o checkpoint preferencialmente do experimento que o notebook selecionou:

```text
yolov5/runs/train/fase6_60_final/weights/best.pt
```

**Alternativa:** se o checkpoint não existir e você tiver o dataset de treinamento/labels, reproduza a execução do notebook para gerar pesos novos, registrando as condições. Não use pesos genéricos `yolov5s.pt` como se fossem o modelo customizado de duas classes.

### Instalar e configurar

```powershell
# Recomendado: usar a mesma revisão/versão YOLOv5 do treinamento, se conhecida.
git clone https://github.com/ultralytics/yolov5.git yolov5
pip install -r yolov5/requirements.txt

New-Item -ItemType Directory -Force models
# Copie seu best.pt original para models/fase6_60_final_best.pt
# Em .env: YOLOV5_REPO=yolov5 e YOLO_WEIGHTS=models/fase6_60_final_best.pt
```

A biblioteca YOLOv5 pode precisar da instalação de PyTorch compatível com o sistema. Consulte a documentação do projeto para sua máquina, especialmente se usar GPU. A versão YOLOv5 mais recente pode divergir da usada no treinamento; prefira a mesma revisão quando possível.

### Comandos

```powershell
python src/fase6_vision/detector.py --imagem caminho\para\imagem.jpg
python src/fase6_vision/detector.py --imagem caminho\para\imagem.jpg --saida outputs\resultado.jpg
python src/fase6_vision/detector.py --imagem caminho\para\imagem.jpg --salvar-oracle
```

O programa chama `detect.py` real em subprocesso, lê as saídas YOLO `.txt` com confiança, converte caixas normalizadas em coordenadas de pixel, devolve JSON e fornece bytes da imagem anotada para o Streamlit. Se faltarem pesos ou YOLOv5, **gera um erro claro e não simula deteções**. A persistência Oracle é opcional e só grava caixas produzidas na inferência real.

Na dashboard, a aba **Sensores** também permite consultar as últimas leituras persistidas no Oracle, separadas dos indicadores do CSV.

Na aba **Visão computacional**: enviar imagem, definir limiar, executar, ver caixas/confiança e (se configurado) gravar/consultar histórico Oracle.

## 4. Fase 7 — AWS SNS baseado em sensores

Arquivos: `src/fase7_alerts/regras_alerta.py` e `mensageria_aws.py`.

A rotina lê a **última leitura por timestamp** do CSV IoT e avalia as regras acadêmicas documentadas no painel:

| Campo | Condição de alerta | Ação sugerida |
| --- | --- | --- |
| Umidade | menor que 60% e sem chuva | Verificar medição, água disponível e irrigação |
| Umidade | maior que 80% | Verificar drenagem e programação da bomba |
| pH | fora de 5,5–7,0 | Repetir medição e consultar análise de solo |
| N/P/K | abaixo de 80/30/100 mg/kg, respectivamente | Validar amostragem e consultar manejo nutricional |

Esses limites são **demonstrativos do projeto**, não orientações clínicas/agronômicas de uso imediato. Cada mensagem contém origem, gravidade, diagnóstico e ação corretiva. O Amazon SNS publica no tópico configurado; as assinaturas confirmadas nesse tópico determinam os destinatários (e-mail/SMS). Usar `publish` não significa que o e-mail foi entregue: verifique a caixa do destinatário e o console SNS.

```powershell
# Segurança: por padrão exibe as regras e NÃO envia nada
python src/fase7_alerts/mensageria_aws.py

# Publicação real: necessita credenciais AWS e ARN real
python src/fase7_alerts/mensageria_aws.py --enviar

# Avaliar dados da última leitura persistida no Oracle (não lê o CSV)
python src/fase7_alerts/mensageria_aws.py --fonte oracle

# Publicar alertas a partir da última leitura do Oracle real
python src/fase7_alerts/mensageria_aws.py --fonte oracle --enviar

# Sobrescreve a proteção contra repetição (somente em teste autorizado)
python src/fase7_alerts/mensageria_aws.py --enviar --forcar
```

Configure `AWS_REGION`, `AWS_SNS_TOPIC_ARN` e credenciais em `.env` ou na cadeia padrão do Boto3 (`~/.aws/credentials`, Role, variáveis do sistema). Learner Lab exige `AWS_SESSION_TOKEN` válido; os tokens expiram. O tópico Standard precisa ter inscrição de e-mail confirmada; a aplicação não cria assinatura automaticamente. A região usada na configuração precisa ser a **mesma** do ARN do tópico.

Para evitar repetições básicas, a aplicação grava uma chave hash de cada evento publicado em `data/alertas_sns_enviados.json` (**não versionado**). Este é um controle local para um único processo/instância, não um sistema distribuído. Se várias instâncias dispararem simultaneamente, use DynamoDB ou outro mecanismo de idempotência transacional.

Na dashboard, aba **Alertas**, o usuário escolhe entre **CSV histórico** e **Oracle real** para avaliar as mesmas regras. A fonte Oracle consulta a última leitura de fato gravada, ampliando a integração entre as Fases 3 e 7. Para publicar, é obrigatório confirmar explicitamente a operação e clicar no botão SNS. A área de prévia manual, desenvolvida anteriormente, permanece disponível e **não envia nada**.

### Agendamento para verificar periodicamente

A atividade pede um serviço que monitore os dados; em produção, agende a execução do comando `--enviar` com Task Scheduler ou cron **depois** de configurar credenciais AWS e uma fonte que receba leituras novas. O CSV incluído é estático; reexecutar nele não produz telemetria ao vivo.

Exemplo de cron a cada 5 minutos (Linux; ajuste caminhos e ambiente):

```cron
*/5 * * * * cd /CAMINHO/farmtech-solutions-platform && /CAMINHO/farmtech-solutions-platform/.venv/bin/python src/fase7_alerts/mensageria_aws.py --enviar >> /CAMINHO/farmtech_sns.log 2>&1
```

## 5. Verificar localmente antes da entrega

```powershell
python -m unittest discover -s tests -v
python src/fase3_database/ingestao_oracle.py --validar
python src/fase7_alerts/mensageria_aws.py
streamlit run src/dashboard/app.py
```

As verificações locais **não** validam credenciais remotas, envio real via SNS ou inferência real sem `best.pt`. Para comprovação da execução integrada, registre prints: resultado da ingestão real/consulta no Oracle, imagem anotada YOLO com checkpoint, dashboard em execução, tópico SNS com assinatura confirmada e e-mail recebido.

## 6. Entrega conforme enunciado

- Repositório **privado** no GitHub, compartilhado com `fiap-tutoria`, com o código, README, arquivos das fases e prints AWS.
- Vídeo geral **não listado**, de até **10 minutos**, demonstrando integração e alertas; link no README e no TXT de entrega.
- Um único arquivo TXT no Portal do Aluno com link do repositório e vídeo.
- Os exercícios *Ir Além 1* (Rekognition) e *Ir Além 2* (algoritmos genéticos) são **opcionais**, não necessários para validar as duas partes obrigatórias.

Os artefatos externos (Oracle da FIAP, AWS Academy, dataset/treino YOLO) não foram acessados aqui; precisam ser validados no ambiente do grupo.
