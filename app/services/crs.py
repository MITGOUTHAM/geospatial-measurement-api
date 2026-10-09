from pyproj import CRS, Transformer
from shapely import transform


def get_projected_crs(geometry, source_crs):
    source = CRS.from_user_input(source_crs)

    if source.is_projected:
        return source

    centroid = geometry.centroid

    longitude = centroid.x
    latitude = centroid.y

    zone = int((longitude + 180) / 6) + 1

    if latitude >= 0:
        epsg_code = 32600 + zone
    else:
        epsg_code = 32700 + zone

    return CRS.from_epsg(epsg_code)


def transform_geometry_to_projected(
    geometry,
    source_crs="EPSG:4326",
):
    projected_crs = get_projected_crs(
        geometry,
        source_crs,
    )

    transformer = Transformer.from_crs(
        source_crs,
        projected_crs,
        always_xy=True,
    )

    projected_geometry = transform(
        geometry,
        transformer.transform,
        interleaved=False,
    )

    return projected_geometry