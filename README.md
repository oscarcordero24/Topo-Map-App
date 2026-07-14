# Topo Frames — Herramienta de preparación de datos geoespaciales

Herramienta interna de escritorio/local para el equipo de Topo Frames. Sirve
para inspeccionar, recortar y editar datos geoespaciales (rasters de
elevación DEM y shapefiles) **antes** de que pasen al motor de renderizado de
mapas topográficos. No es la tienda ni una herramienta de cara al cliente, y
no genera mapas con estilo ni exporta layouts finales — eso lo hace otra
herramienta.

## Funcionalidad

La app tiene 6 operaciones, cada una en su propia pestaña:

1. **Ver raster** — carga un GeoTIFF (DEM) y muestra CRS, bounding box,
   resolución de pixel, dimensiones, número de bandas, rango de elevación y
   una vista previa visual.
2. **Ver shapefile** — carga un shapefile y muestra CRS, tipo de geometría,
   cantidad de features, tabla de atributos y una vista previa de la
   geometría.
3. **Recortar por shapefile** — recorta un raster usando la forma de un
   shapefile como máscara. Si el shapefile está en otro CRS, se reproyecta
   automáticamente al CRS del raster (y se avisa en la interfaz).
4. **Recortar por coordenadas** — recorta un raster a partir de dos puntos
   (lat/lon) que forman un rectángulo (bounding box).
5. **Crear shapefile** — crea un shapefile de un solo polígono rectangular a
   partir de dos puntos (lat/lon), con un campo de atributo de texto.
6. **Editar shapefile** — carga un shapefile, permite editar su tabla de
   atributos en una tabla interactiva y guardar los cambios (sobrescribiendo
   o como archivo nuevo). También permite aplicar un buffer/margen simple a
   la geometría (en metros o grados).

Todas las operaciones piden explícitamente dónde guardar el archivo de
salida y nunca sobrescriben un archivo existente sin confirmación.

## Stack técnico

- Python puro, sin backend web ni base de datos.
- [rasterio](https://rasterio.readthedocs.io/) — lectura, escritura y
  recorte de rasters.
- [geopandas](https://geopandas.org/) + [shapely](https://shapely.readthedocs.io/) —
  lectura, escritura y geometría de shapefiles.
- [pyproj](https://pyproj4.github.io/pyproj/) — manejo de sistemas de
  coordenadas (CRS), usado internamente por geopandas/rasterio.
- [Streamlit](https://streamlit.io/) — interfaz de usuario local.
- [Matplotlib](https://matplotlib.org/) — vistas previas de raster/vector.

## Instalación

Requiere Python 3.9+ y las librerías de sistema de GDAL instaladas (las
necesitan `rasterio` y `geopandas`/`fiona`).

```bash
git clone <url-del-repo>
cd Topo-Map-App

python -m venv .venv
source .venv/bin/activate      # En Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Cómo correr la app

```bash
streamlit run app.py
```

Esto abre la app en el navegador (`http://localhost:8501`), corriendo en
local. Como es una herramienta interna, se le indican rutas de archivos que
existen en el disco de quien la usa (no hay subida a ningún servidor).

## Estructura del proyecto

```
Topo-Map-App/
├── app.py              # Punto de entrada de Streamlit (arma las 6 pestañas)
├── backend/             # Lógica pura, sin dependencia de Streamlit
│   ├── errors.py         # TopoAppError: errores con mensaje en español
│   ├── models.py         # Dataclasses de resultados (InfoRaster, InfoVector, ...)
│   ├── utils.py           # Validaciones compartidas de rutas de entrada/salida
│   ├── raster_ops.py      # Cargar, recortar por shapefile, recortar por bbox
│   └── vector_ops.py       # Cargar, crear, editar atributos, buffer de geometría
├── ui/                   # Capa de Streamlit, un módulo por pestaña
│   ├── ver_raster.py
│   ├── ver_shapefile.py
│   ├── recorte_por_shapefile.py
│   ├── recorte_por_bbox.py
│   ├── crear_shapefile.py
│   └── editar_shapefile.py
├── requirements.txt
└── README.md
```

Las funciones de `backend/` son puras (reciben rutas/parámetros y devuelven
un resultado o lanzan `TopoAppError`), por lo que se pueden reutilizar desde
otro script sin pasar por la interfaz. Por ejemplo:

```python
from backend.raster_ops import cargar_info_raster, recortar_raster_por_shapefile

info = cargar_info_raster("data/dem_origen.tif")
print(info.crs, info.bounds, info.valor_min, info.valor_max)

resultado = recortar_raster_por_shapefile(
    ruta_raster="data/dem_origen.tif",
    ruta_shapefile="data/area_interes.shp",
    ruta_salida="output/dem_recortado.tif",
    sobrescribir=False,
)
print(resultado.ruta_salida, resultado.advertencia)
```
