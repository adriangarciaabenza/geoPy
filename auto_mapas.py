from plot_gdal import *
from my_pysaga import *


print('This is a simple script to demonstrate the usage of SAGA and its tools through Python.')

Verbose = False
if not Verbose:
    saga_api.SG_UI_ProgressAndMsg_Lock(True)

import os;
output = './ResumenesClimaticos/results/'
if not os.path.exists(output):
    os.mkdir(output)


#Cargamos el polígono de la Región de Murcia 
my_polygon = saga_api.SG_Get_Data_Manager().Add_Shapes("./ResumenesClimaticos/assets/Contorno_Murcia/Murcia.shp")
print("My_polygon", my_polygon)
polygon_output = output + 'My_Polygon/'
if not os.path.exists(polygon_output):
    os.mkdir(polygon_output)
my_polygon.Save(polygon_output+"my_polygon.shp")

#Cargamos las estaciones de la Región de Murcia 
estaciones = saga_api.SG_Get_Data_Manager().Add_Shapes("./ResumenesClimaticos/assets/Estaciones_Murcia/Estaciones.shp")
print("Estaciones", estaciones)
estaciones_output = output + 'Estaciones/'
if not os.path.exists(estaciones_output):
    os.mkdir(estaciones_output)
estaciones.Save(estaciones_output+"estaciones.shp")
estaciones.Save(estaciones_output+"estaciones.tif")

#Cargamos el hillshade de Murcia
my_hillshade = saga_api.SG_Get_Data_Manager().Add_Grid("./ResumenesClimaticos/assets/Hillshade_Murcia/Hillshade_of_Mdt_Murcia.sgrd")
hillshade_output = output + 'My_Hillshade/'
if not os.path.exists(hillshade_output):
    os.mkdir(hillshade_output)
my_hillshade.Save(hillshade_output+"my_hillshade.tif")

#Clipping de los datos del hillshade al recinto de la Región de Murcia.
my_clipped_grid = Clip_Grid_with_Polygon(my_hillshade, my_polygon)
grid_output = output + 'My_Grid/'
if not os.path.exists(grid_output):
    os.mkdir(grid_output)
my_clipped_grid.Save(grid_output+"my_clipped_grid.tif")

plot_tif(hillshade_output+"my_hillshade.tif", filename="hillshade_Murcia.png")
plot_tif(grid_output+"my_clipped_grid.tif", filename="clipped_grid_Murcia.png")

#Cargamos la tabla con las precipitaciones totales mensuales en las estaciones
precipitacion = saga_api.SG_Get_Data_Manager().Add_Table("./ResumenesClimaticos/assets/precipitacion_sep_2023_automaticas.txt")
n_fields = precipitacion.Get_Field_Count()
print("N fields =", n_fields)

#Buscamos el campo que queremos plotear
my_field_name = precipitacion.Get_Field_Name(n_fields-1)
print(my_field_name)

#Comvertimos la tabla a una Shape de Puntos
precipitacion_points = Convert_Table_to_Points(precipitacion, "C_X", "C_Y", "ALTITUD")
precipitacion_points_output = output + 'Precipitacion_Points/'
if not os.path.exists(precipitacion_points_output):
    os.mkdir(precipitacion_points_output)
precipitacion_points.Save(precipitacion_points_output+"precipitacion_points.shp")
print("my_points", precipitacion_points)

#Establecemos el sistema de referencia LON/LAT
precipitacion_points_2 = Set_Coordinate_Reference_System(precipitacion_points, proj4_string='+proj=utm +zone=30 +ellps=WGS72 +towgs84=0,0,1.9,0,0,0.814,-0.38 +units=m +no_defs')
precipitacion_points_2.Save(precipitacion_points_output+"precipitacion_points_2.shp")

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
    3,#'DW_WEIGHTING'
    1,#'DW_BANDWITH'
]

my_precipitacion_grid = Inverse_Distance_Gridding(precipitacion_points, field=n_fields-1, gridding_parameters=gridding_parameters)
precipitacion_grid_output = output + 'Precipitacion_Grid/'
if not os.path.exists(precipitacion_grid_output):
    os.mkdir(precipitacion_grid_output)
my_precipitacion_grid.Save(precipitacion_grid_output+"precipitacion_grid.tif")
my_precipitacion_grid.Save(precipitacion_grid_output+"precipitacion_grid.sgrd")

#Clipping de los datos del hillshade al recinto de la Región de Murcia.
my_clipped_precipitacion_grid = Clip_Grid_with_Polygon(my_precipitacion_grid, my_polygon)
my_clipped_precipitacion_grid.Save(precipitacion_grid_output+"my_clipped_precipitacion_grid.tif")
my_clipped_precipitacion_grid.Save(precipitacion_grid_output+"my_clipped_precipitacion_grid.sgrd")
Export_Grid_to_GeoTiff(my_clipped_precipitacion_grid, precipitacion_grid_output+"geo_clipped_precipitacion_grid.tif")
Export_Grid_to_GeoTiff(my_clipped_grid, precipitacion_grid_output+"geo_clipped_hillshade.tif")
plot_tif(precipitacion_grid_output+"precipitacion_grid.tif", cscale='gist_rainbow')
plot_tif(precipitacion_grid_output+"my_clipped_precipitacion_grid.tif", cscale='gist_rainbow')

from my_colormap import newcmp
plot_layered_tif(tif_files=[grid_output+"my_clipped_grid.tif", precipitacion_grid_output+"my_clipped_precipitacion_grid.tif"],
                 alphas=[1.0, 0.8] , cscales=[mpl.colormaps['gist_gray'], newcmp], filename='layered_map.png')
