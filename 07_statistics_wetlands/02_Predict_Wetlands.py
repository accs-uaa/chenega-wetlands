# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Predict wetlands to points
# Author: Timm Nawrocki
# Last Updated: 2023-02-24
# Usage: Must be executed in an Anaconda Python 3.9+ distribution.
# Description: "Predict wetlands to points" predicts a random forest model to a set of grid csv files containing extracted covariate values to produce a set of output predictions. The script must be run on a machine that can support 4 cores.
# ---------------------------------------------------------------------------

# Import packages
import joblib
import os
import pandas as pd
import time
import datetime

# Import functions from repository statistics package
from package_Statistics import multiclass_predict

# Define round
round_date = 'round_20230223'

# Define number of predicted classes
class_number = 21

#### SET UP DIRECTORIES, FILES, AND FIELDS

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/VegetationEcology/EPA_Chenega/Data')
covariate_folder = os.path.join(data_folder, 'Data_Input/training_data/table_covariate')
response_folder = os.path.join(data_folder, 'Data_Input/training_data/table_training')
model_folder = os.path.join(data_folder, 'Data_Output/model_results', round_date)
output_folder = os.path.join(data_folder, 'Data_Output/predicted_tables', round_date)

# Define input files
classifier_path = os.path.join(model_folder, 'classifier.joblib')

# Define variable sets
class_variable = ['train_class']
predictor_all = ['top_aspect', 'top_elevation', 'top_exposure', 'top_heat_load', 'top_position', 'top_radiation',
                 'top_roughness', 'top_slope', 'top_surface_area', 'top_surface_relief', 'top_wetness',
                 'hyd_coastal',
                 'maxr_01_blue', 'maxr_02_green', 'maxr_03_red', 'maxr_04_nearir', 'maxr_evi2', 'maxr_ndvi', 'maxr_ndwi',
                 'maxr_01_blue_std', 'maxr_02_green_std', 'maxr_03_red_std', 'maxr_04_nearir_std',
                 'maxr_evi2_std', 'maxr_ndvi_std', 'maxr_ndwi_std',
                 'maxr_01_blue_rng', 'maxr_02_green_rng', 'maxr_03_red_rng', 'maxr_04_nearir_rng',
                 'maxr_evi2_rng', 'maxr_ndvi_rng', 'maxr_ndwi_rng',
                 's1_vh_summ', 's1_vv_summ', 's1_vh_fall', 's1_vv_fall', 's1_vh_wint', 's1_vv_wint',
                 'shape_m', 'shape_m2',
                 's2_06_02_blue', 's2_06_03_green', 's2_06_04_red', 's2_06_05_rededge1', 's2_06_06_rededge2',
                 's2_06_07_rededge3', 's2_06_08_nearir', 's2_06_08a_rededge4', 's2_06_11_shortir1', 's2_06_12_shortir2',
                 's2_06_evi2', 's2_06_nbr', 's2_06_ndmi', 's2_06_ndsi', 's2_06_ndvi', 's2_06_ndwi',
                 's2_07_02_blue', 's2_07_03_green', 's2_07_04_red', 's2_07_05_rededge1', 's2_07_06_rededge2',
                 's2_07_07_rededge3', 's2_07_08_nearir', 's2_07_08a_rededge4', 's2_07_11_shortir1', 's2_07_12_shortir2',
                 's2_07_evi2', 's2_07_nbr', 's2_07_ndmi', 's2_07_ndsi', 's2_07_ndvi', 's2_07_ndwi',
                 's2_08_02_blue', 's2_08_03_green', 's2_08_04_red', 's2_08_05_rededge1', 's2_08_06_rededge2',
                 's2_08_07_rededge3', 's2_08_08_nearir', 's2_08_08a_rededge4', 's2_08_11_shortir1', 's2_08_12_shortir2',
                 's2_08_evi2', 's2_08_nbr', 's2_08_ndmi', 's2_08_ndsi', 's2_08_ndvi', 's2_08_ndwi',
                 's2_09_02_blue', 's2_09_03_green', 's2_09_04_red', 's2_09_05_rededge1', 's2_09_06_rededge2',
                 's2_09_07_rededge3', 's2_09_08_nearir', 's2_09_08a_rededge4', 's2_09_11_shortir1', 's2_09_12_shortir2',
                 's2_09_evi2', 's2_09_nbr', 's2_09_ndmi', 's2_09_ndsi', 's2_09_ndvi', 's2_09_ndwi']
retain_variables = ['segment_id', 'POINT_X', 'POINT_Y']
prediction = ['wetland']
output_columns = retain_variables + predictor_all

# Define random state
rstate = 21

# Load model into memory
print('Loading classifier into memory...')
segment_start = time.time()
classifier = joblib.load(classifier_path)
# Report success
segment_end = time.time()
segment_elapsed = int(segment_end - segment_start)
segment_success_time = datetime.datetime.now()
print(
    f'Completed at {segment_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=segment_elapsed)})')
print('----------')

# Define grids
grid_list = ['A1', 'A2',
             'B1', 'B2', 'B3',
             'C1', 'C2', 'C3',
             'D1', 'D2', 'D3']

# Predict each input dataset
count = 1
input_length = len(grid_list)
for grid in grid_list:
    # Define output file
    output_file = os.path.join(output_folder, grid + '.csv')

    # Predict input dataset if output does not already exist
    if os.path.exists(output_file) == 0:
        print(f'Predicting input dataset {count} out of {input_length}...')

        # Load input data
        print('\tLoading input data')
        segment_start = time.time()
        covariate_file = os.path.join(covariate_folder, grid + '.csv')
        response_file = os.path.join(response_folder, grid + '.csv')
        covariate_data = pd.read_csv(covariate_file)
        response_data = pd.read_csv(response_file)
        join_data = response_data.join(covariate_data.set_index('segment_id'), on='segment_id')
        input_data = join_data[retain_variables + class_variable + predictor_all].copy()
        input_data = input_data.fillna(0)
        print(f'\tInput dataset contains {len(input_data)} rows...')
        X_data = input_data[predictor_all].astype(float)
        # Prepare output_data
        output_data = input_data[output_columns]
        # Report success
        segment_end = time.time()
        segment_elapsed = int(segment_end - segment_start)
        segment_success_time = datetime.datetime.now()
        print(
            f'\tCompleted at {segment_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=segment_elapsed)})')
        print('\t----------')

        # Predict data
        print('\tPredicting classes to points...')
        segment_start = time.time()
        output_data = multiclass_predict(classifier, X_data, prediction, class_number, output_data)
        # Report success
        segment_end = time.time()
        segment_elapsed = int(segment_end - segment_start)
        segment_success_time = datetime.datetime.now()
        print(
            f'\tCompleted at {segment_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=segment_elapsed)})')
        print('\t----------')

        # Export output data to csv
        print('\tExporting predictions to csv...')
        segment_start = time.time()
        output_data = output_data.drop(['shape_m', 'shape_m2'], axis=1)
        output_data.to_csv(output_file, header=True, index=False, sep=',', encoding='utf-8')
        # Report success
        segment_end = time.time()
        segment_elapsed = int(segment_end - segment_start)
        segment_success_time = datetime.datetime.now()
        print(
            f'\tCompleted at {segment_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=segment_elapsed)})')
        print('\t----------')

    else:
        # Return message that output already exists
        print(f'Output dataset {count} out of {input_length} already exists.')

    # Increase count
    count += 1
    print('----------')
