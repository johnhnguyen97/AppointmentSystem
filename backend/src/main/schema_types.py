"""
Shared GraphQL types used across the schema.
"""
from datetime import datetime
from enum import Enum
import strawberry
from typing import List, Optional

from src.main.models import (
    User, Appointment, Client, ServiceHistory, ServiceType, AppointmentStatus,
    ClientCategory, ClientStatus, ServicePackage
)

# Auth Types
@strawberry.type
class LoginSuccess:
    """Successful login response type."""
    token: str = strawberry.field(description="JWT access token")
    user: 'UserType' = strawberry.field(description="Authenticated user")

@strawberry.type
class LoginError:
    """Login error response type."""
    message: str = strawberry.field(description="Error message")

# Union type for login results
LoginResult = strawberry.union(
    "LoginResult",
    types=[LoginSuccess, LoginError],
    description="Result of a login attempt"
)

# Enums
@strawberry.enum
class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"

@strawberry.enum
class AppointmentStatusEnum(Enum):
    """Available appointment statuses."""
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"

# Common Types
@strawberry.type
class PageInfo:
    """Information about pagination in a connection."""
    has_next_page: bool = strawberry.field(description="When paginating forwards, are there more items?")
    has_previous_page: bool = strawberry.field(description="When paginating backwards, are there more items?")
    start_cursor: Optional[str] = strawberry.field(description="When paginating backwards, the cursor to continue.")
    end_cursor: Optional[str] = strawberry.field(description="When paginating forwards, the cursor to continue.")

@strawberry.type
class AuthError:
    """Authentication related error."""
    message: str = strawberry.field(description="Error message")

@strawberry.type
class ValidationError:
    """Validation related error."""
    field: str = strawberry.field(description="Field that caused the error")
    message: str = strawberry.field(description="Error message")

# Input Types
@strawberry.input
class LoginInput:
    """Input for login mutation."""
    username: str = strawberry.field(description="Username")
    password: str = strawberry.field(description="Password")

@strawberry.input
class AppointmentInput:
    """Input for creating/updating appointments."""
    title: str = strawberry.field(description="Appointment title")
    description: Optional[str] = strawberry.field(description="Optional description")
    start_time: datetime = strawberry.field(description="Start time")
    duration_minutes: int = strawberry.field(description="Duration in minutes")
    service_type: str = strawberry.field(description="Type of service")

@strawberry.input
class AppointmentFilterInput:
    """Input for filtering appointments."""
    status: Optional[AppointmentStatusEnum] = strawberry.field(description="Filter by status")
    date_from: Optional[datetime] = strawberry.field(description="Filter by start date")
    date_to: Optional[datetime] = strawberry.field(description="Filter by end date")
    service_type: Optional[str] = strawberry.field(description="Filter by service type")

@strawberry.input
class ClientInput:
    """Input for creating/updating clients."""
    phone: str = strawberry.field(description="Phone number")
    service: str = strawberry.field(description="Preferred service")
    notes: Optional[str] = strawberry.field(description="Optional notes")

@strawberry.input
class ClientFilterInput:
    """Input for filtering clients."""
    status: Optional[str] = strawberry.field(description="Filter by status")
    category: Optional[str] = strawberry.field(description="Filter by category")
    service: Optional[str] = strawberry.field(description="Filter by preferred service")
    search: Optional[str] = strawberry.field(description="Search in phone number")

# Response/Payload Types
@strawberry.type
class MutationResponse:
    """Generic mutation response."""
    success: bool = strawberry.field(description="Whether the operation was successful")
    errors: Optional[List[ValidationError]] = strawberry.field(description="List of validation errors if any")

# Domain Types
@strawberry.type
class UserType:
    """User type with all user related fields."""
    id: strawberry.ID = strawberry.field(description="Unique identifier")
    username: str = strawberry.field(description="Username for login")
    email: str = strawberry.field(description="Email address")
    first_name: str = strawberry.field(description="First name")
    last_name: str = strawberry.field(description="Last name")
    enabled: bool = strawberry.field(description="Whether user account is enabled")
    is_admin: bool = strawberry.field(description="Whether user has admin privileges")

    @classmethod
    def from_db(cls, user: User) -> 'UserType':
        return cls(
            id=strawberry.ID(str(user.id)),
            username=str(user.username),
            email=str(user.email),
            first_name=str(user.first_name),
            last_name=str(user.last_name),
            enabled=bool(user.enabled),
            is_admin=bool(user.is_admin)
        )

@strawberry.type
class AppointmentEdge:
    """An edge in an appointment connection."""
    node: 'AppointmentType' = strawberry.field(description="The appointment")
    cursor: str = strawberry.field(description="Cursor for pagination")

@strawberry.type
class AppointmentConnection:
    """Connection for appointments pagination."""
    page_info: PageInfo = strawberry.field(description="Pagination information")
    edges: List[AppointmentEdge] = strawberry.field(description="List of appointment edges")
    total_count: int = strawberry.field(description="Total number of appointments")

@strawberry.type
class AppointmentType:
    """Appointment type with all appointment related fields."""
    id: strawberry.ID = strawberry.field(description="Unique identifier")
    title: str = strawberry.field(description="Appointment title")
    description: Optional[str] = strawberry.field(description="Optional description")
    start_time: datetime = strawberry.field(description="Start time")
    duration_minutes: int = strawberry.field(description="Duration in minutes")
    status: str = strawberry.field(description="Current status")
    service_type: str = strawberry.field(description="Type of service")
    estimated_cost: float = strawberry.field(description="Estimated cost")
    creator: UserType = strawberry.field(description="User who created the appointment")
    attendees: List[UserType] = strawberry.field(description="Users attending the appointment")

    @classmethod
    def from_db(cls, appointment: Appointment) -> 'AppointmentType':
        def get_value(obj, attr, is_enum=False, default=None):
            val = getattr(obj, attr)
            if val is None:
                return default
            if hasattr(val, 'scalar_value'):
                val = val.scalar_value()
            if val is None:
                return default
            return val.value if is_enum and hasattr(val, 'value') else val

        return cls(
            id=strawberry.ID(str(get_value(appointment, 'id', default='0'))),
            title=str(get_value(appointment, 'title', default='')),
            description=str(get_value(appointment, 'description')) if get_value(appointment, 'description') is not None else None,
            start_time=datetime.fromisoformat(str(get_value(appointment, 'startTime'))) if get_value(appointment, 'startTime') is not None else datetime.now(),
            duration_minutes=int(get_value(appointment, 'durationMinutes', default=0)),
            status=str(get_value(appointment, 'status', is_enum=True, default="")),
            service_type=str(get_value(appointment, 'serviceType', is_enum=True, default="")),
            estimated_cost=float(get_value(appointment, 'estimated_cost', default=0.0)),
            creator=UserType.from_db(appointment.creator),
            attendees=[UserType.from_db(u) for u in appointment.attendees]
        )

@strawberry.type
class ClientEdge:
    """An edge in a client connection."""
    node: 'ClientType' = strawberry.field(description="The client")
    cursor: str = strawberry.field(description="Cursor for pagination")

@strawberry.type
class ClientConnection:
    """Connection for clients pagination."""
    page_info: PageInfo = strawberry.field(description="Pagination information")
    edges: List[ClientEdge] = strawberry.field(description="List of client edges")
    total_count: int = strawberry.field(description="Total number of clients")

@strawberry.type
class ClientType:
    """Client type with all client related fields."""
    id: strawberry.ID = strawberry.field(description="Unique identifier")
    phone: str = strawberry.field(description="Phone number")
    service: str = strawberry.field(description="Preferred service")
    status: str = strawberry.field(description="Current status")
    notes: Optional[str] = strawberry.field(description="Optional notes")
    loyalty_points: int = strawberry.field(description="Accumulated loyalty points")
    total_spent: float = strawberry.field(description="Total amount spent")
    visit_count: int = strawberry.field(description="Number of visits")
    last_visit: Optional[datetime] = strawberry.field(description="Date of last visit")
    category: str = strawberry.field(description="Client category")

    @classmethod
    def from_db(cls, client: Client) -> 'ClientType':
        def get_value(obj, attr, is_enum=False, default=None):
            val = getattr(obj, attr)
            if val is None:
                return default
            if hasattr(val, 'scalar_value'):
                val = val.scalar_value()
            if val is None:
                return default
            return val.value if is_enum and hasattr(val, 'value') else val

        return cls(
            id=strawberry.ID(str(get_value(client, 'id', default='0'))),
            phone=str(get_value(client, 'phone', default='')),
            service=str(get_value(client, 'service', is_enum=True, default="")),
            status=str(get_value(client, 'status', is_enum=True, default="")),
            notes=str(get_value(client, 'notes')) if get_value(client, 'notes') is not None else None,
            loyalty_points=int(get_value(client, 'loyalty_points', default=0)),
            total_spent=float(get_value(client, 'total_spent', default=0.0)),
            visit_count=int(get_value(client, 'visit_count', default=0)),
            last_visit=get_value(client, 'last_visit') if get_value(client, 'last_visit') is not None else None,
            category=str(get_value(client, 'category', is_enum=True, default=""))
        )

@strawberry.type
class DashboardSummary:
    """Summary statistics for the dashboard."""
    total_clients: int = strawberry.field(description="Total number of active clients")
    todays_appointments_count: int = strawberry.field(description="Number of appointments today")
    upcoming_appointments_count: int = strawberry.field(description="Number of upcoming appointments")
