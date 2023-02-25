# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create training raster
# Author: Timm Nawrocki
# Last Updated: 2022-10-09
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create training raster" creates a raster of training data values from a set of manually delineated polygons representing different types for a classification.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import convert_class_data

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/EPA_Chenega'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Data')
training_folder = os.path.join(project_folder, 'Data_Input/training/processed')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')

# Define input datasets
chenega_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea.tif')
class_feature = os.path.join(work_geodatabase, 'Chenega_training_polys')

# Define output datasets
class_raster = os.path.join(training_folder, 'Chenega_Training.tif')

# Define fields
class_field = 'attribute'

# Define class values
class_values = {
    'E2AB1M': 1,
    'E2AB1N': 2,
    'E2AB3M': 3,
    'E2EM1M': 4,
    'E2EM1N': 5,
    'E2EM1P': 6,
    'E2RS1M': 7,
    'E2RS1N': 8,
    'E2RS1P': 9,
    'E2RS2N': 10,
    'E2RS2P': 11,
    'E2SB3M': 12,
    'E2SB4N': 13,
    'E2US1M': 14,
    'E2US1N': 15,
    'E2US1P': 16,
    'E2US2M': 17,
    'E2US2N': 18,
    'E2US2P': 19,
    'E2US3P': 20,
    'M1AB1L': 21,
    'M1L': 22,
    'M1RB2L': 23,
    'M1UB1L': 24,
    'M1UB2L': 25,
    'M1UBL': 26,
    'PAB3H': 27,
    'PEM1B': 28,
    'PEM1C': 29,
    'PFO4B': 30,
    'PRB1C': 31,
    'PRB1H': 32,
    'PSS4B': 33,
    'PUB1V': 34,
    'PUB3H': 35,
    'R1AB3M': 36,
    'R1RB2V': 37,
    'R1UB1Q': 38,
    'R1UB2Q': 39,
    'R1US2Q': 40,
    'UPL': 41
}

#### CREATE TRAINING RASTER

# Create key word arguments
kwargs_training = {'class_field': class_field,
                   'value_dictionary': class_values,
                   'work_geodatabase': work_geodatabase,
                   'input_array': [chenega_raster, class_feature],
                   'output_array': [class_raster]
                   }

# Convert polygon class data to raster
print(f'Converting polygon class data to raster...')
arcpy_geoprocessing(convert_class_data, **kwargs_training)
print('----------')
