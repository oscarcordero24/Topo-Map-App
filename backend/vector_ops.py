"""Operaciones puras sobre shapefiles (vectores).

Igual que raster_ops.py: funciones sin dependencia de Streamlit, que
reciben rutas/parámetros y devuelven resultados o lanzan TopoAppError.
"""

from typing import Tuple

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from .errors import TopoAppError
from .models import InfoVector, ResultadoOperacion
from .utils import validar_archivo_existe, validar_ruta_salida


def cargar_info_shapefile(ruta: str) -> InfoVector:
    """Abre un shapefile y devuelve sus metadatos y tabla de atributos."""
    validar_archivo_existe(ruta, "shapefile")

    try:
        gdf = gpd.read_file(ruta)
    except Exception as e:
        raise TopoAppError(
            f"No se pudo leer el shapefile '{ruta}'. "
            "Verifica que el archivo y sus componentes (.shx, .dbf, .prj) estén presentes."
        ) from e

    if gdf.empty:
        raise TopoAppError("El shapefile no contiene ninguna geometría.")

    tipos_geometria = ", ".join(sorted(gdf.geom_type.unique()))

    return InfoVector(
        ruta=ruta,
        crs=str(gdf.crs) if gdf.crs else "Sin CRS definido",
        tipo_geometria=tipos_geometria,
        num_features=len(gdf),
        atributos=gdf.drop(columns="geometry").reset_index(drop=True),
        bounds=tuple(float(valor) for valor in gdf.total_bounds),
    )


def leer_shapefile_para_preview(ruta: str) -> gpd.GeoDataFrame:
    """Lee el shapefile completo para dibujar su geometría."""
    validar_archivo_existe(ruta, "shapefile")

    try:
        return gpd.read_file(ruta)
    except Exception as e:
        raise TopoAppError(
            f"No se pudo leer el shapefile '{ruta}' para generar la vista previa."
        ) from e


def crear_shapefile_rectangulo(
    punto1: Tuple[float, float],
    punto2: Tuple[float, float],
    nombre_campo: str,
    valor_campo: str,
    ruta_salida: str,
    sobrescribir: bool = False,
    crs: str = "EPSG:4326",
) -> ResultadoOperacion:
    """Crea un shapefile con un único polígono rectangular a partir de dos puntos (lat, lon)."""
    validar_ruta_salida(ruta_salida, sobrescribir)

    if not nombre_campo:
        raise TopoAppError("Debes indicar un nombre para el campo de atributo.")

    lat1, lon1 = punto1
    lat2, lon2 = punto2

    minx, maxx = sorted([lon1, lon2])
    miny, maxy = sorted([lat1, lat2])

    if minx == maxx or miny == maxy:
        raise TopoAppError(
            "El rectángulo definido por los dos puntos tiene área cero. Verifica las coordenadas ingresadas."
        )

    geometria = box(minx, miny, maxx, maxy)
    gdf = gpd.GeoDataFrame({nombre_campo: [valor_campo]}, geometry=[geometria], crs=crs)

    try:
        gdf.to_file(ruta_salida, driver="ESRI Shapefile")
    except Exception as e:
        raise TopoAppError(f"No se pudo guardar el shapefile en '{ruta_salida}'.") from e

    return ResultadoOperacion(ruta_salida=ruta_salida)


def guardar_atributos_editados(
    ruta_original: str,
    tabla_editada: pd.DataFrame,
    ruta_salida: str,
    sobrescribir: bool = False,
) -> ResultadoOperacion:
    """Guarda un shapefile con la misma geometría del original pero atributos editados."""
    validar_archivo_existe(ruta_original, "shapefile")
    validar_ruta_salida(ruta_salida, sobrescribir)

    try:
        gdf = gpd.read_file(ruta_original)
    except Exception as e:
        raise TopoAppError(f"No se pudo leer el shapefile original '{ruta_original}'.") from e

    if len(tabla_editada) != len(gdf):
        raise TopoAppError(
            "La tabla editada tiene un número de filas distinto al shapefile original. No se puede guardar."
        )

    gdf_nuevo = gdf.copy()
    for columna in tabla_editada.columns:
        gdf_nuevo[columna] = tabla_editada[columna].values

    try:
        gdf_nuevo.to_file(ruta_salida, driver="ESRI Shapefile")
    except Exception as e:
        raise TopoAppError(f"No se pudo guardar el shapefile en '{ruta_salida}'.") from e

    return ResultadoOperacion(ruta_salida=ruta_salida)


def aplicar_buffer_geometria(
    ruta_original: str,
    distancia: float,
    unidad: str,
    ruta_salida: str,
    sobrescribir: bool = False,
) -> ResultadoOperacion:
    """Aplica un buffer (margen) a la geometría de un shapefile y guarda el resultado.

    unidad: "metros" o "grados". Si el CRS original es geográfico y la unidad
    es "metros", se reproyecta temporalmente a un CRS UTM métrico para que el
    buffer sea preciso, y luego se vuelve a proyectar al CRS original.
    """
    validar_archivo_existe(ruta_original, "shapefile")
    validar_ruta_salida(ruta_salida, sobrescribir)

    if unidad not in ("metros", "grados"):
        raise TopoAppError("Unidad de buffer no reconocida. Usa 'metros' o 'grados'.")

    if not distancia:
        raise TopoAppError("La distancia del buffer no puede ser cero.")

    try:
        gdf = gpd.read_file(ruta_original)
    except Exception as e:
        raise TopoAppError(f"No se pudo leer el shapefile original '{ruta_original}'.") from e

    crs_original = gdf.crs
    advertencia = None

    if unidad == "metros" and crs_original is not None and crs_original.is_geographic:
        crs_metrico = gdf.estimate_utm_crs()
        gdf_metrico = gdf.to_crs(crs_metrico)
        gdf_metrico["geometry"] = gdf_metrico.buffer(distancia)
        gdf = gdf_metrico.to_crs(crs_original)
        advertencia = (
            f"El shapefile original está en un CRS geográfico ({crs_original}). "
            f"Se reproyectó temporalmente a {crs_metrico} para aplicar el buffer en metros con precisión, "
            "y luego se devolvió al CRS original."
        )
    else:
        gdf = gdf.copy()
        gdf["geometry"] = gdf.buffer(distancia)

    try:
        gdf.to_file(ruta_salida, driver="ESRI Shapefile")
    except Exception as e:
        raise TopoAppError(f"No se pudo guardar el shapefile en '{ruta_salida}'.") from e

    return ResultadoOperacion(ruta_salida=ruta_salida, advertencia=advertencia)
