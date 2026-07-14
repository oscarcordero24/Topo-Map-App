import streamlit as st

from backend.errors import TopoAppError
from backend.vector_ops import crear_shapefile_rectangulo


def render():
    st.header("Crear shapefile (rectángulo)")
    st.caption(
        "Crea un shapefile de un solo polígono rectangular a partir de dos puntos (lat/lon) "
        "y un campo de atributo de texto."
    )

    st.markdown("**Punto 1 (una esquina)**")
    c1, c2 = st.columns(2)
    lat1 = c1.number_input("Latitud 1", value=0.0, format="%.6f", key="crear_lat1")
    lon1 = c2.number_input("Longitud 1", value=0.0, format="%.6f", key="crear_lon1")

    st.markdown("**Punto 2 (esquina opuesta)**")
    c3, c4 = st.columns(2)
    lat2 = c3.number_input("Latitud 2", value=0.0, format="%.6f", key="crear_lat2")
    lon2 = c4.number_input("Longitud 2", value=0.0, format="%.6f", key="crear_lon2")

    crs = st.text_input("CRS de las coordenadas ingresadas", value="EPSG:4326", key="crear_crs")

    st.markdown("**Atributo**")
    c5, c6 = st.columns(2)
    nombre_campo = c5.text_input("Nombre del campo", value="nombre", key="crear_campo_nombre")
    valor_campo = c6.text_input("Valor / descripción", key="crear_campo_valor")

    ruta_salida = st.text_input("Ruta de salida para el shapefile (.shp)", key="crear_salida")
    sobrescribir = st.checkbox("Sobrescribir si el archivo de salida ya existe", key="crear_sobrescribir")

    if not st.button("Crear shapefile", key="crear_boton"):
        return

    try:
        resultado = crear_shapefile_rectangulo(
            (lat1, lon1), (lat2, lon2), nombre_campo, valor_campo, ruta_salida, sobrescribir, crs
        )
    except TopoAppError as e:
        st.error(str(e))
        return
    except Exception:
        st.error("Ocurrió un error inesperado al crear el shapefile.")
        return

    st.success(f"Shapefile creado en: {resultado.ruta_salida}")
