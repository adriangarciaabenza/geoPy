import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pykrige.ok import OrdinaryKriging

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
                                  
# Carga los datos
lats = np.asarray(df_estaciones["C_Y"])
lons = np.asarray(df_estaciones["C_X"])
values = np.asarray(df_estaciones["P20"])
print("Values:",values)
# Define la cuadrícula sobre la que realizarás el kriging
grid_lon, grid_lat = np.meshgrid(np.linspace(min(lons), max(lons), 40), np.linspace(min(lats), max(lats), 40))

# Definir el modelo de variograma
variogram_model = 'linear'
#variogram_model_parameters = {"slope": 1, "nugget": 0}

# Configura el modelo de kriging ordinario
ok_model = OrdinaryKriging(lons, lats, values, variogram_model=variogram_model)#, variogram_parameters=variogram_model_parameters)

# Realiza el kriging en la cuadrícula
print("Grid_lon shape:", grid_lon.shape)
print(grid_lon[:][0])
print("Grid_lat shape:", grid_lat.shape)
print(grid_lat[:,0])
grid_z, grid_var = ok_model.execute('grid', grid_lon[:][0], grid_lat[:,0])
print(grid_z)
# Reshape para obtener una cuadrícula 2D
grid_z = grid_z.reshape(grid_lon.shape)

# Visualiza los resultados
plt.figure(figsize=(8, 8))
plt.contourf(grid_lon, grid_lat, grid_z, cmap='viridis')
plt.scatter(lons, lats, c=values, cmap='viridis', edgecolor='k', s=100, label='Datos Observados')
plt.colorbar(label='Precipitación')
plt.title('Kriging de Precipitación')
plt.xlabel('Longitud')
plt.ylabel('Latitud')
plt.legend()
plt.show()