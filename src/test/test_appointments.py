import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from uuid import uuid4
from src.main.models import User, Client, Appointment, ServiceType, AppointmentStatus, appointment_attendees

@pytest.mark.asyncio
async def test_appointment_creation(async_session):
    """Test creating an appointment with proper associations"""
    # Create test user and client first
    user = User(
        username="appttest",
        email="appt@test.com",
        password="testpass123",
        first_name="Appointment",
        last_name="Test"
    )
    async_session.add(user)
    await async_session.commit()

    client = Client(
        user_id=user.id,
        phone="555-0123",
        service=ServiceType.HAIRCUT,
        status="active"
    )
    async_session.add(client)
    await async_session.commit()

    # Create appointment
    start_time = datetime.now(timezone.utc) + timedelta(days=1)  # Tomorrow
    appointment = Appointment(
        title="Haircut Appointment",
        description="Regular haircut service",
        start_time=start_time,
        duration_minutes=60,
        service_type=ServiceType.HAIRCUT,
        creator_id=user.id
    )
    async_session.add(appointment)
    await async_session.commit()

    # Add client as attendee using direct SQL
    await async_session.execute(
        appointment_attendees.insert().values(
            user_id=user.id,
            appointment_id=appointment.id
        )
    )
    await async_session.commit()

    # Verify appointment
    stmt = select(Appointment).where(Appointment.id == appointment.id)
    result = await async_session.execute(stmt)
    fetched_appt = result.scalar_one()

    assert fetched_appt.title == "Haircut Appointment"
    assert fetched_appt.duration_minutes == 60
    assert fetched_appt.service_type == ServiceType.HAIRCUT
    assert fetched_appt.status == AppointmentStatus.SCHEDULED
    assert fetched_appt.end_time == start_time + timedelta(minutes=60)

    # Check attendees separately
    stmt_attendees = select(appointment_attendees).where(
        appointment_attendees.c.appointment_id == appointment.id
    )
    result_attendees = await async_session.execute(stmt_attendees)
    attendees = result_attendees.all()
    assert len(attendees) == 1
    assert attendees[0].user_id == user.id

@pytest.mark.asyncio
async def test_appointment_conflicts(async_session):
    """Test detection of conflicting appointments"""
    # Create and store test user IDs first
    user1 = User(username="conflict1", email="conflict1@test.com", password="testpass123")
    user2 = User(username="conflict2", email="conflict2@test.com", password="testpass123")
    async_session.add_all([user1, user2])
    await async_session.commit()
    
    # Store IDs for later use
    user1_id = user1.id
    user2_id = user2.id
    
    # Create first appointment
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    appt1 = Appointment(
        title="First Appointment",
        start_time=start_time,
        duration_minutes=60,
        service_type=ServiceType.HAIRCUT,
        creator_id=user1_id
    )
    async_session.add(appt1)
    await async_session.commit()

    try:
        # Try to create overlapping appointment
        appt2 = Appointment(
            title="Overlapping Appointment",
            start_time=start_time + timedelta(minutes=30),  # Overlaps with first appointment
            duration_minutes=60,
            service_type=ServiceType.HAIRCUT,
            creator_id=user2_id
        )
        async_session.add(appt2)
        await async_session.commit()
        assert False, "Should have detected overlapping appointment"
    except ValueError as e:
        assert "overlapping appointment" in str(e)
    finally:
        await async_session.rollback()

    # Create non-overlapping appointment
    await async_session.rollback()  # Ensure clean session state
    appt3 = Appointment(
        title="Non-overlapping Appointment",
        start_time=start_time + timedelta(hours=2),
        duration_minutes=60,
        service_type=ServiceType.HAIRCUT,
        creator_id=user2_id
    )
    async_session.add(appt3)
    await async_session.commit()

@pytest.mark.asyncio
async def test_multi_attendee_appointments(async_session):
    """Test appointments with multiple attendees"""
    # Create test users
    users = [
        User(username=f"attendee{i}", email=f"attendee{i}@test.com", password="testpass123")
        for i in range(3)
    ]
    async_session.add_all(users)
    await async_session.commit()

    # Create appointment
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    appointment = Appointment(
        title="Group Appointment",
        start_time=start_time,
        duration_minutes=90,
        service_type=ServiceType.HAIRCUT,
        creator_id=users[0].id
    )
    async_session.add(appointment)
    await async_session.commit()

    # Add all users as attendees
    for user in users:
        await async_session.execute(
            appointment_attendees.insert().values(
                user_id=user.id,
                appointment_id=appointment.id
            )
        )
    await async_session.commit()

    # Verify all attendees
    stmt = select(appointment_attendees).where(
        appointment_attendees.c.appointment_id == appointment.id
    )
    result = await async_session.execute(stmt)
    attendees = result.all()
    assert len(attendees) == 3
    attendee_ids = {a.user_id for a in attendees}
    assert all(user.id in attendee_ids for user in users)

@pytest.mark.asyncio
async def test_appointment_cancellation(async_session):
    """Test appointment cancellation flow"""
    user = User(username="canceltest", email="cancel@test.com", password="testpass123")
    async_session.add(user)
    await async_session.commit()

    # Create appointment
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    appointment = Appointment(
        title="Cancellation Test",
        start_time=start_time,
        duration_minutes=60,
        service_type=ServiceType.HAIRCUT,
        creator_id=user.id
    )
    async_session.add(appointment)
    await async_session.commit()

    # Cancel appointment
    appointment.status = AppointmentStatus.CANCELLED
    await async_session.commit()

    # Verify cancellation
    stmt = select(Appointment).where(Appointment.id == appointment.id)
    result = await async_session.execute(stmt)
    fetched_appt = result.scalar_one()
    assert fetched_appt.status == AppointmentStatus.CANCELLED

    # Attempt to schedule new appointment in the cancelled slot
    new_appointment = Appointment(
        title="Replacement Appointment",
        start_time=start_time,
        duration_minutes=60,
        service_type=ServiceType.HAIRCUT,
        creator_id=user.id
    )
    async_session.add(new_appointment)
    await async_session.commit()

@pytest.mark.asyncio
async def test_appointment_rescheduling(async_session):
    """Test appointment rescheduling"""
    user = User(username="rescheduletest", email="reschedule@test.com", password="testpass123")
    async_session.add(user)
    await async_session.commit()

    # Create original appointment
    original_time = datetime.now(timezone.utc) + timedelta(days=1)
    appointment = Appointment(
        title="Original Appointment",
        start_time=original_time,
        duration_minutes=60,
        service_type=ServiceType.HAIRCUT,
        creator_id=user.id
    )
    async_session.add(appointment)
    await async_session.commit()

    # Reschedule appointment
    new_time = original_time + timedelta(days=1)
    appointment.start_time = new_time
    await async_session.commit()

    # Verify rescheduling
    stmt = select(Appointment).where(Appointment.id == appointment.id)
    result = await async_session.execute(stmt)
    fetched_appt = result.scalar_one()
    assert fetched_appt.start_time == new_time
    assert fetched_appt.end_time == new_time + timedelta(minutes=60)
