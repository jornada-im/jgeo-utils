from shapely.geometry import box
from osgeo import ogr
import datetime as dt
# Some functions

def update_md_record_id(current_id, gdf, schemaname, tablename):
    """_summary_

    Parameters
    ----------
    current_id : _type_
        _description_
    gdf : _type_
        _description_
    schemaname : _type_
        _description_
    tablename : _type_
        _description_
    """
    new_id = current_id
    current_id_fields = current_id.split(' ')
    new_id = new_id.replace(current_id_fields[6], 'srid={0}'.format(gdf.crs.to_epsg()))
    new_id = new_id.replace(current_id_fields[7], 'type={0}'.format(gdf.geom_type[1]))
    new_id = new_id.replace(current_id_fields[9], 'table="{0}"."{1}"'.format(schemaname, tablename))
    return(new_id)

def update_md_qmd(current_rec, gdf, schemaname, tablename, abstract):
    """_summary_

    Parameters
    ----------
    current_rec : _type_
        _description_
    gdf : _type_
        _description_
    schemaname : _type_
        _description_
    tablename : _type_
        _description_
    abstract : _type_
        _description_
    """
    # Read the qmd into an elementtree
    root = ET.fromstring(current_rec.qmd.values[0])
    # Make some changes to the XML element contents
    root.find('identifier').text = update_md_record_id(current_rec.identifier.values[0],
                                                       gdf, schemaname,
                                                       tablename)
    root.find('parentidentifier').text = 'jgeo/{0}'.format(schemaname)
    root.find('language').text = 'en'
    # title is a litte different than tablename for jrn_studies
    if schemaname=='jrn_studies':
        root.find('title').text = tablename.split('_', 1)[1]
    else:
        root.find('title').text = tablename
    root.find('abstract').text = abstract
    # These are hard to fill in - leaving as is
    root.find('crs').text = ''
    root.find('extent').text = '' # Contains a "spatial" sub-element that could be changed
    return(ET.tostring(root, encoding='unicode'))

def gdf_extent_wkt(gdf):
    """Given a GeoPandas geodataframe, return a bounding extent polygon in WKT
    format

    Parameters
    ----------
    gdf : GeoDataFrame
        A GeoPandas geodataframe derived from a PostGIS database layer
    """
    # Get the extent and convert to a WKT polygon
    bounds = gdf.total_bounds
    poly = box(*bounds)

    return(poly.wkt)

def gdf_qmd_extentspatial_attrib(gdf):
    """Given a GeoPandas geodataframe, return a dictionary with extent/spatial
    attributes for a qmd file

    Parameters
    ----------
    gdf : GeoDataFrame
        A GeoPandas geodataframe derived from a PostGIS database layer
    """
    poly_wkt = gdf_extent_wkt(gdf)
    geom = ogr.CreateGeometryFromWkt(poly_wkt)
    env = geom.GetEnvelope() # minx, maxx, miny, maxy
    attribs = {'minx': str(env[0]),
               'maxx': str(env[1]),
               'miny': str(env[2]),
               'maxy': str(env[3]),
               'crs': 'EPSG:{0}'.format(gdf.crs.to_epsg()),
               'dimensions': '2',
               'minz': '0',
               'maxz': '0'
               }

    return(attribs)

def gdf_qmd_crs_editelement(gdf, crs_elem):
    """Given a GeoPandas geodataframe, return a dictionary with extent/spatial
    attributes for a qmd file

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        A GeoPandas geodataframe derived from a PostGIS database layer
    crs_elem : ElementTree.Element
        An ElementTree.Element containing coordinate reference system (crs)
        information formatted to qgis metadata format (iso 19319?)
    """
    crs_elem.find('spatialrefsys/wkt').text = gdf.crs.to_wkt()
    crs_elem.find('spatialrefsys/proj4').text = gdf.crs.to_proj4()
    crs_elem.find('spatialrefsys/srsid').text = None # not sure what this is
    crs_elem.find('spatialrefsys/srid').text = str(gdf.crs.to_epsg())
    crs_elem.find('spatialrefsys/authid').text = 'EPSG:{0}'.format(gdf.crs.to_epsg())
    crs_elem.find('spatialrefsys/description').text = gdf.crs.name
    # There isn't always a projection (coordinate_operation)
    if gdf.crs.coordinate_operation is not None:
        crs_elem.find('spatialrefsys/projectionacronym').text = gdf.crs.coordinate_operation.name
    else:
        crs_elem.find('spatialrefsys/projectionacronym').text = 'longlat'
    # This works for WGS84 UTM13N, not sure it always will
    ellac = gdf.crs.ellipsoid.to_json_dict()['id']['authority'] + ':' + str(gdf.crs.ellipsoid.to_json_dict()['id']['code'])
    crs_elem.find('spatialrefsys/ellipsoidacronym').text = ellac
    crs_elem.find('spatialrefsys/geographicflag').text = str(gdf.crs.is_geographic).lower()
    crs_elem.find('spatialrefsys').attrib =  {'nativeFormat': 'Wkt'}

    return(crs_elem)


def qmd_add_keywords(qmd, kws_elem):
    """Add a keywords element (<keywords>) or individual keywords <keyword> to
    a QGIS metadata root element

    The function uses the attribute of kws_elem to find a matching <keywords>
    list and appends new keywords to that list if available. If no matching
    <keywords> attribute is found, the entire kws_elem is appended to qmd after
    other <keywords> elements (which assumes they exist).

    Parameters
    ----------
    qmd : ElementTree.Element
        The root ET.Element for a parsed QGIS metadata file (~ISO 19319)
    kws_elem : ElementTree.Element
        An ElementTree.Element containing a list of keywords (<keywords>). This
        function expects an attribute in this element
    """
    # Get attribute of provided <keywords> element
    kws_elem_attrib = kws_elem.attrib
    # Find any matching <keywords> (same attrib) in qmd
    matching_kws_list = qmd.findall(".//keywords[@{0}='{1}']".format(
        next(iter(kws_elem_attrib.keys())),
        next(iter(kws_elem_attrib.values()))))
    # For a matching <keywords>, loop through, check if already present, and
    # if not, insert <keyword> as subelement
    if len(matching_kws_list) > 0:
        kws = matching_kws_list[0] #matching <keywords> in qmd
        kwlist = [k.text for k in list(kws.findall('keyword'))]
        for k in list(kws_elem.findall('keyword')):
            if k.text not in kwlist:
                kws.append(k)
    # If no match, just add the entire kws_elem as a subelement to root
    else:
        # Get the index of the last <keywords> element and add one
        lastkws_pos = list(qmd).index(qmd.findall("keywords")[-1]) + 1
        qmd.insert(lastkws_pos, kws_elem)


def qmd_add_links(qmd, links_elem):
    """Add a links element (<links>) or individual links <link> to
    a QGIS metadata root element

    The function tests the equivalence of each <link> element attribute dict 
    within the <links> parent element. If there is no match append the new
    link. If there is a match skip it. If no <links> list is found in qmd, 
    the entire links_elem is added is appended after the last of <title>,
    <abstract>, and <contact> elements (at least one must be present for this
    to work).

    Parameters
    ----------
    qmd : ElementTree.Element
        The root ET.Element for a parsed QGIS metadata file (~ISO 19319)
    links_elem : ElementTree.Element
        An ElementTree.Element containing a list of links (<links>). This
        function expects these to be full of attributes (no values)
    """
    # Find all links elements
    links_qmd = qmd.findall('links')
    if len(links_qmd) > 0: # if <links> present
        # Get the attribute dicts for all links
        qatt_dicts = [l.attrib for l in links_qmd]
        # Loop through <link> elements in dts_elem
        for l in list(links_elem.findall('link')):
            # Test equivalence of attributes and if none match append
            test_equiv = [l.attrib==qatt for qatt in qatt_dicts]
            if not any(test_equiv):
                links_qmd.append(l)
    # If no <links>, just add the entire links_elem as a subelement to root
    else:
        # Get the index of the last <contact> element and add one
        tag_order = [qroot.findall(tag)[0] for tag in ['title', 'abstract', 'contact']]
        links_elem_pos =  max([list(qmd).index(t) for t in tag_order]) + 1
        qmd.insert(links_elem_pos, links_elem)


def qmd_add_dates(qmd, dts_elem):
    """Add a dates element (<dates>) or individual dates <date> to
    a QGIS metadata root element

    The function uses the attribute of date elements within dts_elem to find
    matching <date> elements. If a match is present the date is updated with 
    the new value. If no matching <date> attribute is found, the new <date> is
    added to <dates>. If no <dates> list is found in qmd, the entire dts_elem
    is added is appended after the last of <contact>, <links>, and <history> 
    elements (at least one must be present for this to work).

    Parameters
    ----------
    qmd : ElementTree.Element
        The root ET.Element for a parsed QGIS metadata file (~ISO 19319)
    dts_elem : ElementTree.Element
        An ElementTree.Element containing a list of dates (<dates>). This
        function expects an attribute in this element
    """
    # Find all dates elements
    dts_qmd = qmd.findall('dates')
    if len(dts_qmd) > 0: # if <dates> present
        # Loop through <date> elements in dts_elem
        for d in list(dts_elem.findall('date')):
            # Find existing date elements with matching type attribute
            matching_d_qmd = qmd.findall(".//date[@{0}='{1}']".format(
                'type', d.attrib['type']))
            # If matching date type exists update the value, otherwise
            # append new <date> element
            if len(matching_d_qmd) > 0:
                matching_d_qmd.attrib['value'] = d.attrib['value']
            else:
                dts_qmd.append(d)
    # If no <dates>, just add the entire dts_elem as a subelement to root
    else:
        # Get the index of the last <history> element and add one
        tag_order = [qroot.findall(tag)[0] for tag in ['contact', 'links', 'history']]
        dts_elem_pos =  max([list(qmd).index(t) for t in tag_order]) + 1
        qmd.insert(dts_elem_pos, dts_elem)


def qmd_add_history(qmd, hist_elem):
    """Add a history element (<history>) to a QGIS metadata root element

    Parameters
    ----------
    qmd : ElementTree.Element
        The root ET.Element for a parsed QGIS metadata file (~ISO 19319)
    hist_elem : ElementTree.Element
        An ElementTree.Element containing a <history> element.
    """
    # Find all dates elements
    hist_qmd = qmd.findall('history')
    if len(hist_qmd) > 0: # if <history> present
        # Get the index of the last <history> element and add one
        lasthist_pos = list(qmd).index(qmd.findall("history")[-1]) + 1
        qmd.insert(lasthist_pos, hist_elem)
    else:
        # Get the index of the last <contact> or <links> element and add one
        tag_order = [qroot.findall(tag)[0] for tag in ['contact', 'links']]
        hist_elem_pos =  max([list(qmd).index(t) for t in tag_order]) + 1
        qmd.insert(hist_elem_pos, hist_elem)