from os.path import exists
from urllib.request import urlretrieve
import geopandas as gpd
import pandas as pd

def get_gdf_from_wfs(layer):
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
    Get pandas.DataFrame of air quality data from https://go.gv.at/l9lumesakt
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
    df.rename(columns={'Unnamed: 0': 'NAME_KURZ', 
                       'Zeit-LTM': 'time airtemp',
                       'LTM': 'airtemp °C',
                       'Zeit-Wind': 'time wind',
                       'WG': 'windspeed kmh',
                       'WR': 'winddirection °',
                       'Zeit-RF': 'time humidity',
                       'RF': 'relhumidity %',
                       'Zeit-NO2': 'time NO2',
                       'Zeit-NOX': 'time NOX',
                       'Zeit-PM': 'time PM',
                       'Zeit-O3': 'time O3',
                       'Zeit-SO2': 'time SO2',
                       'Zeit-CO': 'time CO'}, inplace=True)
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
    df = pd.read_csv(file, sep=';', encoding='latin1', decimal=',')
    df.set_index('SUB_DISTRICT_CODE_VIE', inplace=True)
    return df

def get_heatvulnerabilityindex_gdf():
    """
    Get geopandas.GeoDataFrame of heat vulnerability from 
    https://www.wien.gv.at/gogv/l9ogdaverageurbanheatvulnerabilityindex
    """
    df = get_heatvulnerabilityindex_df()
    districts = get_gdf_from_wfs('ZAEHLBEZIRKOGD')
    districts['SUB_DISTRICT_CODE_VIE'] = districts['ZBEZ'].astype(int) + 90000
    districts.set_index('SUB_DISTRICT_CODE_VIE', inplace=True)
    gdf = districts.join(df) 
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

def get_uber_movement_gdf():
    """
    Get geopandas.GeoDataFrame of Uber Movement data
    
    Source: https://movement.uber.com/explore/vienna/travel-times
    © 2021 Copyright Uber Technologies, Inc. Data Attributions
    
    Data is made available under [CC BY-NC 3.0 US](https://creativecommons.org/licenses/by-nc/3.0/us/)
    """
    file = 'uber_vienna_statistical_areas.zip'
    url = 'https://github.com/anitagraser/ogd-at-lab-data/raw/main/uber/vienna_statistical_areas.zip'
    if not exists(file):
        urlretrieve(url, file)
    gdf = gpd.read_file(f'zip://{file}')
    gdf['MOVEMENT_ID'] = gdf['MOVEMENT_ID'].astype(int)
    gdf.set_index('MOVEMENT_ID', inplace=True)

    file = 'uber_vienna-statistical_areas-2020-1-All-MonthlyAggregate.zip'
    url = 'https://github.com/anitagraser/ogd-at-lab-data/raw/main/uber/vienna-statistical_areas-2020-1-All-MonthlyAggregate.zip'
    if not exists(file):
        urlretrieve(url, file)
    df = pd.read_csv(file)
    df.set_index('dstid', inplace=True)

    return gdf.join(df)

def get_osm_traces(page=0, bbox='16.18,48.09,16.61,48.32'):
    file = 'osm_traces.gpx'
    url = f'https://api.openstreetmap.org/api/0.6/trackpoints?bbox={bbox}&page={page}'
    if not exists(file):
        urlretrieve(url, file)
    gdf = gpd.read_file(file, layer='track_points')
    # dropping empty columns
    gdf.drop(columns=['ele', 'course', 'speed', 'magvar', 'geoidheight', 'name', 'cmt', 'desc',
       'src', 'url', 'urlname', 'sym', 'type', 'fix', 'sat', 'hdop', 'vdop',
       'pdop', 'ageofdgpsdata', 'dgpsid'], inplace=True) 
    gdf['t'] = pd.to_datetime(gdf['time'])
    gdf.set_index('t', inplace=True)
    return gdf
