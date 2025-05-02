import plotly.graph_objects as go

def grafico_tasas_por_entidad(df, entidad_col, tasa_col):
    # Agrupar por banco y calcular promedio, min y max
    resumen = df.groupby(entidad_col)[tasa_col].agg(['mean', 'min', 'max']).reset_index()
    resumen.columns = [entidad_col, 'Promedio', 'Mínima', 'Máxima']

    # Crear figura
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=resumen[entidad_col], y=resumen['Promedio'],
        name='Promedio', marker_color='steelblue'
    ))
    fig.add_trace(go.Bar(
        x=resumen[entidad_col], y=resumen['Mínima'],
        name='Mínima', marker_color='lightgreen'
    ))
    fig.add_trace(go.Bar(
        x=resumen[entidad_col], y=resumen['Máxima'],
        name='Máxima', marker_color='indianred'
    ))

    fig.update_layout(
        title="Tasas Efectivas por Entidad",
        xaxis_title="Entidad",
        yaxis_title="Tasa Efectiva Anual (%)",
        barmode='group',
        xaxis_tickangle=-45,
        height=600
    )

    return fig
