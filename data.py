import pandas as pd
import colorsys
import plotly.express as px

def generate_distinct_colors(n):
    HSV_tuples = [(x*1.0/n, 0.5, 0.5) for x in range(n)]
    RGB_tuples = [colorsys.hsv_to_rgb(*x) for x in HSV_tuples]
    return ['rgb({},{},{})'.format(int(r*255), int(g*255), int(b*255)) for r, g, b in RGB_tuples]

def load_and_process_data(file_path):
    df = pd.read_csv(file_path, encoding='utf-8-sig', decimal=',', sep=';')
    df = df[df['Referencia_Sem'].isin(['N-01'] + ['N0'] + [f'N{str(i).zfill(2)}' for i in range(-1, 13)])]
    return df

def generate_color_map(df):
    base_colors = (
        px.colors.qualitative.Plotly +
        px.colors.qualitative.Set1 +
        px.colors.qualitative.Set2 +
        px.colors.qualitative.Set3 +
        px.colors.qualitative.Dark24 +
        px.colors.qualitative.Light24
    )
    additional_colors = generate_distinct_colors(80 - len(base_colors))
    color_scale = (base_colors + additional_colors)[:80]
    unique_weeks = sorted(df['Sem_Origen'].unique())
    return dict(zip(unique_weeks, [color_scale[i % len(color_scale)] for i in range(len(unique_weeks))]))

def get_item_data(df, selected_item):
    if selected_item == 'Todos':
        # Agrupar los datos por semana y referencia, calcular la suma total de 'Total' por semana
        grouped_data = df.groupby(['Sem_Origen', 'Sem_Proyectada'])['Forecast'].sum().reset_index()
        grouped_data['SKU'] = 'Todos'
        grouped_data['SKU_Descr'] = 'Todos los items'
        
        # Agrupar por semana y seleccionar el primer valor único de Venta_Real por producto
        venta_real_unica = df.groupby(['Sem_Proyectada', 'SKU'])['Venta_Real'].first().reset_index()
        
        # Agrupar las ventas reales por semana sumando para todos los productos
        venta_real_total = venta_real_unica.groupby('Sem_Proyectada')['Venta_Real'].sum().reset_index()
        
        # Hacer un merge de los datos agrupados con las ventas reales totales por semana
        grouped_data = grouped_data.merge(venta_real_total, on='Sem_Proyectada', how='left')
        
        return grouped_data
    else:
        # Devolver los datos filtrados por item seleccionado
        return df[df['SKU'] == selected_item]

def get_venta_real(item_data):
    venta_real = item_data.groupby('Sem_Proyectada')['Venta_Real'].first().reset_index()
    return venta_real[venta_real['Venta_Real'].notna()]

def get_forecast_data(item_data, target_week):
    return item_data[item_data['Sem_Proyectada'] == target_week].sort_values('Sem_Origen')