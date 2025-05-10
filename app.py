import streamlit as st
import pandas as pd
import plotly.express as px
from utils.api_client import obtener_datos_desde_api

st.set_page_config(page_title="Créditos Colombia", layout="wide")
st.title("Dashboard de Créditos - Datos Abiertos de Colombia")

# Paso 1: Cargar datos
with st.spinner("Cargando datos desde la API..."):
    df = obtener_datos_desde_api()
    df = df.head(1000)
    st.success("Datos cargados correctamente")

# Conversión de tipos
df["tasa_efectiva_promedio"] = pd.to_numeric(df["tasa_efectiva_promedio"], errors="coerce")
df["fecha_corte"] = pd.to_datetime(df["fecha_corte"], errors="coerce")
df["montos_desembolsados"] = pd.to_numeric(df["montos_desembolsados"], errors="coerce")
df["numero_de_creditos"] = pd.to_numeric(df["numero_de_creditos"], errors="coerce")

# Convertir campos categóricos a string
categ_cols = ["tipo_de_cr_dito", "producto_de_cr_dito", "tama_o_de_empresa", "nombre_entidad",
              "tipo_de_garant_a", "antiguedad_de_la_empresa", "tipo_de_persona", "codigo_municipio"]
for col in categ_cols:
    df[col] = df[col].astype(str)

# Opciones únicas
get_opts = lambda col: sorted(df[col].dropna().unique())
tipo_credito_opts = get_opts("tipo_de_cr_dito")
producto_credito_opts = get_opts("producto_de_cr_dito")
tipo_garantia_opts = get_opts("tipo_de_garant_a")
tamano_empresa_opts = get_opts("tama_o_de_empresa")
antiguedad_opts = get_opts("antiguedad_de_la_empresa")

# 🎛️ Filtros en el sidebar
with st.sidebar:
    st.header("🎧️ Filtros Interactivos")
    with st.expander("🏦 Filtros de crédito"):
        tipo_credito = st.selectbox("Tipo de crédito", ["Todos"] + tipo_credito_opts)
        producto_credito = st.selectbox("Producto de crédito", ["Todos"] + producto_credito_opts)
        tipo_garantia = st.selectbox("Tipo de garantía", ["Todos"] + tipo_garantia_opts)

    with st.expander("🏢 Filtros de empresa"):
        tamano_empresa = st.selectbox("Tamaño de empresa", ["Todos"] + tamano_empresa_opts)
        antiguedad = st.selectbox("Antigüedad de la empresa", ["Todos"] + antiguedad_opts)

    with st.expander("📅 Otros filtros"):
        tasa_min, tasa_max = float(df["tasa_efectiva_promedio"].min()), float(df["tasa_efectiva_promedio"].max())
        rango_tasa = st.slider("Rango de tasa efectiva promedio", tasa_min, tasa_max, (tasa_min, tasa_max))

        fechas_disponibles = df["fecha_corte"].dropna().sort_values()
        if not fechas_disponibles.empty:
            fecha_inicio, fecha_fin = fechas_disponibles.min().date(), fechas_disponibles.max().date()
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
df_filtrado = df_filtrado[(df_filtrado["tasa_efectiva_promedio"] >= rango_tasa[0]) & (df_filtrado["tasa_efectiva_promedio"] <= rango_tasa[1])]
if rango_fechas:
    fecha_ini, fecha_fin = pd.to_datetime(rango_fechas[0]), pd.to_datetime(rango_fechas[1])
    df_filtrado = df_filtrado[(df_filtrado["fecha_corte"] >= fecha_ini) & (df_filtrado["fecha_corte"] <= fecha_fin)]

# 📈 Visualización general
st.subheader("📈 Tasa Efectiva Promedio por Entidad (Filtrada)")
if not df_filtrado.empty:
    df_agrupado = df_filtrado.groupby("nombre_entidad")["tasa_efectiva_promedio"].mean().reset_index()
    fig_general = px.bar(df_agrupado, x="nombre_entidad", y="tasa_efectiva_promedio", title="Tasa Promedio por Entidad")
    st.plotly_chart(fig_general, use_container_width=True)
    st.caption(f"🔍 Filas después de aplicar filtros: {len(df_filtrado)}")
else:
    st.info("ℹ️ Usa los filtros del panel izquierdo para visualizar los datos.")

# 📊 Análisis por preguntas
st.header("Análisis Específicos")

# Pregunta 1
st.subheader("Pregunta 1: ¿Cuál es la tasa de interés promedio de los créditos de consumo o vivienda en los principales bancos de mi ciudad?")
codigo_ciudad = st.selectbox("📍 Código de municipio", sorted(df["codigo_municipio"].dropna().unique()))
tipo_cred_1 = st.radio("Tipo de crédito", ["Consumo", "Vivienda"], horizontal=True)
df_1 = df_filtrado[(df_filtrado["codigo_municipio"] == codigo_ciudad) & (df_filtrado["tipo_de_cr_dito"] == tipo_cred_1)]
if not df_1.empty:
    graf_1 = df_1.groupby("nombre_entidad")["tasa_efectiva_promedio"].mean().reset_index()
    fig1 = px.bar(graf_1.sort_values("tasa_efectiva_promedio", ascending=False), x="nombre_entidad", y="tasa_efectiva_promedio", title=f"Tasa promedio - {tipo_cred_1} en municipio {codigo_ciudad}")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("No hay datos para esta ciudad y tipo de crédito.")

# Pregunta 2
st.subheader("Pregunta 2: ¿Qué tipo de crédito tiene la tasa más baja para personas naturales o empresas en el país?")
tipo_persona = st.selectbox("👤 Tipo de persona", df["tipo_de_persona"].dropna().unique())
df_2 = df_filtrado[df_filtrado["tipo_de_persona"] == tipo_persona]
graf_2 = df_2.groupby("tipo_de_cr_dito")["tasa_efectiva_promedio"].mean().reset_index().sort_values("tasa_efectiva_promedio")
fig2 = px.bar(graf_2, x="tipo_de_cr_dito", y="tasa_efectiva_promedio", title=f"Tasa promedio por tipo de crédito ({tipo_persona})")
st.plotly_chart(fig2, use_container_width=True)

# Pregunta 3
st.subheader("Pregunta 3: ¿Cómo han evolucionado las tasas de interés de los créditos de vivienda y consumo en el último trimestre?")
df_3 = df_filtrado[df_filtrado["tipo_de_cr_dito"].isin(["Consumo", "Vivienda"])]
df_3["trimestre"] = df_3["fecha_corte"].dt.to_period("Q").astype(str)
graf_3 = df_3.groupby(["trimestre", "tipo_de_cr_dito"])["tasa_efectiva_promedio"].mean().reset_index()
fig3 = px.line(graf_3, x="trimestre", y="tasa_efectiva_promedio", color="tipo_de_cr_dito", markers=True, title="📈 Evolución de tasas - Consumo vs Vivienda (por trimestre)")
st.plotly_chart(fig3, use_container_width=True)

# Pregunta 4
st.subheader("Pregunta 4: ¿Qué tipo de empresa obtiene mejores tasas para créditos comerciales?")
df_4 = df_filtrado[df_filtrado["tipo_de_cr_dito"] == "Comercial"]
graf_4 = df_4.groupby("tama_o_de_empresa")["tasa_efectiva_promedio"].mean().reset_index()
fig4 = px.bar(graf_4.sort_values("tasa_efectiva_promedio"), x="tama_o_de_empresa", y="tasa_efectiva_promedio", title="Tasa promedio por tamaño de empresa - Créditos comerciales")
st.plotly_chart(fig4, use_container_width=True)

# Pregunta 5
st.subheader("Pregunta 5: ¿Qué bancos otorgan el mayor volumen de créditos (en monto y número) para consumo o vivienda?")
df_5 = df_filtrado[df_filtrado["tipo_de_cr_dito"].isin(["Consumo", "Vivienda"])]
graf_5 = df_5.groupby("nombre_entidad").agg(total_monto=("montos_desembolsados", "sum"), total_creditos=("numero_de_creditos", "sum")).reset_index()

col1, col2 = st.columns(2)
with col1:
    fig5a = px.bar(graf_5.sort_values("total_monto", ascending=False).head(10), x="nombre_entidad", y="total_monto", title="🏦 Top bancos por monto total desembolsado")
    st.plotly_chart(fig5a, use_container_width=True)
with col2:
    fig5b = px.bar(graf_5.sort_values("total_creditos", ascending=False).head(10), x="nombre_entidad", y="total_creditos", title="🏦 Top bancos por número de créditos")
    st.plotly_chart(fig5b, use_container_width=True)
