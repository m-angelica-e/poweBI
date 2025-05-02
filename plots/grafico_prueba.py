import plotly.express as px

def grafico_barra(df, columna_x, columna_y, titulo="Gráfico de barras"):
    fig = px.bar(df, x=columna_x, y=columna_y, title=titulo)
    return fig