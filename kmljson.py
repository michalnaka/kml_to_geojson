import json
from fastkml import kml
from geojson import Feature, Point, Polygon, FeatureCollection
from lxml import etree

def kml_to_geojson(kml_file, geojson_file):
    # Read the KML file
    with open(kml_file, 'rb') as file:  # Read as bytes
        kml_content = file.read()

    # Parse the KML content
    k = kml.KML()
    k.from_string(kml_content)

    # Extract features from the KML file
    features = []
    for document in k.features():
        print("Document:", document.name)  # Debugging
        for feature in document.features():
            print("Feature:", feature.name)  # Debugging
            # Check if the feature is a folder
            if feature.geometry is None:
                for placemark in feature.features():
                    print("Placemark:", placemark.name)  # Debugging
                    # Extract geometry and convert to GeoJSON
                    geo_feature = convert_geometry_to_geojson(placemark)
                    if geo_feature:
                        features.append(geo_feature)
            else:
                # The feature is a placemark
                placemark = feature
                print("Placemark:", placemark.name)  # Debugging
                # Extract geometry and convert to GeoJSON
                geo_feature = convert_geometry_to_geojson(placemark)
                if geo_feature:
                    features.append(geo_feature)

    # Create a GeoJSON FeatureCollection
    feature_collection = FeatureCollection(features)

    # Write the GeoJSON file
    with open(geojson_file, 'w') as file:
        file.write(json.dumps(feature_collection, indent=2))

def convert_geometry_to_geojson(placemark):
    # Check the type of geometry and extract coordinates accordingly
    geometry = placemark.geometry
    if isinstance(geometry, Point):
        coordinates = geometry.coords[0]
        geo_geometry = Point(coordinates)
    elif hasattr(geometry, 'exterior'):  # Check if the geometry has an 'exterior' attribute
        coordinates = list(geometry.exterior.coords)
        geo_geometry = Polygon([coordinates])
    else:
        # Unsupported geometry type
        return None
    
    # Create GeoJSON Feature with properties
    properties = placemark.extended_data.elements[0].data if placemark.extended_data else {}
    # Include the name of the placemark in the properties
    properties['name'] = placemark.name
    geo_feature = Feature(geometry=geo_geometry, properties=properties)
    return geo_feature

# Example usage
kml_to_geojson('Budapest.kml', 'output.geojson')
