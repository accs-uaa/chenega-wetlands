# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate Topographic Properties
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate Topographic Properties" is a function that calculates multiple integer topographic properties from a float elevation raster.
# ---------------------------------------------------------------------------

# Define a function to calculate topographic properties.
def calculate_topographic_properties(**kwargs):
    """
    Description: calculates integer topographic properties from a float elevation raster
    Inputs: 'z_unit' -- a string value of either 'Meter' or 'Foot' representing the vertical unit of the elevation raster
            'position_width' -- an integer value of the distance to consider for topographic position in the same units as the input raster
            'input_array' -- an array containing the grid raster (must be first) and the float elevation raster
            'output_array' -- an array containing the output rasters for elevation (integer), slope, aspect, exposure, heat load, position, radiation, roughness, surface area, surface relief, wetness (in that order).
    Returned Value: Returns a raster dataset on disk for each topographic property
    Preconditions: requires an input DEM that can be created through other scripts in this repository
    """

    # Import packages
    import arcpy
    from arcpy.sa import Raster
    from package_Geomorphometry import calculate_aspect
    from package_Geomorphometry import calculate_exposure
    from package_Geomorphometry import calculate_flow
    from package_Geomorphometry import calculate_heat_load
    from package_Geomorphometry import calculate_integer_elevation
    from package_Geomorphometry import calculate_position
    from package_Geomorphometry import calculate_radiation
    from package_Geomorphometry import calculate_roughness
    from package_Geomorphometry import calculate_slope
    from package_Geomorphometry import calculate_surface_area
    from package_Geomorphometry import calculate_surface_relief
    from package_Geomorphometry import calculate_wetness
    import datetime
    import os
    import time

    # Parse key word argument inputs
    z_unit = kwargs['z_unit']
    position_width = kwargs['position_width']
    area_raster = kwargs['input_array'][0]
    elevation_float = kwargs['input_array'][1]
    elevation_integer = kwargs['output_array'][0]
    slope_integer = kwargs['output_array'][1]
    aspect_output = kwargs['output_array'][2]
    exposure_output = kwargs['output_array'][3]
    heatload_output = kwargs['output_array'][4]
    position_output = kwargs['output_array'][5]
    radiation_output = kwargs['output_array'][6]
    roughness_output = kwargs['output_array'][7]
    surfacearea_output = kwargs['output_array'][8]
    surfacerelief_output = kwargs['output_array'][9]
    wetness_output = kwargs['output_array'][10]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "75%"

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Define folder structure
    float_folder = os.path.split(elevation_float)[0]

    # Define intermediate datasets
    flow_accumulation = os.path.join(float_folder, 'Flow_Accumulation.tif')
    slope_float = os.path.join(float_folder, 'Slope.tif')
    aspect_raw = os.path.join(float_folder, 'Aspect.tif')

    #### CALCULATE FOUNDATIONAL TOPOGRAPHY DATASETS

    # Calculate integer elevation if it does not already exist
    if arcpy.Exists(elevation_integer) == 0:
        print(f'\tCalculating integer elevation...')
        iteration_start = time.time()
        calculate_integer_elevation(elevation_float, elevation_integer)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tInteger elevation already exists.')
        print('\t----------')

    # Calculate slope in degrees if it does not already exist
    if os.path.exists(slope_integer) == 0:
        # Calculate slope
        print(f'\tCalculating slope...')
        iteration_start = time.time()
        calculate_slope(elevation_float, z_unit, slope_float, slope_integer)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tRaw slope already exists.')
        print('\t----------')

    # Calculate aspect if it does not already exist
    if os.path.exists(aspect_output) == 0:
        # Calculate aspect
        print(f'\tCalculating aspect...')
        iteration_start = time.time()
        calculate_aspect(elevation_float, z_unit, aspect_raw, aspect_output)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tAspect already exists.')
        print('\t----------')

    # Calculate flow accumulation if it does not already exist
    if arcpy.Exists(flow_accumulation) == 0:
        # Calculate flow direction
        print(f'\tCalculating flow direction...')
        iteration_start = time.time()
        calculate_flow(elevation_float, flow_accumulation)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tFlow direction already exists.')
        print('\t----------')

    #### CALCULATE DERIVED TOPOGRAPHY DATASETS

    # Calculate solar exposure index if it does not already exist
    if arcpy.Exists(exposure_output) == 0:
        print(f'\tCalculating solar exposure...')
        iteration_start = time.time()
        calculate_exposure(aspect_raw, slope_float, 10, exposure_output)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tSite exposure already exists.')
        print('\t----------')

    # Calculate heat load index if it does not already exist
    if arcpy.Exists(heatload_output) == 0:
        print('\tCalculating heat load index...')
        iteration_start = time.time()
        calculate_heat_load(elevation_float, slope_float, aspect_raw, 10, heatload_output)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tHeat load index already exists.')
        print('\t----------')

    # Calculate topographic position if it does not already exist
    if arcpy.Exists(position_output) == 0:
        print(f'\tCalculating topographic position...')
        iteration_start = time.time()
        calculate_position(elevation_float, position_width, position_output)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tTopographic position already exists.')
        print('\t----------')

    # Calculate topographic radiation if it does not already exist
    if arcpy.Exists(radiation_output) == 0:
        print(f'\tCalculating topographic radiation...')
        iteration_start = time.time()
        calculate_radiation(aspect_raw, 1000, radiation_output)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tTopographic radiation already exists.')
        print('\t----------')

    # Calculate roughness if it does not already exist
    if arcpy.Exists(roughness_output) == 0:
        print(f'\tCalculating roughness...')
        iteration_start = time.time()
        calculate_roughness(elevation_float, 10, roughness_output)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tRoughness already exists.')
        print('\t----------')

    # Calculate surface area ratio if it does not already exist
    if os.path.exists(surfacearea_output) == 0:
        print(f'\tCalculating surface area ratio...')
        iteration_start = time.time()
        calculate_surface_area(slope_float, 10, surfacearea_output)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tSurface area ratio already exists.')
        print('\t----------')

    # Calculate surface relief ratio if it does not already exist
    if arcpy.Exists(surfacerelief_output) == 0:
        print(f'\tCalculating surface relief ratio...')
        iteration_start = time.time()
        calculate_surface_relief(elevation_float, 1000, surfacerelief_output)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tSurface relief ratio already exists.')
        print('\t----------')

    # Calculate topographic wetness if it does not already exist
    if arcpy.Exists(wetness_output) == 0:
        print(f'\tCalculating topographic wetness...')
        iteration_start = time.time()
        calculate_wetness(elevation_float, flow_accumulation, slope_float, 100, wetness_output)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tTopographic wetness already exists.')
        print('\t----------')

    outprocess = f'Finished calculating topographic properties.'
    return outprocess
