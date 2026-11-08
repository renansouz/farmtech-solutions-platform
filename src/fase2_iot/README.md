# 🔌 Módulo IoT & Irrigação de Precisão — ESP32 (Fase 2)

## 1. Visão Geral

Este módulo implementa o firmware de borda para o microcontrolador ESP32 DevKit v4, simulando a leitura contínua de parâmetros agronômicos de solo e acionamento inteligente de bomba de irrigação.

---

## 2. Pinagem Oficial do Circuito (Pinout)

| Componente              |     Tipo de Sinal      | Pino ESP32 | Função Agronômica Simulada                               |
| :---------------------- | :--------------------: | :--------: | :------------------------------------------------------- |
| **Botão Verde 1**       | Digital (INPUT_PULLUP) | `GPIO 12`  | Sensor de Nitrogênio (N) — Toggle ON/OFF                 |
| **Botão Verde 2**       | Digital (INPUT_PULLUP) | `GPIO 13`  | Sensor de Fósforo (P) — Toggle ON/OFF                    |
| **Botão Verde 3**       | Digital (INPUT_PULLUP) | `GPIO 14`  | Sensor de Potássio (K) — Toggle ON/OFF                   |
| **Sensor LDR + 10kΩ**   |    Analógico (ADC)     | `GPIO 35`  | pH do Solo (Mapeamento linear de 0.0 a 14.0)             |
| **Sensor DHT22**        |     Digital (SDA)      | `GPIO 15`  | Umidade do Solo (Faixa crítica: 60% a 80%) e Temperatura |
| **Módulo Relé (Bomba)** |    Digital (OUTPUT)    | `GPIO 26`  | Atuador da Bomba d'Água (Nível Alto = Ligada)            |

---

## 3. Lógica Agronômica de Decisão (Cultura do Café)

A bomba de irrigação (`GPIO 26`) é acionada **exclusivamente** quando todas as seguintes condições forem satisfeitas em conjunto:

```text
[ Umidade < 60% ]  AND  [ 5.5 <= pH <= 7.0 ]  AND  [ N_OK && P_OK && K_OK ]  AND  [ Previsão Chuva == 0 ]
```
