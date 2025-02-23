import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.main.models import User, Client, ServiceHistory, ServicePackage, ServiceType

@pytest.mark.asyncio
async def test_unique_constraints(async_session):
    """Test unique constraints on username and email"""
    # Create initial user
    user1 = User(
        username="uniquetest",
        email="unique@test.com",
        password="testpass123"
    )
    async_session.add(user1)
    await async_session.commit()

    # Try creating user with same username
    user2 = User(
        username="uniquetest",  # Same username
        email="different@test.com",
        password="testpass123"
    )
    async_session.add(user2)
    with pytest.raises(IntegrityError, match="unique"):
        await async_session.commit()
    await async_session.rollback()

    # Try creating user with same email
    user3 = User(
        username="differentuser",
        email="unique@test.com",  # Same email
        password="testpass123"
    )
    async_session.add(user3)
    with pytest.raises(IntegrityError, match="unique"):
        await async_session.commit()
    await async_session.rollback()

@pytest.mark.asyncio
async def test_package_validation(async_session):
    """Test service package validation rules"""
    # Create user and client
    user = User(
        username="packagevalidation",
        email="packageval@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0500",
        service=ServiceType.MASSAGE,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    # Test invalid sessions count
    package1 = ServicePackage(
        client_id=client.id,
        service_type=ServiceType.MASSAGE,
        total_sessions=0,  # Invalid: must be positive
        sessions_remaining=0,
        purchase_date=datetime.now(timezone.utc),
        expiry_date=datetime.now(timezone.utc) + timedelta(days=365),
        package_cost=800.00
    )
    async_session.add(package1)
    with pytest.raises(ValueError, match="sessions must be positive"):
        await async_session.commit()
    await async_session.rollback()

    # Test sessions_remaining > total_sessions
    package2 = ServicePackage(
        client_id=client.id,
        service_type=ServiceType.MASSAGE,
        total_sessions=5,
        sessions_remaining=10,  # Invalid: more than total
        purchase_date=datetime.now(timezone.utc),
        expiry_date=datetime.now(timezone.utc) + timedelta(days=365),
        package_cost=800.00
    )
    async_session.add(package2)
    with pytest.raises(ValueError, match="cannot exceed total sessions"):
        await async_session.commit()
    await async_session.rollback()

    # Test expiry date in past
    package3 = ServicePackage(
        client_id=client.id,
        service_type=ServiceType.MASSAGE,
        total_sessions=5,
        sessions_remaining=5,
        purchase_date=datetime.now(timezone.utc),
        expiry_date=datetime.now(timezone.utc) - timedelta(days=1),  # Past date
        package_cost=800.00
    )
    async_session.add(package3)
    with pytest.raises(ValueError, match="cannot be in the past"):
        await async_session.commit()
    await async_session.rollback()

@pytest.mark.asyncio
async def test_service_history_validation(async_session):
    """Test service history validation rules"""
    # Create user and client
    user = User(
        username="historyvalidation",
        email="historyval@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0600",
        service=ServiceType.HAIRCUT,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    # Test future service date
    service1 = ServiceHistory(
        client_id=client.id,
        service_type=ServiceType.HAIRCUT,
        provider_name="Test Provider",
        date_of_service=datetime.now(timezone.utc) + timedelta(days=1),  # Future date
        service_cost=50.00
    )
    async_session.add(service1)
    with pytest.raises(ValueError, match="cannot be in the future"):
        await async_session.commit()
    await async_session.rollback()

    # Test negative service cost
    service2 = ServiceHistory(
        client_id=client.id,
        service_type=ServiceType.HAIRCUT,
        provider_name="Test Provider",
        date_of_service=datetime.now(timezone.utc),
        service_cost=-50.00  # Negative cost
    )
    async_session.add(service2)
    with pytest.raises(ValueError, match="cannot be negative"):
        await async_session.commit()
    await async_session.rollback()

    # Test negative loyalty points
    service3 = ServiceHistory(
        client_id=client.id,
        service_type=ServiceType.HAIRCUT,
        provider_name="Test Provider",
        date_of_service=datetime.now(timezone.utc),
        service_cost=50.00,
        loyalty_points_earned=-50  # Negative points
    )
    async_session.add(service3)
    with pytest.raises(ValueError, match="cannot be negative"):
        await async_session.commit()
    await async_session.rollback()

@pytest.mark.asyncio
async def test_client_status_validation(async_session):
    """Test client status validation"""
    # Create user
    user = User(
        username="statustest",
        email="status@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    # Test invalid status
    client = Client(
        user_id=user.id,
        phone="555-0700",
        service=ServiceType.HAIRCUT,
        status="INVALID_STATUS"  # Invalid status
    )
    async_session.add(client)
    with pytest.raises(ValueError, match="Invalid status"):
        await async_session.commit()
    await async_session.rollback()

    # Test status transition validation
    client = Client(
        user_id=user.id,
        phone="555-0700",
        service=ServiceType.HAIRCUT,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    # Try to change status directly to terminated without going through inactive
    client.status = "terminated"
    with pytest.raises(ValueError, match="Invalid status transition"):
        await async_session.commit()
    await async_session.rollback()
