from plot_gdal import *
from my_pysaga import *
import pandas as pd
import numpy as np

print('Running AutoMapas Temperatura Diaria \n This script uses SAGA and its tools through Python.')

Verbose = False
if not Verbose:
    saga_api.SG_UI_ProgressAndMsg_Lock(True)

import os;
input = './AppInput/'
output = './AppOutput/'
if not os.path.exists(input):
    os.mkdir(input)
if not os.path.exists(output):
    os.mkdir(output)



def calculate_grid_temperatures(upload_file):

    #Cargamos el polígono de la Región de Murcia 
    my_polygon = saga_api.SG_Get_Data_Manager().Add_Shapes(input+"Contorno_Murcia/Murcia.shp")
    print("My_polygon", my_polygon)

    with open(upload_file) as file:
        data = file.read().replace("ñ","n").replace(";","\t")

    with open(input+"input_data.txt", "+w") as file:
        file.write(data)

    #Comprobación generando la tabla directamente con las estaciones
    df_estaciones = pd.read_csv(input+"input_data.txt", sep="\t")
    print(df_estaciones.head())

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

        
    #Cargamos la tabla con las temperaturees totales mensuales en las estaciones
    temperature = saga_api.SG_Get_Data_Manager().Add_Table(input+"input_data.txt")
    n_fields = temperature.Get_Field_Count()
    print("N fields =", n_fields)

    results = {"Variable":[], "Media":[], "DevStd":[], "Min":[], "Max":[]}
    #Hacemos un bucle recorriendo todos los campos de temperatura diaria
    for i in range(6, n_fields): #n_fields
        #Buscamos el campo que queremos plotear
        my_field_name = temperature.Get_Field_Name(i)
        print(my_field_name)
        results["Variable"].append(my_field_name)

        #Comvertimos la tabla a una Shape de Punto
        temperature_points = Convert_Table_to_Points(temperature, "C_X", "C_Y", "ALTITUD")
        print("my_points", temperature_points)

        #Establecemos el sistema de referencia LON/LAT
        temperature_points_2 = Set_Coordinate_Reference_System(temperature_points, proj4_string='+proj=utm +zone=30 +ellps=WGS72 +towgs84=0,0,1.9,0,0,0.814,-0.38 +units=m +no_defs')
        #temperature_points_2.Save(temperature_points_output+"temperature_points_2.shp")

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
            2,#'DW_WEIGHTING' 3=Peso Gaussiano 2=Inverse Distance Squared
            1,#'DW_BANDWITH'
        ]

        my_temperature_grid = Inverse_Distance_Gridding(temperature_points_2, field=i, gridding_parameters=gridding_parameters)
        temperature_grid_output = output + 'temperature_Grid/'
        if not os.path.exists(temperature_grid_output):
            os.mkdir(temperature_grid_output)
        my_temperature_grid.Save(temperature_grid_output+"temperature_grid.tif")

        #Clipping de los datos del hillshade al recinto de la Región de Murcia.
        my_clipped_temperature_grid = Clip_Grid_with_Polygon(my_temperature_grid, my_polygon)
        my_clipped_temperature_grid.Save(temperature_grid_output+"clipped_temperature_grid.tif")
        #Export_Grid_to_GeoTiff(my_clipped_temperature_grid, temperature_grid_output+"geo_clipped_temperature_grid.tif")
        #Export_Grid_to_GeoTiff(my_clipped_grid, temperature_grid_output+"geo_clipped_hillshade.tif")
        #plot_tif(temperature_grid_output+"temperature_grid.tif", cscale='gist_rainbow')
        #plot_tif(temperature_grid_output+"clipped_temperature_grid.tif", cscale='gist_rainbow')

        mean_temperature = my_clipped_temperature_grid.Get_Mean()/10.0
        results["Media"].append(mean_temperature)
        std_dev_temperature = my_clipped_temperature_grid.Get_StdDev()/10.0
        results["DevStd"].append(std_dev_temperature)
        min_tempperature = my_clipped_temperature_grid.Get_Min()/10.0
        results["Min"].append(min_tempperature)
        max_temperature = my_clipped_temperature_grid.Get_Max()/10.0
        results["Max"].append(max_temperature)
        print("Temperatura Media = ", mean_temperature, "ºC")

    df = pd.DataFrame(results)
    print(df.head())
    df.to_csv(output+"ResultadosDiarios.csv", sep=';')

    return df
#from my_colormap import newcmp
#plot_layered_tif(tif_files=[grid_output+"my_clipped_grid.tif", temperature_grid_output+"my_clipped_temperature_grid.tif"],
#                 alphas=[1.0, 0.8] , cscales=[mpl.colormaps['gist_gray'], newcmp], filename='layered_map.png')