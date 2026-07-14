import os

from .errors import TopoAppError


def validar_archivo_existe(ruta: str, tipo_archivo: str = "archivo") -> None:
    """Verifica que una ruta de entrada haya sido indicada y exista en disco."""
    if not ruta:
        raise TopoAppError(f"Debes indicar la ruta del {tipo_archivo}.")
    if not os.path.isfile(ruta):
        raise TopoAppError(f"No se encontró el {tipo_archivo} en la ruta: {ruta}")


def validar_ruta_salida(ruta_salida: str, sobrescribir: bool) -> None:
    """Verifica que la ruta de salida sea válida y evita sobrescrituras silenciosas."""
    if not ruta_salida:
        raise TopoAppError("Debes indicar dónde guardar el archivo de salida.")

    directorio = os.path.dirname(ruta_salida) or "."
    if not os.path.isdir(directorio):
        raise TopoAppError(f"La carpeta de destino no existe: {directorio}")

    if os.path.exists(ruta_salida) and not sobrescribir:
        raise TopoAppError(
            f"Ya existe un archivo en '{ruta_salida}'. "
            "Marca la opción de sobrescribir si deseas reemplazarlo, o elige otro nombre."
        )
