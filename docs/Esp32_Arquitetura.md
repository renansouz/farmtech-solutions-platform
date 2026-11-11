# Estrutura do ESP32 --- FarmTech Solutions

## 1. Visão geral

O ESP32 é o componente responsável pela coleta dos dados ambientais,
simulação dos indicadores de nutrientes (NPK), controle da irrigação e
comunicação com a API da FarmTech Solutions.

O firmware foi desenvolvido em C++ utilizando o framework Arduino e é
executado no ESP32. No ambiente de desenvolvimento, o projeto pode ser
compilado pelo PlatformIO e testado no simulador Wokwi.

## 2. Componentes e conexões

  ------------------------------------------------------------------------
  Componente                           Pino do ESP32 Função
  --------------------- ---------------------------- ---------------------
  Sensor DHT22                               GPIO 15 Leitura da
                                                     temperatura e umidade
                                                     do ar

  Potenciômetro                              GPIO 34 Simulação da leitura
                                                     de umidade do solo e
                                                     dos estados NPK

  Módulo relé                                GPIO 26 Acionamento da bomba
                                                     de irrigação
  ------------------------------------------------------------------------

**Observação:** no protótipo, o potenciômetro é utilizado para simular
os valores associados à umidade do solo e aos estados dos nutrientes.
Portanto, os estados NPK representam uma simulação por faixas de
leitura, não uma medição real da concentração de nitrogênio, fósforo e
potássio.

## 3. Organização funcional do firmware

O código do ESP32 está organizado em blocos funcionais:

### 3.1 Conexão Wi-Fi

-   Conecta o ESP32 à rede `Wokwi-GUEST` durante a simulação.
-   Verifica se a conexão está ativa antes de enviar os dados.
-   Tenta restabelecer a conexão caso ela seja perdida.

### 3.2 Leitura da previsão de chuva

A previsão é definida por um comando enviado pelo Monitor Serial:

  Comando   Estado
  --------- -----------------------
  `0`       Sem previsão de chuva
  `1`       Previsão de chuva

Esse indicador é utilizado pela lógica de decisão da irrigação.

### 3.3 Leitura dos sensores ambientais

O firmware coleta:

-   **Temperatura:** obtida pelo sensor DHT22, em graus Celsius.
-   **Umidade do ar:** obtida pelo sensor DHT22, em porcentagem.
-   **Umidade do solo:** estimada a partir da leitura analógica do
    potenciômetro, convertida para uma escala de 0 a 100%.

A leitura analógica do potenciômetro utiliza o intervalo de 0 a 4095.

### 3.4 Simulação dos indicadores NPK

A leitura analógica do potenciômetro determina os estados simulados de
nitrogênio (N), fósforo (P) e potássio (K).

    Leitura analógica Nitrogênio   Fósforo   Potássio
  ------------------- ------------ --------- ----------
        Menor que 720 Inativo      Inativo   Inativo
        De 720 a 1439 Ativo        Inativo   Inativo
       De 1440 a 2159 Ativo        Ativo     Inativo
     A partir de 2160 Ativo        Ativo     Ativo

Os indicadores são armazenados em variáveis booleanas no firmware.

### 3.5 Controle automático da irrigação

A decisão de acionamento da bomba considera os três estados NPK e a
previsão de chuva.

A bomba é ligada somente quando:

-   Nitrogênio está ativo;
-   Fósforo está ativo;
-   Potássio está ativo;
-   Não há previsão de chuva.

Em termos lógicos:

``` cpp
bombaIrrigacao = estadoN &&
                 estadoP &&
                 estadoK &&
                 !previsaoChuva;
```

O resultado controla o pino GPIO 26, conectado ao relé:

-   `HIGH`: bomba ligada;
-   `LOW`: bomba desligada.

Essa lógica corresponde à regra implementada no protótipo.

## 4. Comunicação com a API

Após atualizar as leituras e os estados, o ESP32 envia os dados para a
API Flask por meio de uma requisição HTTP `POST`, utilizando o formato
JSON.

**Endpoint:**

``` text
https://farmtech-solutions-2-0.onrender.com/api/dados
```

**Estrutura do JSON enviado:**

``` json
{
  "temperatura": 35.20,
  "umidade_ar": 67.00,
  "umidade_solo": 67,
  "estado_n": true,
  "estado_p": true,
  "estado_k": false,
  "previsao_chuva": false,
  "bomba_irrigacao": false
}
```

Os campos ambientais preservam o contrato de integração original. Os
demais campos complementam o registro com os estados NPK e as
informações da automação.

Quando a API recebe e processa a requisição com sucesso, retorna o
código HTTP `201`.

## 5. Ciclo de execução

O firmware utiliza dois intervalos principais:

  Processo                                    Intervalo
  --------------------------------------- -------------
  Atualização dos sensores, NPK e bomba      5 segundos
  Envio dos dados para a API                10 segundos

O ciclo principal executa as seguintes etapas:

1.  Verifica se existe um novo comando de previsão de chuva no Monitor
    Serial.
2.  Atualiza as leituras ambientais.
3.  Calcula os estados simulados de NPK.
4.  Aplica a regra de acionamento da bomba.
5.  Exibe as informações no Monitor Serial.
6.  Envia os dados atualizados à API no intervalo definido.

## 6. Monitoramento e validação

O Monitor Serial permite acompanhar:

-   Temperatura;
-   Umidade do ar;
-   Umidade do solo;
-   Leitura analógica do potenciômetro;
-   Estados de nitrogênio, fósforo e potássio;
-   Previsão de chuva;
-   Estado da bomba;
-   JSON enviado e código de resposta HTTP.

A validação da integração deve considerar tanto os valores exibidos no
Monitor Serial quanto o conteúdo do JSON enviado. O retorno HTTP `201`,
isoladamente, confirma que a requisição foi aceita pela API, mas não
garante que todos os campos esperados estejam presentes no corpo
enviado.

## 7. Resumo da arquitetura

``` text
              ESP32
                |
       +--------+---------+
       |                  |
     DHT22           Potenciômetro
       |                  |
 Temperatura e       Umidade do solo
 umidade do ar       e simulação NPK
       |                  |
       +--------+---------+
                |
        Lógica de irrigação
                |
         Módulo relé
                |
         Bomba de água
                |
        Comunicação Wi-Fi
                |
           API Flask
                |
          Banco Oracle
```

## 8. Considerações do protótipo

-   O DHT22 fornece as leituras ambientais de temperatura e umidade do
    ar.
-   O potenciômetro é utilizado como recurso de simulação para a umidade
    do solo e para os estados NPK.
-   A previsão de chuva é informada manualmente pelo Monitor Serial
    nesta versão.
-   O acionamento da bomba é determinado pela regra lógica implementada
    no ESP32.
-   A comunicação com a API utiliza Wi-Fi e requisições HTTP com
    conteúdo JSON.
-   A arquitetura permite evoluir posteriormente para sensores
    específicos de nutrientes, umidade do solo e previsão meteorológica
    integrada.
