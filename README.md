# jgeo_utils

Utilities for the Jornada Geospatial database (jgeo) and related services.

* A python package called `jgeo_py` for managing geopackages, metadata, ArcGIS
feature services, and maps.
* Some jupyter notebooks for interacting with ArcGIS online and the jgeo PostGIS
database.
* QGIS scripts
* Various logs and other records.

All of this is for working with a the geospatial data resources below.

1. The jgeo PostGIS database hosted (for now) on the termite server (at Wooton
Hall)
2.  The ESRI file geodatabases created and maintained by the Jornada GIS group 
(Scott Schrader, Andrea Ernst, Amy Slaughter, et al)
3. ArcGIS featureLayerCollections derived from the data sources above
and hosted in NMSU's ArcGIS Online system (NMSU AGOL, https://nmsu.maps.arcgis.com)
4. ArcGIS web maps and applications hosted on NMSU AGOL and mirrored
on the Jornada LTER website (in development...)

## Contents of this repository

* **jgeo_py/** is a basic python package for working with geopackages and
ArcGIS online (AGOL)
* **notebooks/** contains a bunch of jupyter notebooks - these are the main
source of code for making geopackages and populating jgeo.
* **qgis_scripts/** has a few scripts using the pyQGIS api to extract things
from geospatial layers.

If you want to use the scripts and notebooks you may need to create a
`jgeo_cred.py` and an `nmsu_agol_cred.py` files with your credentials for
these resources.

## jgeo and other resources

* **jrn_studies_gpkg/** is a collection of geopackages corresponding to named
Jornada studies (prj001, prj002, etc) and holding known geospatial layers for
those projects. 
* **logs/** has the various logs created in the process of populating the jgeo
database
* **metadata/** is a collection of metadata files in the `.qmd` format (QGIS).
This includes those extracted from JornadaGIS file geodatabases, and newer 
metadata created by the IM team.
* **qgis_projects/** has a few QGIS project files
* **requests/** contains a few requested data files
* **thematic_gpkgs/** has a few "thematic" geopackages with metadata. These are
being tranfered to jgeo soon.
* **tmp/** empty (usually) temporary directory

## Some notes

The reference geopackages were derived from ArcGIS file geodatabases managed
by the USDA Jornada GIS team (Scott Schrader et al) and from layers in the 
Jornada mobile app (contact Dylan Burruss). The AGOL hosted feature services
were then derived from these reference geopackages and uploaded to NMSU AGOL
using the ArcGIS python API in early 2022.

At some point they'll need to be updated to follow spatial data QA/QC, so naming
of all JornadaGeospatial layers is being preserved to match the source layers. 

Updating the NMSU AGOL layers will probably need to be done non-destructively.
That is, metadata and feature service settings on NMSU AGOL should be preserved
if possible.

## Links and stuff

* [ArcGIS Python API documentation](https://developers.arcgis.com/python/api-reference/index.html)
* [GeoPandas](https://geopandas.org/en/stable/docs/user_guide.html) is a useful complement to ArcGIS python API, and there are ways to upload geodataframes to AGOL hosted feature services (though maybe buggy) using the [GeoAccessor](https://developers.arcgis.com/python/api-reference/arcgis.features.toc.html#geoaccessor).
* [Info about AGOL Feature Services](https://developers.arcgis.com/rest/services-reference/enterprise/feature-service.htm)
* [A tutorial](https://community.esri.com/t5/geodev-germany-blog/publish-multiple-layers-in-one-feature-service-on/ba-p/888883) on publishing multiple layers to a featureLayerCollection
* See [this question/answer](https://community.esri.com/t5/arcgis-api-for-python-questions/overwriting-geojson-based-hosted-feature-service/td-p/808579) for a way to update AGOL hosted feature layers using GeoJSON files.
* Publishing feature services and layers on AGOL using the python API is complex and requires setting lots of options using python dicts or json formats. More [here](https://gis.stackexchange.com/questions/349706/publish-file-geodatabase-to-arcgis-online-using-arcgis-api-for-python) and [here](https://developers.arcgis.com/rest/services-reference/enterprise/feature-service.htm).
* [Another tutorial](https://www.esri.com/arcgis-blog/products/arcgis-online/data-management/keeping-layers-updated-by-appending-features-using-the-arcgis-api-for-python/) for adding features to an AGOL feature service.
