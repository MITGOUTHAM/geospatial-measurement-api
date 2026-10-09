from app.services.file_processor import (
    process_kml,
    process_shapefile,
    process_zip,
)

from app.services.measurement import calculate_measurement


def test_kml_point():
    features = process_kml("test_data/sample.kml")

    assert len(features) == 1
    assert features[0]["geometry_type"] == "Point"
    assert features[0]["crs"] == "EPSG:4326"


def test_kml_polygon():
    features = process_kml("test_data/polygon.kml")

    assert len(features) == 1
    assert features[0]["geometry_type"] == "Polygon"


def test_kml_line():
    features = process_kml("test_data/line.kml")

    assert len(features) == 1
    assert features[0]["geometry_type"] == "LineString"


def test_shapefile():
    features = process_shapefile(
        "test_data/sample.shp"
    )

    assert len(features) == 1
    assert features[0]["geometry_type"] == "Point"
    assert features[0]["crs"] == "EPSG:4326"


def test_zip():
    features = process_zip(
        "test_data/sample.zip"
    )

    assert len(features) == 1
    assert features[0]["geometry_type"] == "Point"


def test_point_measurement():
    features = process_kml(
        "test_data/sample.kml"
    )

    feature = features[0]

    result = calculate_measurement(
        feature["geometry"],
        feature["geometry_type"],
        feature["crs"],
    )

    assert result["measurement_type"] is None
    assert result["value"] is None
    assert result["unit"] is None


def test_polygon_measurement():
    features = process_kml(
        "test_data/polygon.kml"
    )

    feature = features[0]

    result = calculate_measurement(
        feature["geometry"],
        feature["geometry_type"],
        feature["crs"],
    )

    assert result["measurement_type"] == "area"
    assert result["value"] > 0
    assert result["unit"] == "m²"


def test_line_measurement():
    features = process_kml(
        "test_data/line.kml"
    )

    feature = features[0]

    result = calculate_measurement(
        feature["geometry"],
        feature["geometry_type"],
        feature["crs"],
    )

    assert result["measurement_type"] == "length"
    assert result["value"] > 0
    assert result["unit"] == "m"