# ---------------------------------------------------------------------------
# Format confusion matrix
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2023-06-11
# Usage: Script should be executed in R 4.1.0+.
# Description: "Format confusion matrix" calculates user's and producer's accuracy.
# ---------------------------------------------------------------------------

# Define version
round_date = 'round_20230611'
n_type = 21

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
  rename(E1AB1L = X1, 
         E1UBL = X2, 
         E2AB1M = X3, 
         E2AB1N = X4, 
         E2RS1N = X5, 
         E2US1N = X6, 
         PAB3H = X7, 
         PEM1D = X8, 
         PEM1E = X9, 
         PFO4B = X10, 
         PSS4B = X11, 
         PUB3H = X12, 
         alpine_dwarf = X13, 
         alpine_barren = X14, 
         alpine_herbaceous = X15, 
         barren_disturbed = X16, 
         coastal_herbaceous = X17, 
         hemlock_spruce = X18, 
         alder_salmonberry = X19, 
         riparian_shrub = X20, 
         subalpine_hemlock = X21) %>%
  mutate(Actual = case_when(Actual == 1 ~ 'E1AB1L',
                            Actual == 2 ~ 'E1UBL',
                            Actual == 3 ~ 'E2AB1M',
                            Actual == 4 ~ 'E2AB1N',
                            Actual == 5 ~ 'E2RS1N',
                            Actual == 6 ~ 'E2US1N',
                            Actual == 7 ~ 'PAB3H',
                            Actual == 8 ~ 'PEM1D',
                            Actual == 9 ~ 'PEM1E',
                            Actual == 10 ~ 'PFO4B',
                            Actual == 11 ~ 'PSS4B',
                            Actual == 12 ~ 'PUB3H',
                            Actual == 13 ~ 'alpine_dwarf',
                            Actual == 14 ~ 'alpine_barren',
                            Actual == 15 ~ 'alpine_herbaceous',
                            Actual == 16 ~ 'barren_disturbed',
                            Actual == 17 ~ 'coastal_herbaceous',
                            Actual == 18 ~ 'hemlock_spruce',
                            Actual == 19 ~ 'alder_salmonberry',
                            Actual == 20 ~ 'riparian_shrub',
                            Actual == 21 ~ 'subalpine_hemlock',
                            TRUE ~ Actual)) %>%
  mutate(acc_producer = 0)

# Calculate user accuracy
count = 1
while (count < (n_type+2)) {
  confusion_matrix[count, (n_type+3)] = round(confusion_matrix[count, count + 1] / confusion_matrix[count, (n_type+2)],
                                      digits = 2)
  count = count + 1
}

# Calculate producers accuracy
confusion_matrix[(n_type+2), 1] = 'acc_user'
count = 2
while (count < (n_type+3)) {
  confusion_matrix[(n_type+2), count] = round(confusion_matrix[count - 1, count] / confusion_matrix[(n_type+1), count],
                                      digits = 2)
  count = count + 1
}

# Export data
write.csv(confusion_matrix, file = output_file, fileEncoding = 'UTF-8', row.names = FALSE)