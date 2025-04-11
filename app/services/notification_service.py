from app.core.rabbitmq import RabbitMQ
from app.db.session import SessionLocal
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from typing import List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    async def send_notification(notification: NotificationCreate):
        """
        Send a notification using RabbitMQ
        """
        try:
            # Store notification in database
            db = SessionLocal()
            try:
                db_notification = Notification(
                    user_id=notification.user_id,
                    type=notification.type,
                    content=notification.content
                )
                db.add(db_notification)
                db.commit()
                db.refresh(db_notification)
                
                # Publish to RabbitMQ
                message = {
                    "notification_id": str(db_notification.id),
                    "user_id": str(notification.user_id),
                    "type": notification.type,
                    "content": notification.content
                }
                await RabbitMQ.publish_message(
                    "notifications",
                    json.dumps(message)
                )
                logger.info(f"Notification sent: {message}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise

    @staticmethod
    async def send_appointment_reminder(appointment_id: str):
        """
        Send appointment reminder notification
        """
        db = SessionLocal()
        try:
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if not appointment:
                raise ValueError(f"Appointment {appointment_id} not found")
            
            notification = NotificationCreate(
                user_id=appointment.patient_id,
                type="appointment_reminder",
                content=f"Reminder: You have an appointment with Dr. {appointment.doctor.first_name} "
                       f"on {appointment.start_time.strftime('%Y-%m-%d %H:%M')}"
            )
            await NotificationService.send_notification(notification)
        finally:
            db.close()

    @staticmethod
    async def send_follow_up(medical_record_id: str):
        """
        Send follow-up notification
        """
        db = SessionLocal()
        try:
            medical_record = db.query(MedicalRecord).filter(MedicalRecord.id == medical_record_id).first()
            if not medical_record:
                raise ValueError(f"Medical record {medical_record_id} not found")
            
            notification = NotificationCreate(
                user_id=medical_record.patient_id,
                type="follow_up",
                content=f"Follow-up required for your recent appointment. "
                       f"Please schedule a follow-up visit with Dr. {medical_record.doctor.first_name}"
            )
            await NotificationService.send_notification(notification)
        finally:
            db.close()

    @staticmethod
    async def mark_notification_as_read(notification_id: str):
        """
        Mark a notification as read
        """
        db = SessionLocal()
        try:
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            if notification:
                notification.is_read = True
                db.commit()
        finally:
            db.close()

    @staticmethod
    async def get_user_notifications(user_id: str, skip: int = 0, limit: int = 100) -> List[Notification]:
        """
        Get notifications for a user
        """
        db = SessionLocal()
        try:
            return db.query(Notification)\
                .filter(Notification.user_id == user_id)\
                .order_by(Notification.created_at.desc())\
                .offset(skip)\
                .limit(limit)\
                .all()
        finally:
            db.close()

    @staticmethod
    async def get_unread_notifications_count(user_id: str) -> int:
        """
        Get count of unread notifications for a user
        """
        db = SessionLocal()
        try:
            return db.query(Notification)\
                .filter(Notification.user_id == user_id, Notification.is_read == False)\
                .count()
        finally:
            db.close()
