from sqlalchemy import String, Column, DateTime, Integer, Boolean, Float, ForeignKey, Table, text, func, event
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import relationship, declarative_mixin, declared_attr
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.elements import Cast
from typing import Union
from sqlalchemy.orm import declarative_base, registry, Session
from enum import StrEnum
from datetime import datetime, timezone, UTC, timedelta
from nanoid import generate
from enum import StrEnum
import logging

logger = logging.getLogger(__name__)

class AppointmentStatus(StrEnum):
    SCHEDULED = 'SCHEDULED'
    CONFIRMED = 'CONFIRMED'
    CANCELLED = 'CANCELLED'
    COMPLETED = 'COMPLETED'
    DECLINED = 'DECLINED'

# Custom Enum Type for SQLAlchemy
class EnumType(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            return value
        return value.value if value else None

    def process_result_value(self, value, dialect):
        return self._enumtype(value) if value else None

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

    @classmethod
    def get_duration_minutes(cls, service: 'ServiceType') -> int:
        durations = {
            cls.HAIRCUT: 30,
            cls.MANICURE: 45,
            cls.PEDICURE: 60,
            cls.FACIAL: 60,
            cls.MASSAGE: 60,
            cls.HAIRCOLOR: 120,
            cls.HAIRSTYLE: 45,
            cls.MAKEUP: 60,
            cls.WAXING: 30,
            cls.OTHER: 30
        }
        return durations.get(service, 30)

    @classmethod
    def get_base_cost(cls, service: 'ServiceType') -> float:
        costs = {
            cls.HAIRCUT: 30.0,
            cls.MANICURE: 25.0,
            cls.PEDICURE: 35.0,
            cls.FACIAL: 65.0,
            cls.MASSAGE: 75.0,
            cls.HAIRCOLOR: 100.0,
            cls.HAIRSTYLE: 45.0,
            cls.MAKEUP: 55.0,
            cls.WAXING: 30.0,
            cls.OTHER: 40.0
        }
        return costs.get(service, 40.0)

    @classmethod
    def get_loyalty_points(cls, service: 'ServiceType') -> int:
        points = {
            cls.HAIRCUT: 10,
            cls.MANICURE: 8,
            cls.PEDICURE: 12,
            cls.FACIAL: 15,
            cls.MASSAGE: 20,
            cls.HAIRCOLOR: 25,
            cls.HAIRSTYLE: 12,
            cls.MAKEUP: 15,
            cls.WAXING: 10,
            cls.OTHER: 10
        }
        return points.get(service, 10)

def generate_nanoid():
    return generate(size=21)

mapper_registry = registry()
Base = declarative_base()

@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def touch(self):
        self.updated_at = datetime.now(UTC)

# Association table for appointment attendees
appointment_attendees = Table(
    'appointment_attendees',
    Base.metadata,
    Column('user_id', String(21), ForeignKey('users.id'), primary_key=True),
    Column('appointment_id', String(21), ForeignKey('appointments.id'), primary_key=True),
    extend_existing=True
)

class User(TimestampMixin, Base):
    """User model with authentication support."""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(String(21), primary_key=True, default=generate_nanoid)
    sequential_id = Column(Integer, server_default=text("nextval('user_sequential_id_seq')"), unique=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)  # For testing, store raw password for admin
    first_name = Column(String)
    last_name = Column(String)
    enabled = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    created_appointments = relationship(
        "Appointment",
        primaryjoin="User.id==Appointment.creatorId",
        backref="creator",
        foreign_keys="[Appointment.creatorId]"
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

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, is_admin={self.is_admin})>"

class ClientCategory(StrEnum):
    NEW = "NEW"
    REGULAR = "REGULAR"
    VIP = "VIP"
    PREMIUM = "PREMIUM"

class ClientStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"

class Client(Base):
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}

    id = Column(String(21), primary_key=True, default=generate_nanoid)
    phone = Column(String(20), nullable=False)
    service = Column(EnumType(ServiceType), nullable=False)
    status = Column(EnumType(ClientStatus), nullable=False, default=ClientStatus.ACTIVE)
    notes = Column(String(500))
    category = Column(EnumType(ClientCategory), nullable=False, default=ClientCategory.NEW)
    loyalty_points = Column(Integer, nullable=False, default=0)
    total_spent = Column(Float, nullable=False, default=0.0)
    last_visit = Column(DateTime(timezone=True), nullable=True)
    visit_count = Column(Integer, nullable=False, default=0)
    user_id = Column(String(21), ForeignKey('users.id'), nullable=False, unique=True)

    user = relationship("User", back_populates="client_profile", overlaps="client_profile")
    service_packages = relationship("ServicePackage", back_populates="client", cascade="all, delete-orphan")
    service_history = relationship("ServiceHistory", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(id={self.id}, user_id={self.user_id}, status={self.status})>"

class Appointment(TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = {'extend_existing': True}

    id = Column(String(21), primary_key=True, default=generate_nanoid)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    startTime = Column('start_time', DateTime(timezone=True), nullable=False)
    durationMinutes = Column('duration_minutes', Integer, nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(EnumType(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED)
    serviceType = Column('service_type', EnumType(ServiceType), nullable=False)
    creatorId = Column('creator_id', String(21), ForeignKey('users.id'), nullable=False)

    attendees = relationship(
        "User",
        secondary=appointment_attendees,
        back_populates="attending_appointments"
    )

    @property
    def estimated_cost(self) -> Union[float, Column, Cast]:
        return calculate_appointment_cost(self.serviceType, self.durationMinutes)

class ServiceHistory(TimestampMixin, Base):
    __tablename__ = "service_history"
    __table_args__ = {'extend_existing': True}

    id = Column(String(21), primary_key=True, default=generate_nanoid)
    client_id = Column(String(21), ForeignKey('clients.id'), nullable=False)
    service_type = Column(EnumType(ServiceType), nullable=False)
    provider_name = Column(String, nullable=False)
    date_of_service = Column(DateTime(timezone=True), nullable=False)
    notes = Column(String(500))
    service_cost = Column(Float, nullable=False)
    loyalty_points_earned = Column(Integer, nullable=False, default=0)
    points_redeemed = Column(Integer, nullable=False, default=0)
    satisfaction_rating = Column(Integer, nullable=True)
    feedback = Column(String(1000), nullable=True)
    service_duration = Column(Integer, nullable=False)
    package_id = Column(String(21), ForeignKey('service_packages.id'), nullable=True)

    client = relationship("Client", back_populates="service_history")
    package = relationship("ServicePackage", back_populates="service_history")

class ServicePackage(TimestampMixin, Base):
    __tablename__ = "service_packages"
    __table_args__ = {'extend_existing': True}

    id = Column(String(21), primary_key=True, default=generate_nanoid)
    client_id = Column(String(21), ForeignKey('clients.id'), nullable=False)
    service_type = Column(EnumType(ServiceType), nullable=False)
    total_sessions = Column(Integer, nullable=False)
    client = relationship("Client", back_populates="service_packages")
    service_history = relationship("ServiceHistory", back_populates="package")
    sessions_remaining = Column(Integer, nullable=False)
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    package_cost = Column(Float, nullable=False)
    minimum_interval = Column(Integer, nullable=False, default=1)
    last_session_date = Column(DateTime(timezone=True), nullable=True)
    average_satisfaction = Column(Float, nullable=True)

def calculate_appointment_cost(service_type: Union[ServiceType, Column], duration_minutes: Union[int, Column]) -> Union[float, Column, Cast]:
    # Handle SQL expression case
    if hasattr(service_type, 'is_clause_element'):
        base_cost = 40.0  # Default cost for SQL expressions
        default_duration = 30  # Default duration for SQL expressions
        # Return the SQL expression directly as a Column type
        return cast(base_cost * cast(duration_minutes, Float) / default_duration, Float)

    # Handle direct value case
    service_instance = service_type if isinstance(service_type, ServiceType) else ServiceType(service_type)
    base_cost = ServiceType.get_base_cost(service_instance)
    default_duration = ServiceType.get_duration_minutes(service_instance)

    if hasattr(duration_minutes, 'is_clause_element'):
        # Return the SQL expression directly as a Column type
        return cast(base_cost * cast(duration_minutes, Float) / default_duration, Float)

    # Handle numeric value case
    if hasattr(duration_minutes, 'is_clause_element'):
        # Already handled above
        return cast(base_cost * cast(duration_minutes, Float) / default_duration, Float)
    else:
        # Direct numeric value comparison is safe here
        if isinstance(duration_minutes, int) or isinstance(duration_minutes, float):
            duration_numeric = float(duration_minutes)
            if duration_numeric != default_duration:
                return float(base_cost * (duration_numeric / default_duration))
            return float(base_cost)
        else:
            # This should not happen due to the checks above, but adding as a fallback
            return cast(base_cost * cast(duration_minutes, Float) / default_duration, Float)

def validate_appointment(mapper, connection, target):
    target.end_time = target.startTime + timedelta(minutes=target.durationMinutes)

    # Check for overlapping appointments
    stmt = text("""
        SELECT COUNT(1) FROM appointments
        WHERE status != :cancelled
        AND (:start_time < end_time AND :end_time > start_time)
        AND id != :id
    """)
    result = connection.execute(
        stmt,
        {
            'cancelled': AppointmentStatus.CANCELLED.value,
            'start_time': target.startTime,
            'end_time': target.end_time,
            'id': target.id or ''
        }
    ).scalar()

    if result > 0:
        raise ValueError("This time slot is already booked")

event.listen(Appointment, 'before_insert', validate_appointment)
event.listen(Appointment, 'before_update', validate_appointment)
