# src/test/test_appointment_model.py
import pytest
from datetime import datetime, timedelta
from sqlalchemy import select
from src.main.models import User, Appointment
from src.main.schema import AppointmentStatus
import uuid

@pytest.mark.asyncio
async def test_create_appointment(async_session):
    # Create test users
    creator = User(
        username="creator",
        email="creator@test.com",
        password="testpass123",
        first_name="Test",
        last_name="Creator"
    )
    attendee = User(
        username="attendee",
        email="attendee@test.com",
        password="testpass123",
        first_name="Test",
        last_name="Attendee"
    )
    async_session.add_all([creator, attendee])
    await async_session.commit()
    
    # Create appointment
    start_time = datetime.now() + timedelta(days=1)
    appointment = Appointment(
        title="Test Appointment",
        description="Test Description",
        start_time=start_time,
        duration_minutes=60,
        creator_id=creator.id
    )
    appointment.attendees.append(attendee)
    
    async_session.add(appointment)
    await async_session.commit()
    
    # Verify appointment was created
    stmt = select(Appointment).where(Appointment.id == appointment.id)
    result = await async_session.execute(stmt)
    saved_appointment = result.scalar_one()
    
    assert saved_appointment.title == "Test Appointment"
    assert saved_appointment.description == "Test Description"
    assert saved_appointment.start_time == start_time
    assert saved_appointment.duration_minutes == 60
    assert saved_appointment.creator_id == creator.id
    assert saved_appointment.status == AppointmentStatus.SCHEDULED
    assert len(saved_appointment.attendees) == 1
    assert saved_appointment.attendees[0].id == attendee.id

@pytest.mark.asyncio
async def test_update_appointment(async_session):
    # Create test user and appointment
    user = User(
        username="testuser",
        email="test@test.com",
        password="testpass123",
        first_name="Test",
        last_name="User"
    )
    async_session.add(user)
    await async_session.commit()
    
    appointment = Appointment(
        title="Original Title",
        description="Original Description",
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=60,
        creator_id=user.id
    )
    async_session.add(appointment)
    await async_session.commit()
    
    # Update appointment
    new_start_time = datetime.now() + timedelta(days=2)
    appointment.title = "Updated Title"
    appointment.description = "Updated Description"
    appointment.start_time = new_start_time
    appointment.duration_minutes = 90
    appointment.status = AppointmentStatus.CONFIRMED
    
    await async_session.commit()
    
    # Verify updates
    stmt = select(Appointment).where(Appointment.id == appointment.id)
    result = await async_session.execute(stmt)
    updated_appointment = result.scalar_one()
    
    assert updated_appointment.title == "Updated Title"
    assert updated_appointment.description == "Updated Description"
    assert updated_appointment.start_time == new_start_time
    assert updated_appointment.duration_minutes == 90
    assert updated_appointment.status == AppointmentStatus.CONFIRMED

@pytest.mark.asyncio
async def test_manage_attendees(async_session):
    # Create test users
    creator = User(username="creator", email="creator@test.com", password="testpass123", first_name="Test", last_name="Creator")
    attendee1 = User(username="attendee1", email="attendee1@test.com", password="testpass123", first_name="Test", last_name="Attendee1")
    attendee2 = User(username="attendee2", email="attendee2@test.com", password="testpass123", first_name="Test", last_name="Attendee2")
    async_session.add_all([creator, attendee1, attendee2])
    await async_session.commit()
    
    # Create appointment with one attendee
    appointment = Appointment(
        title="Test Appointment",
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=60,
        creator_id=creator.id
    )
    appointment.attendees.append(attendee1)
    async_session.add(appointment)
    await async_session.commit()
    
    # Add second attendee
    appointment.attendees.append(attendee2)
    await async_session.commit()
    
    # Verify both attendees are present
    stmt = select(Appointment).where(Appointment.id == appointment.id)
    result = await async_session.execute(stmt)
    saved_appointment = result.scalar_one()
    
    assert len(saved_appointment.attendees) == 2
    attendee_ids = {attendee.id for attendee in saved_appointment.attendees}
    assert attendee1.id in attendee_ids
    assert attendee2.id in attendee_ids
    
    # Remove first attendee
    appointment.attendees.remove(attendee1)
    await async_session.commit()
    
    # Verify only second attendee remains
    stmt = select(Appointment).where(Appointment.id == appointment.id)
    result = await async_session.execute(stmt)
    saved_appointment = result.scalar_one()
    
    assert len(saved_appointment.attendees) == 1
    assert saved_appointment.attendees[0].id == attendee2.id

@pytest.mark.asyncio
async def test_cascade_delete(async_session):
    # Create test users
    creator = User(username="creator", email="creator@test.com", password="testpass123", first_name="Test", last_name="Creator")
    attendee = User(username="attendee", email="attendee@test.com", password="testpass123", first_name="Test", last_name="Attendee")
    async_session.add_all([creator, attendee])
    await async_session.commit()
    
    # Create appointment
    appointment = Appointment(
        title="Test Appointment",
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=60,
        creator_id=creator.id
    )
    appointment.attendees.append(attendee)
    async_session.add(appointment)
    await async_session.commit()
    
    # Delete appointment
    await async_session.delete(appointment)
    await async_session.commit()
    
    # Verify appointment is deleted but users remain
    stmt = select(Appointment).where(Appointment.id == appointment.id)
    result = await async_session.execute(stmt)
    assert result.scalar_one_or_none() is None
    
    stmt = select(User).where(User.id.in_([creator.id, attendee.id]))
    result = await async_session.execute(stmt)
    remaining_users = result.scalars().all()
    assert len(remaining_users) == 2
