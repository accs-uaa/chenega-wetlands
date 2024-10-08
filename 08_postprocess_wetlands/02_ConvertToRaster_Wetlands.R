# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert wetlands predictions to rasters
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2023-06-12
# Usage: Script must be executed using R 4.2.1+.
# Description: "Convert wetlands predictions to rasters" processes the predicted tables into predicted rasters by grid.
# ---------------------------------------------------------------------------

# Define round date and target
round_date = 'round_20230611'

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
project_folder = paste(drive,
                       root_folder,
                       'Projects/VegetationEcology/EPA_Chenega/Data',
                       sep = '/')

# Define folder containing segment rasters
segment_folder = paste(project_folder,
                       'Data_Input/imagery/segments/gridded',
                       sep = '/')

# Define geodatabase storing segment polygons
segment_geodatabase = paste(project_folder,
                            'EPA_Chenega_Segments.gdb',
                            sep = '/')

# Define input folder
prediction_folder = paste(project_folder,
                          'Data_Output/predicted_tables',
                          round_date,
                          sep = '/')
# Define output folder
raster_folder = paste(project_folder,
                      'Data_Output/predicted_rasters',
                      round_date,
                      sep = '/')

# Import libraries
library(dplyr)
library(fasterize)
library(raster)
library(sf)
library(stringr)

# Define grids
grid_list = c('A1', 'A2',
              'B1', 'B2', 'B3',
              'C1', 'C2', 'C3',
              'D1', 'D2', 'D3')
prediction_length = length(grid_list)

#### CONVERT WETLANDS

# Loop through each grid and convert predictions to raster
count = 1
for (grid in grid_list) {
  # Define output folder
  output_folder = paste(raster_folder, sep = '/')
  
  # Define input and output data
  input_file = paste(prediction_folder, '/', grid, '.csv', sep = '')
  segment_file = paste(segment_folder, '/', grid, '.tif', sep = '')
  segment_feature = paste('polygons_', grid, sep = '')
  output_raster = paste(output_folder, '/', grid, '.tif', sep='')
  
  # Process raster if it does not already exist
  if (!file.exists(output_raster)) {
    start = proc.time()
    # Import data
    input_data = read.csv(input_file)
    segment_raster = raster(segment_file)
    segment_polygon = st_read(dsn = segment_geodatabase, layer = segment_feature)
    
    # Bind predicted points to segment polygons and create value field
    segment_predictions = segment_polygon %>%
      dplyr::left_join(input_data, by = 'segment_id')
    
    # Rasterize the polygon
    predicted_raster = fasterize(segment_predictions,
                                 segment_raster,
                                 field = 'wetland',
                                 fun = 'first')
    
    # Export raster
    rf = writeRaster(predicted_raster,
                     filename=output_raster,
                     format="GTiff",
                     overwrite=TRUE)
    end = proc.time() - start
    print(end[3])
    # Print output
    print(paste('Conversion iteration ',
                toString(count),
                ' out of ',
                toString(prediction_length),
                ' completed...',
                sep=''))
    print('----------')
  } else {
    print(paste('Raster ',
                toString(count),
                ' out of ',
                toString(prediction_length),
                ' already exists.',
                sep = ''))
    print('----------')
  }
  count = count + 1
}
