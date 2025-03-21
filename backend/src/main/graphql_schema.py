from datetime import datetime, timedelta, UTC
from typing import List, Optional
import strawberry
from sqlalchemy import select, and_, or_, func
from strawberry.types import Info
from nanoid import generate
from src.main.models import (
    User, Appointment, Client, ServiceHistory, ServiceType, AppointmentStatus,
    ClientCategory, ClientStatus, ServicePackage, calculate_appointment_cost
)
from src.main.auth import check_auth, get_password_hash, verify_password, create_access_token
from src.main.typing import CustomContext
from src.main.database import async_session
import logging

logger = logging.getLogger(__name__)

@strawberry.input
class LoginInput:
    username: str
    password: str

@strawberry.type
class AuthResponse:
    token: str
    user: 'UserType'

@strawberry.type
class DashboardSummary:
    total_clients: int
    todaysAppointmentsCount: int
    upcomingAppointmentsCount: int

@strawberry.type
class UserType:
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    enabled: bool
    is_admin: bool

    @classmethod
    def from_db(cls, user: User) -> 'UserType':
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            enabled=user.enabled,
            is_admin=user.is_admin
        )

@strawberry.type
class AppointmentType:
    @classmethod
    def from_db(cls, appointment: Appointment) -> 'AppointmentType':
        return cls(
            id=appointment.id,
            title=appointment.title,
            description=appointment.description,
            startTime=appointment.startTime,
            durationMinutes=appointment.durationMinutes,
            status=appointment.status.value if appointment.status else None,
            serviceType=appointment.serviceType.value if appointment.serviceType else None,
            estimatedCost=appointment.estimated_cost
        )

    id: str
    title: str
    description: Optional[str]
    startTime: datetime
    durationMinutes: int
    status: str
    serviceType: str
    estimatedCost: float

@strawberry.type
class ClientType:
    @classmethod
    def from_db(cls, client: Client) -> 'ClientType':
        return cls(
            id=client.id,
            phone=client.phone,
            service=client.service.value if client.service else None,
            status=client.status.value if client.status else None,
            notes=client.notes,
            loyaltyPoints=client.loyalty_points,
            totalSpent=client.total_spent,
            visitCount=client.visit_count,
            lastVisit=client.last_visit,
            category=client.category.value if client.category else None
        )

    id: str
    phone: str
    service: str
    status: str
    notes: Optional[str]
    loyaltyPoints: int
    totalSpent: float
    visitCount: int
    lastVisit: Optional[datetime]
    category: str

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, input: LoginInput) -> AuthResponse:
        """Login mutation to authenticate users"""
        async with async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.username == input.username)
                result = await session.execute(stmt)
                user = result.scalars().first()

                if not user:
                    raise ValueError("Invalid username or password")

                if not verify_password(input.password, user.password):
                    raise ValueError("Invalid username or password")

                if not user.enabled:
                    raise ValueError("User account is disabled")

                token = create_access_token(user.id)
                return AuthResponse(token=token, user=UserType.from_db(user))

@strawberry.type
class Query:
    @strawberry.field
    async def dashboard_summary(self, info: Info[CustomContext, None]) -> DashboardSummary:
        """Get dashboard summary with multiple sessions for concurrent operations"""
        current_user = await check_auth(info)
        now = datetime.now(UTC)
        today_start = datetime(now.year, now.month, now.day, tzinfo=UTC)
        today_end = today_start + timedelta(days=1)

        total_clients = 0
        todays_count = 0
        upcoming_count = 0

        try:
            # Get clients count with its own session
            async with async_session() as session:
                async with session.begin():
                    clients_stmt = select(func.count(Client.id)).where(Client.status == ClientStatus.ACTIVE)
                    if not current_user.is_admin:
                        clients_stmt = clients_stmt.where(Client.user_id == current_user.id)
                    clients_result = await session.execute(clients_stmt)
                    total_clients = clients_result.scalar() or 0

            # Get today's appointments count with its own session
            async with async_session() as session:
                async with session.begin():
                    today_apt_stmt = select(func.count(Appointment.id)).where(
                        and_(
                            Appointment.startTime >= today_start,
                            Appointment.startTime < today_end
                        )
                    )
                    if not current_user.is_admin:
                        today_apt_stmt = today_apt_stmt.where(
                            or_(
                                Appointment.creatorId == current_user.id,
                                Appointment.attendees.any(User.id == current_user.id)
                            )
                        )
                    today_result = await session.execute(today_apt_stmt)
                    todays_count = today_result.scalar() or 0

            # Get upcoming appointments count with its own session
            async with async_session() as session:
                async with session.begin():
                    upcoming_stmt = select(func.count(Appointment.id)).where(
                        and_(
                            Appointment.startTime >= now,
                            Appointment.status == AppointmentStatus.SCHEDULED
                        )
                    )
                    if not current_user.is_admin:
                        upcoming_stmt = upcoming_stmt.where(
                            or_(
                                Appointment.creatorId == current_user.id,
                                Appointment.attendees.any(User.id == current_user.id)
                            )
                        )
                    upcoming_result = await session.execute(upcoming_stmt)
                    upcoming_count = upcoming_result.scalar() or 0

        except Exception as e:
            logger.error(f"Error fetching dashboard summary: {str(e)}")
            raise

        return DashboardSummary(
            total_clients=total_clients,
            todaysAppointmentsCount=todays_count,
            upcomingAppointmentsCount=upcoming_count
        )

    @strawberry.field
    async def todays_appointments(self, info: Info[CustomContext, None]) -> List[AppointmentType]:
        current_user = await check_auth(info)
        now = datetime.now(UTC)
        today_start = datetime(now.year, now.month, now.day, tzinfo=UTC)
        today_end = today_start + timedelta(days=1)

        async with async_session() as session:
            async with session.begin():
                stmt = select(Appointment).where(
                    and_(
                        Appointment.startTime >= today_start,
                        Appointment.startTime < today_end
                    )
                )

                if not current_user.is_admin:
                    stmt = stmt.where(
                        or_(
                            Appointment.creatorId == current_user.id,
                            Appointment.attendees.any(User.id == current_user.id)
                        )
                    )

                stmt = stmt.order_by(Appointment.startTime)
                result = await session.execute(stmt)
                appointments = result.scalars().all()
                return [AppointmentType.from_db(apt) for apt in appointments]

    @strawberry.field
    async def recent_clients(self, info: Info[CustomContext, None], limit: int = 5) -> List[ClientType]:
        current_user = await check_auth(info)

        async with async_session() as session:
            async with session.begin():
                stmt = select(Client).order_by(Client.created_at.desc())
                if not current_user.is_admin:
                    stmt = stmt.where(Client.user_id == current_user.id)

                stmt = stmt.limit(limit)
                result = await session.execute(stmt)
                clients = result.scalars().all()
                return [ClientType.from_db(client) for client in clients]

schema = strawberry.Schema(query=Query, mutation=Mutation)
