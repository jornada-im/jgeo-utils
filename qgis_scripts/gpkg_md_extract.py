from qgis.core import *
from qgis.utils import *

save_options = QgsVectorFileWriter.SaveVectorOptions()

save_options.driverName = 'ESRI Shapefile'
save_options.fileEncoding = 'UTF-8'
save_options.saveMetadata = True
transform_context = QgsProject.instance().transformContext()

for vLayer in iface.mapCanvas().layers():
    print(vLayer.name())
    save_options.layerMetadata = vLayer.metadata()
    QgsVectorFileWriter.writeAsVectorFormat( vLayer,
        '/home/greg/data/rawdata/JornadaGeospatial/tmp/' + vLayer.name() + '.shp',
        save_options)
        

