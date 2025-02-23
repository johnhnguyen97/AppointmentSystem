from datetime import datetime, timedelta, UTC
from typing import List, Optional

import strawberry
from sqlalchemy import select, and_, or_, func, text
from strawberry.types import Info
from nanoid import generate

from src.main.models import (
    User, Appointment, Client, ServiceHistory, ServiceType, AppointmentStatus,
    ClientCategory, ClientStatus, ServicePackage, calculate_appointment_cost
)
from src.main.auth import check_auth, get_password_hash, verify_password, create_access_token
from src.main.graphql_context import CustomContext

@strawberry.input
class CreateUserInput:
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    enabled: bool = True

@strawberry.input
class UpdateUserInput:
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enabled: Optional[bool] = None

@strawberry.input
class LoginInput:
    username: str
    password: str

@strawberry.input
class CreateClientInput:
    phone: str
    service: ServiceType
    status: ClientStatus = ClientStatus.ACTIVE
    notes: Optional[str] = None

@strawberry.input
class UpdateClientInput:
    phone: Optional[str] = None
    service: Optional[ServiceType] = None
    status: Optional[ClientStatus] = None
    notes: Optional[str] = None

@strawberry.type
class UserType:
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    enabled: bool
    is_admin: bool

@strawberry.type
class LoginResponse:
    token: str
    user: UserType

@strawberry.type
class ServicePackageType:
    id: str
    client_id: str
    service_type: ServiceType
    total_sessions: int
    sessions_remaining: int
    purchase_date: datetime
    expiry_date: datetime
    package_cost: float
    minimum_interval: int
    last_session_date: Optional[datetime]
    average_satisfaction: Optional[float]

    @strawberry.field
    def can_use_session(self) -> bool:
        if self.sessions_remaining <= 0:
            return False
        if self.last_session_date:
            min_next_date = self.last_session_date + timedelta(days=self.minimum_interval)
            if datetime.now(UTC) < min_next_date:
                return False
        return True

@strawberry.type
class ServiceHistoryType:
    id: str
    client_id: str
    service_type: ServiceType
    provider_name: str
    date_of_service: datetime
    notes: Optional[str]
    service_cost: float
    loyalty_points_earned: int
    points_redeemed: int
    satisfaction_rating: Optional[int]
    feedback: Optional[str]
    service_duration: int

@strawberry.type
class ClientType:
    id: str
    phone: str
    service: ServiceType
    status: ClientStatus
    notes: Optional[str]
    category: ClientCategory
    user_id: str
    loyalty_points: int
    total_spent: float
    visit_count: int
    last_visit: Optional[datetime]
    
    @strawberry.field
    async def user(self, info: Info[CustomContext, None]) -> UserType:
        stmt = select(User).where(User.id == self.user_id)
        result = await info.context.session.execute(stmt)
        return result.scalars().first()

    @strawberry.field
    async def service_packages(self, info: Info[CustomContext, None]) -> List[ServicePackageType]:
        stmt = select(ServicePackage).where(ServicePackage.client_id == self.id)
        result = await info.context.session.execute(stmt)
        return list(result.scalars().all())

    @strawberry.field
    async def service_history(self, info: Info[CustomContext, None]) -> List[ServiceHistoryType]:
        stmt = select(ServiceHistory).where(ServiceHistory.client_id == self.id)
        result = await info.context.session.execute(stmt)
        return list(result.scalars().all())

@strawberry.type
class AppointmentType:
    id: str
    title: str
    description: Optional[str]
    start_time: datetime
    duration_minutes: int
    status: AppointmentStatus
    service_type: ServiceType
    creator_id: str

    @strawberry.field
    def estimated_cost(self) -> float:
        return calculate_appointment_cost(self.service_type, self.duration_minutes)

    @strawberry.field
    async def creator(self, info: Info[CustomContext, None]) -> UserType:
        stmt = select(User).where(User.id == self.creator_id)
        result = await info.context.session.execute(stmt)
        return result.scalars().first()

    @strawberry.field
    async def attendees(self, info: Info[CustomContext, None]) -> List[UserType]:
        stmt = select(User).join(Appointment.attendees).where(Appointment.id == self.id)
        result = await info.context.session.execute(stmt)
        return list(result.scalars().all())

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, info: Info[CustomContext, None], id: str) -> Optional[UserType]:
        await check_auth(info)
        stmt = select(User).where(User.id == id)
        result = await info.context.session.execute(stmt)
        user = result.scalars().first()
        return user

    @strawberry.field
    async def client(self, info: Info[CustomContext, None], id: str) -> Optional[ClientType]:
        await check_auth(info)
        stmt = select(Client).where(Client.id == id)
        result = await info.context.session.execute(stmt)
        client = result.scalars().first()
        return client

    @strawberry.field
    async def service_package(
        self, info: Info[CustomContext, None], id: str
    ) -> Optional[ServicePackageType]:
        await check_auth(info)
        stmt = select(ServicePackage).where(ServicePackage.id == id)
        result = await info.context.session.execute(stmt)
        return result.scalars().first()

    @strawberry.field
    async def clients(self, info: Info[CustomContext, None]) -> List[ClientType]:
        current_user = await check_auth(info)
        stmt = select(Client)
        if not current_user.is_admin:
            stmt = stmt.where(Client.user_id == current_user.id)
        result = await info.context.session.execute(stmt)
        return list(result.scalars().all())

    @strawberry.field
    async def appointments(self, info: Info[CustomContext, None]) -> List[AppointmentType]:
        current_user = await check_auth(info)
        stmt = select(Appointment).where(
            or_(
                Appointment.creator_id == current_user.id,
                Appointment.attendees.any(User.id == current_user.id)
            )
        )
        result = await info.context.session.execute(stmt)
        return list(result.scalars().all())

    @strawberry.field
    async def allAppointments(self, info: Info[CustomContext, None]) -> List[AppointmentType]:
        current_user = await check_auth(info)
        if not current_user.is_admin:
            raise PermissionError("Not authorized to view all appointments")
        
        stmt = select(Appointment)
        result = await info.context.session.execute(stmt)
        return list(result.scalars().all())

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(
        self,
        info: Info[CustomContext, None],
        input: CreateUserInput
    ) -> UserType:
        current_user = await check_auth(info)
        if not current_user.is_admin:
            raise PermissionError("Only administrators can create users")

        stmt = select(User).where(
            or_(User.username == input.username, User.email == input.email)
        )
        result = await info.context.session.execute(stmt)
        if result.scalars().first():
            raise ValueError("Username or email already exists")

        user = User(
            username=input.username,
            email=input.email,
            password=get_password_hash(input.password),
            first_name=input.first_name,
            last_name=input.last_name,
            enabled=input.enabled
        )
        info.context.session.add(user)
        await info.context.session.commit()
        return user

    @strawberry.mutation
    async def create_service_package(
        self,
        info: Info[CustomContext, None],
        client_id: str,
        service_type: ServiceType,
        total_sessions: int,
        expiry_date: datetime,
        package_cost: float,
        minimum_interval: Optional[int] = 1
    ) -> ServicePackageType:
        current_user = await check_auth(info)
        if not current_user.is_admin:
            raise PermissionError("Only administrators can create service packages")

        package = ServicePackage(
            client_id=client_id,
            service_type=service_type,
            total_sessions=total_sessions,
            sessions_remaining=total_sessions,
            purchase_date=datetime.now(UTC),
            expiry_date=expiry_date,
            package_cost=package_cost,
            minimum_interval=minimum_interval
        )
        info.context.session.add(package)
        await info.context.session.commit()
        return package

    @strawberry.mutation
    async def update_user(
        self,
        info: Info[CustomContext, None],
        id: str,
        input: UpdateUserInput
    ) -> UserType:
        current_user = await check_auth(info)
        if not current_user.is_admin and current_user.id != id:
            raise PermissionError("Not authorized to update this user")

        stmt = select(User).where(User.id == id)
        result = await info.context.session.execute(stmt)
        user = result.scalars().first()
        if not user:
            raise ValueError("User not found")

        if input.email is not None:
            stmt = select(User).where(
                and_(User.email == input.email, User.id != id)
            )
            result = await info.context.session.execute(stmt)
            if result.scalars().first():
                raise ValueError("Email already in use")
            user.email = input.email

        if input.first_name is not None:
            user.first_name = input.first_name
        if input.last_name is not None:
            user.last_name = input.last_name
        if input.enabled is not None and current_user.is_admin:
            user.enabled = input.enabled

        await info.context.session.commit()
        return user

    @strawberry.mutation
    async def login(
        self,
        info: Info[CustomContext, None],
        input: LoginInput
    ) -> LoginResponse:
        stmt = select(User).where(User.username == input.username)
        result = await info.context.session.execute(stmt)
        user = result.scalars().first()

        if not user or not verify_password(input.password, user.password):
            raise ValueError("Invalid username or password")

        if not user.enabled:
            raise ValueError("User account is disabled")

        token = create_access_token(user.id)
        return LoginResponse(token=token, user=user)

    @strawberry.mutation
    async def create_client(
        self,
        info: Info[CustomContext, None],
        input: CreateClientInput
    ) -> ClientType:
        current_user = await check_auth(info)

        client = Client(
            phone=input.phone,
            service=input.service.name,
            status=input.status.value,
            notes=input.notes,
            category=ClientCategory.NEW,
            user_id=current_user.id
        )
        info.context.session.add(client)
        await info.context.session.commit()
        return client

    @strawberry.mutation
    async def update_client(
        self,
        info: Info[CustomContext, None],
        id: str,
        input: UpdateClientInput
    ) -> ClientType:
        current_user = await check_auth(info)
        
        stmt = select(Client).where(Client.id == id)
        result = await info.context.session.execute(stmt)
        client = result.scalars().first()
        if not client:
            raise ValueError("Client not found")

        if not current_user.is_admin:
            raise PermissionError("Only administrators can update clients")

        if input.phone is not None:
            client.phone = input.phone
        if input.service is not None:
            client.service = input.service.value
        if input.status is not None:
            client.status = input.status.value
        if input.notes is not None:
            client.notes = input.notes

        await info.context.session.commit()
        return client

    @strawberry.mutation
    async def create_appointment(
        self,
        info: Info[CustomContext, None],
        title: str,
        service_type: ServiceType,
        description: Optional[str],
        start_time: str,
        duration_minutes: int,
        attendee_ids: List[str],
    ) -> AppointmentType:
        current_user = await check_auth(info)
        
        # Parse datetime from ISO string
        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        # Create new appointment
        appointment = Appointment(
            title=title,
            description=description,
            start_time=start_time,
            duration_minutes=duration_minutes,
            creator_id=current_user.id,
            service_type=service_type,
            status=AppointmentStatus.SCHEDULED
        )

        if attendee_ids:
            # Fetch attendees
            stmt = select(User).where(User.id.in_(attendee_ids))
            result = await info.context.session.execute(stmt)
            attendees = result.scalars().all()
            appointment.attendees.extend(attendees)

        info.context.session.add(appointment)
        await info.context.session.commit()
        return appointment

    @strawberry.mutation
    async def update_appointment_status(
        self,
        info: Info[CustomContext, None],
        id: str,
        status: AppointmentStatus
    ) -> AppointmentType:
        current_user = await check_auth(info)
        stmt = select(Appointment).where(Appointment.id == id)
        result = await info.context.session.execute(stmt)
        appointment = result.scalars().first()
        
        if not appointment:
            raise ValueError("Appointment not found")
            
        if appointment.creator_id != current_user.id and not current_user.is_admin:
            raise PermissionError("Not authorized to update this appointment")
            
        # Add status transition validation
        valid_transitions = {
            AppointmentStatus.SCHEDULED: [AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED],
            AppointmentStatus.CONFIRMED: [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED],
            AppointmentStatus.CANCELLED: [],
            AppointmentStatus.COMPLETED: [],
            AppointmentStatus.DECLINED: []
        }
        
        if status not in valid_transitions[appointment.status]:
            raise ValueError(f"Invalid status transition from {appointment.status} to {status}")
            
        appointment.status = status
        await info.context.session.commit()
        return appointment

    @strawberry.mutation
    async def add_service_history(
        self,
        info: Info[CustomContext, None],
        client_id: str,
        service_type: ServiceType,
        service_cost: float,
        service_duration: int,
        notes: Optional[str] = None,
        satisfaction_rating: Optional[int] = None,
        feedback: Optional[str] = None,
        package_id: Optional[str] = None
    ) -> ServiceHistoryType:
        current_user = await check_auth(info)
        
        # Calculate loyalty points
        loyalty_points = ServiceType.get_loyalty_points(service_type)
        
        service_history = ServiceHistory(
            client_id=client_id,
            service_type=service_type.value,
            provider_name=f"{current_user.first_name} {current_user.last_name}",
            date_of_service=datetime.now(UTC),
            notes=notes,
            service_cost=service_cost,
            loyalty_points_earned=loyalty_points,
            service_duration=service_duration,
            satisfaction_rating=satisfaction_rating,
            feedback=feedback,
            package_id=package_id
        )
        
        if package_id:
            stmt = select(ServicePackage).where(ServicePackage.id == package_id)
            result = await info.context.session.execute(stmt)
            package = result.scalars().first()
            if not package or not package.can_use_session():
                raise ValueError("Invalid package or cannot use session at this time")
            package.use_session()
        
        info.context.session.add(service_history)
        await info.context.session.commit()
        return service_history

schema = strawberry.Schema(query=Query, mutation=Mutation)
