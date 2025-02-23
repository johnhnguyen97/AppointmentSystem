# src/main/models.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Float, Enum as SQLEnum, Table, event, and_, or_
from sqlalchemy.future import select
from enum import StrEnum
from datetime import datetime, timezone, UTC, timedelta
from nanoid import generate

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
        """Default duration in minutes for each service type"""
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
        """Base cost for each service type"""
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
        """Loyalty points earned for each service type"""
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
from sqlalchemy.ext.hybrid import hybrid_property
from src.main.schema import AppointmentStatus
from sqlalchemy.orm import relationship, declarative_mixin, declared_attr
from sqlalchemy.sql import func, text
from datetime import datetime, timezone, UTC
from sqlalchemy.orm import declarative_base, registry, Session

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
        if self.total_spent >= 1000 and self.visit_count >= 20:
            return ClientCategory.PREMIUM
        elif self.total_spent >= 500 and self.visit_count >= 10:
            return ClientCategory.VIP
        elif self.visit_count >= 3:
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
    base_cost = ServiceType.get_base_cost(service_type)
    default_duration = ServiceType.get_duration_minutes(service_type)
    
    # Adjust cost if duration differs from default
    if duration_minutes != default_duration:
        cost_ratio = duration_minutes / default_duration
        return base_cost * cost_ratio
    return base_cost

def validate_appointment(mapper, connection, target):
    """Enhanced appointment validation with business rules"""
    """Validate appointment rules and set calculated fields"""
    # Business hours validation (9 AM to 7 PM)
    start_hour = target.start_time.hour
    end_time = target.start_time + timedelta(minutes=target.duration_minutes)
    end_hour = end_time.hour
    
    if start_hour < 9 or end_hour >= 19:
        raise ValueError("Appointments must be between 9 AM and 7 PM")
    
    # Weekend validation
    if target.start_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
        raise ValueError("Appointments cannot be scheduled on weekends")
    
    # Validate start_time is not in the past and has minimum notice
    min_notice = timedelta(hours=2)
    if target.start_time < datetime.now(timezone.utc) + min_notice:
        raise ValueError("Appointments must be scheduled at least 2 hours in advance")
    
    # Validate duration based on service type
    min_duration = 15
    max_duration = 480  # 8 hours
    default_duration = ServiceType.get_duration_minutes(target.service_type)
    
    if target.duration_minutes < min_duration:
        raise ValueError("Appointment duration must be at least 15 minutes")
    if target.duration_minutes > max_duration:
        raise ValueError("Appointment duration cannot exceed 8 hours")
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
    min_duration = timedelta(days=30)  # Minimum package duration is 30 days
    if target.expiry_date <= datetime.now(UTC) + min_duration:
        raise ValueError("Package expiry must be at least 30 days in the future")
    
    # Validate sessions
    if target.total_sessions < 1:
        raise ValueError("Package must include at least 1 session")
    if target.total_sessions > 52:  # Maximum 52 sessions (weekly for a year)
        raise ValueError("Package cannot exceed 52 sessions")
    
    # Validate cost based on service type and sessions
    min_cost_per_session = ServiceType.get_base_cost(target.service_type) * 0.8  # 20% discount
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
    """Update client loyalty points when service history is added"""
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
    if not target.updated_at:
        target.updated_at = datetime.now(UTC)

# Register the event listeners
event.listen(Appointment, 'before_insert', validate_appointment)
event.listen(Appointment, 'before_update', validate_appointment)
event.listen(User, 'before_insert', ensure_timestamps)
event.listen(Appointment, 'before_insert', ensure_timestamps)
event.listen(ServiceHistory, 'before_insert', ensure_timestamps)
# Register all event listeners
event.listen(Appointment, 'before_insert', validate_appointment)
event.listen(Appointment, 'before_update', validate_appointment)
event.listen(ServicePackage, 'before_insert', validate_service_package)
event.listen(ServicePackage, 'before_update', validate_service_package)
event.listen(ServiceHistory, 'after_insert', update_client_metrics)
