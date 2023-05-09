"""Tools for manipulating geospatial data on Jornada's ArcGIS Online account.
Some of this relies on the ArcGIS python API, which is documented here:

    https://developers.arcgis.com/python/api-reference/index.html

Some guides are here:

    https://developers.arcgis.com/python/guide/accessing-and-creating-content

"""
import os
import geopandas as gpd
import fiona
from arcgis import features as fs
import xml.etree.ElementTree as ET

def add_geojson_item(fname, gis, gis_folder, properties=None,
                     publish_after=False, remove_after=False):
    """Create a geojson item in ArcGIS (online or enterprise)

    Parameters
    ----------
    fname : _type_
        _description_
    gis : _type_
        _description_
    gis_folder : _type_
        _description_
    properties : dict, optional
        _description_, by default {}
    publish_after : bool, optional
        _description_, by default False
    remove_after : bool, optional
        _description_, by default False
    """
    if bool(properties):
        properties.update({'type': 'GeoJson'})
    else:
        properties = {'type':'GeoJson','description': 'No description given',
            'title': fname, 'tags': ''}

    # Add item to AGOL in the given folder.
    item = gis.content.add(properties, fname, folder=gis_folder)
    # Remove if requested
    if remove_after:
        os.remove(fname)
    # Publish if requested and return
    if publish_after:
        item_p = item.publish(overwrite=True)#xfile_type='geojson')
        return(item, item_p)
    else:
        return(item)


def jornada_fs_definitions(flc, metadf):
    """Update a featureLayerCollections definitions with a dictionary that
    defines preferred options and metadata for Jornada spatial files.

    The properties that can be assigned to a feature service are here:
    https://developers.arcgis.com/rest/services-reference/enterprise/feature-service.htm

    Parameters
    ----------
    flc : object
        A featureLayerCollection in ArcGIS (online or enterprise)
    metadf : pandas DataFrame
        A dataframe with metadata for the geopackage being added
    """
    defsDict = {
        "copyrightText": metadf.license.iloc[0] + ' - ' + metadf.access_use_text.iloc[0],
        "objectIdField" : "FID",
        "globalIdField" : "GlobalID",
        "maxRecordCount": 25000,
        "serviceDescription": "A service for publishing geospatial "
            "data for Jornada research projects",
        "hasVersionedData" : False,
        "summary": "Feature service for " + metadf.package_name.iloc[0] + "/" + metadf.gpkg_fname.iloc[0],
        "description": metadf.package_abstract.iloc[0],
        "tags": metadf.package_tags.iloc[0], # Only works for item
        "capabilities": 'Editing,Query,Update,Uploads,Delete,Sync,Extract',
        "spatialReference": {"wkid": 4326,"latestWkid": 4326},
        "initialExtent":{
            "xmax": 180.0,"ymin": -90.0,"xmin": -180.0,"ymax": 90.0,
            "spatialReference": {"wkid" : 4326, "latestWkid" : 4326}
        },
        "fullExtent":{
            "xmax": 180.0,"ymin": -90.0,"xmin": -180.0,"ymax": 90.0,
            "spatialReference": {"wkid" : 4326, "latestWkid" : 4326}
        }
        }
    return(defsDict)


def jornada_layer_definitions(metadf, item_pub=None):
    """Create a layer definition dictionary from published layer properties in
    ArcGIS. Both the item attributes are used, as are the feature layer
    properties.

    Parameters
    ----------
    item_pub : object
        A published ArcGIS item
    """
    if item_pub is not None:
        flayer = item_pub.layers[0]
        defsDict = {"geometryType" : flayer.properties["geometryType"],
            "globalIdField" : flayer.properties["globalIdField"],
            "objectIdField" : flayer.properties["objectIdField"],
            "extent" : flayer.properties["extent"],
            "name" : flayer.properties["name"],
            "fields" : flayer.properties["fields"],
            "description" : (metadf.layer_abstract.iloc[0] + '\n ' + 
                metadf.package_abstract.iloc[0]),
            "tags" : (metadf.package_tags.iloc[0] + ',' + 
                metadf.layer_tags.iloc[0])
        }
    else:
        defsDict = {#"geometryType" : metadf.geom_type.iloc[0],
            "globalIdField" : "GlobalID",
            "objectIdField" : "FID",
            #"extent" : {
            #    "xmax": 180.0,"ymin": -90.0,"xmin": -180.0,"ymax": 90.0,
            #    "spatialReference": {"wkid" : 4326, "latestWkid" : 4326}
            #    },
            "name" : metadf.layer_name.iloc[0],
            #"fields" : metadf.attributes.iloc[0],
            "description" : (metadf.layer_abstract.iloc[0] + '\n ' + 
                metadf.package_abstract.iloc[0]),
            "tags" : (metadf.package_tags.iloc[0] + ',' + 
                metadf.layer_tags.iloc[0])
        }
    return(defsDict)

def geopkg_to_multi_fs(gis, geojson_folder, flc, gpkg, metadf,
                      clean_local=False, upsert=False):
    """[summary]

    Parameters
    ----------
    gis : [type]
        [description]
    geojson_folder : [type]
        [description]
    flc : [type]
        [description]
    gpkg : [type]
        [description]
    metadf : [type]
        [description]
    clean_local : bool, optional
        [description], by default False
    upsert : bool, optional
        [description], by default False
    """
    pkg_layers = fiona.listlayers(gpkg)
    lyrList = [] # Layer definition list
    itemList = [] # GeoJSON item list
    dfList = [] # DataFrame list
    
    for j, lyr in enumerate(pkg_layers):
        # Get the metadata anc create a geojson
        meta = metadf.loc[metadf.layer_name==lyr,:]
        layer_geojson = gpkglayer_to_geojson(gpkg, lyr)
        # Put a geojson on AGOL. This just creates a static geoJSON item there
        item = add_geojson_item(layer_geojson, gis, geojson_folder,
            properties=jornada_layer_definitions(meta),
            remove_after=clean_local)
        # Publish item, which creates a hosted feature layer
        item_s = item.publish(file_type='geojson')
        # Add layer definition and item to lists
        lyrList.append(jornada_layer_definitions(
            meta, item_s)) # get dict from item properties
        itemList.append(item)
        # Convert layer to dataframe and add to dataframe list
        #dfList.append(fs.GeoAccessor.from_layer(item_s.layers[0]))
        item_s.delete()
    
    # Update the FeatureLayerCollection with the new layer definitions
    dictUpdate = {"layers": lyrList}
    flc.manager.add_to_definition(dictUpdate)
    
    # Cycle through the layers and 
    for j in range(len(pkg_layers)):
        # Add the dataframe to each defined layer in newFtLC
        #result = newFtLC.layers[j].edit_features(adds = dfList[j])
        # Or directly append the geojson item
        result = flc.layers[j].append(itemList[j].id,
            upload_format='geojson',upsert=upsert)
        print(result)

def geopkg_to_single_fs(gis, geojson_folder, gpkg, metadf,
                        clean_local=False):
    """[summary]

    Parameters
    ----------
    gis : [type]
        [description]
    geojson_folder : [type]
        [description]
    gpkg : [type]
        [description]
    metadf : [type]
        [description]
    clean_local : bool, optional
        [description], by default False
    """
    pkg_layers = fiona.listlayers(gpkg)
    itemList = [] # GeoJSON item list
    fsList = [] # Published feature service list
    
    for j, lyr in enumerate(pkg_layers):
        print(lyr)
        meta = metadf.loc[metadf.layer_name==lyr,:]
        try:
            layer_geojson = gpkglayer_to_geojson(gpkg, lyr)
            # Put a geojson on AGOL. This just creates a static geoJSON item
            # then publishes it as a feature service
            item, item_fs = add_geojson_item(layer_geojson, gis, geojson_folder,
                properties=jornada_layer_definitions(meta),
                publish_after=True, remove_after=clean_local)
            itemList.append(item)
            fsList.append(item_fs)
        except:
            print('skipping layer: ' +  lyr)
            pass

    return(itemList, fsList)

def gdf_to_single_fs(gis, agol_folder, gdf, metadf,
                     tags=['Jornada', 'jgeo'], local_folder='tmp/',
                     clean_local=False):
    """[summary]

    Parameters
    ----------
    gis : [type]
        [description]
    geojson_folder : [type]
        [description]
    gpkg : [type]
        [description]
    metadf : [type]
        [description]
    clean_local : bool, optional
        [description], by default False
    """
    layer_properties={'title':metadf.f_table_name[0],
                      'description':metadf.abstract[0],
                      'tags':tags}
    try:
        layer_geojson = geodf_to_geojson(gdf, lyr, dirname=local_folder)
        print(layer_geojson)
        # Put a geojson on AGOL. This just creates a static geoJSON item
        # then publishes it as a feature service
        item, item_fs = add_geojson_item(layer_geojson, gis, gis_folder,
            properties=layer_properties,
            publish_after=True, remove_after=clean_local)
    except:
        print('skipping layer: ' +  layer_properties['title'])
        pass
    return(item, item_fs)


def qmd_to_agol(agol_title, qmd):
    """_summary_

    For other properties see here:

    https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.ContentManager.add

    Parameters
    ----------
    agol_title : _type_
        _description_
    qmd : _type_
        _description_
    """
    root = ET.fromstring(qmd) # read qmd XML
    kw = root.find('keywords') # extract keywords tree
    # Make a properties dictionary
    props = {
        "title":agol_title,
        "description":root.find('abstract').text,
        "tags":','.join([e.text for e in kw.findall('keyword')]),
        "licenseInfo":root.find('rights').text,
        "typeKeywords":"Geoscientific, Environment" #not sure if this is right
        }
    return(props)
