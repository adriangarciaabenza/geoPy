import osgeo.gdal
import osgeo.ogr
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import sys
import cartopy.crs as ccrs
print("Gdal imported succesfully!")

def plot_tif(tif_file, filename="Tiff.png", cscale='gist_gray', levs=np.linspace(-10, 50, 1000, endpoint=True)):
    try:
        tif = osgeo.gdal.Open(tif_file)
    except:
        print('The file does not exist.')
        sys.exit(0)

    band1 = tif.GetRasterBand(1)
    band1Array = band1.ReadAsArray()
    band1Array[band1Array <= 1.0e-3] = -10

    #Ploteamos el archivo tif resultante
    f = plt.figure() 
    plt.imshow(band1Array, cmap=mpl.colormaps[cscale], interpolation='gaussian') 
    plt.savefig(filename) 
    plt.show()

def plot_layered_tif(tif_files=[], alphas=[], filename="Tiff.png", cscales=['gist_gray']):
    f = plt.figure()
    i = 0
    for tif_file in tif_files:
        try:
            tif = osgeo.gdal.Open(tif_file)
        except:
            print('The file does not exist.')
            sys.exit(0)

        band1 = tif.GetRasterBand(1)
        band1Array = band1.ReadAsArray()
        band1Array[band1Array <= 1.0e-3] = -100
        if i == 1:
            band1Array = band1Array/10.0
        extent=(0.0, 145.0, -145.0, 0.0)
        #Ploteamos el archivo tif resultante
        my_plot = plt.imshow(band1Array, alpha=alphas[i], cmap=cscales[i], vmin=-1, vmax=300.0, interpolation='gaussian', extent=extent) 
        if i > 0:
            f.colorbar(my_plot)
        i = i+1

    plt.show() 
    plt.savefig(filename) 

