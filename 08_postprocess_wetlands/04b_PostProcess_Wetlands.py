# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process wetlands
# Author: Timm Nawrocki
# Last Updated: 2023-08-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process wetlands" processes the predicted raster into the final deliverable.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import postprocess_categorical_raster
from package_GeospatialProcessing import postprocess_marine_types
from package_GeospatialProcessing import postprocess_terrestrial_types
from package_GeospatialProcessing import postprocess_waterbodies

# Set round date
round_date = 'round_20230611'
version_number = 'v0_3'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')

# Define geodatabases
project_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')
work_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')

# Define minimum mapping units
mmu_terrestrial = 506
mmu_marine = 2023

# Define input datasets
study_raster = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea_1m_3338.tif')
study_feature = os.path.join(project_geodatabase, 'Chenega_ModelArea')
input_raster = os.path.join(project_folder, 'Data_Output/output_rasters',
                            round_date, 'Chenega_Wetlands_Raw.tif')
waterbody_additions = os.path.join(project_geodatabase, 'Chenega_Waterbody_Manual_Addition')
waterbody_deletions = os.path.join(project_geodatabase, 'Chenega_Waterbody_Manual_Remove')
coastline_feature = os.path.join(project_geodatabase, 'Chenega_Coast_LAF_Smooth')
inverse_feature = os.path.join(project_geodatabase, 'Chenega_Coast_LAF_Inverse_Smooth')

# Define output raster
waterbody_feature = os.path.join(project_geodatabase, 'Chenega_Waterbody_Processed')
wetlands_506m = os.path.join(project_folder, 'Data_Output/output_rasters',
                             round_date, 'Chenega_Wetlands_506m.tif')
wetlands_2023m = os.path.join(project_folder, 'Data_Output/output_rasters',
                              round_date, 'Chenega_Wetlands_2023m.tif')
marine_feature = os.path.join(project_geodatabase, 'Chenega_Marine_Processed')
terrestrial_feature = os.path.join(project_geodatabase, 'Chenega_Terrestrial_Processed')

# Define surficial features dictionary
class_values = {'E1AB1L': 1,
                'E1UBL': 2,
                'E2AB1M': 3,
                'E2AB1N': 4,
                'E2RS1N': 5,
                'E2US1N': 6,
                'PAB3H': 7,
                'PEM1D': 8,
                'PEM1E': 9,
                'PFO4B': 10,
                'PSS4B': 11,
                'PUB3H': 12,
                'alpine dwarf shrub': 13,
                'alpine sparse/barren': 14,
                'alpine-subalpine herbaceous': 15,
                'barren disturbed': 16,
                'coastal herbaceous': 17,
                'mountain hemlock - Sitka spruce': 18,
                'Sitka alder-salmonberry': 19,
                'riparian shrub': 20,
                'subalpine mountain hemlock woodland': 21,
                'LAB3H': 22,
                'LUB3H': 23}

#### POST-PROCESS WATERBODIES

# Create key word arguments
kwargs_waterbodies = {'mmu': mmu_terrestrial,
                      'attribute_dictionary': class_values,
                      'work_geodatabase': work_geodatabase,
                      'input_array': [study_raster, input_raster, waterbody_additions, waterbody_deletions],
                      'output_array': [waterbody_feature]
                      }

# Post-process waterbodies
if arcpy.Exists(waterbody_feature) == 0:
    print(f'Post-processing waterbodies...')
    arcpy_geoprocessing(postprocess_waterbodies, **kwargs_waterbodies)
    print('----------')
else:
    print(f'Waterbody feature class already exists.')
    print('----------')

#### POST-PROCESS CATEGORICAL RASTER FOR TERRESTRIAL MMU

# Create key word arguments
kwargs_process = {'mmu': mmu_terrestrial,
                  'attribute_dictionary': class_values,
                  'work_geodatabase': work_geodatabase,
                  'input_array': [study_raster, input_raster],
                  'output_array': [wetlands_506m]
                  }

# Post-process wetlands map
if arcpy.Exists(wetlands_506m) == 0:
    print(f'Post-processing wetlands map...')
    arcpy_geoprocessing(postprocess_categorical_raster, **kwargs_process)
    print('----------')
else:
    print(f'Post-processed raster already exists.')
    print('----------')

#### POST-PROCESS CATEGORICAL RASTER FOR MARINE MMU

# Create key word arguments
kwargs_process = {'mmu': mmu_marine,
                  'attribute_dictionary': class_values,
                  'work_geodatabase': work_geodatabase,
                  'input_array': [study_raster, input_raster],
                  'output_array': [wetlands_2023m]
                  }

# Post-process wetlands map
if arcpy.Exists(wetlands_2023m) == 0:
    print(f'Post-processing wetlands map...')
    arcpy_geoprocessing(postprocess_categorical_raster, **kwargs_process)
    print('----------')
else:
    print(f'Post-processed raster already exists.')
    print('----------')

#### SPLIT MARINE LAYER

# Create key word arguments
kwargs_marine = {'attribute_dictionary': class_values,
                 'work_geodatabase': work_geodatabase,
                 'input_array': [study_raster, wetlands_2023m, study_feature],
                 'output_array': [marine_feature]
                 }

# Post-process marine types
if arcpy.Exists(marine_feature) == 0:
    print(f'Post-processing marine types...')
    arcpy_geoprocessing(postprocess_marine_types, **kwargs_marine)
    print('----------')
else:
    print(f'Marine feature class already exists.')
    print('----------')

#### SPLIT TERRESTRIAL LAYER

kwargs_terrestrial = {'attribute_dictionary': class_values,
                      'work_geodatabase': work_geodatabase,
                      'input_array': [study_raster, wetlands_506m, coastline_feature,
                                      inverse_feature, study_feature],
                      'output_array': [terrestrial_feature]
                      }

# Post-process terrestrial types
if arcpy.Exists(terrestrial_feature) == 0:
    print(f'Post-processing terrestrial types...')
    arcpy_geoprocessing(postprocess_terrestrial_types, **kwargs_terrestrial)
    print('----------')
else:
    print(f'Terrestrial feature class already exists.')
    print('----------')
