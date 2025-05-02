import streamlit as st
import pandas as pd
from utils.api_client import obtener_datos_desde_api
from plots.grafico_prueba import grafico_barra

st.set_page_config(page_title="Créditos Colombia", layout="wide")
st.title("💰 Dashboard de Créditos - Datos Abiertos de Colombia")

# Paso 1: Cargar datos
with st.spinner("🔄 Cargando datos desde la API..."):
    df = obtener_datos_desde_api()
    st.success("✅ Datos cargados correctamente")

# Conversión de tipos
df["tasa_efectiva_promedio"] = pd.to_numeric(df["tasa_efectiva_promedio"], errors="coerce")
df["fecha_corte"] = pd.to_datetime(df["fecha_corte"], errors="coerce")

# Convertir campos categóricos a string
df["tipo_de_cr_dito"] = df["tipo_de_cr_dito"].astype(str)
df["producto_de_cr_dito"] = df["producto_de_cr_dito"].astype(str)
df["tama_o_de_empresa"] = df["tama_o_de_empresa"].astype(str)
df["nombre_entidad"] = df["nombre_entidad"].astype(str)

# 🎛️ Filtros en el sidebar
with st.sidebar:
    st.header("🎚️ Filtros interactivos")

    # Selección de tipo de crédito
    tipo_credito_opts = sorted(df["tipo_de_cr_dito"].dropna().unique())
    tipo_credito = st.multiselect("📄 Tipo de crédito", tipo_credito_opts, default=tipo_credito_opts)

    # Selección de producto de crédito
    producto_credito_opts = sorted(df["producto_de_cr_dito"].dropna().unique())
    producto_credito = st.multiselect("🛠 Producto de crédito", producto_credito_opts, default=producto_credito_opts)

    # Selección de tamaño de empresa
    tamano_empresa_opts = sorted(df["tama_o_de_empresa"].dropna().unique())
    tamano_empresa = st.multiselect("🏢 Tamaño de empresa", tamano_empresa_opts, default=tamano_empresa_opts)

    # Selección de rango de tasa
    tasa_min = float(df["tasa_efectiva_promedio"].min())
    tasa_max = float(df["tasa_efectiva_promedio"].max())
    rango_tasa = st.slider("📉 Rango de tasa efectiva promedio", tasa_min, tasa_max, (tasa_min, tasa_max))

    # Selección de rango de fechas
    fechas_disponibles = df["fecha_corte"].dropna().sort_values()
    if not fechas_disponibles.empty:
        fecha_inicio = fechas_disponibles.min().date()
        fecha_fin = fechas_disponibles.max().date()
        rango_fechas = st.date_input(
            "📅 Rango de fecha de corte",
            (fecha_inicio, fecha_fin),
            min_value=fecha_inicio,
            max_value=fecha_fin
        )
    else:
        rango_fechas = None

# Depuración de los filtros
st.write("Filtros seleccionados:")
st.write("Tipo de Crédito:", tipo_credito)
st.write("Producto de Crédito:", producto_credito)
st.write("Tamaño de Empresa:", tamano_empresa)
st.write("Rango de Tasa:", rango_tasa)
st.write("Rango de Fechas:", rango_fechas)

# 🔍 Aplicar filtros
df_filtrado = df.copy()

# Aplicamos los filtros si tienen valores
if tipo_credito:
    df_filtrado = df_filtrado[df_filtrado["tipo_de_cr_dito"].isin(tipo_credito)]
    st.write(f"Filtrado por tipo de crédito: {len(df_filtrado)} filas restantes")

if producto_credito:
    df_filtrado = df_filtrado[df_filtrado["producto_de_cr_dito"].isin(producto_credito)]
    st.write(f"Filtrado por producto de crédito: {len(df_filtrado)} filas restantes")

if tamano_empresa:
    df_filtrado = df_filtrado[df_filtrado["tama_o_de_empresa"].isin(tamano_empresa)]
    st.write(f"Filtrado por tamaño de empresa: {len(df_filtrado)} filas restantes")

df_filtrado = df_filtrado[
    (df_filtrado["tasa_efectiva_promedio"] >= rango_tasa[0]) &
    (df_filtrado["tasa_efectiva_promedio"] <= rango_tasa[1])
]
st.write(f"Filtrado por tasa efectiva promedio: {len(df_filtrado)} filas restantes")

if rango_fechas and len(rango_fechas) == 2:
    fecha_inicio = pd.to_datetime(rango_fechas[0])
    fecha_fin = pd.to_datetime(rango_fechas[1])
    df_filtrado = df_filtrado[
        (df_filtrado["fecha_corte"] >= fecha_inicio) &
        (df_filtrado["fecha_corte"] <= fecha_fin)
    ]
    st.write(f"Filtrado por fecha de corte: {len(df_filtrado)} filas restantes")

# 📊 Visualización
st.subheader("📈 Tasa Efectiva Promedio por Entidad (Filtrada)")

if not df_filtrado.empty:
    df_agrupado = df_filtrado.groupby("nombre_entidad")["tasa_efectiva_promedio"].mean().reset_index()
    fig = grafico_barra(df_agrupado, "nombre_entidad", "tasa_efectiva_promedio", "Tasa Efectiva Promedio por Entidad")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"🔍 Filas después de aplicar filtros: {len(df_filtrado)}")
else:
    st.info("ℹ️ Usa los filtros del panel izquierdo para visualizar los datos.")
