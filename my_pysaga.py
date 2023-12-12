#! /usr/bin/env python

#################################################################################
# MIT License

# Copyright (c) 2023 Olaf Conrad

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#################################################################################

#_________________________________________
##########################################
# Initialize the environment...

# Windows: Let the 'SAGA_PATH' environment variable point to
# the SAGA installation folder before importing 'saga_api'!
# This can be defined globally in the Windows system or
# user environment variable settings, in the 'PySAGA/__init__.py'
# file, or in the individual Python script itself. To do the latter
# just uncomment the following line and adjust the path accordingly:
###import os; os.environ['SAGA_PATH'] = os.path.split(os.path.dirname(__file__))[0]

# Windows: The most convenient way to make PySAGA available to all your
# Python scripts is to copy the PySAGA folder to the 'Lib/site-packages/'
# folder of your Python installation. If you don't want to do this or if you
# don't have the rights to do so, you can also copy it to the folder with
# the Python scripts in which you want to use PySAGA, or alternatively
# you can add the path containing the PySAGA folder (e.g. the path to your
# SAGA installation) to the PYTHONPATH environment variable. To do this
# from within your script you can also take the following command (just
# uncomment the following line and adjust the path accordingly):
###import sys, os; sys.path.insert(1, os.path.split(os.path.dirname(__file__))[0])

import os
import sys
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

os.environ['SAGA_PATH'] = 'C:/Users/AEMet/OneDrive - Agencia Estatal de Meteorología/AEMET-Murcia/saga-9.1.1_x64/saga-9.1.1_x64'
sys.path.insert(1, 'C:/Users/AEMet/OneDrive - Agencia Estatal de Meteorología/AEMET-Murcia/saga-9.1.1_x64/saga-9.1.1_x64')

from PySAGA import saga_api

print(saga_api.SG_Get_Tool_Library_Manager().Get_Summary(saga_api.SG_SUMMARY_FMT_FLAT).c_str())
print("PySAGA succesfully imported!")

#_________________________________________
##########################################
def Run_Random_Terrain():
    print('Running: Random Terrain')
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('grid_calculus', '6')
    if not Tool:
        print('Failed to request tool: Random Terrain')
        import sys; sys.exit()

    Tool.Reset()
    Tool.Set_Parameter('RADIUS'          , 25)
    Tool.Set_Parameter('ITERATIONS'      , 250)
    Tool.Set_Parameter('TARGET_USER_SIZE', 10)
    Tool.Set_Parameter('TARGET_USER_XMIN', 0)
    Tool.Set_Parameter('TARGET_USER_XMAX', 2000)
    Tool.Set_Parameter('TARGET_USER_YMIN', 0)
    Tool.Set_Parameter('TARGET_USER_YMAX', 2000)

    if not Tool.Execute():
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        import sys; sys.exit()

    return Tool.Get_Parameter('TARGET_OUT_GRID').asGrid()


#_________________________________________
##########################################
def Run_Slope_Aspect_Curvature(DEM):
    print('Running: Slope, Aspect, Curvature')
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('ta_morphometry', '0')
    if not Tool:
        print('Failed to request tool: Slope, Aspect, Curvature')
        return  None, None, None, None

    Tool.Reset()
    Tool.Set_Parameter('ELEVATION'  , DEM)
    Tool.Set_Parameter('METHOD'     , 6) # '9 parameter 2nd order polynom (Zevenbergen & Thorne 1987)'
    Tool.Set_Parameter('UNIT_SLOPE' , 0) # 'radians'
    Tool.Set_Parameter('UNIT_ASPECT', 1) # 'degree'
    Tool.Set_Parameter('C_LONG'     , saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it
    Tool.Set_Parameter('C_CROS'     , saga_api.SG_Get_Create_Pointer()) # optional output, remove this line, if you don't want to create it

    if not Tool.Execute():
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        import sys; sys.exit()

    return Tool.Get_Parameter('SLOPE' ).asGrid(),\
           Tool.Get_Parameter('ASPECT').asGrid(),\
           Tool.Get_Parameter('C_LONG').asGrid(),\
           Tool.Get_Parameter('C_CROS').asGrid()


#_________________________________________
##########################################
def Run_Grid_Difference(A, B, PythonLoop):
    if not A.is_Compatible(B):
        print('Error: grids [' + A + '] and [' + B + '] are not compatible')
        import sys; sys.exit()

    import time; Time_Start = time.time()

    # ------------------------------------
    # cell by cell, slower than second solution
    if PythonLoop:
        print('Running: Grid Difference (Cell by Cell)\n')
        C = saga_api.SG_Create_Grid(A.Get_System())
        for y in range(0, C.Get_NY()):
            print('\r{:04.1f}%'.format(y * 100. / C.Get_NY()), end='\r', flush=True)
            for x in range(0, C.Get_NX()):
                if A.is_NoData(x, y) or B.is_NoData(x, y):
                    C.Set_NoData(x, y)
                else:
                    C.Set_Value(x, y, A.asDouble(x, y) - B.asDouble(x, y))

    # ------------------------------------
    # using built-in CSG_Grid function 'Subtract()'
    else:
        print('Running: Grid Difference (CSG_Grid::Subtract())')
        C = saga_api.SG_Create_Grid(A)
        C.Subtract(B)

    # ------------------------------------
    Time = time.time() - Time_Start
    print('finished after {:d}min {:02.2f}sec'.format(int(Time / 60.), Time % 60.))
    return C


#_________________________________________
##########################################
def Run_Contour_Lines_from_Grid(Grid):
    print('Running: Contour Lines from Grid')
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('shapes_grid', '5')
    if not Tool:
        print('Failed to request tool: Contour Lines from Grid')
        import sys; sys.exit()

    Tool.Reset()
    Tool.Set_Parameter('GRID', Grid)

    if not Tool.Execute():
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        import sys; sys.exit()

    return Tool.Get_Parameter('CONTOUR').asShapes()


#_________________________________________
##########################################
def Run_Geomorphons(DEM):
    print('Running: Geomorphons')
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('ta_lighting', '8')
    if not Tool:
        print('Failed to request tool: Geomorphons')
        import sys; sys.exit()

    Tool.Reset()
    Tool.Set_Parameter('DEM'      , DEM)
    Tool.Set_Parameter('THRESHOLD', 1)
    Tool.Set_Parameter('RADIUS'   , 10000)
    Tool.Set_Parameter('METHOD'   , 1) # 'line tracing'

    if not Tool.Execute():
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        import sys; sys.exit()

    return Tool.Get_Parameter('GEOMORPHONS').asGrid()


#_________________________________________
##########################################

#_________________________________________
##########################################
def Convert_Table_to_Points(Table, X, Y, Z):
    print('Running: Convert Table to Points')
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('shapes_points', '0')
    if not Tool:
        print('Failed to request tool: Convert Table to Points')
        import sys; sys.exit()

    Tool.Reset()
    Tool.Set_Parameter('TABLE', Table)
    Tool.Set_Parameter('X', X )
    Tool.Set_Parameter('Y', Y )
    Tool.Set_Parameter('Z', Z)

    if not Tool.Execute():
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        import sys; sys.exit()

    return Tool.Get_Parameter('POINTS').asShapes()


#_________________________________________
#_________________________________________
##########################################
def Set_Coordinate_Reference_System(my_shape, proj4_string='+proj=longlat +datum=WGS84 +no_defs'):
    print('Running: Set Coordinate Reference System')
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('pj_proj4', '0')
    if not Tool:
        print('Failed to request tool: Set Coordinate Reference System')
        import sys; sys.exit()

    Tool.Reset()
    Parms = Tool.Get_Parameters()
    Parms('SHAPES').asShapesList().Add_Item(my_shape)
    print("Setting Coordinate Reference System:", proj4_string)
    Tool.Set_Parameter('CRS_FILE', 'my_points.prj')
    Tool.Set_Parameter('CRS_METHOD', 0)
    Tool.Set_Parameter('CRS_PROJ4', proj4_string)
    Tool.Set_Parameter('CRS_EPSG', 4326)
    Tool.Set_Parameter('CRS_EPSG_AUTH', 'EPSG')
    print("Shapes", Tool.Get_Parameter("SHAPES").asString())
    print("CRS_PROJ4", Tool.Get_Parameter("CRS_PROJ4").asString())

    if not Tool.Execute():
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        import sys; sys.exit()

    return Tool.Get_Parameter('SHAPES_OUT').asShapesList().Get_Shapes(0).asShapes()


#_________________________________________
#_________________________________________
##########################################
def Clip_Grid_with_Polygon(my_grid, my_polygon):
    print('Running: Clip Grid with Polygon')
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('shapes_grid', '7')
    if not Tool:
        print('Failed to request tool: Clip Grid with Polygon')
        import sys; sys.exit()

    Tool.Reset()
    Parms = Tool.Get_Parameters()
    Parms('INPUT').asGridList().Add_Item(my_grid)
    Tool.Set_Parameter('POLYGONS', my_polygon)
    Tool.Set_Parameter('EXTENT', 1)
    

    if not Tool.Execute():
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        import sys; sys.exit()

    return Tool.Get_Parameter('OUTPUT').asGridList().Get_Grid(0).asGrid()


#_________________________________________
#_________________________________________
##########################################
def Export_Grid_to_GeoTiff(my_grid, outputfile):
    print('Running: Export Grid to GeoTiff')
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('io_gdal', '2')
    if not Tool:
        print('Failed to request tool: Export Grid to GeoTiff')
        import sys; sys.exit()

    Tool.Reset()
    Parms = Tool.Get_Parameters()
    Parms('GRIDS').asGridList().Add_Item(my_grid)
    Tool.Set_Parameter('FILE', outputfile)
  
    if not Tool.Execute():
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        import sys; sys.exit()

    return True


#_________________________________________
#_________________________________________
##########################################
def Inverse_Distance_Gridding(Points, field, gridding_parameters=[0.021, -9.282, 4.284, 35.301, 43.743, 647, 403, 0, 20, 3, 1]):
    print('Running: Inverse Distance Gridding')
    Tool = saga_api.SG_Get_Tool_Library_Manager().Get_Tool('grid_gridding', '1')
    if not Tool:
        print('Failed to request tool: Inverse Distance Gridding')
        import sys; sys.exit()
    
    Tool.Reset()
    Tool.Set_Parameter('POINTS'          , Points)
    Tool.Set_Parameter('FIELD'          , field)
    Tool.Set_Parameter('TARGET_USER_SIZE', gridding_parameters[0])
    Tool.Set_Parameter('TARGET_USER_XMIN', gridding_parameters[1])
    Tool.Set_Parameter('TARGET_USER_XMAX', gridding_parameters[2])
    Tool.Set_Parameter('TARGET_USER_YMIN', gridding_parameters[3])
    Tool.Set_Parameter('TARGET_USER_YMAX', gridding_parameters[4])
    Tool.Set_Parameter('TARGET_USER_COLS', gridding_parameters[5])
    Tool.Set_Parameter('TARGET_USER_ROWS', gridding_parameters[6])
    Tool.Set_Parameter('SEARCH_POINTS_ALL', gridding_parameters[7])
    Tool.Set_Parameter('SEARCH_POINTS_MAX', gridding_parameters[8])
    Tool.Set_Parameter('DW_WEIGHTING', gridding_parameters[9])
    Tool.Set_Parameter('DW_BANDWITH', gridding_parameters[10])
    '''
    Tool.Set_Parameter('TARGET_USER_SIZE', 1000)
    Tool.Set_Parameter('TARGET_USER_XMIN', 550500)
    Tool.Set_Parameter('TARGET_USER_XMAX', 709500)
    Tool.Set_Parameter('TARGET_USER_YMIN', 4130500)
    Tool.Set_Parameter('TARGET_USER_YMAX', 4299500)
    Tool.Set_Parameter('TARGET_USER_COLS', 160)
    Tool.Set_Parameter('TARGET_USER_ROWS', 170)
    Tool.Set_Parameter('SEARCH_POINTS_ALL', 0)
    Tool.Set_Parameter('SEARCH_POINTS_MAX', 20)
    Tool.Set_Parameter('DW_WEIGHTING', 1)
    #Tool.Set_Parameter('DW_BANDWITH', 10)
    '''

    if not Tool.Execute():
        print('failed to execute tool: ' + Tool.Get_Name().c_str())
        import sys; sys.exit()

    return Tool.Get_Parameter('TARGET_OUT_GRID').asGrid()


#_________________________________________
##########################################
