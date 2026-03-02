"""
RADAR DE ALERTAS – CONTRATACIÓN EN SALUD (SECOP)
Dashboard Auditor – Prototipo MVP v2.0
Datos híbridos: estructura real SECOP + scores simulados.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Radar de Alertas tempranas – Contratación en Salud",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Source Sans 3', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #1a2a4a 0%, #2c4a7c 100%);
        color: white; padding: 1.2rem 2rem; border-radius: 10px;
        margin-bottom: 1.5rem; text-align: center;
        box-shadow: 0 4px 15px rgba(26,42,74,0.3);
    }
    .main-header h1 { margin: 0; font-size: 1.5rem; font-weight: 700; letter-spacing: 1px; }
    .main-header p { margin: 0.3rem 0 0 0; font-size: 0.85rem; opacity: 0.8; }

    .kpi-card {
        background: white; border-radius: 10px; padding: 0.9rem 1rem;
        text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-top: 4px solid #2c4a7c; transition: transform 0.2s ease;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,0,0,0.12); }
    .kpi-card.alert { border-top-color: #e74c3c; }
    .kpi-card.warning { border-top-color: #f39c12; }
    .kpi-card.success { border-top-color: #27ae60; }
    .kpi-card.info { border-top-color: #3498db; }
    .kpi-label {
        font-size: 0.72rem; font-weight: 600; color: #5a6a7a;
        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.2rem;
    }
    .kpi-value { font-size: 1.6rem; font-weight: 700; color: #1a2a4a; line-height: 1.2; }
    .kpi-value.alert { color: #e74c3c; }
    .kpi-value.success { color: #27ae60; }
    .kpi-value.info { color: #3498db; }
    .kpi-delta { font-size: 0.72rem; color: #888; margin-top: 0.15rem; }

    .section-title {
        font-size: 1rem; font-weight: 700; color: #1a2a4a;
        border-left: 4px solid #2c4a7c; padding-left: 0.8rem;
        margin: 1.5rem 0 0.8rem 0;
    }

    .explanation-panel {
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 10px; padding: 1.2rem;
    }

    .provider-card {
        background: white; border: 1px solid #e2e8f0;
        border-radius: 10px; padding: 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }

    .quality-bar-bg {
        background: #eef2f7; border-radius: 6px; height: 18px;
        margin: 4px 0; overflow: hidden;
    }
    .quality-bar-fill {
        height: 100%; border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.7rem; font-weight: 600; color: white;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f0f4f8 0%, #e8eef5 100%);
    }
    .chart-desc { font-size: 0.8rem; color: #6b7b8d; font-style: italic; margin-top: 0.3rem; margin-bottom: 0.5rem; line-height: 1.4; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# GENERACIÓN DE DATOS SIMULADOS
# ─────────────────────────────────────────────
@st.cache_data
def generar_datos(n=600):
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

    pesos = np.random.dirichlet(np.ones(len(departamentos)) * 0.5)
    pw = dict(zip(departamentos, pesos))
    for d in ["Bogotá D.C.", "Antioquia", "Valle del Cauca", "Atlántico"]:
        if d in pw: pw[d] *= 3
    total = sum(pw.values())
    pesos_norm = [pw[d] / total for d in departamentos]

    modalidades = ["Contratación Directa", "Licitación Pública", "Selección Abreviada", "Mínima Cuantía", "Concurso de Méritos"]
    tipos_entidad = ["Hospital", "ESE", "IPS", "EPS", "Secretaría de Salud", "Instituto Dptal Salud", "Clínica"]
    objetos = [
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

    proveedores = [f"Prov-{i:03d}" for i in range(80)]

    records = []
    for i in range(n):
        dept = np.random.choice(departamentos, p=pesos_norm)
        modalidad = np.random.choice(modalidades, p=[0.35, 0.15, 0.25, 0.20, 0.05])
        tipo_ent = np.random.choice(tipos_entidad)
        base_valor = np.random.lognormal(mean=7.5, sigma=1.2)
        valor = round(base_valor * 1000, -3)
        valor = max(valor, 5_000_000)
        valor = min(valor, 15_000_000_000)
        fecha = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 900))

        score_base = np.random.beta(2, 5) * 100
        if modalidad == "Contratación Directa":
            score_base += np.random.uniform(5, 20)
        if valor > 3_000_000_000:
            score_base += np.random.uniform(10, 25)
        score = min(round(score_base, 1), 99.5)

        if score >= 70: nivel = "Alto"
        elif score >= 40: nivel = "Medio"
        else: nivel = "Bajo"

        factores = {
            "freq_proveedor": round(np.random.uniform(0, 50), 1),
            "valor_vs_historico": round(np.random.uniform(0, 40), 1),
            "num_oferentes": round(np.random.uniform(0, 25), 1),
            "modalidad_directa": round(np.random.uniform(5, 20) if modalidad == "Contratación Directa" else np.random.uniform(0, 5), 1),
            "variables_macro": round(np.random.uniform(0, 15), 1),
        }
        total_f = sum(factores.values())
        if total_f > 0:
            factores = {k: round(v / total_f * 100, 1) for k, v in factores.items()}

        proveedor = np.random.choice(proveedores[:40] if score >= 40 else proveedores)
        entidad_nombre = f"{tipo_ent} {dept}"
        dias_publicacion = random.randint(0, 45)

        records.append({
            "id_contrato": f"C-{random.randint(1000, 9999)}",
            "fecha": fecha, "anio": fecha.year,
            "mes": fecha.strftime("%b"), "mes_num": fecha.month,
            "departamento": dept,
            "entidad": entidad_nombre,
            "tipo_entidad": tipo_ent,
            "modalidad": modalidad,
            "objeto": np.random.choice(objetos),
            "valor": valor,
            "score_riesgo": score,
            "nivel_riesgo": nivel,
            "proveedor_id": proveedor,
            "contratos_previos_proveedor": random.randint(0, 15),
            "factor_freq_proveedor": factores["freq_proveedor"],
            "factor_valor_historico": factores["valor_vs_historico"],
            "factor_num_oferentes": factores["num_oferentes"],
            "factor_modalidad_directa": factores["modalidad_directa"],
            "factor_variables_macro": factores["variables_macro"],
            "valor_promedio_historico": round(valor * np.random.uniform(0.3, 0.8), -3),
            "num_oferentes": random.randint(1, 8),
            "dias_publicacion": dias_publicacion,
            "calidad_completitud": round(np.random.uniform(50, 100), 1),
            "calidad_consistencia": round(np.random.uniform(40, 100), 1),
            "calidad_oportunidad": round(max(0, 100 - dias_publicacion * 2.5), 1),
            "calidad_estandarizacion": round(np.random.uniform(30, 100), 1),
        })

    df = pd.DataFrame(records)
    df["calidad_datos"] = round(
        df["calidad_completitud"] * 0.30 +
        df["calidad_consistencia"] * 0.25 +
        df["calidad_oportunidad"] * 0.25 +
        df["calidad_estandarizacion"] * 0.20, 1
    )
    return df


@st.cache_data
def get_coords():
    return {
        "Amazonas": {"lat": -1.0, "lon": -71.9}, "Antioquia": {"lat": 6.9, "lon": -75.6},
        "Arauca": {"lat": 7.1, "lon": -70.7}, "Atlántico": {"lat": 10.7, "lon": -75.0},
        "Bolívar": {"lat": 8.6, "lon": -74.0}, "Boyacá": {"lat": 5.9, "lon": -73.4},
        "Caldas": {"lat": 5.3, "lon": -75.5}, "Caquetá": {"lat": 1.5, "lon": -75.6},
        "Casanare": {"lat": 5.3, "lon": -71.3}, "Cauca": {"lat": 2.7, "lon": -76.8},
        "Cesar": {"lat": 9.3, "lon": -73.5}, "Chocó": {"lat": 5.7, "lon": -76.6},
        "Córdoba": {"lat": 8.3, "lon": -75.6}, "Cundinamarca": {"lat": 5.0, "lon": -74.0},
        "Guainía": {"lat": 2.6, "lon": -68.5}, "Guaviare": {"lat": 2.0, "lon": -72.6},
        "Huila": {"lat": 2.5, "lon": -75.5}, "La Guajira": {"lat": 11.4, "lon": -72.4},
        "Magdalena": {"lat": 10.0, "lon": -74.0}, "Meta": {"lat": 3.5, "lon": -73.0},
        "Nariño": {"lat": 1.6, "lon": -77.9}, "Norte de Santander": {"lat": 7.9, "lon": -72.5},
        "Putumayo": {"lat": 0.8, "lon": -76.0}, "Quindío": {"lat": 4.5, "lon": -75.7},
        "Risaralda": {"lat": 5.0, "lon": -75.9}, "San Andrés": {"lat": 12.5, "lon": -81.7},
        "Santander": {"lat": 6.9, "lon": -73.1}, "Sucre": {"lat": 9.0, "lon": -75.4},
        "Tolima": {"lat": 3.9, "lon": -75.2}, "Valle del Cauca": {"lat": 3.8, "lon": -76.5},
        "Vaupés": {"lat": 1.2, "lon": -70.2}, "Vichada": {"lat": 5.0, "lon": -69.0},
        "Bogotá D.C.": {"lat": 4.7, "lon": -74.1},
    }


def fmt_moneda(v):
    if v >= 1_000_000_000: return f"${v/1_000_000_000:,.1f}B"
    elif v >= 1_000_000: return f"${v/1_000_000:,.0f}M"
    else: return f"${v:,.0f}"

def color_riesgo(nivel):
    return {"Alto": "#e74c3c", "Medio": "#f39c12", "Bajo": "#27ae60"}.get(nivel, "#888")

def color_calidad(score):
    if score >= 75: return "#27ae60"
    elif score >= 50: return "#f39c12"
    else: return "#e74c3c"


# ─────────────────────────────────────────────
# DATOS
# ─────────────────────────────────────────────
df = generar_datos(n=600)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Filtros de búsqueda</div>', unsafe_allow_html=True)
anios = sorted(df["anio"].unique())
periodo = st.select_slider("📅 Período", options=anios, value=(min(anios), max(anios)))
depts = ["Todos"] + sorted(df["departamento"].unique().tolist())
dept_sel = st.selectbox("📍 Departamento", depts, index=0)
mods = ["Todas"] + sorted(df["modalidad"].unique().tolist())
mod_sel = st.selectbox("📋 Modalidad", mods, index=0)
niveles = ["Todos", "Alto", "Medio", "Bajo"]
nivel_sel = st.selectbox("⚠️ Nivel de Riesgo", niveles, index=0)
        

# ─────────────────────────────────────────────
# FILTROS
# ─────────────────────────────────────────────
df_f = df[(df["anio"] >= periodo[0]) & (df["anio"] <= periodo[1])].copy()
if dept_sel != "Todos":
    df_f = df_f[df_f["departamento"] == dept_sel]
if mod_sel != "Todas":
    df_f = df_f[df_f["modalidad"] == mod_sel]
if nivel_sel != "Todos":
    df_f = df_f[df_f["nivel_riesgo"] == nivel_sel]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(
    '<div class="main-header">'
    '<h1>🏥 RADAR DE ALERTAS TEMPRANAS – CONTRATACIÓN EN SALUD (SECOP)</h1>'
    '<p>Sistema de alertas tempranas para contratación pública · Vista Auditor</p>'
    '</div>',
    unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPIs (5)
# ─────────────────────────────────────────────
total_c = len(df_f)
total_alertas = len(df_f[df_f["score_riesgo"] >= 40])
r_alto = len(df_f[df_f["nivel_riesgo"] == "Alto"])
pct_directa = (len(df_f[df_f["modalidad"] == "Contratación Directa"]) / max(total_c, 1) * 100)
ahorro = df_f[df_f["nivel_riesgo"] == "Alto"]["valor"].sum() * 0.12

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Contratos Analizados</div><div class="kpi-value">{total_c:,}</div><div class="kpi-delta">3% priorizado por score</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Alertas Generadas</div><div class="kpi-value">{total_alertas:,}</div><div class="kpi-delta">{total_alertas/max(total_c,1)*100:.1f}% del total</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card alert"><div class="kpi-label">Riesgo Alto</div><div class="kpi-value alert">{r_alto} ▲</div><div class="kpi-delta">Revisión prioritaria</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-card info"><div class="kpi-label">Contratación Directa</div><div class="kpi-value info">{pct_directa:.1f}%</div><div class="kpi-delta">Del total analizado</div></div>', unsafe_allow_html=True)
with c5:
    st.markdown(f'<div class="kpi-card success"><div class="kpi-label">Potencial Ahorro Auditoría.</div><div class="kpi-value success">{fmt_moneda(ahorro)}</div><div class="kpi-delta">Est. 12% sobre riesgo alto</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FILA 2: MAPA + SERIE TEMPORAL CONTEXTUAL
# ─────────────────────────────────────────────
col_mapa, col_temp = st.columns([1, 1])

with col_mapa:
    st.markdown('<div class="section-title">Mapa de Riesgo Contractual</div>', unsafe_allow_html=True)
    coords = get_coords()
    ds = df_f.groupby("departamento").agg(
        total=("id_contrato", "count"),
        alertas=("score_riesgo", lambda x: (x >= 40).sum()),
        alto=("nivel_riesgo", lambda x: (x == "Alto").sum()),
        score_prom=("score_riesgo", "mean"),
        valor_total=("valor", "sum"),
    ).reset_index()
    ds["lat"] = ds["departamento"].map(lambda d: coords.get(d, {}).get("lat", 4.5))
    ds["lon"] = ds["departamento"].map(lambda d: coords.get(d, {}).get("lon", -74.0))
    ds["texto"] = ds.apply(lambda r: f"<b>{r['departamento']}</b><br>Contratos: {r['total']}<br>Alertas: {r['alertas']}<br>Riesgo Alto: {r['alto']}<br>Score Prom: {r['score_prom']:.1f}<br>Valor: {fmt_moneda(r['valor_total'])}", axis=1)

    fig_mapa = go.Figure(go.Scattergeo(
        lat=ds["lat"], lon=ds["lon"], text=ds["texto"], hoverinfo="text",
        marker=dict(
            size=ds["alto"].clip(lower=3) * 2 + 8,
            color=ds["score_prom"],
            colorscale=[[0,"#27ae60"],[0.4,"#f1c40f"],[0.7,"#e67e22"],[1.0,"#e74c3c"]],
            cmin=0, cmax=80,
            colorbar=dict(title=dict(text="Score", font=dict(size=10)), thickness=12, len=0.5),
            line=dict(width=1, color="white"), opacity=0.85,
        ),
    ))
    fig_mapa.update_geos(scope="south america", center=dict(lat=4.5, lon=-74.0), projection_scale=5.5, showland=True, landcolor="#f0f4f8", showocean=True, oceancolor="#dce6f0", showcountries=True, countrycolor="#bdc3c7", showframe=False)
    fig_mapa.update_layout(height=420, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="rgba(0,0,0,0)", geo=dict(bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_mapa, use_container_width=True)

with col_temp:
    st.markdown('<div class="section-title">Alertas por Mes </div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Evolución mensual. Zonas sombreadas: amarillo = cierre fiscal, rojo = pre-electoral.</div>', unsafe_allow_html=True)

    am = df_f[df_f["score_riesgo"] >= 40].groupby(["anio","mes_num","mes"]).size().reset_index(name="alertas").sort_values(["anio","mes_num"])
    am["periodo"] = am["mes"] + " " + am["anio"].astype(str)
    hm = df_f[df_f["nivel_riesgo"]=="Alto"].groupby(["anio","mes_num","mes"]).size().reset_index(name="alto").sort_values(["anio","mes_num"])
    hm["periodo"] = hm["mes"] + " " + hm["anio"].astype(str)

    fig_t = go.Figure()

    # Sombreados contextuales
    for anio in am["anio"].unique():
        # Fin de vigencia fiscal (Nov-Dic)
        nov_idx = am[(am["anio"]==anio) & (am["mes_num"]==11)]
        dic_idx = am[(am["anio"]==anio) & (am["mes_num"]==12)]
        if not nov_idx.empty:
            fig_t.add_vrect(
                x0=nov_idx["periodo"].values[0],
                x1=dic_idx["periodo"].values[0] if not dic_idx.empty else nov_idx["periodo"].values[0],
                fillcolor="rgba(241,196,15,0.12)", line_width=0,
                annotation_text="Cierre fiscal" if anio == am["anio"].min() else "",
                annotation_position="top left",
                annotation=dict(font=dict(size=9, color="#b7950b")),
            )
        # Pre-electoral Oct 2023
        if anio == 2023:
            oct_idx = am[(am["anio"]==2023) & (am["mes_num"].isin([8,9,10]))]
            if not oct_idx.empty:
                fig_t.add_vrect(
                    x0=oct_idx["periodo"].values[0], x1=oct_idx["periodo"].values[-1],
                    fillcolor="rgba(231,76,60,0.08)", line_width=0,
                    annotation_text="Pre-electoral", annotation_position="top left",
                    annotation=dict(font=dict(size=9, color="#c0392b")),
                )

    fig_t.add_trace(go.Scatter(x=am["periodo"], y=am["alertas"], mode="lines+markers", name="Total Alertas", line=dict(color="#2c4a7c", width=2.5), marker=dict(size=7), fill="tozeroy", fillcolor="rgba(44,74,124,0.1)"))
    fig_t.add_trace(go.Scatter(x=hm["periodo"], y=hm["alto"], mode="lines+markers", name="Riesgo Alto", line=dict(color="#e74c3c", width=2, dash="dot"), marker=dict(size=6, symbol="diamond")))

    fig_t.update_layout(
        height=420, margin=dict(l=20,r=20,t=10,b=60),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="#eef2f7", title=dict(text="Cantidad", font=dict(size=11))),
        legend=dict(orientation="h", y=-0.3, xanchor="right", x=1, font=dict(size=11)),
        hovermode="x unified",
    )
    st.plotly_chart(fig_t, use_container_width=True)


# ─────────────────────────────────────────────
# FILA 3: TABLA CONTRATOS PRIORIZADOS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Contratos Priorizados por Score de Riesgo</div>', unsafe_allow_html=True)

df_top = df_f.sort_values("score_riesgo", ascending=False).head(50).reset_index(drop=True)
df_disp = df_top[["id_contrato","entidad","departamento","modalidad","valor","nivel_riesgo","score_riesgo"]].copy()
df_disp["valor"] = df_disp["valor"].apply(fmt_moneda)
df_disp["score_riesgo"] = df_disp["score_riesgo"].apply(lambda x: f"{x:.1f}%")
df_disp.columns = ["ID","Entidad","Departamento","Modalidad","Valor","Riesgo","Score"]
st.dataframe(df_disp, use_container_width=True, height=300, hide_index=True)


# ─────────────────────────────────────────────
# FILA 4: PANEL DE EXPLICACIÓN
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">¿Por qué este contrato tiene riesgo?</div>', unsafe_allow_html=True)

ids = df_top["id_contrato"].tolist()
sel = st.selectbox("Selecciona un contrato para ver el detalle:", ids, index=0)

if sel:
    c = df_top[df_top["id_contrato"] == sel].iloc[0]

    col_det, col_fact = st.columns([1, 1])

    with col_det:
        st.markdown(
            f'<div class="explanation-panel">'
            f'<h4 style="color:#1a2a4a;margin-top:0;">📄 Contrato {c["id_contrato"]}</h4>'
            f'<p><strong>Entidad:</strong> {c["entidad"]}</p>'
            f'<p><strong>Departamento:</strong> {c["departamento"]}</p>'
            f'<p><strong>Modalidad:</strong> {c["modalidad"]}</p>'
            f'<p><strong>Objeto:</strong> {c["objeto"]}</p>'
            f'<p><strong>Valor:</strong> {fmt_moneda(c["valor"])}</p>'
            f'<p><strong>Valor Prom. Histórico:</strong> {fmt_moneda(c["valor_promedio_historico"])}</p>'
            f'<p><strong>No. Oferentes:</strong> {c["num_oferentes"]}</p>'
            f'<p><strong>Proveedor:</strong> {c["proveedor_id"]}</p>'
            f'<p><strong>Contratos previos proveedor:</strong> {c["contratos_previos_proveedor"]}</p>'
            f'</div>', unsafe_allow_html=True)

        sobreprecio = (c["valor"] - c["valor_promedio_historico"]) / max(c["valor_promedio_historico"], 1) * 100
        alertas = []
        if sobreprecio > 50:
            alertas.append(f"🔴 Valor {sobreprecio:.0f}% superior al promedio histórico")
        if c["contratos_previos_proveedor"] >= 5:
            alertas.append(f"🟠 Proveedor recurrente ({c['contratos_previos_proveedor']} contratos previos)")
        if c["modalidad"] == "Contratación Directa":
            alertas.append("🟠 Contratación directa sin competencia")
        if c["num_oferentes"] <= 2:
            alertas.append(f"🟡 Baja competencia ({c['num_oferentes']} oferentes)")
        if sobreprecio > 100:
            alertas.append("🔴 Incremento no explicado por inflación")
        if alertas:
            st.markdown("**Señales detectadas:**")
            for a in alertas:
                st.markdown(f"- {a}")

    with col_fact:
        st.markdown("**Factores de Riesgo (contribución al score):**")
        fd = pd.DataFrame({
            "Factor": ["Frecuencia Proveedor", "Valor vs Histórico", "Nº Oferentes", "Modalidad Directa", "Variables Macro"],
            "Peso": [c["factor_freq_proveedor"], c["factor_valor_historico"], c["factor_num_oferentes"], c["factor_modalidad_directa"], c["factor_variables_macro"]],
        }).sort_values("Peso", ascending=True)

        fig_f = go.Figure(go.Bar(
            y=fd["Factor"], x=fd["Peso"], orientation="h",
            marker=dict(color=["#2c4a7c","#e74c3c","#f39c12","#27ae60","#e67e22"]),
            text=fd["Peso"].apply(lambda x: f"{x:.1f}%"), textposition="outside",
            textfont=dict(size=12, color="#1a2a4a"),
        ))
        fig_f.update_layout(
            height=280, margin=dict(l=10,r=60,t=10,b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#eef2f7", range=[0, max(fd["Peso"])*1.3], title=dict(text="Contribución (%)", font=dict(size=11))),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)), showlegend=False,
        )
        st.plotly_chart(fig_f, use_container_width=True)

        # Gauge
        sv = c["score_riesgo"]
        nc = color_riesgo(c["nivel_riesgo"])
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=sv,
            number=dict(suffix="%", font=dict(size=28)),
            title=dict(text="Score de Riesgo", font=dict(size=13)),
            gauge=dict(
                axis=dict(range=[0,100]),
                bar=dict(color=nc), bgcolor="white",
                steps=[dict(range=[0,40], color="#e8f5e9"), dict(range=[40,70], color="#fff3e0"), dict(range=[70,100], color="#ffebee")],
                threshold=dict(line=dict(color="black", width=2), thickness=0.75, value=sv),
            ),
        ))
        fig_g.update_layout(height=200, margin=dict(l=30,r=30,t=40,b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_g, use_container_width=True)


    # ─────────────────────────────────────────────
    # FILA 5: PARES + TRAZABILIDAD + CALIDAD
    # ─────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    col_pares, col_traz, col_calidad = st.columns([1, 1, 1])

    # ── COMPARACIÓN ENTRE PARES ──
    with col_pares:
        st.markdown('<div class="section-title">Comparación con Pares</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-desc">Compara el valor de este contrato con otros del mismo tipo de entidad y modalidad.</div>', unsafe_allow_html=True)

        pares = df[(df["tipo_entidad"] == c["tipo_entidad"]) & (df["modalidad"] == c["modalidad"])]
        if len(pares) > 5:
            stats_pares = {
                "Promedio": pares["valor"].mean(),
                "Mediana": pares["valor"].median(),
                "P75": pares["valor"].quantile(0.75),
                "P95": pares["valor"].quantile(0.95),
                "Este contrato": c["valor"],
            }

            es_extremo = c["valor"] > pares["valor"].quantile(0.95)
            colores_pares = ["#bdc3c7", "#95a5a6", "#7f8c8d", "#f39c12", "#e74c3c" if es_extremo else "#2c4a7c"]

            fig_p = go.Figure(go.Bar(
                x=list(stats_pares.keys()),
                y=list(stats_pares.values()),
                marker=dict(color=colores_pares),
                text=[fmt_moneda(v) for v in stats_pares.values()],
                textposition="outside", textfont=dict(size=10),
            ))
            fig_p.update_layout(
                height=320, margin=dict(l=10,r=10,t=10,b=60),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickangle=-25, tickfont=dict(size=9)),
                yaxis=dict(showgrid=True, gridcolor="#eef2f7", title=dict(text="Valor ($)", font=dict(size=10))),
                showlegend=False,
            )
            st.plotly_chart(fig_p, use_container_width=True)

            ratio = c["valor"] / max(pares["valor"].median(), 1)
            if ratio > 2:
                st.markdown(f"⚠️ Este contrato vale **{ratio:.1f}x** la mediana de contratos similares ({c['tipo_entidad']}, {c['modalidad']})")
            elif ratio > 1.3:
                st.markdown(f"📊 **{((ratio-1)*100):.0f}%** por encima de la mediana de sus pares")
            else:
                st.markdown("✅ Valor dentro del rango esperado para contratos similares")
        else:
            st.info("Insuficientes pares para comparación (mín. 5 contratos similares)")

    # ── TRAZABILIDAD DEL PROVEEDOR ──
    with col_traz:
        st.markdown('<div class="section-title">Trazabilidad del Proveedor</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-desc">Actividad del proveedor: en cuántas entidades opera, contratos simultáneos y valor acumulado.</div>', unsafe_allow_html=True)

        prov = c["proveedor_id"]
        contratos_prov = df[df["proveedor_id"] == prov]
        n_entidades = contratos_prov["entidad"].nunique()
        n_contratos = len(contratos_prov)
        valor_total = contratos_prov["valor"].sum()
        n_dptos = contratos_prov["departamento"].nunique()
        mismo_periodo = contratos_prov[(contratos_prov["anio"] == c["anio"]) & (contratos_prov["mes_num"] == c["mes_num"])]
        n_simultaneos = len(mismo_periodo)
        score_prom_prov = contratos_prov["score_riesgo"].mean()

        st.markdown(
            f'<div class="provider-card">'
            f'<h4 style="color:#1a2a4a;margin-top:0;">🏢 {prov}</h4>'
            f'<p><strong>Total contratos:</strong> {n_contratos}</p>'
            f'<p><strong>Entidades diferentes:</strong> {n_entidades}</p>'
            f'<p><strong>Departamentos:</strong> {n_dptos}</p>'
            f'<p><strong>Valor acumulado:</strong> {fmt_moneda(valor_total)}</p>'
            f'<p><strong>Contratos simultáneos (mismo mes):</strong> {n_simultaneos}</p>'
            f'<p><strong>Score promedio riesgo:</strong> {score_prom_prov:.1f}%</p>'
            f'</div>', unsafe_allow_html=True)

        prov_alertas = []
        if n_entidades >= 4:
            prov_alertas.append(f"🔴 Presente en {n_entidades} entidades diferentes")
        if n_simultaneos >= 3:
            prov_alertas.append(f"🟠 {n_simultaneos} contratos simultáneos")
        if score_prom_prov >= 50:
            prov_alertas.append(f"🟠 Score promedio elevado ({score_prom_prov:.1f}%)")
        if n_dptos >= 3:
            prov_alertas.append(f"🟡 Opera en {n_dptos} departamentos")

        if prov_alertas:
            st.markdown("**Señales del proveedor:**")
            for a in prov_alertas:
                st.markdown(f"- {a}")
        else:
            st.markdown("✅ Sin señales destacables")

        if n_contratos > 1:
            ent_dist = contratos_prov.groupby("entidad").size().reset_index(name="n").sort_values("n", ascending=True).tail(8)
            fig_prov = go.Figure(go.Bar(
                y=ent_dist["entidad"].str[:30], x=ent_dist["n"], orientation="h",
                marker=dict(color="#2c4a7c"), text=ent_dist["n"], textposition="outside",
            ))
            fig_prov.update_layout(
                height=220, margin=dict(l=10,r=30,t=10,b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor="#eef2f7", title=dict(text="Contratos", font=dict(size=10))),
                yaxis=dict(tickfont=dict(size=9)), showlegend=False,
            )
            st.plotly_chart(fig_prov, use_container_width=True)

    # ── ÍNDICE DE CALIDAD DE DATOS ──
    with col_calidad:
        st.markdown('<div class="section-title">Calidad de Datos · Entidad</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-desc">Mide qué tan completa, consistente y oportuna es la información que esta entidad publica en SECOP II.</div>', unsafe_allow_html=True)

        entidad_c = df[df["entidad"] == c["entidad"]]
        cal_comp = entidad_c["calidad_completitud"].mean()
        cal_cons = entidad_c["calidad_consistencia"].mean()
        cal_opor = entidad_c["calidad_oportunidad"].mean()
        cal_est = entidad_c["calidad_estandarizacion"].mean()
        cal_global = entidad_c["calidad_datos"].mean()

        fig_cal = go.Figure(go.Indicator(
            mode="gauge+number", value=cal_global,
            number=dict(suffix="/100", font=dict(size=24)),
            title=dict(text="Índice Global", font=dict(size=12)),
            gauge=dict(
                axis=dict(range=[0,100]),
                bar=dict(color=color_calidad(cal_global)),
                bgcolor="white",
                steps=[dict(range=[0,50], color="#ffebee"), dict(range=[50,75], color="#fff3e0"), dict(range=[75,100], color="#e8f5e9")],
            ),
        ))
        fig_cal.update_layout(height=180, margin=dict(l=20,r=20,t=35,b=5), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_cal, use_container_width=True)

        dims = [
            ("Completitud (30%)", cal_comp),
            ("Consistencia (25%)", cal_cons),
            ("Oportunidad (25%)", cal_opor),
            ("Estandarización (20%)", cal_est),
        ]
        for nombre, valor in dims:
            col_c = color_calidad(valor)
            st.markdown(
                f'<div style="font-size:0.8rem;font-weight:600;color:#1a2a4a;margin-top:6px;">{nombre}</div>'
                f'<div class="quality-bar-bg">'
                f'<div class="quality-bar-fill" style="width:{valor:.0f}%;background:{col_c};">{valor:.0f}</div>'
                f'</div>',
                unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if cal_global < 50:
            st.markdown("🔴 **Calidad deficiente.** Información con carencias significativas. Datos poco fiables para análisis.")
        elif cal_global < 75:
            st.markdown("🟡 **Calidad mejorable.** Campos incompletos o inconsistencias. Interpretar con cautela.")
        else:
            st.markdown("🟢 **Buena calidad.** Datos consistentes y completos.")

        dias_prom = entidad_c["dias_publicacion"].mean()
        st.markdown(f"📅 Publicación promedio: **{dias_prom:.0f} días** tras firma")


# ─────────────────────────────────────────────
# DISTRIBUCIÓN POR MODALIDAD
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Distribución por Modalidad de Contratación</div>', unsafe_allow_html=True)

md = df_f.groupby("modalidad").agg(
    contratos=("id_contrato","count"),
    alto=("nivel_riesgo", lambda x: (x=="Alto").sum()),
).reset_index().sort_values("contratos", ascending=False)

fig_m = go.Figure()
fig_m.add_trace(go.Bar(x=md["modalidad"], y=md["contratos"], name="Total", marker_color="#2c4a7c", opacity=0.7))
fig_m.add_trace(go.Bar(x=md["modalidad"], y=md["alto"], name="Riesgo Alto", marker_color="#e74c3c"))
fig_m.update_layout(
    height=320, margin=dict(l=20,r=20,t=20,b=80),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    barmode="overlay",
    xaxis=dict(tickangle=-25, tickfont=dict(size=10)),
    yaxis=dict(showgrid=True, gridcolor="#eef2f7"),
    legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center", font=dict(size=11)),
)
st.plotly_chart(fig_m, use_container_width=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center; color:#aaa; font-size:0.8rem; padding:1rem 0;">'
    '<strong>Alerta Salud Abierta</strong> · Sistema de Alertas Tempranas para Contratación en Salud<br>'
    'Prototipo MVP v2.0 · Datos simulados con estructura SECOP II · Universidad Javeriana 2025'
    '</div>', unsafe_allow_html=True)
