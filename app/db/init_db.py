from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.db.models import User, Patient, Doctor, Staff, Appointment, MedicalRecord, DoctorSchedule

def init_db(db: Session) -> None:
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            # Create admin user
            from app.core.security import get_password_hash
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

if __name__ == "__main__":
    init_db() 