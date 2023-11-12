"""
This is to pull existing metadata from a Jornada File Geodatabase (gdb)
and create a qmd file
"""

from qgis.core import *
from qgis.utils import *
import glob
import os

# Which geodatabase and path to extract metadata from
gdb_name = "All_studies_JornadaGDB.gdb"
gdb_path = "/home/greg/data/rawdata/JornadaGIS_copies/"

# Directory for raw shapefile metadata exports
md_raw_dir = '/home/greg/data/rawdata/JornadaGeospatial/tmp/'
md_raw_dir = '/home/greg/data/rawdata/JornadaGeospatial/tmp/'

# Directory for final qmds
md_dir = '/home/greg/data/rawdata/JornadaGeospatial/md/' + gdb_name + '_qmd/'
os.mkdir(md_dir)

# Some options for how to export the metadta (we're exporting
# shapefiles to a temp directory, then  moving just the exported qmds)
save_options = QgsVectorFileWriter.SaveVectorOptions()
save_options.driverName = 'ESRI Shapefile'
save_options.fileEncoding = 'UTF-8'
save_options.saveMetadata = True

# Open the geodatabase and then get a list of sub layers withing it
gdb = QgsVectorLayer(gdb_path + gdb_name,"test","ogr")
subLayers =gdb.dataProvider().subLayers()

# Loop through list of sublayers and read the metadata
for subLayer in subLayers:
    # First get the layer name and create the identifier
    name = subLayer.split('!!::!!')[1]
    uri = "{0}|layername={1}".format(gdb_path + gdb_name, name,)
    # Read in the layer and check if valid
    sub_vlayer = QgsVectorLayer(uri, name, 'ogr')
    if not sub_vlayer.isValid():
        print("Layer failed to load!")
    # Add layer to map
    #QgsProject.instance().addMapLayer(sub_vlayer)
    
    # Take the length of some important metadta elements
    abstractlen = len(sub_vlayer.metadata().abstract())
    keywordlen = len(sub_vlayer.metadata().keywords())
    contactlen = len(sub_vlayer.metadata().contacts())
    rightslen = len(sub_vlayer.metadata().rights())
    licenselen = len(sub_vlayer.metadata().licenses())
    historylen = len(sub_vlayer.metadata().history())
    lentup = (abstractlen, keywordlen, contactlen, rightslen, licenselen, historylen)
    print(max(lentup))
    # If there is important metadata (len > 0), export the shapfile (with a
    # qmd file)
    if max(lentup) > 0:
        save_options.layerMetadata = sub_vlayer.metadata()
        QgsVectorFileWriter.writeAsVectorFormat( sub_vlayer,
        md_raw_dir + sub_vlayer.name() + '.shp',
        save_options)
# Now move all the qmd files to the "finished" metadata directory        
qmd_files = glob.glob(md_raw_dir +'*.qmd')
for f in qmd_files:
    os.rename(f, f.replace(md_raw_dir, md_dir))
# Now remove the files in the raw (tmp) directory
for f in os.listdir(md_raw_dir):
    os.remove(os.path.join(md_raw_dir, f))

