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

def get_elevation(point):
    """
    Retrieve elevation info from the Austrian Elevation Service
    
    Implementation based on https://github.com/maegger/AustrianElevation/blob/6e0f468b6094caace6cd35f00704e4087e851cec/tree/AustrianElevation/AustrianElevation.py#L97
    
    Parameters
    ----------
    point : Shapely Point
        Point in EPSG:3857 
    """
    x = point.x
    y = point.y
    mod_x_path = x % 20000;
    path_x = x - mod_x_path;
    database = int(path_x );
    mod_y = y % 10;
    raster_y = y - mod_y;
    mod_x = x % 10;
    raster_x = int(x - mod_x);
    file = f'{int(raster_y)}.txt'
    url = f"https://raw.githubusercontent.com/maegger/{database}/master/{int(raster_y)}.txt"
    if not exists(file):
        urlretrieve(url, file)
    data = open(file, 'r')
    for line in data:
        x_wert =  int(line.split(' ', 1 )[0])
        if x_wert == raster_x:
            elevationall = line.split(' ', 1 )[1]
            return int(elevationall)
        