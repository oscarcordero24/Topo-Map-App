import tkinter as tk
from tkinter import ttk

from ui import (
    crear_shapefile,
    editar_shapefile,
    recorte_por_bbox,
    recorte_por_shapefile,
    ver_raster,
    ver_shapefile,
)


def main():
    root = tk.Tk()
    root.title("Topo Frames — Preparación de datos geoespaciales")
    root.geometry("1150x780")

    ttk.Label(
        root,
        text=(
            "Herramienta interna para inspeccionar, recortar y editar rasters (DEM) y shapefiles "
            "antes de pasarlos al motor de renderizado de mapas."
        ),
        wraplength=1100,
        justify="left",
        padding=(10, 10),
    ).pack(fill="x")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    pestanas = [
        ("1. Ver raster", ver_raster.VerRasterFrame),
        ("2. Ver shapefile", ver_shapefile.VerShapefileFrame),
        ("3. Recortar por shapefile", recorte_por_shapefile.RecorteShapefileFrame),
        ("4. Recortar por coordenadas", recorte_por_bbox.RecorteBboxFrame),
        ("5. Crear shapefile", crear_shapefile.CrearShapefileFrame),
        ("6. Editar shapefile", editar_shapefile.EditarShapefileFrame),
    ]

    for titulo, clase_frame in pestanas:
        pestana = clase_frame(notebook)
        notebook.add(pestana, text=titulo)

    root.mainloop()


if __name__ == "__main__":
    main()
