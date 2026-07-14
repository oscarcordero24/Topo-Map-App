import matplotlib.pyplot as plt
import streamlit as st

from backend.errors import TopoAppError
from backend.raster_ops import cargar_info_raster, leer_raster_para_preview


def render():
    st.header("Ver raster (DEM)")
    st.caption("Carga un GeoTIFF de elevación y revisa sus metadatos y una vista previa.")

    ruta = st.text_input("Ruta del archivo raster (GeoTIFF)", key="ver_raster_ruta")

    if not st.button("Cargar raster", key="ver_raster_boton"):
        return

    try:
        info = cargar_info_raster(ruta)
    except TopoAppError as e:
        st.error(str(e))
        return
    except Exception:
        st.error("Ocurrió un error inesperado al cargar el raster. Verifica el archivo e inténtalo nuevamente.")
        return

    col_meta, col_preview = st.columns(2)

    with col_meta:
        st.subheader("Metadatos")
        st.write(f"**CRS:** {info.crs}")
        st.write(f"**Bounding box (izq, abajo, der, arriba):** {info.bounds}")
        st.write(f"**Dimensiones (ancho x alto):** {info.ancho} x {info.alto} px")
        st.write(
            f"**Resolución de pixel:** {info.resolucion_x:.4f} x {info.resolucion_y:.4f} (unidades del CRS)"
        )
        st.write(f"**Número de bandas:** {info.num_bandas}")
        st.write(f"**Rango de elevación (banda 1):** {info.valor_min:.2f} a {info.valor_max:.2f}")
        if info.nodata is not None:
            st.write(f"**Valor NoData:** {info.nodata}")

    with col_preview:
        st.subheader("Vista previa")
        try:
            datos, bounds = leer_raster_para_preview(ruta)
        except TopoAppError as e:
            st.error(str(e))
            return

        fig, ax = plt.subplots()
        extent = (bounds[0], bounds[2], bounds[1], bounds[3])
        imagen = ax.imshow(datos, cmap="terrain", extent=extent)
        fig.colorbar(imagen, ax=ax, label="Elevación")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        st.pyplot(fig)
