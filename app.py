import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
from data import load_and_process_data, get_item_data, generate_color_map
from plot import create_forecast_plots

# Cargar y procesar los datos
df = load_and_process_data('forecast_y_venta_real.csv')
color_map = generate_color_map(df)

app = dash.Dash(__name__, assets_folder='assets')

app.layout = html.Div([
    html.Div([
        html.H1("Variación del Forecast en el Tiempo")
    ], className='app-header'),
    
    html.Div([
        html.Div([
            html.Label('Grupo:', className='filter-label'),
            dcc.Dropdown(
                id='demand-grupo-filter',
                options=[{'label': 'Todos', 'value': 'Todos'}] + [{'label': i, 'value': i} for i in sorted(df['Demand Grupo'].unique())],
                multi=True
            )
        ], className='filter-item'),
        html.Div([
            html.Label('Sistema:', className='filter-label'),
            dcc.Dropdown(
                id='sistema-filter',
                options=[{'label': 'Todos', 'value': 'Todos'}] + [{'label': i, 'value': i} for i in sorted(df['SISTEMA'].unique().astype(str))],
                multi=True
            )
        ], className='filter-item'),
        html.Div([
            html.Label('Formato:', className='filter-label'),
            dcc.Dropdown(
                id='formato-filter',
                options=[{'label': 'Todos', 'value': 'Todos'}] + [{'label': i, 'value': i} for i in sorted(df['FORMATO'].unique().astype(str))],
                multi=True
            )
        ], className='filter-item'),
        html.Div([
            html.Label('Categoría:', className='filter-label'),
            dcc.Dropdown(
                id='categoria-filter',
                options=[{'label': 'Todos', 'value': 'Todos'}] + [{'label': i, 'value': i} for i in sorted(df['CATEGORIA'].unique().astype(str))],
                multi=True
            )
        ], className='filter-item'),
        html.Div([
            html.Label('Pinta:', className='filter-label'),
            dcc.Dropdown(
                id='pinta-filter',
                options=[{'label': 'Todos', 'value': 'Todos'}] + [{'label': i, 'value': i} for i in sorted(df['PINTA'].unique().astype(str))],
                multi=True
            )
        ], className='filter-item'),
        html.Div([
            html.Label('Item:', className='filter-label'),
            dcc.Dropdown(
                id='item-filter',
                options=[{'label': 'Todos', 'value': 'Todos'}] + [{'label': f"{item} - {df[df['ITEM'] == item]['SKU_DESCR'].iloc[0]}", 'value': item} for item in df['ITEM'].unique()],
                multi=True
            )
        ], className='filter-item'),
    ], className='filter-container'),
    
    html.Div([
        dcc.Graph(id='forecast-plots')
    ], className='graph-container'),
    
    html.Div([
        html.Label('Seleccionar Semana(s) Objetivo:', className='filter-label'),
        dcc.Dropdown(
            id='week-dropdown',
            options=[{'label': f'Semana {week}', 'value': week} for week in sorted(df['Num_Sem'].unique())],
            value=[],
            multi=True
        )
    ], className='filter-container')
])


@app.callback(
    [Output('sistema-filter', 'options'),
     Output('formato-filter', 'options'),
     Output('categoria-filter', 'options'),
     Output('pinta-filter', 'options'),
     Output('item-filter', 'options')],
    [Input('demand-grupo-filter', 'value'),
     Input('sistema-filter', 'value'),
     Input('formato-filter', 'value'),
     Input('categoria-filter', 'value'),
     Input('pinta-filter', 'value')]
)
def update_filter_options(demand_grupo, sistema, formato, categoria, pinta):
    filtered_df = df.copy()
    if demand_grupo and 'Todos' not in demand_grupo:
        filtered_df = filtered_df[filtered_df['Demand Grupo'].isin(demand_grupo)]
    if sistema and 'Todos' not in sistema:
        filtered_df = filtered_df[filtered_df['SISTEMA'].isin(sistema)]
    if formato and 'Todos' not in formato:
        filtered_df = filtered_df[filtered_df['FORMATO'].isin(formato)]
    if categoria and 'Todos' not in categoria:
        filtered_df = filtered_df[filtered_df['CATEGORIA'].isin(categoria)]
    if pinta and 'Todos' not in pinta:
        filtered_df = filtered_df[filtered_df['PINTA'].isin(pinta)]
    
    sistema_options = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': i, 'value': i} for i in sorted(filtered_df['SISTEMA'].unique().astype(str))]
    formato_options = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': i, 'value': i} for i in sorted(filtered_df['FORMATO'].unique().astype(str))]
    categoria_options = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': i, 'value': i} for i in sorted(filtered_df['CATEGORIA'].unique().astype(str))]
    pinta_options = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': i, 'value': i} for i in sorted(filtered_df['PINTA'].unique().astype(str))]
    
    item_options = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': f"{item} - {df[df['ITEM'] == item]['SKU_DESCR'].iloc[0]}", 'value': item} for item in filtered_df['ITEM'].unique()]
    
    return sistema_options, formato_options, categoria_options, pinta_options, item_options


@app.callback(
    Output('forecast-plots', 'figure'),
    [Input('demand-grupo-filter', 'value'),
     Input('sistema-filter', 'value'),
     Input('formato-filter', 'value'),
     Input('categoria-filter', 'value'),
     Input('pinta-filter', 'value'),
     Input('item-filter', 'value'),
     Input('week-dropdown', 'value')]
)
def update_graphs(demand_grupo, sistema, formato, categoria, pinta, item, selected_weeks):
    filtered_df = df.copy()
    if demand_grupo and 'Todos' not in demand_grupo:
        filtered_df = filtered_df[filtered_df['Demand Grupo'].isin(demand_grupo)]
    if sistema and 'Todos' not in sistema:
        filtered_df = filtered_df[filtered_df['SISTEMA'].isin(sistema)]
    if formato and 'Todos' not in formato:
        filtered_df = filtered_df[filtered_df['FORMATO'].isin(formato)]
    if categoria and 'Todos' not in categoria:
        filtered_df = filtered_df[filtered_df['CATEGORIA'].isin(categoria)]
    if pinta and 'Todos' not in pinta:
        filtered_df = filtered_df[filtered_df['PINTA'].isin(pinta)]
    if item and 'Todos' not in item:
        filtered_df = filtered_df[filtered_df['ITEM'].isin(item)]
    
    item_data = get_item_data(filtered_df, 'Todos' if not item or 'Todos' in item else item[0])
    
    return create_forecast_plots(item_data, color_map, selected_weeks)



if __name__ == '__main__':
    app.run_server(debug=True)