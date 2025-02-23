import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from src.main.models import User, Client, ServiceHistory, ServicePackage, ServiceType

@pytest.mark.asyncio
async def test_user_clients_relationship(async_session):
    """Test relationship between users and their clients"""
    # Create user with multiple clients
    user = User(
        username="multiclients",
        email="multi@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    # Create multiple clients for the user
    clients = [
        Client(
            user_id=user.id,
            phone=f"555-{i:04d}",
            service=ServiceType.HAIRCUT,
            status="active"
        )
        for i in range(3)
    ]
    async_session.add_all(clients)
    await async_session.commit()

    # Query user with clients
    stmt = select(User).options(
        selectinload(User.clients)
    ).where(User.username == "multiclients")
    result = await async_session.execute(stmt)
    fetched_user = result.scalar_one()

    assert len(fetched_user.clients) == 3
    assert all(c.status == "active" for c in fetched_user.clients)

@pytest.mark.asyncio
async def test_client_service_history_relationship(async_session):
    """Test relationship between clients and their service history"""
    # Create user and client
    user = User(
        username="historyrel",
        email="historyrel@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0800",
        service=ServiceType.HAIRCUT,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    # Create multiple service history entries
    base_time = datetime.now(timezone.utc) - timedelta(days=30)
    services = [
        ServiceHistory(
            client_id=client.id,
            service_type=ServiceType.HAIRCUT,
            provider_name="Test Provider",
            date_of_service=base_time + timedelta(days=i*7),
            service_cost=50.00
        )
        for i in range(4)
    ]
    async_session.add_all(services)
    await async_session.commit()

    # Query client with service history
    stmt = select(Client).options(
        selectinload(Client.service_history)
    ).where(Client.id == client.id)
    result = await async_session.execute(stmt)
    fetched_client = result.scalar_one()

    assert len(fetched_client.service_history) == 4
    assert all(s.service_type == ServiceType.HAIRCUT for s in fetched_client.service_history)

@pytest.mark.asyncio
async def test_complex_service_queries(async_session):
    """Test complex queries involving multiple relationships"""
    # Create test data
    user = User(username="complextest", email="complex@test.com", password="testpass123")
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0900",
        service=ServiceType.MASSAGE,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    # Create package and associated services
    package = ServicePackage(
        client_id=client.id,
        service_type=ServiceType.MASSAGE,
        total_sessions=10,
        sessions_remaining=7,
        purchase_date=datetime.now(timezone.utc),
        expiry_date=datetime.now(timezone.utc) + timedelta(days=365),
        package_cost=800.00
    )
    async_session.add(package)
    await async_session.commit()

    base_time = datetime.now(timezone.utc) - timedelta(days=30)
    services = [
        ServiceHistory(
            client_id=client.id,
            service_type=ServiceType.MASSAGE,
            provider_name="Test Provider",
            date_of_service=base_time + timedelta(days=i*7),
            service_cost=100.00,
            package_id=package.id
        )
        for i in range(3)
    ]
    async_session.add_all(services)
    await async_session.commit()

    # Query for services used from package
    stmt = select(ServiceHistory).where(
        ServiceHistory.package_id == package.id
    ).order_by(ServiceHistory.date_of_service)
    result = await async_session.execute(stmt)
    package_services = result.scalars().all()

    assert len(package_services) == 3
    assert all(s.package_id == package.id for s in package_services)
    assert package.sessions_remaining == 7

    # Calculate service statistics
    stmt = select(
        func.count(ServiceHistory.id).label('total_services'),
        func.sum(ServiceHistory.service_cost).label('total_cost'),
        func.avg(ServiceHistory.service_cost).label('avg_cost')
    ).where(ServiceHistory.client_id == client.id)
    result = await async_session.execute(stmt)
    stats = result.one()

    assert stats.total_services == 3
    assert stats.total_cost == 300.00
    assert stats.avg_cost == 100.00

@pytest.mark.asyncio
async def test_referral_chain_relationship(async_session):
    """Test referral chain relationships between clients"""
    # Create initial user
    user = User(username="referraltest", email="referral@test.com", password="testpass123")
    async_session.add(user)
    await async_session.commit()

    # Create chain of referred clients
    prev_client = None
    clients = []
    for i in range(3):
        client = Client(
            user_id=user.id,
            phone=f"555-{1000+i}",
            service=ServiceType.HAIRCUT,
            status="active",
            referred_by=prev_client.id if prev_client else None
        )
        async_session.add(client)
        await async_session.commit()
        clients.append(client)
        prev_client = client

    # Query referral chain
    for i in range(1, 3):
        stmt = select(Client).options(
            joinedload(Client.referred_by_client)
        ).where(Client.id == clients[i].id)
        result = await async_session.execute(stmt)
        current_client = result.scalar_one()
        
        assert current_client.referred_by == clients[i-1].id
        assert current_client.referred_by_client.phone == f"555-{1000+i-1}"

    # Query clients referred by first client
    stmt = select(Client).where(Client.referred_by == clients[0].id)
    result = await async_session.execute(stmt)
    referred_clients = result.scalars().all()
    
    assert len(referred_clients) == 1
    assert referred_clients[0].id == clients[1].id
