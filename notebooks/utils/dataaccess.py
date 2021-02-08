from os.path import exists
from urllib.request import urlretrieve
import geopandas as gpd
import pandas as pd

def gdf_from_wfs(layer):
    """
    Get geopandas.GeoDataFrame from data.wien.gv.at WFS service based on layer name
    
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
    point : shapely.Point
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
        
def get_airquality_df():
    """
    Get data from https://go.gv.at/l9lumesakt
    """
    file = 'lumesakt.csv'
    url = 'https://go.gv.at/l9lumesakt'
    urlretrieve(url, file)
    df = pd.read_csv(file, sep=';', encoding='latin1')
    return df

def get_heatvulnerabilityindex_df():
    """
    Get pandas.DataFrame of heat vulnerability from 
    https://www.wien.gv.at/gogv/l9ogdaverageurbanheatvulnerabilityindex
    """
    file = 'heatvulnerabilityindex.csv'
    url = 'https://www.wien.gv.at/gogv/l9ogdaverageurbanheatvulnerabilityindex'
    if not exists(file):
        urlretrieve(url, file)
    df = pd.read_csv(file, sep=';', encoding='latin1')
    df['AVG_UHVI_A'] = df['AVG_UHVI_A'].str.replace(',', '.').astype(float)
    df['AVG_UHVI_O'] = df['AVG_UHVI_O'].str.replace(',', '.').astype(float)
    df['AVG_UHVI_Y'] = df['AVG_UHVI_Y'].str.replace(',', '.').astype(float)
    df.set_index('SUB_DISTRICT_CODE_VIE', inplace=True)
    return df

def get_heatvulnerabilityindex_gdf():
    """
    Get geopandas.GeoDataFrame of heat vulnerability from 
    https://www.wien.gv.at/gogv/l9ogdaverageurbanheatvulnerabilityindex
    """
    df = get_heatvulnerabilityindex_df()
    districts = gdf_from_wfs('ZAEHLBEZIRKOGD')
    districts['SUB_DISTRICT_CODE_VIE'] = districts['ZBEZ'].astype(int) + 90000
    districts.set_index('SUB_DISTRICT_CODE_VIE', inplace=True)
    gdf = gpd.GeoDataFrame(pd.DataFrame(districts).join(df))
    return gdf

def get_zaehlsprengel_gdf(year=2020):
    """
    Get geopandas.GeoDataFrame of Zählsprengel districts from Statistik Austria
    """
    file = f'OGDEXT_ZSP_1_STATISTIK_AUSTRIA_{year}0101.zip'
    url = f'http://data.statistik.gv.at/data/OGDEXT_ZSP_1_STATISTIK_AUSTRIA_{year}0101.zip'
    if not exists(file):
        urlretrieve(url, file)
    gdf = gpd.read_file(f'zip://{file}')
    return gdf
                             