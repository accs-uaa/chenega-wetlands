# ---------------------------------------------------------------------------
# Format confusion matrix
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2023-02-24
# Usage: Script should be executed in R 4.1.0+.
# Description: "Format confusion matrix" calculates user's and producer's accuracy.
# ---------------------------------------------------------------------------

# Define version
round_date = 'round_20230223'
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
         E2AB1 = X3, 
         E2EM1P = X4, 
         E2RS = X5, 
         E2US = X6, 
         PAB3H = X7, 
         PEM1D = X8, 
         PEM1E = X9, 
         PFO4B = X10, 
         PSS4B = X11, 
         PUB = X12, 
         alpine_dwarf = X13, 
         alpine_barren = X14, 
         alpine_herbaceous = X15, 
         barren_disturbed = X16, 
         coastal_herbaceous = X17, 
         hemlock_spruce = X18, 
         alder_salmonberry = X19, 
         riparian_willow = X20, 
         subalpine_hemlock = X21) %>%
  mutate(Actual = case_when(Actual == 1 ~ 'E1AB1L',
                            Actual == 2 ~ 'E1UBL',
                            Actual == 3 ~ 'E2AB1',
                            Actual == 4 ~ 'E2EM1P',
                            Actual == 5 ~ 'E2RS',
                            Actual == 6 ~ 'E2US',
                            Actual == 7 ~ 'PAB3H',
                            Actual == 8 ~ 'PEM1D',
                            Actual == 9 ~ 'PEM1E',
                            Actual == 10 ~ 'PFO4B',
                            Actual == 11 ~ 'PSS4B',
                            Actual == 12 ~ 'PUB',
                            Actual == 13 ~ 'alpine dwarf shrub',
                            Actual == 14 ~ 'alpine sparse/barren',
                            Actual == 15 ~ 'alpine-subalpine herbaceous',
                            Actual == 16 ~ 'barren disturbed',
                            Actual == 17 ~ 'coastal herbaceous',
                            Actual == 18 ~ 'mountain hemlock - Sitka spruce',
                            Actual == 19 ~ 'Sitka alder - salmonberry',
                            Actual == 20 ~ 'Sitka Willow - Barclay Willow Riparian Shrub',
                            Actual == 21 ~ 'subalpine mountain hemlock woodland',
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