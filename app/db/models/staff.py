from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base_class import Base

class Staff(Base):
    __tablename__ = "staff"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), unique=True, nullable=False)
    department = Column(String, nullable=False)
    position = Column(String, nullable=False)
    status = Column(String, nullable=False, default='unverified')
    hire_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with User - staff belongs to one user
    user = relationship("User", back_populates="staff_profile")

    def __repr__(self):
        return f"<Staff {self.department} - {self.position}>" 