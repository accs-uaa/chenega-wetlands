# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process terrestrial types
# Author: Timm Nawrocki
# Last Updated: 2023-08-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process terrestrial types" is a function that selects the terrestrial types, enforces a coastline, and converts to polygons.
# ---------------------------------------------------------------------------

# Define a function to post-process terrestrial types
def postprocess_terrestrial_types(**kwargs):
    """
    Description: converts terrestrial types to polygon
    Inputs: 'attribute_dictionary' -- a dictionary of name and value pairs for the map schema
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first) and the post-processed raster
            'output_array' -- an array containing the output feature class
    Returned Value: Returns a feature class to disk
    Preconditions: requires a post-processed categorical raster
    """

    # Import packages
    from akutils import get_attribute_code_block
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Nibble
    from arcpy.sa import Raster
    from arcpy.sa import SetNull
    import datetime
    import os
    import time

    # Parse key word argument inputs
    attribute_dictionary = kwargs['attribute_dictionary']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    input_raster = kwargs['input_array'][1]
    inner_feature = kwargs['input_array'][2]
    outer_feature = kwargs['input_array'][3]
    study_feature = kwargs['input_array'][4]
    output_feature = kwargs['output_array'][0]

    # Define work folder
    work_folder = os.path.split(input_raster)[0]

    # Define intermediate datasets
    terrestrial_type_feature = os.path.join(work_geodatabase, 'terrestrial_type_feature')
    coastal_type_feature = os.path.join(work_geodatabase, 'coastal_type_feature')
    merged_feature = os.path.join(work_geodatabase, 'merged_terrestrial_coastal_types')
    merged_raster = os.path.join(work_folder, 'merged_terrestrial_coastal_types.tif')
    processed_feature = os.path.join(work_geodatabase, 'processed_feature')

    # Define code block
    label_block = get_attribute_code_block()

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

    # Creating terrestrial type layer
    print(f'\tCreating terrestrial type layer...')
    iteration_start = time.time()
    # Extract wetlands raster to coastline
    print(f'\t\tExtracting wetlands to coastline...')
    extract_inner = ExtractByMask(input_raster, inner_feature)
    # Remove coastal and marine types
    print(f'\t\tRemoving coastal and marine types...')
    terrestrial_raster = SetNull(extract_inner <= 6, extract_inner)
    # Extend terrestrial raster to study area
    print(f'\t\tExtend terrestrial types...')
    extend_terrestrial = Nibble(terrestrial_raster, terrestrial_raster, 'DATA_ONLY', 'PROCESS_NODATA')
    # Extract terrestrial raster to coastline
    print(f'\t\tExtracting terrestrial raster to coastline...')
    extract_terrestrial = ExtractByMask(extend_terrestrial, inner_feature)
    # Convert terrestrial raster to polygon
    print(f'\t\tConverting terrestrial raster to polygons...')
    arcpy.conversion.RasterToPolygon(extract_terrestrial, terrestrial_type_feature, 'NO_SIMPLIFY',
                                     'VALUE', 'SINGLE_OUTER_PART')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Creating coastal type layer
    print(f'\tCreating coastal type layer...')
    iteration_start = time.time()
    # Extract wetlands raster to inverse coastline
    print(f'\t\tExtracting wetlands to inverse coastline...')
    extract_outer = ExtractByMask(input_raster, outer_feature)
    # Remove terrestrial types
    print(f'\t\tRemoving terrestrial types...')
    coastal_raster = SetNull((extract_outer != 4) & (extract_outer != 5) &
                             (extract_outer != 6) & (extract_outer != 17), extract_outer)
    # Extend coastal raster to study area
    print(f'\t\tExtend coastal types...')
    extend_coastal = Nibble(coastal_raster, coastal_raster, 'DATA_ONLY', 'PROCESS_NODATA')
    # Set marine types to null
    print(f'\t\tSetting marine types to null...')
    null_marine = SetNull((Raster(input_raster) == 1) | (Raster(input_raster) == 2) |
                            (Raster(input_raster) == 3), extend_coastal)
    # Extract coastal raster to inverse coastline
    print(f'\t\tExtracting coastal raster to inverse coastline...')
    extract_coastal = ExtractByMask(null_marine, outer_feature)
    # Convert coastal raster to polygon
    print(f'\t\tConverting coastal raster to polygons...')
    arcpy.conversion.RasterToPolygon(extract_coastal, coastal_type_feature, 'NO_SIMPLIFY',
                                     'VALUE', 'SINGLE_OUTER_PART')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Merge terrestrial and coastal types
    print(f'\tMerging terrestrial and coastal types...')
    iteration_start = time.time()
    # Merge polygons
    print(f'\t\tMerging polygons...')
    arcpy.management.Merge([terrestrial_type_feature, coastal_type_feature],
                           merged_feature)
    # Convert polygon to raster
    arcpy.conversion.PolygonToRaster(merged_feature, 'gridcode', merged_raster,
                                     'CELL_CENTER', '', cell_size, 'BUILD')
    # Convert raster to polygon
    arcpy.conversion.RasterToPolygon(merged_raster, processed_feature, 'SIMPLIFY',
                                     'VALUE', 'SINGLE_OUTER_PART')
    # Calculate attribute label field
    label_expression = f'get_response(!gridcode!, {attribute_dictionary}, "value")'
    arcpy.management.AddField(processed_feature, 'label', 'TEXT')
    arcpy.management.CalculateField(processed_feature,
                                    'label',
                                    label_expression,
                                    'PYTHON3',
                                    label_block)
    arcpy.management.DeleteField(processed_feature, ['gridcode'], 'DELETE_FIELDS')
    # Clip processed feature to study area boundary
    arcpy.analysis.PairwiseClip(processed_feature, study_feature, output_feature)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Delete intermediate datasets
    if arcpy.Exists(terrestrial_type_feature) == 1:
        arcpy.management.Delete(terrestrial_type_feature)
    if arcpy.Exists(coastal_type_feature) == 1:
        arcpy.management.Delete(coastal_type_feature)
    if arcpy.Exists(merged_feature) == 1:
        arcpy.management.Delete(merged_feature)
    if arcpy.Exists(merged_raster) == 1:
        arcpy.management.Delete(merged_raster)
    if arcpy.Exists(processed_feature) == 1:
        arcpy.management.Delete(processed_feature)

    # Return success message
    out_process = f'Successfully post-processed terrestrial types.'
    return out_process
