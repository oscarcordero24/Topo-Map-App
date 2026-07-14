from dataclasses import dataclass
from typing import Optional, Tuple

import pandas as pd


@dataclass
class InfoRaster:
    ruta: str
    crs: str
    bounds: Tuple[float, float, float, float]  # left, bottom, right, top
    ancho: int
    alto: int
    resolucion_x: float
    resolucion_y: float
    num_bandas: int
    valor_min: float
    valor_max: float
    nodata: Optional[float]


@dataclass
class InfoVector:
    ruta: str
    crs: str
    tipo_geometria: str
    num_features: int
    atributos: pd.DataFrame
    bounds: Tuple[float, float, float, float]


@dataclass
class ResultadoOperacion:
    ruta_salida: str
    advertencia: Optional[str] = None
