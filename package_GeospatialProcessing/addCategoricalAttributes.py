# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Add categorical attributes
# Author: Timm Nawrocki
# Last Updated: 2023-02-24
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Add categorical attributes" is a function that builds a raster attribute table.
# ---------------------------------------------------------------------------

# Define a function to add categorical raster attributes
def add_categorical_attributes(**kwargs):
    """
    Description: adds attributes to each value in a categorical raster based on a dictionary
    Inputs: 'attribute_dictionary' -- a dictionary of name and value pairs for the map schema
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the area raster (must be first), the predicted raster, and the segments feature class
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster to disk
    Preconditions: requires a predicted categorical raster
    """

    # Import packages
    from akutils import get_attribute_code_block
    import arcpy
    from arcpy.sa import Raster
    import datetime
    import time

    # Parse key word argument inputs
    attribute_dictionary = kwargs['attribute_dictionary']
    work_geodatabase = kwargs['work_geodatabase']
    area_input = kwargs['input_array'][0]
    wetlands_input = kwargs['input_array'][1]
    wetlands_output = kwargs['output_array'][0]

    # Define code block
    code_block = get_attribute_code_block()

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set snap raster and extent
    arcpy.env.snapRaster = area_input
    arcpy.env.extent = Raster(area_input).extent

    # Set output coordinate system
    arcpy.env.outputCoordinateSystem = Raster(area_input)

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(area_input, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Generalize raster results
    iteration_start = time.time()
    # Copy raster to integer
    print('\tConverting input raster to integers...')
    arcpy.management.CopyRaster(wetlands_input,
                                wetlands_output,
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
    print('\tCalculating statistics...')
    arcpy.management.CalculateStatistics(wetlands_output)
    print('\tBuilding pyramids...')
    arcpy.management.BuildPyramids(wetlands_output, -1, 'NONE', 'NEAREST',
                                   'LZ77', '', 'OVERWRITE')
    print('\tAdding raster attributes...')
    arcpy.management.BuildRasterAttributeTable(wetlands_output, 'Overwrite')
    # Calculate attribute label field
    expression = f'get_response(!VALUE!, {attribute_dictionary}, "value")'
    arcpy.management.CalculateField(wetlands_output,
                                    'label',
                                    expression,
                                    'PYTHON3',
                                    code_block)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Return success message
    out_process = f'Successfully post-processed categorical raster.'
    return out_process
