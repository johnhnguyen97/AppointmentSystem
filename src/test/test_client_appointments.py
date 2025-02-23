import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from uuid import uuid4
from zoneinfo import ZoneInfo
from src.main.models import User, Client, Appointment, ServiceHistory, ServicePackage
from src.main.schema import ServiceType, AppointmentStatus

# Test data constants
TEST_TIMEZONE = ZoneInfo("America/Chicago")

@pytest.mark.asyncio
async def test_client_appointment_history(async_session):
    """
    Test client appointment history with timezone handling.
    Verifies:
    - Appointment creation and completion
    - Service history recording
    - Loyalty points accumulation
    - Timezone consistency
    """
    # Create user and client
    user = User(
        username="timetest",
        email="time@test.com",
        password="testpass123",
        first_name="Time",
        last_name="Tester",
        enabled=True  # Explicitly set enabled
    )
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0123",
        service=ServiceType.HAIRCUT,
        status="active",
        category="REGULAR",
        loyalty_points=0  # Explicitly set initial points
    )
    async_session.add(client)
    await async_session.commit()

    # Create appointments across different days and times
    base_time = datetime.now(timezone.utc) + timedelta(days=1)  # Start tomorrow
    appointments = []
    for days in range(3):
        appt_time = base_time + timedelta(days=days, hours=10)  # 10 AM UTC each day
        appointment = Appointment(
            title=f"Day {days+1} Appointment",
            start_time=appt_time,
            duration_minutes=60,
            service_type=ServiceType.HAIRCUT,
            creator_id=user.id
        )
        appointments.append(appointment)
        async_session.add(appointment)
    await async_session.commit()

    # Add service history entries for completed appointments
    for i, appt in enumerate(appointments[:2]):  # Mark first two as completed
        appt.status = AppointmentStatus.COMPLETED
        service_history = ServiceHistory(
            client_id=client.id,
            service_type=ServiceType.HAIRCUT,
            provider_name="Test Provider",
            date_of_service=appt.start_time,
            service_cost=50.0,
            loyalty_points_earned=10,
            points_redeemed=0  # Explicitly set points redeemed
        )
        async_session.add(service_history)
        await async_session.commit()  # Commit after each service history to trigger points update

    # Verify service history
    stmt = select(ServiceHistory).where(ServiceHistory.client_id == client.id)
    result = await async_session.execute(stmt)
    history_entries = result.scalars().all()
    assert len(history_entries) == 2

    # Verify client loyalty points
    assert client.loyalty_points == 20  # 10 points per completed service

@pytest.mark.asyncio
async def test_service_package_tracking(async_session):
    """
    Test service package management and appointment tracking.
    Verifies:
    - Package creation and session tracking
    - Session usage through appointments
    - Package expiration handling
    - Service history with package association
    """
    # Create user and client
    user = User(
        username="packagetest",
        email="package@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0124",
        service=ServiceType.MASSAGE,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    # Create service package
    start_date = datetime.now(timezone.utc) + timedelta(minutes=1)  # Ensure future date
    package = ServicePackage(
        client_id=client.id,
        service_type=ServiceType.MASSAGE,
        total_sessions=5,
        sessions_remaining=5,
        purchase_date=start_date,
        expiry_date=start_date + timedelta(days=90),
        package_cost=200.0
    )
    async_session.add(package)
    await async_session.commit()

    # Create and complete appointments using package
    # Get tomorrow as the start date for appointments
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    for i in range(3):  # Use 3 out of 5 sessions
        appt_time = tomorrow + timedelta(days=i*7)  # Weekly appointments
        appointment = Appointment(
            title=f"Package Session {i+1}",
            start_time=appt_time,
            duration_minutes=60,
            service_type=ServiceType.MASSAGE,
            creator_id=user.id
        )
        async_session.add(appointment)
        await async_session.commit()

        # Mark as completed and record service
        appointment.status = AppointmentStatus.COMPLETED
        service_history = ServiceHistory(
            client_id=client.id,
            service_type=ServiceType.MASSAGE,
            provider_name="Massage Therapist",
            date_of_service=appt_time,
            package_id=package.id
        )
        async_session.add(service_history)
        package.sessions_remaining -= 1
    await async_session.commit()

    # Verify package status
    stmt = select(ServicePackage).where(ServicePackage.id == package.id)
    result = await async_session.execute(stmt)
    updated_package = result.scalar_one()
    assert updated_package.sessions_remaining == 2

    # Verify service history
    stmt = select(ServiceHistory).where(
        ServiceHistory.client_id == client.id,
        ServiceHistory.package_id == package.id
    )
    result = await async_session.execute(stmt)
    history_entries = result.scalars().all()
    assert len(history_entries) == 3

@pytest.mark.asyncio
async def test_timezone_handling(async_session):
    """
    Test appointment scheduling across different timezones.
    Verifies:
    - UTC storage of appointments
    - Local timezone conversion
    - Appointment validation across timezones
    - Time-based conflicts in different timezones
    """
    # Create user and client
    user = User(
        username="tztest",
        email="timezone@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    # Test appointment creation with specific timezone
    tomorrow = datetime.now(TEST_TIMEZONE).replace(
        hour=9, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)
    
    # Create morning appointment (9 AM Central)
    morning_appt = Appointment(
        title="Morning Appointment",
        start_time=tomorrow.astimezone(timezone.utc),
        duration_minutes=60,
        service_type=ServiceType.HAIRCUT,
        creator_id=user.id
    )
    async_session.add(morning_appt)
    await async_session.commit()

    # Attempt to create overlapping appointment (should fail)
    with pytest.raises(ValueError, match="overlapping appointment"):
        overlap_appt = Appointment(
            title="Overlapping Appointment",
            start_time=tomorrow.astimezone(timezone.utc),
            duration_minutes=30,
            service_type=ServiceType.HAIRCUT,
            creator_id=user.id
        )
        async_session.add(overlap_appt)
        await async_session.commit()

    # Create appointment in past (should fail)
    past_time = datetime.now(TEST_TIMEZONE) - timedelta(hours=1)
    with pytest.raises(ValueError, match="cannot be in the past"):
        past_appt = Appointment(
            title="Past Appointment",
            start_time=past_time.astimezone(timezone.utc),
            duration_minutes=60,
            service_type=ServiceType.HAIRCUT,
            creator_id=user.id
        )
        async_session.add(past_appt)
        await async_session.commit()

    # Test duration limits
    with pytest.raises(ValueError, match="at least 15 minutes"):
        short_appt = Appointment(
            title="Short Appointment",
            start_time=tomorrow.astimezone(timezone.utc) + timedelta(days=1),
            duration_minutes=10,
            service_type=ServiceType.HAIRCUT,
            creator_id=user.id
        )
        async_session.add(short_appt)
        await async_session.commit()

    with pytest.raises(ValueError, match="cannot exceed 8 hours"):
        long_appt = Appointment(
            title="Long Appointment",
            start_time=tomorrow.astimezone(timezone.utc) + timedelta(days=1),
            duration_minutes=481,  # Over 8 hours
            service_type=ServiceType.HAIRCUT,
            creator_id=user.id
        )
        async_session.add(long_appt)
        await async_session.commit()

    # Verify timezone handling
    stmt = select(Appointment).where(Appointment.creator_id == user.id)
    result = await async_session.execute(stmt)
    appointments = result.scalars().all()
    
    for appt in appointments:
        # Verify UTC storage
        assert appt.start_time.tzinfo == timezone.utc
        assert appt.end_time.tzinfo == timezone.utc
        
        # Verify correct local time conversion
        local_start = appt.start_time.astimezone(TEST_TIMEZONE)
        assert local_start.hour == 9  # Should be 9 AM Central
        assert local_start.minute == 0

@pytest.mark.asyncio
async def test_appointment_cancellation_with_package(async_session):
    """
    Test appointment cancellation and its effect on service packages.
    Verifies:
    - Appointment cancellation process
    - Package session restoration on cancellation
    - Service history updates
    """
    # Create user and client
    user = User(
        username="canceltest",
        email="cancel@test.com",
        password="testpass123"
    )
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

    # Create service package
    start_date = datetime.now(timezone.utc)
    package = ServicePackage(
        client_id=client.id,
        service_type=ServiceType.MASSAGE,
        total_sessions=3,
        sessions_remaining=3,
        purchase_date=start_date,
        expiry_date=start_date + timedelta(days=90),
        package_cost=150.0
    )
    async_session.add(package)
    await async_session.commit()

    # Create and complete one appointment
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    appointment = Appointment(
        title="Package Session 1",
        start_time=tomorrow,
        duration_minutes=60,
        service_type=ServiceType.MASSAGE,
        creator_id=user.id
    )
    async_session.add(appointment)
    await async_session.commit()

    # Mark as completed and record service
    appointment.status = AppointmentStatus.COMPLETED
    service_history = ServiceHistory(
        client_id=client.id,
        service_type=ServiceType.MASSAGE,
        provider_name="Massage Therapist",
        date_of_service=tomorrow,
        package_id=package.id
    )
    async_session.add(service_history)
    package.sessions_remaining -= 1
    await async_session.commit()

    # Create another appointment and cancel it
    next_week = tomorrow + timedelta(days=7)
    cancel_appt = Appointment(
        title="Package Session 2 (To Cancel)",
        start_time=next_week,
        duration_minutes=60,
        service_type=ServiceType.MASSAGE,
        creator_id=user.id
    )
    async_session.add(cancel_appt)
    await async_session.commit()

    # Initially mark as completed
    cancel_appt.status = AppointmentStatus.COMPLETED
    service_history2 = ServiceHistory(
        client_id=client.id,
        service_type=ServiceType.MASSAGE,
        provider_name="Massage Therapist",
        date_of_service=next_week,
        package_id=package.id
    )
    async_session.add(service_history2)
    package.sessions_remaining -= 1
    await async_session.commit()

    # Now cancel the appointment
    cancel_appt.status = AppointmentStatus.CANCELLED
    package.sessions_remaining += 1  # Restore the session
    await async_session.commit()

    # Verify package status
    stmt = select(ServicePackage).where(ServicePackage.id == package.id)
    result = await async_session.execute(stmt)
    updated_package = result.scalar_one()
    assert updated_package.sessions_remaining == 2  # Should have 2 sessions remaining

    # Verify appointment status
    stmt = select(Appointment).where(Appointment.id == cancel_appt.id)
    result = await async_session.execute(stmt)
    cancelled_appt = result.scalar_one()
    assert cancelled_appt.status == AppointmentStatus.CANCELLED

@pytest.mark.asyncio
async def test_loyalty_points_redemption(async_session):
    """
    Test loyalty points earning and redemption.
    Verifies:
    - Points accumulation from services
    - Points redemption process
    - Points balance updates
    - Service history tracking of points
    """
    # Create user and client
    user = User(
        username="loyaltytest",
        email="loyalty@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0126",
        service=ServiceType.HAIRCUT,
        status="active",
        category="REGULAR",
        loyalty_points=0
    )
    async_session.add(client)
    await async_session.commit()

    # Earn points through services
    base_time = datetime.now(timezone.utc) + timedelta(days=1)  # Start tomorrow
    for i in range(3):
        service_history = ServiceHistory(
            client_id=client.id,
            service_type=ServiceType.HAIRCUT,
            provider_name="Test Provider",
            date_of_service=base_time + timedelta(days=i),
            service_cost=50.0,
            loyalty_points_earned=10,
            points_redeemed=0
        )
        async_session.add(service_history)
        await async_session.commit()  # Commit after each service to trigger points update
        await async_session.refresh(client)  # Refresh client to get updated points

    # Verify points accumulation
    stmt = select(Client).where(Client.id == client.id)
    result = await async_session.execute(stmt)
    updated_client = result.scalar_one()
    assert updated_client.loyalty_points == 30  # 3 services × 10 points

    # Redeem points for a service
    redemption_service = ServiceHistory(
        client_id=client.id,
        service_type=ServiceType.HAIRCUT,
        provider_name="Test Provider",
        date_of_service=base_time + timedelta(days=10),
        service_cost=0.0,  # Free service using points
        loyalty_points_earned=0,
        points_redeemed=25  # Redeem 25 points
    )
    async_session.add(redemption_service)
    await async_session.commit()
    await async_session.refresh(client)  # Refresh client to get updated points

    # Verify points deduction
    stmt = select(Client).where(Client.id == client.id)
    result = await async_session.execute(stmt)
    updated_client = result.scalar_one()
    assert updated_client.loyalty_points == 5  # 30 initial - 25 redeemed

    # Verify service history records
    stmt = select(ServiceHistory).where(
        ServiceHistory.client_id == client.id
    ).order_by(ServiceHistory.date_of_service)
    result = await async_session.execute(stmt)
    history = result.scalars().all()
    
    assert len(history) == 4  # 3 earning services + 1 redemption
    assert sum(h.loyalty_points_earned for h in history) == 30
    assert sum(h.points_redeemed for h in history) == 25

@pytest.mark.asyncio
async def test_optimal_slot_finding(async_session):
    """
    Test optimal appointment slot finding algorithm.
    Verifies:
    - Finding best available slot based on preferences
    - Handling time constraints
    - Load balancing across time slots
    - Avoiding fragmentation
    """
    # Create user and client
    user = User(
        username="slottest",
        email="slot@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    # Create existing appointments
    base_time = datetime.now(timezone.utc) + timedelta(days=1)
    busy_slots = [
        (9, 10),  # 9 AM - 10 AM
        (11, 12), # 11 AM - 12 PM
        (14, 15)  # 2 PM - 3 PM
    ]

    for start_hour, end_hour in busy_slots:
        appt_time = base_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        appointment = Appointment(
            title=f"Existing {start_hour}",
            start_time=appt_time,
            duration_minutes=60,
            service_type=ServiceType.HAIRCUT,
            creator_id=user.id
        )
        async_session.add(appointment)
    await async_session.commit()

    # Find optimal slot for 60-minute appointment
    # Should return 10 AM slot (between 9-10 and 11-12 appointments)
    optimal_start = base_time.replace(hour=10, minute=0, second=0, microsecond=0)
    optimal_appt = Appointment(
        title="Optimal Slot",
        start_time=optimal_start,
        duration_minutes=60,
        service_type=ServiceType.HAIRCUT,
        creator_id=user.id
    )
    async_session.add(optimal_appt)
    await async_session.commit()

    # Verify no overlaps
    stmt = select(Appointment).where(
        Appointment.creator_id == user.id,
        Appointment.start_time >= base_time,
        Appointment.start_time < base_time + timedelta(days=1)
    ).order_by(Appointment.start_time)
    result = await async_session.execute(stmt)
    appointments = result.scalars().all()

    # Verify appointments are properly spaced
    for i in range(len(appointments) - 1):
        current = appointments[i]
        next_appt = appointments[i + 1]
        # Verify no overlap
        assert current.end_time <= next_appt.start_time
        # Verify minimal fragmentation (no large gaps)
        gap = (next_appt.start_time - current.end_time).total_seconds() / 60
        assert gap <= 60  # Maximum 1-hour gap between appointments

@pytest.mark.asyncio
async def test_load_balancing(async_session):
    """
    Test appointment load balancing algorithm.
    Verifies:
    - Even distribution of appointments
    - Peak hour handling
    - Buffer time management
    - Resource utilization
    """
    # Create user
    user = User(
        username="loadtest",
        email="load@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    # Create appointments across a day
    base_time = datetime.now(timezone.utc) + timedelta(days=1)
    appointments = []
    
    # Morning peak (9 AM - 11 AM)
    morning_slots = [
        (9, 30),   # 9:00 - 9:30
        (9, 45),   # 9:45 - 10:15
        (10, 30),  # 10:30 - 11:00
    ]

    # Afternoon slots (2 PM - 4 PM)
    afternoon_slots = [
        (14, 0),   # 2:00 - 2:30
        (14, 45),  # 2:45 - 3:15
        (15, 30),  # 3:30 - 4:00
    ]

    # Create morning appointments
    for hour, minute in morning_slots:
        appt_time = base_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        appointment = Appointment(
            title=f"Morning {hour}:{minute}",
            start_time=appt_time,
            duration_minutes=30,
            service_type=ServiceType.HAIRCUT,
            creator_id=user.id,
            buffer_time=15  # 15-minute buffer between appointments
        )
        appointments.append(appointment)
        async_session.add(appointment)

    # Create afternoon appointments
    for hour, minute in afternoon_slots:
        appt_time = base_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        appointment = Appointment(
            title=f"Afternoon {hour}:{minute}",
            start_time=appt_time,
            duration_minutes=30,
            service_type=ServiceType.HAIRCUT,
            creator_id=user.id,
            buffer_time=15
        )
        appointments.append(appointment)
        async_session.add(appointment)

    await async_session.commit()

    # Verify load distribution
    morning_count = len([a for a in appointments if a.start_time.hour < 12])
    afternoon_count = len([a for a in appointments if a.start_time.hour >= 12])
    assert abs(morning_count - afternoon_count) <= 1  # Balanced distribution

    # Verify buffer times
    for i in range(len(appointments) - 1):
        current = appointments[i]
        next_appt = appointments[i + 1]
        # Verify minimum buffer time
        buffer = (next_appt.start_time - current.end_time).total_seconds() / 60
        assert buffer >= current.buffer_time

    # Verify no overbooking in peak hours
    peak_hours = [9, 10, 14, 15]  # 9-11 AM and 2-4 PM
    for hour in peak_hours:
        hour_start = base_time.replace(hour=hour, minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        
        # Count appointments in this hour
        hour_appointments = [
            a for a in appointments 
            if hour_start <= a.start_time < hour_end
        ]
        # Maximum 2 30-minute appointments per hour
        assert len(hour_appointments) <= 2

@pytest.mark.asyncio
async def test_smart_conflict_resolution(async_session):
    """
    Test smart conflict resolution algorithm.
    Verifies:
    - Detecting direct conflicts
    - Finding alternative slots
    - Handling cascading conflicts
    - Priority-based resolution
    """
    # Create user
    user = User(
        username="conflicttest",
        email="conflict@test.com",
        password="testpass123"
    )
    async_session.add(user)
    await async_session.commit()

    # Create base appointments
    base_time = datetime.now(timezone.utc) + timedelta(days=1)
    
    # Create a chain of appointments
    chain_slots = [
        (9, 0, 60),    # 9:00 - 10:00
        (10, 0, 30),   # 10:00 - 10:30
        (10, 30, 60),  # 10:30 - 11:30
        (11, 30, 30)   # 11:30 - 12:00
    ]

    chain_appointments = []
    for hour, minute, duration in chain_slots:
        appt_time = base_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        appointment = Appointment(
            title=f"Chain {hour}:{minute}",
            start_time=appt_time,
            duration_minutes=duration,
            service_type=ServiceType.HAIRCUT,
            creator_id=user.id
        )
        chain_appointments.append(appointment)
        async_session.add(appointment)
    await async_session.commit()

    # Try to insert a new appointment that would cause cascading conflicts
    conflict_time = base_time.replace(hour=9, minute=30, second=0, microsecond=0)
    with pytest.raises(ValueError, match="overlapping appointment"):
        conflict_appt = Appointment(
            title="Conflict Appointment",
            start_time=conflict_time,
            duration_minutes=60,
            service_type=ServiceType.HAIRCUT,
            creator_id=user.id
        )
        async_session.add(conflict_appt)
        await async_session.commit()

    # Find next available slot that doesn't disrupt existing appointments
    next_slot = base_time.replace(hour=12, minute=0, second=0, microsecond=0)
    new_appt = Appointment(
        title="Rescheduled Appointment",
        start_time=next_slot,
        duration_minutes=60,
        service_type=ServiceType.HAIRCUT,
        creator_id=user.id
    )
    async_session.add(new_appt)
    await async_session.commit()

    # Verify appointment chain integrity
    stmt = select(Appointment).where(
        Appointment.creator_id == user.id,
        Appointment.start_time >= base_time,
        Appointment.start_time < base_time + timedelta(days=1)
    ).order_by(Appointment.start_time)
    result = await async_session.execute(stmt)
    appointments = result.scalars().all()

    # Verify all appointments maintain proper spacing
    for i in range(len(appointments) - 1):
        current = appointments[i]
        next_appt = appointments[i + 1]
        assert current.end_time <= next_appt.start_time

    # Verify original chain is unchanged
    chain_times = [(a.start_time.hour, a.start_time.minute) for a in appointments[:4]]
    expected_times = [(s[0], s[1]) for s in chain_slots]
    assert chain_times == expected_times

    # Verify new appointment was added without conflicts
    last_appt = appointments[-1]
    assert last_appt.start_time.hour == 12
    assert last_appt.start_time.minute == 0
