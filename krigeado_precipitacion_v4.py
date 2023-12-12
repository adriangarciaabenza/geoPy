import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import rasterio
import cartopy.crs as ccrs
from pykrige.ok import OrdinaryKriging
import geopandas as gpd
from shapely.geometry import Point
from rasterio.plot import show
from rasterio.features import geometry_mask
from matplotlib.colors import LightSource
from my_colormap import newcmp, daily_precipitation_cmap, precipitation_cmap, precipitation_norm, daily_precipitation_norm, monthly_levels, daily_levels, daily_ticks, monthly_ticks

# Cargar datos de estaciones y precipitación
# Supongamos que tienes datos de precipitación, latitud, longitud y altitud
import os;
input = './PrecipitacionesDiarias/input/'
output = './PrecipitacionesDiarias/output/'
if not os.path.exists(input):
    os.mkdir(input)
if not os.path.exists(output):
    os.mkdir(output)

#Comprobación generando la tabla directamente con las estaciones
df_estaciones = pd.read_csv(input+"Pcp072023.csv", sep=";")
print(df_estaciones)
#for i in range(6, len(df_estaciones.keys())): 
    #df_estaciones[df_estaciones[df_estaciones.keys()[i]] < 0.0] = 0
    #df_estaciones[df_estaciones[df_estaciones.keys()[i]] == ""] = 0


# Selecciona las columnas a partir de la sexta
columns_to_update = df_estaciones.columns[6:]

# Itera sobre las columnas seleccionadas
for column in columns_to_update:
    # Convierte la columna a tipo numérico
    df_estaciones[column] = pd.to_numeric(df_estaciones[column], errors='coerce')
    
    # Establece a cero los valores negativos
    df_estaciones[column] = df_estaciones[column].apply(lambda x: max(0.0, x))
print(df_estaciones)

# Cargar el shapefile de la región de Murcia
region_path = r".\PrecipitacionesDiarias\input\Contorno_Murcia\Murcia.shp" #'./ruta/al/archivo/Murcia.shp'
region = gpd.read_file(region_path)

# Crear GeoDataFrame con las estaciones
geometry = [Point(xy) for xy in zip(df_estaciones["C_X"], df_estaciones["C_Y"])]
gdf_estaciones = gpd.GeoDataFrame(df_estaciones, geometry=geometry, crs=region.crs)

# Realizar la intersección para obtener las estaciones dentro de la región
estaciones_en_murcia = gpd.sjoin(gdf_estaciones, region, op='within')

# Obtener las coordenadas de las estaciones dentro de la región
lats_murcia = np.asarray(estaciones_en_murcia["C_Y"])
lons_murcia = np.asarray(estaciones_en_murcia["C_X"])

outpath="./Krigeado_Precipitacion/"
if not os.path.exists(outpath):
    os.mkdir(outpath)

#Dict con variables estadísticas de la región.
results = {"Variable":[], "Media":[], "DevStd":[], "Min":[], "Max":[], "Media Acumulada":[]}
media_acumulada = 0.0
n_days = 0
for field in df_estaciones.keys()[6:]:
    print("Calculando: ", field)
    values_murcia = np.asarray(estaciones_en_murcia[field])

    # Definir la cuadrícula sobre la que realizarás el kriging
    grid_lon, grid_lat = np.meshgrid(np.linspace(550000.0, 710000.0, 100), 
                                    np.linspace(4130000.0,  4300000.0, 100))

    if np.any(values_murcia != 0.0):
        # Definir el modelo de variograma
        variogram_model = 'linear'
        variogram_model_parameters = {"slope": 1, "nugget": 0.0}

        # Aplicar el logaritmo natural a los valores de precipitación
        values_log = np.log1p(values_murcia)

        # Configurar el modelo de kriging ordinario
        ok_model = OrdinaryKriging(lons_murcia, lats_murcia, values_murcia, variogram_model=variogram_model, variogram_parameters=variogram_model_parameters)

        # Realizar el kriging en la cuadrícula
        #grid_z, grid_var = ok_model.execute('grid', grid_lon.flatten(), grid_lat.flatten())
        #print("Grid_lon shape:", grid_lon.shape)
        #print(grid_lon[:][0])
        #print("Grid_lat shape:", grid_lat.shape)
        #print(grid_lat[:,0])
        grid_z, grid_var= ok_model.execute('grid', grid_lon[:][0], grid_lat[:,0])

        # Aplicar la transformación inversa (exponencial) para obtener los valores originales
        #grid_z = np.expm1(grid_z_log)

        # Asegurarse de que los valores predichos no sean negativos
        grid_z = np.clip(grid_z, a_min=0, a_max=None)

        # Reshape para obtener una cuadrícula 2D
        grid_z = grid_z.reshape(grid_lon.shape)
        #print(grid_z)
        #print(values_murcia)
    else:
        # Si todos los valores son 0.0, asignar 0.0 a la cuadrícula
        grid_z = np.zeros_like(grid_lon)

    # Enmascarar las áreas fuera de la región de Murcia
    murcia_geometry = region.unary_union
    murcia_geometry = murcia_geometry.buffer(500)
    # Crear una serie de GeoPandas Points para cada punto en la cuadrícula
    grid_points = gpd.GeoSeries([Point(x, y) for x, y in zip(grid_lon.flatten(), grid_lat.flatten())])

    # Aplicar la función contains a cada punto
    contains_mask = grid_points.apply(lambda point: murcia_geometry.contains(point))

    # Usar la máscara para filtrar los valores de la cuadrícula
    masked_grid_z = np.where(contains_mask, grid_z.flatten(), np.nan)
    masked_grid_z = masked_grid_z.reshape(grid_z.shape)

    if n_days == 0:
        cum_grid_z = masked_grid_z
    else:
        cum_grid_z = cum_grid_z +masked_grid_z
    n_days = n_days + 1

    # Calcular estadísticas del grid
    mean_value = np.nanmean(masked_grid_z/10.0)
    std_dev = np.nanstd(masked_grid_z/10.0)
    min_value = np.nanmin(masked_grid_z/10.0)
    max_value = np.nanmax(masked_grid_z/10.0)
    media_acumulada = media_acumulada + mean_value

    # Mostrar estadísticas
    print(f'Media: {mean_value:.2f}')
    print(f'Desviación Estándar: {std_dev:.2f}')
    print(f'Mínimo: {min_value:.2f}')
    print(f'Máximo: {max_value:.2f}')

    #Guardamos resultados en dict results
    results["Variable"].append(field)
    results["Media"].append(mean_value)
    results["DevStd"].append(std_dev)
    results["Min"].append(min_value)
    results["Max"].append(max_value)
    results["Media Acumulada"].append(media_acumulada)
    print("Precipitacion Media Acumulada = ", media_acumulada, "mm")
    # Visualizar los resultados dentro de la región de Murcia
    plt.figure(figsize=(8, 8))

    hillshade_path = r".\ResumenesClimaticos\results\My_Hillshade\my_hillshade.tif"  # Reemplaza con la ruta correcta
    with rasterio.open(hillshade_path) as src:
        # Crear una máscara basada en la geometría de la región de Murcia
        mask = geometry_mask([murcia_geometry], out_shape=src.shape, transform=src.transform, invert=False)

        # Aplicar la máscara al hillshade
        hillshade = src.read(1, masked=True)
        hillshade = np.ma.masked_array(hillshade, mask)

        # Crear una máscara basada en la geometría de la región de Murcia
        mask2 = geometry_mask([murcia_geometry], out_shape=src.shape, transform=src.transform, invert=True)

        # Aplicar la máscara al hillshade
        hillshade2 = src.read(1, masked=True)
        hillshade2 = np.ma.masked_array(hillshade2, mask2)
        
        # Obtener la extensión
        hillshade_extent = rasterio.plot.plotting_extent(src)

    #-------------------------------------------------------------
    # Plot PRECIPITACION DIARIA
    #print(hillshade_extent)
    plt.imshow(hillshade, cmap='gray', alpha=1.0, extent=hillshade_extent, origin='upper')
    plt.imshow(hillshade2, cmap='gray', alpha=1.0, extent=hillshade_extent, origin='upper')
    #plt.show()
    #plt.figure(figsize=(8, 8))
    plt.contourf(grid_lon, grid_lat, masked_grid_z, cmap=daily_precipitation_cmap, norm=daily_precipitation_norm, extent=hillshade_extent, alpha=0.7)
    plt.scatter(lons_murcia, lats_murcia, c=values_murcia, cmap=daily_precipitation_cmap, norm=daily_precipitation_norm, edgecolor='k', s=100, alpha=0.7, label='Datos Observados')
    #plt.colorbar(label='Precipitación')
    cbar = plt.colorbar(ticks = daily_levels)
    cbar.ax.set_yticklabels(daily_ticks)
    if len(field) == 2:
        plt.title('Kriging de Precipitación en la Región de Murcia '+"Día 0"+field[-1])
    else:
        plt.title('Kriging de Precipitación en la Región de Murcia '+"Día "+field[-2:]) 
    
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    region.boundary.plot(color='black', linewidth=2.5, ax=plt.gca(), label='Contorno de Murcia')

    # Carga el archivo shapefile
    shapefile_path = r"./ResumenesClimaticos/assets/Estaciones_Murcia/Estaciones.shp"  # Reemplaza con la ruta de tu archivo .shp
    gdf = gpd.read_file(shapefile_path)

    #Explorar los nombres de los campos del archivo .shp
    nombres_de_campos = gdf.columns
    #print("Nombres de campos en el shapefile:")
    #for campo in nombres_de_campos:
        #print(campo)
    # Convierte las coordenadas UTM a latitud y longitud
    #gdf = gdf.to_crs(geographic_crs)
    # Nombre del campo que se utilizará para etiquetar los puntos
    campo_etiqueta = "ESTACIóN"  # Reemplaza con el nombre de tu campo

    # Plotea los puntos
    #plt.scatter(gdf["X"], gdf["Y"], color='blue')
    # Etiqueta los puntos con el valor del campo especificado
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf[campo_etiqueta]):
        plt.text(x, y, label, fontsize=12, ha='center', va='bottom', weight='bold')

    plt.legend(loc='upper left')
    if len(field) == 2:
        plt.savefig("./Krigeado_Precipitacion/Dia0"+field[-1]+".png")
    else:
        plt.savefig("./Krigeado_Precipitacion/Dia"+field[-2:]+".png")
    plt.close()
    
    #--------------------------------------------------
    # Repetimos plot para PRECIPITACION ACUMULADA
    plt.figure(figsize=(8, 8))
    #print(hillshade_extent)
    plt.imshow(hillshade, cmap='gray', alpha=1.0, extent=hillshade_extent, origin='upper')
    plt.imshow(hillshade2, cmap='gray', alpha=1.0, extent=hillshade_extent, origin='upper')
    #plt.show()
    #plt.figure(figsize=(8, 8))
    plt.contourf(grid_lon, grid_lat, cum_grid_z, cmap=precipitation_cmap, norm=precipitation_norm, extent=hillshade_extent, alpha=0.7)
    plt.scatter(lons_murcia, lats_murcia, c=values_murcia, cmap=precipitation_cmap, norm=precipitation_norm, edgecolor='k', s=0, alpha=0.7)
    #plt.colorbar(label='Precipitación')
    cbar2 = plt.colorbar(ticks = monthly_levels)
    cbar2.ax.set_yticklabels(monthly_ticks)
    if len(field) == 2:
        plt.title('Kriging de Precipitación Acumulada en la Región de Murcia '+"Día 0"+field[-1])
    else:
        plt.title('Kriging de Precipitación Acumulada en la Región de Murcia '+"Día "+field[-2:]) 
    
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    region.boundary.plot(color='black', linewidth=2.5, ax=plt.gca(), label='Contorno de Murcia')

    # Carga el archivo shapefile
    shapefile_path = r"./ResumenesClimaticos/assets/Estaciones_Murcia/Estaciones.shp"  # Reemplaza con la ruta de tu archivo .shp
    gdf = gpd.read_file(shapefile_path)

    #Explorar los nombres de los campos del archivo .shp
    nombres_de_campos = gdf.columns
    #print("Nombres de campos en el shapefile:")
    #for campo in nombres_de_campos:
        #print(campo)
    # Convierte las coordenadas UTM a latitud y longitud
    #gdf = gdf.to_crs(geographic_crs)
    # Nombre del campo que se utilizará para etiquetar los puntos
    campo_etiqueta = "ESTACIóN"  # Reemplaza con el nombre de tu campo

    # Plotea los puntos
    plt.scatter(gdf["X"], gdf["Y"], color='black', label="Principales Poblaciones")
    # Etiqueta los puntos con el valor del campo especificado
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf[campo_etiqueta]):
        plt.text(x, y, label, fontsize=12, ha='center', va='bottom', weight='bold')

    plt.legend(loc='upper left')
    if len(field) == 2:
        plt.savefig("./Krigeado_Precipitacion/AcumuladaDia0"+field[-1]+".png")
    else:
        plt.savefig("./Krigeado_Precipitacion/AcumuladaDia"+field[-2:]+".png")
    plt.close()


df = pd.DataFrame(results)
print(df.head())
df.to_csv(outpath+"ResultadosDiarios_KrigingPreciptiacion.csv", sep=';')
print("Precipitación media mensual:", df['Media'].sum(), "mm")