import streamlit as st

from backend.errors import TopoAppError
from backend.raster_ops import recortar_raster_por_shapefile


def render():
    st.header("Recortar raster usando un shapefile")
    st.caption(
        "Recorta un raster a la forma de un shapefile. Si el shapefile está en otro CRS, "
        "se reproyecta automáticamente al CRS del raster."
    )

    ruta_raster = st.text_input("Ruta del raster de entrada (GeoTIFF)", key="rs_raster")
    ruta_shp = st.text_input("Ruta del shapefile de máscara (.shp)", key="rs_shp")
    ruta_salida = st.text_input("Ruta de salida para el raster recortado (.tif)", key="rs_salida")
    sobrescribir = st.checkbox("Sobrescribir si el archivo de salida ya existe", key="rs_sobrescribir")

    if not st.button("Recortar raster", key="rs_boton"):
        return

    try:
        resultado = recortar_raster_por_shapefile(ruta_raster, ruta_shp, ruta_salida, sobrescribir)
    except TopoAppError as e:
        st.error(str(e))
        return
    except Exception:
        st.error("Ocurrió un error inesperado al recortar el raster.")
        return

    if resultado.advertencia:
        st.warning(resultado.advertencia)
    st.success(f"Raster recortado guardado en: {resultado.ruta_salida}")
