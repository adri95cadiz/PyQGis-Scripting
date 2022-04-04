from qgis.core import *

############################PARAMETERS##############################
#
# NAME OF THE LAYER TO PROCESS CUTS:
vector_layer = 'NAME_OF_VECTOR_LAYER';
#
# NAME OF THE PARAMETER TO SEPARATE THE PROCESS LAYER WITH:
cut_param = 'SELECT_FROM_LAYER_PARAMETER';
#
# URL OF THE .SHP FILE WHERE THE RESULTS WILL BE STORED:
result_file = 'C:/Path/to/Folder/Results_'+vector_layer+'.shp'
#
# MINIMUM SUM VALUE TO TAKE ELEMENT INTO ACCOUNT:
min_value = 1000;
#
# PARAMETER THAT WILL BE TESTED FOR ELEMENT SELECTION:
value_param = 'VALUE_PARAM';
#
# NAME OF THE ANNUAL RASTER LAYER WE WILL EXTRACT THE DATA FROM.
annual_raster = 'ANNUAL_RASTER_LAYER_NAME';
#
# NAME OF THE MONTHLY RASTER GROUP WE WILL EXTRACT THE DATA FROM.
monthly_group = 'MONTHLY_RASTER_GROUP_NAME';
#
#####################################################################

# Create the data structure for the data we are going to fill
layerFields = QgsFields();
layerFields.append(QgsField(cut_param, QVariant.Int));
layerFields.append(QgsField(value_param, QVariant.Double));
layerFields.append(QgsField('MONTH', QVariant.Int));
layerFields.append(QgsField('ANNUAL_DATA', QVariant.Double));
layerFields.append(QgsField('MONTHLY_DATA', QVariant.Double));

# Create the writer to append the table data.
writer = QgsVectorFileWriter(result_file, 'UTF-8', layerFields, QgsWkbTypes.Point, QgsCoordinateReferenceSystem('EPSG:26912'), 'ESRI Shapefile');

# Obtain the vector layer for the data to be analyzed.
input_layer = QgsProject.instance().mapLayersByName(vector_layer)[0];

# Recover the values of the cut parameter.
index_cut = input_layer.fields().indexOf(cut_param);
cut_codes = input_layer.uniqueValues(index_cut);

# For each cut:
for cut_id in cut_codes:
    # Select the rows which value matches the selection parameter (cut_param).
    selection = processing.run('qgis:selectbyattribute',{'FIELD':cut_param, 'INPUT':input_layer, 'METHOD':0, 'OPERATOR':0, 'VALUE':cut_id})['OUTPUT'];

    # Copy the selection to a new temporary layer.
    cut_layer = processing.run('qgis:saveselectedfeatures', {'INPUT':selection, 'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT'];

    # Calculate the total value of the sum value of the processing.
    list_values = QgsVectorLayerUtils.getValues(cut_layer, value_param)[0];
    list_values = list(filter(None, list_values));
    # I have selected to base the condition on the sum of values but this can be changed too.
    total_value = sum(list_values); 

    # If the total value of the cut layer is bigger than the minimum stablished value...
    if total_value > min_value:
        # Process the layer:
        
        ###############ANNUAL_DATA###############

        # Cut the annual raster layer.
        annual_layer = QgsProject.instance().mapLayersByName(annual_raster)[0];
        parameters = {
        'ALPHA_BAND': False,
        'CROP_TO_CUTLINE': True,
        'DATA_TYPE': 0,
        'INPUT': annual_layer,
        'KEEP_RESOLUTION': True,
        'MASK': cut_layer,
        'MULTITHREADING': True,
        'SOURCE_CRS': cut_layer.crs(),
        'TARGET_CRS': cut_layer.crs(),
        'OUTPUT' : 'TEMPORARY_OUTPUT',
        };
        clip_output = processing.run("gdal:cliprasterbymasklayer", parameters)['OUTPUT'];
        annual_result = QgsRasterLayer(clip_output, "clipped", 'gdal');
        # Calculate the statistics of the cut made to the raster layer.
        annual_data = processing.run("native:rasterlayerstatistics",{'BAND':1, 'INPUT':annual_result, 'OUTPUT':'TEMPORARY_OUTPUT'});

        # Add the data to the table. 
        feature = QgsFeature();
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(cut_id, 0)));
        # I have selected to get the mean value of the extracted data but you can choose any statistic.
        feature.setAttributes([cut_id, total_value, 0, annual_data['MEAN'], NULL]); 
        writer.addFeature(feature);

        ###############MONTHLY_DATA###############

        # Obtain the root of the project.
        root = QgsProject.instance().layerTreeRoot();

        # Obtain the monthly layers from the root.
        monthly_layers = (root.findGroup(monthly_group));
           
        # For each month in the group:
        for month in range(12): 
            # Cut the layer corresponding to the iterated month.
            monthly_layer = QgsProject.instance().mapLayersByName(monthly_layers.children()[month].name())[0];
            parameters = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,
            'INPUT': cut_layer,
            'KEEP_RESOLUTION': True,
            'MASK': municipio,
            'MULTITHREADING': True,
            'SOURCE_CRS': cut_layer.crs(),
            'TARGET_CRS': cut_layer.crs(),
            'OUTPUT' : 'TEMPORARY_OUTPUT',
            };
            clip_output = processing.run("gdal:cliprasterbymasklayer", parameters)['OUTPUT'];
            monthly_result = QgsRasterLayer(clip_output, "clipped", 'gdal');
            
            # Calculate the statistics of the obtained monthly cut.
            monthly_data = processing.run("native:rasterlayerstatistics",{'BAND':1, 'INPUT':monthly_result, 'OUTPUT':'TEMPORARY_OUTPUT'});

            # Add the results to the table. 
            feature = QgsFeature();
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(cut_id, month)));
            # I have selected to get the mean value of the extracted data but you can choose any statistic.
            feature.setAttributes([cut_id, total_value, month+1, NULL, monthly_data['MEAN']]);
            writer.addFeature(feature);
            
            # Iterate the month.
            month += 1;  

        ##########################################

# Save the obtained results to a layer and add to the project.
results = iface.addVectorLayer(result_file, "Results_" + vector_layer, "ogr");
QgsProject.instance().addMapLayer(results);
del(writer);
