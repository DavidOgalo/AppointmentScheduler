import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.main import app
from app.core.security import create_access_token
from app.db.models import User, Doctor, Patient, Appointment, MedicalRecord
from app.schemas.user import UserCreate
from app.schemas.doctor import DoctorCreate
from app.schemas.patient import PatientCreate
from app.schemas.appointment import AppointmentCreate
from app.schemas.medical_record import MedicalRecordCreate

client = TestClient(app)

def test_complete_patient_flow():
    """Test the complete flow from patient registration to appointment and medical record creation"""
    # 1. Register a new patient
    patient_data = {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "address": "123 Main St",
        "insurance_info": {"provider": "ABC Insurance", "policy_number": "12345"}
    }
    response = client.post("/api/v1/patients/", json=patient_data)
    assert response.status_code == 200
    patient = response.json()
    
    # 2. Create a user account for the patient
    user_data = {
        "username": "johndoe",
        "email": "john.doe@example.com",
        "password": "password123",
        "full_name": "John Doe",
        "role": "patient"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    user = response.json()
    
    # 3. Login and get token
    login_data = {
        "username": "johndoe",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 4. Get available doctors
    response = client.get("/api/v1/doctors/", headers=headers)
    assert response.status_code == 200
    doctors = response.json()
    assert len(doctors) > 0
    
    # 5. Create an appointment
    appointment_data = {
        "doctor_id": doctors[0]["id"],
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
        "reason": "Regular checkup"
    }
    response = client.post("/api/v1/appointments/", json=appointment_data, headers=headers)
    assert response.status_code == 200
    appointment = response.json()
    
    # 6. Create a medical record
    medical_record_data = {
        "appointment_id": appointment["id"],
        "diagnosis": "Healthy",
        "prescription": "No medication needed",
        "notes": "Patient is in good health"
    }
    response = client.post("/api/v1/medical-records/", json=medical_record_data, headers=headers)
    assert response.status_code == 200
    medical_record = response.json()
    
    # 7. Get patient's medical history
    response = client.get(f"/api/v1/patients/{patient['id']}/medical-records", headers=headers)
    assert response.status_code == 200
    medical_records = response.json()
    assert len(medical_records) > 0
    assert medical_records[0]["id"] == medical_record["id"]

def test_doctor_workflow():
    """Test the complete workflow for a doctor"""
    # 1. Register a new doctor
    doctor_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "specialization": "Cardiology",
        "email": "jane.smith@example.com",
        "phone": "0987654321",
        "license_number": "DOC12345"
    }
    response = client.post("/api/v1/doctors/", json=doctor_data)
    assert response.status_code == 200
    doctor = response.json()
    
    # 2. Create a user account for the doctor
    user_data = {
        "username": "janesmith",
        "email": "jane.smith@example.com",
        "password": "password123",
        "full_name": "Jane Smith",
        "role": "doctor"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    user = response.json()
    
    # 3. Login and get token
    login_data = {
        "username": "janesmith",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 4. Set doctor's schedule
    schedule_data = {
        "day_of_week": 1,  # Monday
        "start_time": "09:00:00",
        "end_time": "17:00:00",
        "is_available": True
    }
    response = client.post(f"/api/v1/doctors/{doctor['id']}/schedule", json=schedule_data, headers=headers)
    assert response.status_code == 200
    
    # 5. Get doctor's appointments
    response = client.get(f"/api/v1/doctors/{doctor['id']}/appointments", headers=headers)
    assert response.status_code == 200
    appointments = response.json()
    
    # 6. Update appointment status
    if appointments:
        appointment_id = appointments[0]["id"]
        update_data = {"status": "completed"}
        response = client.patch(f"/api/v1/appointments/{appointment_id}", json=update_data, headers=headers)
        assert response.status_code == 200

def test_security_measures():
    """Test various security measures and access controls"""
    # 1. Test rate limiting
    for _ in range(6):  # Assuming limit is 5 requests per minute
        response = client.post("/api/v1/auth/login", data={"username": "test", "password": "test"})
    assert response.status_code == 429  # Too Many Requests
    
    # 2. Test token expiration
    expired_token = create_access_token(data={"sub": "test"}, expires_delta=timedelta(seconds=-1))
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    
    # 3. Test role-based access control
    # Create a patient user
    patient_data = {
        "username": "patient_user",
        "email": "patient@example.com",
        "password": "password123",
        "full_name": "Patient User",
        "role": "patient"
    }
    response = client.post("/api/v1/auth/register", json=patient_data)
    assert response.status_code == 200
    
    # Login as patient
    login_data = {
        "username": "patient_user",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to access admin-only endpoint
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 403
    
    # 4. Test input validation
    invalid_data = {
        "email": "invalid-email",
        "password": "short"
    }
    response = client.post("/api/v1/auth/register", json=invalid_data)
    assert response.status_code == 422
    
    # 5. Test SQL injection prevention
    malicious_input = {
        "username": "admin'--",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", data=malicious_input)
    assert response.status_code == 401  # Should not reveal whether user exists 