from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import analyse

settings = get_settings()

app = FastAPI(
    title="Viralify API",
    description="Analyse content and predict viral potential",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyse.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
