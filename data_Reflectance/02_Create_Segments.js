/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Image segments from simple non-iterative clustering
Author: Timm Nawrocki, Alaska Center for Conservation Science
Last Updated: 2022-01-01
Usage: Must be executed from the Google Earth Engine code editor.
Description: "Image clusters from simple non-iterative clustering" produces image segments and summarized bands from a raster asset.
---------------------------------------------------------------------------*/

// 1. SETUP ANALYSIS

// Import assets
var segmentation_image = ee.Image('projects/accs-geospatial-processing/assets/chenega_imagery');
var area_feature = ee.FeatureCollection('projects/accs-geospatial-processing/assets/chenega_modelarea');

// Add image asset to map
var rgbVis = {
  min: 100,
  max: 1600,
  bands: ['b3', 'b2', 'b1']
};
Map.addLayer(segmentation_image, rgbVis, 'Segmentation Composite');
Map.centerObject(area_feature);

// Add study area to map
var empty = ee.Image().byte();
var outlines = empty.paint({
  featureCollection: area_feature,
  color: 'red',
  width: 2
});
Map.addLayer(outlines, {palette: 'FFFF00'}, 'Study Area');

// 2. DEFINE FUNCTIONS

// Define a function for EVI-2 calculation.
function add_EVI2(image) {
  // Assign variables to the red and green Sentinel-2 bands.
  var red = image.select('b3');
  var green = image.select('b2');
  //Compute the Enhanced Vegetation Index-2 (EVI2).
  var evi2_calc = red.subtract(green)
    .divide(red.add(green.multiply(2.4)).add(1))
    .rename('EVI2');
  // Return the masked image with an EVI-2 band.
  return image.addBands(evi2_calc);
}

// Define a function for NDVI calculation.
function add_NDVI(image) {
  //Compute the Normalized Difference Vegetation Index (NDVI).
  var ndvi_calc = image.normalizedDifference(['b4', 'b3'])
    .rename('NDVI');
  // Return the masked image with an NDVI band.
  return image.addBands(ndvi_calc);
}

// Define a function for NDWI calculation.
function add_NDWI(image) {
  //Compute the Normalized Difference Water Index (NDWI).
  var ndwi_calc = image.normalizedDifference(['b2', 'b4'])
    .rename('NDWI');
  // Return the masked image with an NDWI band.
  return image.addBands(ndwi_calc);
}

// 3. CREATE SEGMENTS

// Add EVI2 to image
segmentation_image = add_EVI2(segmentation_image)

// Add NDVI to image
segmentation_image = add_NDVI(segmentation_image)

// Add NDWI to image
segmentation_image = add_NDWI(segmentation_image)

// Print metadata on segmentation image
print(segmentation_image)

// Select subset of the composite for clustering
var image = segmentation_image.select('b1', 'b2', 'b3', 'b4', 'EVI2', 'NDVI', 'NDWI')

// Set seed grid
var seeds = ee.Algorithms.Image.Segmentation.seedGrid(12);

// Execute Simple Non-Iterative Clustering
var segments = ee.Algorithms.Image.Segmentation.SNIC({
  image: segmentation_image,
  size: 2,
  compactness: 0,
  connectivity: 4,
  neighborhoodSize: 64,
  seeds: seeds
}).reproject({
  crs: 'EPSG:3338',
  scale: 2
}).select(
  ['b1_mean', 'b2_mean', 'b3_mean', 'b4_mean', 'EVI2_mean', 'NDVI_mean', 'NDWI_mean', 'clusters'],
  ['B1', 'B2', 'B3', 'B4', 'EVI2', 'NDVI', 'NDWI', 'clusters']);
var clusters = segments.select('clusters')

// Add RGB composite and clusters to the map.
Map.addLayer(clusters.randomVisualizer(), {}, 'clusters')

// Parse image to single band rasters
var blue = segmentation_image.select('b1')
var red = segmentation_image.select('b2')
var green = segmentation_image.select('b3')
var nearir = segmentation_image.select('b4')
var evi2 = segmentation_image.select('EVI2')
var ndvi = segmentation_image.select('NDVI')
var ndwi = segmentation_image.select('NDWI')

// Export clusters to Google Drive.
Export.image.toDrive({
  image: clusters,
  description: 'Chenega_Segments_Initial',
  folder: 'chenega_clusters',
  scale: 2,
  region: area_feature,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: blue,
  description: 'Chenega_Maxar_Blue',
  folder: 'chenega_maxar',
  scale: 2,
  region: area_feature,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: green,
  description: 'Chenega_Maxar_Green',
  folder: 'chenega_maxar',
  scale: 2,
  region: area_feature,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: red,
  description: 'Chenega_Maxar_Red',
  folder: 'chenega_maxar',
  scale: 2,
  region: area_feature,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: nearir,
  description: 'Chenega_Maxar_NearIR',
  folder: 'chenega_maxar',
  scale: 2,
  region: area_feature,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: evi2,
  description: 'Chenega_Maxar_EVI2',
  folder: 'chenega_maxar',
  scale: 2,
  region: area_feature,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndvi,
  description: 'Chenega_Maxar_NDVI',
  folder: 'chenega_maxar',
  scale: 2,
  region: area_feature,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndwi,
  description: 'Chenega_Maxar_NDWI',
  folder: 'chenega_maxar',
  scale: 2,
  region: area_feature,
  maxPixels: 1e12
});
