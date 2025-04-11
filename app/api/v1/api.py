from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    doctors,
    patients,
    appointments,
    medical_records,
    doctor_patient_assignments
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(medical_records.router, prefix="/medical-records", tags=["medical-records"])
api_router.include_router(doctor_patient_assignments.router, prefix="/doctor-patient-assignments", tags=["doctor-patient-assignments"]) 