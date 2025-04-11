import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, time
from uuid import uuid4
import os

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.db.models.user import User
from app.db.models.doctor import Doctor
from app.db.models.patient import Patient
from app.db.models.staff import Staff

# Use PostgreSQL for testing if TEST_DATABASE_URL is set, otherwise use SQLite
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:se2025@localhost:5434/appointment_test"
)

# Create test database engine
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password_hash="hashed_password",
        role="patient",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_doctor(db):
    doctor = Doctor(
        first_name="Test",
        last_name="Doctor",
        specialization="General Medicine",
        email="doctor@example.com",
        phone="1234567890",
        license_number="MD123456",
        is_active=True
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

@pytest.fixture
def test_patient(db):
    patient = Patient(
        first_name="Test",
        last_name="Patient",
        date_of_birth=date(1990, 1, 1),
        email="patient@example.com",
        phone="0987654321",
        address="123 Test St",
        insurance_info={"provider": "Test Insurance"}
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

@pytest.fixture
def test_staff(db):
    staff = Staff(
        department="Administration",
        position="Receptionist",
        status="active"
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff

@pytest.fixture
def test_token(test_user):
    return create_access_token(
        subject=test_user.id,
        role=test_user.role,
        expires_delta=None
    )

@pytest.fixture
def test_doctor_token(test_doctor):
    # Create a user for the doctor
    doctor_user = User(
        id=uuid4(),
        username="doctortest",
        email="doctortest@example.com",
        full_name="Doctor Test",
        password_hash="hashed_password",
        role="doctor",
        doctor_id=test_doctor.id,
        is_active=True
    )
    return create_access_token({"sub": str(doctor_user.id)})

@pytest.fixture
def test_patient_token(test_patient):
    # Create a user for the patient
    patient_user = User(
        id=uuid4(),
        username="patienttest",
        email="patienttest@example.com",
        full_name="Patient Test",
        password_hash="hashed_password",
        role="patient",
        patient_id=test_patient.id,
        is_active=True
    )
    return create_access_token({"sub": str(patient_user.id)})

@pytest.fixture
def test_staff_token(test_staff):
    # Create a user for the staff
    staff_user = User(
        id=uuid4(),
        username="stafftest",
        email="stafftest@example.com",
        full_name="Staff Test",
        password_hash="hashed_password",
        role="staff",
        is_active=True
    )
    return create_access_token({"sub": str(staff_user.id)}) 