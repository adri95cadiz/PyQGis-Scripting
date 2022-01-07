from qgis.core import QgsProject
from qgis.utils import iface
import processing

root = QgsProject.instance().layerTreeRoot();

# Replace here name of the group to dissolve.
group = (root.findGroup("GROUP_NAME")); 

for child in group.children():
    layer = processing.run("native:dissolve", {'INPUT':child.name(),'FIELD':[],'OUTPUT':'memory:'})["OUTPUT"];
    layer.setName(child.name()+"_dissolved");
    QgsProject.instance().addMapLayer(layer);