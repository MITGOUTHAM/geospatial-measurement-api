from fastapi import FastAPI

from app.api.files import router as files_router


app = FastAPI(
    title="Geospatial File Measurement API",
    description="API for processing geospatial files and calculating measurements.",
    version="1.0.0",
)


app.include_router(files_router)


@app.get("/")
def root():
    return {
        "message": "Geospatial Measurement API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }