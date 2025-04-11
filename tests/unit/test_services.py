import pytest
from datetime import datetime, date, time, timedelta
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

from app.services.user_service import UserService
from app.services.doctor_service import DoctorService
from app.services.patient_service import PatientService
from app.services.appointment_service import AppointmentService
from app.services.medical_record_service import MedicalRecordService
from app.services.doctor_patient_assignment_service import DoctorPatientAssignmentService
from app.services.staff_service import StaffService
from app.services.notification_service import NotificationService
from app.services.audit_log_service import AuditLogService

def test_user_service_create_and_get(db):
    """Test user service create and get operations"""
    service = UserService(db)
    
    # Create user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password_hash": "hashed_password",
        "role": "patient"
    }
    user = service.create(user_data)
    
    # Get user
    retrieved_user = service.get_by_id(user.id)
    assert retrieved_user.username == "testuser"
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.role == "patient"

def test_doctor_service_create_and_get(db):
    """Test doctor service create and get operations"""
    service = DoctorService(db)
    
    # Create doctor
    doctor_data = {
        "first_name": "John",
        "last_name": "Doe",
        "specialization": "Cardiology",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "license_number": "MD123456"
    }
    doctor = service.create(doctor_data)
    
    # Get doctor
    retrieved_doctor = service.get_by_id(doctor.id)
    assert retrieved_doctor.full_name == "John Doe"
    assert retrieved_doctor.specialization == "Cardiology"

def test_patient_service_create_and_get(db):
    """Test patient service create and get operations"""
    service = PatientService(db)
    
    # Create patient
    patient_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "date_of_birth": date(1990, 1, 1),
        "email": "jane.smith@example.com",
        "phone": "0987654321",
        "address": "123 Main St"
    }
    patient = service.create(patient_data)
    
    # Get patient
    retrieved_patient = service.get_by_id(patient.id)
    assert retrieved_patient.full_name == "Jane Smith"
    assert retrieved_patient.date_of_birth == date(1990, 1, 1)

def test_appointment_service_create_and_get(db, test_doctor, test_patient):
    """Test appointment service create and get operations"""
    service = AppointmentService(db)
    
    # Create appointment
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=1)
    appointment_data = {
        "doctor_id": test_doctor.id,
        "patient_id": test_patient.id,
        "start_time": start_time,
        "end_time": end_time,
        "status": "scheduled",
        "reason": "Regular checkup"
    }
    appointment = service.create(appointment_data)
    
    # Get appointment
    retrieved_appointment = service.get_by_id(appointment.id)
    assert retrieved_appointment.doctor_id == test_doctor.id
    assert retrieved_appointment.patient_id == test_patient.id
    assert retrieved_appointment.status == "scheduled"

def test_medical_record_service_create_and_get(db, test_doctor, test_patient, test_appointment):
    """Test medical record service create and get operations"""
    service = MedicalRecordService(db)
    
    # Create medical record
    record_data = {
        "patient_id": test_patient.id,
        "doctor_id": test_doctor.id,
        "appointment_id": test_appointment.id,
        "diagnosis": "Common cold",
        "prescription": "Rest and fluids",
        "notes": "Patient should follow up in a week"
    }
    record = service.create(record_data)
    
    # Get medical record
    retrieved_record = service.get_by_id(record.id)
    assert retrieved_record.patient_id == test_patient.id
    assert retrieved_record.doctor_id == test_doctor.id
    assert retrieved_record.diagnosis == "Common cold"

def test_doctor_patient_assignment_service_create_and_get(db, test_doctor, test_patient):
    """Test doctor-patient assignment service create and get operations"""
    service = DoctorPatientAssignmentService(db)
    
    # Create assignment
    assignment_data = {
        "doctor_id": test_doctor.id,
        "patient_id": test_patient.id,
        "is_active": True,
        "notes": "Initial assignment"
    }
    assignment = service.create(assignment_data)
    
    # Get assignment
    retrieved_assignment = service.get_by_id(assignment.id)
    assert retrieved_assignment.doctor_id == test_doctor.id
    assert retrieved_assignment.patient_id == test_patient.id
    assert retrieved_assignment.is_active is True

def test_staff_service_create_and_get(db, test_user):
    """Test staff service create and get operations"""
    service = StaffService(db)
    
    # Create staff
    staff_data = {
        "user_id": test_user.id,
        "department": "Administration",
        "position": "Manager",
        "status": "verified"
    }
    staff = service.create(staff_data)
    
    # Get staff
    retrieved_staff = service.get_by_id(staff.id)
    assert retrieved_staff.user_id == test_user.id
    assert retrieved_staff.department == "Administration"

def test_notification_service_create_and_get(db, test_user):
    """Test notification service create and get operations"""
    service = NotificationService(db)
    
    # Create notification
    notification_data = {
        "user_id": test_user.id,
        "type": "appointment_reminder",
        "content": "Your appointment is tomorrow at 10:00 AM"
    }
    notification = service.create(notification_data)
    
    # Get notification
    retrieved_notification = service.get_by_id(notification.id)
    assert retrieved_notification.user_id == test_user.id
    assert retrieved_notification.type == "appointment_reminder"
    assert retrieved_notification.is_read is False

def test_audit_log_service_create_and_get(db, test_user):
    """Test audit log service create and get operations"""
    service = AuditLogService(db)
    
    # Create audit log
    log_data = {
        "user_id": test_user.id,
        "action": "create",
        "resource_type": "appointment",
        "resource_id": uuid4(),
        "details": {"field": "value"}
    }
    log = service.create(log_data)
    
    # Get audit log
    retrieved_log = service.get_by_id(log.id)
    assert retrieved_log.user_id == test_user.id
    assert retrieved_log.action == "create"
    assert retrieved_log.resource_type == "appointment"

def test_appointment_service_time_conflict(db, test_doctor, test_patient):
    """Test appointment service time conflict detection"""
    service = AppointmentService(db)
    
    # Create first appointment
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=1)
    appointment1_data = {
        "doctor_id": test_doctor.id,
        "patient_id": test_patient.id,
        "start_time": start_time,
        "end_time": end_time,
        "status": "scheduled",
        "reason": "First appointment"
    }
    service.create(appointment1_data)
    
    # Try to create overlapping appointment
    appointment2_data = {
        "doctor_id": test_doctor.id,
        "patient_id": test_patient.id,
        "start_time": start_time + timedelta(minutes=30),  # Overlaps with first appointment
        "end_time": end_time + timedelta(minutes=30),
        "status": "scheduled",
        "reason": "Second appointment"
    }
    with pytest.raises(ValueError):
        service.create(appointment2_data)

def test_doctor_patient_assignment_service_unique_constraint(db, test_doctor, test_patient):
    """Test doctor-patient assignment service unique constraint"""
    service = DoctorPatientAssignmentService(db)
    
    # Create first assignment
    assignment1_data = {
        "doctor_id": test_doctor.id,
        "patient_id": test_patient.id,
        "is_active": True
    }
    service.create(assignment1_data)
    
    # Try to create duplicate assignment
    assignment2_data = {
        "doctor_id": test_doctor.id,
        "patient_id": test_patient.id,
        "is_active": True
    }
    with pytest.raises(IntegrityError):
        service.create(assignment2_data) 