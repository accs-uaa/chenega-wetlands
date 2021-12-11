/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Image segments from simple non-iterative clustering
Author: Timm Nawrocki, Alaska Center for Conservation Science
Last Updated: 2021-12-09
Usage: Must be executed from the Google Earth Engine code editor.
Description: "Image clusters from simple non-iterative clustering" produces image segments from a raster asset.
---------------------------------------------------------------------------*/

// 1. SETUP ANALYSIS

// Import assets
var segmentation_image = ee.Image('projects/accs-geospatial-processing/assets/chenega_imagery');
var area_feature = ee.FeatureCollection('projects/accs-geospatial-processing/assets/chenega_modelarea');

// Print metadata on segmentation imagery
print(segmentation_image)

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

// 3. CREATE CLOUD-REDUCED IMAGE COLLECTION

// Add NDVI to image
segmentation_image = add_NDVI(segmentation_image)

// Select subset of the composite for clustering
var image = segmentation_image.select('b1', 'b2', 'b3', 'NDVI')

// Calculate a Gaussian kernel for image
var kernel = ee.Kernel.gaussian(3);
var image_kernel = image.convolve(kernel);

// Set seed grid
var seeds = ee.Algorithms.Image.Segmentation.seedGrid(36);

// Execute Simple Non-Iterative Clustering
var segments = ee.Algorithms.Image.Segmentation.SNIC({
  image: image_kernel,
  size: 3,
  compactness: 0,
  connectivity: 8,
  neighborhoodSize: 64,
  seeds: seeds
}).select(['b1_mean', 'b2_mean', 'b3_mean', 'NDVI_mean', 'clusters'], ['B1', 'B2', 'B3', 'NDVI', 'clusters']);
var clusters = segments.select('clusters')

// Add RGB composite and clusters to the map.
Map.addLayer(clusters.randomVisualizer(), {}, 'clusters')

// Export clusters to Google Drive.
Export.image.toDrive({
  image: clusters,
  description: 'clusters',
  folder: 'chenega_clusters',
  scale: 2,
  region: area_feature,
  maxPixels: 1e12
});
