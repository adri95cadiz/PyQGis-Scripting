# PyQGis Scripting

Scripts developed for the automation of processes in the QGis platform

## dissolve_group

Lets you batch dissolve layers in PyQGis, just put the name of the group and execute the script.

## cut_raster_by_vector_and_process_data

Lets you cut an annual and a monthly raster layer of data with a parametrized vector layer which we can divide into fragments by a selection field parameter, then the extracted cuts mean (or any other statistic), is calculated and it is all composed into a attribute table inside an .shp file which can then be exported into xlsx or any other datasheet format.

### PARAMETERS 

NAME OF THE LAYER TO PROCESS CUTS:
vector_layer = 'NAME_OF_VECTOR_LAYER';

NAME OF THE PARAMETER TO SEPARATE THE PROCESS LAYER WITH:
cut_param = 'SELECT_FROM_LAYER_PARAMETER';

URL OF THE .SHP FILE WHERE THE RESULTS WILL BE STORED:
result_file = 'C:/Path/to/Folder/Results_'+vector_layer+'.shp'

MINIMUM SUM VALUE TO TAKE ELEMENT INTO ACCOUNT:
min_value = 1000;

PARAMETER THAT WILL BE TESTED FOR ELEMENT SELECTION:
value_param = 'VALUE_PARAM';

NAME OF THE ANNUAL RASTER LAYER WE WILL EXTRACT THE DATA FROM:
annual_raster = 'ANNUAL_RASTER_LAYER_NAME';

NAME OF THE MONTHLY RASTER GROUP WE WILL EXTRACT THE DATA FROM:
monthly_group = 'MONTHLY_RASTER_GROUP_NAME';

## split_merge_and_compare

Let's you create two layers based on the input_layer, each layer will be filtered by the parameter FILTER_PARAM = FILTER_VAL which you can redefine to any parameter to any value or just skip this step, later the layer will be split by the parameter ITER_PARAM which you can also redefine, and each section will be dissolved to create a homogeneous layer. Later they will merge in two layers, one with all the dissolved sections, and another which will only have the sections where the sum of VAL_TOTAL is bigger than min_value.

### PARAMETERS
