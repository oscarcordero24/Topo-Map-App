import tkinter as tk
from tkinter import ttk

from backend.errors import TopoAppError
from backend.vector_ops import crear_shapefile_rectangulo
from ui.widgets import fila_coordenadas, mostrar_error, mostrar_resultado, selector_guardar


class CrearShapefileFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        ttk.Label(
            self,
            text=(
                "Crea un shapefile de un solo polígono rectangular a partir de dos puntos (lat/lon) "
                "y un campo de atributo de texto."
            ),
            font=("", 10, "italic"),
            wraplength=1000,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        self.lat1_var, self.lon1_var = fila_coordenadas(self, "Punto 1 (una esquina)")
        self.lat2_var, self.lon2_var = fila_coordenadas(self, "Punto 2 (esquina opuesta)")

        fila_crs = ttk.Frame(self)
        fila_crs.pack(fill="x", pady=(10, 4))
        ttk.Label(fila_crs, text="CRS de las coordenadas ingresadas:", width=28, anchor="w").pack(side="left")
        self.crs_var = tk.StringVar(value="EPSG:4326")
        ttk.Entry(fila_crs, textvariable=self.crs_var, width=20).pack(side="left", padx=4)

        fila_campo = ttk.Frame(self)
        fila_campo.pack(fill="x", pady=4)
        ttk.Label(fila_campo, text="Nombre del campo:").pack(side="left")
        self.nombre_campo_var = tk.StringVar(value="nombre")
        ttk.Entry(fila_campo, textvariable=self.nombre_campo_var, width=20).pack(side="left", padx=(4, 16))
        ttk.Label(fila_campo, text="Valor / descripción:").pack(side="left")
        self.valor_campo_var = tk.StringVar()
        ttk.Entry(fila_campo, textvariable=self.valor_campo_var, width=30).pack(side="left", padx=4)

        frame_salida, self.salida_var = selector_guardar(
            self, "Guardar shapefile como:", ".shp", [("Shapefile", "*.shp")]
        )
        frame_salida.pack(fill="x", pady=4)

        self.sobrescribir_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self, text="Sobrescribir si el archivo de salida ya existe", variable=self.sobrescribir_var
        ).pack(anchor="w", pady=4)

        ttk.Button(self, text="Crear shapefile", command=self._crear).pack(anchor="w", pady=10)

    def _crear(self):
        try:
            lat1 = float(self.lat1_var.get())
            lon1 = float(self.lon1_var.get())
            lat2 = float(self.lat2_var.get())
            lon2 = float(self.lon2_var.get())
        except ValueError:
            mostrar_error("Las coordenadas deben ser números válidos.")
            return

        try:
            resultado = crear_shapefile_rectangulo(
                (lat1, lon1),
                (lat2, lon2),
                self.nombre_campo_var.get(),
                self.valor_campo_var.get(),
                self.salida_var.get(),
                self.sobrescribir_var.get(),
                self.crs_var.get(),
            )
        except TopoAppError as e:
            mostrar_error(str(e))
            return
        except Exception:
            mostrar_error("Ocurrió un error inesperado al crear el shapefile.")
            return

        mostrar_resultado(resultado, f"Shapefile creado en:\n{resultado.ruta_salida}")
