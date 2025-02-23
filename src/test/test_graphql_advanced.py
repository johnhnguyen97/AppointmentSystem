from datetime import datetime, timedelta, UTC
from uuid import uuid4
import pytest
from sqlalchemy import select

from src.main.models import User, Client, ServiceHistory, ServiceType, AppointmentStatus
from src.main.graphql_context import CustomContext
from src.main.auth import get_password_hash
from src.main.graphql_schema import schema

async def execute_graphql(query, variables=None, context=None):
    return await schema.execute(
        query,
        variable_values=variables,
        context_value=context
    )

@pytest.fixture
async def test_provider(async_session):
    provider = User(
        id=uuid4(),
        username="testprovider",
        email="provider@example.com",
        password=get_password_hash("testpass123"),
        first_name="Test",
        last_name="Provider",
        enabled=True,
        is_admin=False
    )
    async_session.add(provider)
    await async_session.commit()
    return provider

@pytest.fixture
async def test_client_user(async_session, test_provider):
    client_user = User(
        id=uuid4(),
        username="testclient",
        email="client@example.com",
        password=get_password_hash("testpass123"),
        first_name="Test",
        last_name="Client",
        enabled=True
    )
    async_session.add(client_user)
    
    client = Client(
        id=uuid4(),
        phone="(555) 123-4567",
        service=ServiceType.HAIRCUT.value,
        status="active",
        notes="Test client",
        user_id=client_user.id
    )
    async_session.add(client)
    await async_session.commit()
    return client

@pytest.mark.asyncio
async def test_appointment_overlap_prevention(async_session, test_provider):
    """Test that GraphQL mutation prevents overlapping appointments"""
    create_appointment_query = """
    mutation CreateAppointment($title: String!, $startTime: String!, $duration: Int!) {
        createAppointment(
            title: $title
            description: "Test Description"
            startTime: $startTime
            durationMinutes: $duration
            attendeeIds: []
        ) {
            id
            title
            startTime
            durationMinutes
        }
    }
    """

    start_time = datetime.now(UTC) + timedelta(days=1)

    async def get_current_user():
        return test_provider

    context = CustomContext(
        session=async_session,
        get_current_user_override=get_current_user
    )

    # Create first appointment
    result1 = await execute_graphql(
        create_appointment_query,
        context=context,
        variables={
            "title": "First Appointment",
            "startTime": start_time.isoformat(),
            "duration": 60
        }
    )
    assert result1.errors is None

    # Try to create overlapping appointment
    result2 = await execute_graphql(
        create_appointment_query,
        context=context,
        variables={
            "title": "Overlapping Appointment",
            "startTime": (start_time + timedelta(minutes=30)).isoformat(),
            "duration": 60
        }
    )
    assert result2.errors is not None
    assert "overlaps" in str(result2.errors[0]).lower()

@pytest.mark.asyncio
async def test_appointment_status_transitions(async_session, test_provider):
    """Test appointment status transition validation via GraphQL"""
    create_query = """
    mutation CreateAppointment($title: String!) {
        createAppointment(
            title: $title
            description: "Test Description"
            startTime: "2025-03-01T10:00:00Z"
            durationMinutes: 60
            attendeeIds: []
        ) {
            id
            status
        }
    }
    """

    update_query = """
    mutation UpdateStatus($id: UUID!, $status: AppointmentStatus!) {
        updateAppointmentStatus(
            appointmentId: $id
            newStatus: $status
        ) {
            id
            status
        }
    }
    """

    async def get_current_user():
        return test_provider

    context = CustomContext(
        session=async_session,
        get_current_user_override=get_current_user
    )

    # Create appointment
    result = await execute_graphql(
        create_query,
        context=context,
        variables={"title": "Status Test"}
    )
    assert result.data is not None, f"Create appointment failed: {result.errors}"
    appointment_id = result.data["createAppointment"]["id"]

    # Test valid transition
    result = await execute_graphql(
        update_query,
        context=context,
        variables={
            "id": appointment_id,
            "status": AppointmentStatus.CONFIRMED.value
        }
    )
    assert result.errors is None
    assert result.data["updateAppointmentStatus"]["status"] == AppointmentStatus.CONFIRMED.value

    # Test invalid transition
    result = await execute_graphql(
        update_query,
        context=context,
        variables={
            "id": appointment_id,
            "status": AppointmentStatus.SCHEDULED.value
        }
    )
    assert result.errors is not None
    assert "invalid status transition" in str(result.errors[0]).lower()

@pytest.mark.asyncio
async def test_service_history_tracking(async_session, test_provider, test_client_user):
    """Test service history creation and querying"""
    # Create a service history entry directly
    service_entry = ServiceHistory(
        id=uuid4(),
        client_id=test_client_user.id,
        service_type=ServiceType.HAIRCUT.value,
        provider_name=f"{test_provider.first_name} {test_provider.last_name}",
        date_of_service=datetime.now(UTC),
        notes="Regular haircut with styling"
    )
    async_session.add(service_entry)
    await async_session.commit()

    # Query service history through GraphQL
    service_history_query = """
    query GetServiceHistory($clientId: UUID!) {
        clientServiceHistory(clientId: $clientId) {
            id
            serviceType
            dateOfService
            providerName
            notes
        }
    }
    """

    async def get_current_user():
        return test_provider

    context = CustomContext(
        session=async_session,
        get_current_user_override=get_current_user
    )

    # Query service history
    result = await execute_graphql(
        service_history_query,
        context=context,
        variables={"clientId": str(test_client_user.id)}
    )
    assert result.errors is None
    assert len(result.data["clientServiceHistory"]) == 1
    history_entry = result.data["clientServiceHistory"][0]
    assert history_entry["serviceType"] == ServiceType.HAIRCUT.value
    assert history_entry["notes"] == "Regular haircut with styling"

@pytest.mark.asyncio
async def test_enhanced_authorization(async_session, test_provider):
    """Test role-based access control for appointments"""
    admin_query = """
    query AdminQuery {
        allAppointments {
            id
            title
            status
            creator {
                username
            }
        }
    }
    """

    provider_query = """
    query ProviderQuery {
        appointments {
            id
            title
            status
        }
    }
    """

    async def get_current_user():
        return test_provider

    # Test as regular provider
    context = CustomContext(
        session=async_session,
        get_current_user_override=get_current_user
    )

    # Should not be able to access allAppointments
    result = await execute_graphql(admin_query, context=context)
    assert result.errors is not None
    assert "not authorized" in str(result.errors[0]).lower()

    # Should be able to access own appointments
    result = await execute_graphql(provider_query, context=context)
    assert result.errors is None

    # Update provider to admin
    test_provider.is_admin = True
    await async_session.commit()

    # Should now be able to access allAppointments
    result = await execute_graphql(admin_query, context=context)
    assert result.errors is None
