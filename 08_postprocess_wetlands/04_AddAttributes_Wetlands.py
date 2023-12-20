# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Add attributes for wetlands
# Author: Timm Nawrocki
# Last Updated: 2023-12-17
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Add attributes for wetlands" adds attributes to the predicted raster.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import add_categorical_attributes

# Set round date
round_date = 'round_20231217'

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')

# Define geodatabases
project_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')

# Define input datasets
area_input = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea_1m_3338.tif')
wetlands_input = os.path.join(project_folder, 'Data_Output/output_rasters',
                              round_date, 'Chenega_Wetlands_Raw.tif')

# Define output raster
wetlands_output = os.path.join(project_folder, 'Data_Output/output_rasters',
                               round_date, 'Chenega_Wetlands_Attributed.tif')

# Define wetlands dictionary
wetlands_dictionary = {1: 'M1AB1L',
                       2: 'M1UBL',
                       3: 'M2AB1M',
                       4: 'M2AB1N',
                       5: 'M2RS1N',
                       6: 'M2RS1N',
                       7: 'PAB3H',
                       8: 'PEM1D',
                       9: 'PEM1E',
                       10: 'PFO4B',
                       11: 'PSS4B',
                       12: 'PUB3H',
                       13: 'alpine dwarf shrub',
                       14: 'alpine sparse/barren',
                       15: 'alpine-subalpine herbaceous',
                       16: 'barren disturbed',
                       17: 'coastal herbaceous',
                       18: 'mountain hemlock - Sitka spruce',
                       19: 'Sitka alder-salmonberry',
                       20: 'riparian shrub',
                       21: 'subalpine mountain hemlock woodland'}

# Create key word arguments
kwargs_attributes = {'attribute_dictionary': wetlands_dictionary,
                     'work_geodatabase': work_geodatabase,
                     'input_array': [area_input, wetlands_input],
                     'output_array': [wetlands_output]
                     }

# Add attributes
print(f'Adding raster attributes...')
arcpy_geoprocessing(add_categorical_attributes, **kwargs_attributes)
print('----------')
