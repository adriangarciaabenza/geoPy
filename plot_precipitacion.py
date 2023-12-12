shade_file = r".\ResumenesClimaticos\results\My_Hillshade\my_hillshade.tif"
tif_file =  r".\ResumenesClimaticos\results\Precipitacion_Grid\geo_clipped_precipitacion_grid.tif"
import os
import rasterio
from rasterio.plot import show
from osgeo import gdal 
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from my_colormap import newcmp, precipitation_cmap, precipitation_norm


# Define una proyección geográfica para la visualización (latitud y longitud)
geographic_crs = ccrs.PlateCarree()
# Crea una figura y ejes con la proyección geográfica
fig, ax = plt.subplots(subplot_kw={'projection': geographic_crs}, figsize=(10, 10))
# Configura el parámetro GTIFF_SRS_SOURCE en EPSG para utilizar los parámetros oficiales del sistema de referencia de coordenadas (CRS) EPSG:4326
os.environ['GTIFF_SRS_SOURCE'] = 'GEOKEYS'
raster_path = tif_file  # Reemplaza con la ruta de tu archivo GeoTIFF
outputfile = "output.tif"
#Do not change the following line, it will reproject the geotiff file
ds1 = gdal.Warp(outputfile, shade_file, srcSRS='+proj=utm +zone=30 +ellps=GRS80 +units=m +no_defs', dstSRS="+proj=longlat +datum=WGS84 +no_defs")
with rasterio.open(outputfile) as src:
    show(src, ax=ax, transform=src.transform, cmap='gist_gray', alpha=1.0, interpolation='nearest')

ds = gdal.Warp(outputfile, tif_file, srcSRS='+proj=utm +zone=30 +ellps=GRS80 +units=m +no_defs', dstSRS="+proj=longlat +datum=WGS84 +no_defs")
with rasterio.open(outputfile) as src:
    my_plot = show(src, ax=ax, transform=src.transform, cmap=precipitation_cmap, alpha=0.5, norm=precipitation_norm, interpolation='nearest')
fig.colorbar(my_plot.get_images()[1])
ax.set_title("Precipitación Mensual Septiembre 2023 en la Región de Murcia")
plt.show()
