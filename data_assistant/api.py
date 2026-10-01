from fastapi import FastAPI

from data_assistant.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "application": settings.app_name,
        "version": settings.app_version,
    }