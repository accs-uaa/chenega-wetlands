# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process wetlands
# Author: Timm Nawrocki
# Last Updated: 2023-08-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process wetlands" processes the predicted raster into polygon versions for manual adjustment.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import postprocess_categorical_raster
from package_GeospatialProcessing import postprocess_marine_types
from package_GeospatialProcessing import postprocess_terrestrial_types

# Set round date
round_date = 'round_20231217'
version_number = 'v1_0'

# Set root directory
drive = 'D:/'
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
area_input = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea_1m_3338.tif')
boundary_input = os.path.join(project_geodatabase, 'Chenega_ModelArea')
wetlands_input = os.path.join(project_folder, 'Data_Output/output_rasters',
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
wetlands_dictionary = {1: 'M1AB1L',
                       2: 'M1UBL',
                       3: 'M2AB1M',
                       4: 'M2AB1N',
                       5: 'M2RS1N',
                       6: 'M2RS1N',
                       7: 'PAB3H',
                       8: 'PEM1D',
                       9: 'PEM1E',
                       10: 'PFO4B',
                       11: 'PSS4B',
                       12: 'PUB3H',
                       13: 'alpine dwarf shrub',
                       14: 'alpine sparse/barren',
                       15: 'alpine-subalpine herbaceous',
                       16: 'barren disturbed',
                       17: 'coastal herbaceous',
                       18: 'mountain hemlock - Sitka spruce',
                       19: 'Sitka alder-salmonberry',
                       20: 'riparian shrub',
                       21: 'subalpine mountain hemlock woodland',
                       22: 'LAB3H',
                       23: 'LUB3H',
                       24: 'PRB1H',
                       25: 'E2EM1P',
                       26: 'PEM1C',
                       27: 'PSS1C',
                       28: 'R1UB1V',
                       29: 'R2UB1H',
                       30: 'R3UB1H',
                       31: 'R4SB3J'}

#### POST-PROCESS WATERBODIES

# Create key word arguments
kwargs_waterbodies = {'mmu': mmu_terrestrial,
                      'attribute_dictionary': wetlands_dictionary,
                      'work_geodatabase': work_geodatabase,
                      'input_array': [area_input,
                                      wetlands_input,
                                      waterbody_additions,
                                      waterbody_deletions],
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
                  'attribute_dictionary': wetlands_dictionary,
                  'work_geodatabase': work_geodatabase,
                  'input_array': [area_input, wetlands_input],
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
                  'attribute_dictionary': wetlands_dictionary,
                  'work_geodatabase': work_geodatabase,
                  'input_array': [area_input, wetlands_input],
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
