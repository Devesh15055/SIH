"""
SIH26188 - AI-Based Fake Identity & Document Screening System
FastAPI Backend Application Entrypoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import HealthResponse
from backend.api.v1.router import router as api_v1_router

app = FastAPI(
    title="SIH26188 Identity Screening Backend API",
    description="Multi-signal AI microservice for identity document screening, OCR parsing, MRZ validation, and risk scoring.",
    version="1.0.0"
)

# CORS Configuration for Streamlit Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router V1
app.include_router(api_v1_router)

@app.get("/health", response_model=HealthResponse, tags=["System Health"])
def root_health():
    """Root health check endpoint."""
    return HealthResponse()

@app.get("/", tags=["System Information"])
def root_info():
    return {
        "status": "online",
        "system": "SIH26188 AI Fake Identity & Document Screening System API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
