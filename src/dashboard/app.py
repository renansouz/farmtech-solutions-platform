"""FarmTech Solutions — Central Integrada de Gestão Agrícola (Fase 7)."""

import os
import re
import math
from html import escape
import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Diretório raiz absoluto e inclusão no sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA = ROOT / "data" / "sensores_farmtech_v2.csv"
FARM_DATA = ROOT / "data" / "dados_fazenda.csv"
LOGO_PATH = ROOT / "docs" / "assets" / "logo.png"

SERVICES = [
    ("Fase 1 · Manejo de Insumos e Geometria", "fase1_planejamento/manejo_insumos.py", "2\n5\n"),
    ("Fase 2 · Monitoramento Climático e IoT", "fase2_iot/clima.py", None),
    ("Fase 3 · Ingestão e Persistência Oracle DB", "fase3_database/ingestao_oracle.py", None),
    ("Fase 4 · Motor de Recomendações Agronômicas", "fase4_ml/recomendacoes.py", None),
    ("Fase 6 · Visão Computacional (YOLOv5 / OpenCV)", "fase6_vision/detector.py", None),
    ("Fase 7 · Mensageria e Alertas AWS SNS", "fase7_alerts/mensageria_aws.py", None),
]

REQUIRED = {"timestamp", "umidade", "ph", "nitrogenio", "fosforo", "potassio", "chuva", "irrigacao"}
SENSOR_LABELS = {
    "umidade": ("💧 Umidade do Solo", "%"),
    "ph": ("🧪 pH do Solo", ""),
    "nitrogenio": ("🌿 Nitrogênio (N)", "mg/kg"),
    "fosforo": ("🌱 Fósforo (P)", "mg/kg"),
    "potassio": ("⚡ Potássio (K)", "mg/kg"),
    "chuva": ("🌧️ Chuva (0/1)", ""),
    "irrigacao": ("🚰 Irrigação (0/1)", ""),
}


@st.cache_data(ttl=30)
def read_telemetry(path: str):
    frame = pd.read_csv(path)
    missing = REQUIRED.difference(frame.columns)
    if missing:
        raise ValueError(f"Colunas ausentes no CSV: {', '.join(sorted(missing))}")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
    for column in REQUIRED - {"timestamp"}:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.dropna(subset=["timestamp"]).sort_values("timestamp")


def execute_service(script: Path, stdin: str | None = None):
    try:
        result = subprocess.run(
            [sys.executable, str(script)], input=stdin, text=True,
            capture_output=True, cwd=ROOT, timeout=25,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        return result.returncode, (result.stdout + "\n" + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, "Tempo limite de 25 segundos atingido durante a execução."
    except OSError as exc:
        return -1, f"Falha ao iniciar o processo: {exc}"


def execute_r(script: Path):
    try:
        result = subprocess.run(["Rscript", str(script)], capture_output=True, text=True,
                                cwd=ROOT, timeout=25)
        return result.returncode, (result.stdout + "\n" + result.stderr).strip()
    except FileNotFoundError:
        return -1, "Rscript não está instalado ou não foi encontrado no PATH do sistema."
    except subprocess.TimeoutExpired:
        return -1, "Execução do script R excedeu o limite de 25 segundos."


st.set_page_config(page_title="FarmTech Solutions — Central Integrada", page_icon="🌱", layout="wide")

# ─── ESTILIZAÇÃO MODERNA E LEVE (AGRO ENTERPRISE) ────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main {
        background-color: #F7FAF5;
    }

    /* Cabeçalho Hero */
    .hero-card {
        background: #FFFFFF;
        border: 1px solid #D6E2CE;
        border-radius: 14px;
        padding: 22px 28px;
        margin-bottom: 22px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .hero-tag {
        display: inline-block;
        background: #EAF2E3;
        color: #2E7D32;
        border: 1px solid #C5DCBA;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 999px;
        margin-bottom: 8px;
    }
    .hero-card h1 {
        font-size: 2.1rem;
        font-weight: 800;
        color: #1F2933;
        margin: 0;
        line-height: 1.2;
    }
    .hero-card h1 span { color: #2E7D32; }
    .hero-card p {
        color: #52606D;
        font-size: 0.92rem;
        margin-top: 5px;
        margin-bottom: 0;
    }

    /* Cards de Métricas Compactos (1 Linha) */
    .mini-card {
        background: #FFFFFF;
        border: 1px solid #D6E2CE;
        border-radius: 12px;
        padding: 14px 12px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .mini-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(46, 125, 50, 0.08);
    }
    .mini-card-lbl {
        font-size: 0.75rem;
        font-weight: 600;
        color: #52606D;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    .mini-card-val {
        font-size: 1.55rem;
        font-weight: 800;
        color: #1F2933;
        line-height: 1.1;
    }

    /* Badges de Status da Bomba */
    .badge-pump-on {
        background: #EAF2E3;
        color: #2E7D32;
        border: 1px solid #2E7D32;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
        margin-top: 4px;
    }
    .badge-pump-off {
        background: #FDF2F2;
        color: #B3261E;
        border: 1px solid #B3261E;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
        margin-top: 4px;
    }

    /* Notificações Acessíveis */
    .ft-notice {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin: 10px 0 14px;
        padding: 12px 16px;
        border-left: 4px solid;
        border-radius: 8px;
        background: #FFFFFF;
        border-top: 1px solid #D6E2CE;
        border-right: 1px solid #D6E2CE;
        border-bottom: 1px solid #D6E2CE;
        font-size: 0.9rem;
    }

    /* Botões */
    div.stButton > button {
        background-color: #2E7D32 !important;
        color: #FFFFFF !important;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 8px 18px;
    }
    div.stButton > button:hover {
        background-color: #236327 !important;
    }
</style>
""", unsafe_allow_html=True)


def notice(message, kind="info"):
    icons = {"info": "ℹ️", "warning": "⚠️", "success": "✅", "error": "⛔"}
    colors = {"info": "#1565C0", "warning": "#B26A00", "success": "#2E7D32", "error": "#B3261E"}
    st.markdown(
        f'<div class="ft-notice" style="border-left-color:{colors[kind]}">'
        f'<span>{icons[kind]}</span>'
        f'<span>{escape(str(message))}</span></div>',
        unsafe_allow_html=True,
    )


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=170)
    else:
        st.title("🌱 FarmTech")

    st.markdown("### Navegação")
    st.caption("Consolidação de Sistemas · Fase 7")
    st.markdown("---")
    st.write("☕ **Cultura Principal:** Café")
    st.write("🌱 **Cultura Secundária:** Soja")
    st.write("📍 **Localização:** São Paulo (SP)")
    st.markdown("---")
    st.caption("FarmTech Solutions © 2026\nLicença MIT · Acessibilidade WCAG AA")


# ─── CABEÇALHO HERO ───────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-card">
    <div class="hero-tag">Plataforma Integrada · FIAP Inteligência Artificial</div>
    <h1>Farm<span>Tech</span> Solutions</h1>
    <p>Central Agrícola Integrada: IoT de Borda, Banco de Dados, Machine Learning, Visão Computacional e Nuvem AWS</p>
</div>
""", unsafe_allow_html=True)

# ─── ABAS DO SISTEMA ──────────────────────────────────────────────────────────
tab_resumo, tab_fase1, tab_iot, tab_ml, tab_visao, tab_aws = st.tabs([
    "📊 Resumo Operacional",
    "📐 Manejo & Insumos (Fase 1)",
    "🔌 IoT & Oracle (Fases 2 e 3)",
    "🤖 IA Preditiva (Fase 4)",
    "📷 Visão Computacional (Fase 6)",
    "🚨 Alertas Cloud AWS (Fase 7)"
])

# ─── ABA 1: RESUMO OPERACIONAL (CARDS EM 1 LINHA + 2 GRÁFICOS) ────────────────
with tab_resumo:
    if not DATA.is_file():
        notice(f"Arquivo de telemetria não encontrado: {DATA.name}", "warning")
    else:
        df = read_telemetry(str(DATA))
        ultimo = df.iloc[-1]

        # 6 Cards alinhados em uma única linha harmoniosa
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            st.markdown(f'<div class="mini-card"><div class="mini-card-lbl">💧 Umidade Solo</div><div class="mini-card-val" style="color:#1565C0;">{ultimo["umidade"]:.1f}%</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="mini-card"><div class="mini-card-lbl">🧪 pH do Solo</div><div class="mini-card-val" style="color:#2E7D32;">{ultimo["ph"]:.2f}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="mini-card"><div class="mini-card-lbl">🌿 Nitrogênio</div><div class="mini-card-val">{ultimo["nitrogenio"]:.0f} <span style="font-size:0.75rem; color:#64748B;">mg/kg</span></div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="mini-card"><div class="mini-card-lbl">🔬 Fósforo</div><div class="mini-card-val">{ultimo["fosforo"]:.0f} <span style="font-size:0.75rem; color:#64748B;">mg/kg</span></div></div>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'<div class="mini-card"><div class="mini-card-lbl">⚡ Potássio</div><div class="mini-card-val">{ultimo["potassio"]:.0f} <span style="font-size:0.75rem; color:#64748B;">mg/kg</span></div></div>', unsafe_allow_html=True)
        with c6:
            badge_classe = "badge-pump-on" if ultimo["irrigacao"] == 1 else "badge-pump-off"
            txt_bomba = "LIGADA" if ultimo["irrigacao"] == 1 else "DESLIGADA"
            ico_bomba = "🚿" if ultimo["irrigacao"] == 1 else "🛑"
            st.markdown(f'<div class="mini-card"><div class="mini-card-lbl">Bomba Irrigação</div><div><span class="{badge_classe}">{ico_bomba} {txt_bomba}</span></div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2 Gráficos de Alto Valor (Sem Poluição)
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            fig_line = px.line(
                df, x="timestamp", y=["umidade", "ph"],
                title="Histórico de Umidade e pH do Solo",
                color_discrete_map={"umidade": "#1565C0", "ph": "#2E7D32"},
                labels={"value": "Medição", "timestamp": "Data/Hora", "variable": "Sensor"}
            )
            fig_line.update_layout(
                paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                font=dict(family="Inter", color="#1F2933", size=11),
                margin=dict(l=30, r=20, t=40, b=30),
                legend=dict(orientation="h", y=1.1)
            )
            fig_line.update_xaxes(showgrid=True, gridcolor="#EAF2E3")
            fig_line.update_yaxes(showgrid=True, gridcolor="#EAF2E3")
            st.plotly_chart(fig_line, width="stretch")

        with col_g2:
            irrigando = int(df["irrigacao"].sum())
            inativo = len(df) - irrigando
            fig_pie = go.Figure(go.Pie(
                labels=["Bomba Ligada", "Bomba Desligada"],
                values=[irrigando, inativo],
                hole=0.6,
                marker_colors=["#2E7D32", "#C2571A"]
            ))
            fig_pie.update_layout(
                title="Ativação da Irrigação",
                paper_bgcolor="#FFFFFF",
                font=dict(family="Inter", color="#1F2933", size=11),
                margin=dict(l=20, r=20, t=40, b=30)
            )
            st.plotly_chart(fig_pie, width="stretch")

        # Explorador Detalhado em Expansor (Dá o respiro visual que faltava)
        with st.expander("🔍 Explorador Detalhado de Sensores & Tabela de Registros", expanded=False):
            options = list(SENSOR_LABELS)
            selected = st.multiselect("Selecione variáveis para análise individual:", options=options, default=["umidade", "ph", "nitrogenio"], format_func=lambda n: SENSOR_LABELS[n][0])
            for name in selected:
                label, unit = SENSOR_LABELS[name]
                chart = px.line(df, x="timestamp", y=name, title=f"Série — {label}", labels={"timestamp": "Data/Hora", name: label})
                if name in ("chuva", "irrigacao"):
                    chart.update_traces(line_shape="hv")
                chart.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(family="Inter", size=10))
                st.plotly_chart(chart, width="stretch")

            st.markdown("#### Últimos Registros Brutos")
            st.dataframe(df[["timestamp", *selected]].tail(50), width="stretch", hide_index=True)


# ─── ABA 2: FASE 1 — MANEJO DE INSUMOS & GEOMETRIA ────────────────────────────
with tab_fase1:
    st.markdown("### 📐 Planejamento Agrícola e Manejo de Insumos (Fase 1)")
    st.write("Cálculo geométrico de área plantada e dosagem volumétrica de insumos em Python e R.")

    col_c1, col_c2 = st.columns([1, 1])
    with col_c1:
        st.markdown("#### Calculadora Interativa de Campo")
        cultura = st.radio("Cultura:", ["Café (Área Retangular)", "Soja (Pivô Circular)"], horizontal=True)
        if "Café" in cultura:
            comp = st.number_input("Comprimento da Lavoura (m):", min_value=10.0, value=100.0, step=10.0)
            larg = st.number_input("Largura da Lavoura (m):", min_value=10.0, value=50.0, step=10.0)
            ruas = st.number_input("Ruas de Plantio:", min_value=1, value=25, step=1)
            dose = st.number_input("Dosagem de Fosfato (mL/m linear):", min_value=1.0, value=100.0, step=10.0)
            area_m2 = comp * larg
            insumo_l = (comp * ruas * dose) / 1000.0
        else:
            raio = st.number_input("Raio do Pivô Central (m):", min_value=10.0, value=80.0, step=5.0)
            dose_m2 = st.number_input("Dosagem de Defensivo (mL/m²):", min_value=0.1, value=50.0, step=5.0)
            area_m2 = math.pi * (raio ** 2)
            insumo_l = (area_m2 * dose_m2) / 1000.0

        q1, q2 = st.columns(2)
        q1.metric("Área Estimada", f"{area_m2:,.1f} m²")
        q2.metric("Demanda de Insumo", f"{insumo_l:,.1f} L")

    with col_c2:
        st.markdown("#### Talhões Cadastrados (`data/dados_fazenda.csv`)")
        if FARM_DATA.exists():
            farm_df = pd.read_csv(FARM_DATA)
            st.dataframe(farm_df, width="stretch", hide_index=True)
            if "Insumo_L" in farm_df.columns:
                fig_bar = px.bar(farm_df, x="Cultura", y="Insumo_L", color="Cultura", title="Volume Cadastrado (L)")
                fig_bar.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(family="Inter", size=10))
                st.plotly_chart(fig_bar, width="stretch")

    st.markdown("---")
    st.markdown("#### Disparo de Scripts da Fase 1")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("▶️ Executar Script Python (Fase 1)"):
            with st.spinner("Executando módulo Python..."):
                code, out = execute_service(ROOT / "src/fase1_planejamento/manejo_insumos.py", stdin="2\n5\n")
                st.code(out, language="text")
    with b2:
        if st.button("▶️ Executar Pipeline R (Fase 1)"):
            with st.spinner("Executando Rscript..."):
                code_r, out_r = execute_r(ROOT / "src/fase1_planejamento/analise_estatistica.R")
                st.code(out_r, language="text")


# ─── ABA 3: FASES 2 E 3 — IOT E ORACLE ─────────────────────────────────────────
with tab_iot:
    st.markdown("### 🔌 Fases 2 e 3: Sensoriamento IoT e Banco de Dados")
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.markdown("#### Telemetria Climática (OpenWeather API)")
        st.caption("Consumo de API meteorológica e transmissão serial de decisão de chuva para o ESP32.")
        if st.button("☁️ Consultar Previsão de Chuva em Tempo Real"):
            with st.spinner("Consultando OpenWeather..."):
                code, out = execute_service(ROOT / "src/fase2_iot/clima.py")
                st.code(out, language="text")

    with col_i2:
        st.markdown("#### Ingestão e Persistência Oracle DB")
        st.caption("Conexão e validação da tabela `SENSORES_FARMTECH_IOT` no Oracle Database FIAP.")
        if st.button("🗄️ Testar Carga e Conexão Oracle"):
            with st.spinner("Conectando ao Oracle DB..."):
                code, out = execute_service(ROOT / "src/fase3_database/ingestao_oracle.py")
                st.code(out, language="text")


# ─── ABA 4: FASE 4 — IA PREDITIVA ─────────────────────────────────────────────
with tab_ml:
    st.markdown("### 🤖 Fase 4: Inteligência Preditiva e Recomendações de Manejo")
    st.write("Simulador de cenários agrícolas (*What-If*) aplicando regras agronômicas em tempo real.")

    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        st.markdown("#### 🧪 Simulador de Solo")
        s_umidade = st.slider("Umidade do Solo (%):", 10.0, 95.0, 52.0, 1.0)
        s_ph = st.slider("pH do Solo:", 4.0, 9.0, 5.8, 0.1)
        s_n = st.slider("Nitrogênio - N (mg/kg):", 10.0, 150.0, 70.0, 5.0)
        s_p = st.slider("Fósforo - P (mg/kg):", 5.0, 80.0, 25.0, 1.0)
        s_k = st.slider("Potássio - K (mg/kg):", 20.0, 200.0, 85.0, 5.0)
        s_chuva = st.radio("Previsão Meteorológica:", [0, 1], format_func=lambda v: "🌧️ Chuva Prevista" if v else "☀️ Sem Chuva", horizontal=True)

    with col_s2:
        st.markdown("#### 📋 Ações Corretivas Recomendadas")
        from src.fase4_ml.recomendacoes import gerar_recomendacoes_agronomicas
        for a in gerar_recomendacoes_agronomicas(s_umidade, s_ph, s_n, s_p, s_k, s_chuva):
            if "IRRIGAR IMEDIATAMENTE" in a or "ácido" in a:
                notice(a, "warning")
            elif "SUSPENDER" in a or "NÃO IRRIGAR" in a:
                notice(a, "error")
            else:
                notice(a, "success")


# ─── ABA 5: FASE 6 — VISÃO COMPUTACIONAL ──────────────────────────────────────
with tab_visao:
    st.markdown("### 📷 Fase 6: Diagnóstico Visual de Objetos e Insumos (YOLOv5)")
    st.write("Detecção automatizada e medição de latência em CPU para recipientes de defensivos (`garrafa`) e ferramentas de amostragem (`caneca`).")

    col_v1, col_v2 = st.columns([1, 1])
    with col_v1:
        st.markdown("#### Executar Detecção em Lote")
        st.caption("Comando: `python src/fase6_vision/detector.py`")
        if st.button("🔍 Executar Inferência OpenCV / YOLO"):
            with st.spinner("Processando amostras reais..."):
                code, out = execute_service(ROOT / "src/fase6_vision/detector.py")
                st.code(out, language="text")

    with col_v2:
        st.markdown("#### Classes Identificadas no Campo")
        st.info("• **Classe 0 (Garrafa):** Insumo Líquido / Defensivo Agrícola\n• **Classe 1 (Caneca):** Utensílio de Coleta de Amostras")
        st.caption("Inspeção visual automatizada para conformidade de defensivos no campo.")

    st.markdown("---")
    st.markdown("#### 🖼️ Imagens Processadas com Bounding Boxes Reais")
    img_g = ROOT / "src/fase6_vision/resultado_garrafa.jpg"
    img_c = ROOT / "src/fase6_vision/resultado_caneca.jpg"

    vg1, vg2 = st.columns(2)
    with vg1:
        if img_g.exists():
            st.image(str(img_g), caption="Detecção Real: Garrafa (Insumo) — Confiança: 96.0%", width="stretch")
    with vg2:
        if img_c.exists():
            st.image(str(img_c), caption="Detecção Real: Caneca (Amostragem) — Confiança: 94.0%", width="stretch")


# ─── ABA 6: FASE 7 — MENSAGERIA AWS ───────────────────────────────────────────
with tab_aws:
    st.markdown("### 🚨 Fase 7: Central de Alertas e Mensageria Cloud AWS (Amazon SNS)")
    st.write(f"**Tópico Configurado:** `arn:aws:sns:us-east-1:608221021260:FarmTechAlertas` *(US East - N. Virginia)*")

    with st.form("alert_form"):
        origin = st.selectbox("Origem do Diagnóstico:", ["Sensores IoT de Solo (Setor Café A-12)", "Visão Computacional (Setor Armazém)", "Estação Meteorológica"])
        severity = st.select_slider("Nível de Severidade:", options=["Informativo", "Atenção", "Crítico"], value="Crítico")
        details = st.text_area("Diagnóstico Agronômico:", value="Umidade do solo em 42% (abaixo do limiar mínimo de 60%) com déficit hídrico prolongado.")
        action = st.text_input("Ação Corretiva Recomendada:", value="Acionar irrigação de emergência (volume: 7.2 L/m²) e aplicar calcário dolomítico.")

        b_sub1, b_sub2 = st.columns(2)
        with b_sub1:
            preview = st.form_submit_button("👁️ Pré-visualizar Mensagem")
        with b_sub2:
            publish = st.form_submit_button("📤 Transmitir Alerta via Amazon SNS")

    if preview:
        from src.fase7_alerts.mensageria_aws import formatar_mensagem_alerta
        subj, body, sms = formatar_mensagem_alerta(origin, severity, details, action)
        st.write("**Assunto:**", subj)
        st.text_area("Prévia de E-mail:", body, height=180)
        st.text_area("Prévia de SMS:", sms, height=65)
        notice("Prévia estruturada pronta para envio.", "info")

    if publish:
        from src.fase7_alerts.mensageria_aws import enviar_alerta_aws
        with st.spinner("Transmitindo notificação para a AWS..."):
            sucesso = enviar_alerta_aws(origin, severity, details, action)
            if sucesso:
                notice("Alerta publicado com sucesso no Amazon SNS e entregue aos destinatários cadastrados!", "success")
            else:
                notice("Falha ao publicar alerta na AWS.", "error")

# ─── RODAPÉ ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#52606D; font-size:0.82rem;'>"
    "FarmTech Solutions © 2026 — FIAP Inteligência Artificial · Fase 7: A Consolidação de um Sistema"
    "</p>",
    unsafe_allow_html=True
)