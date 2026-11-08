"""FarmTech Fase 7 — painel de integração (executar na raiz com Streamlit)."""

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


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DATA = ROOT / "data" / "sensores_farmtech_v2.csv"
SERVICES = [
    ("Fase 1 · Manejo de insumos", "fase1_planejamento/manejo_insumos.py", "2\n5\n"),
    ("Fase 2 · Clima/IoT", "fase2_iot/clima.py", None),
    ("Fase 3 · Oracle", "fase3_database/ingestao_oracle.py", None),
    ("Fase 4 · Recomendações", "fase4_ml/recomendacoes.py", None),
    ("Fase 6 · Visão computacional (aba dedicada)", "fase6_vision/detector.py", None),
    ("Fase 7 · Teste local de alertas", "fase7_alerts/mensageria_aws.py", None),
]
REQUIRED = {"timestamp", "umidade", "ph", "nitrogenio", "fosforo", "potassio", "chuva", "irrigacao"}
SENSOR_LABELS = {
    "umidade": ("💧 Umidade do solo", "%"),
    "ph": ("🧪 pH do solo", ""),
    "nitrogenio": ("🌿 Nitrogênio", "mg/kg"),
    "fosforo": ("🌱 Fósforo", "mg/kg"),
    "potassio": ("⚡ Potássio", "mg/kg"),
    "chuva": ("🌧️ Chuva (0/1)", ""),
    "irrigacao": ("🚰 Irrigação (0/1)", ""),
}


@st.cache_data(ttl=30)
def read_telemetry(path: str):
    frame = pd.read_csv(path)
    missing = REQUIRED.difference(frame.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {', '.join(sorted(missing))}")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
    for column in REQUIRED - {"timestamp"}:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.dropna(subset=["timestamp"]).sort_values("timestamp")


def execute_service(script: Path, stdin: str | None = None, *,
                    args: list[str] | None = None, timeout: int = 25):
    """Executa apenas os módulos conhecidos, com limite de tempo e saída capturada."""
    try:
        result = subprocess.run(
            [sys.executable, str(script), *(args or [])], input=stdin, text=True,
            capture_output=True, cwd=ROOT, timeout=timeout,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        return result.returncode, (result.stdout + "\n" + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, f"Tempo limite de {timeout} segundos atingido. Execute esse módulo pelo terminal para investigar."
    except OSError as exc:
        return -1, f"Falha ao iniciar: {exc}"


def execute_r(script: Path):
    try:
        result = subprocess.run(["Rscript", str(script)], capture_output=True, text=True,
                                cwd=ROOT, timeout=25)
        return result.returncode, (result.stdout + "\n" + result.stderr).strip()
    except FileNotFoundError:
        return -1, "Rscript não está instalado ou não está disponível no PATH."
    except subprocess.TimeoutExpired:
        return -1, "Execução R excedeu 25 segundos."


st.set_page_config(page_title="FarmTech | Central Integrada", page_icon="🌱", layout="wide")
with st.sidebar:
    st.markdown("### 🎨 Aparência")
    theme_name = st.radio("Tema da plataforma", ["Azul-marinho", "Escuro", "Claro"],
                          horizontal=False, key="farmtech_theme")

PALETTES = {
    "Azul-marinho": {"bg": "#0b1730", "surface": "#142642", "sidebar": "#101f39",
                    "border": "#294365", "text": "#eaf3ff", "muted": "#adc4df", "accent": "#59b8ff",
                    "control": "#1b3457", "log": "#203c62"},
    "Escuro": {"bg": "#10151d", "surface": "#1c2631", "sidebar": "#151d27",
               "border": "#354353", "text": "#f2f5f9", "muted": "#b6c4d3", "accent": "#5ce0ac",
               "control": "#273543", "log": "#304151"},
    "Claro": {"bg": "#f2f7fb", "surface": "#ffffff", "sidebar": "#e7f0f9",
              "border": "#ccdae8", "text": "#18304d", "muted": "#506985", "accent": "#146bad",
              "control": "#ffffff", "log": "#f1f6fa"},
}
palette = PALETTES[theme_name]
px.defaults.template = "plotly_white" if theme_name == "Claro" else "plotly_dark"
px.defaults.color_discrete_sequence = (["#146bad", "#249a7f", "#df953f"] if theme_name == "Claro"
                                       else [palette["accent"], "#40c9a2", "#d9a451"])


def notice(message, kind="info"):
    """Aviso próprio: contraste independente dos estilos de alerta do Streamlit."""
    icons = {"info": "ℹ️", "warning": "⚠️", "success": "✅", "error": "⛔"}
    colors = {"info": "#328acb", "warning": "#db922b", "success": "#21996d", "error": "#d45959"}
    st.markdown(
        f'<div class="ft-notice" style="border-left-color:{colors[kind]} !important">'
        f'<span class="ft-notice-icon">{icons[kind]}</span>'
        f'<span class="ft-notice-text">{escape(str(message))}</span></div>',
        unsafe_allow_html=True,
    )


def themed_table(frame):
    """Tabela com fundo/contraste controlados pelo tema, sem canvas externo."""
    markup = frame.to_html(index=False, border=0, classes="ft-table", escape=True)
    st.markdown(f'<div class="ft-table-wrap">{markup}</div>', unsafe_allow_html=True)


def themed_log(output):
    # O componente nativo preserva precisamente as quebras de linha do terminal.
    st.code(output or "Sem saída textual.", language="text")


def themed_chart(fig):
    """Aplica tema completo ao Plotly (o template não cobre o fundo de todos os gráficos)."""
    fig.update_layout(
        paper_bgcolor=palette["surface"], plot_bgcolor=palette["surface"],
        font=dict(color=palette["text"]),
        title_font=dict(color=palette["text"]),
        legend=dict(font=dict(color=palette["text"])),
        margin=dict(l=30, r=25, t=55, b=35),
    )
    fig.update_xaxes(gridcolor=palette["border"], linecolor=palette["border"],
                     tickfont=dict(color=palette["muted"]), title_font=dict(color=palette["muted"]))
    fig.update_yaxes(gridcolor=palette["border"], linecolor=palette["border"],
                     tickfont=dict(color=palette["muted"]), title_font=dict(color=palette["muted"]))
    st.plotly_chart(fig, use_container_width=True)
st.markdown("""
<style>
div[data-testid="stMetric"] {border-radius:14px; padding:16px 18px;}
div[data-testid="stExpander"] {border-radius:14px;}
.service-title {font-weight:700; font-size:1.05rem;}
.ft-intro {padding:22px 26px; border-radius:18px; margin:8px 0 24px;}
.ft-intro h1 {font-size:2.25rem; font-weight:850; margin:0 0 8px;}
.ft-intro p {margin:0; font-size:0.95rem;}
.ft-notice {display:flex;align-items:flex-start;gap:12px;margin:10px 0 14px;
  padding:15px 18px;border-left:5px solid;border-radius:11px;line-height:1.55;}
.ft-notice-icon {flex:none;font-size:1.05rem;}
.ft-notice-text {font-size:0.94rem;font-weight:500;overflow-wrap:anywhere;}
.ft-table-wrap {overflow:auto;max-height:470px;margin:12px 0 18px;border-radius:12px;}
.ft-table {border-collapse:collapse;width:100%;font-size:0.9rem;}
.ft-table th,.ft-table td {padding:11px 14px;text-align:left;white-space:nowrap;}
</style>
""", unsafe_allow_html=True)
st.markdown(f"""
<style>
:root {{
  --ft-bg:{palette['bg']}; --ft-surface:{palette['surface']};
  --ft-sidebar:{palette['sidebar']}; --ft-border:{palette['border']};
  --ft-text:{palette['text']}; --ft-muted:{palette['muted']};
  --ft-accent:{palette['accent']};
  --ft-control:{palette['control']}; --ft-log:{palette['log']};
}}
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"] {{
  background-color:var(--ft-bg) !important; color:var(--ft-text) !important;
}}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {{
  background-color:var(--ft-sidebar) !important;
}}
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"] {{background:var(--ft-bg) !important;}}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,
.stApp p,.stApp label {{color:var(--ft-text);}}
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stCaptionContainer"] *,
.stApp small {{color:var(--ft-muted) !important; opacity:1 !important;}}
[data-testid="stMetric"], [data-testid="stExpander"] {{
  background:var(--ft-surface) !important;
  border:1px solid var(--ft-border) !important;
  box-shadow:0 4px 14px rgba(0,0,0,0.055) !important;
}}
[data-testid="stMetric"] {{border-radius:14px !important; padding:16px 18px !important;}}
[data-testid="stMetricLabel"] *, [data-testid="stMetricLabel"] {{color:var(--ft-muted) !important;}}
[data-testid="stMetricValue"] *, [data-testid="stMetricValue"] {{color:var(--ft-text) !important;}}
.service-title {{color:var(--ft-accent) !important;}}
.ft-intro {{background:linear-gradient(125deg,var(--ft-surface),var(--ft-sidebar)) !important;
  border:1px solid var(--ft-border) !important;}}
.ft-intro h1 {{color:var(--ft-text) !important;}}
.ft-intro p {{color:var(--ft-muted) !important;}}
.ft-notice {{background:var(--ft-surface) !important;border-top:1px solid var(--ft-border);
  border-right:1px solid var(--ft-border);border-bottom:1px solid var(--ft-border);}}
.ft-notice .ft-notice-text {{color:var(--ft-text) !important;opacity:1 !important;}}
.ft-table-wrap {{background:var(--ft-surface);border:1px solid var(--ft-border);}}
.ft-table th {{background:var(--ft-control) !important;color:var(--ft-text) !important;
  position:sticky;top:0;z-index:1;}}
.ft-table td {{background:var(--ft-surface) !important;color:var(--ft-text) !important;
  border-top:1px solid var(--ft-border);}}
.ft-table tr:hover td {{background:var(--ft-control) !important;}}
[data-testid="stTabs"] button {{color:var(--ft-muted) !important;}}
[data-testid="stTabs"] button[aria-selected="true"] {{color:var(--ft-accent) !important;}}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{background-color:var(--ft-accent) !important;}}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] details > summary,
[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"] {{
  background-color:var(--ft-control) !important;
  color:var(--ft-text) !important;
}}
[data-testid="stExpander"] summary *,
[data-testid="stExpander"] summary p {{color:var(--ft-text) !important;}}
[data-baseweb="select"], [data-baseweb="select"] > div,
[data-baseweb="select"] > div > div,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="input"], [data-baseweb="input"] > div,
[data-baseweb="textarea"], [data-baseweb="textarea"] > div,
.stApp input, .stApp textarea,
.stApp [data-testid="stTextInput"] input,
.stApp [data-testid="stTextArea"] textarea {{
  background-color:var(--ft-control) !important;
  color:var(--ft-text) !important;
  border-color:var(--ft-border) !important;
  -webkit-text-fill-color:var(--ft-text) !important;
}}
.stApp input::placeholder, .stApp textarea::placeholder {{
  color:var(--ft-muted) !important;
  -webkit-text-fill-color:var(--ft-muted) !important;
}}
[data-baseweb="select"] span, [data-baseweb="select"] svg,
[data-baseweb="select"] input, [data-baseweb="textarea"] textarea {{
  color:var(--ft-text) !important;
}}
.stApp [data-testid="stForm"] {{
  background-color:var(--ft-surface) !important;
  border:1px solid var(--ft-border) !important;
  border-radius:14px !important;
  padding:18px !important;
}}
.stApp [data-testid="stFormSubmitButton"] button,
.stApp [data-testid="stButton"] button {{
  background-color:var(--ft-control) !important;
  border-color:var(--ft-border) !important;
  color:var(--ft-text) !important;
}}
.stApp [data-testid="stFormSubmitButton"] button *,
.stApp [data-testid="stButton"] button * {{color:var(--ft-text) !important;}}
.stApp [data-testid="stButton"] button[kind="primary"],
.stApp [data-testid="stFormSubmitButton"] button[kind="primary"] {{
  background-color:var(--ft-accent) !important;
  border-color:var(--ft-accent) !important;
  color:{'#ffffff' if theme_name == 'Claro' else '#071724'} !important;
}}
.stApp [data-testid="stButton"] button[kind="primary"] *,
.stApp [data-testid="stFormSubmitButton"] button[kind="primary"] * {{
  color:{'#ffffff' if theme_name == 'Claro' else '#071724'} !important;
}}
[data-testid="stAlert"] {{
  background-color:var(--ft-surface) !important;
  border:1px solid var(--ft-border) !important;
  border-left:5px solid var(--ft-accent) !important;
  border-radius:10px !important;
}}
[data-testid="stAlert"] *,
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] strong {{
  color:var(--ft-text) !important;
  opacity:1 !important;
}}
[data-testid="stAlert"] svg {{color:var(--ft-accent) !important;}}
[data-testid="stSidebar"] [data-testid="stImage"] {{
  background:#f6fafc !important;
  padding:10px !important;
  border-radius:12px !important;
}}
[data-testid="stDataFrame"] {{border:1px solid var(--ft-border);border-radius:10px;}}
</style>
""", unsafe_allow_html=True)


def show_service_result(rel_path: str, code: int, output: str):
    """Apresenta um resultado legível e preserva a saída técnica para auditoria."""
    if code != 0:
        notice(f"O serviço terminou com erro (código {code}).", "error")
        if output:
            themed_log(output)
        return

    notice("Execução finalizada; confira abaixo se houve persistência/publicação real.")
    if "fase1_planejamento" in rel_path:
        file = ROOT / "data/dados_fazenda.csv"
        if file.exists():
            table = pd.read_csv(file)
            a, b, c = st.columns(3)
            a.metric("Culturas cadastradas", len(table))
            b.metric("Área total", f"{table['Area_m2'].sum():,.1f} m²")
            c.metric("Insumos previstos", f"{table['Insumo_L'].sum():,.1f} L")
            themed_table(table.rename(columns={"Cultura":"Cultura", "Area_m2":"Área (m²)",
                                              "Insumo_L":"Insumo (L)"}))
            if not table.empty:
                themed_chart(px.bar(table, x="Cultura", y="Insumo_L", color="Cultura",
                                    title="Insumos por cultura (L)"))
        else:
            notice("Relatório executado; CSV de culturas ainda não encontrado para visualização.")
    elif "fase3_database" in rel_path:
        if "[ORACLE REAL]" in output:
            notice("Leituras importadas por MERGE e consultadas no Oracle real.", "success")
        else:
            notice("CSV local validado; esta execução NÃO confirmou gravação no Oracle.", "warning")
        if DATA.exists():
            table = read_telemetry(str(DATA))
            a, b, c = st.columns(3)
            a.metric("Registros no CSV", len(table))
            b.metric("Umidade média", f"{table['umidade'].mean():.1f}%")
            c.metric("Acionamentos no CSV", int(table["irrigacao"].sum()))
    elif "fase4_ml" in rel_path:
        lines = [line.strip().lstrip("• ") for line in output.splitlines()
                 if line.strip().startswith(("•", "✅", "⚠️", "💧", "🧪", "🌿", "🌧️"))]
        if lines:
            st.subheader("Recomendações do serviço")
            for line in lines:
                notice(line)
        else:
            st.write("A saída do módulo está disponível no log técnico.")
        st.caption("O módulo atual utiliza regras agronômicas, não inferência de modelo treinado.")
    elif "fase6_vision" in rel_path:
        notice("Para inferência YOLO real, abra a aba 'Visão computacional' e envie uma imagem.")
    elif "fase7_alerts" in rel_path:
        if "SNS MessageId:" in output:
            notice("O serviço informou publicação no SNS. Confirme o recebimento no destino.", "success")
        else:
            notice("Não há confirmação de publicação real: resultado local ou simulado.", "warning")
        st.caption("Publicação no SNS e entrega efetiva de e-mail/SMS são etapas diferentes.")
    else:
        st.subheader("Resumo da execução")
        meaningful = [line.strip() for line in output.splitlines()
                      if line.strip() and not line.strip().startswith(("=", "-"))]
        for line in meaningful[:12]:
            st.write("•", line)
        if not meaningful:
            notice("Serviço concluído sem mensagens para exibir.")

    if st.checkbox("🔎 Mostrar log técnico completo", key=f"log_{rel_path}"):
        themed_log(output)


st.markdown("""
<div class="ft-intro">
  <h1>🌱 FarmTech Solutions</h1>
  <p>Central agrícola integrada · Sensores, planejamento, análise de cenários e serviços · FIAP Fase 7</p>
</div>
""", unsafe_allow_html=True)
st.caption("Fase 7 · integração Oracle + YOLO + SNS · arquivo histórico de sensores")
with st.sidebar:
    logo = ROOT / "docs/assets/logo.png"
    if logo.exists():
        st.image(str(logo), width=160)
    else:
        st.title("🌱 FarmTech")
    st.markdown("### Plataforma integrada")
    st.write("**Culturas de estudo:** café e soja")
    st.caption("Projeto acadêmico FIAP · Fase 7")
    st.divider()
    notice("Os sensores exibem dados históricos locais até a integração IoT definitiva.")

tab_data, tab_farm, tab_sim, tab_vision, tab_services, tab_alerts = st.tabs([
    "📊 Sensores", "🌾 Planejamento", "🧪 Simular cenários", "📷 Visão computacional", "⚙️ Serviços", "🚨 Alertas"
])

with tab_data:
    if not DATA.is_file():
        notice(f"Aguardando arquivo de telemetria: {DATA.relative_to(ROOT)}", "warning")
    else:
        try:
            df = read_telemetry(str(DATA))
            if df.empty:
                notice("CSV sem registros com datas válidas.", "warning")
            else:
                last = df.iloc[-1]
                st.subheader("📡 Visão operacional da lavoura")
                a, b, c, d = st.columns(4)
                a.metric("Umidade", f"{last['umidade']:.1f}%")
                b.metric("pH", f"{last['ph']:.2f}")
                c.metric("Irrigação", "Ligada" if last["irrigacao"] == 1 else "Desligada")
                d.metric("Registros", len(df))

                e, f, g = st.columns(3)
                e.metric("Nitrogênio", f"{last['nitrogenio']:.1f} mg/kg")
                f.metric("Fósforo", f"{last['fosforo']:.1f} mg/kg")
                g.metric("Potássio", f"{last['potassio']:.1f} mg/kg")

                updated_at = last["timestamp"].strftime("%d/%m/%Y às %H:%M")
                start_at = df["timestamp"].iloc[0].strftime("%d/%m/%Y")
                st.caption(f"Última leitura do arquivo: **{updated_at}** · Histórico desde {start_at} · Fonte: CSV local")
                notice("Os indicadores refletem o arquivo histórico disponível, não leituras ao vivo do ESP32.")

                st.markdown("#### 🩺 Diagnóstico rápido (limiares acadêmicos)")
                diagnostic = []
                if pd.notna(last["umidade"]):
                    if last["umidade"] < 60 and last["chuva"] != 1:
                        diagnostic.append("💧 Umidade abaixo de 60% sem chuva registrada: verificar necessidade de irrigação.")
                    elif last["umidade"] > 80:
                        diagnostic.append("💧 Umidade acima de 80%: verificar possível excesso hídrico.")
                if pd.notna(last["ph"]) and not 5.5 <= last["ph"] <= 7:
                    diagnostic.append("🧪 pH fora do intervalo demonstrativo de 5,5 a 7,0.")
                for column, minimum in (("nitrogenio", 80), ("fosforo", 30), ("potassio", 100)):
                    if pd.notna(last[column]) and last[column] < minimum:
                        diagnostic.append(f"🌿 {SENSOR_LABELS[column][0]} abaixo da referência de estudo ({minimum} mg/kg).")
                if diagnostic:
                    for message in diagnostic:
                        notice(message, "warning")
                else:
                    notice("Nenhum desvio identificado pelas regras demonstrativas na última leitura.", "success")

                with st.expander("🧾 Qualidade e cobertura dos dados"):
                    total_missing = int(df[list(SENSOR_LABELS)].isna().sum().sum())
                    q1, q2, q3 = st.columns(3)
                    q1.metric("Linhas válidas com data", len(df))
                    q2.metric("Campos numéricos ausentes", total_missing)
                    q3.metric("Grandezas disponíveis", len(SENSOR_LABELS))
                    st.caption("Registros sem data válida são descartados na importação. Números inválidos são convertidos em valores ausentes.")

                st.markdown("#### Visão geral da irrigação")
                pie = go.Figure(go.Pie(
                    labels=["Irrigação ligada", "Irrigação desligada"],
                    values=[int((df["irrigacao"] == 1).sum()), int((df["irrigacao"] == 0).sum())],
                    hole=0.55, marker_colors=["#24b47e", "#d9973b"],
                ))
                pie.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                                  showlegend=True, paper_bgcolor=palette["surface"],
                                  plot_bgcolor=palette["surface"],
                                  font=dict(color=palette["text"]))
                themed_chart(pie)

                st.divider()
                st.subheader("🔎 Explorador de sensores")
                st.caption("Escolha uma ou várias grandezas para analisar. Cada gráfico mantém sua própria unidade.")
                options = list(SENSOR_LABELS)
                selected = st.multiselect(
                    "Variáveis para análise", options=options,
                    default=["umidade", "ph", "nitrogenio", "fosforo", "potassio"],
                    format_func=lambda name: SENSOR_LABELS[name][0],
                )
                period = st.date_input(
                    "Período de análise",
                    value=(df["timestamp"].min().date(), df["timestamp"].max().date()),
                    min_value=df["timestamp"].min().date(),
                    max_value=df["timestamp"].max().date(),
                )
                filtered = df
                if isinstance(period, (tuple, list)) and len(period) == 2:
                    start, end = period
                    filtered = df[(df["timestamp"].dt.date >= start) &
                                  (df["timestamp"].dt.date <= end)]
                st.caption(f"{len(filtered)} registros no período escolhido · Fonte: CSV histórico")

                if not selected:
                    notice("Selecione ao menos uma variável para visualizar os gráficos.")
                elif filtered.empty:
                    notice("Não há medições no período selecionado.", "warning")
                else:
                    for name in selected:
                        label, unit = SENSOR_LABELS[name]
                        values = filtered[name].dropna()
                        if values.empty:
                            notice(f"{label}: sem valores válidos no período.", "warning")
                            continue
                        st.markdown(f"#### {label}")
                        x, y, z = st.columns(3)
                        x.metric("Última medição no período", f"{values.iloc[-1]:.2f} {unit}".strip())
                        y.metric("Média no período", f"{values.mean():.2f} {unit}".strip())
                        z.metric("Mínimo / máximo", f"{values.min():.2f} / {values.max():.2f}")
                        chart = px.line(filtered, x="timestamp", y=name,
                                        markers=len(filtered) <= 70,
                                        title=f"Histórico — {label}", labels={"timestamp":"Data e hora", name: label})
                        if name in ("chuva", "irrigacao"):
                            chart.update_traces(line_shape="hv")
                            chart.update_yaxes(tickvals=[0, 1], range=[-0.1, 1.1])
                        themed_chart(chart)

                with st.expander("📋 Ver dados detalhados do período"):
                    themed_table(filtered[["timestamp", *selected]].tail(100))

                st.subheader("Recomendações a partir da última leitura")
                module = ROOT / "src/fase4_ml/recomendacoes.py"
                if module.exists():
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("farmtech_recomendacoes", module)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        if hasattr(mod, "gerar_recomendacoes_agronomicas"):
                            items = mod.gerar_recomendacoes_agronomicas(
                                last["umidade"], last["ph"], last["nitrogenio"],
                                last["fosforo"], last["potassio"], int(last["chuva"])
                            )
                            for item in items:
                                st.write("-", item)
                        else:
                            notice("Módulo encontrado, mas a função de recomendações ainda não está disponível.")
                else:
                    notice("Aguardando integração do módulo de recomendações da Fase 4.")
                st.caption("As recomendações são regras demonstrativas, não um modelo preditivo treinado.")
        except (OSError, ValueError, KeyError) as exc:
            notice(f"Não foi possível carregar a telemetria: {exc}", "error")

    st.divider()
    with st.expander("🗄️ Consultar medições persistidas no Oracle (Fase 3)"):
        st.caption("Consulta ao banco REAL; não usa o CSV local para gerar a tabela de resultados.")
        if st.button("🔎 Buscar últimas 10 leituras no Oracle"):
            try:
                from src.fase3_database.conexao import conectar_oracle
                from src.fase3_database.ingestao_oracle import listar_ultimas_leituras
                with conectar_oracle() as conn:
                    linhas_oracle = listar_ultimas_leituras(conn, 10)
                if linhas_oracle:
                    themed_table(pd.DataFrame(linhas_oracle))
                    notice(f"{len(linhas_oracle)} registro(s) consultado(s) diretamente no Oracle.", "success")
                else:
                    notice("Conexão efetuada, mas tabela sem leituras.", "warning")
            except Exception as exc:
                notice(f"Consulta Oracle falhou: {exc}", "error")

with tab_farm:
    st.subheader("📐 Planejamento agrícola — Fase 1")
    st.caption("Calculadora de cenários independente do cadastro oficial: nenhum dado é gravado.")
    left, right = st.columns(2)
    with left:
        culture = st.radio("Cultura", ["Café (área retangular)", "Soja (pivô circular)"],
                           horizontal=True)
        if culture.startswith("Café"):
            length = st.number_input("Comprimento (m)", min_value=0.1, value=100.0)
            width = st.number_input("Largura (m)", min_value=0.1, value=50.0)
            rows = st.number_input("Ruas de plantio", min_value=1, value=25, step=1)
            dosage = st.number_input("Dosagem (mL por metro de rua)", min_value=0.0, value=100.0)
            area = length * width
            supply = length * rows * dosage / 1000
        else:
            radius = st.number_input("Raio do pivô (m)", min_value=0.1, value=80.0)
            dosage = st.number_input("Dosagem (mL por m²)", min_value=0.0, value=50.0)
            area = math.pi * radius**2
            supply = area * dosage / 1000
        x, y = st.columns(2)
        x.metric("Área calculada", f"{area:,.1f} m²")
        y.metric("Insumos estimados", f"{supply:,.1f} L")
    with right:
        st.markdown("#### Culturas cadastradas")
        farm_csv = ROOT / "data/dados_fazenda.csv"
        if farm_csv.exists():
            try:
                farm_df = pd.read_csv(farm_csv)
                themed_table(farm_df)
                if {"Cultura", "Insumo_L"}.issubset(farm_df.columns):
                    themed_chart(px.bar(farm_df, x="Cultura", y="Insumo_L",
                                        title="Insumos cadastrados (L)"))
            except (OSError, ValueError) as exc:
                notice(f"Não foi possível ler o cadastro: {exc}", "error")
        else:
            notice("Aguardando data/dados_fazenda.csv.")

    st.markdown("#### Análise estatística em R")
    r_script = ROOT / "src/fase1_planejamento/analise_estatistica.R"
    if st.button("▶ Executar script R", disabled=not r_script.exists()):
        st.session_state["result_r"] = execute_r(r_script)
    if not r_script.exists():
        st.caption("Aguardando o script R na pasta da Fase 1.")
    if "result_r" in st.session_state:
        r_code, r_output = st.session_state["result_r"]
        notice("Análise R concluída" if r_code == 0 else "Não foi possível concluir a análise R",
               "success" if r_code == 0 else "error")
        with st.expander("Ver relatório R"):
            themed_log(r_output)

with tab_sim:
    st.subheader("🧪 Simulador de cenários agrícolas — Fase 4")
    st.caption("Análise hipotética com regras do módulo de recomendações; não é previsão de modelo treinado.")
    a, b = st.columns(2)
    with a:
        sim_h = st.slider("Umidade (%)", 0.0, 100.0, 52.0)
        sim_ph = st.slider("pH", 3.0, 10.0, 5.8, 0.1)
        sim_n = st.slider("Nitrogênio (mg/kg)", 0.0, 200.0, 70.0)
        sim_p = st.slider("Fósforo (mg/kg)", 0.0, 150.0, 25.0)
        sim_k = st.slider("Potássio (mg/kg)", 0.0, 250.0, 85.0)
        sim_rain = st.radio("Chuva", [0, 1], format_func=lambda v: "Sim" if v else "Não",
                            horizontal=True)
    with b:
        st.markdown("#### Ações sugeridas")
        rec_file = ROOT / "src/fase4_ml/recomendacoes.py"
        if rec_file.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("farmtech_simulador", rec_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for advice in module.gerar_recomendacoes_agronomicas(
                    sim_h, sim_ph, sim_n, sim_p, sim_k, sim_rain
                ):
                    notice(advice)
            except (ImportError, AttributeError, OSError, ValueError) as exc:
                notice(f"Módulo de recomendações indisponível: {exc}", "error")
        else:
            notice("Aguardando o módulo de recomendações da Fase 4.", "warning")
        st.caption("Valores e doses são apenas demonstrações acadêmicas.")

with tab_vision:
    st.subheader("📷 Inferência real — YOLOv5 (Fase 6)")
    st.caption("Modelo do notebook Fase 6: garrafa/caneca, imagem 320 px, limiar ajustável. Não utiliza dados simulados.")
    from src.fase6_vision.detector import analisar_imagem, configuracao_modelo
    from src.fase3_database.conexao import conectar_oracle, garantir_tabelas
    from src.fase3_database.deteccoes_oracle import salvar_deteccoes, listar_deteccoes

    try:
        caminho_pesos, caminho_repo = configuracao_modelo()
        notice(f"Modelo configurado: {caminho_pesos.name} · YOLOv5 local disponível", "success")
        disponivel_modelo = True
    except FileNotFoundError as exc:
        notice(str(exc), "warning")
        disponivel_modelo = False

    arquivo_upload = st.file_uploader("Imagem de campo para classificação de objetos",
                                      type=["jpg", "jpeg", "png", "bmp", "webp"],
                                      key="visao_upload")
    minimo_conf = st.slider("Confiança mínima da detecção", 0.05, 0.95, 0.25, 0.05)
    gravar_oracle = st.checkbox("Persistir caixas detectadas no Oracle", key="gravar_deteccoes_oracle")
    if st.button("▶ Analisar imagem com YOLOv5", type="primary",
                 disabled=not (disponivel_modelo and arquivo_upload)):
        import tempfile
        try:
            if arquivo_upload.size > 15 * 1024 * 1024:
                raise ValueError("Envie uma imagem de até 15 MB.")
            with tempfile.TemporaryDirectory(prefix="farmtech_upload_") as temp:
                extensao = Path(arquivo_upload.name).suffix.lower()
                origem = Path(temp) / f"imagem{extensao}"
                origem.write_bytes(arquivo_upload.getvalue())
                with st.spinner("Executando YOLOv5 real com os pesos treinados..."):
                    resultado = analisar_imagem(origem, confianca_minima=minimo_conf)
            resultado["arquivo"] = Path(arquivo_upload.name).name
            resultado["gravado_oracle"] = None
            st.session_state["visao_resultado"] = resultado
            if gravar_oracle:
                with conectar_oracle() as conn:
                    garantir_tabelas(conn)
                    gravadas = salvar_deteccoes(
                        conn, resultado["arquivo"], resultado["deteccoes"], resultado["modelo"]
                    )
                resultado["gravado_oracle"] = gravadas
        except Exception as exc:
            notice(f"Não foi possível concluir a análise/persistência: {exc}", "error")
    if "visao_resultado" in st.session_state:
        resultado = st.session_state["visao_resultado"]
        st.subheader("Resultado da inferência")
        x, y = st.columns(2)
        x.metric("Objetos identificados", len(resultado["deteccoes"]))
        y.metric("Modelo utilizado", resultado["modelo"])
        if resultado["gravado_oracle"] is not None:
            notice(f"{resultado['gravado_oracle']} detecção(ões) gravada(s) no Oracle real.", "success")
        st.image(resultado["imagem_anotada"], caption=resultado["arquivo"],
                 use_container_width=True)
        if resultado["deteccoes"]:
            themed_table(pd.DataFrame([
                {"Classe": d["classe"], "Confiança (%)": round(d["confianca"] * 100, 2),
                 "Box (x1,y1,x2,y2)": str(d["box"])} for d in resultado["deteccoes"]
            ]))
        else:
            notice("O modelo executou corretamente, mas não identificou objetos acima do limiar.")
        st.download_button("Baixar imagem anotada", data=resultado["imagem_anotada"],
                           file_name=f"resultado_{resultado['arquivo']}",
                           mime="image/png" if resultado["arquivo"].lower().endswith(".png") else "image/jpeg")

    if st.button("🔎 Consultar histórico de detecções Oracle"):
        try:
            with conectar_oracle() as conn:
                registros = listar_deteccoes(conn, limite=30)
            if registros:
                themed_table(pd.DataFrame(registros))
            else:
                notice("Tabela acessível, mas ainda não há detecções armazenadas.")
        except Exception as exc:
            notice(f"Consulta Oracle indisponível: {exc}", "error")

with tab_services:
    st.subheader("Central de operações")
    st.caption("Execute os serviços e consulte seus resultados em painéis visuais. Logs técnicos continuam disponíveis para depuração.")
    available = sum((ROOT / "src" / path).is_file() for _, path, _ in SERVICES)
    a, b = st.columns(2)
    a.metric("Serviços disponíveis", f"{available}/{len(SERVICES)}")
    b.metric("Aguardando integração", len(SERVICES) - available)
    for title, rel_path, stdin in SERVICES:
        script = ROOT / "src" / rel_path
        exists = script.is_file()
        with st.expander(f"{'✅' if exists else '⏳'} {title}", expanded=False):
            if not exists:
                notice("Aguardando arquivo do integrante responsável.")
            if "fase6_vision" in rel_path:
                notice("Envie uma imagem na aba 'Visão computacional'. O detector não fabrica resultados.")
            if st.button("▶ Executar e visualizar", key=rel_path,
                         disabled=(not exists or "fase6_vision" in rel_path),
                         type="primary"):
                with st.spinner("Executando..."):
                    code, output = execute_service(script, stdin)
                st.session_state[f"result_{rel_path}"] = (code, output)
            result = st.session_state.get(f"result_{rel_path}")
            if result is not None:
                show_service_result(rel_path, *result)

with tab_alerts:
    st.subheader("🚨 Alertas automáticos baseados no CSV de sensores")
    from src.fase7_alerts.regras_alerta import avaliar_leitura, ultima_leitura_csv
    from src.fase7_alerts.mensageria_aws import ultima_leitura_oracle
    fonte_alerta = st.radio(
        "Fonte dos dados para avaliar e enviar alertas",
        ["CSV histórico", "Oracle (Fase 3)"], horizontal=True,
        key="sns_fonte_dados",
    )
    fonte_codigo = "oracle" if fonte_alerta.startswith("Oracle") else "csv"
    try:
        leitura_alertas = (ultima_leitura_oracle() if fonte_codigo == "oracle"
                           else ultima_leitura_csv(DATA))
        eventos_alerta = avaliar_leitura(leitura_alertas)
        st.caption(f"Última leitura da fonte {fonte_alerta}: {leitura_alertas['timestamp']} — atualização conforme a origem.")
        if eventos_alerta:
            for evento in eventos_alerta:
                notice(f"{evento['nivel']}: {evento['detalhes']} Ação: {evento['acao_corretiva']}", "warning")
            st.caption(f"{len(eventos_alerta)} alerta(s) gerado(s) automaticamente por regras verificáveis.")
        else:
            notice("Nenhuma condição de alerta na última leitura do CSV.", "success")
        confirmar_envio = st.checkbox(
            "Confirmo que configurei o tópico SNS real e autorizo enviar os alertas por e-mail/SMS assinados.",
            key="sns_confirmacao",
        )
        if st.button("📨 Publicar alertas detectados no AWS SNS", type="primary",
                     disabled=not (eventos_alerta and confirmar_envio)):
            with st.spinner("Publicando eventos elegíveis no SNS..."):
                codigo, log = execute_service(
                    ROOT / "src/fase7_alerts/mensageria_aws.py",
                    args=["--enviar", "--fonte", fonte_codigo], timeout=45
                )
            st.session_state["alerta_resultado_real"] = (codigo, log)
        if "alerta_resultado_real" in st.session_state:
            codigo, log = st.session_state["alerta_resultado_real"]
            notice("Processo SNS concluído; verifique a entrega na caixa postal." if codigo == 0
                   else "Falha no processamento do SNS; consulte o log.",
                   "success" if codigo == 0 else "error")
            themed_log(log)
        st.caption("Eventos já publicados ficam registrados em data/alertas_sns_enviados.json para evitar reenvio.")
    except Exception as exc:
        notice(f"Falha ao avaliar os dados de sensores: {exc}", "error")
    st.divider()
    st.subheader("✉️ Prévia de mensagem personalizada (não envia)")
    st.caption("Monte uma mensagem de teste e visualize o conteúdo antes de qualquer publicação.")
    with st.form("alert_preview"):
        origin = st.selectbox("Origem", ["Sensores de solo", "Visão computacional", "Clima"])
        severity = st.select_slider("Severidade", options=["Informativo", "Atenção", "Crítico"])
        details = st.text_area("Diagnóstico", value="Umidade do solo abaixo do limiar demonstrativo.")
        action = st.text_input("Ação sugerida", value="Verificar irrigação e inspecionar sensores.")
        preview = st.form_submit_button("👁️ Pré-visualizar mensagem")
    if preview:
        module_path = ROOT / "src/fase7_alerts/mensageria_aws.py"
        if module_path.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("farmtech_alert_preview", module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                subject, body, sms = module.formatar_mensagem_alerta(
                    origin, severity, details, action
                )
                st.write("**Assunto:**", subject)
                st.text_area("Prévia de e-mail", body, height=290)
                st.text_area("Prévia de SMS", sms, height=90)
                notice("Prévia gerada localmente. Nenhuma mensagem foi enviada.", "success")
            except (ImportError, AttributeError, OSError, ValueError) as exc:
                notice(f"Não foi possível preparar a prévia: {exc}", "error")
        else:
            notice("Aguardando o módulo de mensageria do Integrante 5.", "warning")
    notice("Publicação real requer tópico SNS configurado e confirmação no botão de envio acima.")
    notice("Uma simulação ou resposta positiva de publish não comprova recebimento de e-mail/SMS.", "warning")
