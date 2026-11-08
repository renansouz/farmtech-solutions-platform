#include "DHT.h"

// ========== PINOS ==========
#define BTN_N 12
#define BTN_P 13
#define BTN_K 14
#define LDR_PIN 35
#define DHT_PIN 15
#define RELE_PIN 26

DHT dht(DHT_PIN, DHT22);

// ========== VARIÁVEIS DE ESTADO ==========
bool estadoN = false;
bool estadoP = false;
bool estadoK = false;
bool ultimoN = HIGH;
bool ultimoP = HIGH;
bool ultimoK = HIGH;
int previsaoChuva = 0; // 0 = sem chuva, 1 = chuva prevista

void setup()
{
  Serial.begin(9600);

  pinMode(BTN_N, INPUT_PULLUP);
  pinMode(BTN_P, INPUT_PULLUP);
  pinMode(BTN_K, INPUT_PULLUP);
  pinMode(RELE_PIN, OUTPUT);
  digitalWrite(RELE_PIN, LOW);

  dht.begin();
  delay(1500);

  Serial.println("====================================");
  Serial.println(" FarmTech Solutions — IoT Edge");
  Serial.println(" Sistema de Irrigacao Inteligente");
  Serial.println("====================================");
  Serial.println("Entrada Serial: 0 = sem chuva | 1 = tem chuva");
}

// ========== TOGGLE BOTÕES ==========
void verificarBotao(int pino, bool &estado, bool &ultimo)
{
  bool leitura = digitalRead(pino);
  if (ultimo == HIGH && leitura == LOW)
  {
    estado = !estado;
    delay(50); // debounce simples
  }
  ultimo = leitura;
}

// ========== COMUNICAÇÃO SERIAL (PYTHON) ==========
void lerPrevisaoChuva()
{
  if (Serial.available() > 0)
  {
    char dado = Serial.read();
    if (dado == '0')
    {
      previsaoChuva = 0;
      Serial.println(">> Previsao atualizada: SEM CHUVA");
    }
    else if (dado == '1')
    {
      previsaoChuva = 1;
      Serial.println(">> Previsao atualizada: TEM CHUVA (Irrigacao suspensa)");
    }
  }
}

void loop()
{
  lerPrevisaoChuva();

  // Leitura botões NPK
  verificarBotao(BTN_N, estadoN, ultimoN);
  verificarBotao(BTN_P, estadoP, ultimoP);
  verificarBotao(BTN_K, estadoK, ultimoK);

  // Leitura pH (LDR mapeado de 0 a 14)
  int ldr = analogRead(LDR_PIN);
  float ph = (ldr / 4095.0) * 14.0;

  // Leitura DHT22 (Umidade do solo simulada e temperatura)
  float umidade = dht.readHumidity();
  float temperatura = dht.readTemperature();

  if (isnan(umidade) || isnan(temperatura))
  {
    Serial.println("Aviso: Falha na leitura do sensor DHT22");
    delay(2000);
    return;
  }

  // ========== REGRAS AGRONÔMICAS (CAFÉ) ==========
  bool phIdeal = (ph >= 5.5 && ph <= 7.0);
  bool umidadeBaixa = (umidade < 60.0);
  bool umidadeAlta = (umidade > 80.0);

  // CORREÇÃO: N, P e K avaliados em conjunto
  bool npkOk = (estadoN && estadoP && estadoK);

  bool ligarBomba = false;

  if (umidadeBaixa && phIdeal && npkOk && previsaoChuva == 0)
  {
    ligarBomba = true;
  }
  if (umidadeAlta || previsaoChuva == 1)
  {
    ligarBomba = false;
  }

  digitalWrite(RELE_PIN, ligarBomba ? HIGH : LOW);

  // Telemetria no Monitor Serial
  Serial.println("------------------------------------");
  Serial.print("N: ");
  Serial.print(estadoN ? "OK " : "BAIXO ");
  Serial.print("| P: ");
  Serial.print(estadoP ? "OK " : "BAIXO ");
  Serial.print("| K: ");
  Serial.println(estadoK ? "OK " : "BAIXO ");
  Serial.print("pH: ");
  Serial.print(ph, 1);
  Serial.print(" | Umidade: ");
  Serial.print(umidade, 1);
  Serial.println("%");
  Serial.print("Chuva Prevista: ");
  Serial.println(previsaoChuva == 1 ? "SIM" : "NAO");
  Serial.print("Bomba Irrigacao: ");
  Serial.println(ligarBomba ? "LIGADA [ON]" : "DESLIGADA [OFF]");
  Serial.println("====================================");

  delay(3000);
}