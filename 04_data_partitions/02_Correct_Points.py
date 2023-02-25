# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Correct segment points
# Author: Timm Nawrocki
# Last Updated: 2023-02-24
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Correct segment points" adds necessary fields to revised segment points.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')
segments_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Segments.gdb')

# Define grids
grid_list = ['A1', 'A2',
             'B1', 'B2', 'B3',
             'C1', 'C2', 'C3',
             'D1', 'D2', 'D3']

# Loop through each grid in grid list and add segment metadata
for grid in grid_list:
    print(f'Correcting segments for grid {grid}...')

    # Define input polygons
    input_feature = os.path.join(segments_geodatabase, 'polygons_' + grid)

    # Define output points
    output_feature = os.path.join(segments_geodatabase, 'points_' + grid)

    # Create zonal summary if output raster does not already exist
    if arcpy.Exists(output_feature) == 0:
        arcpy.management.CalculateField(input_feature,
                                        'shape_m',
                                        '!SHAPE.length!',
                                        'PYTHON3')
        arcpy.management.CalculateField(input_feature,
                                        'shape_m2',
                                        '!SHAPE.area!',
                                        'PYTHON3')
        arcpy.management.FeatureToPoint(input_feature,
                                        output_feature,
                                        'INSIDE')
        arcpy.management.DeleteField(output_feature,
                                     ['ORIG_FID'],
                                     'DELETE_FIELDS')
        arcpy.management.AddXY(output_feature)
        print('----------')

    # If point feature class already exists, print message
    else:
        print(f'Segment points for {grid} already exist.')
        print('----------')
