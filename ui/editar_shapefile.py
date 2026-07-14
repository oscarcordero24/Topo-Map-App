import streamlit as st

from backend.errors import TopoAppError
from backend.vector_ops import (
    aplicar_buffer_geometria,
    cargar_info_shapefile,
    guardar_atributos_editados,
)

SOBRESCRIBIR_ORIGINAL = "Sobrescribir el archivo original"
GUARDAR_NUEVO = "Guardar como archivo nuevo"


def render():
    st.header("Editar shapefile existente")
    st.caption("Carga un shapefile, edita su tabla de atributos y, opcionalmente, aplica un buffer a la geometría.")

    ruta = st.text_input("Ruta del shapefile a editar (.shp)", key="editar_ruta")

    if st.button("Cargar shapefile", key="editar_cargar_boton"):
        try:
            info = cargar_info_shapefile(ruta)
        except TopoAppError as e:
            st.error(str(e))
            return
        except Exception:
            st.error("Ocurrió un error inesperado al cargar el shapefile.")
            return

        st.session_state["editar_ruta_cargada"] = ruta
        st.session_state["editar_tabla"] = info.atributos

    if "editar_tabla" not in st.session_state or st.session_state.get("editar_ruta_cargada") != ruta:
        return

    _render_edicion_atributos(ruta)
    st.divider()
    _render_edicion_geometria(ruta)


def _render_edicion_atributos(ruta: str):
    st.subheader("Tabla de atributos (editable)")
    tabla_editada = st.data_editor(
        st.session_state["editar_tabla"],
        num_rows="fixed",
        key="editar_data_editor",
    )

    modo = st.radio(
        "Destino de los cambios",
        [SOBRESCRIBIR_ORIGINAL, GUARDAR_NUEVO],
        key="editar_modo_attr",
    )

    ruta_salida_nueva = ""
    sobrescribir_nuevo = False
    if modo == GUARDAR_NUEVO:
        ruta_salida_nueva = st.text_input("Ruta del nuevo shapefile (.shp)", key="editar_ruta_nueva")
        sobrescribir_nuevo = st.checkbox(
            "Sobrescribir si el archivo de salida ya existe", key="editar_sobrescribir_nuevo"
        )

    if not st.button("Guardar atributos", key="editar_guardar_boton"):
        return

    ruta_salida = ruta if modo == SOBRESCRIBIR_ORIGINAL else ruta_salida_nueva
    sobrescribir = True if modo == SOBRESCRIBIR_ORIGINAL else sobrescribir_nuevo

    try:
        resultado = guardar_atributos_editados(ruta, tabla_editada, ruta_salida, sobrescribir=sobrescribir)
    except TopoAppError as e:
        st.error(str(e))
        return
    except Exception:
        st.error("Ocurrió un error inesperado al guardar los cambios.")
        return

    st.success(f"Cambios guardados en: {resultado.ruta_salida}")


def _render_edicion_geometria(ruta: str):
    st.subheader("Edición simple de geometría (buffer / margen)")

    c1, c2 = st.columns(2)
    distancia = c1.number_input("Distancia del buffer", value=0.0, key="editar_buffer_distancia")
    unidad = c2.selectbox("Unidad", ["metros", "grados"], key="editar_buffer_unidad")

    modo_geom = st.radio(
        "Destino del resultado",
        [SOBRESCRIBIR_ORIGINAL, GUARDAR_NUEVO],
        key="editar_modo_geom",
    )

    ruta_salida_nueva = ""
    sobrescribir_nuevo = False
    if modo_geom == GUARDAR_NUEVO:
        ruta_salida_nueva = st.text_input("Ruta del nuevo shapefile (.shp)", key="editar_ruta_geom_nueva")
        sobrescribir_nuevo = st.checkbox(
            "Sobrescribir si el archivo de salida ya existe", key="editar_sobrescribir_geom_nuevo"
        )

    if not st.button("Aplicar buffer y guardar", key="editar_buffer_boton"):
        return

    ruta_salida = ruta if modo_geom == SOBRESCRIBIR_ORIGINAL else ruta_salida_nueva
    sobrescribir = True if modo_geom == SOBRESCRIBIR_ORIGINAL else sobrescribir_nuevo

    try:
        resultado = aplicar_buffer_geometria(ruta, distancia, unidad, ruta_salida, sobrescribir=sobrescribir)
    except TopoAppError as e:
        st.error(str(e))
        return
    except Exception:
        st.error("Ocurrió un error inesperado al aplicar el buffer.")
        return

    if resultado.advertencia:
        st.warning(resultado.advertencia)
    st.success(f"Geometría con buffer guardada en: {resultado.ruta_salida}")
