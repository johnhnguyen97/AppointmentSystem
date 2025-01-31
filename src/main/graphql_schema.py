from typing import List, Optional, Any
import strawberry
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, or_
from strawberry.types import Info as StrawberryInfo
from strawberry.scalars import JSON
from src.main.schema import AppointmentStatus
from src.main import models, auth
from strawberry.exceptions import GraphQLError
from src.main.context import CustomContext

Info = StrawberryInfo[CustomContext, None]

def get_context(session: Any = None) -> dict:
    return {"session": session}

@strawberry.type
class User:
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: Optional[datetime]
    enabled: bool

    @strawberry.field
    async def created_appointments(self, info: Info) -> List['Appointment']:
        session = info.context.session
        result = await session.execute(
            select(models.Appointment).where(models.Appointment.creator_id == self.id)
        )
        return result.scalars().all()

    @strawberry.field
    async def attending_appointments(self, info: Info) -> List['Appointment']:
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
    async def creator(self, info: Info) -> User:
        session = info.context.session
        result = await session.execute(
            select(models.User).where(models.User.id == self.creator_id)
        )
        return result.scalar_one()

    @strawberry.field
    async def attendees(self, info: Info) -> List[User]:
        session = info.context.session
        result = await session.execute(
            select(models.User).join(models.appointment_attendees).where(
                models.appointment_attendees.c.appointment_id == self.id
            )
        )
        return result.scalars().all()

@strawberry.input
class LoginInput:
    username: str
    password: str

@strawberry.type
class LoginSuccess:
    token: str
    user: User

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, info: Info, id: UUID) -> Optional[User]:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        if not current_user:
            raise GraphQLError("Authentication required")
            
        # Users can only view their own profile for now
        if current_user.id != id:
            raise GraphQLError("Not authorized to view this user")
            
        return current_user

    @strawberry.field
    async def appointments(self, info: Info) -> List[Appointment]:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        if not current_user:
            raise GraphQLError("Authentication required")
        result = await session.execute(
            select(models.Appointment)
            .where(
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
            select(models.Appointment)
            .where(
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
    async def login(self, info: Info, input: LoginInput) -> LoginSuccess:
        session = info.context.session
        user = await auth.authenticate_user(input.username, input.password, session)
        if not user:
            raise GraphQLError("Invalid username or password")
        
        access_token = auth.create_access_token(data={"sub": str(user.id)})
        return LoginSuccess(token=access_token, user=user)

    @strawberry.mutation
    async def create_appointment(
        self,
        info: Info,
        title: str,
        description: Optional[str],
        start_time: datetime,
        duration_minutes: int,
        attendee_ids: List[UUID]
    ) -> Appointment:
        session = info.context.session
        current_user = await info.context.get_current_user()
        
        if not current_user:
            raise GraphQLError("Authentication required")
        
        # Verify all attendees exist
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
    async def update_appointment(
        self,
        info: Info,
        id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_time: Optional[datetime] = None,
        duration_minutes: Optional[int] = None,
        status: Optional[AppointmentStatus] = None
    ) -> Appointment:
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
    async def update_appointment_attendance(
        self,
        info: Info,
        id: UUID,
        attendee_ids: List[UUID]
    ) -> Appointment:
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
        
        # Verify all attendees exist
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
    async def update_appointment_status(
        self,
        info: Info,
        id: UUID,
        status: AppointmentStatus
    ) -> Appointment:
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
        
        # Only creator can cancel
        if status == AppointmentStatus.CANCELLED and appointment.creator_id != current_user.id:
            raise GraphQLError("Only the creator can cancel an appointment")
        
        # Only attendees can decline
        if status == AppointmentStatus.DECLINED and current_user.id not in [a.id for a in appointment.attendees]:
            raise GraphQLError("Only attendees can decline an appointment")
        
        appointment.status = status
        await session.commit()
        await session.refresh(appointment)
        return appointment

schema = strawberry.Schema(query=Query, mutation=Mutation)
