from qgis.core import *

################################PARAMETERS#####################################
#
# NAME OF THE LAYER TO PROCESS:
input_layer_name = 'INPUT_LAYER_NAME';
# .SHP FILE WHERE THE RESULTS WILL BE STORED:
result_file = "Path/To/File";
# Parameter that will filter the layer initially
FILTER_PARAM = 'FILTER_PARAM';
# Value that the FILTER_PARAM will filter by
FILTER_VALUE = 'FILTER_VALUE';
# Parameter that the layer will be divided by
ITER_PARAM = 'ITER_PARAM';
# Parameter that will act as threshold to create the comparison layer
COMPARE_PARAM = 'COMPARE_PARAM';
# THRESHOLD VALUE TO COMPARE THE LAYERS:
MIN_VALUE = 1000;
#
###############################################################################

# We obtain the input_layer defined by input_layer_name
input_layer = QgsProject.instance().mapLayersByName(input_layer_name)[0];

###############################################################################

# FILTER BY: PARAM = VAL

###############################################################################

# Select rows which have PARAM equals VAL (PARAM = VAL)
selection_layer = processing.run('qgis:selectbyattribute',{'FIELD':FILTER_PARAM, 'INPUT':input_layer, 'METHOD':0, 'OPERATOR':0, 'VALUE':FILTER_VALUE})['OUTPUT'];

# Copy the selection to a temporary layer.
layer_selected = processing.run('qgis:saveselectedfeatures', {'INPUT':selection_layer, 'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT'];

# Iterate by CODES defined by ITER_PARAM.
index_list = selection_layer.fields().indexOf(ITER_PARAM);
codes = selection_layer.uniqueValues(index_list);

###############################################################################

array_layers_total = [];
array_layers_value = [];

# Para each code:
for code in codes:
    # Select rows which ITER_PARAM equals code.
    selection = processing.run('qgis:selectbyattribute',{'FIELD':'ITER_PARAM', 'INPUT':layer_selected, 'METHOD':0, 'OPERATOR':0, 'VALUE':code})['OUTPUT'];
    
    # Copy the selection to a temporary layer.
    selected = processing.run('qgis:saveselectedfeatures', {'INPUT':selection, 'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT'];
    
    # We dissolve the selected layer to create a new dissolved layer of the iterated parameter.
    layer_dissolve = processing.run("native:dissolve",{'INPUT':selected, 'FIELD':[], 'OUTPUT':'memory:'})['OUTPUT'];
    
    # We append the layer to the total array
    array_layers_total.append(layer_dissolve);
    
    # Calculate the total of value VAL_TOTAL.
    list_values = QgsVectorLayerUtils.getValues(selected, COMPARE_PARAM)[0];
    list_values = list(filter(None, list_values));
    total_value = sum(list_values);
    
    # If the total value is bigger than the min_value...
    if total_value >= MIN_VALUE:
        # We append the layer to the compare array
        array_layers_value.append(layer_dissolve);

# We merge the layers from all the total layers array
merge_total = processing.run("qgis:mergevectorlayers", {'LAYERS':array_layers_total,'CRS':'EPSG:25830','OUTPUT':'memory:'})['OUTPUT'];

# We store the layer in the project with a new name
merge_total.setName(input_layer + "_total_dissolved");
result = result_file + input_layer + "_total_dissolved.shp";
_writer = QgsVectorFileWriter.writeAsVectorFormat(merge_total,result,'UTF-8',merge_total.crs(),"ESRI Shapefile");
QgsProject.instance().addMapLayer(merge_total);

# We merge the layers from array where the value is bigger than the threshold
merge_value = processing.run("qgis:mergevectorlayers", {'LAYERS':array_layers_value,'CRS':'EPSG:25830','OUTPUT':'memory:'})['OUTPUT'];

# We store the layer in the project with a new name
merge_value.setName(input_layer + "_value_dissolved");
result = result_file + input_layer + "_value_dissolved.shp";
_writer = QgsVectorFileWriter.writeAsVectorFormat(merge_value,result,'UTF-8',merge_value.crs(),"ESRI Shapefile");
QgsProject.instance().addMapLayer(merge_value);
