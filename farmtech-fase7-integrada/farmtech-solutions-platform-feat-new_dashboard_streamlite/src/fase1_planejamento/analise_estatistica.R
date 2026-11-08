# ==============================================================
# FARMTECH SOLUTIONS — ANÁLISE ESTATÍSTICA DESCRITIVA (FASE 1)
# Integração: Lê diretamente o arquivo gerado pelo script Python
# ==============================================================

# 1. Localização dinâmica do CSV na pasta data/
caminho_csv <- file.path("data", "dados_fazenda.csv")

if (!file.exists(caminho_csv)) {
  # Fallback caso seja executado de dentro de src/fase1_planejamento/
  caminho_csv <- file.path("..", "..", "data", "dados_fazenda.csv")
}

if (!file.exists(caminho_csv)) {
  stop("[ERRO] Arquivo dados_fazenda.csv não encontrado.")
}

# 2. Leitura do CSV integrado com Python
dados_fazenda <- read.csv(caminho_csv, header = TRUE, stringsAsFactors = FALSE)

# 3. Filtragem usando Base R (elimina dependência de pacotes externos)
dados_cafe <- subset(dados_fazenda, Cultura == "Café")
dados_soja <- subset(dados_fazenda, Cultura == "Soja")

# 4. Estatísticas Gerais
media_area   <- mean(dados_fazenda$Area_m2, na.rm = TRUE)
desvio_area  <- sd(dados_fazenda$Area_m2, na.rm = TRUE)
media_insumo <- mean(dados_fazenda$Insumo_L, na.rm = TRUE)
desvio_insumo <- sd(dados_fazenda$Insumo_L, na.rm = TRUE)

# 5. Estatísticas Específicas por Cultura
media_cafe   <- mean(dados_cafe$Area_m2, na.rm = TRUE)
desvio_cafe  <- sd(dados_cafe$Area_m2, na.rm = TRUE)
insumo_cafe  <- mean(dados_cafe$Insumo_L, na.rm = TRUE)

media_soja   <- mean(dados_soja$Area_m2, na.rm = TRUE)
desvio_soja  <- sd(dados_soja$Area_m2, na.rm = TRUE)
insumo_soja  <- mean(dados_soja$Insumo_L, na.rm = TRUE)

# 6. Emissão do Relatório Formatado no Terminal
divisoria <- strrep("=", 45)

cat("\n", divisoria, "\n")
cat("   FARMTECH SOLUTIONS — RELATÓRIO ESTATÍSTICO (R)\n")
cat(divisoria, "\n\n")

cat("Fonte dos dados: ", caminho_csv, "\n")
cat("Total de registros analisados: ", nrow(dados_fazenda), "\n\n")

cat("--- ESTATÍSTICAS GERAIS DA FAZENDA ---\n")
cat("Média da Área Total:       ", round(media_area, 2), " m²\n")
cat("Desvio Padrão da Área:     ", round(ifelse(is.na(desvio_area), 0, desvio_area), 2), " m²\n")
cat("Média de Insumos:          ", round(media_insumo, 2), " L\n")
cat("Desvio Padrão de Insumos:  ", round(ifelse(is.na(desvio_insumo), 0, desvio_insumo), 2), " L\n\n")

cat("--- ANÁLISE ESPECÍFICA: CAFÉ ---\n")
cat("Média da Área (Café):      ", round(media_cafe, 2), " m²\n")
cat("Média de Insumo (Café):    ", round(insumo_cafe, 2), " L\n\n")

cat("--- ANÁLISE ESPECÍFICA: SOJA ---\n")
cat("Média da Área (Soja):      ", round(media_soja, 2), " m²\n")
cat("Média de Insumo (Soja):    ", round(insumo_soja, 2), " L\n")

cat("\n", divisoria, "\n")
cat("         PIPELINE PYTHON -> CSV -> R CONCLUÍDO\n")
cat(divisoria, "\n\n")