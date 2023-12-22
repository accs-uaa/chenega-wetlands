# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Compile wetlands output
# Author: Timm Nawrocki
# Last Updated: 2023-12-20
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Compile wetlands output" merges the post-processed waterbodies, terrestrial, marine, and manual types into a single map.
# ---------------------------------------------------------------------------

# Import packages
from akutils import *
import arcpy
from arcpy.sa import Raster
import os
import time

# Set round date
round_date = 'round_20231217'

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')
manual_folder = os.path.join(project_folder, 'Data_Input/manual_types')
output_folder = os.path.join(project_folder, 'Data_Output/output_rasters', round_date)

# Define geodatabases
project_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')
workspace_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')

# Define input datasets
area_input = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea_1m_3338.tif')
boundary_input = os.path.join(project_geodatabase, 'Chenega_ModelArea')
terrestrial_input = os.path.join(project_geodatabase, 'Chenega_Terrestrial_Processed')
marine_input = os.path.join(project_geodatabase, 'Chenega_Marine_Processed')

# Define intermediate datasets
marine_erase = os.path.join(workspace_geodatabase, 'marine_erase')
wetlands_merge = os.path.join(workspace_geodatabase, 'wetlands_merge')
wetlands_dissolve = os.path.join(workspace_geodatabase, 'wetlands_dissolve')

# Define output datasets
wetlands_output = os.path.join(project_geodatabase, 'Chenega_Wetlands_20231220')
wetlands_smooth = os.path.join(project_geodatabase, 'Chenega_Wetlands_20231220_Smooth10m')

# Define surficial features dictionary
wetlands_dictionary = {1: 'M1AB1L',
                       2: 'M1UBL',
                       3: 'M2AB1M',
                       4: 'M2AB1N',
                       5: 'M2RS1N',
                       6: 'M2US1N',
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
                       31: 'R4SB3J',
                       32: 'lakeshore'}

# Set overwrite option
arcpy.env.overwriteOutput = True

# Specify core usage
arcpy.env.parallelProcessingFactor = '0'

# Set workspace
arcpy.env.workspace = workspace_geodatabase

# Set snap raster and extent
arcpy.env.snapRaster = area_input
arcpy.env.extent = Raster(area_input).extent

# Set output coordinate system
arcpy.env.outputCoordinateSystem = Raster(area_input)

# Set cell size environment
cell_size = arcpy.management.GetRasterProperties(area_input, 'CELLSIZEX', '').getOutput(0)
arcpy.env.cellSize = int(cell_size)

# Compile marine and terrestrial wetlands
print('Compiling marine and terrestrial wetlands...')
iteration_start = time.time()
# Erase terrestrial features from marine features
print('\tErasing terrestrial features from marine features...')
arcpy.analysis.PairwiseErase(marine_input, terrestrial_input, marine_erase)
# Merge marine and terrestrial wetlands
print('\tMerging marine and terrestrial wetlands...')
arcpy.management.Merge([marine_erase, terrestrial_input], wetlands_merge)
# Dissolve adjacent types
print('\tDissolving adjacent types...')
arcpy.analysis.PairwiseDissolve(wetlands_merge,
                                wetlands_dissolve,
                                'VALUE',
                                '',
                                'SINGLE_PART',
                                '')
# Clip polygon to coastline
print('\tClip polygons to study area...')
arcpy.analysis.PairwiseClip(wetlands_dissolve,
                            boundary_input,
                            wetlands_output)
arcpy.management.CopyFeatures(wetlands_output, wetlands_smooth)
# Smooth shared edges
print('\tSmoothing edges...')
arcpy.cartography.SmoothSharedEdges(wetlands_smooth,
                                    'PAEK',
                                    '10 Meters',
                                    '',
                                    '')
# Calculate attribute label field
print('\tBuilding attribute table...')
label_block = get_attribute_code_block()
label_expression = f'get_response(!VALUE!, {wetlands_dictionary}, "value")'
arcpy.management.CalculateField(wetlands_output,
                                'label',
                                label_expression,
                                'PYTHON3',
                                label_block)
arcpy.management.CalculateField(wetlands_smooth,
                                'label',
                                label_expression,
                                'PYTHON3',
                                label_block)
end_timing(iteration_start)

# Delete intermediate datasets
if arcpy.Exists(marine_erase) == 1:
    arcpy.management.Delete(marine_erase)
if arcpy.Exists(wetlands_merge) == 1:
    arcpy.management.Delete(wetlands_merge)
if arcpy.Exists(wetlands_dissolve) == 1:
    arcpy.management.Delete(wetlands_dissolve)
