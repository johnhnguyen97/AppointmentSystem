"""
Mutation definitions for the GraphQL API.
"""
from datetime import datetime, UTC
import strawberry
from typing import List, Optional, Union, Annotated, cast
from strawberry.types import Info
import logging
from sqlalchemy import select

from src.main.models import (
    User, Appointment, Client, ServiceHistory, ServiceType, AppointmentStatus,
    ClientCategory, ClientStatus, ServicePackage, calculate_appointment_cost
)
from src.main.auth import (
    check_auth, create_token, TokenType, get_password_hash, verify_password
)
from src.main.typing import CustomContext
from src.main.database import async_session
from src.main.schema_types import (
    AppointmentInput, AppointmentType, ClientInput, ClientType,
    MutationResponse, ValidationError, LoginSuccess, LoginError, LoginResult,
    UserType
)

logger = logging.getLogger(__name__)

@strawberry.type
class AuthMutations:
    """Authentication-related mutations."""

    @strawberry.mutation
    async def login(
        self,
        username: str,
        password: str,
        info: Info[CustomContext, None]
    ) -> Union[LoginSuccess, LoginError]:
        """Authenticate user and return JWT token."""
        try:
            logger.info(f"Login attempt for user: {username}")  # Add logging
            # Validate input
            if not username or not password:
                return LoginError(message="Username and password are required")

            async with async_session() as session:
                async with session.begin():
                    # Use proper async SQLAlchemy query with explicit field selection
                    query = select(
                        User.id,
                        User.username,
                        User.password,
                        User.enabled,
                        User.is_admin
                    ).where(User.username == username)
                    result = await session.execute(query)
                    row = result.one_or_none()

                    if not row:
                        logger.warning(f"User not found: {username}")
                        return LoginError(message="Invalid username or password")

                    # Access fields directly from the row tuple
                    user_id, _, stored_password, enabled, is_admin = row

                    # Check account status
                    if not enabled:
                        logger.warning(f"Disabled account attempt: {username}")
                        return LoginError(message="Account is disabled")

                    # Verify password
                    if not verify_password(password, str(stored_password)):
                        logger.warning(f"Invalid password for user: {username}")
                        return LoginError(message="Invalid username or password")

                    # Generate token
                    token = await create_token(str(user_id), TokenType.ACCESS)

                    # Get complete user object for the response
                    user_query = select(User).where(User.id == user_id)
                    user = (await session.execute(user_query)).scalar_one()

                    logger.info(f"Login successful for user: {username}")
                    return LoginSuccess(token=token, user=UserType.from_db(user))

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return LoginError(message="An error occurred during login")

    @strawberry.mutation
    async def register(
        self,
        username: str,
        password: str,
        email: str,
        info: Info[CustomContext, None]
    ) -> Union[LoginSuccess, LoginError]:
        """Register a new user."""
        try:
            if not username or not password or not email:
                return LoginError(message="All fields are required")

            async with async_session() as session:
                async with session.begin():
                    # Check if username exists
                    query = select(User).where(User.username == username)
                    result = await session.execute(query)
                    if result.scalar_one_or_none():
                        return LoginError(message="Username already exists")

                    # Create new user with correct field names matching the model
                    hashed_password = get_password_hash(password)
                    user_data = {
                        'username': username,
                        'password': hashed_password,
                        'email': email,
                        'enabled': True,
                        'is_admin': False
                    }
                    user = User(**user_data)
                    session.add(user)
                    await session.flush()

                    # Get user ID and convert to string for token
                    user_id = user.id.scalar_value() if hasattr(user.id, 'scalar_value') else user.id
                    token = await create_token(str(user_id), TokenType.ACCESS)
                    return LoginSuccess(token=token, user=UserType.from_db(user))

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return LoginError(message="An error occurred during registration")

@strawberry.type
class AppointmentMutations:
    """Namespace for appointment-related mutations."""

    @strawberry.mutation
    async def create_appointment(
        self,
        info: Info[CustomContext, None],
        input: AppointmentInput
    ) -> MutationResponse:
        """Create a new appointment."""
        current_user = await check_auth(info)

        try:
            async with async_session() as session:
                async with session.begin():
                    # Get current user ID properly
                    creator_id = current_user.id.scalar_value() if hasattr(current_user.id, 'scalar_value') else current_user.id

                    appointment_data = {
                        'title': input.title,
                        'description': input.description,
                        'start_time': input.start_time,
                        'duration_minutes': input.duration_minutes,
                        'service_type': ServiceType(input.service_type),
                        'creator_id': creator_id,
                        'status': AppointmentStatus.SCHEDULED
                    }
                    appointment = Appointment(**appointment_data)
                    session.add(appointment)
                    await session.flush()

                    return MutationResponse(success=True, errors=[])
        except Exception as e:
            logger.error(f"Error creating appointment: {str(e)}")
            return MutationResponse(
                success=False,
                errors=[ValidationError(
                    field="appointment",
                    message=str(e)
                )]
            )

    @strawberry.mutation
    async def update_appointment(
        self,
        info: Info[CustomContext, None],
        id: strawberry.ID,
        input: AppointmentInput
    ) -> MutationResponse:
        """Update an existing appointment."""
        current_user = await check_auth(info)

        try:
            async with async_session() as session:
                async with session.begin():
                    appointment = await session.get(Appointment, id)
                    if not appointment:
                        return MutationResponse(
                            success=False,
                            errors=[ValidationError(
                                field="id",
                                message="Appointment not found"
                            )]
                        )

                    # Compare with SQLAlchemy values properly converted
                    current_user_id = current_user.id.scalar_value() if hasattr(current_user.id, 'scalar_value') else current_user.id
                    creator_id = appointment.creator_id.scalar_value() if hasattr(appointment.creator_id, 'scalar_value') else appointment.creator_id
                    is_admin = current_user.is_admin.scalar_value() if hasattr(current_user.is_admin, 'scalar_value') else current_user.is_admin

                    if not bool(is_admin) and str(creator_id) != str(current_user_id):
                        return MutationResponse(
                            success=False,
                            errors=[ValidationError(
                                field="permission",
                                message="Not authorized to update this appointment"
                            )]
                        )

                    # Update fields using setattr
                    update_data = {
                        'title': input.title,
                        'description': input.description,
                        'start_time': input.start_time,
                        'duration_minutes': input.duration_minutes,
                        'service_type': ServiceType(input.service_type)
                    }
                    for key, value in update_data.items():
                        setattr(appointment, key, value)

                    await session.flush()
                    return MutationResponse(success=True, errors=[])
        except Exception as e:
            logger.error(f"Error updating appointment: {str(e)}")
            return MutationResponse(
                success=False,
                errors=[ValidationError(
                    field="appointment",
                    message=str(e)
                )]
            )

    @strawberry.mutation
    async def delete_appointment(
        self,
        info: Info[CustomContext, None],
        id: strawberry.ID
    ) -> MutationResponse:
        """Delete an appointment."""
        current_user = await check_auth(info)

        try:
            async with async_session() as session:
                async with session.begin():
                    appointment = await session.get(Appointment, id)
                    if not appointment:
                        return MutationResponse(
                            success=False,
                            errors=[ValidationError(
                                field="id",
                                message="Appointment not found"
                            )]
                        )
                    # Compare with SQLAlchemy values properly converted
                    current_user_id = current_user.id.scalar_value() if hasattr(current_user.id, 'scalar_value') else current_user.id
                    creator_id = appointment.creator_id.scalar_value() if hasattr(appointment.creator_id, 'scalar_value') else appointment.creator_id
                    is_admin = current_user.is_admin.scalar_value() if hasattr(current_user.is_admin, 'scalar_value') else current_user.is_admin

                    if not bool(is_admin) and str(creator_id) != str(current_user_id):
                        return MutationResponse(
                            success=False,
                            errors=[ValidationError(
                                field="permission",
                                message="Not authorized to delete this appointment"
                            )]
                        )

                    await session.delete(appointment)
                    return MutationResponse(success=True, errors=[])
        except Exception as e:
            logger.error(f"Error deleting appointment: {str(e)}")
            return MutationResponse(
                success=False,
                errors=[ValidationError(
                    field="appointment",
                    message=str(e)
                )]
            )

@strawberry.type
class ClientMutations:
    """Namespace for client-related mutations."""

    @strawberry.mutation
    async def create_client(
        self,
        info: Info[CustomContext, None],
        input: ClientInput
    ) -> MutationResponse:
        """Create a new client."""
        current_user = await check_auth(info)

        try:
            async with async_session() as session:
                async with session.begin():
                    # Get current user ID properly
                    user_id = current_user.id.scalar_value() if hasattr(current_user.id, 'scalar_value') else current_user.id

                    client_data = {
                        'phone': input.phone,
                        'service': ServiceType(input.service),
                        'notes': input.notes,
                        'user_id': user_id,
                        'status': ClientStatus.ACTIVE,
                        'category': ClientCategory.NEW
                    }
                    client = Client(**client_data)
                    session.add(client)
                    await session.flush()

                    return MutationResponse(success=True, errors=[])
        except Exception as e:
            logger.error(f"Error creating client: {str(e)}")
            return MutationResponse(
                success=False,
                errors=[ValidationError(
                    field="client",
                    message=str(e)
                )]
            )

    @strawberry.mutation
    async def update_client(
        self,
        info: Info[CustomContext, None],
        id: strawberry.ID,
        input: ClientInput
    ) -> MutationResponse:
        """Update an existing client."""
        current_user = await check_auth(info)

        try:
            async with async_session() as session:
                async with session.begin():
                    client = await session.get(Client, id)
                    if not client:
                        return MutationResponse(
                            success=False,
                            errors=[ValidationError(
                                field="id",
                                message="Client not found"
                            )]
                        )
                    # Compare with SQLAlchemy values properly converted
                    current_user_id = current_user.id.scalar_value() if hasattr(current_user.id, 'scalar_value') else current_user.id
                    user_id = client.user_id.scalar_value() if hasattr(client.user_id, 'scalar_value') else client.user_id
                    is_admin = current_user.is_admin.scalar_value() if hasattr(current_user.is_admin, 'scalar_value') else current_user.is_admin

                    if not bool(is_admin) and str(user_id) != str(current_user_id):
                        return MutationResponse(
                            success=False,
                            errors=[ValidationError(
                                field="permission",
                                message="Not authorized to update this client"
                            )]
                        )

                    # Update fields using setattr
                    update_data = {
                        'phone': input.phone,
                        'service': ServiceType(input.service),
                        'notes': input.notes
                    }
                    for key, value in update_data.items():
                        setattr(client, key, value)

                    await session.flush()
                    return MutationResponse(success=True, errors=[])
        except Exception as e:
            logger.error(f"Error updating client: {str(e)}")
            return MutationResponse(
                success=False,
                errors=[ValidationError(
                    field="client",
                    message=str(e)
                )]
            )

    @strawberry.mutation
    async def delete_client(
        self,
        info: Info[CustomContext, None],
        id: strawberry.ID
    ) -> MutationResponse:
        """Delete a client."""
        current_user = await check_auth(info)

        try:
            async with async_session() as session:
                async with session.begin():
                    client = await session.get(Client, id)
                    if not client:
                        return MutationResponse(
                            success=False,
                            errors=[ValidationError(
                                field="id",
                                message="Client not found"
                            )]
                        )

                    # Compare with SQLAlchemy values properly converted
                    current_user_id = current_user.id.scalar_value() if hasattr(current_user.id, 'scalar_value') else current_user.id
                    user_id = client.user_id.scalar_value() if hasattr(client.user_id, 'scalar_value') else client.user_id
                    is_admin = current_user.is_admin.scalar_value() if hasattr(current_user.is_admin, 'scalar_value') else current_user.is_admin

                    if not bool(is_admin) and str(user_id) != str(current_user_id):
                        return MutationResponse(
                            success=False,
                            errors=[ValidationError(
                                field="permission",
                                message="Not authorized to delete this client"
                            )]
                        )
                    return MutationResponse(success=True, errors=[])
        except Exception as e:
            logger.error(f"Error deleting client: {str(e)}")
            return MutationResponse(
                success=False,
                errors=[ValidationError(
                    field="client",
                    message=str(e)
                )]
            )
