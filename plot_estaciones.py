import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import rasterio
from rasterio.warp import transform
from rasterio.plot import show
from osgeo import gdal
from my_colormap import newcmp, precipitation_cmap, precipitation_norm


# Define una proyección geográfica para la visualización (latitud y longitud)
geographic_crs = ccrs.PlateCarree()

# Crea una figura y ejes con la proyección geográfica
fig, ax = plt.subplots(subplot_kw={'projection': geographic_crs}, figsize=(10, 10))

#Ahora ploteamos el resto de archivos
contorno_file = r"./ResumenesClimaticos/assets/Contorno_Murcia/Murcia.shp"
tif_file = r".\PrecipitacionesDiarias\output\preciptiation_Grid\clipped_precipitation_grid_P20.tif"#r".\ResumenesClimaticos\results\Precipitacion_Grid\geo_clipped_precipitacion_grid.tif"
shade_file = r".\ResumenesClimaticos\results\My_Hillshade\my_hillshade.tif"
precipitation = rasterio.open(tif_file)
hillshade = rasterio.open(shade_file)
show(hillshade, ax=ax, alpha=0.8, cmap='gray', interpolation='bilinear')
#my_plot = show(precipitation, ax=ax, cmap=newcmp, alpha=0.5, vmin=-100, vmax=3000.0, interpolation='nearest')
contorno_gdf = gpd.read_file(contorno_file)
contorno_gdf = contorno_gdf.to_crs(geographic_crs)
contorno_gdf.plot(facecolor="none", edgecolor='black',ax=ax, linewidth=1)

# Carga el archivo shapefile
shapefile_path = r"./ResumenesClimaticos/assets/Estaciones_Murcia/Estaciones.shp"  # Reemplaza con la ruta de tu archivo .shp
gdf = gpd.read_file(shapefile_path)

#Explorar los nombres de los campos del archivo .shp
nombres_de_campos = gdf.columns
print("Nombres de campos en el shapefile:")
for campo in nombres_de_campos:
    print(campo)


# Convierte las coordenadas UTM a latitud y longitud
gdf = gdf.to_crs(geographic_crs)
# Nombre del campo que se utilizará para etiquetar los puntos
campo_etiqueta = "ESTACIóN"  # Reemplaza con el nombre de tu campo




# Plotea los puntos
gdf.plot(ax=ax, markersize=10, color='blue')

# Etiqueta los puntos con el valor del campo especificado
for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf[campo_etiqueta]):
    ax.text(x, y, label, fontsize=12, ha='center', va='bottom')

# Agrega líneas de cuadrícula geográfica y etiquetas de ejes
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linestyle='--', color='gray', alpha=0.7)
gl.xlabels_top = False  # No mostrar etiquetas en la parte superior
gl.ylabels_right = False  # No mostrar etiquetas en el lado derecho

# Carga el archivo GeoTIFF
import os
# Configura el parámetro GTIFF_SRS_SOURCE en EPSG para utilizar los parámetros oficiales del sistema de referencia de coordenadas (CRS) EPSG:4326
os.environ['GTIFF_SRS_SOURCE'] = 'GEOKEYS'
raster_path = tif_file  # Reemplaza con la ruta de tu archivo GeoTIFF
outputfile = "output.tif"
#Do not change the following line, it will reproject the geotiff file
ds = gdal.Warp(outputfile, shade_file, dstSRS="+proj=longlat +datum=WGS84 +no_defs")
with rasterio.open(outputfile) as src:
    show(src, ax=ax, transform=src.transform, alpha=0.8, cmap='gray', interpolation='bilinear')

#Do not change the following line, it will reproject the geotiff file
ds = gdal.Warp(outputfile, tif_file, srcSRS='+proj=utm +zone=30 +ellps=GRS80 +units=m +no_defs', dstSRS="+proj=longlat +datum=WGS84 +no_defs")
with rasterio.open(outputfile) as src:
    my_plot = show(src, ax=ax, transform=src.transform, cmap=precipitation_cmap, norm=precipitation_norm, alpha=0.8, interpolation='gaussian')
# Añade título al gráfico
ax.set_title("Precipitación Mensual Septiembre 2023 en la Región de Murcia")
# Establece los límites de la región que deseas mostrar
ax.set_extent([-2.35, -0.65, 37.35, 38.8], crs=geographic_crs)

fig.colorbar(my_plot.get_images()[2])
# Muestra el gráfico
plt.show()