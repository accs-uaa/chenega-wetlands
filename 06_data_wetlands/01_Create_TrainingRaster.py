# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create training raster
# Author: Timm Nawrocki
# Last Updated: 2023-06-11
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create training raster" creates a raster of training data values from a set of manually delineated polygons representing different types for a classification.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import convert_class_data

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')
training_folder = os.path.join(project_folder, 'Data_Input/training_data/processed')

# Define geodatabases
primary_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')

# Define input datasets
study_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea_1m_3338.tif')
class_feature = os.path.join(primary_geodatabase, 'chenega_training_polys_20230606')

# Define output datasets
class_raster = os.path.join(training_folder, 'Training_Wetlands.tif')

# Define fields
class_field = 'ATTRIBUTE'

# Define class values
class_values = {'E1AB1L': 1,
                'E1UBL': 2,
                'E2AB1M': 3,
                'E2AB1N': 4,
                'E2RS1N': 5,
                'E2RS1P': 5,
                'E2RS2N': 5,
                'E2US1N': 6,
                'PAB3H': 7,
                'PEM1D': 8,
                'PEM1E': 9,
                'PFO4B': 10,
                'PSS4B': 11,
                'L1UB3H': 12,
                'PUB3H': 12,
                'Alpine Dwarf Shrub/Herbaceous': 13,
                'Alpine Dwarf Shrub/Lichen': 13,
                'Alpine Sparse/Barren': 14,
                'Alpine Herbaceous': 15,
                'Subalpine Herbaceous Meadow': 15,
                'Barren Disturbed': 16,
                'Coastal Herbaceous': 17,
                'Hemlock Forest': 18,
                'Hemlock-Sitka Spruce Forest': 18,
                'Sitka Spruce Forest': 18,
                'Sitka Alder-Salmonberry Sideslope Shrubland': 19,
                'Sitka Willow-Barclay Willow Riparian Shrub': 20,
                'Subalpine Mountain Hemlock Woodland': 21,
                'Subalpine Mountain Hemlock/Lichen Woodland': 21}

#### CREATE TRAINING RASTER

# Create key word arguments
kwargs_training = {'class_field': class_field,
                   'value_dictionary': class_values,
                   'work_geodatabase': work_geodatabase,
                   'input_array': [study_raster, class_feature],
                   'output_array': [class_raster]
                   }

# Convert polygon class data to raster
print(f'Converting polygon class data to raster...')
arcpy_geoprocessing(convert_class_data, **kwargs_training)
print('----------')
