# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Compile wetlands output
# Author: Timm Nawrocki
# Last Updated: 2024-01-09
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Compile wetlands output" merges the post-processed waterbodies, terrestrial, marine, and manual types into a single map.
# ---------------------------------------------------------------------------

# Import packages
from akutils import *
import arcpy
from arcpy.sa import Con
from arcpy.sa import ExtractByAttributes
from arcpy.sa import Nibble
from arcpy.sa import Raster
from arcpy.sa import RegionGroup
import os
import time

# Set round date
round_date = 'round_20231217'

# Define minimum mapping units in meters squared
mmu_terrestrial = 506

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')
output_folder = os.path.join(project_folder, 'Data_Output/output_rasters', round_date)

# Define geodatabases
project_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')
workspace_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')

# Define input datasets
area_input = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea_1m_3338.tif')
boundary_input = os.path.join(project_geodatabase, 'Chenega_ModelArea')
terrestrial_input = os.path.join(project_geodatabase, 'Chenega_Terrestrial_Processed')
marine_input = os.path.join(project_geodatabase, 'Chenega_Marine_Processed')
manual_input = os.path.join(project_geodatabase, 'Chenega_Manual_Types')
waterbody_input = os.path.join(project_geodatabase, 'Chenega_Waterbody_Processed')

# Define intermediate datasets
marine_erase = os.path.join(workspace_geodatabase, 'marine_erase')
wetlands_merge = os.path.join(workspace_geodatabase, 'wetlands_merge')
wetlands_dissolve = os.path.join(workspace_geodatabase, 'wetlands_dissolve')
wetlands_select = os.path.join(workspace_geodatabase, 'wetlands_select')
wetlands_compiled = os.path.join(output_folder, 'wetlands_compiled.tif')
wetlands_nibble = os.path.join(output_folder, 'wetlands_nibble.tif')
wetlands_preliminary = os.path.join(workspace_geodatabase, 'wetlands_preliminary')
manual_erase_1 = os.path.join(workspace_geodatabase, 'manual_erase_1')
manual_erase_2 = os.path.join(workspace_geodatabase, 'manual_erase_2')
manual_merge = os.path.join(workspace_geodatabase, 'manual_merge')
manual_dissolve = os.path.join(workspace_geodatabase, 'manual_dissolve')

# Define output datasets
wetlands_output = os.path.join(project_geodatabase, 'Chenega_Wetlands_20240110')
wetlands_smooth = os.path.join(project_geodatabase, 'Chenega_Wetlands_20240110_Smooth10m')
prb1h_output = os.path.join(project_geodatabase, 'Chenega_PRB1H_Processed')

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
# Remove slivers
print('\tRemoving polygon slivers...')
select_layer = 'select_layer'
arcpy.management.MakeFeatureLayer(wetlands_dissolve, select_layer)
arcpy.management.SelectLayerByAttribute(select_layer,
                                        'NEW_SELECTION',
                                        '"Shape_Area" < 13',
                                        'NON_INVERT')
arcpy.management.DeleteFeatures(select_layer)
arcpy.management.CopyFeatures(select_layer, wetlands_select)
end_timing(iteration_start)

# Remove slivers
print('Remove and replace raster slivers...')
iteration_start = time.time()
# Convert polygon to raster
print('\tConvert polygon to raster...')
arcpy.conversion.PolygonToRaster(wetlands_select,
                                 'VALUE',
                                 wetlands_compiled,
                                 'CELL_CENTER',
                                 '',
                                 cell_size,
                                 'BUILD')
# Calculate regions
print('\tCalculating contiguous value areas...')
region_raster = RegionGroup(wetlands_compiled,
                            'FOUR',
                            'WITHIN',
                            'NO_LINK')
# Remove zones below minimum mapping unit
print('\tReplacing contiguous areas below minimum mapping unit...')
criteria = f'COUNT > {mmu_terrestrial}'
mask_1 = ExtractByAttributes(region_raster, criteria)
mask_2 = Con(Raster(wetlands_compiled) > 23, 32760, mask_1)
# Replace removed data
nibble_raster = Nibble(wetlands_compiled,
                       mask_2,
                       'DATA_ONLY',
                       'PROCESS_NODATA')
# Export modified raster
print('\tExporting modified raster...')
arcpy.management.CopyRaster(nibble_raster,
                            wetlands_nibble,
                            '',
                            '',
                            '-128',
                            'NONE',
                            'NONE',
                            '8_BIT_SIGNED',
                            'NONE',
                            'NONE',
                            'TIFF',
                            'NONE',
                            'CURRENT_SLICE',
                            'NO_TRANSPOSE')
arcpy.management.CalculateStatistics(wetlands_nibble)
arcpy.management.BuildRasterAttributeTable(wetlands_nibble, 'Overwrite')
# Converting to polygon
arcpy.conversion.RasterToPolygon(wetlands_nibble,
                                 wetlands_preliminary,
                                 'SIMPLIFY',
                                 'VALUE',
                                 'SINGLE_OUTER_PART',
                                 '')
# Calculate attribute label field
print('\tBuilding attribute table...')
label_block = get_attribute_code_block()
label_expression = f'get_response(!gridcode!, {wetlands_dictionary}, "value")'
value_expression = f'get_response(!label!, {wetlands_dictionary}, "key")'
arcpy.management.CalculateField(wetlands_preliminary,
                                'label',
                                label_expression,
                                'PYTHON3',
                                label_block)
# Calculate attribute value field
arcpy.management.AddField(wetlands_preliminary,
                          'VALUE',
                          'LONG',
                          '',
                          '',
                          '',
                          '',
                          'NULLABLE',
                          'NON_REQUIRED',
                          '')
arcpy.management.CalculateField(wetlands_preliminary,
                                'VALUE',
                                value_expression,
                                'PYTHON3',
                                label_block)
print('\tDeleting extraneous fields...')
arcpy.management.DeleteField(wetlands_preliminary,
                             ['VALUE',
                              'label'],
                             'KEEP_FIELDS')
end_timing(iteration_start)

# Integrating manual types
print('Integrating manual types...')
iteration_start = time.time()
# Select PRB1H
print('\tSelect PRB1H...')
waterbody_layer = 'waterbody_layer'
arcpy.management.MakeFeatureLayer(waterbody_input, waterbody_layer)
arcpy.management.SelectLayerByAttribute(waterbody_layer,
                                        'NEW_SELECTION',
                                        "label = 'PRB1H'",
                                        'NON_INVERT')
arcpy.management.CopyFeatures(waterbody_layer, prb1h_output)
# Erase manual types
print('\tErasing manual types...')
arcpy.analysis.PairwiseErase(wetlands_preliminary, prb1h_output, manual_erase_1)
arcpy.analysis.PairwiseErase(manual_erase_1, manual_input, manual_erase_2)
# Merge manual types and model results
print('\tMerging manual types...')
arcpy.management.Merge([manual_erase_2, manual_input, prb1h_output], manual_merge)
# Dissolve polygons
print('\tDissolving adjacent polygons...')
arcpy.analysis.PairwiseDissolve(manual_merge,
                                manual_dissolve,
                                'VALUE',
                                '',
                                'SINGLE_PART',
                                '')
# Calculate attribute label field
print('\tBuilding attribute table...')
label_expression = f'get_response(!VALUE!, {wetlands_dictionary}, "value")'
arcpy.management.CalculateField(manual_dissolve,
                                'label',
                                label_expression,
                                'PYTHON3',
                                label_block)
print('\tDeleting extraneous fields...')
arcpy.management.DeleteField(manual_dissolve,
                             ['VALUE',
                              'label'],
                             'KEEP_FIELDS')
end_timing(iteration_start)

# Create final polygons
print('Creating final polygons...')
iteration_start = time.time()
# Clip polygons to study area
print('\tClip polygons to study area...')
arcpy.analysis.PairwiseClip(manual_dissolve,
                            boundary_input,
                            wetlands_output)
# Smooth shared edges
print('\tSmoothing edges...')
arcpy.management.CopyFeatures(wetlands_output, wetlands_smooth)
arcpy.cartography.SmoothSharedEdges(wetlands_smooth,
                                    'PAEK',
                                    '10 Meters',
                                    '',
                                    '')
end_timing(iteration_start)

# Delete intermediate datasets
if arcpy.Exists(marine_erase) == 1:
    arcpy.management.Delete(marine_erase)
if arcpy.Exists(wetlands_merge) == 1:
    arcpy.management.Delete(wetlands_merge)
if arcpy.Exists(wetlands_dissolve) == 1:
    arcpy.management.Delete(wetlands_dissolve)
if arcpy.Exists(wetlands_compiled) == 1:
    arcpy.management.Delete(wetlands_compiled)
if arcpy.Exists(wetlands_nibble) == 1:
    arcpy.management.Delete(wetlands_nibble)
if arcpy.Exists(wetlands_preliminary) == 1:
    arcpy.management.Delete(wetlands_preliminary)
if arcpy.Exists(manual_erase_1) == 1:
    arcpy.management.Delete(manual_erase_1)
if arcpy.Exists(manual_erase_2) == 1:
    arcpy.management.Delete(manual_erase_2)
if arcpy.Exists(manual_merge) == 1:
    arcpy.management.Delete(manual_merge)
if arcpy.Exists(manual_dissolve) == 1:
    arcpy.management.Delete(manual_dissolve)