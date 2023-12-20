# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process wetlands
# Author: Timm Nawrocki
# Last Updated: 2023-08-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process wetlands" processes the predicted raster into polygon versions for manual adjustment.
# ---------------------------------------------------------------------------

# Import packages
from akutils import *
import arcpy
from arcpy.sa import Con
from arcpy.sa import Int
from arcpy.sa import IsNull
from arcpy.sa import Raster
from arcpy.sa import SetNull
from arcpy.sa import ZonalStatistics
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

# Define minimum mapping units
mmu_terrestrial = 506
mmu_marine = 2023

# Define input datasets
area_input = os.path.join(project_folder, 'Data_Input/Chenega_ModelArea_1m_3338.tif')
wetlands_input = os.path.join(output_folder, 'Chenega_Wetlands_Raw.tif')
additions_input = os.path.join(project_geodatabase, 'Chenega_Waterbody_Manual_Addition')
deletions_input = os.path.join(project_geodatabase, 'Chenega_Waterbody_Manual_Remove')
prbh_input = os.path.join(manual_folder, 'Chenega_PRBH_Digitized.shp')

# Define intermediate datasets
integer_raster = os.path.join(output_folder, 'integer_raster.tif')
conversion_feature = os.path.join(workspace_geodatabase, 'conversion_feature')
waterbody_feature = os.path.join(workspace_geodatabase, 'waterbody_original')
additions_feature = os.path.join(workspace_geodatabase, 'waterbody_corrected_additions')
deletions_feature = os.path.join(workspace_geodatabase, 'waterbody_corrected_deletions')
modified_feature = os.path.join(workspace_geodatabase, 'waterbody_modified')
zonal_raster = os.path.join(output_folder, 'aquaticbed_proportion.tif')
parsed_feature = os.path.join(workspace_geodatabase, 'waterbody_parsed')
point_feature = os.path.join(workspace_geodatabase, 'point_feature')
joined_feature = os.path.join(workspace_geodatabase, 'joined_feature')

# Define output datasets
waterbody_output = os.path.join(project_geodatabase, 'Chenega_Waterbody_Processed')

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

# Retrieve waterbody values
value_pub3h = get_response('PUB3H', wetlands_dictionary, 'key')
value_pab3h = get_response('PAB3H', wetlands_dictionary, 'key')
value_lab3h = get_response('LAB3H', wetlands_dictionary, 'key')
value_lub3h = get_response('LUB3H', wetlands_dictionary, 'key')
value_prb1h = get_response('PRB1H', wetlands_dictionary, 'key')

# Convert raster to polygon
print('Converting waterbody raster to polygon...')
iteration_start = time.time()
# Select raster values
print('\tSelecting waterbody raster values...')
null_raster = SetNull((Raster(wetlands_input) != value_pub3h) & (Raster(wetlands_input) != value_pab3h),
                      Raster(wetlands_input))
# Convert raster to integer
print('\tConverting waterbodies to integer raster...')
arcpy.management.CopyRaster(null_raster,
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
# Convert raster to polygon
print('\tConverting waterbodies to polygon...')
arcpy.conversion.RasterToPolygon(integer_raster,
                                 conversion_feature,
                                 'NO_SIMPLIFY',
                                 'VALUE',
                                 'SINGLE_OUTER_PART')
# Dissolve adjacent waterbody polygons
print('\tDissolving adjacent waterbody polygons...')
arcpy.analysis.PairwiseDissolve(conversion_feature,
                                waterbody_feature,
                                '',
                                '',
                                'SINGLE_PART')
end_timing(iteration_start)

# Modify waterbody polygons
print('Modifying waterbody polygons with manual corrections...')
iteration_start = time.time()
# Add additional water
print('\tAdding additional water...')
arcpy.management.Merge([waterbody_feature, additions_input], additions_feature)
# Remove erroneous water
print('\tRemoving erroneous water...')
arcpy.analysis.PairwiseErase(additions_feature, deletions_input, deletions_feature)
# Dissolve adjacent waterbody polygons
print('\tDissolving adjacent waterbody polygons...')
arcpy.analysis.PairwiseDissolve(deletions_feature,
                                modified_feature,
                                '',
                                '',
                                'SINGLE_PART')
end_timing(iteration_start)

# Calculate percentage aquatic bed
print('Calculating percentage aquatic bed...')
iteration_start = time.time()
# Create binary raster for aquatic bed
print('\tCalculating binary raster...')
aquaticbed_raster = Con(Raster(integer_raster) == value_pab3h, 1, 0)
binary_raster = Con(IsNull(aquaticbed_raster), 0, aquaticbed_raster)
# Calculate zonal statistics for waterbodies
print('\tCalculating zonal statistics...')
aquatic_zonal = ZonalStatistics(modified_feature,
                                'OBJECTID',
                                binary_raster,
                                'MEAN',
                                'DATA',
                                'CURRENT_SLICE')
aquatic_integer = Int((aquatic_zonal * 100) + 0.5)
# Export zonal raster
print('\tExporting zonal raster...')
arcpy.management.CopyRaster(aquatic_integer,
                            zonal_raster,
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
end_timing(iteration_start)

# Parse waterbody types
print('Parse waterbody types...')
iteration_start = time.time()
# Parse zonal results into types
print('\tParsing zonal mean into types...')
aquatic_types = Con(Raster(zonal_raster) >= 30, value_pab3h, value_pub3h)
# Convert aquatic types to polygon
print('\tConverting parsed waterbodies to feature class...')
arcpy.conversion.RasterToPolygon(aquatic_types,
                                 parsed_feature,
                                 'SIMPLIFY',
                                 'VALUE',
                                 'SINGLE_OUTER_PART')
# Convert aquatic types to points
arcpy.management.FeatureToPoint(parsed_feature,
                                point_feature,
                                'INSIDE')
# Join point attributes to modified waterbody polygons
arcpy.analysis.SpatialJoin(modified_feature,
                           point_feature,
                           joined_feature,
                           'JOIN_ONE_TO_ONE',
                           'KEEP_ALL',
                           '',
                           'INTERSECT',
                           '',
                           '',
                           '')
# Smooth Polygon
arcpy.cartography.SmoothSharedEdges(joined_feature,
                                    'PAEK',
                                    '10 Meters',
                                    '',
                                    '')
# Enforce the MMU
waterbody_layer = 'waterbody_output'
arcpy.management.MakeFeatureLayer(joined_feature, waterbody_layer)
arcpy.management.SelectLayerByAttribute(waterbody_layer,
                                        'NEW_SELECTION',
                                        f'SHAPE_AREA < {mmu_terrestrial}',
                                        'NON_INVERT')
arcpy.management.DeleteFeatures(waterbody_layer)
arcpy.management.Merge([waterbody_layer, prbh_input], waterbody_output)
# Attribute waterbodies based on size
type_block = f'''def get_waterbody_type(gridcode, attribute, area):
    waterbody_type = 0
    if attribute == 'PRB1H':
        waterbody_type = {value_prb1h}
    elif gridcode == {value_pab3h}:
        if area >= 80937.1:
            waterbody_type = {value_lab3h}
        else:
            waterbody_type = {value_pab3h}
    elif gridcode == {value_pub3h}:
        if area >= 80937.1:
            waterbody_type = {value_lub3h}
        else:
            waterbody_type = {value_pub3h}
    return waterbody_type
    '''
type_expression = 'get_waterbody_type(!gridcode!, !ATTRIBUTE!, float(!SHAPE.area!))'
arcpy.management.AddField(waterbody_output,
                          'VALUE',
                          'LONG',
                          '',
                          '',
                          '',
                          '',
                          'NULLABLE',
                          'NON_REQUIRED',
                          '')
arcpy.management.CalculateField(waterbody_output,
                                'VALUE',
                                type_expression,
                                'PYTHON3',
                                type_block)
# Calculate attribute label field
label_block = get_attribute_code_block()
label_expression = f'get_response(!VALUE!, {wetlands_dictionary}, "value")'
arcpy.management.CalculateField(waterbody_output,
                                'label',
                                label_expression,
                                'PYTHON3',
                                label_block)
arcpy.management.DeleteField(waterbody_output,
                             ['Join_Count',
                              'TARGET_FID',
                              'Id',
                              'gridcode',
                              'ORIG_FID',
                              'ACRES',
                              'Shape_Leng',
                              'ATTRIBUTE'],
                             'DELETE_FIELDS')
end_timing(iteration_start)

# Delete intermediate datasets
if arcpy.Exists(integer_raster) == 1:
    arcpy.management.Delete(integer_raster)
if arcpy.Exists(conversion_feature) == 1:
    arcpy.management.Delete(conversion_feature)
if arcpy.Exists(waterbody_feature) == 1:
    arcpy.management.Delete(waterbody_feature)
if arcpy.Exists(additions_feature) == 1:
    arcpy.management.Delete(additions_feature)
if arcpy.Exists(deletions_feature) == 1:
    arcpy.management.Delete(deletions_feature)
if arcpy.Exists(modified_feature) == 1:
    arcpy.management.Delete(modified_feature)
if arcpy.Exists(parsed_feature) == 1:
    arcpy.management.Delete(parsed_feature)
if arcpy.Exists(point_feature) == 1:
    arcpy.management.Delete(point_feature)
if arcpy.Exists(joined_feature) == 1:
    arcpy.management.Delete(joined_feature)
