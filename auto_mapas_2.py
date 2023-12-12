#Cartopy
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import pandas as pd
import geopandas as gpd
import osgeo.ogr
import osgeo.gdal
from shapely.geometry import Point
import numpy as np
import sys
import rasterio
from rasterio.plot import show
from my_colormap import newcmp
"./ResumenesClimaticos/assets/Estaciones_Murcia/Estaciones.shp"
"./ResumenesClimaticos/assets/Hillshade_Murcia/Hillshade_of_Mdt_Murcia.sgrd"
"./ResumenesClimaticos/assets/Estaciones_Murcia/Estaciones.shp"
fname = "./ResumenesClimaticos/assets/Estaciones_Murcia/Estaciones.shp"
contorno_file = r"./ResumenesClimaticos/assets/Contorno_Murcia/Murcia.shp"
df = gpd.read_file(r"./ResumenesClimaticos/assets/Contorno_Murcia/Murcia.shp")
df3 = gpd.read_file(r"./ResumenesClimaticos/assets/Estaciones_Murcia/Estaciones.shp")
f, ax = plt.subplots()
tif_file = r".\ResumenesClimaticos\results\Precipitacion_Grid\geo_clipped_precipitacion_grid.tif"
shade_file = r".\ResumenesClimaticos\results\My_Hillshade\my_hillshade.tif"
precipitation = rasterio.open(tif_file)
hillshade = rasterio.open(shade_file)
show(hillshade, ax=ax, alpha=0.8, cmap='gray', interpolation='bilinear')
my_plot = show(precipitation, ax=ax, cmap=newcmp, alpha=0.5, vmin=-100, vmax=3000.0, interpolation='nearest')
df.plot(facecolor="none", edgecolor='black',ax=ax, linewidth=1)
df3.plot(ax=ax, color="k")
f.colorbar(my_plot.get_images()[1])
plt.show()
