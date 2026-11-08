-- ==============================================================
-- FARMTECH SOLUTIONS — SCRIPTS ANALÍTICOS ORACLE SQL
-- Tabela: SENSORES_FARMTECH_IOT
-- ==============================================================

-- 1. Visão geral das últimas 10 leituras de telemetria
SELECT id, ts_leitura, umidade, ph, nitrogenio, fosforo, potassio, chuva, irrigacao
FROM SENSORES_FARMTECH_IOT
ORDER BY ts_leitura DESC
FETCH FIRST 10 ROWS ONLY;

-- 2. Médias gerais dos parâmetros agronômicos do solo
SELECT 
    ROUND(AVG(umidade), 2)    AS media_umidade_pct,
    ROUND(AVG(ph), 2)         AS media_ph,
    ROUND(AVG(nitrogenio), 2) AS media_nitrogenio_mgkg,
    ROUND(AVG(fosforo), 2)    AS media_fosforo_mgkg,
    ROUND(AVG(potassio), 2)   AS media_potassio_mgkg,
    COUNT(*)                  AS total_leituras
FROM SENSORES_FARMTECH_IOT;

-- 3. Agrupamento por estado da bomba (Análise de eficiência hídrica)
SELECT 
    CASE WHEN irrigacao = 1 THEN 'BOMBA LIGADA' ELSE 'BOMBA DESLIGADA' END AS status_irrigacao,
    COUNT(*)                                                               AS total_registros,
    ROUND(AVG(umidade), 2)                                                 AS umidade_media,
    ROUND(AVG(ph), 2)                                                      AS ph_medio
FROM SENSORES_FARMTECH_IOT
GROUP BY irrigacao;

-- 4. Detecção de solo com deficiência crítica de NPK
SELECT ts_leitura, umidade, ph, nitrogenio, fosforo, potassio
FROM SENSORES_FARMTECH_IOT
WHERE nitrogenio < 80 OR fosforo < 30 OR potassio < 100
ORDER BY ts_leitura DESC;

-- 5. Histórico recente de inferências YOLOv5 persistido no Oracle
SELECT id, execucao_id, ts_deteccao, arquivo_imagem, classe,
       confianca, x1, y1, x2, y2, modelo
FROM DETECCOES_FARMTECH
ORDER BY ts_deteccao DESC
FETCH FIRST 30 ROWS ONLY;

-- 6. Contagem de detecções reais por classe
SELECT classe, COUNT(*) AS total, ROUND(AVG(confianca) * 100, 2) AS confianca_media_pct
FROM DETECCOES_FARMTECH
GROUP BY classe
ORDER BY total DESC;
