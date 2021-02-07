import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def location_to_gdf(location, address=None):
    """
    Convert GeoPy Location to GeoPandas GeoDataFrame
    
    Parameters
    ----------
    location : GeoPy.Location
        Location info to be used as the GeoDataFrame geometry
    address : string
        Optional address string to be stored in the GeoDataFrame column 'address'
    """
    gdf = gpd.GeoDataFrame(pd.DataFrame([
        {'geometry': Point(location.longitude, location.latitude), 'address': address}
    ])).set_crs('epsg:4326')
    return gdf
