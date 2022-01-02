# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process image segments
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process image segments" converts the segment output from Google Earth Engine to a standard format raster, polygon, and point set.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import postprocess_segments

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')
segments_folder = os.path.join(project_folder, 'Data_Input/imagery/segments')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')

# Define input datasets
chenega_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea.tif')
segments_initial = os.path.join(segments_folder, 'Chenega_Segments_Initial.tif')

# Define output datasets
segments_final = os.path.join(segments_folder, 'Chenega_Segments_Final.tif')
segments_polygon = os.path.join(work_geodatabase, 'Chenega_Segments_Polygon')
segments_point = os.path.join(work_geodatabase, 'Chenega_Segments_Point')

#### POST-PROCESS IMAGE SEGMENTS

# Create key word arguments
kwargs_process = {'cell_size': 2,
                  'work_geodatabase': work_geodatabase,
                  'input_array': [chenega_raster, segments_initial],
                  'output_array': [segments_final, segments_polygon, segments_point]
                  }

# Post-process segments
print('Post-processing image segments...')
arcpy_geoprocessing(postprocess_segments, **kwargs_process)
print('----------')