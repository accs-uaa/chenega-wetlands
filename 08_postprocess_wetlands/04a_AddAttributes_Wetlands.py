# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Add attributes for wetlands
# Author: Timm Nawrocki
# Last Updated: 2023-02-24
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Add attributes for wetlands" adds attributes to the predicted raster.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import add_categorical_attributes

# Set round date
round_date = 'round_20230223'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')

# Define geodatabases
project_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')

# Define input datasets
study_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea.tif')
input_raster = os.path.join(project_folder, 'Data_Output/output_rasters',
                            round_date, 'Chenega_Wetlands.tif')

# Define output raster
output_raster = os.path.join(project_folder, 'Data_Output/output_rasters',
                             round_date, 'Chenega_Wetlands_Attributed.tif')

# Define surficial features dictionary
class_values = {'E1AB1L': 1,
                'E1UBL': 2,
                'E2AB1': 3,
                'E2EM1P': 4,
                'E2RS1': 5,
                'E2RS2': 6,
                'E2US1N': 7,
                'E2US2': 8,
                'L1UB3H': 9,
                'PAB3H': 10,
                'PEM1D': 11,
                'PEM1E': 12,
                'PFO4B': 13,
                'PRB1H': 14,
                'PSS4B': 15,
                'PUB3H': 16,
                'PUB4H': 17,
                'alpine dwarf shrub herbaceous': 18,
                'alpine dwarf shrub lichen': 19,
                'alpine herbaceous': 20,
                'alpine sparse/barren': 21,
                'anthropogenic': 22,
                'barren disturbed': 23,
                'coastal herbaceous': 24,
                'mountain hemlock': 25,
                'mountain hemlock - Sitka spruce': 26,
                'Sitka alder - salmonberry': 27,
                'Sitka spruce': 28,
                'Sitka Willow - Barclay Willow Riparian Shrub': 29,
                'subalpine herbaceous': 30,
                'subalpine mountain hemlock woodland': 31,
                'subalpine mountain hemlock - lichen woodland': 32}

# Create key word arguments
kwargs_attributes = {'attribute_dictionary': class_values,
                     'work_geodatabase': work_geodatabase,
                     'input_array': [study_raster, input_raster],
                     'output_array': [output_raster]
                     }

# Add attributes
print(f'Attributing raster...')
arcpy_geoprocessing(add_categorical_attributes, **kwargs_attributes)
print('----------')
