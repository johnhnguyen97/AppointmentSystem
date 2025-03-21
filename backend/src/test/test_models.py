import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from uuid import uuid4
from src.main.models import User, Client, ServiceHistory, ServiceType, ServicePackage

@pytest.mark.asyncio
async def test_user_model(async_session):
    """Test user creation and validation"""
    user = User(
        username="modeltest",
        email="model@test.com",
        password="testpass123",
        first_name="Model",
        last_name="Test"
    )
    async_session.add(user)
    await async_session.commit()

    # Test unique constraints
    duplicate_user = User(
        username="modeltest",  # Same username
        email="different@test.com",
        password="testpass123"
    )
    async_session.add(duplicate_user)
    with pytest.raises(Exception, match="unique"):  # Should raise unique constraint violation
        await async_session.commit()
    await async_session.rollback()

@pytest.mark.asyncio
async def test_client_model(async_session):
    """Test client creation and service type validation"""
    # Create user first
    user = User(
        username="clienttest",
        email="client@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    # Create client
    client = Client(
        user_id=user.id,
        phone="555-0123",
        service=ServiceType.HAIRCUT,
        status="active",
        notes="Test client"
    )
    async_session.add(client)
    await async_session.commit()

    # Test invalid service type
    invalid_client = Client(
        user_id=user.id,
        phone="555-0124",
        service="INVALID_SERVICE",  # Invalid service type
        status="active"
    )
    async_session.add(invalid_client)
    with pytest.raises(Exception):  # Should raise validation error
        await async_session.commit()
    await async_session.rollback()

@pytest.mark.asyncio
async def test_service_package_model(async_session):
    """Test service package validation and tracking"""
    # Create user and client
    user = User(username="packagetest", email="package@test.com", password="testpass123")
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0125",
        service=ServiceType.MASSAGE,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    # Create valid package
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

    # Test package usage
    for _ in range(3):
        package.sessions_remaining -= 1
        service = ServiceHistory(
            client_id=client.id,
            package_id=package.id,
            service_type=ServiceType.MASSAGE,
            provider_name="Test Provider",
            date_of_service=datetime.now(timezone.utc)
        )
        async_session.add(service)
        await async_session.commit()

    assert package.sessions_remaining == 7

@pytest.mark.asyncio
async def test_service_history_model(async_session):
    """Test service history tracking and validation"""
    # Create user and client
    user = User(username="historytest", email="history@test.com", password="testpass123")
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0126",
        service=ServiceType.HAIRCUT,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    # Test valid service history entry
    service = ServiceHistory(
        client_id=client.id,
        service_type=ServiceType.HAIRCUT,
        provider_name="Test Provider",
        date_of_service=datetime.now(timezone.utc),
        service_cost=50.00,
        loyalty_points_earned=10
    )
    async_session.add(service)
    await async_session.commit()

    # Test future date validation
    future_service = ServiceHistory(
        client_id=client.id,
        service_type=ServiceType.HAIRCUT,
        provider_name="Test Provider",
        date_of_service=datetime.now(timezone.utc) + timedelta(days=1),  # Future date
        service_cost=50.00
    )
    async_session.add(future_service)
    with pytest.raises(ValueError, match="cannot be in the future"):
        await async_session.commit()
    await async_session.rollback()
