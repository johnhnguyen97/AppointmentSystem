# src/main/models.py
from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Integer, Enum as SQLEnum, Table, event
from enum import StrEnum

class ServiceType(StrEnum):
    HAIRCUT = "Hair Cut"
    MANICURE = "Manicure"
    PEDICURE = "Pedicure"
    FACIAL = "Facial"
    MASSAGE = "Massage"
    HAIRCOLOR = "Hair Color"
    HAIRSTYLE = "Hair Style"
    MAKEUP = "Makeup"
    WAXING = "Waxing"
    OTHER = "Other"
from sqlalchemy.ext.hybrid import hybrid_property
from src.main.schema import AppointmentStatus
from sqlalchemy.orm import relationship, declarative_mixin
from sqlalchemy.sql import func, text
from uuid import uuid4
from datetime import datetime
from src.main.database import Base

@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def touch(self):
        self.updated_at = datetime.utcnow()

# Association table for appointment attendees
appointment_attendees = Table(
    'appointment_attendees',
    Base.metadata,
    Column('user_id', UUID, ForeignKey('users.id'), primary_key=True),
    Column('appointment_id', UUID, ForeignKey('appointments.id'), primary_key=True),
    extend_existing=True
)

class Client(Base):
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    phone = Column(String(20), nullable=False)
    service = Column(SQLEnum(ServiceType), nullable=False)
    status = Column(String(20), nullable=False, default='active')
    notes = Column(String(500))
    
    # Foreign key to User with unique constraint
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False, unique=True)
    # Relationship
    user = relationship("User", back_populates="client_profile")

class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID, primary_key=True, default=uuid4, index=True)
    sequential_id = Column(Integer, unique=True, index=True, 
                         server_default=text("nextval('user_sequential_id_seq')"))  # Auto-incrementing ID
    username = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    enabled = Column(Boolean, default=True)
    
    # Relationships
    created_appointments = relationship("Appointment", back_populates="creator", foreign_keys="[Appointment.creator_id]")
    attending_appointments = relationship("Appointment", secondary=appointment_attendees, back_populates="attendees")
    client_profile = relationship("Client", back_populates="user", uselist=False)

def validate_appointment(mapper, connection, target):
    # Validate start_time is not in the past
    if target.start_time < datetime.now():
        raise ValueError("Appointment start time cannot be in the past")
    
    # Validate duration_minutes
    if target.duration_minutes < 15:
        raise ValueError("Appointment duration must be at least 15 minutes")
    if target.duration_minutes > 480:
        raise ValueError("Appointment duration cannot exceed 8 hours (480 minutes)")

class Appointment(TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID, primary_key=True, default=uuid4, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    start_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(SQLEnum(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED)
    
    # Foreign Keys
    creator_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="created_appointments", foreign_keys=[creator_id])
    attendees = relationship("User", secondary=appointment_attendees, back_populates="attending_appointments")

def ensure_timestamps(mapper, connection, target):
    if not target.updated_at:
        target.updated_at = datetime.utcnow()

# Register the event listeners
event.listen(Appointment, 'before_insert', validate_appointment)
event.listen(Appointment, 'before_update', validate_appointment)
event.listen(User, 'before_insert', ensure_timestamps)
event.listen(Appointment, 'before_insert', ensure_timestamps)
