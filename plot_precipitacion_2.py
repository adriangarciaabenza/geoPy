#tif_file =  r".\ResumenesClimaticos\results\Precipitacion_Grid\geo_clipped_precipitacion_grid.tif"
tif_file = r".\ResumenesClimaticos\results\My_Hillshade\my_hillshade.tif"
from osgeo import gdal
import matplotlib.pyplot as plt
import rasterio
from pyproj import Transformer
import os

outputfile = "output.tif"
#Do not change the following line, it will reproject the geotiff file
ds = gdal.Warp(outputfile, shade_file, dstSRS="+proj=longlat +datum=WGS84 +no_defs")
with rasterio.open(outputfile) as src:
    rasterio.plot.show(src, ax=ax, transform=src.transform, cmap='viridis')