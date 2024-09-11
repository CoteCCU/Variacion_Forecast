import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import colorsys

def generate_distinct_colors(n):
    HSV_tuples = [(x*1.0/n, 0.5, 0.5) for x in range(n)]
    RGB_tuples = [colorsys.hsv_to_rgb(*x) for x in HSV_tuples]
    return ['rgb({},{},{})'.format(int(r*255), int(g*255), int(b*255)) for r, g, b in RGB_tuples]

# Generar 80 colores distintos
base_colors = (
    px.colors.qualitative.Plotly +
    px.colors.qualitative.Set1 +
    px.colors.qualitative.Set2 +
    px.colors.qualitative.Set3 +
    px.colors.qualitative.Dark24 +
    px.colors.qualitative.Light24
)

additional_colors = generate_distinct_colors(80 - len(base_colors))
color_scale = base_colors + additional_colors
color_scale = color_scale[:80]

def load_and_prepare_data(file_path):
    df = pd.read_csv(file_path)
    df = df[df['Referencia Sem'].isin(['N0'] + [f'N{str(i).zfill(2)}' for i in range(-1, 13)])]
    unique_weeks = sorted(df['Num_Sem'].unique())
    color_map = dict(zip(unique_weeks, [color_scale[i % len(color_scale)] for i in range(len(unique_weeks))]))
    return df, color_map

def create_forecast_plots(data, color_map, selected_item, selected_weeks):
    if selected_item != 'Todos':
        item_data = data[data['ITEM'] == selected_item]
        title = f"Variación del Forecast para el Item {selected_item}"
    else:
        item_data = data.groupby(['Num_Sem', 'Semana', 'Referencia Sem'])['Total'].sum().reset_index()
        title = "Suma Total del Forecast para Todos los Items"

    fig = make_subplots(rows=1, cols=1, subplot_titles=(title,))

    # Crear un diccionario para mapear 'Referencia Sem' a colores
    ref_sem_colors = {ref: color_scale[i % len(color_scale)] for i, ref in enumerate(sorted(item_data['Referencia Sem'].unique()))}

    # Graficar líneas para cada 'Referencia Sem'
    for ref_sem in sorted(item_data['Referencia Sem'].unique()):
        ref_data = item_data[item_data['Referencia Sem'] == ref_sem]
        fig.add_trace(go.Scatter(
            x=ref_data['Semana'],
            y=ref_data['Total'],
            mode='lines+markers',
            name=f'Forecast {ref_sem}',
            line=dict(color=ref_sem_colors[ref_sem])
        ))

    # Agregar venta real si está disponible y no es 'Todos'
    if selected_item != 'Todos' and 'Venta_Real' in item_data.columns:
        venta_real = item_data.groupby('Semana')['Venta_Real'].sum().reset_index()
        venta_real = venta_real[venta_real['Venta_Real'].notna()]
        fig.add_trace(go.Scatter(
            x=venta_real['Semana'],
            y=venta_real['Venta_Real'],
            mode='lines+markers',
            name='Venta Real',
            line=dict(color='red', width=2)
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Semana",
        yaxis_title="Cantidad",
        legend_title="Referencia",
        height=600
    )

    return fig