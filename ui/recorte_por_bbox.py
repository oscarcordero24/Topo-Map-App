import tkinter as tk
from tkinter import ttk

from backend.errors import TopoAppError
from backend.raster_ops import recortar_raster_por_bbox
from ui.widgets import fila_coordenadas, mostrar_error, mostrar_resultado, selector_archivo, selector_guardar


class RecorteBboxFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        ttk.Label(
            self,
            text=(
                "Ingresa dos puntos (lat/lon) que formen las esquinas opuestas de un rectángulo "
                "para recortar el raster a esa área."
            ),
            font=("", 10, "italic"),
            wraplength=1000,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        frame_raster, self.raster_var = selector_archivo(
            self, "Raster de entrada (GeoTIFF):", [("GeoTIFF", "*.tif *.tiff"), ("Todos", "*.*")]
        )
        frame_raster.pack(fill="x", pady=4)

        self.lat1_var, self.lon1_var = fila_coordenadas(self, "Punto 1 (una esquina)")
        self.lat2_var, self.lon2_var = fila_coordenadas(self, "Punto 2 (esquina opuesta)")

        frame_salida, self.salida_var = selector_guardar(
            self, "Guardar raster recortado como:", ".tif", [("GeoTIFF", "*.tif")]
        )
        frame_salida.pack(fill="x", pady=(10, 4))

        self.sobrescribir_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self, text="Sobrescribir si el archivo de salida ya existe", variable=self.sobrescribir_var
        ).pack(anchor="w", pady=4)

        ttk.Button(self, text="Recortar raster", command=self._recortar).pack(anchor="w", pady=10)

    def _recortar(self):
        try:
            lat1 = float(self.lat1_var.get())
            lon1 = float(self.lon1_var.get())
            lat2 = float(self.lat2_var.get())
            lon2 = float(self.lon2_var.get())
        except ValueError:
            mostrar_error("Las coordenadas deben ser números válidos.")
            return

        try:
            resultado = recortar_raster_por_bbox(
                self.raster_var.get(), (lat1, lon1), (lat2, lon2), self.salida_var.get(), self.sobrescribir_var.get()
            )
        except TopoAppError as e:
            mostrar_error(str(e))
            return
        except Exception:
            mostrar_error("Ocurrió un error inesperado al recortar el raster.")
            return

        mostrar_resultado(resultado, f"Raster recortado guardado en:\n{resultado.ruta_salida}")
