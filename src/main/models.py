# src/main/models.py
from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Integer, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from src.main.database import Base
from src.main.schema import AppointmentStatus

# Association table for appointment attendees
appointment_attendees = Table(
    'appointment_attendees',
    Base.metadata,
    Column('user_id', UUID, ForeignKey('users.id'), primary_key=True),
    Column('appointment_id', UUID, ForeignKey('appointments.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True, default=uuid4, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    enabled = Column(Boolean, default=True)
    
    # Relationships
    created_appointments = relationship("Appointment", back_populates="creator", foreign_keys="[Appointment.creator_id]")
    attending_appointments = relationship("Appointment", secondary=appointment_attendees, back_populates="attendees")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(UUID, primary_key=True, default=uuid4, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    start_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(SQLEnum(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign Keys
    creator_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="created_appointments", foreign_keys=[creator_id])
    attendees = relationship("User", secondary=appointment_attendees, back_populates="attending_appointments")
