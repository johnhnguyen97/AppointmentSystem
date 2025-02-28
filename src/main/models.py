# src/main/models.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Float, Enum as SQLEnum, Table, event, and_, or_
from sqlalchemy.future import select
from enum import StrEnum
from datetime import datetime, timezone, UTC, timedelta
from nanoid import generate
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, declarative_mixin, declared_attr, declarative_base, registry, Session
from sqlalchemy.sql import func, text
from src.main.schema import AppointmentStatus
from src.main.config import settings, ServiceType

def generate_nanoid():
    return generate(size=21)  # Default nanoid size

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
    Column('user_id', String(21), ForeignKey('users.id'), primary_key=True),
    Column('appointment_id', String(21), ForeignKey('appointments.id'), primary_key=True),
    extend_existing=True
)

class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(21), primary_key=True, default=generate_nanoid)
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
    """Client model with enhanced business logic"""
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(21), primary_key=True, default=generate_nanoid)
    phone = Column(String(20), nullable=False)
    service = Column(SQLEnum(ServiceType), nullable=False)
    status = Column(String(20), nullable=False, default='active')
    notes = Column(String(500))
    category = Column(String(20), nullable=False, default='NEW')
    loyalty_points = Column(Integer, nullable=False, default=0)
    referred_by = Column(String(21), ForeignKey('clients.id'), nullable=True)
    total_spent = Column(Float, nullable=False, default=0.0)
    last_visit = Column(DateTime(timezone=True), nullable=True)
    visit_count = Column(Integer, nullable=False, default=0)
    
    # Foreign key to User with unique constraint
    user_id = Column(String(21), ForeignKey('users.id'), nullable=False, unique=True)

    @property
    def calculated_category(self) -> ClientCategory:
        """Calculate client category based on spending and visit history"""
        if self.total_spent >= settings.CLIENT_PREMIUM_SPEND and self.visit_count >= settings.CLIENT_PREMIUM_VISITS:
            return ClientCategory.PREMIUM
        elif self.total_spent >= settings.CLIENT_VIP_SPEND and self.visit_count >= settings.CLIENT_VIP_VISITS:
            return ClientCategory.VIP
        elif self.visit_count >= settings.CLIENT_REGULAR_VISITS:
            return ClientCategory.REGULAR
        return ClientCategory.NEW

    def update_visit_metrics(self, amount_spent: float):
        """Update visit-related metrics when a service is completed"""
        self.visit_count += 1
        self.last_visit = datetime.now(UTC)
        self.total_spent += amount_spent
    
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

def calculate_appointment_cost(service_type: ServiceType, duration_minutes: int) -> float:
    """Calculate appointment cost based on service type and duration"""
    base_cost = settings.SERVICE_BASE_COSTS.get(service_type, 40.0)
    default_duration = settings.SERVICE_DURATIONS.get(service_type, 30)
    
    # Adjust cost if duration differs from default
    if duration_minutes != default_duration:
        cost_ratio = duration_minutes / default_duration
        return base_cost * cost_ratio
    return base_cost

def validate_appointment(mapper, connection, target):
    """Enhanced appointment validation with business rules"""
    # Business hours validation
    start_hour = target.start_time.hour
    end_time = target.start_time + timedelta(minutes=target.duration_minutes)
    end_hour = end_time.hour
    
    if start_hour < settings.BUSINESS_HOUR_START or end_hour >= settings.BUSINESS_HOUR_END:
        raise ValueError(f"Appointments must be between {settings.BUSINESS_HOUR_START} AM and {settings.BUSINESS_HOUR_END - 12} PM")
    
    # Weekend validation
    if not settings.ALLOW_WEEKEND_APPOINTMENTS and target.start_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
        raise ValueError("Appointments cannot be scheduled on weekends")
    
    # Validate start_time is not in the past and has minimum notice
    min_notice = timedelta(hours=settings.APPOINTMENT_MIN_NOTICE_HOURS)
    if target.start_time < datetime.now(timezone.utc) + min_notice:
        raise ValueError(f"Appointments must be scheduled at least {settings.APPOINTMENT_MIN_NOTICE_HOURS} hours in advance")
    
    # Validate duration based on service type
    min_duration = settings.APPOINTMENT_MIN_DURATION_MINUTES
    max_duration = settings.APPOINTMENT_MAX_DURATION_MINUTES
    default_duration = settings.SERVICE_DURATIONS.get(target.service_type, 30)
    
    if target.duration_minutes < min_duration:
        raise ValueError(f"Appointment duration must be at least {min_duration} minutes")
    if target.duration_minutes > max_duration:
        raise ValueError(f"Appointment duration cannot exceed {max_duration} minutes")
    if target.duration_minutes < default_duration:
        raise ValueError(f"Duration cannot be less than {default_duration} minutes for {target.service_type.value}")

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
        'id': target.id if target.id else '',
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
            'id': target.id if target.id else '',
            'start_time': target.start_time,
            'end_time': end_time
        }).scalar()
        raise ValueError(f"There is already an overlapping appointment at {overlapping}")

class Appointment(TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(21), primary_key=True, default=generate_nanoid)
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
    creator_id = Column(String(21), ForeignKey('users.id'), nullable=False)
    
    # Relationships
    attendees = relationship(
        "User",
        secondary=appointment_attendees,
        back_populates="attending_appointments"
    )

class ServiceHistory(TimestampMixin, Base):
    """Enhanced service history tracking"""
    __tablename__ = "service_history"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(21), primary_key=True, default=generate_nanoid)
    client_id = Column(String(21), ForeignKey('clients.id'), nullable=False)
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    provider_name = Column(String, nullable=False)
    date_of_service = Column(DateTime(timezone=True), nullable=False)
    notes = Column(String(500))
    service_cost = Column(Float, nullable=False)
    loyalty_points_earned = Column(Integer, nullable=False, default=0)
    points_redeemed = Column(Integer, nullable=False, default=0)
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 rating
    feedback = Column(String(1000), nullable=True)
    service_duration = Column(Integer, nullable=False)  # Actual duration in minutes
    package_id = Column(String(21), ForeignKey('service_packages.id'), nullable=True)
    
    # Relationships
    client = relationship(
        "Client",
        back_populates="service_history"
    )
    package = relationship("ServicePackage", back_populates="services")

def validate_service_package(mapper, connection, target):
    """Validate service package rules"""
    # Ensure expiry date is in the future
    min_duration = timedelta(days=settings.PACKAGE_MIN_DURATION_DAYS)
    if target.expiry_date <= datetime.now(UTC) + min_duration:
        raise ValueError(f"Package expiry must be at least {settings.PACKAGE_MIN_DURATION_DAYS} days in the future")
    
    # Validate sessions
    if target.total_sessions < 1:
        raise ValueError("Package must include at least 1 session")
    if target.total_sessions > settings.PACKAGE_MAX_SESSIONS:
        raise ValueError(f"Package cannot exceed {settings.PACKAGE_MAX_SESSIONS} sessions")
    
    # Validate cost based on service type and sessions
    discount_factor = (100 - settings.PACKAGE_DISCOUNT_PERCENTAGE) / 100
    base_cost = settings.SERVICE_BASE_COSTS.get(target.service_type, 40.0)
    min_cost_per_session = base_cost * discount_factor
    if target.package_cost < (min_cost_per_session * target.total_sessions):
        raise ValueError("Package cost is below minimum allowed value")

class ServicePackage(TimestampMixin, Base):
    """Enhanced service package management"""
    __tablename__ = "service_packages"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(21), primary_key=True, default=generate_nanoid)
    client_id = Column(String(21), ForeignKey('clients.id'), nullable=False)
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    total_sessions = Column(Integer, nullable=False)
    sessions_remaining = Column(Integer, nullable=False)
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    package_cost = Column(Float, nullable=False)
    minimum_interval = Column(Integer, nullable=False, default=1)  # Minimum days between sessions
    last_session_date = Column(DateTime(timezone=True), nullable=True)
    average_satisfaction = Column(Float, nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="service_packages")
    services = relationship("ServiceHistory", back_populates="package")
    
    def can_use_session(self) -> bool:
        """Check if a session can be used based on remaining sessions and interval"""
        if self.sessions_remaining <= 0:
            return False
        if self.last_session_date:
            min_next_date = self.last_session_date + timedelta(days=self.minimum_interval)
            if datetime.now(UTC) < min_next_date:
                return False
        return True

    def use_session(self):
        """Use a session from the package"""
        if not self.can_use_session():
            raise ValueError("Cannot use session at this time")
        self.sessions_remaining -= 1
        self.last_session_date = datetime.now(UTC)

def update_client_metrics(mapper, connection, target):
    """Update client metrics when service is completed"""
    # Update client metrics
    client_result = connection.execute(text("""
        UPDATE clients
        SET loyalty_points = loyalty_points + :points,
            total_spent = total_spent + :cost,
            visit_count = visit_count + 1,
            last_visit = NOW()
        WHERE id = :client_id
        RETURNING (loyalty_points >= 100) as can_redeem
    """), {
        'points': target.loyalty_points_earned,
        'cost': target.service_cost,
        'client_id': target.client_id
    }).scalar()

def ensure_timestamps(mapper, connection, target):
    """Ensure timestamps are set"""
    if not target.updated_at:
        target.updated_at = datetime.now(UTC)

# Register the event listeners
event.listen(Appointment, 'before_insert', validate_appointment)
event.listen(Appointment, 'before_update', validate_appointment)
event.listen(ServicePackage, 'before_insert', validate_service_package)
event.listen(ServicePackage, 'before_update', validate_service_package)
event.listen(ServiceHistory, 'after_insert', update_client_metrics)
event.listen(User, 'before_insert', ensure_timestamps)
event.listen(Appointment, 'before_insert', ensure_timestamps)
event.listen(ServiceHistory, 'before_insert', ensure_timestamps)
