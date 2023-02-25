# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract covariates to points
# Author: Timm Nawrocki
# Last Updated: 2023-02-24
# Usage: Must be executed in R 4.0.0+.
# Description: "Extract covariates to points" extracts data from rasters to points.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
project_folder = paste(drive,
                       root_folder,
                       'Projects/VegetationEcology/EPA_Chenega/Data',
                       sep = '/')
training_folder = paste(project_folder,
                        'Data_Input/training_data',
                        sep = '/')
zonal_folder = paste(project_folder,
                     'Data_Input/zonal',
                     sep = '/')

# Define output folders
output_folder = paste(training_folder,
                      'table_covariate',
                      sep = '/')

# Define segments geodatabase
segments_geodatabase = paste(project_folder,
                             'EPA_Chenega_Segments.gdb',
                             sep = '/')

# Define grids
grid_list = c('A1', 'A2',
              'B1', 'B2', 'B3',
              'C1', 'C2', 'C3',
              'D1', 'D2', 'D3')
grid_length = length(grid_list)

# Import libraries
library(dplyr)
library(raster)
library(sf)
library(stringr)

# Set count
count = 1

# Loop through each grid and extract covariates
for (grid in grid_list) {
  # Define input points
  input_points = paste('points_', grid, sep = '')
  
  # Define output table
  output_file = paste(output_folder, '/', grid, '.csv', sep = '')
  
  # Define zonal data
  zonal_data = paste(zonal_folder, grid, sep = '/')
  
  # Create output table if it does not already exist
  if (!file.exists(output_file)) {
    print(paste('Extracting segments ', toString(count), ' out of ',
                toString(grid_length), '...', sep=''))
    
    # Create a list of zonal predictor rasters
    predictors_zonal = list.files(zonal_data, pattern = 'tif$', full.names = TRUE)
    print(paste('Number of predictor rasters: ', length(predictors_zonal), sep = ''))
    
    # Generate a stack of zonal predictor rasters
    print('Creating zonal raster stack...')
    start = proc.time()
    predictor_stack = stack(predictors_zonal)
    end = proc.time() - start
    print(end[3])
    
    # Read path data and extract covariates
    print('Extracting covariates...')
    start = proc.time()
    print(input_points)
    point_data = st_read(dsn = segments_geodatabase, layer = input_points)
    point_zonal = data.frame(point_data, raster::extract(predictor_stack, point_data))
    end = proc.time() - start
    print(end[3])
    
    # Convert field names to standard
    point_zonal = point_zonal %>%
      dplyr::rename(top_aspect = Aspect,
                    top_elevation = Elevation,
                    top_exposure = Exposure,
                    top_heat_load = HeatLoad,
                    top_position = Position,
                    top_radiation = Radiation,
                    top_roughness = Roughness,
                    top_slope = Slope,
                    top_surface_area = SurfaceArea,
                    top_surface_relief = SurfaceRelief,
                    top_wetness = Wetness,
                    hyd_coastal = Chenega_Coastal_Distance,
                    maxr_01_blue = Chenega_Maxar_01_Blue,
                    maxr_01_blue_std = Chenega_Maxar_01_Blue_STD,
                    maxr_01_blue_rng = Chenega_Maxar_01_Blue_RNG,
                    maxr_02_green = Chenega_Maxar_02_Green,
                    maxr_02_green_std = Chenega_Maxar_02_Green_STD,
                    maxr_02_green_rng = Chenega_Maxar_02_Green_RNG,
                    maxr_03_red = Chenega_Maxar_03_Red,
                    maxr_03_red_std = Chenega_Maxar_03_Red_STD,
                    maxr_03_red_rng = Chenega_Maxar_03_Red_RNG,
                    maxr_04_nearir = Chenega_Maxar_04_NearIR,
                    maxr_04_nearir_std = Chenega_Maxar_04_nearir_STD,
                    maxr_04_nearir_rng = Chenega_Maxar_04_nearir_RNG,
                    maxr_evi2 = Chenega_Maxar_EVI2,
                    maxr_evi2_std = Chenega_Maxar_EVI2_STD,
                    maxr_evi2_rng = Chenega_Maxar_EVI2_RNG,
                    maxr_ndvi = Chenega_Maxar_NDVI,
                    maxr_ndvi_std = Chenega_Maxar_NDVI_STD,
                    maxr_ndvi_rng = Chenega_Maxar_NDVI_RNG,
                    maxr_ndwi = Chenega_Maxar_NDWI,
                    maxr_ndwi_std = Chenega_Maxar_NDWI_STD,
                    maxr_ndwi_rng = Chenega_Maxar_NDWI_RNG,
                    s1_vh_summ = Sent1_vh_summer,
                    s1_vv_summ = Sent1_vv_summer,
                    s1_vh_fall = Sent1_vh_fall,
                    s1_vv_fall = Sent1_vv_fall,
                    s1_vh_wint = Sent1_vh_winter,
                    s1_vv_wint = Sent1_vv_winter,
                    s2_06_02_blue = Sent2_06_2_blue,
                    s2_06_03_green = Sent2_06_3_green,
                    s2_06_04_red = Sent2_06_4_red,
                    s2_06_05_rededge1 = Sent2_06_5_redEdge1,
                    s2_06_06_rededge2 = Sent2_06_6_redEdge2,
                    s2_06_07_rededge3 = Sent2_06_7_redEdge3,
                    s2_06_08_nearir = Sent2_06_8_nearInfrared,
                    s2_06_08a_rededge4 = Sent2_06_8a_redEdge4,
                    s2_06_11_shortir1 = Sent2_06_11_shortInfrared1,
                    s2_06_12_shortir2 = Sent2_06_12_shortInfrared2,
                    s2_06_evi2 = Sent2_06_evi2,
                    s2_06_nbr = Sent2_06_nbr,
                    s2_06_ndmi = Sent2_06_ndmi,
                    s2_06_ndsi = Sent2_06_ndsi,
                    s2_06_ndvi = Sent2_06_ndvi,
                    s2_06_ndwi = Sent2_06_ndwi,
                    s2_07_02_blue = Sent2_07_2_blue,
                    s2_07_03_green = Sent2_07_3_green,
                    s2_07_04_red = Sent2_07_4_red,
                    s2_07_05_rededge1 = Sent2_07_5_redEdge1,
                    s2_07_06_rededge2 = Sent2_07_6_redEdge2,
                    s2_07_07_rededge3 = Sent2_07_7_redEdge3,
                    s2_07_08_nearir = Sent2_07_8_nearInfrared,
                    s2_07_08a_rededge4 = Sent2_07_8a_redEdge4,
                    s2_07_11_shortir1 = Sent2_07_11_shortInfrared1,
                    s2_07_12_shortir2 = Sent2_07_12_shortInfrared2,
                    s2_07_evi2 = Sent2_07_evi2,
                    s2_07_nbr = Sent2_07_nbr,
                    s2_07_ndmi = Sent2_07_ndmi,
                    s2_07_ndsi = Sent2_07_ndsi,
                    s2_07_ndvi = Sent2_07_ndvi,
                    s2_07_ndwi = Sent2_07_ndwi,
                    s2_08_02_blue = Sent2_08_2_blue,
                    s2_08_03_green = Sent2_08_3_green,
                    s2_08_04_red = Sent2_08_4_red,
                    s2_08_05_rededge1 = Sent2_08_5_redEdge1,
                    s2_08_06_rededge2 = Sent2_08_6_redEdge2,
                    s2_08_07_rededge3 = Sent2_08_7_redEdge3,
                    s2_08_08_nearir = Sent2_08_8_nearInfrared,
                    s2_08_08a_rededge4 = Sent2_08_8a_redEdge4,
                    s2_08_11_shortir1 = Sent2_08_11_shortInfrared1,
                    s2_08_12_shortir2 = Sent2_08_12_shortInfrared2,
                    s2_08_evi2 = Sent2_08_evi2,
                    s2_08_nbr = Sent2_08_nbr,
                    s2_08_ndmi = Sent2_08_ndmi,
                    s2_08_ndsi = Sent2_08_ndsi,
                    s2_08_ndvi = Sent2_08_ndvi,
                    s2_08_ndwi = Sent2_08_ndwi,
                    s2_09_02_blue = Sent2_09_2_blue,
                    s2_09_03_green = Sent2_09_3_green,
                    s2_09_04_red = Sent2_09_4_red,
                    s2_09_05_rededge1 = Sent2_09_5_redEdge1,
                    s2_09_06_rededge2 = Sent2_09_6_redEdge2,
                    s2_09_07_rededge3 = Sent2_09_7_redEdge3,
                    s2_09_08_nearir = Sent2_09_8_nearInfrared,
                    s2_09_08a_rededge4 = Sent2_09_8a_redEdge4,
                    s2_09_11_shortir1 = Sent2_09_11_shortInfrared1,
                    s2_09_12_shortir2 = Sent2_09_12_shortInfrared2,
                    s2_09_evi2 = Sent2_09_evi2,
                    s2_09_nbr = Sent2_09_nbr,
                    s2_09_ndmi = Sent2_09_ndmi,
                    s2_09_ndsi = Sent2_09_ndsi,
                    s2_09_ndvi = Sent2_09_ndvi,
                    s2_09_ndwi = Sent2_09_ndwi)
    
    # Export data as a csv
    st_write(point_zonal, output_file, coords = FALSE)
    print(paste('Extraction iteration ', toString(count), ' out of ', toString(grid_length), ' completed.', sep=''))
    print('----------')
  } else {
    # Report that output already exists
    print(paste('Extraction ', toString(count), ' out of ', toString(grid_length), ' already exists.', sep = ''))
    print('----------')
  }
  # Increase count
  count = count + 1
}
