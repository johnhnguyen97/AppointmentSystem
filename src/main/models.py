# src/main/models.py
from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Integer, Float, Enum as SQLEnum, Table, event, and_, or_
from sqlalchemy.future import select
from enum import StrEnum
from datetime import datetime, timezone, UTC, timedelta

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
from sqlalchemy.orm import declarative_base, registry, Session

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
        uselist=False,
        cascade="all, delete-orphan"
    )

class Client(Base):
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID, primary_key=True, default=uuid4)
    phone = Column(String(20), nullable=False)
    service = Column(SQLEnum(ServiceType), nullable=False)
    status = Column(String(20), nullable=False, default='active')
    notes = Column(String(500))
    category = Column(String(20), nullable=False, default='NEW')
    loyalty_points = Column(Integer, nullable=False, default=0)
    referred_by = Column(UUID, ForeignKey('clients.id'), nullable=True)
    
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
    service_packages = relationship(
        "ServicePackage",
        back_populates="client",
        cascade="all, delete-orphan"
    )

def validate_appointment(mapper, connection, target):
    """Validate appointment rules and set calculated fields"""
    # Validate start_time is not in the past
    if target.start_time < datetime.now(timezone.utc):
        raise ValueError("Appointment start time cannot be in the past")
    
    # Validate duration_minutes
    if target.duration_minutes < 15:
        raise ValueError("Appointment duration must be at least 15 minutes")
    if target.duration_minutes > 480:
        raise ValueError("Appointment duration cannot exceed 8 hours (480 minutes)")

    # Calculate end_time
    end_time = target.start_time + timedelta(minutes=target.duration_minutes)
    target.end_time = end_time

    # Check for overlapping appointments using text-based SQL
    result = connection.execute(text("""
        SELECT COUNT(1) as overlap_count
        FROM appointments
        WHERE id != :id
        AND status != 'CANCELLED'
        AND (:start_time < end_time AND :end_time > start_time)
    """), {
        'id': str(target.id) if target.id else '00000000-0000-0000-0000-000000000000',
        'start_time': target.start_time,
        'end_time': end_time
    }).scalar()

    if result and result > 0:
        overlapping = connection.execute(text("""
            SELECT start_time
            FROM appointments
            WHERE id != :id
            AND status != 'CANCELLED'
            AND (:start_time < end_time AND :end_time > start_time)
            LIMIT 1
        """), {
            'id': str(target.id) if target.id else '00000000-0000-0000-0000-000000000000',
            'start_time': target.start_time,
            'end_time': end_time
        }).scalar()
        raise ValueError(f"There is already an overlapping appointment at {overlapping}")

class Appointment(TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID, primary_key=True, default=uuid4)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    start_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED)
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    buffer_time = Column(Integer, nullable=False, default=0)
    is_recurring = Column(Boolean, nullable=False, default=False)
    recurrence_pattern = Column(String(20), nullable=True)
    
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
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    provider_name = Column(String, nullable=False)
    date_of_service = Column(DateTime(timezone=True), nullable=False)
    notes = Column(String(500))
    service_cost = Column(Float, nullable=True)
    loyalty_points_earned = Column(Integer, nullable=False, default=0)
    points_redeemed = Column(Integer, nullable=False, default=0)
    package_id = Column(UUID, ForeignKey('service_packages.id'), nullable=True)
    
    # Relationships
    client = relationship(
        "Client",
        back_populates="service_history"
    )
    package = relationship("ServicePackage", back_populates="services")

class ServicePackage(TimestampMixin, Base):
    __tablename__ = "service_packages"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID, primary_key=True, default=uuid4)
    client_id = Column(UUID, ForeignKey('clients.id'), nullable=False)
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    total_sessions = Column(Integer, nullable=False)
    sessions_remaining = Column(Integer, nullable=False)
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    package_cost = Column(Float, nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="service_packages")
    services = relationship("ServiceHistory", back_populates="package")

def update_loyalty_points(mapper, connection, target):
    """Update client loyalty points when service history is added"""
    # Get the client
    client = connection.execute(text("""
        UPDATE clients
        SET loyalty_points = loyalty_points + :points
        WHERE id = :client_id
        RETURNING loyalty_points
    """), {
        'points': target.loyalty_points_earned,
        'client_id': target.client_id
    }).scalar()

def ensure_timestamps(mapper, connection, target):
    if not target.updated_at:
        target.updated_at = datetime.now(UTC)

# Register the event listeners
event.listen(Appointment, 'before_insert', validate_appointment)
event.listen(Appointment, 'before_update', validate_appointment)
event.listen(User, 'before_insert', ensure_timestamps)
event.listen(Appointment, 'before_insert', ensure_timestamps)
event.listen(ServiceHistory, 'before_insert', ensure_timestamps)
event.listen(ServiceHistory, 'after_insert', update_loyalty_points)
