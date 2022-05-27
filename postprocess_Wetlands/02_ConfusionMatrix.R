# ---------------------------------------------------------------------------
# Format confusion matrix
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2022-05-27
# Usage: Script should be executed in R 4.1.0+.
# Description: "Format confusion matrix" calculates user's and producer's accuracy.
# ---------------------------------------------------------------------------

# Define version
round_date = 'round_20220526'

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
         I2EM = X5, I2RS = X6, I2US = X7, PEM = X8, PFOSS = X9,
         PML = X10, PRB = X11, PSS = X12, R = X13, UPL = X14) %>%
  mutate(Actual = case_when(Actual == 1 ~ 'D1',
                            Actual == 2 ~ 'FAB',
                            Actual == 3 ~ 'FUB',
                            Actual == 4 ~ 'I2AB',
                            Actual == 5 ~ 'I2EM',
                            Actual == 6 ~ 'I2RS',
                            Actual == 7 ~ 'I2US',
                            Actual == 8 ~ 'PEM',
                            Actual == 9 ~ 'PFOSS',
                            Actual == 10 ~ 'PML',
                            Actual == 11 ~ 'PRB',
                            Actual == 12 ~ 'PSS',
                            Actual == 13 ~ 'R',
                            Actual == 14 ~ 'UPL',
                            TRUE ~ Actual)) %>%
  mutate(acc_producer = 0)

# Calculate user accuracy
count = 1
while (count < 15) {
  confusion_matrix[count, 17] = round(confusion_matrix[count, count + 1] / confusion_matrix[count, 16],
                                      digits = 2)
  count = count + 1
}

# Calculate producers accuracy
confusion_matrix[16, 1] = 'acc_user'
count = 2
while (count < 16) {
  confusion_matrix[16, count] = round(confusion_matrix[count - 1, count] / confusion_matrix[15, count],
                                      digits = 2)
  count = count + 1
}

# Export data
write.csv(confusion_matrix, file = output_file, fileEncoding = 'UTF-8', row.names = FALSE)