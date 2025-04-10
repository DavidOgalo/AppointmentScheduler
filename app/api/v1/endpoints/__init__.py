"""
API v1 endpoints package initialization
"""

from . import auth
from . import users
from . import appointments
from . import patients
from . import doctors
from . import staff
from . import profiles
from . import doctor_schedules

__all__ = ["auth", "users", "appointments", "patients", "doctors", "staff", "profiles", "doctor_schedules"] 