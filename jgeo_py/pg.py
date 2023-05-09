import sqlalchemy as sqla
import pandas as pd
import geopandas as gpd
import os

def table_to_gdf(conn, schema, layer):
    """_summary_

    Parameters
    ----------
    conn : _type_
        _description_
    schema : _type_
        _description_
    layer : _type_
        _description_
    """
    gdf = gpd.GeoDataFrame.from_postgis("SELECT * FROM {0}.{1};".format(
        schema, layer), conn, geom_col='geom', index_col='ogc_fid',
        coerce_float=True)
    return(gdf)

def md_dict(conn, schema, layer):
    """_summary_

    Parameters
    ----------
    conn : _type_
        _description_
    schema : _type_
        _description_
    layer : _type_
        _description_
    """
    md = pd.read_sql("SELECT * FROM public.qgis_layer_metadata WHERE \
        f_table_name = '{0}' AND f_table_schema = '{1}';".format(layer, schema),
         conn)
    return(md.to_dict('records')[0])

def table_to_geojson(conn, schema, layer, outdir='tmp'):
    """Read a table layer and write out to a geojson file.

    Parameters
    ----------
    conn : _type_
        _description_
    schema : _type_
        _description_
    layer : _type_
        _description_
    outdir : str, optional
        _description_, by default 'tmp'
    """
    gdf = table_to_gdf(conn, schema, layer)
    fname = os.path.join(outdir, layer + '.geojson')
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    gdf.to_file(fname, driver='GeoJSON')
    return(fname) 