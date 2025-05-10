import streamlit as st
import pandas as pd
import plotly.express as px
from utils.api_client import obtener_datos_desde_api

st.set_page_config(page_title="Créditos Colombia", layout="wide")
st.title("💰 Dashboard de Créditos - Datos Abiertos de Colombia")

# Paso 1: Cargar datos
with st.spinner("🔄 Cargando datos desde la API..."):
    df = obtener_datos_desde_api()
    df = df.head(1000)  # puedes ajustar el número
    st.success("✅ Datos cargados correctamente")

# Conversión de tipos
df["tasa_efectiva_promedio"] = pd.to_numeric(df["tasa_efectiva_promedio"], errors="coerce")
df["fecha_corte"] = pd.to_datetime(df["fecha_corte"], errors="coerce")
df["montos_desembolsados"] = pd.to_numeric(df["montos_desembolsados"], errors="coerce")
df["numero_de_creditos"] = pd.to_numeric(df["numero_de_creditos"], errors="coerce")

# Convertir campos categóricos a string
df["tipo_de_cr_dito"] = df["tipo_de_cr_dito"].astype(str)
df["producto_de_cr_dito"] = df["producto_de_cr_dito"].astype(str)
df["tama_o_de_empresa"] = df["tama_o_de_empresa"].astype(str)
df["nombre_entidad"] = df["nombre_entidad"].astype(str)
df["tipo_de_garant_a"] = df["tipo_de_garant_a"].astype(str)
df["antiguedad_de_la_empresa"] = df["antiguedad_de_la_empresa"].astype(str)
df["tipo_de_persona"] = df["tipo_de_persona"].astype(str)
df["codigo_municipio"] = df["codigo_municipio"].astype(str)

# Opciones únicas
tipo_credito_opts = sorted(df["tipo_de_cr_dito"].dropna().unique())
producto_credito_opts = sorted(df["producto_de_cr_dito"].dropna().unique())
tipo_garantia_opts = sorted(df["tipo_de_garant_a"].dropna().unique())
tamano_empresa_opts = sorted(df["tama_o_de_empresa"].dropna().unique())
antiguedad_opts = sorted(df["antiguedad_de_la_empresa"].dropna().unique())

# 🎛️ Filtros en el sidebar
with st.sidebar:
    st.header("🎚️ Filtros Interactivos")

    with st.expander("🏦 Filtros de crédito"):
        tipo_credito = st.selectbox("Tipo de crédito", ["Todos"] + tipo_credito_opts)
        producto_credito = st.selectbox("Producto de crédito", ["Todos"] + producto_credito_opts)
        tipo_garantia = st.selectbox("Tipo de garantía", ["Todos"] + tipo_garantia_opts)

    with st.expander("🏢 Filtros de empresa"):
        tamano_empresa = st.selectbox("Tamaño de empresa", ["Todos"] + tamano_empresa_opts)
        antiguedad = st.selectbox("Antigüedad de la empresa", ["Todos"] + antiguedad_opts)

    with st.expander("📅 Otros filtros"):
        tasa_min = float(df["tasa_efectiva_promedio"].min())
        tasa_max = float(df["tasa_efectiva_promedio"].max())
        rango_tasa = st.slider("Rango de tasa efectiva promedio", tasa_min, tasa_max, (tasa_min, tasa_max))

        fechas_disponibles = df["fecha_corte"].dropna().sort_values()
        if not fechas_disponibles.empty:
            fecha_inicio = fechas_disponibles.min().date()
            fecha_fin = fechas_disponibles.max().date()
            rango_fechas = st.date_input("Rango de fecha de corte", (fecha_inicio, fecha_fin), min_value=fecha_inicio, max_value=fecha_fin)
        else:
            rango_fechas = None

# 🔍 Aplicar filtros
df_filtrado = df.copy()

if tipo_credito != "Todos":
    df_filtrado = df_filtrado[df_filtrado["tipo_de_cr_dito"] == tipo_credito]

if producto_credito != "Todos":
    df_filtrado = df_filtrado[df_filtrado["producto_de_cr_dito"] == producto_credito]

if tipo_garantia != "Todos":
    df_filtrado = df_filtrado[df_filtrado["tipo_de_garant_a"] == tipo_garantia]

if tamano_empresa != "Todos":
    df_filtrado = df_filtrado[df_filtrado["tama_o_de_empresa"] == tamano_empresa]

if antiguedad != "Todos":
    df_filtrado = df_filtrado[df_filtrado["antiguedad_de_la_empresa"] == antiguedad]

df_filtrado = df_filtrado[(df_filtrado["tasa_efectiva_promedio"] >= rango_tasa[0]) &
                          (df_filtrado["tasa_efectiva_promedio"] <= rango_tasa[1])]

if rango_fechas:
    fecha_ini, fecha_fin = pd.to_datetime(rango_fechas[0]), pd.to_datetime(rango_fechas[1])
    df_filtrado = df_filtrado[(df_filtrado["fecha_corte"] >= fecha_ini) & (df_filtrado["fecha_corte"] <= fecha_fin)]

# 📈 Visualización general
st.subheader("📈 Tasa Efectiva Promedio por Entidad (Filtrada)")
if not df_filtrado.empty:
    df_agrupado = df_filtrado.groupby("nombre_entidad")["tasa_efectiva_promedio"].mean().reset_index()
    fig_general = px.bar(df_agrupado, x="nombre_entidad", y="tasa_efectiva_promedio",
                         title="Tasa Promedio por Entidad")
    st.plotly_chart(fig_general, use_container_width=True)
    st.caption(f"🔍 Filas después de aplicar filtros: {len(df_filtrado)}")
else:
    st.info("ℹ️ Usa los filtros del panel izquierdo para visualizar los datos.")

# 📊 Análisis por preguntas

st.header("📊 Análisis Específicos")

# Pregunta 1
codigo_ciudad = st.selectbox("📍 Código de municipio (para análisis por ciudad)", sorted(df["codigo_municipio"].dropna().unique()))
tipo_cred_1 = st.radio("Tipo de crédito", ["Consumo", "Vivienda"], horizontal=True)
df_1 = df_filtrado[(df_filtrado["codigo_municipio"] == codigo_ciudad) &
                   (df_filtrado["tipo_de_cr_dito"] == tipo_cred_1)]
if not df_1.empty:
    graf_1 = df_1.groupby("nombre_entidad")["tasa_efectiva_promedio"].mean().reset_index()
    fig1 = px.bar(graf_1.sort_values("tasa_efectiva_promedio", ascending=False),
                  x="nombre_entidad", y="tasa_efectiva_promedio",
                  title=f"Tasa promedio - {tipo_cred_1} en municipio {codigo_ciudad}")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("No hay datos para esta ciudad y tipo de crédito.")

# Pregunta 2
tipo_persona = st.selectbox("👤 Tipo de persona", df["tipo_de_persona"].dropna().unique())
df_2 = df_filtrado[df_filtrado["tipo_de_persona"] == tipo_persona]
graf_2 = df_2.groupby("tipo_de_cr_dito")["tasa_efectiva_promedio"].mean().reset_index()
graf_2 = graf_2.sort_values("tasa_efectiva_promedio")
fig2 = px.bar(graf_2, x="tipo_de_cr_dito", y="tasa_efectiva_promedio",
              title=f"Tasa promedio por tipo de crédito ({tipo_persona})")
st.plotly_chart(fig2, use_container_width=True)

# Pregunta 3
df_3 = df_filtrado[df_filtrado["tipo_de_cr_dito"].isin(["Consumo", "Vivienda"])].copy()
df_3["trimestre"] = df_3["fecha_corte"].dt.to_period("Q").astype(str)
graf_3 = df_3.groupby(["trimestre", "tipo_de_cr_dito"])["tasa_efectiva_promedio"].mean().reset_index()
fig3 = px.line(graf_3, x="trimestre", y="tasa_efectiva_promedio", color="tipo_de_cr_dito", markers=True,
               title="📈 Evolución de tasas - Consumo vs Vivienda (por trimestre)")
st.plotly_chart(fig3, use_container_width=True)

# Pregunta 4
df_4 = df_filtrado[df_filtrado["tipo_de_cr_dito"] == "Comercial"]
graf_4 = df_4.groupby("tama_o_de_empresa")["tasa_efectiva_promedio"].mean().reset_index()
fig4 = px.bar(graf_4.sort_values("tasa_efectiva_promedio"),
              x="tama_o_de_empresa", y="tasa_efectiva_promedio",
              title="Tasa promedio por tamaño de empresa - Créditos comerciales")
st.plotly_chart(fig4, use_container_width=True)

# Pregunta 5
df_5 = df_filtrado[df_filtrado["tipo_de_cr_dito"].isin(["Consumo", "Vivienda"])]
graf_5 = df_5.groupby("nombre_entidad").agg(
    total_monto=("montos_desembolsados", "sum"),
    total_creditos=("numero_de_creditos", "sum")
).reset_index()

col1, col2 = st.columns(2)
with col1:
    fig5a = px.bar(graf_5.sort_values("total_monto", ascending=False).head(10),
                   x="nombre_entidad", y="total_monto",
                   title="🏦 Top bancos por monto total desembolsado")
    st.plotly_chart(fig5a, use_container_width=True)
with col2:
    fig5b = px.bar(graf_5.sort_values("total_creditos", ascending=False).head(10),
                   x="nombre_entidad", y="total_creditos",
                   title="🏦 Top bancos por número de créditos")
    st.plotly_chart(fig5b, use_container_width=True)
