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