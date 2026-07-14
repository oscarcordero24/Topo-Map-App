import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from backend.errors import TopoAppError
from backend.vector_ops import cargar_info_shapefile, leer_shapefile_para_preview
from ui.widgets import mostrar_error, selector_archivo


class VerShapefileFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        ttk.Label(
            self,
            text="Carga un shapefile y revisa su CRS, atributos y geometría.",
            font=("", 10, "italic"),
        ).pack(anchor="w", pady=(0, 8))

        frame_selector, self.ruta_var = selector_archivo(
            self, "Shapefile (.shp):", [("Shapefile", "*.shp"), ("Todos los archivos", "*.*")]
        )
        frame_selector.pack(fill="x", pady=4)

        ttk.Button(self, text="Cargar shapefile", command=self._cargar).pack(anchor="w", pady=6)

        self.frame_meta_texto = ttk.Frame(self)
        self.frame_meta_texto.pack(fill="x", pady=(0, 8))

        contenedor = ttk.Frame(self)
        contenedor.pack(fill="both", expand=True)

        self.frame_tabla = ttk.LabelFrame(contenedor, text="Tabla de atributos (primeras filas)", padding=6)
        self.frame_tabla.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.frame_preview = ttk.LabelFrame(contenedor, text="Vista previa de la geometría", padding=6)
        self.frame_preview.pack(side="left", fill="both", expand=True)

        self.canvas_widget = None

    def _cargar(self):
        ruta = self.ruta_var.get()
        try:
            info = cargar_info_shapefile(ruta)
        except TopoAppError as e:
            mostrar_error(str(e))
            return
        except Exception:
            mostrar_error("Ocurrió un error inesperado al cargar el shapefile.")
            return

        for widget in self.frame_meta_texto.winfo_children():
            widget.destroy()

        texto = (
            f"CRS: {info.crs}    |    Tipo de geometría: {info.tipo_geometria}    |    "
            f"Features: {info.num_features}    |    Bounding box: {info.bounds}"
        )
        ttk.Label(self.frame_meta_texto, text=texto, wraplength=1000, justify="left").pack(anchor="w")

        self._llenar_tabla(info.atributos.head(20))

        try:
            gdf = leer_shapefile_para_preview(ruta)
        except TopoAppError as e:
            mostrar_error(str(e))
            return

        if self.canvas_widget is not None:
            self.canvas_widget.get_tk_widget().destroy()

        figura = Figure(figsize=(5, 5))
        ax = figura.add_subplot(111)
        gdf.plot(ax=ax, edgecolor="black", facecolor="lightblue")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        figura.tight_layout()

        self.canvas_widget = FigureCanvasTkAgg(figura, master=self.frame_preview)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)

    def _llenar_tabla(self, df):
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()

        columnas = list(df.columns)
        tree = ttk.Treeview(self.frame_tabla, columns=columnas, show="headings", height=10)
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=110, anchor="w")
        for _, fila in df.iterrows():
            tree.insert("", "end", values=list(fila))

        scrollbar_y = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=tree.yview)
        scrollbar_x = ttk.Scrollbar(self.frame_tabla, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.frame_tabla.rowconfigure(0, weight=1)
        self.frame_tabla.columnconfigure(0, weight=1)
