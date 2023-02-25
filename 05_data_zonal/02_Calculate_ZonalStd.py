# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate zonal standard deviations
# Author: Timm Nawrocki
# Last Updated: 2023-02-23
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate zonal standard deviations" calculates zonal standard deviations of input datasets to segments defined in a raster.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import calculate_zonal_statistics

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')
grid_folder = os.path.join(project_folder, 'Data_Input/imagery/segments/gridded')
composite_folder = os.path.join(project_folder, 'Data_Input/imagery/maxar/composite')
processed_folder = os.path.join(project_folder, 'Data_Input/imagery/maxar/processed')
zonal_folder = os.path.join(project_folder, 'Data_Input/zonal')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')

# Define grids
grid_list = ['A1', 'A2',
             'B1', 'B2', 'B3',
             'C1', 'C2', 'C3',
             'D1', 'D2', 'D3']

# Create input raster list
blue_raster = os.path.join(composite_folder, 'Chenega_MaxarComposite_WGS84.tif/Band_1')
green_raster = os.path.join(composite_folder, 'Chenega_MaxarComposite_WGS84.tif/Band_2')
red_raster = os.path.join(composite_folder, 'Chenega_MaxarComposite_WGS84.tif/Band_3')
nearir_raster = os.path.join(composite_folder, 'Chenega_MaxarComposite_WGS84.tif/Band_4')
evi2_raster = os.path.join(processed_folder, 'Chenega_Maxar_EVI2.tif')
ndvi_raster = os.path.join(processed_folder, 'Chenega_Maxar_NDVI.tif')
ndwi_raster = os.path.join(processed_folder, 'Chenega_Maxar_NDWI.tif')
input_rasters = [blue_raster, green_raster, red_raster, nearir_raster,
                 evi2_raster, ndvi_raster, ndwi_raster]

# Create output raster list
output_rasters = ['Chenega_Maxar_01_Blue',
                  'Chenega_Maxar_02_Green',
                  'Chenega_Maxar_03_Red',
                  'Chenega_Maxar_04_nearir',
                  'Chenega_Maxar_EVI2',
                  'Chenega_Maxar_NDVI',
                  'Chenega_Maxar_NDWI']

# Loop through each grid in grid list and produce zonal summaries
for grid in grid_list:
    print(f'Creating zonal summaries for grid {grid}...')

    # Define input datasets
    grid_raster = os.path.join(grid_folder, grid + '.tif')

    # Create zonal summary for each raster in input list
    count = 1
    raster_length = len(input_rasters)
    for input_raster in input_rasters:
        # Create output folder
        output_folder = os.path.join(zonal_folder, grid)

        # Make grid folder if it does not already exist
        if os.path.exists(output_folder) == 0:
            os.mkdir(output_folder)

        # Define output raster
        raster_name = output_rasters[count-1]
        output_raster = os.path.join(output_folder, raster_name + '_STD.tif')

        # Create zonal summary if output raster does not already exist
        if arcpy.Exists(output_raster) == 0:
            # Create key word arguments
            kwargs_zonal = {'statistic': 'STD',
                            'zone_field': 'VALUE',
                            'work_geodatabase': work_geodatabase,
                            'input_array': [grid_raster, input_raster],
                            'output_array': [output_raster]
                            }

            # Process the zonal summaries
            print(f'\tProcessing zonal summary {count} of {raster_length}...')
            arcpy_geoprocessing(calculate_zonal_statistics, **kwargs_zonal)
            print('\t----------')

        # If raster already exists, print message
        else:
            print(f'\tZonal summary {count} of {raster_length} already exists.')
            print('\t----------')

        # Increase counter
        count += 1

    # Report success at end of loop
    print(f'Finished zonal summaries for {grid}.')
