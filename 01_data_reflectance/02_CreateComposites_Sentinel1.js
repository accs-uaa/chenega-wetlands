/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Median Composites Sentinel 1 SAR for 2015-2021
Author: Timm Nawrocki, Alaska Center for Conservation Science
Last Updated: 2023-02-24
Usage: Must be executed from the Google Earth Engine code editor.
Description: This script produces median composites using ascending orbitals for the VV and VH polarizations from Sentinel-1.
---------------------------------------------------------------------------*/

// Define an area of interest geometry.
var area_feature = ee.FeatureCollection('projects/accs-geospatial-processing/assets/chenega_modelarea');

// Import the Sentinel-1 Image Collection VV and VH polarizations within study area and date range
var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(area_feature)
    .filter(ee.Filter.calendarRange(2015, 2021, 'year'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
    .sort('system:time_start');
print("Sentinel 1 (date-filtered:", s1);

// Separate image collections by date
var s1_summer = s1.filter(ee.Filter.calendarRange(6, 8, 'month'))
var s1_fall = s1.filter(ee.Filter.calendarRange(9, 10, 'month'))
var s1_winter = s1.filter(ee.Filter.calendarRange(1, 3, 'month'))

// Create a VV and VH composite from ascending orbits
var vv_summer = s1_summer.select('VV').median()
var vh_summer = s1_summer.select('VH').median()
var vv_fall = s1_fall.select('VV').median()
var vh_fall = s1_fall.select('VH').median()
var vv_winter = s1_winter.select('VV').median()
var vh_winter = s1_winter.select('VH').median()


// Add image to the map.
Map.centerObject(area_feature);
Map.addLayer(vv_summer, {min: -30, max: 0}, 'vv summer');
Map.addLayer(vh_summer, {min: -30, max: 0}, 'vh summer');
Map.addLayer(vv_fall, {min: -30, max: 0}, 'vv fall');
Map.addLayer(vh_fall, {min: -30, max: 0}, 'vh fall');
Map.addLayer(vv_winter, {min: -30, max: 0}, 'vv winter');
Map.addLayer(vh_winter, {min: -30, max: 0}, 'vh winter');

// Add study area to map
var empty = ee.Image().byte();
var outlines = empty.paint({
  featureCollection: area_feature,
  color: 'red',
  width: 2
});
Map.addLayer(outlines, {palette: 'FFFF00'}, 'Study Area');

// Export images to Google Drive.
Export.image.toDrive({
    image: vv_summer,
    description: 'Sent1_vv_summer',
    folder: 'chenega_sentinel1',
    scale: 10,
    crs: 'EPSG:3338',
    region: area_feature,
    maxPixels: 1e12
});
Export.image.toDrive({
    image: vh_summer,
    description: 'Sent1_vh_summer',
    folder: 'chenega_sentinel1',
    scale: 10,
    crs: 'EPSG:3338',
    region: area_feature,
    maxPixels: 1e12
});
Export.image.toDrive({
    image: vv_fall,
    description: 'Sent1_vv_fall',
    folder: 'chenega_sentinel1',
    scale: 10,
    crs: 'EPSG:3338',
    region: area_feature,
    maxPixels: 1e12
});
Export.image.toDrive({
    image: vh_fall,
    description: 'Sent1_vh_fall',
    folder: 'chenega_sentinel1',
    scale: 10,
    crs: 'EPSG:3338',
    region: area_feature,
    maxPixels: 1e12
});
Export.image.toDrive({
    image: vv_winter,
    description: 'Sent1_vv_winter',
    folder: 'chenega_sentinel1',
    scale: 10,
    crs: 'EPSG:3338',
    region: area_feature,
    maxPixels: 1e12
});
Export.image.toDrive({
    image: vh_winter,
    description: 'Sent1_vh_winter',
    folder: 'chenega_sentinel1',
    scale: 10,
    crs: 'EPSG:3338',
    region: area_feature,
    maxPixels: 1e12
});
