# ---------------------------------------------------------------------------
# Format confusion matrix
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2023-02-24
# Usage: Script should be executed in R 4.1.0+.
# Description: "Format confusion matrix" calculates user's and producer's accuracy.
# ---------------------------------------------------------------------------

# Define version
round_date = 'round_20230223'
n_type = 23

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
         E2RS1 = X5, 
         E2RS2 = X6, 
         E2US = X7, 
         L1UB3H = X8, 
         PAB3H = X9, 
         PEM1D = X10, 
         PEM1E = X11, 
         PFO4B = X12, 
         PSS4B = X13, 
         PUB = X14, 
         alpine_dwarf = X15, 
         alpine_barren = X16, 
         alpine_herbaceous = X17, 
         barren_disturbed = X18, 
         coastal_herbaceous = X19, 
         hemlock_spruce = X20, 
         alder_salmonberry = X21, 
         riparian_willow = X22, 
         subalpine_hemlock = X23) %>%
  mutate(Actual = case_when(Actual == 1 ~ 'E1AB1L',
                            Actual == 2 ~ 'E1UBL',
                            Actual == 3 ~ 'E2AB1',
                            Actual == 4 ~ 'E2EM1P',
                            Actual == 5 ~ 'E2RS1',
                            Actual == 6 ~ 'E2RS2',
                            Actual == 7 ~ 'E2US',
                            Actual == 8 ~ 'L1UB3H',
                            Actual == 9 ~ 'PAB3H',
                            Actual == 10 ~ 'PEM1D',
                            Actual == 11 ~ 'PEM1E',
                            Actual == 12 ~ 'PFO4B',
                            Actual == 13 ~ 'PSS4B',
                            Actual == 14 ~ 'PUB',
                            Actual == 15 ~ 'alpine dwarf shrub',
                            Actual == 16 ~ 'alpine sparse/barren',
                            Actual == 17 ~ 'alpine-subalpine herbaceous',
                            Actual == 18 ~ 'barren disturbed',
                            Actual == 19 ~ 'coastal herbaceous',
                            Actual == 20 ~ 'mountain hemlock - Sitka spruce',
                            Actual == 21 ~ 'Sitka alder - salmonberry',
                            Actual == 22 ~ 'Sitka Willow - Barclay Willow Riparian Shrub',
                            Actual == 23 ~ 'subalpine mountain hemlock woodland',
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