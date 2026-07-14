class TopoAppError(Exception):
    """Error de aplicación con un mensaje en español listo para mostrar en la UI.

    Las funciones del backend capturan las excepciones técnicas de rasterio,
    fiona/geopandas, pyproj, etc. y las relanzan como TopoAppError con un
    mensaje claro, para que la capa de Streamlit nunca muestre un stacktrace
    crudo al usuario.
    """
