"""seed data

Revision ID: 002
Revises: 001
Create Date: 2024-04-08 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, time
from app.core.security.security import get_password_hash

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Create admin user
    op.execute("""
        INSERT INTO users (id, username, email, password_hash, role, is_active, created_at, updated_at)
        VALUES (
            '00000000-0000-0000-0000-000000000000',
            'admin',
            'admin@healthcare.com',
            '{}',
            'admin',
            true,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
    """.format(get_password_hash("admin123")))

    # Create sample doctors
    doctors = [
        {
            'id': '11111111-1111-1111-1111-111111111111',
            'username': 'dr_smith',
            'email': 'dr.smith@healthcare.com',
            'password_hash': get_password_hash("doctor123"),
            'first_name': 'John',
            'last_name': 'Smith',
            'specialization': 'Cardiology',
            'license_number': 'MD123456',
            'phone_number': '+1234567890',
            'office_address': '123 Medical Center Dr, Suite 100',
            'bio': 'Board-certified cardiologist with 15 years of experience.'
        },
        {
            'id': '22222222-2222-2222-2222-222222222222',
            'username': 'dr_jones',
            'email': 'dr.jones@healthcare.com',
            'password_hash': get_password_hash("doctor123"),
            'first_name': 'Sarah',
            'last_name': 'Jones',
            'specialization': 'Pediatrics',
            'license_number': 'MD789012',
            'phone_number': '+1987654321',
            'office_address': '456 Children\'s Hospital Ave, Suite 200',
            'bio': 'Pediatric specialist with a focus on preventive care.'
        }
    ]

    for doctor in doctors:
        # Create user
        op.execute("""
            INSERT INTO users (id, username, email, password_hash, role, is_active, created_at, updated_at)
            VALUES (
                '{}',
                '{}',
                '{}',
                '{}',
                'doctor',
                true,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
        """.format(
            doctor['id'],
            doctor['username'],
            doctor['email'],
            doctor['password_hash']
        ))

        # Create doctor
        op.execute("""
            INSERT INTO doctors (
                id, user_id, first_name, last_name, specialization,
                license_number, phone_number, email, office_address, bio,
                is_active, created_at, updated_at
            )
            VALUES (
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                true,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
        """.format(
            doctor['id'],
            doctor['id'],
            doctor['first_name'],
            doctor['last_name'],
            doctor['specialization'],
            doctor['license_number'],
            doctor['phone_number'],
            doctor['email'],
            doctor['office_address'],
            doctor['bio']
        ))

        # Create doctor schedules (Monday to Friday, 9 AM to 5 PM)
        for day in range(5):  # Monday to Friday
            op.execute("""
                INSERT INTO doctor_schedules (
                    id, doctor_id, day_of_week, start_time, end_time,
                    is_available, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(),
                    '{}',
                    {},
                    '{}',
                    '{}',
                    true,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
            """.format(
                doctor['id'],
                day,
                time(9, 0).strftime('%H:%M:%S'),
                time(17, 0).strftime('%H:%M:%S')
            ))

    # Create sample patients
    patients = [
        {
            'id': '33333333-3333-3333-3333-333333333333',
            'username': 'patient1',
            'email': 'patient1@example.com',
            'password_hash': get_password_hash("patient123"),
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'date_of_birth': '1985-06-15',
            'gender': 'Female',
            'phone_number': '+1122334455',
            'address': '789 Patient St, Apt 101',
            'emergency_contact': 'Bob Johnson',
            'emergency_phone': '+1555666777',
            'medical_history': 'No significant medical history',
            'insurance_info': 'ABC Insurance, Policy #123456'
        },
        {
            'id': '44444444-4444-4444-4444-444444444444',
            'username': 'patient2',
            'email': 'patient2@example.com',
            'password_hash': get_password_hash("patient123"),
            'first_name': 'Michael',
            'last_name': 'Brown',
            'date_of_birth': '1990-03-22',
            'gender': 'Male',
            'phone_number': '+1444555666',
            'address': '321 Health Ave, Unit 202',
            'emergency_contact': 'Lisa Brown',
            'emergency_phone': '+1888999000',
            'medical_history': 'Allergic to penicillin',
            'insurance_info': 'XYZ Insurance, Policy #789012'
        }
    ]

    for patient in patients:
        # Create user
        op.execute("""
            INSERT INTO users (id, username, email, password_hash, role, is_active, created_at, updated_at)
            VALUES (
                '{}',
                '{}',
                '{}',
                '{}',
                'patient',
                true,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
        """.format(
            patient['id'],
            patient['username'],
            patient['email'],
            patient['password_hash']
        ))

        # Create patient
        op.execute("""
            INSERT INTO patients (
                id, user_id, first_name, last_name, date_of_birth,
                gender, phone_number, address, emergency_contact,
                emergency_phone, medical_history, insurance_info,
                is_active, created_at, updated_at
            )
            VALUES (
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                '{}',
                true,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
        """.format(
            patient['id'],
            patient['id'],
            patient['first_name'],
            patient['last_name'],
            patient['date_of_birth'],
            patient['gender'],
            patient['phone_number'],
            patient['address'],
            patient['emergency_contact'],
            patient['emergency_phone'],
            patient['medical_history'],
            patient['insurance_info']
        ))

def downgrade():
    # Delete all data
    op.execute("DELETE FROM appointments")
    op.execute("DELETE FROM doctor_schedules")
    op.execute("DELETE FROM doctors")
    op.execute("DELETE FROM patients")
    op.execute("DELETE FROM users WHERE role != 'admin'") 