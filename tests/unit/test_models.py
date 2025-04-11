import pytest
from datetime import datetime, date, time
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

from app.db.models.user import User
from app.db.models.doctor import Doctor
from app.db.models.patient import Patient
from app.db.models.appointment import Appointment
from app.db.models.medical_record import MedicalRecord
from app.db.models.doctor_patient_assignment import DoctorPatientAssignment
from app.db.models.staff import Staff
from app.db.models.notification import Notification
from app.db.models.audit_log import AuditLog

def test_user_model(db):
    """Test User model creation and validation"""
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed_password",
        role="patient"
    )
    db.add(user)
    db.commit()
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == "patient"
    assert user.is_active is True

def test_doctor_model(db):
    """Test Doctor model creation and validation"""
    doctor = Doctor(
        first_name="John",
        last_name="Doe",
        specialization="Cardiology",
        email="john.doe@example.com",
        phone="1234567890",
        license_number="MD123456"
    )
    db.add(doctor)
    db.commit()
    
    assert doctor.full_name == "John Doe"
    assert doctor.specialization == "Cardiology"
    assert doctor.is_active is True

def test_patient_model(db):
    """Test Patient model creation and validation"""
    patient = Patient(
        first_name="Jane",
        last_name="Smith",
        date_of_birth=date(1990, 1, 1),
        email="jane.smith@example.com",
        phone="0987654321",
        address="123 Main St"
    )
    db.add(patient)
    db.commit()
    
    assert patient.full_name == "Jane Smith"
    assert patient.date_of_birth == date(1990, 1, 1)
    assert patient.email == "jane.smith@example.com"

def test_appointment_model(db, test_doctor, test_patient):
    """Test Appointment model creation and validation"""
    appointment = Appointment(
        doctor_id=test_doctor.id,
        patient_id=test_patient.id,
        start_time=datetime.now(),
        end_time=datetime.now(),
        status="scheduled",
        reason="Regular checkup"
    )
    db.add(appointment)
    db.commit()
    
    assert appointment.doctor_id == test_doctor.id
    assert appointment.patient_id == test_patient.id
    assert appointment.status == "scheduled"

def test_medical_record_model(db, test_doctor, test_patient, test_appointment):
    """Test MedicalRecord model creation and validation"""
    record = MedicalRecord(
        patient_id=test_patient.id,
        doctor_id=test_doctor.id,
        appointment_id=test_appointment.id,
        diagnosis="Common cold",
        prescription="Rest and fluids",
        notes="Patient should follow up in a week"
    )
    db.add(record)
    db.commit()
    
    assert record.patient_id == test_patient.id
    assert record.doctor_id == test_doctor.id
    assert record.diagnosis == "Common cold"

def test_doctor_patient_assignment_model(db, test_doctor, test_patient):
    """Test DoctorPatientAssignment model creation and validation"""
    assignment = DoctorPatientAssignment(
        doctor_id=test_doctor.id,
        patient_id=test_patient.id,
        is_active=True,
        notes="Initial assignment"
    )
    db.add(assignment)
    db.commit()
    
    assert assignment.doctor_id == test_doctor.id
    assert assignment.patient_id == test_patient.id
    assert assignment.is_active is True

def test_staff_model(db, test_user):
    """Test Staff model creation and validation"""
    staff = Staff(
        user_id=test_user.id,
        department="Administration",
        position="Manager",
        status="verified"
    )
    db.add(staff)
    db.commit()
    
    assert staff.user_id == test_user.id
    assert staff.department == "Administration"
    assert staff.status == "verified"

def test_notification_model(db, test_user):
    """Test Notification model creation and validation"""
    notification = Notification(
        user_id=test_user.id,
        type="appointment_reminder",
        content="Your appointment is tomorrow at 10:00 AM"
    )
    db.add(notification)
    db.commit()
    
    assert notification.user_id == test_user.id
    assert notification.type == "appointment_reminder"
    assert notification.is_read is False

def test_audit_log_model(db, test_user):
    """Test AuditLog model creation and validation"""
    log = AuditLog(
        user_id=test_user.id,
        action="create",
        resource_type="appointment",
        resource_id=uuid4(),
        details={"field": "value"}
    )
    db.add(log)
    db.commit()
    
    assert log.user_id == test_user.id
    assert log.action == "create"
    assert log.resource_type == "appointment"

def test_appointment_time_constraint(db, test_doctor, test_patient):
    """Test appointment time constraint validation"""
    with pytest.raises(IntegrityError):
        appointment = Appointment(
            doctor_id=test_doctor.id,
            patient_id=test_patient.id,
            start_time=datetime.now(),
            end_time=datetime.now(),  # Same as start_time
            status="scheduled",
            reason="Test"
        )
        db.add(appointment)
        db.commit()

def test_doctor_patient_assignment_unique_constraint(db, test_doctor, test_patient):
    """Test unique constraint on doctor-patient assignments"""
    # Create first assignment
    assignment1 = DoctorPatientAssignment(
        doctor_id=test_doctor.id,
        patient_id=test_patient.id,
        is_active=True
    )
    db.add(assignment1)
    db.commit()
    
    # Try to create duplicate assignment
    with pytest.raises(IntegrityError):
        assignment2 = DoctorPatientAssignment(
            doctor_id=test_doctor.id,
            patient_id=test_patient.id,
            is_active=True
        )
        db.add(assignment2)
        db.commit()

def test_user_role_constraint(db):
    """Test user role constraint validation"""
    with pytest.raises(IntegrityError):
        user = User(
            username="invalidrole",
            email="invalid@example.com",
            full_name="Invalid Role",
            password_hash="hashed_password",
            role="invalid_role"  # Invalid role
        )
        db.add(user)
        db.commit() 