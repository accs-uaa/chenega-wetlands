# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create training raster
# Author: Timm Nawrocki
# Last Updated: 2022-10-03
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
    'L1UB3H': 21,
    'L2UB3H': 22,
    'M1AB1L': 23,
    'M1L': 24,
    'M1RB2L': 25,
    'M1UB1L': 26,
    'M1UB2L': 27,
    'M1UBL': 28,
    'M2RS1P': 29,
    'PAB3F': 30,
    'PAB3H': 31,
    'PEM1A': 32,
    'PEM1B': 33,
    'PEM1C': 34,
    'PEM1E': 35,
    'PEM1F': 36,
    'PEM1S': 37,
    'PFO4B': 38,
    'PRB1A': 39,
    'PRB1F': 40,
    'PRB1H': 41,
    'PSS1B': 42,
    'PSS1C': 43,
    'PSS1S': 44,
    'PSS4B': 45,
    'PUB1V': 46,
    'PUB3H': 47,
    'PUB4F': 48,
    'PUB4H': 49,
    'PUBH': 50,
    'R1AB3M': 51,
    'R1RB2V': 52,
    'R1UB1Q': 53,
    'R1UB2Q': 54,
    'R1US2Q': 55,
    'R2UB1H': 56,
    'R2UB3H': 57,
    'R3UB1F': 58,
    'R3UB1H': 59,
    'R3US1A': 60,
    'R3US1F': 61,
    'R4SB2A': 62,
    'UPL': 63
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
