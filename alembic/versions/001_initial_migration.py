"""initial migration

Revision ID: 001
Revises: 
Create Date: 2024-04-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create enum type for appointment status
    appointment_status = postgresql.ENUM(
        'scheduled', 'confirmed', 'cancelled', 'completed', 'no_show',
        name='appointment_status'
    )
    appointment_status.create(op.get_bind())

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(200), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('last_login', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=sa.func.utcnow()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.utcnow(), onupdate=sa.func.utcnow())
    )

    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, unique=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('date_of_birth', sa.Date, nullable=False),
        sa.Column('gender', sa.String(10), nullable=False),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('address', sa.String(200)),
        sa.Column('emergency_contact', sa.String(100)),
        sa.Column('emergency_phone', sa.String(20)),
        sa.Column('medical_history', sa.String(500)),
        sa.Column('insurance_info', sa.String(200)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.utcnow()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.utcnow(), onupdate=sa.func.utcnow())
    )

    # Create doctors table
    op.create_table(
        'doctors',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, unique=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('specialization', sa.String(100), nullable=False),
        sa.Column('license_number', sa.String(50), nullable=False, unique=True),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('office_address', sa.String(200)),
        sa.Column('bio', sa.Text),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.utcnow()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.utcnow(), onupdate=sa.func.utcnow())
    )

    # Create doctor_schedules table
    op.create_table(
        'doctor_schedules',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('doctor_id', sa.String(36), sa.ForeignKey('doctors.id'), nullable=False),
        sa.Column('day_of_week', sa.Integer, nullable=False),
        sa.Column('start_time', sa.DateTime, nullable=False),
        sa.Column('end_time', sa.DateTime, nullable=False),
        sa.Column('is_available', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.utcnow()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.utcnow(), onupdate=sa.func.utcnow())
    )

    # Create appointments table
    op.create_table(
        'appointments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('patient_id', sa.String(36), sa.ForeignKey('patients.id'), nullable=False),
        sa.Column('doctor_id', sa.String(36), sa.ForeignKey('doctors.id'), nullable=False),
        sa.Column('appointment_date', sa.DateTime, nullable=False),
        sa.Column('duration_minutes', sa.Integer, nullable=False, default=30),
        sa.Column('status', appointment_status, nullable=False, default='scheduled'),
        sa.Column('reason', sa.Text),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, default=sa.func.utcnow()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.utcnow(), onupdate=sa.func.utcnow())
    )

    # Add constraints
    op.create_check_constraint(
        'check_duration_minutes',
        'appointments',
        'duration_minutes >= 15 AND duration_minutes <= 120'
    )
    op.create_check_constraint(
        'check_appointment_date',
        'appointments',
        'appointment_date > created_at'
    )

def downgrade():
    # Drop tables in reverse order
    op.drop_table('appointments')
    op.drop_table('doctor_schedules')
    op.drop_table('doctors')
    op.drop_table('patients')
    op.drop_table('users')

    # Drop enum type
    appointment_status = postgresql.ENUM(
        'scheduled', 'confirmed', 'cancelled', 'completed', 'no_show',
        name='appointment_status'
    )
    appointment_status.drop(op.get_bind()) 