# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download Sentinel-2 Data from Drive
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in a Python 3.8 installation with Google API Python Client and PyDrive installed.
# Description: "Download Sentinel-2 Data from Drive" programmatically downloads Sentinel-2 tiles from a Google Drive folder. The composites must first be calculated in Google Earth Engine and exported to the Google Drive folder.
# ---------------------------------------------------------------------------

# Import packages
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from package_GeospatialProcessing import download_from_drive
from package_GeospatialProcessing import list_from_drive
import pickle
import time

# Define target Google Drive folder
google_folder = '1xlcOh2TVQw_wMvsrk8r08xTxk5BfT-_4'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Set data folder
data_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/EPA_Chenega/Data/Data_Input/imagery/sentinel-2/unprocessed')
credentials_folder = os.path.join(drive, root_folder, 'Administrative/Credentials')

# Change working directory to credentials folder
os.chdir(credentials_folder)

# Set scopes
scopes = ['https://www.googleapis.com/auth/drive']

# Reiterate download process until manually stopped in case errors occur in individual downloads
reiterate = True
while reiterate == True:
    # Create persistent credentials
    credentials = None

    # Create file token.pickle to store the user's access and refresh tokens.
    if os.path.exists('token.pickle') == 1:
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', scopes)
            credentials = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    # Build a Google Drive instance
    drive_service = build('drive', 'v2', credentials=credentials)
    print('Refresh token active:')
    print(credentials.refresh_token)
    print('----------')

    # List all files in Google Drive Folder
    file_id_list = list_from_drive(drive_service, google_folder)

    # Subset list
    file_id_subset = file_id_list[0:]
    total = len(file_id_subset)

    # Download all files in Google Drive Folder
    count = 1
    for file_id in file_id_subset:
        # Refresh the access token
        credentials.refresh(Request())

        # Get file title metadata by file id
        file_meta = drive_service.files().get(fileId=file_id).execute()
        file_title = file_meta['title']

        # Generate download file path
        output_file = os.path.join(data_folder, file_title)

        # Start download file iteration if file does not exist.
        if os.path.exists(output_file) == 0:
            try:
                # Start timing function
                iteration_start = time.time()
                # Download file
                print(f'Downloading file {count} of {total}...')
                download_from_drive(drive_service, file_id, file_title, output_file)
                # End timing
                iteration_end = time.time()
                iteration_elapsed = int(iteration_end - iteration_start)
                iteration_success_time = datetime.datetime.now()
                # Report success
                print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
                print('\t----------')
            except:
                print('Download error occurred.')

        # If file exists then skip download file iteration
        else:
            print(f'File {count} of {total} already exists...')

        # Increase count
        count += 1
