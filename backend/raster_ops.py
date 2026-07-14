"""Operaciones puras sobre rasters (DEM en GeoTIFF).

Estas funciones no dependen de Streamlit: reciben rutas/parámetros y
devuelven objetos de resultado o lanzan TopoAppError con un mensaje en
español. Pueden reutilizarse desde cualquier script Python.
"""

from typing import Iterable, Tuple

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.errors import RasterioIOError
from rasterio.mask import mask as rasterio_mask
from shapely.geometry import box

from .errors import TopoAppError
from .models import InfoRaster, ResultadoOperacion
from .utils import validar_archivo_existe, validar_ruta_salida


def cargar_info_raster(ruta: str) -> InfoRaster:
    """Abre un GeoTIFF y devuelve sus metadatos principales."""
    validar_archivo_existe(ruta, "raster")

    try:
        with rasterio.open(ruta) as ds:
            datos = ds.read(1, masked=True)
            hay_datos_validos = datos.count() > 0
            return InfoRaster(
                ruta=ruta,
                crs=str(ds.crs) if ds.crs else "Sin CRS definido",
                bounds=tuple(ds.bounds),
                ancho=ds.width,
                alto=ds.height,
                resolucion_x=abs(ds.transform.a),
                resolucion_y=abs(ds.transform.e),
                num_bandas=ds.count,
                valor_min=float(datos.min()) if hay_datos_validos else float("nan"),
                valor_max=float(datos.max()) if hay_datos_validos else float("nan"),
                nodata=ds.nodata,
            )
    except RasterioIOError as e:
        raise TopoAppError(
            f"No se pudo abrir el raster '{ruta}'. Verifica que sea un archivo GeoTIFF válido."
        ) from e


def leer_raster_para_preview(ruta: str, max_dim: int = 800) -> Tuple[np.ndarray, Tuple[float, float, float, float]]:
    """Lee una versión reducida de la primera banda para mostrarla como imagen."""
    validar_archivo_existe(ruta, "raster")

    try:
        with rasterio.open(ruta) as ds:
            escala = max(1, max(ds.width, ds.height) // max_dim)
            alto_salida = max(1, ds.height // escala)
            ancho_salida = max(1, ds.width // escala)
            datos = ds.read(1, out_shape=(alto_salida, ancho_salida), masked=True)
            return datos, tuple(ds.bounds)
    except RasterioIOError as e:
        raise TopoAppError(
            f"No se pudo leer el raster '{ruta}' para generar la vista previa."
        ) from e


def _recortar_raster_con_geometrias(
    ruta_raster: str,
    geometrias: Iterable,
    crs_geometrias,
    ruta_salida: str,
    sobrescribir: bool,
) -> ResultadoOperacion:
    validar_archivo_existe(ruta_raster, "raster")
    validar_ruta_salida(ruta_salida, sobrescribir)

    advertencia = None

    try:
        with rasterio.open(ruta_raster) as ds:
            crs_raster = ds.crs
            if crs_raster is None:
                raise TopoAppError(
                    "El raster de entrada no tiene un CRS definido; no se puede recortar de forma confiable."
                )

            gdf_recorte = gpd.GeoDataFrame(geometry=list(geometrias), crs=crs_geometrias)
            if gdf_recorte.crs != crs_raster:
                gdf_recorte = gdf_recorte.to_crs(crs_raster)
                advertencia = (
                    f"El área de recorte estaba en {crs_geometrias} y el raster está en {crs_raster}. "
                    "Se reproyectó automáticamente el área de recorte al CRS del raster antes de recortar."
                )

            try:
                datos_recortados, transform_recortado = rasterio_mask(ds, gdf_recorte.geometry, crop=True)
            except ValueError as e:
                raise TopoAppError(
                    "El área de recorte no se superpone con el raster. "
                    "Verifica las coordenadas o el shapefile utilizado."
                ) from e

            perfil = ds.profile.copy()
            perfil.update(
                {
                    "height": datos_recortados.shape[1],
                    "width": datos_recortados.shape[2],
                    "transform": transform_recortado,
                }
            )

            with rasterio.open(ruta_salida, "w", **perfil) as dst:
                dst.write(datos_recortados)

        return ResultadoOperacion(ruta_salida=ruta_salida, advertencia=advertencia)
    except RasterioIOError as e:
        raise TopoAppError(f"No se pudo procesar el raster '{ruta_raster}'.") from e


def recortar_raster_por_shapefile(
    ruta_raster: str,
    ruta_shapefile: str,
    ruta_salida: str,
    sobrescribir: bool = False,
) -> ResultadoOperacion:
    """Recorta un raster usando la forma de un shapefile como máscara."""
    validar_archivo_existe(ruta_shapefile, "shapefile")

    try:
        gdf_mascara = gpd.read_file(ruta_shapefile)
    except Exception as e:
        raise TopoAppError(
            f"No se pudo leer el shapefile '{ruta_shapefile}'. "
            "Verifica que el archivo y sus componentes (.shx, .dbf, .prj) estén presentes."
        ) from e

    if gdf_mascara.empty:
        raise TopoAppError("El shapefile de máscara no contiene ninguna geometría.")

    return _recortar_raster_con_geometrias(
        ruta_raster, gdf_mascara.geometry, gdf_mascara.crs, ruta_salida, sobrescribir
    )


def recortar_raster_por_bbox(
    ruta_raster: str,
    punto1: Tuple[float, float],
    punto2: Tuple[float, float],
    ruta_salida: str,
    sobrescribir: bool = False,
    crs_entrada: str = "EPSG:4326",
) -> ResultadoOperacion:
    """Recorta un raster a partir de un rectángulo definido por dos puntos (lat, lon)."""
    lat1, lon1 = punto1
    lat2, lon2 = punto2

    minx, maxx = sorted([lon1, lon2])
    miny, maxy = sorted([lat1, lat2])

    if minx == maxx or miny == maxy:
        raise TopoAppError(
            "El rectángulo definido por los dos puntos tiene área cero. Verifica las coordenadas ingresadas."
        )

    geometria = box(minx, miny, maxx, maxy)

    return _recortar_raster_con_geometrias(
        ruta_raster, [geometria], crs_entrada, ruta_salida, sobrescribir
    )
