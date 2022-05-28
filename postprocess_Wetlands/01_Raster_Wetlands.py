# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create wetland raster
# Author: Timm Nawrocki
# Last Updated: 2022-05-27
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create wetland raster" combines tiles into a wetland raster.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import predictions_to_raster

# Set round date
round_date = 'round_20220526'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')
segment_folder = os.path.join(project_folder, 'Data_Input/imagery/segments/gridded')
prediction_folder = os.path.join(project_folder, 'Data_Output/predicted_tables', round_date)
grid_folder = os.path.join(project_folder, 'Data_Output/predicted_rasters', round_date, 'wetlands')
output_folder = os.path.join(project_folder, 'Data_Output/output_rasters', round_date)

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')

# Define input datasets
alphabet_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea.tif')

# Define output raster
output_raster = os.path.join(output_folder, 'Chenega_Wetlands.tif')

# Define wetland dictionary
wetland_dictionary = {'D1': 1,
                      'FAB': 2,
                      'FUB': 3,
                      'I2AB': 4,
                      'I2EM': 5,
                      'I2RS': 6,
                      'I2US': 7,
                      'PEM': 8,
                      'PFOSS': 9,
                      'PML': 10,
                      'PRB': 11,
                      'PSS': 12,
                      'R': 13,
                      'UPL': 14
                      }

# Create key word arguments
kwargs_attributes = {'segment_folder': segment_folder,
                     'prediction_folder': prediction_folder,
                     'grid_folder': grid_folder,
                     'target_field': 'wetland',
                     'attribute_dictionary': wetland_dictionary,
                     'work_geodatabase': work_geodatabase,
                     'input_array': [alphabet_raster],
                     'output_array': [output_raster]
                     }

# Convert predictions to wetlands raster
print(f'Converting predictions to wetlands raster...')
arcpy_geoprocessing(predictions_to_raster, **kwargs_attributes)
print('----------')
