import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, date
from uuid import uuid4

from app.db.models.doctor_patient_assignment import DoctorPatientAssignment
from app.schemas.doctor_patient_assignment import DoctorPatientAssignmentCreate, DoctorPatientAssignmentUpdate
from app.db.models.doctor import Doctor
from app.db.models.patient import Patient
from app.core.security import create_access_token

def test_create_assignment(client: TestClient, test_doctor, test_patient, test_doctor_token):
    """Test creating a new doctor-patient assignment"""
    response = client.post(
        "/api/v1/doctor-patient-assignments/",
        json={
            "doctor_id": str(test_doctor.id),
            "patient_id": str(test_patient.id),
            "is_active": True,
            "notes": "Initial assignment"
        },
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == str(test_doctor.id)
    assert data["patient_id"] == str(test_patient.id)
    assert data["is_active"] is True
    assert data["notes"] == "Initial assignment"

def test_create_assignment_invalid_doctor(client: TestClient, test_patient, test_doctor_token):
    """Test creating an assignment with an invalid doctor ID"""
    response = client.post(
        "/api/v1/doctor-patient-assignments/",
        json={
            "doctor_id": str(uuid4()),  # Non-existent doctor ID
            "patient_id": str(test_patient.id),
            "is_active": True,
            "notes": "Invalid assignment"
        },
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert response.status_code == 400
    assert "doctor_id" in response.json()["detail"]

def test_create_assignment_invalid_patient(client: TestClient, test_doctor, test_doctor_token):
    """Test creating an assignment with an invalid patient ID"""
    response = client.post(
        "/api/v1/doctor-patient-assignments/",
        json={
            "doctor_id": str(test_doctor.id),
            "patient_id": str(uuid4()),  # Non-existent patient ID
            "is_active": True,
            "notes": "Invalid assignment"
        },
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert response.status_code == 400
    assert "patient_id" in response.json()["detail"]

def test_get_assignment(client: TestClient, test_doctor, test_patient, test_doctor_token, db: Session):
    """Test retrieving a specific assignment"""
    # First create an assignment
    assignment = DoctorPatientAssignment(
        id=uuid4(),
        doctor_id=test_doctor.id,
        patient_id=test_patient.id,
        is_active=True,
        notes="Test assignment"
    )
    db.add(assignment)
    db.commit()
    
    # Then retrieve it
    response = client.get(
        f"/api/v1/doctor-patient-assignments/{assignment.id}",
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(assignment.id)
    assert data["doctor_id"] == str(test_doctor.id)
    assert data["patient_id"] == str(test_patient.id)

def test_get_nonexistent_assignment(client: TestClient, test_doctor_token):
    """Test retrieving a non-existent assignment"""
    response = client.get(
        f"/api/v1/doctor-patient-assignments/{uuid4()}",
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert response.status_code == 404

def test_get_doctor_assignments(client: TestClient, test_doctor, test_patient, test_doctor_token, db: Session):
    """Test retrieving all assignments for a doctor"""
    # Create multiple assignments
    for i in range(3):
        assignment = DoctorPatientAssignment(
            id=uuid4(),
            doctor_id=test_doctor.id,
            patient_id=test_patient.id,
            is_active=True,
            notes=f"Test assignment {i}"
        )
        db.add(assignment)
    db.commit()
    
    response = client.get(
        f"/api/v1/doctor-patient-assignments/doctor/{test_doctor.id}",
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert all(assignment["doctor_id"] == str(test_doctor.id) for assignment in data)

def test_get_patient_assignments(client: TestClient, test_doctor, test_patient, test_doctor_token, db: Session):
    """Test retrieving all assignments for a patient"""
    # Create multiple assignments
    for i in range(3):
        assignment = DoctorPatientAssignment(
            id=uuid4(),
            doctor_id=test_doctor.id,
            patient_id=test_patient.id,
            is_active=True,
            notes=f"Test assignment {i}"
        )
        db.add(assignment)
    db.commit()
    
    response = client.get(
        f"/api/v1/doctor-patient-assignments/patient/{test_patient.id}",
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert all(assignment["patient_id"] == str(test_patient.id) for assignment in data)

def test_update_assignment(client: TestClient, test_doctor, test_patient, test_doctor_token, db: Session):
    """Test updating an assignment"""
    # Create an assignment first
    assignment = DoctorPatientAssignment(
        id=uuid4(),
        doctor_id=test_doctor.id,
        patient_id=test_patient.id,
        is_active=True,
        notes="Initial assignment"
    )
    db.add(assignment)
    db.commit()
    
    # Update the assignment
    response = client.put(
        f"/api/v1/doctor-patient-assignments/{assignment.id}",
        json={
            "is_active": False,
            "notes": "Updated assignment"
        },
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
    assert data["notes"] == "Updated assignment"

def test_delete_assignment(client: TestClient, test_doctor, test_patient, test_doctor_token, db: Session):
    """Test deleting an assignment"""
    # Create an assignment first
    assignment = DoctorPatientAssignment(
        id=uuid4(),
        doctor_id=test_doctor.id,
        patient_id=test_patient.id,
        is_active=True,
        notes="Assignment to delete"
    )
    db.add(assignment)
    db.commit()
    
    # Delete the assignment
    response = client.delete(
        f"/api/v1/doctor-patient-assignments/{assignment.id}",
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = client.get(
        f"/api/v1/doctor-patient-assignments/{assignment.id}",
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert get_response.status_code == 404

def test_create_duplicate_assignment(client: TestClient, test_doctor, test_patient, test_doctor_token, db: Session):
    """Test creating a duplicate assignment (same doctor and patient)"""
    # Create first assignment
    response1 = client.post(
        "/api/v1/doctor-patient-assignments/",
        json={
            "doctor_id": str(test_doctor.id),
            "patient_id": str(test_patient.id),
            "is_active": True,
            "notes": "First assignment"
        },
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert response1.status_code == 200
    
    # Try to create duplicate assignment
    response2 = client.post(
        "/api/v1/doctor-patient-assignments/",
        json={
            "doctor_id": str(test_doctor.id),
            "patient_id": str(test_patient.id),
            "is_active": True,
            "notes": "Duplicate assignment"
        },
        headers={"Authorization": f"Bearer {test_doctor_token}"}
    )
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"].lower() 