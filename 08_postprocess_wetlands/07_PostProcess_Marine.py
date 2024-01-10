# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process terrestrial
# Author: Timm Nawrocki
# Last Updated: 2024-01-09
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process marine" processes the predicted raster and manually delineated types into polygon marine types.
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

# Define minimum mapping units in meters squared
mmu_terrestrial = 506
mmu_marine = 2023

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data')
manual_folder = os.path.join(project_folder, 'Data_Input/manual_types_projected')
output_folder = os.path.join(project_folder, 'Data_Output/output_rasters', round_date)

# Define geodatabases
project_geodatabase = os.path.join(project_folder, 'EPA_Chenega.gdb')
workspace_geodatabase = os.path.join(project_folder, 'EPA_Chenega_Workspace.gdb')

# Define input datasets
area_input = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea_1m_3338.tif')
wetlands_input = os.path.join(output_folder, 'Chenega_Wetlands_Raw.tif')
coastline_input = os.path.join(project_geodatabase, 'Chenega_Coast_LAF_Inverse_Smooth')
manual_input = os.path.join(project_geodatabase, 'Chenega_Manual_Types')
training_input = os.path.join(project_geodatabase, 'Chenega_Training_Integration')
waterbody_input = os.path.join(project_geodatabase, 'Chenega_Waterbody_Processed')

# Define intermediate datasets
manual_raster = os.path.join(manual_folder, 'manual_raster.tif')
waterbody_raster = os.path.join(output_folder, 'waterbody_raster.tif')
training_raster = os.path.join(output_folder, 'training_raster.tif')
water_feature = os.path.join(workspace_geodatabase, 'marine_water')
water_raster = os.path.join(output_folder, 'marine_water.tif')
smooth_raster = os.path.join(output_folder, 'marine_smooth.tif')
integer_raster = os.path.join(output_folder, 'integer_raster.tif')
integer_majority = os.path.join(output_folder, 'integer_majority.tif')
marine_raster = os.path.join(output_folder, 'marine_raster.tif')

# Define output datasets
marine_output = os.path.join(project_geodatabase, 'Chenega_Marine_Processed')

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
# Convert manual types to raster
print('\tConverting manual types to raster...')
arcpy.conversion.PolygonToRaster(manual_input,
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
# Convert training features to raster
print('\tConverting training features to raster...')
arcpy.conversion.PolygonToRaster(training_input,
                                 'VALUE',
                                 training_raster,
                                 'CELL_CENTER',
                                 '',
                                 cell_size,
                                 'BUILD')
end_timing(iteration_start)

# Create marine water raster
print('Creating marine water raster...')
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
# Select marine water
print('\tSelecting marine water...')
marine_water = SetNull((extract_raster != 2) & (extract_raster != 3), extract_raster)
# Convert raster to integer
print('\tConverting to integer raster...')
arcpy.management.CopyRaster(marine_water,
                            water_raster,
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
arcpy.management.CalculateStatistics(water_raster)
arcpy.management.BuildRasterAttributeTable(water_raster, 'Overwrite')
# Calculate regions
print('\tCalculating contiguous value areas...')
region_initial = RegionGroup(water_raster,
                             'FOUR',
                             'WITHIN',
                             'NO_LINK')
# Remove zones below minimum mapping unit
print('\tReplacing contiguous areas below minimum mapping unit...')
criteria = f'COUNT > {mmu_marine}'
mask_1 = ExtractByAttributes(region_initial, criteria)
# Replace removed data
nibble_initial = Nibble(water_raster,
                        mask_1,
                        'DATA_ONLY',
                        'PROCESS_NODATA')
# Convert marine water to polygon
print('\tSmoothing edges...')
arcpy.conversion.RasterToPolygon(nibble_initial,
                                 water_feature,
                                 'NO_SIMPLIFY',
                                 'VALUE',
                                 'SINGLE_OUTER_PART',
                                 '')
arcpy.cartography.SmoothSharedEdges(water_feature,
                                    'PAEK',
                                    '150 Meters',
                                    '',
                                    '')
arcpy.conversion.PolygonToRaster(water_feature,
                                 'gridcode',
                                 smooth_raster,
                                 'CELL_CENTER',
                                 '',
                                 cell_size,
                                 'BUILD')
end_timing(iteration_start)

# Create marine type raster
print('Creating marine type raster...')
iteration_start = time.time()
# Change waterbody value
print('\tModifying raster values...')
modified_raster = Con((extract_raster == 7) | (extract_raster == 12), 32, extract_raster)
# Remove terrestrial and waterbody types
print('\tRemoving coastal and waterbody types...')
remove_terrestrial = SetNull(modified_raster > 7, modified_raster)
remove_waterbody = SetNull(waterbody_binary == 1, remove_terrestrial)
# Replace marine water
print('\tReplace marine water...')
replace_water = Con((remove_waterbody == 2) | (remove_waterbody == 3),
                    Raster(smooth_raster),
                    remove_waterbody)
# Convert raster to integer
print('\tConverting to integer raster...')
arcpy.management.CopyRaster(replace_water,
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
region_secondary = RegionGroup(majority_raster,
                               'FOUR',
                               'WITHIN',
                               'NO_LINK')
# Remove zones below minimum mapping unit
print('\tReplacing contiguous areas below minimum mapping unit...')
criteria = f'COUNT > {mmu_terrestrial}'
mask_2 = ExtractByAttributes(region_secondary, criteria)
# Replace removed data
nibble_secondary = Nibble(majority_raster,
                          mask_2,
                          'DATA_ONLY',
                          'PROCESS_NODATA')
end_timing(iteration_start)

# Integrate manual types
print('Integrating manual types...')
iteration_start = time.time()
# Change waterbody values
print('\tChanging waterbody data values...')
waterbody_integrate = Con(waterbody_binary == 1, Raster(waterbody_raster), nibble_secondary)
# Change manual data values
print('\tChanging manual data values...')
manual_integrate = Con(manual_binary == 1, Raster(manual_raster), waterbody_integrate)
# Calculate regions
print('\tCalculating contiguous value areas...')
region_tertiary = RegionGroup(manual_integrate,
                              'FOUR',
                              'WITHIN',
                              'NO_LINK')
# Remove zones below minimum mapping unit
print('\tReplacing contiguous areas below minimum mapping unit...')
criteria = f'COUNT > {mmu_terrestrial}'
mask_3 = ExtractByAttributes(region_tertiary, criteria)
mask_4 = Con(waterbody_binary == 1, 32760, mask_3)
mask_5 = Con(manual_binary == 1, 32759, mask_4)
# Replace removed data
nibble_tertiary = Nibble(manual_integrate,
                         mask_5,
                         'DATA_ONLY',
                         'PROCESS_NODATA')
# Export marine raster
print('\tExporting marine raster...')
arcpy.management.CopyRaster(nibble_tertiary,
                            marine_raster,
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
arcpy.management.CalculateStatistics(marine_raster)
arcpy.management.BuildRasterAttributeTable(marine_raster, 'Overwrite')
end_timing(iteration_start)

# Convert marine types to polygon
print('Creating marine type polygon...')
iteration_start = time.time()
# Convert raster to polygon
print('\tConvert raster to polygon...')
arcpy.conversion.RasterToPolygon(marine_raster,
                                 marine_output,
                                 'NO_SIMPLIFY',
                                 'VALUE',
                                 'SINGLE_OUTER_PART')
# Calculate attribute label field
print('\tBuilding attribute table...')
label_expression = f'get_response(!gridcode!, {wetlands_dictionary}, "value")'
label_block = get_attribute_code_block()
arcpy.management.CalculateField(marine_output,
                                'label',
                                label_expression,
                                'PYTHON3',
                                label_block)
# Calculate attribute value field
arcpy.management.AddField(marine_output,
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
arcpy.management.CalculateField(marine_output,
                                'VALUE',
                                value_expression,
                                'PYTHON3',
                                label_block)
print('\tDeleting extraneous fields...')
arcpy.management.DeleteField(marine_output,
                             ['VALUE',
                              'label'],
                             'KEEP_FIELDS')
end_timing(iteration_start)

# Delete intermediate datasets
if arcpy.Exists(manual_raster) == 1:
    arcpy.management.Delete(manual_raster)
if arcpy.Exists(waterbody_raster) == 1:
    arcpy.management.Delete(waterbody_raster)
if arcpy.Exists(training_raster) == 1:
    arcpy.management.Delete(training_raster)
if arcpy.Exists(water_feature) == 1:
    arcpy.management.Delete(water_feature)
if arcpy.Exists(water_raster) == 1:
    arcpy.management.Delete(water_raster)
if arcpy.Exists(integer_raster) == 1:
    arcpy.management.Delete(integer_raster)
if arcpy.Exists(marine_raster) == 1:
    arcpy.management.Delete(marine_raster)
