"""Widgets y helpers reutilizables para las pestañas de Tkinter."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def selector_archivo(parent, etiqueta, filetypes):
    """Fila con Label + Entry + botón 'Examinar...' para elegir un archivo existente.

    Devuelve (frame, StringVar). El frame no está empaquetado: quien llama
    decide con pack()/grid() dónde ubicarlo.
    """
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=etiqueta, width=28, anchor="w").pack(side="left")
    var = tk.StringVar()
    ttk.Entry(frame, textvariable=var, width=55).pack(side="left", padx=4, fill="x", expand=True)

    def elegir():
        ruta = filedialog.askopenfilename(filetypes=filetypes)
        if ruta:
            var.set(ruta)

    ttk.Button(frame, text="Examinar...", command=elegir).pack(side="left")
    return frame, var


def selector_guardar(parent, etiqueta, extension_defecto, filetypes):
    """Fila con Label + Entry + botón 'Guardar como...' para elegir dónde guardar un archivo nuevo."""
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=etiqueta, width=28, anchor="w").pack(side="left")
    var = tk.StringVar()
    ttk.Entry(frame, textvariable=var, width=55).pack(side="left", padx=4, fill="x", expand=True)

    def elegir():
        ruta = filedialog.asksaveasfilename(defaultextension=extension_defecto, filetypes=filetypes)
        if ruta:
            var.set(ruta)

    ttk.Button(frame, text="Guardar como...", command=elegir).pack(side="left")
    return frame, var


def fila_coordenadas(parent, titulo):
    """Bloque de título + fila con entradas de Latitud/Longitud. Devuelve (lat_var, lon_var)."""
    ttk.Label(parent, text=titulo, font=("", 9, "bold")).pack(anchor="w", pady=(6, 0))
    fila = ttk.Frame(parent)
    fila.pack(fill="x", pady=2)

    ttk.Label(fila, text="Latitud:").pack(side="left")
    lat_var = tk.StringVar()
    ttk.Entry(fila, textvariable=lat_var, width=15).pack(side="left", padx=(4, 16))

    ttk.Label(fila, text="Longitud:").pack(side="left")
    lon_var = tk.StringVar()
    ttk.Entry(fila, textvariable=lon_var, width=15).pack(side="left", padx=4)

    return lat_var, lon_var


def mostrar_error(mensaje: str):
    messagebox.showerror("Error", mensaje)


def mostrar_resultado(resultado, mensaje_exito: str):
    if resultado.advertencia:
        messagebox.showwarning("Aviso", resultado.advertencia)
    messagebox.showinfo("Listo", mensaje_exito)
