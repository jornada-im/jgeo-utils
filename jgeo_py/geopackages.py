"""Tools for creating geopackages from other spatial data and attaching
metadata.
"""
import geopandas as gpd
import pandas as pd
import os
from datetime import datetime
import fiona

def gdb_to_gpkg(gdb_fname, gdb_layers, gpkg_name):
    """[summary]

    Parameters
    ----------
    gdb_fname : [type]
        [description]
    gdb_layers : [type]
        [description]
    gpkg_name : [type]
        [description]
    """
    # Create a log list
    log = []
    print("  creating " + gpkg_name)
    # Loop through the geodatabase layers
    for l in gdb_layers:
        # Open layer and get some log values
        with fiona.open(gdb_fname, layer=l) as src:
            n_feat = str(len(src))
            try:
                meta = src.meta
                geometry = meta['schema']['geometry']
            except:
                geometry = 'Exception'
                pass
        # If it has geometry (no data tables or exceptions), read layer 
        # with geopandas and write to geopackage
        if (geometry != 'None' and geometry != 'Exception'):
            added = 'True'
            # Load layer and write to geopackage (GPKG driver allows write)
            print("    adding layer " + l)
            geol = gpd.read_file(gdb_fname, layer=l)
            geol.to_file(gpkg_name, layer=l, driver="GPKG")
        # If not skip it
        else:
            added = 'False'
            print("    excluding layer " + l)

        # Fill the log
        log.append([gdb_fname, l, geometry, n_feat, added, gpkg_name,
            datetime.now()])
    
    # Create and return log dataframe
    logdf = pd.DataFrame(log, columns=['origin_gdb','layer_name','geom_type',
        'n_features','added_to_gpkg','gpkg_fname','dt_added'])
    
    return(logdf)

    
def gpkg_metadata_table(gpkg_path, gpkg_abstract, gpkg_tags,
    gdb_list=[], package_name=None):
    """[summary]

    Parameters
    ----------
    gpkg_path : [type]
        [description]
    gpkg_abstract : [type]
        [description]
    gpkg_tags : [type]
        [description]
    gdb_list : list, optional
        [description], by default []
    package_name : [type], optional
        [description], by default None

    Returns
    -------
    [type]
        [description]
    """
        
    gpkg_fname = os.path.basename(gpkg_path)
    if package_name is None:
        package_name = gpkg_fname.split('.')[0]
        
    metadata = []
    gpkg_layers = fiona.listlayers(gpkg_path)

    for l in gpkg_layers:
        with fiona.open(gpkg_path, layer=l) as src:
            n_feat = str(len(src))
            origin = 'not checked'
            # Try to get metadata
            try:
                meta = src.meta
                geometry = meta['schema']['geometry']
                attrib = list(meta['schema']['properties'].keys())
            except:
                geometry = 'Exception'
                attrib = 'None'
                pass

        if bool(gdb_list): # evaluates to true if list is not empty
            origin = 'other'
            for gdb in gdb_list:
                gdb_layers = fiona.listlayers(gdb)
                if l in gdb_layers:
                    origin = os.path.basename(gdb)
            
        # Fill the metadata list
        metadata.append([package_name, gpkg_fname, l, geometry, attrib,
            n_feat, origin, gpkg_abstract, gpkg_tags,
            'layer abstract','layer summary','layer tags',
            'metadata link', 'data link',
            'Jornada IM Team',
            'jornada.data@nmsu.edu',
            'Creative Commons Attribution 4.0',
            'Restricted to users who have completed the Jornada Spatial Data '
            'Release Policy Agreement form (https://forms.gle/E8gGMzzBr7v5BSF36)'
            ', and indicated they agree with the policy.',
            datetime.now()])

    # Create and return metadata dataframe
    mdf = pd.DataFrame(metadata, columns=['package_name','gpkg_fname',
        'layer_name','geom_type','attributes','n_features','origin_gdb',
        'package_abstract','package_tags','layer_abstract','layer_summary',
        'layer_tags','metadata_link','data_link','contact_name','contact_email',
        'license','access_use_text','date_read'])
        
    return mdf