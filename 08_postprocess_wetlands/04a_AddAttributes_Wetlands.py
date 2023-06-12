# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Add attributes for wetlands
# Author: Timm Nawrocki
# Last Updated: 2023-06-12
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Add attributes for wetlands" adds attributes to the predicted raster.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import add_categorical_attributes

# Set round date
round_date = 'round_20230611'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')

# Define geodatabases
project_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')

# Define input datasets
study_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea_1m_3338.tif')
input_raster = os.path.join(project_folder, 'Data_Output/output_rasters',
                            round_date, 'Chenega_Wetlands_Raw.tif')

# Define output raster
output_raster = os.path.join(project_folder, 'Data_Output/output_rasters',
                             round_date, 'Chenega_Wetlands_Attributed.tif')

# Define surficial features dictionary
class_values = {'E1AB1L': 1,
                'E1UBL': 2,
                'E2AB1M': 3,
                'E2AB1N': 4,
                'E2RS1N': 5,
                'E2US1N': 6,
                'PAB3H': 7,
                'PEM1D': 8,
                'PEM1E': 9,
                'PFO4B': 10,
                'PSS4B': 11,
                'PUB3H': 12,
                'alpine dwarf shrub': 13,
                'apline sparse/barren': 14,
                'alpine-subalpine herbaceous': 15,
                'barren disturbed': 16,
                'coastal herbaceous': 17,
                'mountian hemlock - Sitka spruce': 18,
                'Sitka alder-salmonberry': 19,
                'riparian shrub': 20,
                'subalpine mountain hemlock woodland': 21}

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
