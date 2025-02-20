import pytest
from uuid import uuid4
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from main.models import User, Appointment
from main.auth import get_password_hash, create_access_token
from main.graphql_schema import schema
from main.schema import AppointmentStatus
from main.graphql_context import CustomContext

@pytest.fixture
async def test_user(async_session):
    user = User(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        password=get_password_hash("testpass123"),
        first_name="Test",  # SQLAlchemy model still uses snake_case
        last_name="User",   # SQLAlchemy model still uses snake_case
        enabled=True
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user

@pytest.fixture
def user_token(test_user):
    return create_access_token(data={"sub": str(test_user.id)})

@pytest.fixture
async def test_appointment(async_session, test_user):
    appointment = Appointment(
        id=uuid4(),
        title="Test Appointment",
        description="Test Description",
        start_time=datetime.utcnow() + timedelta(days=1),
        duration_minutes=60,
        creator_id=test_user.id,
        status=AppointmentStatus.SCHEDULED,
        attendees=[test_user]
    )
    async_session.add(appointment)
    await async_session.commit()
    await async_session.refresh(appointment)
    return appointment

async def execute_graphql(query, context=None, variables=None):
    if context is None:
        context = CustomContext(session=None, get_current_user=None)
    return await schema.execute(
        query,
        context_value=context,
        variable_values=variables
    )

@pytest.mark.asyncio
async def test_login_mutation(async_session):
    # Create test user
    user = User(
        id=uuid4(),
        username="logintest",
        email="login@test.com",
        password=get_password_hash("password123"),
        first_name="Login",  # SQLAlchemy model still uses snake_case
        last_name="Test",    # SQLAlchemy model still uses snake_case
        enabled=True
    )
    async_session.add(user)
    await async_session.commit()

    # Test login mutation
    query = """
    mutation {
        login(input: {username: "logintest", password: "password123"}) {
            token
            user {
                username
                email
                firstName
                lastName
            }
        }
    }
    """
    
    context = CustomContext(
        session=async_session,
        get_current_user=None
    )
    
    result = await execute_graphql(query, context=context)
    
    assert result.errors is None
    assert result.data["login"]["token"] is not None
    assert result.data["login"]["user"]["username"] == "logintest"
    assert result.data["login"]["user"]["email"] == "login@test.com"

@pytest.mark.asyncio
async def test_create_appointment_mutation(async_session, test_user, user_token):
    query = """
    mutation CreateAppointment($title: String!, $startTime: DateTime!, $attendeeIds: [UUID!]!) {
        createAppointment(
            title: $title,
            description: "Test Description",
            startTime: $startTime,
            durationMinutes: 60,
            attendeeIds: $attendeeIds
        ) {
            id
            title
            description
            status
            creator {
                username
            }
            attendees {
                username
            }
        }
    }
    """
    
    variables = {
        "title": "New Test Appointment",
        "startTime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "attendeeIds": [str(test_user.id)]
    }
    
    context = CustomContext(
        session=async_session,
        get_current_user=lambda *args, **kwargs: test_user
    )
    
    result = await execute_graphql(query, context=context, variables=variables)
    
    assert result.errors is None
    assert result.data["createAppointment"]["title"] == "New Test Appointment"
    assert result.data["createAppointment"]["description"] == "Test Description"
    assert result.data["createAppointment"]["status"] == AppointmentStatus.SCHEDULED
    assert result.data["createAppointment"]["creator"]["username"] == test_user.username
    assert len(result.data["createAppointment"]["attendees"]) == 1
    assert result.data["createAppointment"]["attendees"][0]["username"] == test_user.username

@pytest.mark.asyncio
async def test_query_appointments(async_session, test_user, test_appointment):
    query = """
    query {
        appointments {
            id
            title
            description
            status
            creator {
                username
            }
            attendees {
                username
            }
        }
    }
    """
    
    context = CustomContext(
        session=async_session,
        get_current_user=lambda *args, **kwargs: test_user
    )
    
    result = await execute_graphql(query, context=context)
    
    assert result.errors is None
    assert len(result.data["appointments"]) == 1
    appointment = result.data["appointments"][0]
    assert appointment["title"] == test_appointment.title
    assert appointment["description"] == test_appointment.description
    assert appointment["status"] == test_appointment.status
    assert appointment["creator"]["username"] == test_user.username
