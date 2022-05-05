# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate flowlines
# Author: Timm Nawrocki
# Last Updated: 2022-03-22
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate flowlines" calculates a stream network from a digital elevation model. The stream network is output as a line feature class, which likely will need to be manually corrected and edited in places.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import generate_flowlines

# Set root directory
drive = 'M:/'
root_folder = 'EPA_Chenega'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Data')
topography_folder = os.path.join(project_folder, 'Data_Input/topography/float')
hydrography_folder = os.path.join(project_folder, 'Data_Input/hydrography')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')

# Define input datasets
chenega_feature = os.path.join(work_geodatabase, 'Chenega_ModelArea')
elevation_raster = os.path.join(topography_folder, 'Elevation.tif')

# Define output datasets
river_feature = os.path.join(work_geodatabase, 'Chenega_Rivers_DEM')
stream_feature = os.path.join(work_geodatabase, 'Chenega_Streams_DEM')

# Create key word arguments
kwargs_flow = {'threshold': 20000,
               'fill_value': 5,
               'work_geodatabase': work_geodatabase,
               'input_array': [chenega_feature, elevation_raster],
               'output_array': [river_feature, stream_feature]
               }

# Process the flowlines
print(f'Processing flowlines...')
arcpy_geoprocessing(generate_flowlines, **kwargs_flow)
print('----------')
