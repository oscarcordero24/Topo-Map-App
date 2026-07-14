# Topo Map App

A Python application for opening, processing, and creating rasters and shapefiles, and for building print-ready layouts to export topographic maps.

## Features

- **Open & inspect** raster (GeoTIFF, etc.) and shapefile/vector data
- **Process** geospatial data — reprojection, clipping, resampling, contour generation, and other raster/vector operations
- **Create & edit** rasters and shapefiles
- **Layout & export** — compose map layouts (title, legend, scale bar, grid) and export finished topo maps as images or PDFs

## Tech Stack

- Python 3.x
- [GDAL](https://gdal.org/) / [rasterio](https://rasterio.readthedocs.io/) — raster I/O and processing
- [Fiona](https://fiona.readthedocs.io/) / [geopandas](https://geopandas.org/) — shapefile and vector I/O
- [Shapely](https://shapely.readthedocs.io/) — geometric operations
- [Matplotlib](https://matplotlib.org/) (or similar) — map layout rendering and export

## Getting Started

### Prerequisites

- Python 3.9+
- [GDAL](https://gdal.org/download.html) system libraries installed (required by `rasterio`/`fiona`)

### Installation

```bash
git clone https://github.com/oscarcordero24/topo-map-app.git
cd topo-map-app

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Usage

```bash
python main.py --help
```

_Update the command above once the entry point is implemented._

## Project Structure

```
topo-map-app/
├── data/           # Input rasters, shapefiles (gitignored)
├── output/         # Generated exports (gitignored)
├── src/            # Application source code
└── README.md
```

## Contributing

Contributions are welcome. Please open an issue or pull request to discuss changes.

## License

TBD
