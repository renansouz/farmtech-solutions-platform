import os
import sys
import subprocess
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Caminhos base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_SENSORES = BASE_DIR / "data" / "sensores_farmtech_v2.csv"
PYTHON_EXEC = sys.executable

# Configuração da página Streamlit
st.set_page_config(
    page_title="FarmTech Solutions — Plataforma Integrada",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS
st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .hero {
        text-align: center;
        padding: 30px 0 20px 0;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 25px;
    }
    .hero-tag {
        display: inline-block;
        background: #0f172a;
        border: 1px solid #334155;
        color: #10b981;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 4px 16px;
        border-radius: 9999px;
        margin-bottom: 10px;
    }
    .hero h1 {
        font-size: 2.6rem;
        font-weight: 800;
        color: #f8fafc;
        margin: 0;
    }
    .hero h1 span { color: #10b981; }
    .hero p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 8px;
    }
    .card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
    }
    .card-val { font-size: 1.8rem; font-weight: 800; color: #10b981; }
    .card-lbl { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)


def carregar_dados():
    if CSV_SENSORES.exists():
        return pd.read_csv(CSV_SENSORES, parse_dates=["timestamp"])
    return pd.DataFrame()


df = carregar_dados()

# Header Principal
st.markdown("""
<div class="hero">
    <div class="hero-tag">Consolidação de Sistemas · Fase 7</div>
    <h1>Farm<span>Tech</span> Solutions</h1>
    <p>Hub Integrado de Gestão Agrícola: IoT, Banco de Dados, Machine Learning, Visão Computacional e Nuvem</p>
</div>
""", unsafe_allow_html=True)

# Abas Principais
tab_painel, tab_servicos, tab_alertas = st.tabs([
    "📊 Painel de Telemetria (Fases 2, 3 e 4)",
    "⚡ Central de Execução de Serviços (Fases 1 a 6)",
    "🚨 Central de Mensageria AWS (Fase 7)"
])

# ─── ABA 1: PAINEL DE TELEMETRIA ──────────────────────────────────────────────
with tab_painel:
    if not df.empty:
        ultimo = df.iloc[-1]
        cols = st.columns(6)
        cards = [
            (f"{ultimo['umidade']}%", "💧 Umidade Solo"),
            (f"{ultimo['ph']}", "🧪 pH Solo"),
            (f"{ultimo['nitrogenio']} mg/kg", "🌿 Nitrogênio (N)"),
            (f"{ultimo['fosforo']} mg/kg", "🔬 Fósforo (P)"),
            (f"{ultimo['potassio']} mg/kg", "⚡ Potássio (K)"),
            ("🌧️ Chuva" if ultimo['chuva'] == 1 else "☀️ Sem Chuva", "🌦️ Clima"),
        ]
        for col, (val, lbl) in zip(cols, cards):
            with col:
                st.markdown(f"""
                <div class="card">
                    <div class="card-val">{val}</div>
                    <div class="card-lbl">{lbl}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            fig_umidade = px.line(
                df, x="timestamp", y=["umidade", "ph"],
                title="Série Histórica — Umidade e pH do Solo",
                color_discrete_map={"umidade": "#38bdf8", "ph": "#a855f7"},
                template="plotly_dark"
            )
            fig_umidade.update_layout(paper_bgcolor="#0b0f19", plot_bgcolor="#0b0f19")
            st.plotly_chart(fig_umidade, use_container_width=True)

        with col_g2:
            irrigando = int(df["irrigacao"].sum())
            desligada = len(df) - irrigando
            fig_bomba = go.Figure(go.Pie(
                labels=["Bomba Ligada", "Bomba Desligada"],
                values=[irrigando, desligada],
                hole=0.5,
                marker_colors=["#10b981", "#ef4444"]
            ))
            fig_bomba.update_layout(
                title="Distribuição de Irrigação",
                template="plotly_dark",
                paper_bgcolor="#0b0f19"
            )
            st.plotly_chart(fig_bomba, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado no arquivo CSV de telemetria.")

# ─── ABA 2: CENTRAL DE DISPARO DE SERVIÇOS ────────────────────────────────────
with tab_servicos:
    st.markdown("### 🛠️ Disparo Integrado de Serviços por Interface ou Terminal")
    st.info("Execute os componentes das fases anteriores diretamente por este painel ou copie os comandos para seu terminal.")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 1. Planejamento Agrícola e Manejo de Insumos (Fase 1)")
        st.caption("Comando: `python src/fase1_planejamento/manejo_insumos.py`")
        if st.button("▶️ Executar Relatório de Manejo (Fase 1)"):
            cmd = [PYTHON_EXEC, str(BASE_DIR / "src" / "fase1_planejamento" / "manejo_insumos.py")]
            # Executa com entrada '2\n5\n' para imprimir relatório e sair
            res = subprocess.run(cmd, input="2\n5\n", capture_output=True, text=True)
            st.code(res.stdout, language="text")

        st.markdown("#### 2. Monitoramento Climático OpenWeather (Fase 2)")
        st.caption("Comando: `python src/fase2_iot/clima.py`")
        if st.button("▶️ Consultar Clima e Decisão de Irrigação (Fase 2)"):
            cmd = [PYTHON_EXEC, str(BASE_DIR / "src" / "fase2_iot" / "clima.py")]
            res = subprocess.run(cmd, capture_output=True, text=True)
            st.code(res.stdout, language="text")

        st.markdown("#### 3. Banco de Dados e Ingestão Oracle (Fase 3)")
        st.caption("Comando: `python src/fase3_database/ingestao_oracle.py`")
        if st.button("▶️ Testar Conexão e Carga Oracle DB (Fase 3)"):
            cmd = [PYTHON_EXEC, str(BASE_DIR / "src" / "fase3_database" / "ingestao_oracle.py")]
            res = subprocess.run(cmd, capture_output=True, text=True)
            st.code(res.stdout, language="text")

    with c2:
        st.markdown("#### 4. Motor de Recomendações Agronômicas (Fase 4)")
        st.caption("Comando: `python src/fase4_ml/recomendacoes.py`")
        if st.button("▶️ Gerar Recomendações de Solo/NPK (Fase 4)"):
            cmd = [PYTHON_EXEC, str(BASE_DIR / "src" / "fase4_ml" / "recomendacoes.py")]
            res = subprocess.run(cmd, capture_output=True, text=True)
            st.code(res.stdout, language="text")

        st.markdown("#### 5. Visão Computacional YOLOv5 (Fase 6)")
        st.caption("Comando: `python src/fase6_vision/detector.py`")
        if st.button("▶️ Executar Detecção de Objetos/Campo (Fase 6)"):
            cmd = [PYTHON_EXEC, str(BASE_DIR / "src" / "fase6_vision" / "detector.py")]
            res = subprocess.run(cmd, capture_output=True, text=True)
            st.code(res.stdout, language="text")

        st.markdown("#### 6. Mensageria e Notificações AWS (Fase 7)")
        st.caption("Comando: `python src/fase7_alerts/mensageria_aws.py`")
        if st.button("▶️ Disparar Alerta AWS de Teste (Fase 7)"):
            cmd = [PYTHON_EXEC, str(BASE_DIR / "src" / "fase7_alerts" / "mensageria_aws.py")]
            res = subprocess.run(cmd, capture_output=True, text=True)
            st.code(res.stdout, language="text")

# ─── ABA 3: CENTRAL DE MENSAGERIA AWS ─────────────────────────────────────────
with tab_alertas:
    st.markdown("### 🚨 Painel de Notificações Cloud AWS (Email / SMS)")
    st.caption("Envio de alertas com orientações agronômicas corretivas aos operadores agrícolas.")

    with st.form("form_alerta_aws"):
        f_origem = st.selectbox(
            "Origem da Ocorrência",
            ["Sensores IoT - Setor Café A-1", "Visão Computacional - Setor Galpão", "Previsão Meteorológica"]
        )
        f_nivel = st.select_slider("Nível de Severidade", options=["Informativo", "Atenção", "Crítico"], value="Crítico")
        f_detalhes = st.text_area("Diagnóstico dos Dados", value="Umidade do solo em 45% com déficit hídrico prolongado.")
        f_acao = st.text_input("Ação Corretiva Sugerida", value="Acionar irrigação de emergência (5 L/m²) e checar válvulas.")

        enviar_btn = st.form_submit_button("📤 Publicar Alerta no Amazon SNS")

        if enviar_btn:
            from src.fase7_alerts.mensageria_aws import enviar_alerta_aws
            with st.spinner("Transmitindo notificação para a AWS..."):
                enviar_alerta_aws(f_origem, f_nivel, f_detalhes, f_acao)
                st.success("✅ Alerta processado com sucesso pelo serviço de mensageria!")
                st.json({
                    "origem": f_origem,
                    "severidade": f_nivel,
                    "diagnostico": f_detalhes,
                    "acao_corretiva": f_acao,
                    "status_envio": "Publicado (AWS SNS / Simulador)"
                })