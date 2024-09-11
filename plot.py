import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_forecast_plots(item_data, color_map, selected_weeks):
    sku_desc = item_data['SKU_DESCR'].iloc[0]
    selected_item = item_data['ITEM'].iloc[0]

    subplot_titles = ("", "Semanas seleccionadas" if selected_weeks else "")
    fig = make_subplots(rows=2, cols=1, subplot_titles=subplot_titles,
                        vertical_spacing=0.2, row_heights=[0.6, 0.4])

    # Obtener todas las semanas únicas, tanto de forecast como de venta real
    forecast_weeks = set(item_data['Num_Sem'].unique())
    venta_real_weeks = set(item_data[item_data['Venta_Real'].notna()]['Semana'].unique())
    all_weeks = sorted(forecast_weeks.union(venta_real_weeks))

    add_boxplots(fig, item_data, all_weeks, color_map)
    add_venta_real(fig, item_data, all_weeks)
    
    if selected_weeks:
        add_selected_weeks_data(fig, item_data, selected_weeks, color_map, all_weeks)
    else:
        add_no_selection_annotation(fig)

    update_layout(fig, all_weeks, item_data, selected_item, sku_desc, selected_weeks)

    return fig

def add_boxplots(fig, item_data, weeks, color_map):
    for week in weeks:
        week_data = item_data[item_data['Num_Sem'] == week]
        fig.add_trace(go.Box(
            y=week_data['Total'],
            name=f'Semana {week}',
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8,
            marker_color=color_map[week]
        ), row=1, col=1)

def add_venta_real(fig, item_data, weeks):
    venta_real = item_data.groupby('Semana')['Venta_Real'].first().reset_index()
    venta_real = venta_real[venta_real['Venta_Real'].notna()]
    fig.add_trace(go.Scatter(
        x=[f'Semana {week}' for week in venta_real['Semana']],
        y=venta_real['Venta_Real'],
        mode='lines+markers',
        name='Venta Real',
        line=dict(color='red', width=2)
    ), row=1, col=1)

def add_selected_weeks_data(fig, item_data, selected_weeks, color_map, all_weeks):
    selected_weeks = sorted(selected_weeks)
    
    for target_week in selected_weeks:
        forecast_data = item_data[item_data['Semana'] == target_week].sort_values('Num_Sem')
        fig.add_trace(go.Bar(
            x=forecast_data['Num_Sem'],
            y=forecast_data['Total'],
            name=f'Semana Objetivo {target_week}',
            marker_color=color_map[target_week]
        ), row=2, col=1)

    venta_real = item_data.groupby('Semana')['Venta_Real'].first().reset_index()
    venta_real_seleccionadas = venta_real[venta_real['Semana'].isin(selected_weeks)]
    if not venta_real_seleccionadas.empty:
        fig.add_trace(go.Scatter(
            x=venta_real_seleccionadas['Semana'],
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
    title_text = f'Variación del Forecast para {"Todos los Items" if selected_item == "Todos" else f"el Item {selected_item}"}'
    subtitle_text = f'Descripción del producto: {sku_desc}'

    # Ordenar las semanas para el eje x del primer gráfico
    sorted_weeks = sorted(weeks)
    
    fig.update_xaxes(
        title_text="Semana Objetivo",
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
