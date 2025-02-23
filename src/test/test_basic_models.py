import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import uuid4
from src.main.models import User, Client, ServiceHistory, ServicePackage, ServiceType

@pytest.mark.asyncio
async def test_user_creation(async_session):
    """Test basic user creation and retrieval"""
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User"
    )
    async_session.add(user)
    await async_session.commit()

    # Retrieve user
    stmt = select(User).where(User.username == "testuser")
    result = await async_session.execute(stmt)
    fetched_user = result.scalar_one()

    assert fetched_user.email == "test@example.com"
    assert fetched_user.first_name == "Test"
    assert fetched_user.last_name == "User"
    assert fetched_user.enabled  # Should default to True
    assert not fetched_user.is_admin  # Should default to False
    assert fetched_user.sequential_id is not None

@pytest.mark.asyncio
async def test_client_creation(async_session):
    """Test client creation with associated user"""
    # Create user first
    user = User(
        username="clienttest",
        email="client@test.com",
        password="testpass123",
        first_name="Client",
        last_name="Test"
    )
    async_session.add(user)
    await async_session.commit()

    # Create client
    client = Client(
        user_id=user.id,
        phone="555-0100",
        service=ServiceType.HAIRCUT,
        status="active",
        category="NEW"
    )
    async_session.add(client)
    await async_session.commit()

    # Retrieve client with user
    stmt = select(Client).options(
        selectinload(Client.user)
    ).where(Client.phone == "555-0100")
    result = await async_session.execute(stmt)
    fetched_client = result.scalar_one()

    assert fetched_client.service == ServiceType.HAIRCUT
    assert fetched_client.status == "active"
    assert fetched_client.category == "NEW"
    assert fetched_client.loyalty_points == 0
    assert fetched_client.user.username == "clienttest"

@pytest.mark.asyncio
async def test_service_package_creation(async_session):
    """Test service package creation and validation"""
    # Create user and client first
    user = User(
        username="packagetest",
        email="package@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0200",
        service=ServiceType.MASSAGE,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    # Create service package
    package = ServicePackage(
        client_id=client.id,
        service_type=ServiceType.MASSAGE,
        total_sessions=10,
        sessions_remaining=10,
        purchase_date=datetime.now(timezone.utc),
        expiry_date=datetime.now(timezone.utc) + timedelta(days=365),
        package_cost=800.00
    )
    async_session.add(package)
    await async_session.commit()

    # Retrieve package
    stmt = select(ServicePackage).where(
        ServicePackage.client_id == client.id
    )
    result = await async_session.execute(stmt)
    fetched_package = result.scalar_one()

    assert fetched_package.total_sessions == 10
    assert fetched_package.sessions_remaining == 10
    assert fetched_package.service_type == ServiceType.MASSAGE
    assert fetched_package.package_cost == 800.00
    assert not fetched_package.expiry_date < datetime.now(timezone.utc)

@pytest.mark.asyncio
async def test_service_history_creation(async_session):
    """Test service history recording"""
    # Create user and client first
    user = User(
        username="historytest",
        email="history@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0300",
        service=ServiceType.HAIRCUT,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    # Create service history entry
    service = ServiceHistory(
        client_id=client.id,
        service_type=ServiceType.HAIRCUT,
        provider_name="Test Provider",
        date_of_service=datetime.now(timezone.utc),
        service_cost=50.00,
        loyalty_points_earned=50
    )
    async_session.add(service)
    await async_session.commit()

    # Retrieve service history
    stmt = select(ServiceHistory).where(
        ServiceHistory.client_id == client.id
    )
    result = await async_session.execute(stmt)
    fetched_service = result.scalar_one()

    assert fetched_service.service_type == ServiceType.HAIRCUT
    assert fetched_service.provider_name == "Test Provider"
    assert fetched_service.service_cost == 50.00
    assert fetched_service.loyalty_points_earned == 50
    assert fetched_service.points_redeemed == 0  # Default value

@pytest.mark.asyncio
async def test_cascading_deletes(async_session):
    """Test that deleting a user cascades properly to related records"""
    # Create full set of related records
    user = User(username="deletetest", email="delete@test.com", password="testpass123")
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0400",
        service=ServiceType.HAIRCUT,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    package = ServicePackage(
        client_id=client.id,
        service_type=ServiceType.HAIRCUT,
        total_sessions=5,
        sessions_remaining=5,
        purchase_date=datetime.now(timezone.utc),
        expiry_date=datetime.now(timezone.utc) + timedelta(days=365),
        package_cost=400.00
    )
    async_session.add(package)

    service = ServiceHistory(
        client_id=client.id,
        service_type=ServiceType.HAIRCUT,
        provider_name="Test Provider",
        date_of_service=datetime.now(timezone.utc),
        service_cost=50.00,
        package_id=package.id
    )
    async_session.add(service)
    await async_session.commit()

    # Delete the user
    await async_session.delete(user)
    await async_session.commit()

    # Verify cascaded deletes
    stmt = select(Client).where(Client.id == client.id)
    result = await async_session.execute(stmt)
    assert result.scalar_one_or_none() is None, "Client should be deleted"

    stmt = select(ServicePackage).where(ServicePackage.id == package.id)
    result = await async_session.execute(stmt)
    assert result.scalar_one_or_none() is None, "Service package should be deleted"

    stmt = select(ServiceHistory).where(ServiceHistory.id == service.id)
    result = await async_session.execute(stmt)
    assert result.scalar_one_or_none() is None, "Service history should be deleted"
