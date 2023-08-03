# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process marine types
# Author: Timm Nawrocki
# Last Updated: 2023-08-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Post-process marine types" is a function that selects the marine types, extends them, and converts to polygons.
# ---------------------------------------------------------------------------

# Define a function to post-process marine types
def postprocess_marine_types(**kwargs):
    """
    Description: converts marine types to polygon with full coverage
    Inputs: 'attribute_dictionary' -- a dictionary of name and value pairs for the map schema
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first) and the post-processed raster
            'output_array' -- an array containing the output feature class
    Returned Value: Returns a feature class to disk
    Preconditions: requires a post-processed categorical raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import BoundaryClean
    from arcpy.sa import ExtractByAttributes
    from arcpy.sa import MajorityFilter
    from arcpy.sa import Nibble
    from arcpy.sa import Raster
    from arcpy.sa import RegionGroup
    from arcpy.sa import SetNull
    import datetime
    import os
    import time

    # Parse key word argument inputs
    attribute_dictionary = kwargs['attribute_dictionary']
    work_geodatabase = kwargs['work_geodatabase']
    area_raster = kwargs['input_array'][0]
    input_raster = kwargs['input_array'][1]
    study_feature = kwargs['input_array'][2]
    output_feature = kwargs['output_array'][0]

    # Define work folder
    work_folder = os.path.split(input_raster)[0]

    # Define intermediate datasets
    processed_feature = os.path.join(work_geodatabase, 'processed_feature')

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

    # Create marine type layer
    print(f'\tCreating marine type layer...')
    iteration_start = time.time()
    # Create marine raster
    print(f'\t\tRemoving terrestrial types...')
    marine_raster = SetNull((Raster(input_raster) != 1) & (Raster(input_raster) != 2) &
                            (Raster(input_raster) != 3), Raster(input_raster))
    # Extend marine raster to study area
    print(f'\t\tExtending coverage of marine types...')
    extend_raster = Nibble(marine_raster, marine_raster, 'DATA_ONLY', 'PROCESS_NODATA')
    # Convert marine raster to polygon
    print(f'\t\tConverting to polygons...')
    arcpy.conversion.RasterToPolygon(extend_raster, processed_feature, 'SIMPLIFY',
                                     'VALUE', 'SINGLE_OUTER_PART')
    # Calculate attribute label field
    label_block = '''def get_label(value, dictionary):
                for label, id in dictionary.items():
                    if value == id:
                        return label'''
    label_expression = f'get_label(!gridcode!, {attribute_dictionary})'
    arcpy.management.AddField(processed_feature, 'label', 'TEXT')
    arcpy.management.CalculateField(processed_feature,
                                    'label',
                                    label_expression,
                                    'PYTHON3',
                                    label_block)
    arcpy.management.DeleteField(processed_feature, ['Id', 'gridcode'], 'DELETE_FIELDS')
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
    if arcpy.Exists(processed_feature) == 1:
        arcpy.management.Delete(processed_feature)

    # Return success message
    out_process = f'Successfully post-processed marine types.'
    return out_process
