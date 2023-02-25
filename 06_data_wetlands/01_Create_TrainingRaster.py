# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create training raster
# Author: Timm Nawrocki
# Last Updated: 2023-02-23
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
study_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea.tif')
class_feature = os.path.join(primary_geodatabase, 'chenega_training_polys_20230223')

# Define output datasets
class_raster = os.path.join(training_folder, 'Training_Wetlands.tif')

# Define fields
class_field = 'ATTRIBUTE'

# Define class values
class_values = {'E1AB1L': 1,
                'E1UB2L': 2,
                'E1UBL': 2,
                'E2AB1M': 3,
                'E2AB1N': 3,
                'E2EM1P': 4,
                'E2RS1N': 5,
                'E2RS1P': 5,
                'E2RS2N': 6,
                'E2US1N': 7,
                'E2US2M': 8,
                'E2US2N': 8,
                'L1UB3H': 9,
                'PAB3H': 10,
                'PEM1D': 11,
                'PEM1E': 12,
                'PFO4B': 13,
                'PRB1H': 14,
                'PSS4B': 15,
                'PUB3H': 16,
                'PUB4H': 17,
                'Alpine Dwarf Shrub/Herbaceous ': 18,
                'Alpine Dwarf Shrub/Lichen ': 19,
                'Alpine Herbaceous ': 20,
                'Alpine Sparse/Barren ': 21,
                'Anthropogenic': 22,
                'Barren Disturbed': 23,
                'Coastal Herbaceous ': 24,
                'Hemlock Forest': 25,
                'Hemlock Forest ': 25,
                'Hemlock-Sitka Spruce Forest ': 26,
                'Sitka Alder-Salmonberry Sideslope Shrubland ': 27,
                'Sitka Spruce Forest': 28,
                'Sitka Spruce Forest ': 28,
                'Sitka Willow-Barclay Willow Riparian Shrub ': 29,
                'Sitka Willow-Barclays Willow Riparian Shrub ': 29,
                'Subalpine Herbaceous Meadow ': 30,
                'Subalpine Mountain Hemlock Woodland': 31,
                'Subalpine Mountain Hemlock Woodland ': 31,
                'Subalpine Mountain Hemlock/Lichen Woodland': 32,
                'Subalpine Mountain Hemlock/Lichen Woodland ': 32}

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
