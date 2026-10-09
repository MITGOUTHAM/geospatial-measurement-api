from app.services.crs import transform_geometry_to_projected


def calculate_measurement(
    geometry,
    geometry_type,
    source_crs,
):
    if geometry_type == "Point":
        return {
            "measurement_type": None,
            "value": None,
            "unit": None,
        }

    projected_geometry = transform_geometry_to_projected(
        geometry,
        source_crs,
    )

    if geometry_type == "Polygon":
        return {
            "measurement_type": "area",
            "value": projected_geometry.area,
            "unit": "m²",
        }

    if geometry_type == "LineString":
        return {
            "measurement_type": "length",
            "value": projected_geometry.length,
            "unit": "m",
        }

    return {
        "measurement_type": None,
        "value": None,
        "unit": None,
    }