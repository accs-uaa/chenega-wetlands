# ---------------------------------------------------------------------------
# Format confusion matrix
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2022-10-09
# Usage: Script should be executed in R 4.1.0+.
# Description: "Format confusion matrix" calculates user's and producer's accuracy.
# ---------------------------------------------------------------------------

# Define version
round_date = 'round_20221009'
class_number = 11

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input data
data_folder = paste(drive,
                    root_folder,
                    'Projects/VegetationEcology/EPA_Chenega/Data',
                    sep = '/')
raw_file = paste(data_folder,
                        'Data_Output/model_results',
                        round_date,
                        'confusion_matrix_raw.csv',
                        sep = '/')

# Define output files
output_file = paste(data_folder,
                    'Data_Output/model_results',
                    round_date,
                    'confusion_matrix.csv',
                    sep = '/')

# Import libraries
library(dplyr)
library(tidyr)

# Import data to data frame
raw_data = read.csv(raw_file)

# Change column and row labels
confusion_matrix = raw_data %>%
  rename(D1 = X1, FAB = X2, FUB = X3, I2AB = X4,
         I2EM = X5, I2RS = X6, I2US = X7, PEM1B = X8, PEM1C = X9,
         PFOSS = X10, UPL = X11) %>%
  mutate(Actual = case_when(Actual == 1 ~ 'D1',
                            Actual == 2 ~ 'FAB',
                            Actual == 3 ~ 'FUB',
                            Actual == 4 ~ 'I2AB',
                            Actual == 5 ~ 'I2EM',
                            Actual == 6 ~ 'I2RS',
                            Actual == 7 ~ 'I2US',
                            Actual == 8 ~ 'PEM1B',
                            Actual == 9 ~ 'PEM1C',
                            Actual == 10 ~ 'PFOSS',
                            Actual == 11 ~ 'UPL',
                            TRUE ~ Actual)) %>%
  mutate(acc_producer = 0)

# Calculate user accuracy
count = 1
while (count < class_number + 1) {
  confusion_matrix[count, class_number + 3] = round(confusion_matrix[count, count + 1]
                                                    / confusion_matrix[count, class_number + 2],
                                      digits = 2)
  count = count + 1
}

# Calculate producers accuracy
confusion_matrix[class_number + 2, 1] = 'acc_user'
count = 2
while (count < class_number + 2) {
  confusion_matrix[class_number + 2, count] = round(confusion_matrix[count - 1, count]
                                                    / confusion_matrix[class_number + 1, count],
                                      digits = 2)
  count = count + 1
}

# Export data
write.csv(confusion_matrix, file = output_file, fileEncoding = 'UTF-8', row.names = FALSE)