import tkinter as tk
from tkinter import ttk

from backend.errors import TopoAppError
from backend.raster_ops import recortar_raster_por_shapefile
from ui.widgets import mostrar_error, mostrar_resultado, selector_archivo, selector_guardar


class RecorteShapefileFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        ttk.Label(
            self,
            text=(
                "Recorta un raster a la forma de un shapefile. Si el shapefile está en otro CRS, "
                "se reproyecta automáticamente al CRS del raster."
            ),
            font=("", 10, "italic"),
            wraplength=1000,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        frame_raster, self.raster_var = selector_archivo(
            self, "Raster de entrada (GeoTIFF):", [("GeoTIFF", "*.tif *.tiff"), ("Todos", "*.*")]
        )
        frame_raster.pack(fill="x", pady=4)

        frame_shp, self.shp_var = selector_archivo(
            self, "Shapefile de máscara (.shp):", [("Shapefile", "*.shp"), ("Todos", "*.*")]
        )
        frame_shp.pack(fill="x", pady=4)

        frame_salida, self.salida_var = selector_guardar(
            self, "Guardar raster recortado como:", ".tif", [("GeoTIFF", "*.tif")]
        )
        frame_salida.pack(fill="x", pady=4)

        self.sobrescribir_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self, text="Sobrescribir si el archivo de salida ya existe", variable=self.sobrescribir_var
        ).pack(anchor="w", pady=4)

        ttk.Button(self, text="Recortar raster", command=self._recortar).pack(anchor="w", pady=10)

    def _recortar(self):
        try:
            resultado = recortar_raster_por_shapefile(
                self.raster_var.get(), self.shp_var.get(), self.salida_var.get(), self.sobrescribir_var.get()
            )
        except TopoAppError as e:
            mostrar_error(str(e))
            return
        except Exception:
            mostrar_error("Ocurrió un error inesperado al recortar el raster.")
            return

        mostrar_resultado(resultado, f"Raster recortado guardado en:\n{resultado.ruta_salida}")
