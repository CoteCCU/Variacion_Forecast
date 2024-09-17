import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def create_forecast_plots(item_data, color_map, selected_weeks):
    sku_desc = item_data['SKU_Descr'].iloc[0]
    selected_sku = item_data['SKU'].iloc[0]

    subplot_titles = ("", "Semanas seleccionadas" if selected_weeks else "")
    fig = make_subplots(rows=2, cols=1, subplot_titles=subplot_titles,
                        vertical_spacing=0.2, row_heights=[0.6, 0.4])

    # Convertir todas las semanas a strings para asegurar consistencia
    forecast_weeks = set(item_data['Sem_Proyectada'].astype(int).unique())
    venta_real_weeks = set(item_data[item_data['Venta_Real'].notna()]['Sem_Origen'].astype(int).unique())
    all_weeks = sorted(forecast_weeks.union(venta_real_weeks), key=lambda x: float(x))

    add_boxplots(fig, item_data, all_weeks, color_map)
    add_venta_real(fig, item_data, all_weeks)
    if selected_weeks:
        add_selected_weeks_data(fig, item_data, selected_weeks, color_map, all_weeks)
   

    update_layout(fig, all_weeks, item_data, selected_sku, sku_desc, selected_weeks)

    return fig

def add_boxplots(fig, item_data, weeks, color_map):
    for week in weeks:
        # Filtrar los datos de la semana actual
        week_data = item_data[item_data['Sem_Proyectada'] == week].sort_values(by='Sem_Origen')
        hover_text = [
            f"Forecast: {forecast}<br>Semana Origen: {sem_origen}"
            for forecast, sem_origen in zip(week_data['Forecast'], week_data['Sem_Origen'])
        ]
        # Convertir la fecha a string para evitar problemas con f-strings
        fecha_str = week_data['Fecha'].iloc[0]
        
        fig.add_trace(go.Scatter(
            x=week_data['Fecha'],
            y=week_data['Forecast'],    # Datos de Forecast en el eje y
            mode='markers',             # Modo de dispersión
            marker=dict(
                color=color_map[int(week)],  # Convert to regular Python int
                size=10
            ),
            text=hover_text,
            hoverinfo='text',
            name=f'Semana {week} <br> {fecha_str}'
        ), row=1, col=1)

        if len(week_data) > 1:
            # Obtener el primer y último valor de Forecast después de ordenar
            first_forecast = week_data['Forecast'].iloc[0]
            last_forecast = week_data['Forecast'].iloc[-1]

            # Determinar color de la línea según la diferencia entre los valores
            if last_forecast < first_forecast:
                line_color = 'yellow'
            else:
                line_color = 'red'

            # Agregar la línea entre los puntos
            fig.add_trace(go.Scatter(
                x=[week_data['Fecha'].iloc[0], week_data['Fecha'].iloc[-1]],  # Mantener la misma semana en el eje x
                y=[first_forecast, last_forecast],  # Primer y último valor de Forecast
                mode='lines',
                line=dict(color=line_color, width=5),
                showlegend=False,
            ), row=1, col=1)

            # Agregar el marcador en forma de flecha en el último punto
            fig.add_trace(go.Scatter(
                x=[week_data['Fecha'].iloc[-1]],
                y=[last_forecast],
                mode='markers',
                marker=dict(
                    color=line_color,
                    size=12,
                    symbol='triangle-up' if last_forecast > first_forecast else 'triangle-down'
                ),
                showlegend=False,
            ), row=1, col=1)

def add_venta_real(fig, item_data, weeks):
    # Agrupar y filtrar los datos de Venta Real
    venta_real = item_data.groupby('Sem_Origen')['Venta_Real'].first().reset_index()
    venta_real = venta_real[venta_real['Venta_Real'].notna()]

    # Filtrar item_data para obtener solo las filas donde Sem_Proyectada coincide con Sem_Origen
    filtered_item_data = item_data[item_data['Sem_Proyectada'].isin(venta_real['Sem_Origen'])]

    # Fusionar con venta_real para obtener las fechas correspondientes
    venta_real = venta_real.merge(filtered_item_data[['Sem_Proyectada', 'Fecha']], 
                                  left_on='Sem_Origen', right_on='Sem_Proyectada', how='left')
    hover_text = [
        f"Venta Real: {venta}<br>Semana: {sem_origen}"
        for venta, sem_origen in zip(venta_real['Venta_Real'], venta_real['Sem_Origen'])
    ]
    # Añadir la traza de Venta Real con hover
    fig.add_trace(go.Scatter(
        x=venta_real['Fecha'], # Semanas en el eje x
        y=venta_real['Venta_Real'],  # Datos de Venta Real en el eje y
        mode='lines+markers',        # Líneas y marcadores
        line=dict(color='green', width=3),  # Configuración de la línea
        marker=dict(size=5),        # Tamaño de los puntos
        text=hover_text,             # Información del hover
        hoverinfo='text',            # Mostrar sólo el texto del hover
        name='Venta Real',
        showlegend=False
    ), row=1, col=1)

def add_selected_weeks_data(fig, item_data, selected_weeks, color_map, all_weeks):
    selected_weeks = sorted(selected_weeks)
    
    for target_week in selected_weeks:
        forecast_data = item_data[item_data['Sem_Origen'] == target_week].sort_values('Sem_Proyectada')
        forecast_data['Fecha'] = pd.to_datetime(forecast_data['Fecha'], format='%Y-%m-%d')
        fig.add_trace(go.Bar(
            x=forecast_data['Fecha'],
            y=forecast_data['Forecast'],
            name=f'Forecast S_{target_week}',
            marker_color=color_map[target_week],
            
        ), row=2, col=1)

    venta_real = item_data.groupby('Sem_Origen')['Venta_Real'].first().reset_index()
    venta_real = venta_real[venta_real['Venta_Real'].notna()]

    # Filtrar item_data para obtener solo las filas donde Sem_Proyectada coincide con Sem_Origen
    filtered_item_data = item_data[item_data['Sem_Proyectada'].isin(venta_real['Sem_Origen'])]

    # Fusionar con venta_real para obtener las fechas correspondientes
    venta_real = venta_real.merge(filtered_item_data[['Sem_Proyectada', 'Fecha']], 
                                  left_on='Sem_Origen', right_on='Sem_Proyectada', how='left')
    if not venta_real.empty:
        fig.add_trace(go.Scatter(
            x=venta_real['Fecha'],
            y=venta_real['Venta_Real'],
            mode='lines+markers',
            name='Venta Real',
            line=dict(color='green', width=3)
        ), row=2, col=1)


def update_layout(fig, weeks, item_data, selected_sku, sku_desc, selected_weeks):
    title_text = f'Variación del Forecast para {"Todos los Productos" if selected_sku == "Todos" else f"el Producto {selected_sku}"}'
    subtitle_text = f'Descripción del producto: {sku_desc}'

    # Asegúrate de que las fechas están en formato datetime
    item_data['Fecha'] = pd.to_datetime(item_data['Fecha'], format='%Y-%m-%d', errors='coerce')

    # Extrae semanas únicas como fechas para usar en ambos gráficos
    all_week_dates = pd.to_datetime(item_data['Fecha'].dt.to_period('W').apply(lambda r: r.start_time).unique())

    # Configuración del eje X para ambos gráficos (mismas fechas)
    fig.update_xaxes(
        title_text="Semana Proyectada",
        tickangle=45,
        tickformat='%Y-%m-%d',
        tickvals=all_week_dates,
        ticktext=[date.strftime('%Y-%m-%d') for date in all_week_dates],
        row=1, col=1
    )

    fig.update_xaxes(
        title_text="Semana Proyectada",
        tickangle=45,
        tickformat='%Y-%m-%d',
        tickvals=all_week_dates,
        ticktext=[date.strftime('%Y-%m-%d') for date in all_week_dates],
        row=2, col=1
    )

    # Configuración del eje Y en ambos gráficos
    fig.update_yaxes(title_text="Forecast", row=1, col=1)
    fig.update_yaxes(title_text="Forecast", row=2, col=1)

    # Configuración general del layout
    fig.update_layout(
        title={
            'text': f'{title_text}<br>{subtitle_text}<br>Todas las Semanas',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        height=1000,
        margin=dict(l=50, r=50, t=100, b=100),
        xaxis_title_standoff=25,
        xaxis2_title_standoff=25,
        legend=dict(
            orientation="v",
            y=1,
            xanchor="center",
            x=1.1,
            traceorder="normal",
            font=dict(size=10),
            itemsizing="constant",
            itemwidth=40,
            itemclick="toggle",
        )
    )