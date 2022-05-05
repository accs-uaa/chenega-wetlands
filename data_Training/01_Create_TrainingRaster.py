# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create training raster
# Author: Timm Nawrocki
# Last Updated: 2022-03-24
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create training raster" creates a raster of training data values from a set of manually delineated polygons representing different types for a classification.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import convert_class_data

# Set root directory
drive = 'M:/'
root_folder = 'EPA_Chenega'

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
    'E1AB1L': 1,
    'E1UB1L': 2,
    'E1UB2L': 3,
    'E2AB1M': 4,
    'E2AB1N': 5,
    'E2EM1M': 6,
    'E2EM1N': 7,
    'E2EM1P': 8,
    'E2RS1P': 9,
    'E2SB3M': 10,
    'E2SB4N': 11,
    'E2SS4P': 12,
    'E2UB2M': 13,
    'E2US1M': 14,
    'E2US1N': 15,
    'E2US2M': 16,
    'E2US2N': 17,
    'E2US3P': 18,
    'L1AB3H': 19,
    'L1UB3H': 20,
    'L1UB3L': 21,
    'L2AB3H': 22,
    'L2RS2': 23,
    'L2UB3H': 24,
    'L2US3H': 25,
    'L2USH': 26,
    'M1AB1L': 27,
    'M1L': 28,
    'M1RB2L': 29,
    'M1UB1L': 30,
    'M1UB2L': 31,
    'M1UBL': 32,
    'M1US2N': 33,
    'M2AB1M': 34,
    'M2AB1N': 35,
    'M2RS1M': 36,
    'M2RS1N': 37,
    'M2RS1P': 38,
    'M2RS2N': 39,
    'M2RS2P': 40,
    'M2UB2M': 41,
    'M2US 1N': 42,
    'M2US1B': 43,
    'M2US1M': 44,
    'M2US1N': 45,
    'M2US1P': 46,
    'M2US2M': 47,
    'M2US2N': 48,
    'M2US2P': 49,
    'PAB3H': 50,
    'PEM1A': 51,
    'PEM1B': 52,
    'PEM1C': 53,
    'PEM1E': 54,
    'PEM1F': 55,
    'PEM1S': 56,
    'PFO4B': 57,
    'PML1B': 58,
    'PML1D': 59,
    'PRB1F': 60,
    'PRB1H': 61,
    'PSS1B': 62,
    'PSS1C': 63,
    'PSS1S': 64,
    'PSS4B': 65,
    'PUB1V': 66,
    'PUB3H': 67,
    'PUB4F': 68,
    'PUB4H': 69,
    'PUBH': 70,
    'R1UB1Q': 71,
    'R1UB2Q': 72,
    'R1US2Q': 73,
    'R2UB1H': 74,
    'R2UB3H': 75,
    'R3UB1F': 76,
    'R3UB2H': 77,
    'R3US1A': 78,
    'R4SB2A': 79,
    'UPL': 80
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
