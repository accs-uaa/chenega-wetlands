# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create composite USGS 3DEP 5m
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Create composite USGS 3DEP 5m" combines individual DEM tiles and reprojects to NAD 1983 Alaska Albers.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import merge_elevation_tiles
import os

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')
topography_folder = os.path.join(project_folder, 'Data_Input/topography')
tile_folder = os.path.join(topography_folder, 'tiles')
projected_folder = os.path.join(topography_folder, 'tiles_projected')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')

# Define input datasets
chenega_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea.tif')

# Define output datasets
output_raster = os.path.join(topography_folder, 'float/Elevation.tif')

#### CREATE COMPOSITE DEM

# Create key word arguments
kwargs_merge = {'tile_folder': tile_folder,
                'projected_folder': projected_folder,
                'workspace': work_geodatabase,
                'cell_size': 5,
                'input_projection': 102247,
                'output_projection': 3338,
                'geographic_transformation': '',
                'input_array': [chenega_raster],
                'output_array': [output_raster]
                }

# Merge source tiles
arcpy_geoprocessing(merge_elevation_tiles, **kwargs_merge)
