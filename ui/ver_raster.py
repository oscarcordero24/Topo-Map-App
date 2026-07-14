import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from backend.errors import TopoAppError
from backend.raster_ops import cargar_info_raster, leer_raster_para_preview
from ui.widgets import mostrar_error, selector_archivo


class VerRasterFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        ttk.Label(
            self,
            text="Carga un GeoTIFF de elevación (DEM) y revisa sus metadatos y una vista previa.",
            font=("", 10, "italic"),
        ).pack(anchor="w", pady=(0, 8))

        frame_selector, self.ruta_var = selector_archivo(
            self, "Raster (GeoTIFF):", [("GeoTIFF", "*.tif *.tiff"), ("Todos los archivos", "*.*")]
        )
        frame_selector.pack(fill="x", pady=4)

        ttk.Button(self, text="Cargar raster", command=self._cargar).pack(anchor="w", pady=6)

        contenedor = ttk.Frame(self)
        contenedor.pack(fill="both", expand=True)

        self.frame_metadatos = ttk.LabelFrame(contenedor, text="Metadatos", padding=10)
        self.frame_metadatos.pack(side="left", fill="y", padx=(0, 10))

        self.frame_preview = ttk.LabelFrame(contenedor, text="Vista previa", padding=10)
        self.frame_preview.pack(side="left", fill="both", expand=True)

        self.canvas_widget = None

    def _cargar(self):
        ruta = self.ruta_var.get()
        try:
            info = cargar_info_raster(ruta)
        except TopoAppError as e:
            mostrar_error(str(e))
            return
        except Exception:
            mostrar_error("Ocurrió un error inesperado al cargar el raster. Verifica el archivo e inténtalo nuevamente.")
            return

        for widget in self.frame_metadatos.winfo_children():
            widget.destroy()

        filas = [
            ("CRS", info.crs),
            ("Bounding box", str(info.bounds)),
            ("Dimensiones (ancho x alto)", f"{info.ancho} x {info.alto} px"),
            ("Resolución de pixel", f"{info.resolucion_x:.4f} x {info.resolucion_y:.4f}"),
            ("Número de bandas", str(info.num_bandas)),
            ("Rango de elevación", f"{info.valor_min:.2f} a {info.valor_max:.2f}"),
        ]
        if info.nodata is not None:
            filas.append(("Valor NoData", str(info.nodata)))

        for etiqueta, valor in filas:
            fila = ttk.Frame(self.frame_metadatos)
            fila.pack(fill="x", pady=2, anchor="w")
            ttk.Label(fila, text=f"{etiqueta}:", font=("", 9, "bold")).pack(anchor="w")
            ttk.Label(fila, text=valor, wraplength=260, justify="left").pack(anchor="w")

        try:
            datos, bounds = leer_raster_para_preview(ruta)
        except TopoAppError as e:
            mostrar_error(str(e))
            return

        if self.canvas_widget is not None:
            self.canvas_widget.get_tk_widget().destroy()

        figura = Figure(figsize=(5, 5))
        ax = figura.add_subplot(111)
        extent = (bounds[0], bounds[2], bounds[1], bounds[3])
        imagen = ax.imshow(datos, cmap="terrain", extent=extent)
        figura.colorbar(imagen, ax=ax, label="Elevación")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        figura.tight_layout()

        self.canvas_widget = FigureCanvasTkAgg(figura, master=self.frame_preview)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)
