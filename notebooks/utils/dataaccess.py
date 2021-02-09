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
    df = pd.read_csv(file, sep=';', encoding='latin1', skiprows=1)
    df.drop([0, 1], inplace=True)
    for col in ['LTM', 'WG', 'WR', 'RF', 'NO2', 'NOX', 'PM10', 'PM10.1', 'PM25', 'PM25.1', 'O3', 'O3.1', 'SO2', 'CO', 'CO.1']:
        df[col] = df[col].str.replace(',', '.')
        df[col] = df[col].str.replace('NE', '')
        df[col] = df[col].str.replace('---', '')
        df[col] = df[col].apply(pd.to_numeric,errors='coerce')
    df.rename(columns={'Unnamed: 0': 'NAME_KURZ'}, inplace=True)
    df.rename(columns={'Zeit-LTM': 'time airtemp'}, inplace=True)
    df.rename(columns={'LTM': 'airtemp °C'}, inplace=True)
    df.rename(columns={'Zeit-Wind': 'time wind'}, inplace=True)
    df.rename(columns={'WG': 'windspeed kmh'}, inplace=True)
    df.rename(columns={'WR': 'winddirection °'}, inplace=True)
    df.rename(columns={'Zeit-RF': 'time humidity'}, inplace=True)
    df.rename(columns={'RF': 'relhumidity %'}, inplace=True)
    df.rename(columns={'Zeit-NO2': 'time NO2'}, inplace=True)
    df.rename(columns={'Zeit-NOX': 'time NOX'}, inplace=True)
    df.rename(columns={'Zeit-PM': 'time PM'}, inplace=True)
    df.rename(columns={'Zeit-O3': 'time O3'}, inplace=True)
    df.rename(columns={'Zeit-SO2': 'time SO2'}, inplace=True)
    df.rename(columns={'Zeit-CO': 'time CO'}, inplace=True)
    df.set_index('NAME_KURZ', inplace=True)
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
    for col in ['AVG_UHVI_A', 'AVG_UHVI_O', 'AVG_UHVI_Y']:
        df[col] = df[col].str.replace(',', '.').apply(pd.to_numeric,errors='coerce')
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
                             