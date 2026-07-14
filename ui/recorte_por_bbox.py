import streamlit as st

from backend.errors import TopoAppError
from backend.raster_ops import recortar_raster_por_bbox


def render():
    st.header("Recortar raster por coordenadas (bounding box)")
    st.caption(
        "Ingresa dos puntos (lat/lon) que formen las esquinas opuestas de un rectángulo "
        "para recortar el raster a esa área."
    )

    ruta_raster = st.text_input("Ruta del raster de entrada (GeoTIFF)", key="bbox_raster")

    st.markdown("**Punto 1 (una esquina)**")
    c1, c2 = st.columns(2)
    lat1 = c1.number_input("Latitud 1", value=0.0, format="%.6f", key="bbox_lat1")
    lon1 = c2.number_input("Longitud 1", value=0.0, format="%.6f", key="bbox_lon1")

    st.markdown("**Punto 2 (esquina opuesta)**")
    c3, c4 = st.columns(2)
    lat2 = c3.number_input("Latitud 2", value=0.0, format="%.6f", key="bbox_lat2")
    lon2 = c4.number_input("Longitud 2", value=0.0, format="%.6f", key="bbox_lon2")

    ruta_salida = st.text_input("Ruta de salida para el raster recortado (.tif)", key="bbox_salida")
    sobrescribir = st.checkbox("Sobrescribir si el archivo de salida ya existe", key="bbox_sobrescribir")

    if not st.button("Recortar raster", key="bbox_boton"):
        return

    try:
        resultado = recortar_raster_por_bbox(
            ruta_raster, (lat1, lon1), (lat2, lon2), ruta_salida, sobrescribir
        )
    except TopoAppError as e:
        st.error(str(e))
        return
    except Exception:
        st.error("Ocurrió un error inesperado al recortar el raster.")
        return

    if resultado.advertencia:
        st.warning(resultado.advertencia)
    st.success(f"Raster recortado guardado en: {resultado.ruta_salida}")
