from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, appointments, patients, doctors, staff, profiles, doctor_schedules

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
api_router.include_router(staff.router, prefix="/staff", tags=["staff"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(doctor_schedules.router, prefix="/doctor-schedules", tags=["doctor-schedules"]) 