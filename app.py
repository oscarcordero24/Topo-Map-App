import streamlit as st

from ui import (
    crear_shapefile,
    editar_shapefile,
    recorte_por_bbox,
    recorte_por_shapefile,
    ver_raster,
    ver_shapefile,
)

st.set_page_config(page_title="Topo Frames — Preparación de datos", layout="wide")

st.title("Topo Frames — Herramienta de preparación de datos geoespaciales")
st.caption(
    "Herramienta interna para inspeccionar, recortar y editar rasters (DEM) y shapefiles "
    "antes de pasarlos al motor de renderizado de mapas."
)

tabs = st.tabs(
    [
        "1. Ver raster",
        "2. Ver shapefile",
        "3. Recortar por shapefile",
        "4. Recortar por coordenadas",
        "5. Crear shapefile",
        "6. Editar shapefile",
    ]
)

with tabs[0]:
    ver_raster.render()
with tabs[1]:
    ver_shapefile.render()
with tabs[2]:
    recorte_por_shapefile.render()
with tabs[3]:
    recorte_por_bbox.render()
with tabs[4]:
    crear_shapefile.render()
with tabs[5]:
    editar_shapefile.render()
