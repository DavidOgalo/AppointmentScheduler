import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.main import app
from app.db.session import get_db
from app.core.security import create_access_token
from app.db.models.user import User
from app.db.models.doctor import Doctor
from app.db.models.patient import Patient
from app.db.models.appointment import Appointment
from app.services.doctor_schedule_service import DoctorScheduleService

client = TestClient(app)

@pytest.fixture
def test_user(db: Session):
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed_password",
        role="patient"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_token(test_user):
    return create_access_token({"sub": str(test_user.id)})

def test_create_appointment_success(db: Session, test_doctor, test_patient, test_token):
    """Test successful appointment creation."""
    # Create doctor's schedule first
    schedule_service = DoctorScheduleService(db)
    schedule_data = {
        "doctor_id": test_doctor.id,
        "day_of_week": 1,  # Monday
        "start_time": "09:00",
        "end_time": "17:00",
        "is_available": True
    }
    schedule_service.create(schedule_data)

    # Create appointment
    start_time = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0)
    response = client.post(
        "/api/v1/appointments/",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "doctor_id": str(test_doctor.id),
            "patient_id": str(test_patient.id),
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(hours=1)).isoformat(),
            "reason": "Regular checkup"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == str(test_doctor.id)
    assert data["patient_id"] == str(test_patient.id)
    assert data["status"] == "scheduled"

def test_create_appointment_conflict(db: Session, test_doctor, test_patient, test_token):
    """Test appointment creation with time conflict."""
    # Create first appointment
    start_time = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0)
    response1 = client.post(
        "/api/v1/appointments/",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "doctor_id": str(test_doctor.id),
            "patient_id": str(test_patient.id),
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(hours=1)).isoformat(),
            "reason": "First appointment"
        }
    )
    assert response1.status_code == 200

    # Try to create overlapping appointment
    response2 = client.post(
        "/api/v1/appointments/",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "doctor_id": str(test_doctor.id),
            "patient_id": str(test_patient.id),
            "start_time": (start_time + timedelta(minutes=30)).isoformat(),
            "end_time": (start_time + timedelta(hours=1, minutes=30)).isoformat(),
            "reason": "Overlapping appointment"
        }
    )
    assert response2.status_code == 400
    assert "conflict" in response2.json()["detail"].lower()

def test_create_appointment_outside_schedule(db: Session, test_doctor, test_patient, test_token):
    """Test appointment creation outside doctor's schedule."""
    # Create doctor's schedule
    schedule_service = DoctorScheduleService(db)
    schedule_data = {
        "doctor_id": test_doctor.id,
        "day_of_week": 1,  # Monday
        "start_time": "09:00",
        "end_time": "17:00",
        "is_available": True
    }
    schedule_service.create(schedule_data)

    # Try to create appointment outside schedule
    start_time = (datetime.now() + timedelta(days=1)).replace(hour=18, minute=0)
    response = client.post(
        "/api/v1/appointments/",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "doctor_id": str(test_doctor.id),
            "patient_id": str(test_patient.id),
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(hours=1)).isoformat(),
            "reason": "After hours appointment"
        }
    )
    assert response.status_code == 400
    assert "not available" in response.json()["detail"].lower()

def test_get_appointment(db: Session, test_doctor, test_patient, test_token):
    """Test retrieving an appointment."""
    # Create appointment first
    start_time = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0)
    create_response = client.post(
        "/api/v1/appointments/",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "doctor_id": str(test_doctor.id),
            "patient_id": str(test_patient.id),
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(hours=1)).isoformat(),
            "reason": "Test appointment"
        }
    )
    appointment_id = create_response.json()["id"]

    # Get appointment
    response = client.get(
        f"/api/v1/appointments/{appointment_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == appointment_id
    assert data["doctor_id"] == str(test_doctor.id)
    assert data["patient_id"] == str(test_patient.id)

def test_update_appointment_status(db: Session, test_doctor, test_patient, test_token):
    """Test updating appointment status."""
    # Create appointment first
    start_time = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0)
    create_response = client.post(
        "/api/v1/appointments/",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "doctor_id": str(test_doctor.id),
            "patient_id": str(test_patient.id),
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(hours=1)).isoformat(),
            "reason": "Test appointment"
        }
    )
    appointment_id = create_response.json()["id"]

    # Update appointment status
    response = client.put(
        f"/api/v1/appointments/{appointment_id}",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "status": "completed",
            "notes": "Patient seen and treated"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["notes"] == "Patient seen and treated"

def test_delete_appointment(db: Session, test_doctor, test_patient, test_token):
    """Test deleting an appointment."""
    # Create appointment first
    start_time = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0)
    create_response = client.post(
        "/api/v1/appointments/",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "doctor_id": str(test_doctor.id),
            "patient_id": str(test_patient.id),
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(hours=1)).isoformat(),
            "reason": "Test appointment"
        }
    )
    appointment_id = create_response.json()["id"]

    # Delete appointment
    response = client.delete(
        f"/api/v1/appointments/{appointment_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200

    # Verify appointment is deleted
    get_response = client.get(
        f"/api/v1/appointments/{appointment_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert get_response.status_code == 404

def test_list_doctor_appointments(db: Session, test_doctor, test_patient, test_token):
    """Test listing all appointments for a doctor."""
    # Create multiple appointments
    start_time = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0)
    for i in range(3):
        client.post(
            "/api/v1/appointments/",
            headers={"Authorization": f"Bearer {test_token}"},
            json={
                "doctor_id": str(test_doctor.id),
                "patient_id": str(test_patient.id),
                "start_time": (start_time + timedelta(days=i)).isoformat(),
                "end_time": (start_time + timedelta(days=i, hours=1)).isoformat(),
                "reason": f"Appointment {i+1}"
            }
        )

    # Get doctor's appointments
    response = client.get(
        f"/api/v1/appointments/doctor/{test_doctor.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(appt["doctor_id"] == str(test_doctor.id) for appt in data)

def test_list_patient_appointments(db: Session, test_doctor, test_patient, test_token):
    """Test listing all appointments for a patient."""
    # Create multiple appointments
    start_time = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0)
    for i in range(3):
        client.post(
            "/api/v1/appointments/",
            headers={"Authorization": f"Bearer {test_token}"},
            json={
                "doctor_id": str(test_doctor.id),
                "patient_id": str(test_patient.id),
                "start_time": (start_time + timedelta(days=i)).isoformat(),
                "end_time": (start_time + timedelta(days=i, hours=1)).isoformat(),
                "reason": f"Appointment {i+1}"
            }
        )

    # Get patient's appointments
    response = client.get(
        f"/api/v1/appointments/patient/{test_patient.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(appt["patient_id"] == str(test_patient.id) for appt in data) 