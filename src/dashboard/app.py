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


def execute_service(script: Path, stdin: str | None = None, *, args: list[str] | None = None, timeout: int = 25):
    """Executa os módulos com suporte a argumentos extras, timeout e captura de logs."""
    try:
        result = subprocess.run(
            [sys.executable, str(script), *(args or [])], input=stdin, text=True,
            capture_output=True, cwd=ROOT, timeout=timeout,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        return result.returncode, (result.stdout + "\n" + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, f"Tempo limite de {timeout} segundos atingido durante a execução."
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


def themed_table(frame):
    markup = frame.to_html(index=False, border=0, classes="ft-table", escape=True)
    st.markdown(f'<div class="ft-table-wrap">{markup}</div>', unsafe_allow_html=True)


def themed_log(output):
    st.code(output or "Sem saída textual.", language="text")


def themed_chart(fig):
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter", color="#1F2933", size=11),
        margin=dict(l=30, r=25, t=40, b=30),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EAF2E3")
    fig.update_yaxes(showgrid=True, gridcolor="#EAF2E3")
    st.plotly_chart(fig, width="stretch")


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

# ─── ABAS DO SISTEMA (UNIFICADAS COM AS MELHORIAS DO TALLES) ───────────────────
tab_resumo, tab_fase1, tab_iot, tab_ml, tab_visao, tab_aws = st.tabs([
    "📊 Resumo Operacional",
    "📐 Manejo & Insumos (Fase 1)",
    "🔌 IoT & Oracle (Fases 2 e 3)",
    "🤖 IA Preditiva (Fase 4)",
    "📷 Visão Computacional (Fase 6)",
    "🚨 Alertas Cloud AWS (Fase 7)"
])

# ─── ABA 1: RESUMO OPERACIONAL ────────────────────────────────────────────────
with tab_resumo:
    if not DATA.is_file():
        notice(f"Arquivo de telemetria não encontrado: {DATA.name}", "warning")
    else:
        df = read_telemetry(str(DATA))
        ultimo = df.iloc[-1]

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

        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            fig_line = px.line(
                df, x="timestamp", y=["umidade", "ph"],
                title="Histórico de Umidade e pH do Solo",
                color_discrete_map={"umidade": "#1565C0", "ph": "#2E7D32"},
                labels={"value": "Medição", "timestamp": "Data/Hora", "variable": "Sensor"}
            )
            themed_chart(fig_line)

        with col_g2:
            irrigando = int(df["irrigacao"].sum())
            inativo = len(df) - irrigando
            fig_pie = go.Figure(go.Pie(
                labels=["Bomba Ligada", "Bomba Desligada"],
                values=[irrigando, inativo],
                hole=0.6,
                marker_colors=["#2E7D32", "#C2571A"]
            ))
            fig_pie.update_layout(title="Ativação da Irrigação", paper_bgcolor="#FFFFFF", font=dict(family="Inter", size=11))
            st.plotly_chart(fig_pie, width="stretch")

        with st.expander("🔍 Explorador Detalhado de Sensores & Tabela de Registros", expanded=False):
            options = list(SENSOR_LABELS)
            selected = st.multiselect("Selecione variáveis:", options=options, default=["umidade", "ph"], format_func=lambda n: SENSOR_LABELS[n][0])
            for name in selected:
                label, unit = SENSOR_LABELS[name]
                chart = px.line(df, x="timestamp", y=name, title=f"Série — {label}")
                if name in ("chuva", "irrigacao"):
                    chart.update_traces(line_shape="hv")
                themed_chart(chart)
            st.dataframe(df[["timestamp", *selected]].tail(50), width="stretch", hide_index=True)


# ─── ABA 2: FASE 1 — MANEJO ───────────────────────────────────────────────────
with tab_fase1:
    st.markdown("### 📐 Planejamento Agrícola e Manejo de Insumos (Fase 1)")
    c1, c2 = st.columns(2)
    with c1:
        cultura = st.radio("Cultura:", ["Café (Retângulo)", "Soja (Pivô)"], horizontal=True)
        if "Café" in cultura:
            comp = st.number_input("Comprimento (m):", value=100.0)
            larg = st.number_input("Largura (m):", value=50.0)
            ruas = st.number_input("Ruas:", value=25, step=1)
            dose = st.number_input("Dosagem (mL/m):", value=100.0)
            area = comp * larg
            insumo = (comp * ruas * dose) / 1000.0
        else:
            raio = st.number_input("Raio (m):", value=80.0)
            dose_m2 = st.number_input("Dosagem (mL/m²):", value=50.0)
            area = math.pi * (raio ** 2)
            insumo = (area * dose_m2) / 1000.0
        st.success(f"**Área:** {area:,.1f} m² | **Insumo:** {insumo:,.1f} L")
    with c2:
        if FARM_DATA.exists():
            st.dataframe(pd.read_csv(FARM_DATA), width="stretch", hide_index=True)

    st.markdown("---")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("▶️ Executar Script Python (Fase 1)"):
            code, out = execute_service(ROOT / "src/fase1_planejamento/manejo_insumos.py", stdin="2\n5\n")
            st.code(out, language="text")
    with b2:
        if st.button("▶️ Executar Pipeline R (Fase 1)"):
            code_r, out_r = execute_r(ROOT / "src/fase1_planejamento/analise_estatistica.R")
            st.code(out_r, language="text")


# ─── ABA 3: IOT & ORACLE ──────────────────────────────────────────────────────
with tab_iot:
    st.markdown("### 🔌 Fases 2 e 3: IoT e Banco de Dados Oracle")
    i1, i2 = st.columns(2)
    with i1:
        if st.button("☁️ Consultar Clima OpenWeather"):
            code, out = execute_service(ROOT / "src/fase2_iot/clima.py")
            st.code(out, language="text")
    with i2:
        if st.button("🗄️ Testar Carga Oracle (Merge)"):
            code, out = execute_service(ROOT / "src/fase3_database/ingestao_oracle.py")
            st.code(out, language="text")


# ─── ABA 4: IA PREDITIVA ─────────────────────────────────────────────────────
with tab_ml:
    st.markdown("### 🤖 Fase 4: Inteligência Preditiva e Recomendações")
    s_h = st.slider("Umidade (%):", 0.0, 100.0, 52.0)
    s_ph = st.slider("pH:", 3.0, 10.0, 5.8, 0.1)
    s_n = st.slider("Nitrogênio (mg/kg):", 0.0, 200.0, 70.0)
    s_p = st.slider("Fósforo (mg/kg):", 0.0, 150.0, 25.0)
    s_k = st.slider("Potássio (mg/kg):", 0.0, 250.0, 85.0)
    s_rain = st.radio("Chuva:", [0, 1], format_func=lambda v: "Sim" if v else "Não", horizontal=True)

    from src.fase4_ml.recomendacoes import gerar_recomendacoes_agronomicas
    for a in gerar_recomendacoes_agronomicas(s_h, s_ph, s_n, s_p, s_k, s_rain):
        notice(a)


# ─── ABA 5: VISÃO COMPUTACIONAL ───────────────────────────────────────────────
with tab_visao:
    st.markdown("### 📷 Fase 6: Visão Computacional (YOLOv5 / OpenCV)")
    if st.button("🔍 Executar Inferência Real em Lote"):
        code, out = execute_service(ROOT / "src/fase6_vision/detector.py", args=["--imagem", str(ROOT / "src/fase6_vision/amostras/garrafa_teste.png")])
        st.code(out, language="text")

    img_g = ROOT / "src/fase6_vision/resultado_garrafa.jpg"
    img_c = ROOT / "src/fase6_vision/resultado_caneca.jpg"
    vg1, vg2 = st.columns(2)
    with vg1:
        if img_g.exists(): st.image(str(img_g), caption="Garrafa (Insumo)", width="stretch")
    with vg2:
        if img_c.exists(): st.image(str(img_c), caption="Caneca (Amostragem)", width="stretch")


# ─── ABA 6: ALERTAS AWS SNS ───────────────────────────────────────────────────
with tab_aws:
    st.markdown("### 🚨 Fase 7: Alertas Cloud AWS (Amazon SNS)")
    st.write("Tópico: `arn:aws:sns:us-east-1:608221021260:FarmTechAlertas`")

    with st.form("alert_form"):
        origin = st.selectbox("Origem:", ["Sensores IoT", "Visão Computacional", "Clima"])
        severity = st.select_slider("Severidade:", options=["Informativo", "Atenção", "Crítico"], value="Crítico")
        details = st.text_area("Diagnóstico:", value="Umidade do solo em 42%.")
        action = st.text_input("Ação:", value="Acionar irrigação de emergência.")
        pub = st.form_submit_button("📤 Transmitir Alerta via Amazon SNS")

    if pub:
        from src.fase7_alerts.mensageria_aws import enviar_alerta_aws
        with st.spinner("Publicando na AWS..."):
            res = enviar_alerta_aws(origin, severity, details, action, publicar=True)
            if res.get("publicado"):
                notice(f"Alerta publicado com sucesso! MessageId: {res.get('message_id')}", "success")
            else:
                notice("Alerta simulado com sucesso.", "info")

# ─── RODAPÉ ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<p style='text-align:center; color:#52606D; font-size:0.82rem;'>FarmTech Solutions © 2026 — FIAP Inteligência Artificial</p>", unsafe_allow_html=True)