#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include "DHT.h"

// ================================================================
// FARMTECH SOLUTIONS - FASE 7
// IoT + Simulação NPK + Irrigação Inteligente
// DHT22 + Potenciômetro + Relay Module
// ================================================================

// ===== WI-FI =====
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// ===== SERVIDOR FLASK =====
const char* serverURL =
  "https://farmtech-solutions-2-0.onrender.com/api/dados";

// ===== DHT22 =====
#define DHTPIN 15
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// ===== POTENCIÔMETRO =====
#define SOIL_PIN 34

// ===== RELÉ / BOMBA =====
#define RELAY_PIN 26

// ===== ESTADOS NPK =====
bool estadoN = false;
bool estadoP = false;
bool estadoK = false;

// ===== PREVISÃO DE CHUVA =====
bool previsaoChuva = false;

// ===== DADOS DOS SENSORES =====
float temperatura = 0;
float umidadeAr = 0;
int umidadeSolo = 0;

// ===== CONTROLE DE ENVIO =====
unsigned long ultimoEnvio = 0;
const unsigned long intervaloEnvio = 10000;

// ================================================================
// SETUP
// ================================================================

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);

  // Inicializa o relé desligado
  digitalWrite(RELAY_PIN, LOW);
  pinMode(RELAY_PIN, OUTPUT);

  dht.begin();

  Serial.println();
  Serial.println("====================================");
  Serial.println("       FARMTECH SOLUTIONS");
  Serial.println("             FASE 7");
  Serial.println("====================================");

  // Conexão Wi-Fi
  Serial.print("Conectando ao Wi-Fi");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi conectado!");
  Serial.print("IP do ESP32: ");
  Serial.println(WiFi.localIP());

  Serial.println();
  Serial.println("Sistema inicializado!");
  Serial.println("------------------------------------");
  Serial.println("SIMULACAO DE CHUVA:");
  Serial.println("Digite 0 = Sem previsao de chuva");
  Serial.println("Digite 1 = Previsao de chuva");
  Serial.println("------------------------------------");
}

// ================================================================
// LOOP PRINCIPAL
// ================================================================

void loop() {

  // 1. Recebe previsão de chuva pelo Serial Monitor
  lerPrevisaoChuva();

  // 2. Lê os sensores
  temperatura = dht.readTemperature();
  umidadeAr = dht.readHumidity();

  int valorSolo = analogRead(SOIL_PIN);

  // Converte leitura para percentual
  umidadeSolo = map(valorSolo, 0, 4095, 0, 100);

  // 3. Atualiza os estados simulados de NPK
  atualizarNPK(valorSolo);

  // 4. Verifica se a bomba deve ser acionada
  controlarBomba();

  // 5. Exibe informações
  exibirStatus(valorSolo);

  // 6. Envia dados ao Flask a cada 10 segundos
  if (millis() - ultimoEnvio >= intervaloEnvio) {

    if (!isnan(temperatura) && !isnan(umidadeAr)) {
      enviarDados(temperatura, umidadeAr, umidadeSolo);
    } else {
      Serial.println("Erro na leitura do DHT22!");
    }

    ultimoEnvio = millis();
  }

  delay(2000);
}

// ================================================================
// LEITURA DA PREVISÃO DE CHUVA
// ================================================================

void lerPrevisaoChuva() {

  while (Serial.available() > 0) {

    char comando = Serial.read();

    if (comando == '0') {
      previsaoChuva = false;
      Serial.println("Previsao atualizada: SEM CHUVA");
    }

    else if (comando == '1') {
      previsaoChuva = true;
      Serial.println("Previsao atualizada: CHUVA");
    }
  }
}

// ================================================================
// SIMULAÇÃO DOS ESTADOS NPK PELO POTENCIÔMETRO
// ================================================================
void atualizarNPK(int valor) {

  if (valor < 720) {

    estadoN = false;
    estadoP = false;
    estadoK = false;

  }

  else if (valor < 1440) {

    estadoN = true;
    estadoP = false;
    estadoK = false;

  }

  else if (valor < 2160) {

    estadoN = true;
    estadoP = true;
    estadoK = false;

  }

  else {

    estadoN = true;
    estadoP = true;
    estadoK = true;

  }
}

// ================================================================
// CONTROLE INTELIGENTE DA BOMBA
// ================================================================

void controlarBomba() {

  // Os três nutrientes precisam estar ativos
  bool npkCompleto = estadoN && estadoP && estadoK;

  // Irriga somente quando:
  // 1. NPK completo
  // 2. Não existe previsão de chuva

  if (npkCompleto && !previsaoChuva) {

    digitalWrite(RELAY_PIN, HIGH);

  } else {

    digitalWrite(RELAY_PIN, LOW);

  }
}

// ================================================================
// EXIBIÇÃO DOS DADOS
// ================================================================

void exibirStatus(int valorSolo) {

  Serial.println();
  Serial.println("========== FARMTECH MONITOR ==========");

  if (!isnan(temperatura)) {
    Serial.print("Temperatura: ");
    Serial.print(temperatura);
    Serial.println(" C");
  } else {
    Serial.println("Temperatura: Erro de leitura");
  }

  if (!isnan(umidadeAr)) {
    Serial.print("Umidade do ar: ");
    Serial.print(umidadeAr);
    Serial.println(" %");
  } else {
    Serial.println("Umidade do ar: Erro de leitura");
  }

  Serial.print("Umidade do solo: ");
  Serial.print(umidadeSolo);
  Serial.println(" %");

  Serial.print("Leitura do potenciometro: ");
  Serial.println(valorSolo);

  Serial.println("--------------------------------------");

  Serial.print("Nitrogenio: ");
  Serial.println(estadoN ? "ATIVO" : "INATIVO");

  Serial.print("Fosforo: ");
  Serial.println(estadoP ? "ATIVO" : "INATIVO");

  Serial.print("Potassio: ");
  Serial.println(estadoK ? "ATIVO" : "INATIVO");

  Serial.println("--------------------------------------");

  Serial.print("Previsao de chuva: ");
  Serial.println(previsaoChuva ? "SIM" : "NAO");

  Serial.print("Bomba de irrigacao: ");

  if (digitalRead(RELAY_PIN) == HIGH) {
    Serial.println("LIGADA");
  } else {
    Serial.println("DESLIGADA");
  }

  Serial.println("======================================");
}

// ================================================================
// ENVIO DOS DADOS PARA O FLASK / RENDER
// ================================================================

void enviarDados(float temperatura, float umidadeAr, int umidadeSolo) {

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi desconectado! Dados nao enviados.");
    return;
  }

  WiFiClientSecure client;

  client.setInsecure();
  client.setHandshakeTimeout(120);

  HTTPClient http;

  http.begin(client, serverURL);
  http.addHeader("Content-Type", "application/json");

  String jsonPayload = "{";

  jsonPayload += "\"temperatura\":" + String(temperatura, 2) + ",";
  jsonPayload += "\"umidade_ar\":" + String(umidadeAr, 2) + ",";
  jsonPayload += "\"umidade_solo\":" + String(umidadeSolo);

  jsonPayload += "}";

  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {

    Serial.print("Dados enviados ao Flask! HTTP: ");
    Serial.println(httpResponseCode);

    Serial.println("JSON enviado:");
    Serial.println(jsonPayload);

  } else {

    Serial.print("Erro no envio: ");
    Serial.println(http.errorToString(httpResponseCode));

  }

  http.end();
}