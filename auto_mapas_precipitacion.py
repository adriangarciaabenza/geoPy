#from plot_gdal import *
import osgeo.gdal
import osgeo.ogr
from my_pysaga import *
import pandas as pd
import numpy as np
import shutil

#from plot_precipitaciones_diarias import plot_daily_precipitation

print('Running AutoMapas Precipitacion Diaria \n This script uses SAGA and its tools through Python.')

Verbose = False
if not Verbose:
    saga_api.SG_UI_ProgressAndMsg_Lock(True)

import os;
input = './PrecipitacionesDiarias/input/'
output = './PrecipitacionesDiarias/output/'
if not os.path.exists(input):
    os.mkdir(input)
if not os.path.exists(output):
    os.mkdir(output)


#Cargamos el polígono de la Región de Murcia 
my_polygon = saga_api.SG_Get_Data_Manager().Add_Shapes(input+"Contorno_Murcia/Murcia.shp")
print("My_polygon", my_polygon)

with open(input+"Pcp072023.csv") as file:
     data = file.read().replace("Ñ","N").replace(";","\t")

with open(input+"input_data.txt", "+w") as file:
     file.write(data)

#Comprobación generando la tabla directamente con las estaciones
df_estaciones = pd.read_csv(input+"input_data.txt", sep="\t")
print(df_estaciones.head())
for i in range(6, len(df_estaciones.keys())): 
    df_estaciones[df_estaciones[df_estaciones.keys()[i]] < 0.0] = 0
    df_estaciones[df_estaciones[df_estaciones.keys()[i]] == ""] = 0
print(df_estaciones.head())
df_estaciones.to_csv(input+"input_data.txt", sep="\t")
results_estaciones = {"Variable":[], "Media":[], "DevStd":[], "Min":[], "Max":[]}
for i in range(6, len(df_estaciones.keys())): 
    var = df_estaciones.keys()[i]
    results_estaciones["Variable"].append(var)
    results_estaciones["Media"].append(np.mean(df_estaciones[var])/10.0)
    results_estaciones["DevStd"].append(np.std(df_estaciones[var])/10.0)
    results_estaciones["Min"].append(np.min(df_estaciones[var])/10.0)
    results_estaciones["Max"].append(np.max(df_estaciones[var])/10.0)

df_estaciones = pd.DataFrame(results_estaciones)
print(df_estaciones.head())
df_estaciones.to_csv(output+"ResultadosDiarios_Estaciones.csv", sep=';')                                   

    
#Cargamos la tabla con las precipitationes totales mensuales en las estaciones
precipitation = saga_api.SG_Get_Data_Manager().Add_Table(input+"input_data.txt")
n_fields = precipitation.Get_Field_Count()
print("N fields =", n_fields)

results = {"Variable":[], "Media":[], "DevStd":[], "Min":[], "Max":[]}
#Hacemos un bucle recorriendo todos los campos de Precipitacion diaria

# Creamos  o recreamos el directorio de salida de los grids: SE BORRA LO QUE HAYA ANTES!
precipitation_grid_output = output + 'preciptiation_Grid/'
# Create output directory if it doesnt exist.
if os.path.exists(precipitation_grid_output):
    shutil.rmtree(precipitation_grid_output)
if not os.path.exists(precipitation_grid_output):
    os.mkdir(precipitation_grid_output)

for i in range(7, n_fields):

    #Buscamos el campo que queremos plotear
    my_field_name = precipitation.Get_Field_Name(i)
    print(my_field_name)
    results["Variable"].append(my_field_name)

    #Comvertimos la tabla a una Shape de Punto
    precipitation_points = Convert_Table_to_Points(precipitation, "C_X", "C_Y", "ALTITUD")
    print("my_points", precipitation_points)

    #Establecemos el sistema de referencia LON/LAT
    precipitation_points_2 = Set_Coordinate_Reference_System(precipitation_points, proj4_string='+proj=utm +zone=30 +ellps=WGS72 +towgs84=0,0,1.9,0,0,0.814,-0.38 +units=m +no_defs')
    #precipitation_points_2.Save(precipitation_points_output+"precipitation_points_2.shp")

    #Calculamos el grid con un peso gaussiano para la inversa de la distancia.
    gridding_parameters = [
        100,#'TARGET_USER_SIZE'
        550500,#'TARGET_USER_XMIN'
        709500,#'TARGET_USER_XMAX'
        4130500,#'TARGET_USER_YMIN'
        4299500,#'TARGET_USER_YMAX'
        1600,#'TARGET_USER_COLS'
        1700,#'TARGET_USER_ROWS'
        0,#'SEARCH_POINTS_ALL'
        20,#'SEARCH_POINTS_MAX'
        3,#'DW_WEIGHTING' 3=Peso Gaussiano 2=Peso Exponencial 1=Peso Inverso Cuadrado Distancia
        1,#'DW_BANDWITH'
    ]

    my_precipitation_grid = Inverse_Distance_Gridding(precipitation_points_2, field=i, gridding_parameters=gridding_parameters)
   

    #Save precipitation grid
    my_precipitation_grid.Save(precipitation_grid_output+"precipitation_grid_"+my_field_name+".tif")

    #Clipping de los datos del hillshade al recinto de la Región de Murcia.
    my_clipped_precipitation_grid = Clip_Grid_with_Polygon(my_precipitation_grid, my_polygon)
    my_clipped_precipitation_grid.Save(precipitation_grid_output+"clipped_precipitation_grid_"+my_field_name+".tif")
    Export_Grid_to_GeoTiff(my_clipped_precipitation_grid, precipitation_grid_output+"geo_clipped_precipitation_grid_"+my_field_name+".tif")
    #Export_Grid_to_GeoTiff(my_clipped_grid, precipitation_grid_output+"geo_clipped_hillshade.tif")
    #plot_tif(precipitation_grid_output+"precipitation_grid.tif", cscale='gist_rainbow')
    #plot_tif(precipitation_grid_output+"clipped_precipitation_grid_"+my_field_name+".tif", cscale='gist_rainbow')
    mean_precipitation = my_clipped_precipitation_grid.Get_Mean()/10.0
    results["Media"].append(mean_precipitation)
    std_dev_precipitation = my_clipped_precipitation_grid.Get_StdDev()/10.0
    results["DevStd"].append(std_dev_precipitation)
    min_precipitation = my_clipped_precipitation_grid.Get_Min()/10.0
    results["Min"].append(min_precipitation)
    max_precipitation = my_clipped_precipitation_grid.Get_Max()/10.0
    results["Max"].append(max_precipitation)
    print("Precipitacion Media = ", mean_precipitation, "mm")

df = pd.DataFrame(results)
print(df.head())
df.to_csv(output+"ResultadosDiarios.csv", sep=';')
print("Precipitación media mensual:", df['Media'].sum(), "mm")
#from my_colormap import newcmp
#plot_layered_tif(tif_files=[grid_output+"my_clipped_grid.tif", precipitation_grid_output+"my_clipped_precipitation_grid.tif"],
#                 alphas=[1.0, 0.8] , cscales=[mpl.colormaps['gist_gray'], newcmp], filename='layered_map.png')