from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate

class StaffService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: str) -> Optional[Staff]:
        return self.db.query(Staff).filter(Staff.id == id).first()

    def get_by_user_id(self, user_id: str) -> Optional[Staff]:
        return self.db.query(Staff).filter(Staff.user_id == user_id).first()

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[Staff]:
        return self.db.query(Staff).offset(skip).limit(limit).all()

    def create(self, obj_in: StaffCreate) -> Staff:
        db_obj = Staff(
            id=obj_in.id,
            user_id=obj_in.user_id,
            department=obj_in.department,
            position=obj_in.position,
            hire_date=obj_in.hire_date
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: Staff, obj_in: StaffUpdate) -> Staff:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, id: str) -> Staff:
        obj = self.db.query(Staff).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj 