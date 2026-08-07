from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging_config import setup_logger
from app.api.routes import router

logger = setup_logger()

app = FastAPI(
    title="Monday BI Agent",
    version="1.0.0",
    description="AI Business Intelligence Agent for Monday.com",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Monday BI Agent Backend Running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }