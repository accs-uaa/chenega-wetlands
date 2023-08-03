# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Smooth wetlands
# Author: Timm Nawrocki
# Last Updated: 2023-08-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Smooth wetlands" is a function that smooths marine, terrestrial, and waterbody types and combines them into a single polygon map.
# ---------------------------------------------------------------------------

# Define a function to smooth wetlands
def smooth_wetlands(**kwargs):
    """
    Description: smooths and combines wetland types
    Inputs: 'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the marine features, terrestrial features, and waterbody features (in that order)
            'output_array' -- an array containing the output feature class
    Returned Value: Returns a feature class to disk
    Preconditions: requires post-processed feature classes
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    marine_feature = kwargs['input_array'][0]
    terrestrial_feature = kwargs['input_array'][1]
    waterbody_feature = kwargs['input_array'][2]
    output_feature = kwargs['output_array'][0]

    # Define intermediate datasets
    marine_smoothed = os.path.join(work_geodatabase, 'marine_smoothed')
    terrestrial_smoothed = os.path.join(work_geodatabase, 'terrestrial_smoothed')
    waterbody_smoothed = os.path.join(work_geodatabase, 'waterbody_smoothed')
    marine_erase = os.path.join(work_geodatabase, 'marine_erase')
    terrestrial_erase = os.path.join(work_geodatabase, 'terrestrial_erase')

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = '0'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set output coordinate system
    arcpy.env.outputCoordinateSystem = waterbody_feature

    # Smooth features
    print(f'\tSmoothing wetland features...')
    iteration_start = time.time()
    # Smooth marine features
    print('\t\tSmoothing marine water types...')
    arcpy.management.CopyFeatures(marine_feature, marine_smoothed)
    arcpy.cartography.SmoothSharedEdges(marine_smoothed, 'PAEK', '250 Meters')
    # Smooth terrestrial types
    print('\t\tSmoothing terrestrial and coastal types...')
    arcpy.management.CopyFeatures(terrestrial_feature, terrestrial_smoothed)
    arcpy.cartography.SmoothSharedEdges(terrestrial_smoothed, 'PAEK', '20 Meters')
    # Smooth waterbodies
    print('\t\tSmoothing waterbodies...')
    arcpy.management.CopyFeatures(waterbody_feature, waterbody_smoothed)
    arcpy.cartography.SmoothSharedEdges(waterbody_smoothed, 'PAEK', '10 Meters')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Combine features to output map
    print('\tCombining features to output map...')
    iteration_start = time.time()
    # Erase terrestrial feature from marine feature
    print('\t\tErasing terrestrial features from marine features...')
    arcpy.analysis.PairwiseErase(marine_smoothed, terrestrial_smoothed, marine_erase)
    # Erase waterbodies from terrestrial features
    print('\t\tErasing waterbodies from terrestrial features...')
    arcpy.analysis.PairwiseErase(terrestrial_smoothed, waterbody_smoothed, terrestrial_erase)
    # Merge features
    print('\t\tMerging features...')
    arcpy.management.Merge([marine_erase, terrestrial_erase, waterbody_smoothed], output_feature)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Delete intermediate datasets
    if arcpy.Exists(marine_smoothed) == 1:
        arcpy.management.Delete(marine_smoothed)
    if arcpy.Exists(terrestrial_smoothed) == 1:
        arcpy.management.Delete(terrestrial_smoothed)
    if arcpy.Exists(waterbody_smoothed) == 1:
        arcpy.management.Delete(waterbody_smoothed)
    if arcpy.Exists(marine_erase) == 1:
        arcpy.management.Delete(marine_erase)
    if arcpy.Exists(terrestrial_erase) == 1:
        arcpy.management.Delete(terrestrial_erase)

    # Return success message
    out_process = f'Successfully created smoothed wetlands feature class.'
    return out_process
