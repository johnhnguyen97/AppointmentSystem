from datetime import datetime, timedelta, UTC
from typing import List, Optional
from uuid import UUID, uuid4

import strawberry
from sqlalchemy import select, and_, or_, func, text
from strawberry.types import Info

from src.main.models import User, Appointment, Client, ServiceHistory, ServiceType, AppointmentStatus
from src.main.auth import check_auth, get_password_hash
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
class CreateClientInput:
    phone: str
    service: ServiceType
    notes: Optional[str] = None
    user_id: UUID

@strawberry.input
class UpdateClientInput:
    phone: Optional[str] = None
    service: Optional[ServiceType] = None
    status: Optional[str] = None
    notes: Optional[str] = None

@strawberry.type
class UserType:
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    enabled: bool
    is_admin: bool

@strawberry.type
class ClientType:
    id: UUID
    phone: str
    service: str
    status: str
    notes: Optional[str]
    user_id: UUID
    
    @strawberry.field
    async def user(self, info: Info[CustomContext, None]) -> UserType:
        stmt = select(User).where(User.id == self.user_id)
        result = await info.context.session.execute(stmt)
        return result.scalars().first()

@strawberry.type
class AppointmentType:
    id: UUID
    title: str
    description: Optional[str]
    start_time: datetime
    duration_minutes: int
    status: AppointmentStatus
    creator_id: UUID

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
class ServiceHistoryType:
    id: UUID
    client_id: UUID
    service_type: str
    provider_name: str
    date_of_service: datetime
    notes: Optional[str]

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, info: Info[CustomContext, None], id: UUID) -> Optional[UserType]:
        await check_auth(info)
        stmt = select(User).where(User.id == id)
        result = await info.context.session.execute(stmt)
        user = result.scalars().first()
        return user

    @strawberry.field
    async def client(self, info: Info[CustomContext, None], id: UUID) -> Optional[ClientType]:
        await check_auth(info)
        stmt = select(Client).where(Client.id == id)
        result = await info.context.session.execute(stmt)
        client = result.scalars().first()
        return client

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

    @strawberry.field
    async def clientServiceHistory(
        self, info: Info[CustomContext, None], client_id: UUID
    ) -> List[ServiceHistoryType]:
        current_user = await check_auth(info)
        stmt = select(ServiceHistory).where(ServiceHistory.client_id == client_id)
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

        # Check if username or email already exists
        stmt = select(User).where(
            or_(User.username == input.username, User.email == input.email)
        )
        result = await info.context.session.execute(stmt)
        if result.scalars().first():
            raise ValueError("Username or email already exists")

        user = User(
            id=uuid4(),
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
    async def update_user(
        self,
        info: Info[CustomContext, None],
        id: UUID,
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
            # Check if email is already used by another user
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
    async def create_client(
        self,
        info: Info[CustomContext, None],
        input: CreateClientInput
    ) -> ClientType:
        current_user = await check_auth(info)
        if not current_user.is_admin:
            raise PermissionError("Only administrators can create clients")

        # Verify user exists
        stmt = select(User).where(User.id == input.user_id)
        result = await info.context.session.execute(stmt)
        if not result.scalars().first():
            raise ValueError("User not found")

        client = Client(
            id=uuid4(),
            phone=input.phone,
            service=input.service.value,
            status="active",
            notes=input.notes,
            user_id=input.user_id
        )
        info.context.session.add(client)
        await info.context.session.commit()
        return client

    @strawberry.mutation
    async def update_client(
        self,
        info: Info[CustomContext, None],
        id: UUID,
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
            client.status = input.status
        if input.notes is not None:
            client.notes = input.notes

        await info.context.session.commit()
        return client

    @strawberry.mutation
    async def create_appointment(
        self,
        info: Info[CustomContext, None],
        title: str,
        description: Optional[str],
        start_time: str,
        duration_minutes: int,
        attendee_ids: List[UUID],
    ) -> AppointmentType:
        current_user = await check_auth(info)
        
        # Parse datetime from ISO string
        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        # Calculate end time
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Check for overlapping appointments using SQL
        overlap_stmt = select(Appointment).where(
            and_(
                Appointment.start_time < end_time,
                text("appointments.start_time + (appointments.duration_minutes || ' minutes')::interval > :start_time")
            )
        ).params(start_time=start_time)
        
        result = await info.context.session.execute(overlap_stmt)
        if result.scalars().first():
            raise ValueError("Appointment overlaps with existing appointment")

        # Create new appointment
        appointment = Appointment(
            id=uuid4(),
            title=title,
            description=description,
            start_time=start_time,
            duration_minutes=duration_minutes,
            creator_id=current_user.id,
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
        appointment_id: UUID,
        new_status: AppointmentStatus
    ) -> AppointmentType:
        current_user = await check_auth(info)
        stmt = select(Appointment).where(Appointment.id == appointment_id)
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
        
        if new_status not in valid_transitions[appointment.status]:
            raise ValueError(f"Invalid status transition from {appointment.status} to {new_status}")
            
        appointment.status = new_status
        await info.context.session.commit()
        return appointment

    @strawberry.mutation
    async def add_service_history(
        self,
        info: Info[CustomContext, None],
        client_id: UUID,
        service_type: ServiceType,
        notes: Optional[str]
    ) -> ServiceHistoryType:
        current_user = await check_auth(info)
        
        service_history = ServiceHistory(
            id=uuid4(),
            client_id=client_id,
            service_type=service_type.value,
            provider_name=f"{current_user.first_name} {current_user.last_name}",
            date_of_service=datetime.now(UTC),
            notes=notes
        )
        
        info.context.session.add(service_history)
        await info.context.session.commit()
        return service_history

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
