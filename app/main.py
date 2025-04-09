from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import auth, users, appointments, patients, doctors, staff, profiles
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
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["appointments"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["patients"])
app.include_router(doctors.router, prefix="/api/v1/doctors", tags=["doctors"])
app.include_router(staff.router, prefix="/api/v1/staff", tags=["staff"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["profiles"])

@app.get("/")
async def root():
    return {"message": "Welcome to Healthcare Appointment Scheduler API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 