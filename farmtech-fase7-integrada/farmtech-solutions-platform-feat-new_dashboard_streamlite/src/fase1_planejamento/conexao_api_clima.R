# ==============================================================
# FARMTECH SOLUTIONS — METEOROLOGIA VIA API OPEN-METEO (R)
# Desafio Ir Além (Fase 1)
# ==============================================================

# Coordenadas geográficas (São Paulo - Sede Agrícola)
lat <- -23.5505
lon <- -46.6333
url <- paste0(
  "https://api.open-meteo.com/v1/forecast?latitude=", lat,
  "&longitude=", lon, "&current_weather=true"
)

divisoria <- strrep("=", 45)

cat("\n", divisoria, "\n")
cat("   FARMTECH SOLUTIONS — MONITORAMENTO CLIMÁTICO (R)\n")
cat(divisoria, "\n\n")

# Consulta HTTP nativa e parsing seguro
tryCatch({
  con <- url(url, open = "r")
  linhas <- readLines(con, warn = FALSE)
  close(con)
  
  texto <- paste(linhas, collapse = "")
  
  # Extração simples sem obrigar instalação pesada de jsonlite no terminal
  temp <- sub('.*"temperature":([0-9.-]+).*', '\\1', texto)
  vento <- sub('.*"windspeed":([0-9.-]+).*', '\\1', texto)
  horario <- sub('.*"time":"([^"]+)".*', '\\1', texto)

  cat("Localização: São Paulo, Brasil\n")
  cat("Temperatura Atual: ", temp, " °C\n")
  cat("Velocidade do Vento: ", vento, " km/h\n")
  cat("Horário da Medição: ", horario, "\n\n")
  cat("✅ Telemetria climática coletada com sucesso via R!\n")
}, error = function(e) {
  cat("[AVISO] Simulação local: 22.4 °C | Vento: 12.1 km/h (API Offline ou sem conexão)\n")
})

cat(divisoria, "\n\n")