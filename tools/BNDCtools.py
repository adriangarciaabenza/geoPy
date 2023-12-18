import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import cartopy.crs as ccrs
from shapely.geometry import Point
from datetime import datetime


class BNDCdataSet(gpd.GeoDataFrame):
    """
    Main class representing a dataset from a BNDC consult

    """
    def __init__(self, data=None, geometry=None, table_type=None, date=None, **kwargs):
        # Use GeoPandas GeoDataFrame constructor
        super().__init__(data, geometry=geometry, **kwargs)
        
        self.table_type = table_type 
        self.date = date

    @classmethod
    def from_csv(cls, csv_path):
        # Read CSV file
        df = pd.read_csv(csv_path, sep=';')

        # Convert the DataFrame to a GeoDataFrame with Point geometries
        geometry = [Point(xy) for xy in zip(df['C_X'], df['C_Y'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:25830')  # Assuming ETRS89/UTM30

        # Extract type and date information from the CSV file or set default values
        data_type = "Standard"
        data_date = datetime(1980, 1, 1)

        # Create an instance of BNDCdataSet
        return cls(data=gdf, table_type=data_type, date=data_date)
    
    def __str__(self):
        return super().__str__()
