# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate zonal means
# Author: Timm Nawrocki
# Last Updated: 2023-02-24
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate zonal means" calculates zonal means of input datasets to segments defined in a raster.
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
topography_folder = os.path.join(project_folder, 'Data_Input/topography/integer')
sent1_folder = os.path.join(project_folder, 'Data_Input/imagery/sentinel-1/unprocessed')
sent2_folder = os.path.join(project_folder, 'Data_Input/imagery/sentinel-2/processed')
coastal_folder = os.path.join(project_folder, 'Data_Input/coastline/processed')
zonal_folder = os.path.join(project_folder, 'Data_Input/zonal')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')

# Define grids
grid_list = ['A1', 'A2',
             'B1', 'B2', 'B3',
             'C1', 'C2', 'C3',
             'D1', 'D2', 'D3']

# Create empty raster list
input_rasters = []

# Create list of topography rasters
arcpy.env.workspace = topography_folder
topography_rasters = arcpy.ListRasters('*', 'TIF')
for raster in topography_rasters:
    raster_path = os.path.join(topography_folder, raster)
    input_rasters.append(raster_path)

# Create list of Sentinel-1 rasters
arcpy.env.workspace = sent1_folder
sent1_rasters = arcpy.ListRasters('*', 'TIF')
for raster in sent1_rasters:
    raster_path = os.path.join(sent1_folder, raster)
    input_rasters.append(raster_path)

# Create list of Sentinel-2 rasters
arcpy.env.workspace = sent2_folder
sent2_rasters = arcpy.ListRasters('*', 'TIF')
for raster in sent2_rasters:
    raster_path = os.path.join(sent2_folder, raster)
    input_rasters.append(raster_path)

# Create list of coastal rasters
arcpy.env.workspace = coastal_folder
coastal_rasters = arcpy.ListRasters('*', 'TIF')
for raster in coastal_rasters:
    raster_path = os.path.join(coastal_folder, raster)
    input_rasters.append(raster_path)

# Set workspace to default
arcpy.env.workspace = work_geodatabase

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
        raster_name = os.path.split(input_raster)[1]
        output_raster = os.path.join(output_folder, raster_name)

        # Create zonal summary if output raster does not already exist
        if arcpy.Exists(output_raster) == 0:
            # Create key word arguments
            kwargs_zonal = {'statistic': 'MEAN',
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
