import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import shapefile
from pyproj import CRS

from shapely.geometry import Point, LineString, Polygon, shape


KML_NAMESPACE = {
    "kml": "http://www.opengis.net/kml/2.2"
}


def parse_coordinates(coordinates_text: str):
    coordinates = []

    for value in coordinates_text.strip().split():
        parts = value.split(",")

        longitude = float(parts[0])
        latitude = float(parts[1])

        coordinates.append((longitude, latitude))

    return coordinates


def process_kml(file_path: str):
    tree = ET.parse(file_path)
    root = tree.getroot()

    features = []

    placemarks = root.findall(
        ".//kml:Placemark",
        KML_NAMESPACE
    )

    for index, placemark in enumerate(placemarks):

        name_element = placemark.find(
            "kml:name",
            KML_NAMESPACE
        )

        name = (
            name_element.text
            if name_element is not None
            else None
        )

        point = placemark.find(
            ".//kml:Point/kml:coordinates",
            KML_NAMESPACE
        )

        line = placemark.find(
            ".//kml:LineString/kml:coordinates",
            KML_NAMESPACE
        )

        polygon = placemark.find(
            ".//kml:Polygon/"
            "kml:outerBoundaryIs/"
            "kml:LinearRing/"
            "kml:coordinates",
            KML_NAMESPACE
        )

        geometry = None
        geometry_type = None

        if point is not None:
            coordinates = parse_coordinates(point.text)

            geometry = Point(coordinates[0])
            geometry_type = "Point"

        elif line is not None:
            coordinates = parse_coordinates(line.text)

            geometry = LineString(coordinates)
            geometry_type = "LineString"

        elif polygon is not None:
            coordinates = parse_coordinates(polygon.text)

            geometry = Polygon(coordinates)
            geometry_type = "Polygon"

        features.append(
            {
                "feature_id": index,
                "geometry_type": geometry_type,
                "geometry": geometry,
                "properties": {
                    "name": name,
                },
                "crs": "EPSG:4326",
            }
        )

    return features


def process_shapefile(shp_path: str):
    reader = shapefile.Reader(shp_path)

    fields = [
        field[0]
        for field in reader.fields[1:]
    ]

    # Read CRS from the .prj file
    shp_path_obj = Path(shp_path)
    prj_path = shp_path_obj.with_suffix(".prj")

    crs = "EPSG:4326"

    if prj_path.exists():
        try:
            crs = CRS.from_wkt(
                prj_path.read_text()
            ).to_string()
        except Exception:
            crs = "EPSG:4326"

    features = []

    for index, record in enumerate(
        reader.iterShapeRecords()
    ):
        properties = dict(
            zip(fields, record.record)
        )

        geometry = shape(
            record.shape.__geo_interface__
        )

        features.append(
            {
                "feature_id": index,
                "geometry_type": geometry.geom_type,
                "geometry": geometry,
                "properties": properties,
                "crs": crs,
            }
        )

    return features


def process_zip(zip_path: str):
    extract_dir = Path(zip_path).with_suffix("")

    extract_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    shp_files = list(
        extract_dir.rglob("*.shp")
    )

    if not shp_files:
        raise ValueError(
            "ZIP file does not contain a Shapefile."
        )

    shp_path = shp_files[0]

    return process_shapefile(
        str(shp_path)
    )