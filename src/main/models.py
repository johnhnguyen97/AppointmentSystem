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
from sqlalchemy.orm import relationship, declarative_mixin, declared_attr
from sqlalchemy.sql import func, text
from uuid import uuid4
from datetime import datetime, timezone, UTC
from sqlalchemy.orm import declarative_base, registry

mapper_registry = registry()
Base = declarative_base()

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

class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID, primary_key=True, default=uuid4)
    sequential_id = Column(Integer, 
                         server_default=text("nextval('user_sequential_id_seq')"),
                         unique=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    enabled = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Relationships
    created_appointments = relationship(
        "Appointment",
        primaryjoin="User.id==Appointment.creator_id",
        backref="creator",
        foreign_keys="[Appointment.creator_id]"
    )
    attending_appointments = relationship(
        "Appointment",
        secondary=appointment_attendees,
        back_populates="attendees"
    )
    client_profile = relationship(
        "Client",
        back_populates="user",
        uselist=False
    )

class Client(Base):
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID, primary_key=True, default=uuid4)
    phone = Column(String(20), nullable=False)
    service = Column(String, nullable=False)
    status = Column(String(20), nullable=False, default='active')
    notes = Column(String(500))
    
    # Foreign key to User with unique constraint
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Relationships
    user = relationship(
        "User",
        back_populates="client_profile",
        overlaps="client_profile"
    )
    service_history = relationship(
        "ServiceHistory",
        back_populates="client",
        cascade="all, delete-orphan"
    )

def validate_appointment(mapper, connection, target):
    # Validate start_time is not in the past
    if target.start_time < datetime.now(timezone.utc):
        raise ValueError("Appointment start time cannot be in the past")
    
    # Validate duration_minutes
    if target.duration_minutes < 15:
        raise ValueError("Appointment duration must be at least 15 minutes")
    if target.duration_minutes > 480:
        raise ValueError("Appointment duration cannot exceed 8 hours (480 minutes)")

class Appointment(TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID, primary_key=True, default=uuid4)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    start_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(SQLEnum(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED)
    
    # Foreign Keys
    creator_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    attendees = relationship(
        "User",
        secondary=appointment_attendees,
        back_populates="attending_appointments"
    )

class ServiceHistory(TimestampMixin, Base):
    __tablename__ = "service_history"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID, primary_key=True, default=uuid4)
    client_id = Column(UUID, ForeignKey('clients.id'), nullable=False)
    service_type = Column(String, nullable=False)
    provider_name = Column(String, nullable=False)
    date_of_service = Column(DateTime(timezone=True), nullable=False)
    notes = Column(String(500))
    
    # Relationships
    client = relationship(
        "Client",
        back_populates="service_history"
    )

def ensure_timestamps(mapper, connection, target):
    if not target.updated_at:
        target.updated_at = datetime.now(UTC)

# Register the event listeners
event.listen(Appointment, 'before_insert', validate_appointment)
event.listen(Appointment, 'before_update', validate_appointment)
event.listen(User, 'before_insert', ensure_timestamps)
event.listen(Appointment, 'before_insert', ensure_timestamps)
event.listen(ServiceHistory, 'before_insert', ensure_timestamps)
