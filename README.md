# Variacion_Forecast

Este proyecto realiza una visualizacion de la variación de los datos utilizando técnicas de análisis de series temporales.


## Estructura del proyecto

- `app.py`: Script principal que orquesta el flujo de trabajo del proyecto.
- `data.py`: Maneja la carga y preprocesamiento de datos.
- `logic.py`: Contiene la lógica.
- `plot.py`: Genera visualizaciones de los resultados del pronóstico.

## Cómo ejecutar

Para ejecutar este proyecto, sigue estos pasos:

1. Asegúrate de tener Python instalado en tu sistema.

2. Instala las dependencias necesarias:
   ```
   pip install pandas numpy dash plotly
   ```

3. Ejecuta el script principal:
   ```
   python app.py
   ```

4. El script cargará los datos, realizará el pronóstico y generará visualizaciones.

# Datos .csv
Recordar poner los datos en .gitignore antes de subir a github
Explicacion de los datos:
Sem_Proyectada: Semana proyectada
Grupo: Grupo de cervezas o analcoholicas
SKU: SKU de producto
Sem_Origen: Semana de origen en la que se hace el pronostico para la semana proyectada
Forecast: Pronostico de ventas
Referencia_Sem: Referencia de la semana (cuantas semanas hacia adelante o atras se pronostica la venta)
Fecha: Fecha de la semana de origen
SKU_Descr: Descripcion del producto
Pinta: Submarca del producto
Sistema: Envase del producto
Formato: Envase físico + unidad de medida
Categoria: Categoria del producto
UXC: Unidades de producto por caja
Venta_Real: Venta real del producto en la semana proyectada



## Notas

- Asegúrate de tener los datos de entrada necesarios en el formato correcto antes de ejecutar el script.



