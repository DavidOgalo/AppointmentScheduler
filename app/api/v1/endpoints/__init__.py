"""
API v1 endpoints package initialization
"""

from app.api.v1.endpoints import auth, users, appointments, patients, doctors, staff, profiles

__all__ = ["auth", "users", "appointments", "patients", "doctors", "staff", "profiles"] 