from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import auth
from app.core.config.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Healthcare Appointment Scheduler",
    description="API for managing healthcare appointments",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Welcome to Healthcare Appointment Scheduler API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 