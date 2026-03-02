"""
RADAR DE ALERTAS – CONTRATACIÓN EN SALUD (SECOP)
Prototipo MVP para detección de anomalías en contratación pública del sector salud en Colombia.
Datos híbridos: estructura real SECOP + scores simulados.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Radar de Alertas – Contratación en Salud",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS CSS PERSONALIZADOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Fuentes */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Source Sans 3', sans-serif;
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #1a2a4a 0%, #2c4a7c 100%);
        color: white;
        padding: 1.2rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(26,42,74,0.3);
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .main-header p {
        margin: 0.3rem 0 0 0;
        font-size: 0.85rem;
        opacity: 0.8;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-top: 4px solid #2c4a7c;
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    }
    .kpi-card.alert {
        border-top-color: #e74c3c;
    }
    .kpi-card.warning {
        border-top-color: #f39c12;
    }
    .kpi-card.success {
        border-top-color: #27ae60;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #5a6a7a;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.3rem;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a2a4a;
        line-height: 1.2;
    }
    .kpi-value.alert {
        color: #e74c3c;
    }
    .kpi-value.success {
        color: #27ae60;
    }
    .kpi-delta {
        font-size: 0.75rem;
        color: #888;
        margin-top: 0.2rem;
    }
    
    /* Sección títulos */
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1a2a4a;
        border-left: 4px solid #2c4a7c;
        padding-left: 0.8rem;
        margin: 1.5rem 0 0.8rem 0;
    }
    
    /* Panel explicación */
    .explanation-panel {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.2rem;
    }
    .risk-factor {
        display: flex;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #eef2f7;
    }
    .risk-factor:last-child {
        border-bottom: none;
    }
    .risk-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.8rem;
        flex-shrink: 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f0f4f8 0%, #e8eef5 100%);
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label {
        font-weight: 600;
        color: #1a2a4a;
        font-size: 0.85rem;
    }
    
    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tabla estilizada */
    .contract-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Badge riesgo */
    .risk-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }
    .risk-badge.alto { background: #e74c3c; }
    .risk-badge.medio { background: #f39c12; }
    .risk-badge.bajo { background: #27ae60; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATOS SIMULADOS (estructura real SECOP)
# ─────────────────────────────────────────────
@st.cache_data
def generar_datos_contratos(n=500):
    """Genera dataset simulado con estructura real de SECOP."""
    np.random.seed(42)
    random.seed(42)
    
    departamentos = [
        "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bolívar",
        "Boyacá", "Caldas", "Caquetá", "Casanare", "Cauca",
        "Cesar", "Chocó", "Córdoba", "Cundinamarca", "Guainía",
        "Guaviare", "Huila", "La Guajira", "Magdalena", "Meta",
        "Nariño", "Norte de Santander", "Putumayo", "Quindío",
        "Risaralda", "San Andrés", "Santander", "Sucre",
        "Tolima", "Valle del Cauca", "Vaupés", "Vichada", "Bogotá D.C."
    ]
    
    # Pesos para distribución realista (más contratos en dptos grandes)
    pesos_dept = np.random.dirichlet(np.ones(len(departamentos)) * 0.5)
    pesos_dept_dict = dict(zip(departamentos, pesos_dept))
    # Aumentar peso de Bogotá, Antioquia, Valle
    for d in ["Bogotá D.C.", "Antioquia", "Valle del Cauca", "Atlántico"]:
        if d in pesos_dept_dict:
            pesos_dept_dict[d] *= 3
    total = sum(pesos_dept_dict.values())
    pesos_norm = [pesos_dept_dict[d] / total for d in departamentos]
    
    modalidades = [
        "Contratación Directa", "Licitación Pública",
        "Selección Abreviada", "Mínima Cuantía", "Concurso de Méritos"
    ]
    
    tipos_entidad = [
        "Hospital", "ESE", "IPS", "EPS", "Secretaría de Salud",
        "Instituto Departamental de Salud", "Clínica"
    ]
    
    objetos_contrato = [
        "Suministro de medicamentos e insumos médicos",
        "Prestación de servicios de salud",
        "Mantenimiento de equipos biomédicos",
        "Servicios de aseo y desinfección hospitalaria",
        "Suministro de material médico-quirúrgico",
        "Consultoría en gestión hospitalaria",
        "Transporte asistencial de pacientes",
        "Servicios de alimentación hospitalaria",
        "Adquisición de equipos médicos",
        "Servicios de laboratorio clínico",
        "Servicios de imagenología diagnóstica",
        "Dotación de personal asistencial temporal",
    ]
    
    records = []
    for i in range(n):
        dept = np.random.choice(departamentos, p=pesos_norm)
        modalidad = np.random.choice(
            modalidades, p=[0.35, 0.15, 0.25, 0.20, 0.05]
        )
        
        # Valor del contrato (distribución log-normal realista)
        base_valor = np.random.lognormal(mean=7.5, sigma=1.2)
        valor = round(base_valor * 1000, -3)  # Redondear a miles
        valor = max(valor, 5_000_000)  # Mínimo 5M
        valor = min(valor, 15_000_000_000)  # Máximo 15B
        
        # Fecha aleatoria 2023-2025
        start_date = datetime(2023, 1, 1)
        random_days = random.randint(0, 900)
        fecha = start_date + timedelta(days=random_days)
        
        # Score de riesgo simulado
        score_base = np.random.beta(2, 5) * 100
        
        # Factores que incrementan riesgo
        if modalidad == "Contratación Directa":
            score_base += np.random.uniform(5, 20)
        if valor > 3_000_000_000:
            score_base += np.random.uniform(10, 25)
        
        score = min(round(score_base, 1), 99.5)
        
        if score >= 70:
            nivel = "Alto"
        elif score >= 40:
            nivel = "Medio"
        else:
            nivel = "Bajo"
        
        # Factores de riesgo (para panel de explicación)
        factores = {}
        factores["freq_proveedor"] = round(np.random.uniform(0, 50), 1)
        factores["valor_vs_historico"] = round(np.random.uniform(0, 40), 1)
        factores["num_oferentes"] = round(np.random.uniform(0, 25), 1)
        factores["modalidad_directa"] = round(
            np.random.uniform(5, 20) if modalidad == "Contratación Directa" else np.random.uniform(0, 5), 1
        )
        factores["variables_macro"] = round(np.random.uniform(0, 15), 1)
        
        # Normalizar factores para que sumen ~100
        total_f = sum(factores.values())
        if total_f > 0:
            factores = {k: round(v / total_f * 100, 1) for k, v in factores.items()}
        
        num_contratos_previos = random.randint(0, 15)
        
        entidad_nombre = f"{np.random.choice(tipos_entidad)} {dept}"
        
        records.append({
            "id_contrato": f"C-{random.randint(1000, 9999)}",
            "fecha": fecha,
            "anio": fecha.year,
            "mes": fecha.strftime("%b"),
            "mes_num": fecha.month,
            "departamento": dept,
            "entidad": entidad_nombre,
            "tipo_entidad": np.random.choice(tipos_entidad),
            "modalidad": modalidad,
            "objeto": np.random.choice(objetos_contrato),
            "valor": valor,
            "score_riesgo": score,
            "nivel_riesgo": nivel,
            "contratos_previos_proveedor": num_contratos_previos,
            "factor_freq_proveedor": factores["freq_proveedor"],
            "factor_valor_historico": factores["valor_vs_historico"],
            "factor_num_oferentes": factores["num_oferentes"],
            "factor_modalidad_directa": factores["modalidad_directa"],
            "factor_variables_macro": factores["variables_macro"],
            "valor_promedio_historico": round(valor * np.random.uniform(0.3, 0.8), -3),
            "num_oferentes": random.randint(1, 8),
        })
    
    return pd.DataFrame(records)


@st.cache_data
def get_colombia_dept_coords():
    """Coordenadas centrales aproximadas de departamentos colombianos."""
    return {
        "Amazonas": {"lat": -1.0, "lon": -71.9},
        "Antioquia": {"lat": 6.9, "lon": -75.6},
        "Arauca": {"lat": 7.1, "lon": -70.7},
        "Atlántico": {"lat": 10.7, "lon": -75.0},
        "Bolívar": {"lat": 8.6, "lon": -74.0},
        "Boyacá": {"lat": 5.9, "lon": -73.4},
        "Caldas": {"lat": 5.3, "lon": -75.5},
        "Caquetá": {"lat": 1.5, "lon": -75.6},
        "Casanare": {"lat": 5.3, "lon": -71.3},
        "Cauca": {"lat": 2.7, "lon": -76.8},
        "Cesar": {"lat": 9.3, "lon": -73.5},
        "Chocó": {"lat": 5.7, "lon": -76.6},
        "Córdoba": {"lat": 8.3, "lon": -75.6},
        "Cundinamarca": {"lat": 5.0, "lon": -74.0},
        "Guainía": {"lat": 2.6, "lon": -68.5},
        "Guaviare": {"lat": 2.0, "lon": -72.6},
        "Huila": {"lat": 2.5, "lon": -75.5},
        "La Guajira": {"lat": 11.4, "lon": -72.4},
        "Magdalena": {"lat": 10.0, "lon": -74.0},
        "Meta": {"lat": 3.5, "lon": -73.0},
        "Nariño": {"lat": 1.6, "lon": -77.9},
        "Norte de Santander": {"lat": 7.9, "lon": -72.5},
        "Putumayo": {"lat": 0.8, "lon": -76.0},
        "Quindío": {"lat": 4.5, "lon": -75.7},
        "Risaralda": {"lat": 5.0, "lon": -75.9},
        "San Andrés": {"lat": 12.5, "lon": -81.7},
        "Santander": {"lat": 6.9, "lon": -73.1},
        "Sucre": {"lat": 9.0, "lon": -75.4},
        "Tolima": {"lat": 3.9, "lon": -75.2},
        "Valle del Cauca": {"lat": 3.8, "lon": -76.5},
        "Vaupés": {"lat": 1.2, "lon": -70.2},
        "Vichada": {"lat": 5.0, "lon": -69.0},
        "Bogotá D.C.": {"lat": 4.7, "lon": -74.1},
    }


def formato_moneda(valor):
    """Formatea valores en pesos colombianos abreviados."""
    if valor >= 1_000_000_000:
        return f"${valor / 1_000_000_000:,.1f}B"
    elif valor >= 1_000_000:
        return f"${valor / 1_000_000:,.0f}M"
    else:
        return f"${valor:,.0f}"


def color_nivel_riesgo(nivel):
    """Retorna color hex según nivel de riesgo."""
    return {"Alto": "#e74c3c", "Medio": "#f39c12", "Bajo": "#27ae60"}.get(nivel, "#888")


# ─────────────────────────────────────────────
# CARGAR DATOS
# ─────────────────────────────────────────────
df = generar_datos_contratos(n=600)

# ─────────────────────────────────────────────
# SIDEBAR: FILTROS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filtros de búsqueda")
    st.markdown("---")
    
    # Período
    anios_disponibles = sorted(df["anio"].unique())
    periodo = st.select_slider(
        "📅 Período",
        options=anios_disponibles,
        value=(min(anios_disponibles), max(anios_disponibles)),
    )
    
    # Departamento
    depts = ["Todos"] + sorted(df["departamento"].unique().tolist())
    dept_sel = st.selectbox("📍 Departamento", depts, index=0)
    
    # Modalidad
    modalidades_lista = ["Todas"] + sorted(df["modalidad"].unique().tolist())
    modalidad_sel = st.selectbox("📋 Modalidad", modalidades_lista, index=0)
    
    # Nivel de riesgo
    niveles = ["Todos", "Alto", "Medio", "Bajo"]
    nivel_sel = st.selectbox("⚠️ Nivel de Riesgo", niveles, index=0)
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#888; font-size:0.75rem;'>"
        "Prototipo MVP v1.0<br>Datos simulados para testeo"
        "</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# APLICAR FILTROS
# ─────────────────────────────────────────────
df_filtered = df.copy()
df_filtered = df_filtered[
    (df_filtered["anio"] >= periodo[0]) & (df_filtered["anio"] <= periodo[1])
]
if dept_sel != "Todos":
    df_filtered = df_filtered[df_filtered["departamento"] == dept_sel]
if modalidad_sel != "Todas":
    df_filtered = df_filtered[df_filtered["modalidad"] == modalidad_sel]
if nivel_sel != "Todos":
    df_filtered = df_filtered[df_filtered["nivel_riesgo"] == nivel_sel]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
        <h1>🏥 RADAR DE ALERTAS – CONTRATACIÓN EN SALUD (SECOP)</h1>
        <p>Sistema de detección de anomalías en contratación pública del sector salud</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
total_contratos = len(df_filtered)
total_alertas = len(df_filtered[df_filtered["score_riesgo"] >= 40])
riesgo_alto = len(df_filtered[df_filtered["nivel_riesgo"] == "Alto"])
ahorro_potencial = df_filtered[df_filtered["nivel_riesgo"] == "Alto"]["valor"].sum() * 0.12

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Contratos Analizados</div>
            <div class="kpi-value">{total_contratos:,}</div>
            <div class="kpi-delta">Período {periodo[0]}–{periodo[1]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card warning">
            <div class="kpi-label">Alertas Generadas</div>
            <div class="kpi-value">{total_alertas:,}</div>
            <div class="kpi-delta">{total_alertas/max(total_contratos,1)*100:.1f}% del total</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card alert">
            <div class="kpi-label">Riesgo Alto Detectado</div>
            <div class="kpi-value alert">{riesgo_alto} ▲</div>
            <div class="kpi-delta">Requieren revisión prioritaria</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card success">
            <div class="kpi-label">Ahorro Pot. Auditoría</div>
            <div class="kpi-value success">{formato_moneda(ahorro_potencial)}</div>
            <div class="kpi-delta">Estimado 12% sobre riesgo alto</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FILA: MAPA + ALERTAS POR MES
# ─────────────────────────────────────────────
col_mapa, col_temporal = st.columns([1, 1])

with col_mapa:
    st.markdown('<div class="section-title">Mapa de Riesgo Contractual</div>', unsafe_allow_html=True)
    
    coords = get_colombia_dept_coords()
    dept_stats = (
        df_filtered.groupby("departamento")
        .agg(
            total_contratos=("id_contrato", "count"),
            alertas=("score_riesgo", lambda x: (x >= 40).sum()),
            riesgo_alto=("nivel_riesgo", lambda x: (x == "Alto").sum()),
            score_promedio=("score_riesgo", "mean"),
            valor_total=("valor", "sum"),
        )
        .reset_index()
    )
    
    dept_stats["lat"] = dept_stats["departamento"].map(lambda d: coords.get(d, {}).get("lat", 4.5))
    dept_stats["lon"] = dept_stats["departamento"].map(lambda d: coords.get(d, {}).get("lon", -74.0))
    dept_stats["valor_display"] = dept_stats["valor_total"].apply(formato_moneda)
    dept_stats["texto"] = dept_stats.apply(
        lambda r: (
            f"<b>{r['departamento']}</b><br>"
            f"Contratos: {r['total_contratos']}<br>"
            f"Alertas: {r['alertas']}<br>"
            f"Riesgo Alto: {r['riesgo_alto']}<br>"
            f"Score Prom.: {r['score_promedio']:.1f}<br>"
            f"Valor Total: {r['valor_display']}"
        ),
        axis=1,
    )
    
    fig_mapa = go.Figure()
    fig_mapa.add_trace(
        go.Scattergeo(
            lat=dept_stats["lat"],
            lon=dept_stats["lon"],
            text=dept_stats["texto"],
            hoverinfo="text",
            marker=dict(
                size=dept_stats["riesgo_alto"].clip(lower=3) * 2 + 8,
                color=dept_stats["score_promedio"],
                colorscale=[
                    [0, "#27ae60"],
                    [0.4, "#f1c40f"],
                    [0.7, "#e67e22"],
                    [1.0, "#e74c3c"],
                ],
                cmin=0,
                cmax=80,
                colorbar=dict(
                    title=dict(text="Score", font=dict(size=11)),
                    thickness=12,
                    len=0.5,
                    tickfont=dict(size=10),
                ),
                line=dict(width=1, color="white"),
                opacity=0.85,
            ),
        )
    )
    
    fig_mapa.update_geos(
        scope="south america",
        center=dict(lat=4.5, lon=-74.0),
        projection_scale=5.5,
        showland=True,
        landcolor="#f0f4f8",
        showocean=True,
        oceancolor="#dce6f0",
        showcountries=True,
        countrycolor="#bdc3c7",
        showcoastlines=True,
        coastlinecolor="#bdc3c7",
        showframe=False,
    )
    
    fig_mapa.update_layout(
        height=420,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
    )
    
    st.plotly_chart(fig_mapa, use_container_width=True)


with col_temporal:
    st.markdown('<div class="section-title">Alertas Detectadas por Mes</div>', unsafe_allow_html=True)
    
    alertas_mes = (
        df_filtered[df_filtered["score_riesgo"] >= 40]
        .groupby(["anio", "mes_num", "mes"])
        .size()
        .reset_index(name="alertas")
        .sort_values(["anio", "mes_num"])
    )
    alertas_mes["periodo"] = alertas_mes["mes"] + " " + alertas_mes["anio"].astype(str)
    
    # También serie de riesgo alto
    alto_mes = (
        df_filtered[df_filtered["nivel_riesgo"] == "Alto"]
        .groupby(["anio", "mes_num", "mes"])
        .size()
        .reset_index(name="riesgo_alto")
        .sort_values(["anio", "mes_num"])
    )
    alto_mes["periodo"] = alto_mes["mes"] + " " + alto_mes["anio"].astype(str)
    
    fig_temporal = go.Figure()
    
    fig_temporal.add_trace(
        go.Scatter(
            x=alertas_mes["periodo"],
            y=alertas_mes["alertas"],
            mode="lines+markers",
            name="Total Alertas",
            line=dict(color="#2c4a7c", width=2.5),
            marker=dict(size=7),
            fill="tozeroy",
            fillcolor="rgba(44,74,124,0.1)",
        )
    )
    
    fig_temporal.add_trace(
        go.Scatter(
            x=alto_mes["periodo"],
            y=alto_mes["riesgo_alto"],
            mode="lines+markers",
            name="Riesgo Alto",
            line=dict(color="#e74c3c", width=2, dash="dot"),
            marker=dict(size=6, symbol="diamond"),
        )
    )
    
    fig_temporal.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=30, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=False,
            tickangle=-45,
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#eef2f7",
            title=dict(text="Cantidad", font=dict(size=11)),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        hovermode="x unified",
    )
    
    st.plotly_chart(fig_temporal, use_container_width=True)


# ─────────────────────────────────────────────
# TABLA DE CONTRATOS PRIORIZADOS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Contratos con Mayor Probabilidad de Riesgo</div>', unsafe_allow_html=True)

# Top contratos ordenados por score
df_top = (
    df_filtered.sort_values("score_riesgo", ascending=False)
    .head(50)
    .reset_index(drop=True)
)

# Preparar tabla para display
df_display = df_top[
    ["id_contrato", "entidad", "departamento", "modalidad", "valor", "nivel_riesgo", "score_riesgo"]
].copy()
df_display["valor"] = df_display["valor"].apply(formato_moneda)
df_display["score_riesgo"] = df_display["score_riesgo"].apply(lambda x: f"{x:.1f}%")
df_display.columns = ["ID", "Entidad", "Departamento", "Modalidad", "Valor", "Riesgo", "Score"]

# Selector de contrato
st.dataframe(
    df_display,
    use_container_width=True,
    height=300,
    column_config={
        "Riesgo": st.column_config.TextColumn(
            "Riesgo",
            help="Nivel de riesgo del contrato",
        ),
        "Score": st.column_config.TextColumn(
            "Score",
            help="Probabilidad de anomalía detectada",
        ),
    },
    hide_index=True,
)

# ─────────────────────────────────────────────
# PANEL DE EXPLICACIÓN
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">¿Por qué este contrato es riesgoso?</div>', unsafe_allow_html=True)

# Selector de contrato para detalle
contratos_ids = df_top["id_contrato"].tolist()
contrato_seleccionado = st.selectbox(
    "Selecciona un contrato para ver el detalle de su alerta:",
    contratos_ids,
    index=0,
)

if contrato_seleccionado:
    contrato = df_top[df_top["id_contrato"] == contrato_seleccionado].iloc[0]
    
    col_detalle, col_factores = st.columns([1, 1])
    
    with col_detalle:
        st.markdown(
            f"""
            <div class="explanation-panel">
                <h4 style="color:#1a2a4a; margin-top:0;">📄 Contrato {contrato['id_contrato']}</h4>
                <p><strong>Entidad:</strong> {contrato['entidad']}</p>
                <p><strong>Departamento:</strong> {contrato['departamento']}</p>
                <p><strong>Modalidad:</strong> {contrato['modalidad']}</p>
                <p><strong>Objeto:</strong> {contrato['objeto']}</p>
                <p><strong>Valor:</strong> {formato_moneda(contrato['valor'])}</p>
                <p><strong>Valor Prom. Histórico:</strong> {formato_moneda(contrato['valor_promedio_historico'])}</p>
                <p><strong>No. Oferentes:</strong> {contrato['num_oferentes']}</p>
                <p><strong>Contratos previos del proveedor:</strong> {contrato['contratos_previos_proveedor']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Señales de alerta
        sobreprecio = (
            (contrato["valor"] - contrato["valor_promedio_historico"])
            / max(contrato["valor_promedio_historico"], 1)
            * 100
        )
        
        alertas_texto = []
        if sobreprecio > 50:
            alertas_texto.append(
                f"🔴 Valor {sobreprecio:.0f}% superior al promedio histórico"
            )
        if contrato["contratos_previos_proveedor"] >= 5:
            alertas_texto.append(
                f"🟠 Proveedor recurrente ({contrato['contratos_previos_proveedor']} contratos previos)"
            )
        if contrato["modalidad"] == "Contratación Directa":
            alertas_texto.append("🟠 Contratación directa sin competencia")
        if contrato["num_oferentes"] <= 2:
            alertas_texto.append(
                f"🟡 Baja competencia ({contrato['num_oferentes']} oferente{'s' if contrato['num_oferentes'] > 1 else ''})"
            )
        if sobreprecio > 100:
            alertas_texto.append("🔴 Incremento no explicado por inflación")
        
        if alertas_texto:
            st.markdown("**Señales detectadas:**")
            for alerta in alertas_texto:
                st.markdown(f"- {alerta}")
    
    with col_factores:
        st.markdown("**Factores de Riesgo (contribución al score):**")
        
        factores_data = pd.DataFrame({
            "Factor": [
                "Frecuencia con Proveedor",
                "Valor vs Prom. Histórico",
                "Nº de Oferentes",
                "Modalidad Directa",
                "Variables Macroeconómicas",
            ],
            "Peso": [
                contrato["factor_freq_proveedor"],
                contrato["factor_valor_historico"],
                contrato["factor_num_oferentes"],
                contrato["factor_modalidad_directa"],
                contrato["factor_variables_macro"],
            ],
        }).sort_values("Peso", ascending=True)
        
        colores = ["#2c4a7c", "#e74c3c", "#f39c12", "#27ae60", "#e67e22"]
        
        fig_factores = go.Figure()
        fig_factores.add_trace(
            go.Bar(
                y=factores_data["Factor"],
                x=factores_data["Peso"],
                orientation="h",
                marker=dict(
                    color=colores[: len(factores_data)],
                    line=dict(width=0),
                ),
                text=factores_data["Peso"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
                textfont=dict(size=12, color="#1a2a4a"),
            )
        )
        
        fig_factores.update_layout(
            height=300,
            margin=dict(l=10, r=60, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                showgrid=True,
                gridcolor="#eef2f7",
                range=[0, max(factores_data["Peso"]) * 1.3],
                title=dict(text="Contribución (%)", font=dict(size=11)),
            ),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
            showlegend=False,
        )
        
        st.plotly_chart(fig_factores, use_container_width=True)
        
        # Gauge del score general
        score_val = contrato["score_riesgo"]
        nivel_color = color_nivel_riesgo(contrato["nivel_riesgo"])
        
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=score_val,
                number=dict(suffix="%", font=dict(size=28)),
                title=dict(text="Score de Riesgo", font=dict(size=13)),
                gauge=dict(
                    axis=dict(range=[0, 100], tickwidth=1),
                    bar=dict(color=nivel_color),
                    bgcolor="white",
                    steps=[
                        dict(range=[0, 40], color="#e8f5e9"),
                        dict(range=[40, 70], color="#fff3e0"),
                        dict(range=[70, 100], color="#ffebee"),
                    ],
                    threshold=dict(
                        line=dict(color="black", width=2),
                        thickness=0.75,
                        value=score_val,
                    ),
                ),
            )
        )
        fig_gauge.update_layout(
            height=200,
            margin=dict(l=30, r=30, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_gauge, use_container_width=True)


# ─────────────────────────────────────────────
# DISTRIBUCIÓN POR MODALIDAD (extra útil)
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

col_mod, col_dist = st.columns(2)

with col_mod:
    st.markdown('<div class="section-title">Distribución por Modalidad</div>', unsafe_allow_html=True)
    
    mod_data = (
        df_filtered.groupby("modalidad")
        .agg(
            contratos=("id_contrato", "count"),
            riesgo_alto=("nivel_riesgo", lambda x: (x == "Alto").sum()),
        )
        .reset_index()
        .sort_values("contratos", ascending=False)
    )
    
    fig_mod = go.Figure()
    fig_mod.add_trace(
        go.Bar(
            x=mod_data["modalidad"],
            y=mod_data["contratos"],
            name="Total",
            marker_color="#2c4a7c",
            opacity=0.7,
        )
    )
    fig_mod.add_trace(
        go.Bar(
            x=mod_data["modalidad"],
            y=mod_data["riesgo_alto"],
            name="Riesgo Alto",
            marker_color="#e74c3c",
        )
    )
    fig_mod.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=20, b=80),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        barmode="overlay",
        xaxis=dict(tickangle=-25, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="#eef2f7"),
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center", font=dict(size=11)),
    )
    st.plotly_chart(fig_mod, use_container_width=True)

with col_dist:
    st.markdown('<div class="section-title">Distribución de Scores de Riesgo</div>', unsafe_allow_html=True)
    
    fig_hist = go.Figure()
    fig_hist.add_trace(
        go.Histogram(
            x=df_filtered["score_riesgo"],
            nbinsx=30,
            marker=dict(
                color=df_filtered["score_riesgo"].apply(
                    lambda x: "#e74c3c" if x >= 70 else ("#f39c12" if x >= 40 else "#27ae60")
                ),
                line=dict(width=0.5, color="white"),
            ),
            opacity=0.85,
        )
    )
    
    # Líneas de umbral
    fig_hist.add_vline(x=40, line_dash="dash", line_color="#f39c12", annotation_text="Medio", annotation_position="top")
    fig_hist.add_vline(x=70, line_dash="dash", line_color="#e74c3c", annotation_text="Alto", annotation_position="top")
    
    fig_hist.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Score de Riesgo", showgrid=False),
        yaxis=dict(title="Frecuencia", showgrid=True, gridcolor="#eef2f7"),
        showlegend=False,
    )
    st.plotly_chart(fig_hist, use_container_width=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#aaa; font-size:0.8rem; padding:1rem 0;">
        <strong>Alerta Salud Abierta</strong> · Prototipo MVP para detección de anomalías en contratación pública<br>
        Datos simulados con estructura SECOP · Proyecto académico – Universidad Javeriana · 2025
    </div>
    """,
    unsafe_allow_html=True,
)
