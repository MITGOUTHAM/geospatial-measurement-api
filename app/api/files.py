from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException


router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".kml", ".zip"}


def find_file(file_id: str):
    for extension in ALLOWED_EXTENSIONS:
        file_path = UPLOAD_DIR / f"{file_id}{extension}"

        if file_path.exists() and file_path.is_file():
            return file_path

    return None


def process_file(file_path: Path):
    from app.services.file_processor import (
        process_kml,
        process_zip,
    )

    extension = file_path.suffix.lower()

    if extension == ".kml":
        return process_kml(str(file_path))

    if extension == ".zip":
        try:
            return process_zip(str(file_path))
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            )

    return []


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Only .kml and .zip files are allowed."
            ),
        )

    file_id = str(uuid4())

    saved_filename = f"{file_id}{extension}"
    file_path = UPLOAD_DIR / saved_filename

    file_content = await file.read()
    file_path.write_bytes(file_content)

    features = process_file(file_path)

    return {
        "id": file_id,
        "filename": file.filename,
        "saved_filename": saved_filename,
        "status": "PROCESSED",
        "feature_count": len(features),
        "message": "File uploaded and processed successfully",
    }


@router.get("/{file_id}")
async def get_file(file_id: str):
    file_path = find_file(file_id)

    if file_path is None:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    features = process_file(file_path)

    return {
        "id": file_id,
        "filename": file_path.name,
        "status": "PROCESSED",
        "feature_count": len(features),
        "features": [
            {
                "feature_id": feature["feature_id"],
                "geometry_type": feature["geometry_type"],
                "crs": feature["crs"],
                "properties": feature["properties"],
                "geometry": feature["geometry"].wkt,
            }
            for feature in features
        ],
    }


@router.get("/{file_id}/measurements")
async def get_measurements(file_id: str):
    file_path = find_file(file_id)

    if file_path is None:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    features = process_file(file_path)

    from app.services.measurement import calculate_measurement

    measurements = []

    for feature in features:
        measurement = calculate_measurement(
            feature["geometry"],
            feature["geometry_type"],
            feature["crs"],
        )

        measurements.append(
            {
                "feature_id": feature["feature_id"],
                "geometry_type": feature["geometry_type"],
                **measurement,
            }
        )

    return {
        "file_id": file_id,
        "measurements": measurements,
    }