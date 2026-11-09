#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include "DHT.h"

// ================================================================
// FARMTECH SOLUTIONS - FASE 7 (EDGE IOT + WI-FI + FLASK CLOUD)
// DHT22 + Potenciômetro de Solo + Relay Module
// ================================================================

// ===== WI-FI WOKWI =====
const char *ssid = "Wokwi-GUEST";
const char *password = "";

// ===== SERVIDOR FLASK (RENDER) =====
const char *serverURL = "https://farmtech-solutions-2-0.onrender.com/api/dados";

// ===== SENSORES =====
#define DHTPIN 15
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

#define SOIL_PIN 34
#define RELAY_PIN 26

bool estadoN = false;
bool estadoP = false;
bool estadoK = false;
bool previsaoChuva = false;

float temperatura = 0;
float umidadeAr = 0;
int umidadeSolo = 0;

unsigned long ultimoEnvio = 0;
const unsigned long intervaloEnvio = 10000;

void setup()
{
  Serial.begin(115200);
  Serial.setTimeout(50);

  digitalWrite(RELAY_PIN, LOW);
  pinMode(RELAY_PIN, OUTPUT);

  dht.begin();

  Serial.println();
  Serial.println("====================================");
  Serial.println("  FARMTECH SOLUTIONS — IOT CLOUD");
  Serial.println("====================================");
  Serial.print("Conectando ao Wi-Fi Wokwi");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(400);
    Serial.print(".");
  }

  Serial.println("\n✅ Wi-Fi conectado!");
  Serial.print("IP ESP32: ");
  Serial.println(WiFi.localIP());
  Serial.println("Comandos Serial: 0 = Sem chuva | 1 = Chuva prevista");
  Serial.println("------------------------------------");
}

void lerPrevisaoChuva()
{
  while (Serial.available() > 0)
  {
    char comando = Serial.read();
    if (comando == '0')
    {
      previsaoChuva = false;
      Serial.println(">> Previsão: SEM CHUVA (Irrigação liberada)");
    }
    else if (comando == '1')
    {
      previsaoChuva = true;
      Serial.println(">> Previsão: CHUVA (Irrigação suspensa)");
    }
  }
}

void atualizarNPK(int valor)
{
  if (valor < 720)
  {
    estadoN = false;
    estadoP = false;
    estadoK = false;
  }
  else if (valor < 1440)
  {
    estadoN = true;
    estadoP = false;
    estadoK = false;
  }
  else if (valor < 2160)
  {
    estadoN = true;
    estadoP = true;
    estadoK = false;
  }
  else
  {
    estadoN = true;
    estadoP = true;
    estadoK = true;
  }
}

void controlarBomba()
{
  bool npkCompleto = estadoN && estadoP && estadoK;

  // CORREÇÃO AGRONÔMICA: A bomba só deve ligar se o solo estiver seco (< 60%),
  // com nutrientes balanceados e SEM previsão de chuva.
  bool soloSeco = (umidadeSolo < 60);

  if (npkCompleto && !previsaoChuva && soloSeco)
  {
    digitalWrite(RELAY_PIN, HIGH);
  }
  else
  {
    digitalWrite(RELAY_PIN, LOW);
  }
}

void exibirStatus(int valorSolo)
{
  Serial.println();
  Serial.println("========== FARMTECH MONITOR ==========");
  Serial.print("Temp: ");
  Serial.print(temperatura);
  Serial.println(" C");
  Serial.print("Umidade Ar: ");
  Serial.print(umidadeAr);
  Serial.println(" %");
  Serial.print("Umidade Solo: ");
  Serial.print(umidadeSolo);
  Serial.println(" %");
  Serial.print("N: ");
  Serial.print(estadoN ? "OK " : "DEFICIT ");
  Serial.print("| P: ");
  Serial.print(estadoP ? "OK " : "DEFICIT ");
  Serial.print("| K: ");
  Serial.println(estadoK ? "OK" : "DEFICIT");
  Serial.print("Chuva: ");
  Serial.println(previsaoChuva ? "SIM" : "NAO");
  Serial.print("Bomba: ");
  Serial.println(digitalRead(RELAY_PIN) == HIGH ? "LIGADA [ON]" : "DESLIGADA [OFF]");
  Serial.println("======================================");
}

void enviarDados(float temp, float umidAr, int umidSolo)
{
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("Aviso: Wi-Fi desconectado.");
    return;
  }

  WiFiClientSecure client;
  client.setInsecure();
  client.setHandshakeTimeout(120);

  HTTPClient http;
  http.begin(client, serverURL);
  http.addHeader("Content-Type", "application/json");

  String jsonPayload = "{\"temperatura\":" + String(temp, 2) +
                       ",\"umidade_ar\":" + String(umidAr, 2) +
                       ",\"umidade_solo\":" + String(umidSolo) + "}";

  int httpCode = http.POST(jsonPayload);
  if (httpCode > 0)
  {
    Serial.print("✅ Telemetria transmitida ao Flask! Status HTTP: ");
    Serial.println(httpCode);
  }
  else
  {
    Serial.print("Aviso no envio HTTP: ");
    Serial.println(http.errorToString(httpCode));
  }
  http.end();
}

void loop()
{
  lerPrevisaoChuva();

  temperatura = dht.readTemperature();
  umidadeAr = dht.readHumidity();
  int valorSolo = analogRead(SOIL_PIN);
  umidadeSolo = map(valorSolo, 0, 4095, 0, 100);

  atualizarNPK(valorSolo);
  controlarBomba();
  exibirStatus(valorSolo);

  if (millis() - ultimoEnvio >= intervaloEnvio)
  {
    if (!isnan(temperatura) && !isnan(umidadeAr))
    {
      enviarDados(temperatura, umidadeAr, umidadeSolo);
    }
    ultimoEnvio = millis();
  }

  delay(2500);
}