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


def upsert_df_to_table(df, key, engine, tmp_table, dest_table,
                       schema='public'):
    """Update/insert ('upsert) a pandas dataframe into a PostgreSQL table

    Since the pandas `to_sql` method has no method to update/insert, this
    essentially creates a temporary table to hold the updated dataframe rows,
    deletes the matching rows (by key) in the destination table, and then
    appends the new/updated rows.
    """
    # Make sure the updated dataframe has the 'key' column as index
    df = df.set_index(key)

    # Put the updated dataframe into a temporary PG table
    df.to_sql(tmp_table, engine, if_exists='replace', index=True, schema=schema)

    # Get the connection/transaction objects
    conn = engine.connect()
    trans = conn.begin()

    try:
        # Delete the rows in the destination table that we are going to "upsert"
        conn.execute(sqla.text("DELETE FROM {0}.{1} WHERE {2} IN (SELECT {2} FROM {0}.{3})".format(
            schema, dest_table, key, tmp_table)))
        trans.commit()

        # Insert the changed rows
        df.to_sql(dest_table, engine, if_exists='append', index=True)
    except:
        trans.rollback()
        raise