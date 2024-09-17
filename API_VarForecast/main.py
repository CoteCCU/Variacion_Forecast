from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from pydantic import BaseModel
from app.plot import create_forecast_plots
from app.utils.data_processing import load_data, generate_color_map, get_item_data, filter_data
import plotly.io as pio
import json
import numpy as np

app = FastAPI()
csv_data = None
color_map = None
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class DropdownOptions(BaseModel):
    grupo: List[dict]
    sistema: List[dict]
    formato: List[dict]
    categoria: List[dict]
    pinta: List[dict]
    item: List[dict]

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

@app.on_event("startup")
async def startup_event():
    global csv_data
    global color_map
    csv_data = load_data('data/Forecast_Proyectado.csv')
    color_map = generate_color_map(csv_data)
    print("CSV cargado exitosamente")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    global csv_data
    global color_map
    selected_weeks = []
    item_data = get_item_data(csv_data, 'Todos')
    fig = create_forecast_plots(item_data, color_map, selected_weeks)
    plot_json = pio.to_json(fig)
    return templates.TemplateResponse("index.html", {"request": request, "plot_json": plot_json})

@app.get("/filter-options", response_model=DropdownOptions)
def get_filter_options(
    grupo: Optional[str] = None,
    sistema: Optional[str] = None,
    formato: Optional[str] = None,
    categoria: Optional[str] = None,
    pinta: Optional[str] = None,
    item: Optional[str] = None
):
    global csv_data
    filtered_df = csv_data.copy()

    # Aplicar filtros dinámicos
    if grupo:
        filtered_df = filtered_df[filtered_df['Grupo'] == grupo]
    if sistema:
        filtered_df = filtered_df[filtered_df['Sistema'] == sistema]
    if formato:
        filtered_df = filtered_df[filtered_df['Formato'] == formato]
    if categoria:
        filtered_df = filtered_df[filtered_df['Categoria'] == categoria]
    if pinta:
        filtered_df = filtered_df[filtered_df['Pinta'] == pinta]
    if item:
        filtered_df = filtered_df[filtered_df['SKU'] == item]

    # Generar las opciones para cada dropdown
    options = {
        "grupo": [{'label': 'Todos', 'value': 'Todos'}] + [{'label': str(i), 'value': str(i)} for i in sorted(csv_data['Grupo'].unique())],
        "sistema": [{'label': 'Todos', 'value': 'Todos'}] + [{'label': str(i), 'value': str(i)} for i in sorted(filtered_df['Sistema'].astype(str).unique())],
        "formato": [{'label': 'Todos', 'value': 'Todos'}] + [{'label': str(i), 'value': str(i)} for i in sorted(filtered_df['Formato'].astype(str).unique())],
        "categoria": [{'label': 'Todos', 'value': 'Todos'}] + [{'label': str(i), 'value': str(i)} for i in sorted(filtered_df['Categoria'].astype(str).unique())],
        "pinta": [{'label': 'Todos', 'value': 'Todos'}] + [{'label': str(i), 'value': str(i)} for i in sorted(filtered_df['Pinta'].astype(str).unique())],
        "item": [{'label': 'Todos', 'value': 'Todos'}] + [{'label': f"{item} - {filtered_df[filtered_df['SKU'] == item]['SKU_Descr'].iloc[0]}", 'value': str(item)} for item in sorted(filtered_df['SKU'].unique())]
    }

    # Usar json.dumps con el encoder personalizado
    json_compatible_item_data = json.dumps(options, cls=NumpyEncoder)
    return JSONResponse(content=json.loads(json_compatible_item_data))

@app.get("/filtered-data")
def get_filtered_data(
    grupo: Optional[str] = None,
    sistema: Optional[str] = None,
    formato: Optional[str] = None,
    categoria: Optional[str] = None,
    pinta: Optional[str] = None,
    item: Optional[str] = None,
    selected_weeks: Optional[List[str]] = Query(None)
):
    global csv_data
    global color_map
    filtered_df = csv_data.copy()

    # Aplicar filtros dinámicos
    if grupo and grupo != 'Todos':
        filtered_df = filtered_df[filtered_df['Grupo'] == grupo]
    if sistema and sistema != 'Todos':
        filtered_df = filtered_df[filtered_df['Sistema'] == sistema]
    if formato and formato != 'Todos':
        filtered_df = filtered_df[filtered_df['Formato'] == formato]
    if categoria and categoria != 'Todos':
        filtered_df = filtered_df[filtered_df['Categoria'] == categoria]
    if pinta and pinta != 'Todos':
        filtered_df = filtered_df[filtered_df['Pinta'] == pinta]
    if item and item != 'Todos':
        filtered_df = filtered_df[filtered_df['SKU'] == item]
    if selected_weeks:
        filtered_df = filtered_df[filtered_df['Sem_Proyectada'].isin(selected_weeks)]
    item_data = get_item_data(filtered_df, 'Todos')
    fig = create_forecast_plots(item_data, color_map, selected_weeks)
    plot_json = pio.to_json(fig)
    return JSONResponse(content=json.loads(plot_json))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
