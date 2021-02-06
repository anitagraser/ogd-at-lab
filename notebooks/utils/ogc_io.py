from os.path import exists
from urllib.request import urlretrieve
import geopandas as gpd

def gdf_from_wfs(layer):
    """
    Get GeoPandas GeoDataFrame from data.wien.gv.at WFS service based on layer name
    
    Parameters
    ----------
    layer : string
        WFS layer name 
    """
    file = f'{layer}.json'
    url = f"https://data.wien.gv.at/daten/geo?service=WFS&request=GetFeature&version=1.1.0&typeName=ogdwien:{layer}&srsName=EPSG:4326&outputFormat=json"
    if not exists(file):
        urlretrieve(url, file)
    return gpd.read_file(file)

