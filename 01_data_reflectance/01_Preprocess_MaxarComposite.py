# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Pre-process Maxar composite for segmentation
# Author: Timm Nawrocki
# Last Updated: 2022-01-03
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Pre-process Maxar composite for segmentation" reprojects and resamples multi-band image rasters to prepare for upload to Google Earth Engine for segmentation.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import datetime
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import composite_segmentation_imagery
import time

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')
tile_folder = os.path.join(project_folder, 'Data_Input/imagery/maxar/tiles')
composite_folder = os.path.join(project_folder, 'Data_Input/imagery/maxar/composite')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')

# Define input datasets
chenega_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea.tif')

# Define output datasets
imagery_composite = os.path.join(composite_folder, 'Chenega_MaxarComposite_WGS84.tif')
imagery_segmentation = os.path.join(composite_folder, 'Chenega_MaxarComposite_AKALB.tif')

# List imagery tiles
print('Searching for imagery tiles...')
# Start timing function
iteration_start = time.time()
# Set environment workspace to the folder containing the grid rasters
arcpy.env.workspace = tile_folder
# Create a raster list using the Arcpy List Rasters function
unprocessed_list = arcpy.ListRasters('*', 'TIF')
# Append file names to rasters in list
unprocessed_tiles = []
for raster in unprocessed_list:
    raster_path = os.path.join(tile_folder, raster)
    unprocessed_tiles.append(raster_path)
tiles_length = len(unprocessed_tiles)
print(f'Composite imagery will be created from {tiles_length} imagery tiles...')
# End timing
iteration_end = time.time()
iteration_elapsed = int(iteration_end - iteration_start)
iteration_success_time = datetime.datetime.now()
# Report success
print(f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
print('----------')

# Reset environment workspace
arcpy.env.workspace = work_geodatabase

#### CREATE AND RESAMPLE IMAGE COMPOSITE

# Create key word arguments
kwargs_composite = {'cell_size': 2,
                    'input_projection': 4326,
                    'output_projection': 3338,
                    'geographic_transformation': 'WGS_1984_(ITRF00)_To_NAD_1983',
                    'conversion_factor': 10,
                    'input_array': [chenega_raster] + unprocessed_tiles,
                    'output_array': [imagery_composite, imagery_segmentation]
                    }

# Merge rasters
print('Creating imagery composites...')
arcpy_geoprocessing(composite_segmentation_imagery, **kwargs_composite)
print('----------')
