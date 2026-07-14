import tkinter as tk
from tkinter import ttk

import pandas as pd

from backend.errors import TopoAppError
from backend.vector_ops import aplicar_buffer_geometria, cargar_info_shapefile, guardar_atributos_editados
from ui.widgets import mostrar_error, mostrar_resultado, selector_archivo, selector_guardar

SOBRESCRIBIR_ORIGINAL = "Sobrescribir el archivo original"
GUARDAR_NUEVO = "Guardar como archivo nuevo"


class EditarShapefileFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        ttk.Label(
            self,
            text="Carga un shapefile, edita su tabla de atributos y, opcionalmente, aplica un buffer a la geometría.",
            font=("", 10, "italic"),
            wraplength=1000,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        frame_selector, self.ruta_var = selector_archivo(
            self, "Shapefile a editar (.shp):", [("Shapefile", "*.shp"), ("Todos", "*.*")]
        )
        frame_selector.pack(fill="x", pady=4)

        ttk.Button(self, text="Cargar shapefile", command=self._cargar).pack(anchor="w", pady=6)

        self.notebook_edicion = ttk.Notebook(self)
        self.notebook_edicion.pack(fill="both", expand=True, pady=(10, 0))

        self.tab_atributos = ttk.Frame(self.notebook_edicion, padding=10)
        self.tab_geometria = ttk.Frame(self.notebook_edicion, padding=10)
        self.notebook_edicion.add(self.tab_atributos, text="Editar atributos")
        self.notebook_edicion.add(self.tab_geometria, text="Editar geometría (buffer)")

        self.ruta_cargada = None
        self.df_original = None
        self.columnas = []
        self.celda_vars = []

        self._construir_tab_geometria()

    # ---------------------------------------------------------------- carga

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

        self.ruta_cargada = ruta
        self.df_original = info.atributos
        self._construir_tabla_editable(info.atributos)

    # ------------------------------------------------------- tabla editable

    def _construir_tabla_editable(self, df: pd.DataFrame):
        for widget in self.tab_atributos.winfo_children():
            widget.destroy()

        self.columnas = list(df.columns)
        self.celda_vars = []

        contenedor_tabla = ttk.Frame(self.tab_atributos)
        contenedor_tabla.pack(fill="both", expand=True)

        canvas = tk.Canvas(contenedor_tabla, borderwidth=0, height=260)
        frame_interior = ttk.Frame(canvas)
        scrollbar_y = ttk.Scrollbar(contenedor_tabla, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(contenedor_tabla, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        contenedor_tabla.rowconfigure(0, weight=1)
        contenedor_tabla.columnconfigure(0, weight=1)

        canvas.create_window((0, 0), window=frame_interior, anchor="nw")

        def _actualizar_scrollregion(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame_interior.bind("<Configure>", _actualizar_scrollregion)

        ttk.Label(frame_interior, text="#", width=5, anchor="w", font=("", 9, "bold")).grid(
            row=0, column=0, padx=2, pady=2
        )
        for j, columna in enumerate(self.columnas):
            ttk.Label(frame_interior, text=columna, width=18, anchor="w", font=("", 9, "bold")).grid(
                row=0, column=j + 1, padx=2, pady=2
            )

        for i, (_, fila) in enumerate(df.iterrows()):
            ttk.Label(frame_interior, text=str(i), width=5, anchor="w").grid(row=i + 1, column=0, padx=2, pady=1)
            fila_vars = []
            for j, columna in enumerate(self.columnas):
                var = tk.StringVar(value=str(fila[columna]))
                ttk.Entry(frame_interior, textvariable=var, width=18).grid(
                    row=i + 1, column=j + 1, padx=2, pady=1
                )
                fila_vars.append(var)
            self.celda_vars.append(fila_vars)

        frame_guardar = ttk.Frame(self.tab_atributos)
        frame_guardar.pack(fill="x", pady=(10, 0))

        self.modo_attr_var = tk.StringVar(value=SOBRESCRIBIR_ORIGINAL)
        ttk.Radiobutton(
            frame_guardar,
            text=SOBRESCRIBIR_ORIGINAL,
            variable=self.modo_attr_var,
            value=SOBRESCRIBIR_ORIGINAL,
            command=self._actualizar_visibilidad_attr,
        ).pack(anchor="w")
        ttk.Radiobutton(
            frame_guardar,
            text=GUARDAR_NUEVO,
            variable=self.modo_attr_var,
            value=GUARDAR_NUEVO,
            command=self._actualizar_visibilidad_attr,
        ).pack(anchor="w")

        self.frame_salida_attr, self.salida_attr_var = selector_guardar(
            frame_guardar, "Nuevo shapefile:", ".shp", [("Shapefile", "*.shp")]
        )

        self.sobrescribir_attr_nuevo_var = tk.BooleanVar(value=False)
        self.check_sobrescribir_attr = ttk.Checkbutton(
            frame_guardar,
            text="Sobrescribir si el archivo de salida ya existe",
            variable=self.sobrescribir_attr_nuevo_var,
        )

        ttk.Button(frame_guardar, text="Guardar atributos", command=self._guardar_atributos).pack(
            anchor="w", pady=8
        )

        self._actualizar_visibilidad_attr()

    def _actualizar_visibilidad_attr(self):
        if self.modo_attr_var.get() == GUARDAR_NUEVO:
            self.frame_salida_attr.pack(fill="x", pady=4)
            self.check_sobrescribir_attr.pack(anchor="w", pady=2)
        else:
            self.frame_salida_attr.pack_forget()
            self.check_sobrescribir_attr.pack_forget()

    def _construir_dataframe_editado(self) -> pd.DataFrame:
        filas = [[var.get() for var in fila_vars] for fila_vars in self.celda_vars]
        df = pd.DataFrame(filas, columns=self.columnas)

        for columna in self.columnas:
            dtype_original = self.df_original[columna].dtype
            if pd.api.types.is_numeric_dtype(dtype_original):
                try:
                    df[columna] = pd.to_numeric(df[columna])
                except ValueError as e:
                    raise TopoAppError(f"La columna '{columna}' debe contener solo valores numéricos.") from e

        return df

    def _guardar_atributos(self):
        if self.ruta_cargada is None:
            mostrar_error("Primero debes cargar un shapefile.")
            return

        try:
            tabla_editada = self._construir_dataframe_editado()
        except TopoAppError as e:
            mostrar_error(str(e))
            return

        modo = self.modo_attr_var.get()
        if modo == SOBRESCRIBIR_ORIGINAL:
            ruta_salida = self.ruta_cargada
            sobrescribir = True
        else:
            ruta_salida = self.salida_attr_var.get()
            sobrescribir = self.sobrescribir_attr_nuevo_var.get()

        try:
            resultado = guardar_atributos_editados(
                self.ruta_cargada, tabla_editada, ruta_salida, sobrescribir=sobrescribir
            )
        except TopoAppError as e:
            mostrar_error(str(e))
            return
        except Exception:
            mostrar_error("Ocurrió un error inesperado al guardar los cambios.")
            return

        mostrar_resultado(resultado, f"Cambios guardados en:\n{resultado.ruta_salida}")

    # -------------------------------------------------------------- buffer

    def _construir_tab_geometria(self):
        ttk.Label(
            self.tab_geometria,
            text="Aplica un buffer/margen a la geometría del shapefile cargado arriba.",
            font=("", 9, "italic"),
        ).pack(anchor="w", pady=(0, 8))

        fila = ttk.Frame(self.tab_geometria)
        fila.pack(fill="x", pady=4)
        ttk.Label(fila, text="Distancia del buffer:").pack(side="left")
        self.distancia_var = tk.StringVar(value="0")
        ttk.Entry(fila, textvariable=self.distancia_var, width=15).pack(side="left", padx=(4, 16))

        ttk.Label(fila, text="Unidad:").pack(side="left")
        self.unidad_var = tk.StringVar(value="metros")
        ttk.Combobox(
            fila, textvariable=self.unidad_var, values=["metros", "grados"], state="readonly", width=10
        ).pack(side="left", padx=4)

        self.modo_geom_var = tk.StringVar(value=SOBRESCRIBIR_ORIGINAL)
        ttk.Radiobutton(
            self.tab_geometria,
            text=SOBRESCRIBIR_ORIGINAL,
            variable=self.modo_geom_var,
            value=SOBRESCRIBIR_ORIGINAL,
            command=self._actualizar_visibilidad_geom,
        ).pack(anchor="w", pady=(8, 0))
        ttk.Radiobutton(
            self.tab_geometria,
            text=GUARDAR_NUEVO,
            variable=self.modo_geom_var,
            value=GUARDAR_NUEVO,
            command=self._actualizar_visibilidad_geom,
        ).pack(anchor="w")

        self.frame_salida_geom, self.salida_geom_var = selector_guardar(
            self.tab_geometria, "Nuevo shapefile:", ".shp", [("Shapefile", "*.shp")]
        )

        self.sobrescribir_geom_nuevo_var = tk.BooleanVar(value=False)
        self.check_sobrescribir_geom = ttk.Checkbutton(
            self.tab_geometria,
            text="Sobrescribir si el archivo de salida ya existe",
            variable=self.sobrescribir_geom_nuevo_var,
        )

        ttk.Button(self.tab_geometria, text="Aplicar buffer y guardar", command=self._aplicar_buffer).pack(
            anchor="w", pady=10
        )

        self._actualizar_visibilidad_geom()

    def _actualizar_visibilidad_geom(self):
        if self.modo_geom_var.get() == GUARDAR_NUEVO:
            self.frame_salida_geom.pack(fill="x", pady=4)
            self.check_sobrescribir_geom.pack(anchor="w", pady=2)
        else:
            self.frame_salida_geom.pack_forget()
            self.check_sobrescribir_geom.pack_forget()

    def _aplicar_buffer(self):
        if self.ruta_cargada is None:
            mostrar_error("Primero debes cargar un shapefile.")
            return

        try:
            distancia = float(self.distancia_var.get())
        except ValueError:
            mostrar_error("La distancia del buffer debe ser un número válido.")
            return

        modo = self.modo_geom_var.get()
        if modo == SOBRESCRIBIR_ORIGINAL:
            ruta_salida = self.ruta_cargada
            sobrescribir = True
        else:
            ruta_salida = self.salida_geom_var.get()
            sobrescribir = self.sobrescribir_geom_nuevo_var.get()

        try:
            resultado = aplicar_buffer_geometria(
                self.ruta_cargada, distancia, self.unidad_var.get(), ruta_salida, sobrescribir=sobrescribir
            )
        except TopoAppError as e:
            mostrar_error(str(e))
            return
        except Exception:
            mostrar_error("Ocurrió un error inesperado al aplicar el buffer.")
            return

        mostrar_resultado(resultado, f"Geometría con buffer guardada en:\n{resultado.ruta_salida}")
