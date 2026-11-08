import os
import sys
import subprocess
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
CSV_SENSORES = BASE_DIR / "data" / "sensores_farmtech_v2.csv"
CSV_FAZENDA = BASE_DIR / "data" / "dados_fazenda.csv"
CAMINHO_LOGO = BASE_DIR / "docs" / "assets" / "logo.png"
PYTHON_EXEC = sys.executable

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions — Plataforma Integrada",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS acessível (WCAG AA)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1F2933;
    }

    /* Container Principal */
    .main {
        background-color: #F7FAF5;
    }

    /* Hero / Cabeçalho */
    .hero-container {
        background: #FFFFFF;
        border: 1px solid #D6E2CE;
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 2px 6px rgba(46, 125, 50, 0.04);
    }
    .hero-badge {
        display: inline-block;
        background: #EAF2E3;
        color: #2E7D32;
        border: 1px solid #C5DCBA;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 9999px;
        margin-bottom: 8px;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #1F2933;
        margin: 0;
        line-height: 1.2;
    }
    .hero-title span {
        color: #2E7D32;
    }
    .hero-desc {
        color: #52606D;
        font-size: 0.95rem;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* Cards de Métricas */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #D6E2CE;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(46, 125, 50, 0.08);
    }
    .metric-val {
        font-size: 1.7rem;
        font-weight: 800;
        color: #2E7D32;
        margin-top: 4px;
    }
    .metric-lbl {
        font-size: 0.82rem;
        font-weight: 600;
        color: #52606D;
        letter-spacing: 0.02em;
    }

    /* Status Semânticos Acessíveis */
    .status-badge-on {
        background: #EAF2E3;
        border: 1px solid #2E7D32;
        color: #2E7D32;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .status-badge-off {
        background: #FDF2F2;
        border: 1px solid #B3261E;
        color: #B3261E;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Botões */
    div.stButton > button {
        background-color: #2E7D32;
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 8px 18px;
        transition: background-color 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #236327;
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)


# ─── FUNÇÕES DE CARREGAMENTO ──────────────────────────────────────────────────
@st.cache_data
def carregar_telemetria():
    if CSV_SENSORES.exists():
        return pd.read_csv(CSV_SENSORES, parse_dates=["timestamp"])
    return pd.DataFrame()


@st.cache_data
def carregar_fazenda():
    if CSV_FAZENDA.exists():
        return pd.read_csv(CSV_FAZENDA)
    return pd.DataFrame()


df_sensores = carregar_telemetria()
df_fazenda = carregar_fazenda()

# ─── CABEÇALHO / HERO ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">Plataforma Integrada · FIAP Inteligência Artificial</div>
    <h1 class="hero-title">Farm<span>Tech</span> Solutions</h1>
    <p class="hero-desc">Hub Central de Gestão Agrícola: Integração de IoT de Borda, Banco Corporativo, IA Preditiva, Visão Computacional e Nuvem AWS</p>
</div>
""", unsafe_allow_html=True)

# ─── BARRA LATERAL (SIDEBAR) ──────────────────────────────────────────────────
with st.sidebar:
    if CAMINHO_LOGO.exists():
        st.image(str(CAMINHO_LOGO), width=180)
    else:
        st.markdown("### 🌱 FarmTech")
    st.markdown("### Navegação da Plataforma")
    st.info("Sistema unificado consolidando as Fases 1 a 7 do projeto acadêmico.")
    
    st.markdown("---")
    st.markdown("#### Parâmetros de Cultura")
    st.write("☕ **Cultura Principal:** Café (*Coffea arabica*)")
    st.write("🌱 **Cultura Secundária:** Soja")
    st.write("📍 **Localização:** Região Sudeste (SP)")

    st.markdown("---")
    st.caption("FarmTech Solutions © 2026\nLicença MIT · Acessibilidade WCAG AA")


# ─── ABAS PRINCIPAIS DO SISTEMA ───────────────────────────────────────────────
tab_painel, tab_fase1, tab_iot, tab_ml, tab_visao, tab_aws = st.tabs([
    "📊 Resumo Operacional",
    "📐 Fase 1: Manejo & Insumos",
    "🔌 Fases 2 e 3: IoT & Banco",
    "🤖 Fase 4: IA Preditiva",
    "📷 Fase 6: Visão Computacional",
    "🚨 Fase 7: Alertas Cloud AWS"
])


# ─── ABA 1: RESUMO OPERACIONAL (CARDS E TELEMETRIA) ───────────────────────────
with tab_painel:
    st.markdown("### 📡 Indicadores de Campo em Tempo Real")
    st.caption("Visão sintética das condições agronômicas da lavoura de café.")

    if not df_sensores.empty:
        ultimo = df_sensores.iloc[-1]
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">💧 Umidade Solo</div><div class="metric-val">{ultimo["umidade"]:.1f}%</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">🧪 pH do Solo</div><div class="metric-val">{ultimo["ph"]:.1f}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">🌿 Nitrogênio (N)</div><div class="metric-val">{ultimo["nitrogenio"]:.0f} <span style="font-size:0.9rem;">mg/kg</span></div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">🔬 Fósforo (P)</div><div class="metric-val">{ultimo["fosforo"]:.0f} <span style="font-size:0.9rem;">mg/kg</span></div></div>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">⚡ Potássio (K)</div><div class="metric-val">{ultimo["potassio"]:.0f} <span style="font-size:0.9rem;">mg/kg</span></div></div>', unsafe_allow_html=True)
        with c6:
            status_bomba = "LIGADA" if ultimo["irrigacao"] == 1 else "DESLIGADA"
            classe_bomba = "status-badge-on" if ultimo["irrigacao"] == 1 else "status-badge-off"
            icone_bomba = "🚿" if ultimo["irrigacao"] == 1 else "🛑"
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">Bomba de Irrigação</div><div style="margin-top:8px;"><span class="{classe_bomba}">{icone_bomba} {status_bomba}</span></div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_graf1, col_graf2 = st.columns([2, 1])
        with col_graf1:
            # Gráfico de série temporal com cores amigáveis
            fig_hist = px.line(
                df_sensores, x="timestamp", y=["umidade", "ph"],
                title="Série Histórica — Umidade e pH do Solo",
                color_discrete_map={"umidade": "#1565C0", "ph": "#2E7D32"},
                labels={"value": "Medição", "timestamp": "Horário", "variable": "Parâmetro"}
            )
            fig_hist.update_layout(
                paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                font=dict(family="Inter", color="#1F2933"),
                legend=dict(orientation="h", y=1.1)
            )
            fig_hist.update_xaxes(showgrid=True, gridcolor="#EAF2E3")
            fig_hist.update_yaxes(showgrid=True, gridcolor="#EAF2E3")
            st.plotly_chart(fig_hist, width="stretch")

        with col_graf2:
            irrigando = int(df_sensores["irrigacao"].sum())
            inativo = len(df_sensores) - irrigando
            fig_pie = go.Figure(go.Pie(
                labels=["Bomba Ligada", "Bomba Desligada"],
                values=[irrigando, inativo],
                hole=0.55,
                marker_colors=["#2E7D32", "#C2571A"]
            ))
            fig_pie.update_layout(
                title="Ativação do Sistema de Irrigação",
                paper_bgcolor="#FFFFFF",
                font=dict(family="Inter", color="#1F2933")
            )
            st.plotly_chart(fig_pie, width="stretch")
    else:
        st.warning("Arquivo de telemetria não encontrado em `data/sensores_farmtech_v2.csv`.")


# ─── ABA 2: FASE 1 — MANEJO DE INSUMOS & GEOMETRIA ────────────────────────────
with tab_fase1:
    st.markdown("### 📐 Fase 1: Planejamento Agrícola & Manejo de Insumos")
    st.write("Cálculo geométrico de área plantada e dimensionamento volumétrico de insumos em Python e R.")

    col_calc, col_dados = st.columns([1, 1])

    with col_calc:
        st.markdown("#### Calculadora Interativa de Campo")
        cultura_sel = st.selectbox("Selecione a Cultura:", ["Café (Geometria Retangular)", "Soja (Pivô Central Circular)"])
        
        if "Café" in cultura_sel:
            c_comp = st.number_input("Comprimento da Lavoura (metros):", min_value=10.0, value=100.0, step=10.0)
            c_larg = st.number_input("Largura da Lavoura (metros):", min_value=10.0, value=50.0, step=10.0)
            c_ruas = st.number_input("Número de Ruas de Plantio:", min_value=1, value=25, step=1)
            c_dose = st.number_input("Dosagem de Fosfato (mL por metro linear):", min_value=1.0, value=100.0, step=10.0)
            
            area_calc = c_comp * c_larg
            insumo_calc = (c_comp * c_ruas * c_dose) / 1000.0
            
            st.success(f"**Área Total:** {area_calc:,.2f} m² | **Demanda de Fosfato:** {insumo_calc:,.2f} Litros")
        else:
            c_raio = st.number_input("Raio do Pivô Central (metros):", min_value=10.0, value=80.0, step=5.0)
            c_dose_m2 = st.number_input("Dosagem de Defensivo (mL por m²):", min_value=0.1, value=50.0, step=5.0)
            
            import math
            area_calc = math.pi * (c_raio ** 2)
            insumo_calc = (area_calc * c_dose_m2) / 1000.0
            
            st.success(f"**Área do Pivô:** {area_calc:,.2f} m² | **Demanda de Defensivo:** {insumo_calc:,.2f} Litros")

    with col_dados:
        st.markdown("#### Histórico de Talhões Cadastrados (`data/dados_fazenda.csv`)")
        if not df_fazenda.empty:
            st.dataframe(df_fazenda, width="stretch", hide_index=True)
        else:
            st.info("Nenhum talhão cadastrado no arquivo CSV.")

        st.markdown("#### Disparo dos Scripts via Terminal")
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("▶️ Rodar Relatório Python (Fase 1)"):
                with st.spinner("Executando módulo Python..."):
                    cmd = [PYTHON_EXEC, str(BASE_DIR / "src" / "fase1_planejamento" / "manejo_insumos.py")]
                    res = subprocess.run(cmd, input="2\n5\n", capture_output=True, text=True)
                    st.code(res.stdout, language="text")
        with c_btn2:
            if st.button("▶️ Rodar Pipeline R (Fase 1)"):
                with st.spinner("Executando script R..."):
                    cmd = ["Rscript", str(BASE_DIR / "src" / "fase1_planejamento" / "analise_estatistica.R")]
                    try:
                        res = subprocess.run(cmd, capture_output=True, text=True)
                        st.code(res.stdout if res.stdout else res.stderr, language="text")
                    except Exception as e:
                        st.warning(f"Rscript não encontrado localmente: {e}. O script está salvo em src/fase1_planejamento/.")


# ─── ABA 3: FASES 2 E 3 — IOT, CLIMA E BANCO ORACLE ───────────────────────────
with tab_iot:
    st.markdown("### 🔌 Fases 2 e 3: Sensoriamento IoT e Banco de Dados")
    st.write("Integração do microcontrolador ESP32 com telemetria climática e persistência corporativa Oracle.")

    c_iot1, c_iot2 = st.columns(2)

    with c_iot1:
        st.markdown("#### Monitoramento Meteorológico (OpenWeather API)")
        st.caption("Consome a API de clima e define se a irrigação deve ser suspensa.")
        if st.button("☁️ Consultar Previsão Climática em Tempo Real"):
            with st.spinner("Consultando OpenWeather..."):
                cmd = [PYTHON_EXEC, str(BASE_DIR / "src" / "fase2_iot" / "clima.py")]
                res = subprocess.run(cmd, capture_output=True, text=True)
                st.code(res.stdout, language="text")

    with c_iot2:
        st.markdown("#### Banco de Dados Oracle FIAP (`SENSORES_FARMTECH_IOT`)")
        st.caption("Validação de integridade e ingestão de telemetria no banco relacional.")
        if st.button("🗄️ Testar Conexão e Carga Oracle"):
            with st.spinner("Conectando ao Oracle Database..."):
                cmd = [PYTHON_EXEC, str(BASE_DIR / "src" / "fase3_database" / "ingestao_oracle.py")]
                res = subprocess.run(cmd, capture_output=True, text=True)
                st.code(res.stdout, language="text")


# ─── ABA 4: FASE 4 — IA PREDITIVA E RECOMENDAÇÕES AGRONÔMICAS ─────────────────
with tab_ml:
    st.markdown("### 🤖 Fase 4: Inteligência Preditiva e Recomendações de Manejo")
    st.write("Simulador de condições de solo que aplica regras agronômicas para tomada de decisão em tempo real.")

    col_sim, col_rec = st.columns([1, 1])

    with col_sim:
        st.markdown("#### 🧪 Simulador de Cenários de Solo (*What-If*)")
        sim_umidade = st.slider("Umidade do Solo (%):", min_value=10.0, max_value=95.0, value=52.0, step=1.0)
        sim_ph = st.slider("pH do Solo:", min_value=4.0, max_value=9.0, value=5.8, step=0.1)
        sim_n = st.slider("Nitrogênio - N (mg/kg):", min_value=10.0, max_value=150.0, value=70.0, step=5.0)
        sim_p = st.slider("Fósforo - P (mg/kg):", min_value=5.0, max_value=80.0, value=25.0, step=1.0)
        sim_k = st.slider("Potássio - K (mg/kg):", min_value=20.0, max_value=200.0, value=85.0, step=5.0)
        sim_chuva = st.radio("Previsão de Chuva:", [0, 1], format_func=lambda x: "🌧️ Chuva Prevista" if x == 1 else "☀️ Sem Chuva", horizontal=True)

    with col_rec:
        st.markdown("#### 📋 Ações Corretivas Geradas pela IA")
        from src.fase4_ml.recomendacoes import gerar_recomendacoes_agronomicas
        
        acoes = gerar_recomendacoes_agronomicas(sim_umidade, sim_ph, sim_n, sim_p, sim_k, sim_chuva)
        for a in acoes:
            if "IRRIGAR IMEDIATAMENTE" in a or "excessivamente ácido" in a or "deficiência" in a:
                st.warning(a)
            elif "SUSPENDER" in a or "NÃO IRRIGAR" in a:
                st.error(a)
            else:
                st.success(a)


# ─── ABA 5: FASE 6 — VISÃO COMPUTACIONAL (YOLO) ──────────────────────────────
with tab_visao:
    st.markdown("### 📷 Fase 6: Diagnóstico Visual de Objetos e Insumos (YOLOv5)")
    st.write("Detecção automatizada e medição de latência em CPU para recipientes de defensivos (`garrafa`) e ferramentas de coleta (`caneca`).")

    col_v1, col_v2 = st.columns([1, 1])

    with col_v1:
        st.markdown("#### Execução do Módulo de Visão Computacional")
        st.caption("Comando de terminal: `python src/fase6_vision/detector.py`")
        
        if st.button("🔍 Executar Detecção Visual em Lote"):
            with st.spinner("Processando amostras reais com OpenCV..."):
                cmd = [PYTHON_EXEC, str(BASE_DIR / "src" / "fase6_vision" / "detector.py")]
                res = subprocess.run(cmd, capture_output=True, text=True)
                st.code(res.stdout, language="text")

    with col_v2:
        st.markdown("#### Classes do Modelo Treinado")
        st.info("• **Classe 0 (Garrafa):** Insumo Líquido / Defensivo Agrícola\n• **Classe 1 (Caneca):** Utensílio de Coleta de Amostras de Solo")
        st.caption("Modelo treinado para inspeção visual automatizada de insumos de campo.")

    # Exibição visual das amostras detectadas
    st.markdown("---")
    st.markdown("#### 🖼️ Resultados Visuais das Bounding Boxes Geradas")
    
    img_garrafa = BASE_DIR / "src" / "fase6_vision" / "resultado_garrafa.jpg"
    img_caneca = BASE_DIR / "src" / "fase6_vision" / "resultado_caneca.jpg"

    c_img1, c_img2 = st.columns(2)
    with c_img1:
        if img_garrafa.exists():
            st.image(str(img_garrafa), caption="Detecção Real: Garrafa (Insumo Agrícola) — Confiança: 96.0%", width="stretch")
    with c_img2:
        if img_caneca.exists():
            st.image(str(img_caneca), caption="Detecção Real: Caneca (Utensílio de Coleta) — Confiança: 94.0%", width="stretch")



# ─── ABA 6: FASE 7 — MENSAGERIA E ALERTAS CLOUD AWS (SNS) ─────────────────────
with tab_aws:
    st.markdown("### 🚨 Fase 7: Central de Alertas na Nuvem (Amazon SNS)")
    st.write("Serviço de mensageria na AWS para notificação imediata de operadores da fazenda via E-mail e SMS.")

    st.markdown(f"**Tópico Ativo:** `arn:aws:sns:us-east-1:608221021260:FarmTechAlertas` *(Região: US East - N. Virginia / Provisionado via AWS Academy)*")

    with st.form("form_alerta_aws"):
        f_origem = st.selectbox(
            "Origem da Notificação:",
            ["Sensores IoT de Solo (Setor Café A-12)", "Visão Computacional (Setor Armazém)", "Estação Meteorológica"]
        )
        f_nivel = st.select_slider("Nível de Severidade:", options=["Informativo", "Atenção", "Crítico"], value="Crítico")
        f_diag = st.text_area("Diagnóstico Agronômico:", value="Déficit hídrico severo detectado: umidade do solo em 42% (abaixo do limiar mínimo de 60%).")
        f_acao = st.text_input("Ação Corretiva Recomendada:", value="Acionar irrigação de emergência (volume 7.2 L/m²) e aplicar calcário dolomítico.")
        
        btn_enviar = st.form_submit_button("📤 Transmitir Alerta via Amazon SNS")

        if btn_enviar:
            from src.fase7_alerts.mensageria_aws import enviar_alerta_aws
            with st.spinner("Publicando no Amazon SNS..."):
                enviar_alerta_aws(f_origem, f_nivel, f_diag, f_acao)
                st.success("✅ Alerta publicado com sucesso no Amazon SNS e transmitido aos e-mails assinados!")
                st.json({
                    "origem": f_origem,
                    "severidade": f_nivel,
                    "diagnostico": f_diag,
                    "acao_corretiva": f_acao,
                    "status": "Publicado com Sucesso"
                })

# ─── RODAPÉ INSTITUCIONAL ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#52606D; font-size:0.82rem;'>"
    "FarmTech Solutions © 2026 — FIAP Inteligência Artificial · Fase 7: A Consolidação de um Sistema"
    "</p>",
    unsafe_allow_html=True
)