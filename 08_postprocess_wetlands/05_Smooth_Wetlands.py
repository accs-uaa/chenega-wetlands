# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Smooth wetland polygons
# Author: Timm Nawrocki
# Last Updated: 2023-08-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Smooth wetland polygons" processes the predicted raster into a single smoothed set of polygons.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import smooth_wetlands

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')

# Define geodatabases
project_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')

# Define input datasets
waterbody_feature = os.path.join(project_geodatabase, 'Chenega_Waterbody_Processed')
marine_feature = os.path.join(project_geodatabase, 'Chenega_Marine_Processed')
terrestrial_feature = os.path.join(project_geodatabase, 'Chenega_Terrestrial_Processed')

# Define output datasets
wetlands_feature = os.path.join(project_geodatabase, 'Chenega_Wetlands_20230802')

# Create key word arguments
kwargs_smooth = {'work_geodatabase': work_geodatabase,
                 'input_array': [marine_feature, terrestrial_feature, waterbody_feature],
                 'output_array': [wetlands_feature]
                 }

# Smooth wetlands
if arcpy.Exists(wetlands_feature) == 0:
    print(f'Smoothing wetlands...')
    arcpy_geoprocessing(smooth_wetlands, **kwargs_smooth)
    print('----------')
else:
    print(f'Wetlands feature class already exists.')
    print('----------')
