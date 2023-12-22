# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process terrestrial
# Author: Timm Nawrocki
# Last Updated: 2023-12-20
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process terrestrial" processes the predicted raster and manually delineated types into polygon terrestrial types.
# ---------------------------------------------------------------------------

# Import packages
from akutils import *
import arcpy
from arcpy.sa import BoundaryClean
from arcpy.sa import Con
from arcpy.sa import ExtractByAttributes
from arcpy.sa import ExtractByMask
from arcpy.sa import IsNull
from arcpy.sa import MajorityFilter
from arcpy.sa import Nibble
from arcpy.sa import Raster
from arcpy.sa import RegionGroup
from arcpy.sa import SetNull
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

# Define minimum mapping units in meters squared
mmu_terrestrial = 506
mmu_marine = 2023

# Define input datasets
area_input = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea_1m_3338.tif')
wetlands_input = os.path.join(output_folder, 'Chenega_Wetlands_Raw.tif')
coastline_input = os.path.join(project_geodatabase, 'Chenega_Coast_LAF_Smooth')
training_input = os.path.join(project_geodatabase, 'Chenega_Training_Polys_20230606')
e2em1p_input = os.path.join(manual_folder, 'Chenega_E2EM1P_Digitized.shp')
pem1c_input = os.path.join(manual_folder, 'Chenega_PEM1C_Digitized.shp')
pss1c_input = os.path.join(manual_folder, 'Chenega_PSS1C_Digitized.shp')
r1ub1v_input = os.path.join(manual_folder, 'Chenega_R1UB1V_Digitized.shp')
r2ub1h_input = os.path.join(manual_folder, 'Chenega_R2UB1H_Digitized.shp')
r3ub1h_input = os.path.join(manual_folder, 'Chenega_R3UB1H_Digitized.shp')
r4sb3j_input = os.path.join(manual_folder, 'Chenega_R4SB3J_Digitized.shp')
waterbody_input = os.path.join(project_geodatabase, 'Chenega_Waterbody_Processed')

# Define intermediate datasets
manual_dissolve = os.path.join(workspace_geodatabase, 'manual_types_dissolve')
manual_raster = os.path.join(manual_folder, 'manual_raster.tif')
waterbody_dissolve = os.path.join(workspace_geodatabase, 'waterbody_dissolve')
waterbody_raster = os.path.join(output_folder, 'waterbody_raster.tif')
training_dissolve = os.path.join(workspace_geodatabase, 'training_dissolve')
training_raster = os.path.join(output_folder, 'training_raster.tif')
integer_raster = os.path.join(output_folder, 'integer_raster.tif')
terrestrial_raster = os.path.join(output_folder, 'terrestrial_raster.tif')
terrestrial_preliminary = os.path.join(workspace_geodatabase, 'terrestrial_preliminary')
manual_erase = os.path.join(workspace_geodatabase, 'manual_erase')
terrestrial_merge = os.path.join(workspace_geodatabase, 'terrestrial_merge')
terrestrial_dissolve = os.path.join(workspace_geodatabase, 'terrestrial_dissolve')
r1ub1v_feature = os.path.join(workspace_geodatabase, 'Chenega_R1UB1V_Digitized')
r2ub1h_feature = os.path.join(workspace_geodatabase, 'Chenega_R2UB1H_Digitized')
r3ub1h_feature = os.path.join(workspace_geodatabase, 'Chenega_R3UB1H_Digitized')
r4sb3j_feature = os.path.join(workspace_geodatabase, 'Chenega_R4SB3J_Digitized')

# Define output datasets
manual_output = os.path.join(project_geodatabase, 'Chenega_Manual_Types')
training_output = os.path.join(project_geodatabase, 'Chenega_Training_Integration')
terrestrial_output = os.path.join(project_geodatabase, 'Chenega_Terrestrial_Processed')
riparian_output = os.path.join(project_geodatabase, 'Chenega_Riparian_Types')

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

# Prepare manual types
print('Preparing manual types for integration...')
iteration_start = time.time()
# Merge manual types
print('\tMerging manual types...')
arcpy.management.Merge([e2em1p_input,
                        pem1c_input,
                        pss1c_input,
                        r1ub1v_input,
                        r2ub1h_input,
                        r3ub1h_input,
                        r4sb3j_input],
                       manual_output)
# Calculate attribute value field
print('\tBuilding attribute table...')
arcpy.management.AddField(manual_output,
                          'VALUE',
                          'LONG',
                          '',
                          '',
                          '',
                          '',
                          'NULLABLE',
                          'NON_REQUIRED',
                          '')
label_block = get_attribute_code_block()
value_expression = f'get_response(!ATTRIBUTE!, {wetlands_dictionary}, "key")'
arcpy.management.CalculateField(manual_output,
                                'VALUE',
                                value_expression,
                                'PYTHON3',
                                label_block)
# Calculate attribute label field
label_expression = f'get_response(!VALUE!, {wetlands_dictionary}, "value")'
arcpy.management.CalculateField(manual_output,
                                'label',
                                label_expression,
                                'PYTHON3',
                                label_block)
# Delete extraneous fields
print('\tDeleting extraneous fields...')
arcpy.management.DeleteField(manual_output,
                             ['VALUE',
                              'label'],
                             'KEEP_FIELDS')
# Convert manual types to raster
print('\tConverting manual types to raster...')
arcpy.conversion.PolygonToRaster(manual_output,
                                 'VALUE',
                                 manual_raster,
                                 'CELL_CENTER',
                                 '',
                                 cell_size,
                                 'BUILD')
end_timing(iteration_start)

# Prepare waterbodies
print('Preparing waterbodies for integration...')
iteration_start = time.time()
# Convert waterbodies to raster
print('\tConverting waterbodies to raster...')
arcpy.conversion.PolygonToRaster(waterbody_input,
                                 'VALUE',
                                 waterbody_raster,
                                 'CELL_CENTER',
                                 '',
                                 cell_size,
                                 'BUILD')
end_timing(iteration_start)

# Prepare training polygons
print('Preparing training polygons for integration...')
iteration_start = time.time()
# Filter by attributes and size
print('\tFiltering training polygons...')
training_layer = 'training_output'
arcpy.management.MakeFeatureLayer(training_input, training_layer)
training_expression = '''ATTRIBUTE IN ('E1AB1L', 'E1UBL', 'E2AB1M', 'E2AB1N', 'E2RS1N', 'E2US1N', 'PEM1D', 'PEM1E', 'PFO4B', 'PSS4B')'''
arcpy.management.SelectLayerByAttribute(training_layer,
                                        'NEW_SELECTION',
                                        training_expression,
                                        'NON_INVERT')
arcpy.management.SelectLayerByAttribute(training_layer,
                                        'SUBSET_SELECTION',
                                        f'SHAPE_AREA >= {mmu_terrestrial}',
                                        'NON_INVERT')
arcpy.management.SelectLayerByLocation(training_layer,
                                       'INTERSECT',
                                       manual_output,
                                       '',
                                       'REMOVE_FROM_SELECTION',
                                       'NOT_INVERT')
arcpy.management.SelectLayerByLocation(training_layer,
                                       'WITHIN_A_DISTANCE',
                                       manual_output,
                                       '5 Meters',
                                       'REMOVE_FROM_SELECTION',
                                       'NOT_INVERT')
arcpy.management.SelectLayerByLocation(training_layer,
                                       'WITHIN_A_DISTANCE',
                                       waterbody_input,
                                       '5 Meters',
                                       'REMOVE_FROM_SELECTION',
                                       'NOT_INVERT')
# Copy selected features to new feature class
print('\tCreating new feature class...')
arcpy.management.CopyFeatures(training_layer, training_output)
# Modify attributes
print('\tBuilding attribute table...')
modify_block = f'''def correct_code(attribute):
    if attribute == 'E1AB1L':
        return 'M1AB1L'
    elif attribute == 'E1UBL':
        return 'M1UBL'
    elif attribute == 'E2AB1M':
        return 'M2AB1M'
    elif attribute == 'E2AB1N':
        return 'M2AB1N'
    elif attribute == 'E2RS1N':
        return 'M2RS1N'
    elif attribute == 'E2US1N':
        return 'M2US1N'
    else:
        return attribute
    '''
modify_expression = 'correct_code(!ATTRIBUTE!)'
arcpy.management.CalculateField(training_output,
                                'label',
                                modify_expression,
                                'PYTHON3',
                                modify_block)
arcpy.management.AddField(training_output,
                          'VALUE',
                          'LONG',
                          '',
                          '',
                          '',
                          '',
                          'NULLABLE',
                          'NON_REQUIRED',
                          '')
value_expression = f'get_response(!label!, {wetlands_dictionary}, "key")'
arcpy.management.CalculateField(training_output,
                                'VALUE',
                                value_expression,
                                'PYTHON3',
                                label_block)
arcpy.management.DeleteField(training_output,
                             ['VALUE',
                              'label'],
                             'KEEP_FIELDS')
# Convert training features to raster
print('\tConverting training features to raster...')
arcpy.conversion.PolygonToRaster(training_output,
                                 'VALUE',
                                 training_raster,
                                 'CELL_CENTER',
                                 '',
                                 cell_size,
                                 'BUILD')
end_timing(iteration_start)

# Create terrestrial type raster
print('Creating terrestrial type raster...')
iteration_start = time.time()
# Calculate binary rasters
print('\tCalculating binary rasters...')
waterbody_binary = Con(IsNull(Raster(waterbody_raster)), 0, 1)
manual_binary = Con(IsNull(Raster(manual_raster)), 0, 1)
# Integrate training polygons
print('\tIntegrating training polygons...')
training_integrated = Con(IsNull(Raster(training_raster)),
                          Raster(wetlands_input),
                          Raster(training_raster))
# Extract wetlands raster to coastline
print('\tExtracting wetlands to coastline...')
extract_raster = ExtractByMask(training_integrated, coastline_input)
# Change waterbody value
print('\tModifying raster values...')
modified_raster = Con((extract_raster == 7) | (extract_raster == 12), 32, extract_raster)
# Remove coastal and waterbody types
print('\tRemoving coastal and waterbody types...')
remove_coastal = SetNull(modified_raster <= 6, modified_raster)
remove_waterbody = SetNull(waterbody_binary == 1, remove_coastal)
# Convert raster to integer
print('\tConverting to integer raster...')
arcpy.management.CopyRaster(remove_waterbody,
                            integer_raster,
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
arcpy.management.CalculateStatistics(integer_raster)
arcpy.management.BuildRasterAttributeTable(integer_raster, 'Overwrite')
# Clean raster boundaries
print('\tCleaning raster boundaries...')
boundary_raster = BoundaryClean(integer_raster,
                                'DESCEND',
                                'TWO_WAY')
# Apply majority filter
print('\tSmoothing raster edges...')
majority_raster = MajorityFilter(boundary_raster,
                                 'EIGHT',
                                 'MAJORITY')
# Calculate regions
print('\tCalculating contiguous value areas...')
region_initial = RegionGroup(majority_raster,
                             'FOUR',
                             'WITHIN',
                             'NO_LINK')
# Remove zones below minimum mapping unit
print('\tReplacing contiguous areas below minimum mapping unit...')
criteria = f'COUNT > {mmu_terrestrial}'
mask_1 = ExtractByAttributes(region_initial, criteria)
# Replace removed data
nibble_initial = Nibble(majority_raster,
                        mask_1,
                        'DATA_ONLY',
                        'PROCESS_NODATA')
end_timing(iteration_start)

# Integrate manual types
print('Integrating manual types...')
iteration_start = time.time()
# Change waterbody values
print('\tChanging waterbody data values...')
waterbody_integrate = Con(waterbody_binary == 1, Raster(waterbody_raster), nibble_initial)
# Change manual data values
print('\tChanging manual data values...')
manual_integrate = Con(manual_binary == 1, Raster(manual_raster), waterbody_integrate)
# Calculate regions
print('\tCalculating contiguous value areas...')
region_secondary = RegionGroup(manual_integrate,
                               'FOUR',
                               'WITHIN',
                               'NO_LINK')
# Remove zones below minimum mapping unit
print('\tReplacing contiguous areas below minimum mapping unit...')
criteria = f'COUNT > {mmu_terrestrial}'
mask_2 = ExtractByAttributes(region_secondary, criteria)
mask_3 = Con(waterbody_binary == 1, 32760, mask_2)
mask_4 = Con(manual_binary == 1, 32759, mask_3)
# Replace removed data
nibble_secondary = Nibble(manual_integrate,
                          mask_4,
                          'DATA_ONLY',
                          'PROCESS_NODATA')
# Export modified raster
print('\tExporting modified raster...')
arcpy.management.CopyRaster(nibble_secondary,
                            terrestrial_raster,
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
arcpy.management.CalculateStatistics(terrestrial_raster)
arcpy.management.BuildRasterAttributeTable(terrestrial_raster, 'Overwrite')
end_timing(iteration_start)

# Convert terrestrial types to polygon
print('Creating terrestrial type polygon...')
iteration_start = time.time()
# Convert raster to polygon
print('\tConvert raster to polygon...')
arcpy.conversion.RasterToPolygon(terrestrial_raster,
                                 terrestrial_preliminary,
                                 'SIMPLIFY',
                                 'VALUE',
                                 'SINGLE_OUTER_PART')
# Calculate attribute label field
print('\tBuilding attribute table...')
label_expression = f'get_response(!gridcode!, {wetlands_dictionary}, "value")'
arcpy.management.CalculateField(terrestrial_preliminary,
                                'label',
                                label_expression,
                                'PYTHON3',
                                label_block)
# Calculate attribute value field
arcpy.management.AddField(terrestrial_preliminary,
                          'VALUE',
                          'LONG',
                          '',
                          '',
                          '',
                          '',
                          'NULLABLE',
                          'NON_REQUIRED',
                          '')
arcpy.management.CalculateField(terrestrial_preliminary,
                                'VALUE',
                                value_expression,
                                'PYTHON3',
                                label_block)
print('\tDeleting extraneous fields...')
arcpy.management.DeleteField(terrestrial_preliminary,
                             ['VALUE',
                              'label'],
                             'KEEP_FIELDS')
# Erase overlapping riparian types
print('\tErasing overlap in riparian types...')
manual_layer = 'manual_layer'
arcpy.management.MakeFeatureLayer(manual_output, manual_layer)
r1ub1v_selection = 'VALUE <> 28'
arcpy.management.SelectLayerByAttribute(manual_layer,
                                        'NEW_SELECTION',
                                        r1ub1v_selection,
                                        'NON_INVERT')
arcpy.analysis.PairwiseErase(manual_output, manual_layer, r1ub1v_feature)
r2ub1h_selection = 'VALUE <> 29'
arcpy.management.SelectLayerByAttribute(manual_layer,
                                        'NEW_SELECTION',
                                        r2ub1h_selection,
                                        'NON_INVERT')
arcpy.analysis.PairwiseErase(manual_output, manual_layer, r2ub1h_feature)
r3ub1h_selection = 'VALUE <> 30'
arcpy.management.SelectLayerByAttribute(manual_layer,
                                        'NEW_SELECTION',
                                        r3ub1h_selection,
                                        'NON_INVERT')
arcpy.analysis.PairwiseErase(manual_output, manual_layer, r3ub1h_feature)
r4sb3j_selection = 'VALUE <> 31'
arcpy.management.SelectLayerByAttribute(manual_layer,
                                        'NEW_SELECTION',
                                        r4sb3j_selection,
                                        'NON_INVERT')
arcpy.analysis.PairwiseErase(manual_output, manual_layer, r4sb3j_feature)
arcpy.management.Merge([r1ub1v_feature,
                        r2ub1h_feature,
                        r3ub1h_feature,
                        r4sb3j_feature],
                       riparian_output)
# Integrate manual riparian types
print('\tIntegrating manual riparian types...')
arcpy.analysis.PairwiseErase(terrestrial_preliminary, riparian_output, manual_erase)
arcpy.management.Merge([manual_erase,
                        riparian_output],
                       terrestrial_merge)
arcpy.analysis.PairwiseDissolve(terrestrial_merge,
                                terrestrial_dissolve,
                                'VALUE',
                                '',
                                'SINGLE_PART',
                                '')
# Clip polygon to coastline
print('\tClip polygons to coastline...')
arcpy.analysis.PairwiseClip(terrestrial_dissolve,
                            coastline_input,
                            terrestrial_output)
end_timing(iteration_start)

# Delete intermediate datasets
if arcpy.Exists(manual_dissolve) == 1:
    arcpy.management.Delete(manual_dissolve)
if arcpy.Exists(manual_raster) == 1:
    arcpy.management.Delete(manual_raster)
if arcpy.Exists(waterbody_dissolve) == 1:
    arcpy.management.Delete(waterbody_dissolve)
if arcpy.Exists(waterbody_raster) == 1:
    arcpy.management.Delete(waterbody_raster)
if arcpy.Exists(training_dissolve) == 1:
    arcpy.management.Delete(training_dissolve)
if arcpy.Exists(training_raster) == 1:
    arcpy.management.Delete(training_raster)
if arcpy.Exists(integer_raster) == 1:
    arcpy.management.Delete(integer_raster)
if arcpy.Exists(terrestrial_raster) == 1:
    arcpy.management.Delete(terrestrial_raster)
if arcpy.Exists(terrestrial_preliminary) == 1:
    arcpy.management.Delete(terrestrial_preliminary)
if arcpy.Exists(manual_erase) == 1:
    arcpy.management.Delete(manual_erase)
if arcpy.Exists(terrestrial_merge) == 1:
    arcpy.management.Delete(terrestrial_merge)
if arcpy.Exists(terrestrial_dissolve) == 1:
    arcpy.management.Delete(terrestrial_dissolve)
if arcpy.Exists(r1ub1v_feature) == 1:
    arcpy.management.Delete(r1ub1v_feature)
if arcpy.Exists(r2ub1h_feature) == 1:
    arcpy.management.Delete(r2ub1h_feature)
if arcpy.Exists(r3ub1h_feature) == 1:
    arcpy.management.Delete(r3ub1h_feature)
if arcpy.Exists(r4sb3j_feature) == 1:
    arcpy.management.Delete(r4sb3j_feature)
