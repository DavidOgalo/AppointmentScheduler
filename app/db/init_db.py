from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config.config import settings
from app.db.base_class import Base
from app.db.models.user import User
from app.db.models.patient import Patient
from app.db.models.doctor import Doctor
from app.db.models.appointment import Appointment
from app.db.models.staff import Staff
from app.db.models.medical_record import MedicalRecord
from app.db.models.doctor_schedule import DoctorSchedule

def init_db() -> None:
    # Create all tables
    engine = create_engine(str(settings.DATABASE_URL))
    Base.metadata.create_all(bind=engine)

    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            # Create admin user
            from app.core.security.security import get_password_hash
            admin_user = User(
                email="admin@example.com",
                username="admin",
                full_name="System Administrator",
                password_hash=get_password_hash("Admin@123"),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 