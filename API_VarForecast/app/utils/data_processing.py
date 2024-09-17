import pandas as pd
from typing import List, Optional
import plotly.express as px

def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, encoding='utf-8-sig', decimal=',', sep=';')
    df = df[df['Referencia_Sem'].isin(['N-01'] + ['N0'] + [f'N{str(i).zfill(2)}' for i in range(-1, 13)])]
    return df

def get_item_data(df, selected_item):
    if selected_item == 'Todos':
        # Agrupar los datos por semana y referencia, calcular la suma total de 'Total' por semana
        grouped_data = df.groupby(['Sem_Origen', 'Sem_Proyectada', 'Fecha'])['Forecast'].sum().reset_index()
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
    
def filter_data(
    df: pd.DataFrame,
    grupo: Optional[List[str]] = None,
    sistema: Optional[List[str]] = None,
    formato: Optional[List[str]] = None,
    categoria: Optional[List[str]] = None,
    pinta: Optional[List[str]] = None,
    item: Optional[List[str]] = None,
    selected_weeks: Optional[List[str]] = None
) -> pd.DataFrame:
    # Aplicar los filtros a los datos
    if grupo:
        df = df[df['Grupo'].isin(grupo)]
    if sistema:
        df = df[df['Sistema'].isin(sistema)]
    if formato:
        df = df[df['Formato'].isin(formato)]
    if categoria:
        df = df[df['Categoria'].isin(categoria)]
    if pinta:
        df = df[df['Pinta'].isin(pinta)]
    if item:
        df = df[df['SKU'].isin(item)]
    if selected_weeks:
        df = df[df['Sem_Proyectada'].isin(selected_weeks)]
    
    return df

def generate_color_map(df):
    unique_weeks = sorted(df['Sem_Proyectada'].unique())
    colors = px.colors.qualitative.Plotly * (len(unique_weeks) // len(px.colors.qualitative.Plotly) + 1)
    return {week: color for week, color in zip(unique_weeks, colors)}
