from typing import List, Optional, Any
import strawberry
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import select, or_
from strawberry.types import Info as StrawberryInfo
from strawberry.exceptions import GraphQLError
from src.main.graphql_context import CustomContext
from src.main.schema import AppointmentStatus
from src.main import models, auth
from enum import StrEnum

Info = StrawberryInfo[CustomContext, None]

@strawberry.enum
class ServiceTypeEnum(StrEnum):
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

def get_context(session: Any = None) -> dict:
    return {"session": session}

@strawberry.type
class Client:
    id: int
    phone: str
    service: ServiceTypeEnum
    status: str
    notes: Optional[str]
    user_id: UUID

    @strawberry.field
    async def user(self, info: Info) -> "User":
        session = info.context.session
        result = await session.execute(
            select(models.User).where(models.User.id == self.user_id)
        )
        return result.scalar_one()

    @classmethod
    def from_sqlalchemy(cls, db_client: models.Client) -> "Client":
        try:
            service_enum = ServiceTypeEnum[db_client.service.replace(" ", "").upper()]
        except KeyError:
            service_enum = ServiceTypeEnum.OTHER  # Fallback for invalid values
        return cls(
            id=db_client.id,
            phone=db_client.phone,
            service=service_enum,
            status=db_client.status,
            notes=db_client.notes,
            user_id=db_client.user_id
        )

@strawberry.type
class User:
    id: UUID
    sequential_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: Optional[datetime]
    enabled: bool
    client_profile: Optional["Client"]

    @strawberry.field
    async def created_appointments(self, info: Info) -> List["Appointment"]:
        session = info.context.session
        result = await session.execute(
            select(models.Appointment).where(models.Appointment.creator_id == self.id)
        )
        return result.scalars().all()

    @strawberry.field
    async def attending_appointments(self, info: Info) -> List["Appointment"]:
        session = info.context.session
        result = await session.execute(
            select(models.Appointment).where(models.Appointment.attendees.any(id=self.id))
        )
        return result.scalars().all()

@strawberry.type
class Appointment:
    id: UUID
    title: str
    description: Optional[str]
    start_time: datetime
    duration_minutes: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: Optional[datetime]

    @strawberry.field
    async def creator(self, info: Info) -> "User":
        session = info.context.session
        result = await session.execute(
            select(models.User).where(models.User.id == self.creator_id)
        )
        return result.scalar_one()

    @strawberry.field
    async def attendees(self, info: Info) -> List["User"]:
        session = info.context.session
        result = await session.execute(
            select(models.User).join(models.appointment_attendees).where(
                models.appointment_attendees.c.appointment_id == self.id
            )
        )
        return result.scalars().all()

@strawberry.input
class CreateUserInput:
    username: str
    email: str
    password: str
    first_name: str
    last_name: str

@strawberry.input
class LoginInput:
    username: str
    password: str

@strawberry.type
class LoginSuccess:
    token: str
    user: "User"

@strawberry.input
class CreateClientInput:
    user_id: UUID
    phone: str
    service: ServiceTypeEnum
    status: Optional[str] = "active"
    notes: Optional[str] = None

@strawberry.input
class UpdateClientInput:
    phone: Optional[str] = None
    service: Optional[ServiceTypeEnum] = None
    status: Optional[str] = None
    notes: Optional[str] = None

@strawberry.type
class Query:
    @strawberry.field
    async def client(self, info: Info, id: int) -> Optional[Client]:
        session = info.context.session
        result = await session.execute(
            select(models.Client).where(models.Client.id == id)
        )
        db_client = result.scalar_one_or_none()
        return Client.from_sqlalchemy(db_client) if db_client else None

    @strawberry.field
    async def clients(self, info: Info, service: Optional[str] = None) -> List[Client]:
        session = info.context.session
        query = select(models.Client)
        if service:
            query = query.where(models.Client.service == service)
        result = await session.execute(query)
        return [Client.from_sqlalchemy(client) for client in result.scalars().all()]

    @strawberry.field
    async def user(self, info: Info, id: Optional[UUID] = None, sequential_id: Optional[int] = None) -> Optional[User]:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        if not current_user:
            raise GraphQLError("Authentication required")
            
        query = select(models.User)
        if id:
            query = query.where(models.User.id == id)
        elif sequential_id:
            query = query.where(models.User.sequential_id == sequential_id)
        else:
            raise GraphQLError("Must provide either id or sequential_id")

        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise GraphQLError("User not found")

        if current_user.id != user.id:
            raise GraphQLError("Not authorized to view this user")
            
        return user

    @strawberry.field
    async def appointments(self, info: Info) -> List[Appointment]:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        if not current_user:
            raise GraphQLError("Authentication required")
        result = await session.execute(
            select(models.Appointment).where(
                or_(
                    models.Appointment.creator_id == current_user.id,
                    models.Appointment.attendees.any(id=current_user.id)
                )
            )
        )
        return result.scalars().all()

    @strawberry.field
    async def appointment(self, info: Info, id: UUID) -> Optional[Appointment]:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        if not current_user:
            raise GraphQLError("Authentication required")
            
        result = await session.execute(
            select(models.Appointment).where(
                models.Appointment.id == id,
                or_(
                    models.Appointment.creator_id == current_user.id,
                    models.Appointment.attendees.any(id=current_user.id)
                )
            )
        )
        return result.scalar_one_or_none()

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, info: Info, input: CreateUserInput) -> User:
        session = info.context.session
        
        result = await session.execute(
            select(models.User).where(models.User.username == input.username)
        )
        if result.scalar_one_or_none():
            raise GraphQLError("Username already exists")
            
        result = await session.execute(
            select(models.User).where(models.User.email == input.email)
        )
        if result.scalar_one_or_none():
            raise GraphQLError("Email already exists")
            
        user = models.User(
            id=uuid4(),
            username=input.username,
            email=input.email,
            password=auth.get_password_hash(input.password),
            first_name=input.first_name,
            last_name=input.last_name,
            enabled=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @strawberry.mutation
    async def create_client(self, info: Info, input: CreateClientInput) -> Client:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        if not current_user:
            raise GraphQLError("Authentication required")

        # Optionally restrict to creator or admin
        # if current_user.id != input.user_id:
        #     raise GraphQLError("You can only create a client for yourself")

        result = await session.execute(
            select(models.User).where(models.User.id == input.user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise GraphQLError("User not found")

        result = await session.execute(
            select(models.Client).where(models.Client.user_id == input.user_id)
        )
        if result.scalar_one_or_none():
            raise GraphQLError("User already has a client profile")

        client = models.Client(
            user_id=input.user_id,
            phone=input.phone,
            service=input.service.value,  # Maps to SQLAlchemy enum string
            status=input.status if input.status else "active",
            notes=input.notes
        )
        try:
            session.add(client)
            await session.commit()
            await session.refresh(client)
            return Client.from_sqlalchemy(client)
        except Exception as e:
            await session.rollback()
            raise GraphQLError(f"Failed to create client: {str(e)}")

    @strawberry.mutation
    async def update_client(self, info: Info, id: int, input: UpdateClientInput) -> Client:
        session = info.context.session
        result = await session.execute(
            select(models.Client).where(models.Client.id == id)
        )
        client = result.scalar_one_or_none()
        
        if not client:
            raise GraphQLError("Client not found")
            
        if input.phone is not None:
            client.phone = input.phone
        if input.service is not None:
            client.service = input.service.value  # Maps to SQLAlchemy enum string
        if input.status is not None:
            client.status = input.status
        if input.notes is not None:
            client.notes = input.notes
            
        await session.commit()
        await session.refresh(client)
        return Client.from_sqlalchemy(client)

    @strawberry.mutation
    async def login(self, info: Info, input: LoginInput) -> LoginSuccess:
        session = info.context.session
        user = await auth.authenticate_user(input.username, input.password, session)
        if not user:
            raise GraphQLError("Invalid username or password")
        
        access_token = auth.create_access_token(data={"sub": str(user.id)})
        return LoginSuccess(token=access_token, user=user)

    @strawberry.mutation
    async def create_appointment(self, info: Info, title: str, description: Optional[str], start_time: datetime, duration_minutes: int, attendee_ids: List[UUID]) -> Appointment:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        if not current_user:
            raise GraphQLError("Authentication required")
        
        result = await session.execute(
            select(models.User).where(models.User.id.in_(attendee_ids))
        )
        attendees = result.scalars().all()
        if len(attendees) != len(attendee_ids):
            raise GraphQLError("One or more attendees not found")
            
        appointment = models.Appointment(
            title=title,
            description=description,
            start_time=start_time,
            duration_minutes=duration_minutes,
            creator_id=current_user.id,
            attendees=attendees
        )
        session.add(appointment)
        await session.commit()
        await session.refresh(appointment)
        return appointment

    @strawberry.mutation
    async def update_appointment(self, info: Info, id: UUID, title: Optional[str] = None, description: Optional[str] = None, start_time: Optional[datetime] = None, duration_minutes: Optional[int] = None, status: Optional[AppointmentStatus] = None) -> Appointment:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        result = await session.execute(
            select(models.Appointment).where(
                models.Appointment.id == id,
                models.Appointment.creator_id == current_user.id
            )
        )
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            raise GraphQLError("Appointment not found or you don't have permission to update it")
            
        if title is not None:
            appointment.title = title
        if description is not None:
            appointment.description = description
        if start_time is not None:
            appointment.start_time = start_time
        if duration_minutes is not None:
            appointment.duration_minutes = duration_minutes
        if status is not None:
            appointment.status = status
            
        await session.commit()
        await session.refresh(appointment)
        return appointment

    @strawberry.mutation
    async def delete_appointment(self, info: Info, id: UUID) -> bool:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        if not current_user:
            raise GraphQLError("Authentication required")
        
        result = await session.execute(
            select(models.Appointment).where(
                models.Appointment.id == id,
                models.Appointment.creator_id == current_user.id
            )
        )
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            raise GraphQLError("Appointment not found or you don't have permission to delete it")
        
        await session.delete(appointment)
        await session.commit()
        return True

    @strawberry.mutation
    async def update_appointment_attendance(self, info: Info, id: UUID, attendee_ids: List[UUID]) -> Appointment:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        if not current_user:
            raise GraphQLError("Authentication required")
        
        result = await session.execute(
            select(models.Appointment).where(
                models.Appointment.id == id,
                models.Appointment.creator_id == current_user.id
            )
        )
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            raise GraphQLError("Appointment not found or you don't have permission to update it")
        
        result = await session.execute(
            select(models.User).where(models.User.id.in_(attendee_ids))
        )
        attendees = result.scalars().all()
        if len(attendees) != len(attendee_ids):
            raise GraphQLError("One or more attendees not found")
        
        appointment.attendees = attendees
        await session.commit()
        await session.refresh(appointment)
        return appointment

    @strawberry.mutation
    async def update_appointment_status(self, info: Info, id: UUID, status: AppointmentStatus) -> Appointment:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        if not current_user:
            raise GraphQLError("Authentication required")
        
        result = await session.execute(
            select(models.Appointment).where(
                models.Appointment.id == id,
                or_(
                    models.Appointment.creator_id == current_user.id,
                    models.Appointment.attendees.any(id=current_user.id)
                )
            )
        )
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            raise GraphQLError("Appointment not found or you're not a participant")
        
        if status == AppointmentStatus.CANCELLED and appointment.creator_id != current_user.id:
            raise GraphQLError("Only the creator can cancel an appointment")
        
        if status == AppointmentStatus.DECLINED and current_user.id not in [a.id for a in appointment.attendees]:
            raise GraphQLError("Only attendees can decline an appointment")
        
        appointment.status = status
        await session.commit()
        await session.refresh(appointment)
        return appointment

    @strawberry.mutation
    async def delete_user(self, info: Info, user_id: Optional[UUID] = None, username: Optional[str] = None) -> bool:
        if not user_id and not username:
            raise GraphQLError("Must provide either user_id or username")
            
        session = info.context.session
        
        query = select(models.User)
        if user_id:
            query = query.where(models.User.id == user_id)
        else:
            query = query.where(models.User.username == username)
            
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return True  # Already deleted
            
        result = await session.execute(
            select(models.Client).where(models.Client.user_id == user.id)
        )
        client = result.scalar_one_or_none()
        if client:
            await session.delete(client)
            
        result = await session.execute(
            select(models.Appointment).where(models.Appointment.creator_id == user.id)
        )
        appointments = result.scalars().all()
        for appointment in appointments:
            await session.delete(appointment)
            
        await session.delete(user)
        await session.commit()
        return True

schema = strawberry.Schema(query=Query, mutation=Mutation)