import matplotlib.pyplot as plt
import streamlit as st

from backend.errors import TopoAppError
from backend.vector_ops import cargar_info_shapefile, leer_shapefile_para_preview


def render():
    st.header("Ver shapefile")
    st.caption("Carga un shapefile y revisa su CRS, atributos y geometría.")

    ruta = st.text_input("Ruta del archivo shapefile (.shp)", key="ver_shp_ruta")

    if not st.button("Cargar shapefile", key="ver_shp_boton"):
        return

    try:
        info = cargar_info_shapefile(ruta)
    except TopoAppError as e:
        st.error(str(e))
        return
    except Exception:
        st.error("Ocurrió un error inesperado al cargar el shapefile.")
        return

    col_meta, col_preview = st.columns(2)

    with col_meta:
        st.subheader("Metadatos")
        st.write(f"**CRS:** {info.crs}")
        st.write(f"**Tipo de geometría:** {info.tipo_geometria}")
        st.write(f"**Cantidad de features:** {info.num_features}")
        st.write(f"**Bounding box (minx, miny, maxx, maxy):** {info.bounds}")

        st.subheader("Tabla de atributos (primeras filas)")
        st.dataframe(info.atributos.head(20))

    with col_preview:
        st.subheader("Vista previa de la geometría")
        try:
            gdf = leer_shapefile_para_preview(ruta)
        except TopoAppError as e:
            st.error(str(e))
            return

        fig, ax = plt.subplots()
        gdf.plot(ax=ax, edgecolor="black", facecolor="lightblue")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        st.pyplot(fig)
