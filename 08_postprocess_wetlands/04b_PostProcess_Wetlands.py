# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process wetlands
# Author: Timm Nawrocki
# Last Updated: 2023-02-23
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process wetlands" processes the predicted raster into the final deliverable.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import postprocess_categorical_raster

# Set round date
round_date = 'round_20230223'
version_number = 'v0_1'

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
                            round_date, 'Chenega_Wetlands_Raw.tif')
segments_feature = os.path.join(project_geodatabase, 'Chenega_Segments_Original_Polygon')

# Define output raster
output_raster = os.path.join(project_folder, 'Data_Output/output_rasters',
                             round_date, 'Chenega_Wetlands_Smoothed.tif')

# Define surficial features dictionary
class_values = {'E1AB1L': 1,
                'E1UBL': 2,
                'E2AB1': 3,
                'E2EM1P': 4,
                'E2RS': 5,
                'E2US': 6,
                'PAB3H': 7,
                'PEM1D': 8,
                'PEM1E': 9,
                'PFO4B': 10,
                'PSS4B': 11,
                'PUB': 12,
                'alpine dwarf shrub': 13,
                'alpine sparse/barren': 14,
                'alpine-subalpine herbaceous': 15,
                'barren disturbed': 16,
                'coastal herbaceous': 17,
                'mountain hemlock - Sitka spruce': 18,
                'Sitka alder - salmonberry': 19,
                'Sitka Willow - Barclay Willow Riparian Shrub': 20,
                'subalpine mountain hemlock woodland': 21}

# Create key word arguments
kwargs_process = {'minimum_count': 505,
                  'attribute_dictionary': class_values,
                  'work_geodatabase': work_geodatabase,
                  'input_array': [study_raster, input_raster, segments_feature],
                  'output_array': [output_raster]
                  }

# Post-process wetlands raster
print(f'Post-processing wetlands raster...')
arcpy_geoprocessing(postprocess_categorical_raster, **kwargs_process)
print('----------')
