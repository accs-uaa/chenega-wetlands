# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process waterbodies
# Author: Timm Nawrocki
# Last Updated: 2023-08-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process waterbodies" is a function that merges waterbodies and then splits by type.
# ---------------------------------------------------------------------------

# Define a function to post-process waterbodies
def postprocess_waterbodies(**kwargs):
    """
    Description: merges waterbodies and then splits by type
    Inputs: 'attribute_dictionary' -- a dictionary of name and value pairs for the map schema
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first), the predicted raster, a feature class of manual additions to waterbodies, and a feature class of manual deletions for waterbodies
            'output_array' -- an array containing the output feature class
    Returned Value: Returns a feature class to disk
    Preconditions: requires a predicted categorical raster and manually created waterbody additions and deletions
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import Int
    from arcpy.sa import IsNull
    from arcpy.sa import Raster
    from arcpy.sa import SetNull
    from arcpy.sa import ZonalStatistics
    import datetime
    import os
    import time

    # Parse key word argument inputs
    attribute_dictionary = kwargs['attribute_dictionary']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    input_raster = kwargs['input_array'][1]
    waterbody_additions = kwargs['input_array'][2]
    waterbody_deletions = kwargs['input_array'][3]
    output_feature = kwargs['output_array'][0]

    # Define work folder
    work_folder = os.path.split(input_raster)[0]

    # Define intermediate datasets
    integer_raster = os.path.join(work_folder,'integer_raster.tif')
    conversion_feature = os.path.join(work_geodatabase, 'conversion_feature')
    waterbody_feature = os.path.join(work_geodatabase, 'waterbody_original')
    additions_feature = os.path.join(work_geodatabase, 'waterbody_corrected_additions')
    deletions_feature = os.path.join(work_geodatabase, 'waterbody_corrected_deletions')
    modified_feature = os.path.join(work_geodatabase, 'waterbody_modified')
    zonal_raster = os.path.join(work_folder, 'aquaticbed_proportion.tif')
    parsed_feature = os.path.join(work_geodatabase, 'waterbody_parsed')

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Set output coordinate system
    arcpy.env.outputCoordinateSystem = Raster(area_raster)

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Retrieve waterbody values
    value_pub3h = attribute_dictionary.get('PUB3H')
    value_pab3h = attribute_dictionary.get('PAB3H')

    # Convert raster to polygon
    print(f'\tConverting waterbody raster to polygon...')
    iteration_start = time.time()
    # Select raster values
    print(f'\t\tSelecting waterbody raster values...')
    null_raster = SetNull((Raster(input_raster) != value_pub3h) & (Raster(input_raster) != value_pab3h),
                          Raster(input_raster))
    # Convert raster to integer
    print(f'\t\tConverting waterbodies to integer raster...')
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
    # Convert raster to feature class
    print(f'\t\tConverting waterbodies to feature class...')
    arcpy.conversion.RasterToPolygon(integer_raster, conversion_feature, 'NO_SIMPLIFY',
                                     'VALUE', 'SINGLE_OUTER_PART')
    # Dissolve adjacent waterbody polygons
    print(f'\t\tDissolving adjacent waterbody polygons...')
    arcpy.analysis.PairwiseDissolve(conversion_feature, waterbody_feature, '',
                                    '', 'SINGLE_PART')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Modify waterbody polygons
    print(f'\tModifying waterbody polygons with manual corrections...')
    iteration_start = time.time()
    # Add additional water
    print(f'\t\tAdding additional water...')
    arcpy.management.Merge([waterbody_feature, waterbody_additions], additions_feature)
    # Remove erroneous water
    print(f'\t\tRemoving erroneous water...')
    arcpy.analysis.PairwiseErase(additions_feature, waterbody_deletions, deletions_feature)
    # Dissolve adjacent waterbody polygons
    print(f'\t\tDissolving adjacent waterbody polygons...')
    arcpy.analysis.PairwiseDissolve(deletions_feature, modified_feature, '',
                                    '', 'SINGLE_PART')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Calculate percentage aquatic bed
    print(f'\tCalculating percentage aquatic bed...')
    iteration_start = time.time()
    # Create binary raster for aquatic bed
    print(f'\t\tCalculating binary raster...')
    aquaticbed_raster = Con(Raster(integer_raster) == value_pab3h, 1, 0)
    binary_raster = Con(IsNull(aquaticbed_raster), 0, aquaticbed_raster)
    # Calculate zonal statistics for waterbodies
    print(f'\t\tCalculating zonal statistics...')
    aquatic_zonal = ZonalStatistics(modified_feature,
                                    'OBJECTID',
                                    binary_raster,
                                    'MEAN',
                                    'DATA',
                                    'CURRENT_SLICE')
    aquatic_integer = Int((aquatic_zonal * 100) + 0.5)
    # Export zonal raster
    print(f'\t\tExporting zonal raster...')
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
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Parse waterbody types
    print(f'\tParse waterbody types...')
    iteration_start = time.time()
    # Parse zonal results into types
    print(f'\t\tParsing zonal mean into types...')
    aquatic_types = Con(Raster(zonal_raster) >= 30, value_pab3h, value_pub3h)
    # Convert aquatic types to polygon
    print(f'\t\tConverting parsed waterbodies to feature class...')
    arcpy.conversion.RasterToPolygon(aquatic_types, parsed_feature, 'SIMPLIFY',
                                     'VALUE', 'SINGLE_OUTER_PART')
    # Attribute waterbodies based on size
    code_block = '''def get_waterbody_type(gridcode, area):
    waterbody_type = 0
    if gridcode == 7:
        if area >= 80937.1:
            waterbody_type = 22
        else:
            waterbody_type = 7
    elif gridcode == 12:
        if area >= 80937.1:
            waterbody_type = 23
        else:
            waterbody_type = 12
    return waterbody_type
    '''
    expression = 'get_waterbody_type(!gridcode!, float(!SHAPE.area!))'
    arcpy.management.AddField(parsed_feature, 'VALUE', 'SHORT')
    arcpy.management.CalculateField(parsed_feature,
                                    'VALUE',
                                    expression,
                                    'PYTHON3',
                                    code_block)
    # Enforce 0.5 acre MMU
    waterbody_layer = 'waterbody_output'
    arcpy.management.MakeFeatureLayer(parsed_feature, waterbody_layer)
    arcpy.management.SelectLayerByAttribute(waterbody_layer, 'NEW_SELECTION',
                                            'SHAPE_AREA < 2023.43', 'NON_INVERT')
    arcpy.management.DeleteFeatures(waterbody_layer)
    arcpy.management.CopyFeatures(waterbody_layer, output_feature)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

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

    # Return success message
    out_process = f'Successfully post-processed categorical raster.'
    return out_process
