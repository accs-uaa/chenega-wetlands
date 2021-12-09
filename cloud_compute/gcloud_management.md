# Instructions for Google Cloud Data Management

*Author*: Timm Nawrocki, Alaska Center for Conservation Science

*Last Updated*: 2021-12-09

*Description*: This document contains instructions and commands for moving data between a local machine and a storage bucket on Google Cloud. Cloud storage can be linked to Google Earth Engine (GEE), allowing the ingestion of large datasets into GEE. Data can also be loaded into cloud storage for access by virtual machine processors on Compute Engine. Most of the Google Cloud Compute Engine configuration can be accomplished using the browser interface, which is how configuration steps are explained in this document. If preferred, all of the configuration steps can also be scripted using the Google Cloud SDK. Users should download and install the [Google Cloud SDK](https://cloud.google.com/sdk/) regardless because it is necessary for batch file uploads and downloads.

## 1. Configure project

Create a new project if necessary and enable API access for Google Cloud Compute Engine. Projects on Google Cloud provide a way to organize similar resource needs and should be more general than the specific funded work project. This document uses the "accs-geospatial-processing" project.

Navigate to the Google Cloud Platform APIs & Services menu for the project and enable the Google Earth Engine, Google Drive, and Compute Engine APIs if not already enabled.

### Create a storage bucket for the project

Create a new storage bucket. Select "Multiregional" and make the multiregion the same as your local machine location. Data can be accessed across regions regardless of which "multiregion" is selected. Select "standard" for storage type. If uploading private data, then select the option to enforce public access prevention.

## 2. Data upload and ingestion

Use the "gsutil cp -r" command in Google Cloud SDK to copy data to and from the bucket. Example:

`gsutil cp -r gs://beringia/example/* ~/example/`

We upload an image composite for segmentation:

```
gsutil cp -r F:/ACCS_Work/Projects/VegetationEcology/EPA_Chenega/Data/Data_Input/imagery/maxar/processed/segmentation_imagery.tif gs://chenega-wetlands/gee-assets/
```

Once the data have been uploaded to the Compute storage bucket, they can be ingested in GEE. 