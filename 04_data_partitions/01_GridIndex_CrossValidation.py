# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create cross-validation grid
# Author: Timm Nawrocki
# Last Updated: 2023-06-11
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create cross-validation grid" creates a validation grid index from a manually-generated study area polygon.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import parse_image_segments
from package_GeospatialProcessing import create_grid_index
from package_GeospatialProcessing import convert_validation_grid
import os

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')
segments_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Segments.gdb')

# Define input datasets
chenega_feature = os.path.join(work_geodatabase, 'Chenega_ModelArea')
chenega_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea_1m_3338.tif')
segments_point = os.path.join(work_geodatabase, 'Chenega_Segments_Original_Point')
segments_polygon = os.path.join(work_geodatabase, 'Chenega_Segments_Original_Polygon')

# Define output grid datasets
validation_grid = os.path.join(work_geodatabase, 'Chenega_GridIndex_Validation_10km')
validation_raster = os.path.join(project_folder, 'Data_Input/validation/Chenega_ValidationGroups.tif')
grid_folder = os.path.join(project_folder, 'Data_Input/imagery/segments/gridded')

#### GENERATE VALIDATION GRID INDEX

# Create key word arguments for the validation grid index
validation_kwargs = {'distance': '10 Kilometers',
                     'grid_field': 'grid_validation',
                     'work_geodatabase': work_geodatabase,
                     'input_array': [chenega_feature],
                     'output_array': [validation_grid]
                     }

# Create the validation grid index
if arcpy.Exists(validation_grid) == 0:
    print('Creating validation grid index...')
    arcpy_geoprocessing(create_grid_index, **validation_kwargs)
    print('----------')
else:
    print('Validation grid index already exists.')
    print('----------')

#### CONVERT VALIDATION GRIDS TO RASTERS

# Create key word arguments for validation raster
raster_kwargs = {'work_geodatabase': work_geodatabase,
                 'input_array': [validation_grid, chenega_feature, chenega_raster],
                 'output_array': [validation_raster]
                 }

# Generate validation group raster
if arcpy.Exists(validation_raster) == 0:
    print('Converting validation grids to raster...')
    arcpy_geoprocessing(convert_validation_grid, **raster_kwargs)
    print('----------')
else:
    print('Validation raster already exists.')
    print('----------')

#### PARSE REFINED IMAGE SEGMENTS FOR VALIDATION GRIDS

parse_kwargs = {'tile_name': 'grid_validation',
                'work_geodatabase': segments_geodatabase,
                'input_array': [chenega_raster, validation_grid, segments_point, segments_polygon],
                'output_folder': grid_folder
                }

# Create buffered tiles for the major grid
arcpy_geoprocessing(parse_image_segments, check_output=False, **parse_kwargs)
print('----------')
