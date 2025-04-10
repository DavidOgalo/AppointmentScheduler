from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models.staff import Staff
from app.db.models.user import User
from app.schemas.staff import StaffCreate, StaffUpdate
from app.services.base import BaseService

class StaffService(BaseService[Staff, StaffCreate, StaffUpdate]):
    def __init__(self, db: Session):
        super().__init__(db, Staff)

    def get(self, id: str) -> Optional[Staff]:
        return self.db.query(Staff).filter(Staff.id == id).first()

    def get_by_user_id(self, user_id: str) -> Optional[Staff]:
        return self.db.query(Staff).join(User).filter(User.id == user_id).first()

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[Staff]:
        return self.db.query(Staff).offset(skip).limit(limit).all()

    def create(self, obj_in: StaffCreate) -> Staff:
        db_obj = Staff(
            user_id=obj_in.user_id,
            department=obj_in.department,
            position=obj_in.position,
            status=obj_in.status,
            hire_date=obj_in.hire_date
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: str, obj_in: StaffUpdate) -> Staff:
        db_obj = self.get(id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def remove(self, id: str) -> Staff:
        obj = self.db.query(Staff).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj 