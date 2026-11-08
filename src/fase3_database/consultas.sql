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