import pytest
from datetime import datetime, timedelta
from sqlalchemy import select, text, and_
from src.main.models import User, Appointment, appointment_attendees
from src.main.schema import AppointmentStatus

@pytest.mark.asyncio
async def test_user_attending_appointments(async_session):
    """Test user's attending_appointments relationship"""
    # Create test user
    user = User(
        username="attendeetest",
        email="attendee@test.com",
        password="testpass123",
        first_name="Test",
        last_name="Attendee"
    )
    
    # Create multiple appointments
    # First create and commit the user
    async_session.add(user)
    await async_session.commit()

    # Now create appointments with the committed user's ID
    appointment1 = Appointment(
        title="Meeting 1",
        description="First meeting",
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=60,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    
    appointment2 = Appointment(
        title="Meeting 2",
        description="Second meeting",
        start_time=datetime.now() + timedelta(days=2),
        duration_minutes=60,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    
    # Add user as attendee to both appointments
    appointment1.attendees.append(user)
    appointment2.attendees.append(user)
    
    # Add and commit appointments
    async_session.add_all([appointment1, appointment2])
    await async_session.commit()
    
    # Refresh user to get updated relationships
    await async_session.refresh(user)
    
    # Query appointments explicitly
    stmt = select(Appointment).join(appointment_attendees).where(appointment_attendees.c.user_id == user.id)
    result = await async_session.execute(stmt)
    attending_appointments = result.scalars().all()
    
    assert len(attending_appointments) == 2
    titles = {apt.title for apt in attending_appointments}
    assert "Meeting 1" in titles
    assert "Meeting 2" in titles

@pytest.mark.asyncio
async def test_appointment_by_status(async_session):
    """Test filtering appointments by status"""
    # Create test user
    user = User(
        username="statustest",
        email="status@test.com",
        password="testpass123",
        first_name="Test",
        last_name="Status"
    )
    async_session.add(user)
    await async_session.commit()
    
    # Create appointments with different statuses
    appointments = [
        Appointment(
            title=f"Meeting {status.value}",
            start_time=datetime.now() + timedelta(days=1),
            duration_minutes=60,
            creator_id=user.id,
            status=status
        )
        for status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED]
    ]
    
    async_session.add_all(appointments)
    await async_session.commit()
    
    # Query appointments by each status
    for status in AppointmentStatus:
        stmt = select(Appointment).where(Appointment.status == status)
        result = await async_session.execute(stmt)
        filtered_appointments = result.scalars().all()
        
        if status == AppointmentStatus.COMPLETED:
            assert len(filtered_appointments) == 0
        else:
            assert len(filtered_appointments) == 1
            assert filtered_appointments[0].status == status

@pytest.mark.asyncio
async def test_overlapping_appointments(async_session):
    """Test detection of overlapping appointments"""
    # Create test user
    user = User(
        username="overlaptest",
        email="overlap@test.com",
        password="testpass123",
        first_name="Test",
        last_name="Overlap"
    )
    async_session.add(user)
    await async_session.commit()
    
    # Create first appointment
    base_time = datetime.now() + timedelta(days=1)
    appointment1 = Appointment(
        title="First Meeting",
        start_time=base_time,
        duration_minutes=60,
        creator_id=user.id
    )
    appointment1.attendees.append(user)
    async_session.add(appointment1)
    await async_session.commit()
    
    # Query overlapping appointments
    overlap_start = base_time + timedelta(minutes=30)
    # Calculate end time using PostgreSQL-specific functions
    overlap_check = select(Appointment).where(
        and_(
            Appointment.id == appointment1.id,
            Appointment.start_time <= overlap_start,
            Appointment.start_time + text("INTERVAL '1 minute' * duration_minutes") > overlap_start
        )
    )
    
    result = await async_session.execute(overlap_check)
    overlapping = result.scalars().all()
    assert len(overlapping) == 1
    assert overlapping[0].id == appointment1.id

@pytest.mark.asyncio
async def test_future_start_time(async_session):
    """Test that appointments cannot be created with past start times"""
    
    user = User(
        username="futuretest",
        email="future@test.com",
        password="testpass123",
        first_name="Test",
        last_name="Future"
    )
    async_session.add(user)
    await async_session.commit()
    
    # Try to create appointment in the past
    past_appointment = Appointment(
        title="Past Meeting",
        start_time=datetime.now() - timedelta(days=1),
        duration_minutes=60,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    
    async_session.add(past_appointment)
    with pytest.raises(Exception):  # Should raise validation error
        await async_session.commit()
        
    await async_session.rollback()
    
    # Verify appointment was not created
    stmt = select(Appointment).where(Appointment.title == "Past Meeting")
    result = await async_session.execute(stmt)
    assert result.scalar_one_or_none() is None

@pytest.mark.asyncio
async def test_appointment_duration_validation(async_session):
    """Test appointment duration validations"""
    user = User(
        username="durationtest",
        email="duration@test.com",
        password="testpass123",
        first_name="Test",
        last_name="Duration"
    )
    async_session.add(user)
    await async_session.commit()

    # Test duration too short (< 15 minutes)
    short_appointment = Appointment(
        title="Short Meeting",
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=10,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    
    async_session.add(short_appointment)
    with pytest.raises(ValueError, match="Appointment duration must be at least 15 minutes"):
        await async_session.commit()
    await async_session.rollback()

    # Test duration too long (> 480 minutes)
    long_appointment = Appointment(
        title="Long Meeting",
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=481,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    
    async_session.add(long_appointment)
    with pytest.raises(ValueError, match="Appointment duration cannot exceed 8 hours"):
        await async_session.commit()
    await async_session.rollback()

    # Test valid duration
    valid_appointment = Appointment(
        title="Valid Meeting",
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=60,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    
    async_session.add(valid_appointment)
    await async_session.commit()
    
    # Verify valid appointment was created
    stmt = select(Appointment).where(Appointment.title == "Valid Meeting")
    result = await async_session.execute(stmt)
    assert result.scalar_one_or_none() is not None

@pytest.mark.asyncio
async def test_appointment_string_lengths(async_session):
    """Test appointment title and description length validations"""
    user = User(
        username="lengthtest",
        email="length@test.com",
        password="testpass123",
        first_name="Test",
        last_name="Length"
    )
    async_session.add(user)
    await async_session.commit()

    # Test title length (max 100 chars)
    long_title = "A" * 101
    title_appointment = Appointment(
        title=long_title,
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=60,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    
    async_session.add(title_appointment)
    with pytest.raises(Exception):  # SQLAlchemy will raise an error for exceeding varchar length
        await async_session.commit()
    await async_session.rollback()

    # Test description length (max 500 chars)
    long_description = "A" * 501
    desc_appointment = Appointment(
        title="Description Test",
        description=long_description,
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=60,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    
    async_session.add(desc_appointment)
    with pytest.raises(Exception):  # SQLAlchemy will raise an error for exceeding varchar length
        await async_session.commit()
    await async_session.rollback()

    # Test valid lengths
    valid_appointment = Appointment(
        title="Valid Title",
        description="Valid description",
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=60,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    
    async_session.add(valid_appointment)
    await async_session.commit()
    
    # Verify valid appointment was created
    stmt = select(Appointment).where(Appointment.title == "Valid Title")
    result = await async_session.execute(stmt)
    assert result.scalar_one_or_none() is not None

@pytest.mark.asyncio
async def test_appointment_update_validation(async_session):
    """Test appointment update validations"""
    user = User(
        username="updatetest",
        email="update@test.com",
        password="testpass123",
        first_name="Test",
        last_name="Update"
    )
    async_session.add(user)
    await async_session.commit()

    # Create a valid appointment
    appointment = Appointment(
        title="Update Test",
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=60,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    async_session.add(appointment)
    await async_session.commit()

    # Test updating to invalid past time
    appointment.start_time = datetime.now() - timedelta(days=1)
    with pytest.raises(ValueError, match="Appointment start time cannot be in the past"):
        await async_session.commit()
    await async_session.rollback()
    
    # Reset appointment state
    await async_session.refresh(appointment)

    # Test updating to invalid duration
    appointment.duration_minutes = 10
    with pytest.raises(ValueError, match="Appointment duration must be at least 15 minutes"):
        await async_session.commit()
    await async_session.rollback()
    
    # Reset appointment state
    await async_session.refresh(appointment)

    # Test valid update
    new_title = "Updated Meeting"
    appointment.title = new_title
    appointment.duration_minutes = 120
    await async_session.commit()

    # Verify update was successful
    stmt = select(Appointment).where(Appointment.title == new_title)
    result = await async_session.execute(stmt)
    updated_appointment = result.scalar_one_or_none()
    assert updated_appointment is not None
    assert updated_appointment.duration_minutes == 120

@pytest.mark.asyncio
async def test_appointment_required_fields(async_session):
    """Test required fields validation"""
    user = User(
        username="requiredtest",
        email="required@test.com",
        password="testpass123",
        first_name="Test",
        last_name="Required"
    )
    async_session.add(user)
    await async_session.commit()

    # Test missing title (nullable=False)
    appointment_no_title = Appointment(
        start_time=datetime.now() + timedelta(days=1),
        duration_minutes=60,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    
    async_session.add(appointment_no_title)
    with pytest.raises(Exception):  # SQLAlchemy will raise an error for null in non-nullable column
        await async_session.commit()
    await async_session.rollback()

    # Test timezone awareness
    from datetime import timezone
    utc_time = datetime.now(timezone.utc) + timedelta(days=1)
    appointment_with_tz = Appointment(
        title="Timezone Test",
        start_time=utc_time,
        duration_minutes=60,
        creator_id=user.id,
        status=AppointmentStatus.SCHEDULED
    )
    
    async_session.add(appointment_with_tz)
    await async_session.commit()
    
    # Verify appointment was created with timezone
    stmt = select(Appointment).where(Appointment.title == "Timezone Test")
    result = await async_session.execute(stmt)
    tz_appointment = result.scalar_one_or_none()
    assert tz_appointment is not None
    assert tz_appointment.start_time.tzinfo is not None  # Verify timezone info is preserved
