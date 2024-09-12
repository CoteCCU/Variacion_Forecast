import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def create_forecast_plots(item_data, color_map, selected_weeks):
    sku_desc = item_data['SKU_Descr'].iloc[0]
    selected_sku = item_data['SKU'].iloc[0]

    subplot_titles = ("", "Semanas seleccionadas" if selected_weeks else "")
    fig = make_subplots(rows=2, cols=1, subplot_titles=subplot_titles,
                        vertical_spacing=0.2, row_heights=[0.6, 0.4])

    # Convertir todas las semanas a strings para asegurar consistencia
    forecast_weeks = set(item_data['Sem_Origen'].astype(int).unique())
    venta_real_weeks = set(item_data[item_data['Venta_Real'].notna()]['Sem_Proyectada'].astype(int).unique())
    all_weeks = sorted(forecast_weeks.union(venta_real_weeks), key=lambda x: float(x))

    add_boxplots(fig, item_data, all_weeks, color_map)
    add_venta_real(fig, item_data, all_weeks)
    
    if selected_weeks:
        add_selected_weeks_data(fig, item_data, selected_weeks, color_map, all_weeks)
    else:
        add_no_selection_annotation(fig)

    update_layout(fig, all_weeks, item_data, selected_sku, sku_desc, selected_weeks)

    return fig

def add_boxplots(fig, item_data, weeks, color_map):
    for week in weeks:
        week_data = item_data[item_data['Sem_Origen'] == week]
        fig.add_trace(go.Box(
            y=week_data['Forecast'],
            name=f'Semana {week}',
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8,
            marker_color=color_map[week]
        ), row=1, col=1)

def add_venta_real(fig, item_data, weeks):
    venta_real = item_data.groupby('Sem_Proyectada')['Venta_Real'].first().reset_index()
    venta_real = venta_real[venta_real['Venta_Real'].notna()]
    fig.add_trace(go.Scatter(
        x=[f'Semana {week}' for week in venta_real['Sem_Proyectada']],
        y=venta_real['Venta_Real'],
        mode='lines+markers',
        name='Venta Real',
        line=dict(color='red', width=2)
    ), row=1, col=1)

def add_selected_weeks_data(fig, item_data, selected_weeks, color_map, all_weeks):
    selected_weeks = sorted(selected_weeks)
    
    for target_week in selected_weeks:
        forecast_data = item_data[item_data['Sem_Proyectada'] == target_week].sort_values('Sem_Origen')
        fig.add_trace(go.Bar(
            x=forecast_data['Sem_Origen'],
            y=forecast_data['Forecast'],
            name=f'Forecast S_{target_week}',
            marker_color=color_map[target_week]
        ), row=2, col=1)

    venta_real = item_data.groupby('Sem_Proyectada')['Venta_Real'].first().reset_index()
    venta_real_seleccionadas = venta_real[venta_real['Sem_Proyectada'].isin(selected_weeks)]
    if not venta_real_seleccionadas.empty:
        fig.add_trace(go.Scatter(
            x=venta_real_seleccionadas['Sem_Proyectada'],
            y=venta_real_seleccionadas['Venta_Real'],
            mode='lines+markers',
            name='Venta Real',
            line=dict(color='red', width=2)
        ), row=2, col=1)

def add_no_selection_annotation(fig):
    fig.add_annotation(text="Seleccione una o más semanas para ver el detalle",
                       xref="paper", yref="paper",
                       x=0.5, y=0.25, showarrow=False)

def update_layout(fig, weeks, item_data, selected_item, sku_desc, selected_weeks):
    title_text = f'Variación del Forecast para {"Todos los Productos" if selected_item == "Todos" else f"el Producto {selected_item}"}'
    subtitle_text = f'Descripción del producto: {sku_desc}'

    # Ordenar las semanas para el eje x del primer gráfico
    sorted_weeks = sorted(weeks)
    
    fig.update_xaxes(
        title_text="Semana Proyectada",
        tickangle=45,
        categoryorder='array',
        categoryarray=[f'Semana {week}' for week in sorted_weeks],
        row=1, col=1
    )
    
    if selected_weeks:
        # Ordenar las semanas seleccionadas para el eje x del segundo gráfico
        sorted_selected_weeks = sorted(selected_weeks)
        fig.update_xaxes(
            title_text="Semana proyectada",
            tickangle=45,
            categoryorder='array',
            categoryarray=[f'Semana {week}' for week in sorted_selected_weeks],
            row=2, col=1
        )
    else:
        fig.update_xaxes(
            title_text="Semana proyectada",
            tickangle=45,
            row=2, col=1
        )
    
    fig.update_yaxes(title_text="Forecast", row=1, col=1)
    fig.update_yaxes(title_text="Forecast", row=2, col=1)
    fig.update_layout(
        title={
            'text': f'{title_text}<br>{subtitle_text}<br>Todas las Semanas',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        height=1000,
        margin=dict(l=50, r=50, t=100, b=100),
        xaxis_title_standoff=25,
        xaxis2_title_standoff=25
    )
