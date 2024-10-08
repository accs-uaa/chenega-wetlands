# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process image segments
# Author: Timm Nawrocki
# Last Updated: 2022-03-22
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process image segments" converts the segment output from Google Earth Engine to a standard format raster, polygon, and point set.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import datetime
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import merge_segmentation_imagery
from package_GeospatialProcessing import postprocess_segments
import time

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')
unprocessed_folder = os.path.join(project_folder, 'Data_Input/imagery/segments/unprocessed')
processed_folder = os.path.join(project_folder, 'Data_Input/imagery/segments/processed')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')

# Define input datasets
chenega_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea.tif')

# Define output datasets
segments_merge = os.path.join(processed_folder, 'Chenega_Segments_Merge.tif')
segments_original = os.path.join(processed_folder, 'Chenega_Segments_Original.tif')
segments_polygon = os.path.join(work_geodatabase, 'Chenega_Segments_Original_Polygon')
segments_point = os.path.join(work_geodatabase, 'Chenega_Segments_Original_Point')

# List segment tiles
print('Searching for segment tiles...')
# Start timing function
iteration_start = time.time()
# Set environment workspace to the folder containing the grid rasters
arcpy.env.workspace = unprocessed_folder
# Create a raster list using the Arcpy List Rasters function
unprocessed_list = arcpy.ListRasters('*', 'TIF')
# Append file names to rasters in list
unprocessed_tiles = []
for raster in unprocessed_list:
    raster_path = os.path.join(unprocessed_folder, raster)
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

#### MERGE IMAGE SEGMENT TILES

# Create key word arguments
kwargs_merge = {'input_projection': 3338,
                'work_geodatabase': work_geodatabase,
                'input_array': [chenega_raster] + unprocessed_tiles,
                'output_array': [segments_merge]
                }

print('Merging image segments...')
arcpy_geoprocessing(merge_segmentation_imagery, **kwargs_merge)
print('----------')

#### POST-PROCESS IMAGE SEGMENTS

# Create key word arguments
kwargs_process = {'cell_size': 1, 'work_geodatabase': work_geodatabase,
                  'input_array': [chenega_raster, segments_merge],
                  'output_array': [segments_original, segments_polygon, segments_point]}

# Post-process segments
print('Post-processing image segments...')
arcpy_geoprocessing(postprocess_segments, **kwargs_process)
print('----------')
