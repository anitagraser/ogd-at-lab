def hvplot_with_buffer(gdf, buffer_size, *args, **kwargs):
    """
    Convenience function for plotting a GeoPandas point GeoDataFrame using point markers plus buffer polygons
    
    Parameters
    ----------
    gdf : geopandas.Geodataframe
        point GeoDataFrame to plot
    buffer_size : numeric
        size of the buffer in meters (measured in EPSG:31287)
    """
    buffered = gdf.to_crs('epsg:31287').buffer(buffer_size)
    buffered = gdf.copy().set_geometry(buffered).to_crs('epsg:4326')
    
    plot = ( buffered.hvplot(geo=True,  tiles='OSM', alpha=0.5, line_width=0, *args, **kwargs) * 
      gdf.hvplot(geo=True, hover_cols=['DESIGNATION']) 
    ).opts(active_tools=['wheel_zoom'])
    
    return plot
