from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Geospatial Measurement API is running"
    )


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_upload_kml():
    with open("test_data/polygon.kml", "rb") as file:
        response = client.post(
            "/api/files/",
            files={
                "file": (
                    "polygon.kml",
                    file,
                    "application/vnd.google-earth.kml+xml",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "polygon.kml"
    assert data["status"] == "PROCESSED"
    assert data["feature_count"] == 1

    return data["id"]


def test_get_file():
    file_id = test_upload_kml()

    response = client.get(
        f"/api/files/{file_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["feature_count"] == 1
    assert data["features"][0]["geometry_type"] == "Polygon"


def test_get_measurements():
    file_id = test_upload_kml()

    response = client.get(
        f"/api/files/{file_id}/measurements"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["measurements"]) == 1

    measurement = data["measurements"][0]

    assert measurement["geometry_type"] == "Polygon"
    assert measurement["measurement_type"] == "area"
    assert measurement["value"] > 0
    assert measurement["unit"] == "m²"


def test_unsupported_file():
    response = client.post(
        "/api/files/",
        files={
            "file": (
                "invalid.txt",
                b"invalid file",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Unsupported file type. "
        "Only .kml and .zip files are allowed."
    )


def test_file_not_found():
    response = client.get(
        "/api/files/non-existent-id"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"