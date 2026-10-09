# Geospatial File Measurement API

A FastAPI-based backend that accepts KML files and ZIP files containing Shapefiles, extracts geospatial features, and calculates measurements such as polygon area and LineString length.

## Setup

Requirements: Python 3.12+ and Git.

Clone and install:

    git clone https://github.com/MITGOUTHAM/geospatial-measurement-api.git
    cd geospatial-measurement-api
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt

Run the application:

    python -m uvicorn app.main:app --reload

Application: http://127.0.0.1:8000
Swagger API Documentation: http://127.0.0.1:8000/docs

Run tests:

    pytest

## API

POST /api/files/
Uploads and processes a .kml file or a .zip file containing a Shapefile.

Example:

    curl -X POST "http://127.0.0.1:8000/api/files/" -F "file=@test_data/polygon.kml"

Example response:

    {
      "id": "file-id",
      "filename": "polygon.kml",
      "status": "PROCESSED",
      "feature_count": 1
    }

GET /api/files/{file_id}
Returns the processed file details including feature ID, geometry type, CRS, properties, and geometry.

Example response:

    {
      "id": "file-id",
      "status": "PROCESSED",
      "feature_count": 1,
      "features": [
        {
          "feature_id": 0,
          "geometry_type": "Polygon",
          "crs": "EPSG:4326",
          "properties": {
            "name": "Test Polygon"
          }
        }
      ]
    }

GET /api/files/{file_id}/measurements
Returns measurements based on geometry type. Point features have no measurement, LineString features return length in metres, and Polygon features return area in square metres.

Example response:

    {
      "file_id": "file-id",
      "measurements": [
        {
          "feature_id": 0,
          "geometry_type": "Polygon",
          "measurement_type": "area",
          "value": 11500.42,
          "unit": "m²"
        }
      ]
    }

## Architecture

The application is divided into API, service, and schema layers. The main application is defined in app/main.py. API endpoints are implemented in app/api/files.py. Geospatial file processing is handled by app/services/file_processor.py. CRS detection and coordinate transformation are handled by app/services/crs.py. Area and length calculations are handled by app/services/measurement.py.

File processing flow:

    Upload File → Validate File → Save File → Read KML/Extract ZIP → Extract Features → Return Processed Data

For each feature, the application extracts the feature ID, geometry type, geometry, properties, and CRS.

Measurement flow:

    Feature → Check Geometry Type → Point: No Measurement
                             → LineString: Calculate Length
                             → Polygon: Calculate Area

Before calculating area or length, geographic geometries are transformed into a suitable projected CRS.

## CRS Handling

KML coordinates are handled as EPSG:4326 latitude/longitude coordinates. For Shapefiles, the CRS is read from the .prj file when available. Area and length are not calculated directly using latitude/longitude degrees because degrees are angular units. If the source CRS is geographic, the application selects a suitable UTM projected CRS and transforms the geometry using pyproj before calculating the measurement.

## Design Decisions

FastAPI was selected because it is lightweight, easy to develop with, and provides automatic Swagger/OpenAPI documentation. Shapely is used for geometry operations and area/length calculations. pyshp is used to read Shapefiles without requiring GDAL/Fiona. Python's XML parser is used for KML processing. pyproj is used for CRS detection and coordinate transformation. File processing, CRS handling, and measurement logic are separated into different service modules so that the application is easier to test and maintain.

## Testing

The project contains tests for KML processing, Shapefile processing, ZIP processing, Point/LineString/Polygon measurements, API endpoints, invalid files, and missing files.

Current test result: 15 passed

Run tests using:

    pytest

## Learning

This project provided practical experience with FastAPI, REST API development, KML and Shapefile processing, Shapely geometry operations, CRS and coordinate transformation, pyproj, API testing with pytest, and Git/GitHub.

## Future Scope

Future improvements can include PostgreSQL/PostGIS for persistent geospatial data, GeoJSON and additional geometry support, authentication, file-size validation, improved ZIP security, background processing for large files, Docker deployment, and more advanced CRS handling.

## Submission

GitHub Repository:
https://github.com/MITGOUTHAM/geospatial-measurement-api
