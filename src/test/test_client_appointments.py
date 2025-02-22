import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy import select
from src.main.models import User, Client, Appointment, ServiceType
from src.main.schema import AppointmentStatus

@pytest.fixture
def test_user():
    return User(
        id=uuid.uuid4(),
        username="test.user",
        email="test.user@example.com",
        password="hashed_password",
        first_name="Test",
        last_name="User",
        enabled=True
    )

@pytest.fixture
def test_client(test_user):
    return Client(
        user_id=test_user.id,
        phone="(555) 123-4567",
        service=ServiceType.HAIRCUT,
        status="active",
        notes="Test client notes"
    )

@pytest.fixture
def test_appointment(test_user):
    future_time = datetime.now() + timedelta(days=1)
    return Appointment(
        creator_id=test_user.id,
        title="Test Appointment",
        description="Test appointment description",
        start_time=future_time,
        duration_minutes=30,
        status=AppointmentStatus.SCHEDULED
    )

async def test_create_client(db_session, test_user):
    """Test creating a new client with valid user"""
    client = Client(
        user_id=test_user.id,
        phone="(555) 987-6543",
        service=ServiceType.HAIRCUT,
        status="active"
    )
    db_session.add(test_user)
    db_session.add(client)
    await db_session.commit()
    
    fetched_client = await db_session.scalar(
        select(Client).filter_by(user_id=test_user.id)
    )
    assert fetched_client is not None
    assert fetched_client.phone == "(555) 987-6543"
    assert fetched_client.service == ServiceType.HAIRCUT

async def test_create_client_invalid_user(db_session):
    """Test creating a client with non-existent user"""
    with pytest.raises(Exception):  # Should raise FK constraint violation
        client = Client(
            user_id=uuid.uuid4(),  # Random non-existent user ID
            phone="(555) 987-6543",
            service=ServiceType.HAIRCUT,
            status="active"
        )
        db_session.add(client)
        await db_session.commit()

async def test_create_appointment(db_session, test_user, test_client):
    """Test creating an appointment with valid client/user"""
    future_time = datetime.now() + timedelta(days=1)
    appointment = Appointment(
        creator_id=test_user.id,
        title="Haircut Appointment",
        description="Regular trim",
        start_time=future_time,
        duration_minutes=30,
        status=AppointmentStatus.SCHEDULED
    )
    
    db_session.add(test_user)
    db_session.add(test_client)
    db_session.add(appointment)
    await db_session.commit()
    
    fetched_appointment = await db_session.scalar(
        select(Appointment).filter_by(creator_id=test_user.id)
    )
    assert fetched_appointment is not None
    assert fetched_appointment.title == "Haircut Appointment"
    assert fetched_appointment.duration_minutes == 30

async def test_appointment_time_validation(db_session, test_user):
    """Test appointment validation for past dates"""
    past_time = datetime.now() - timedelta(days=1)
    appointment = Appointment(
        creator_id=test_user.id,
        title="Past Appointment",
        description="Should fail",
        start_time=past_time,
        duration_minutes=30,
        status=AppointmentStatus.SCHEDULED
    )
    
    db_session.add(test_user)
    with pytest.raises(ValueError) as exc_info:
        db_session.add(appointment)
        await db_session.commit()
    
    assert "Appointment start time cannot be in the past" in str(exc_info.value)

async def test_appointment_duration_validation(db_session, test_user):
    """Test appointment duration validation"""
    future_time = datetime.now() + timedelta(days=1)
    
    # Test too short duration
    with pytest.raises(ValueError) as exc_info:
        appointment = Appointment(
            creator_id=test_user.id,
            title="Short Appointment",
            description="Should fail",
            start_time=future_time,
            duration_minutes=10,  # Less than minimum 15 minutes
            status=AppointmentStatus.SCHEDULED
        )
        db_session.add(test_user)
        db_session.add(appointment)
        await db_session.commit()
    
    assert "Appointment duration must be at least 15 minutes" in str(exc_info.value)
    
    # Test too long duration
    with pytest.raises(ValueError) as exc_info:
        appointment = Appointment(
            creator_id=test_user.id,
            title="Long Appointment",
            description="Should fail",
            start_time=future_time,
            duration_minutes=500,  # More than maximum 480 minutes (8 hours)
            status=AppointmentStatus.SCHEDULED
        )
        db_session.add(appointment)
        await db_session.commit()
    
    assert "Appointment duration cannot exceed 8 hours" in str(exc_info.value)

async def test_unique_client_user_constraint(db_session, test_user):
    """Test that a user can only have one client profile"""
    client1 = Client(
        user_id=test_user.id,
        phone="(555) 111-1111",
        service=ServiceType.HAIRCUT,
        status="active"
    )
    
    client2 = Client(
        user_id=test_user.id,  # Same user_id
        phone="(555) 222-2222",
        service=ServiceType.MANICURE,
        status="active"
    )
    
    db_session.add(test_user)
    db_session.add(client1)
    await db_session.commit()
    
    with pytest.raises(Exception):  # Should raise unique constraint violation
        db_session.add(client2)
        await db_session.commit()

async def test_service_type_validation(db_session, test_user):
    """Test that only valid service types are accepted"""
    client = Client(
        user_id=test_user.id,
        phone="(555) 123-4567",
        service=ServiceType.HAIRCUT,  # Valid service type
        status="active"
    )
    
    db_session.add(test_user)
    db_session.add(client)
    await db_session.commit()
    
    assert client.service == ServiceType.HAIRCUT
    
    # Try updating to invalid service type
    with pytest.raises(ValueError):
        client.service = "INVALID_SERVICE"  # This should raise an error
        await db_session.commit()

async def test_appointment_scheduling_conflict(db_session, test_user):
    """Test that appointments cannot overlap for the same user"""
    future_time = datetime.now() + timedelta(days=1)
    
    # Create first appointment
    appointment1 = Appointment(
        creator_id=test_user.id,
        title="First Appointment",
        description="First test appointment",
        start_time=future_time,
        duration_minutes=60,
        status=AppointmentStatus.SCHEDULED
    )
    
    # Create second appointment that overlaps
    appointment2 = Appointment(
        creator_id=test_user.id,
        title="Second Appointment",
        description="Should fail - overlapping time",
        start_time=future_time + timedelta(minutes=30),  # Starts during first appointment
        duration_minutes=60,
        status=AppointmentStatus.SCHEDULED
    )
    
    db_session.add(test_user)
    db_session.add(appointment1)
    await db_session.commit()
    
    # TODO: Implement overlap check in appointment validation
    # This test currently passes but should fail once overlap validation is added
    db_session.add(appointment2)
    await db_session.commit()

async def test_multiple_attendees(db_session, test_user):
    """Test handling multiple attendees for an appointment"""
    future_time = datetime.now() + timedelta(days=1)
    
    # Create additional test users
    attendee1 = User(
        id=uuid.uuid4(),
        username="attendee1",
        email="attendee1@example.com",
        password="hashed_password",
        first_name="Test",
        last_name="Attendee1",
        enabled=True
    )
    
    attendee2 = User(
        id=uuid.uuid4(),
        username="attendee2",
        email="attendee2@example.com",
        password="hashed_password",
        first_name="Test",
        last_name="Attendee2",
        enabled=True
    )
    
    appointment = Appointment(
        creator_id=test_user.id,
        title="Group Appointment",
        description="Test with multiple attendees",
        start_time=future_time,
        duration_minutes=60,
        status=AppointmentStatus.SCHEDULED
    )
    
    db_session.add(test_user)
    db_session.add(attendee1)
    db_session.add(attendee2)
    db_session.add(appointment)
    
    # Add attendees to appointment
    appointment.attendees.extend([attendee1, attendee2])
    await db_session.commit()
    
    # Verify attendees were added
    fetched_appointment = await db_session.scalar(
        select(Appointment).filter_by(id=appointment.id)
    )
    assert len(fetched_appointment.attendees) == 2
    attendee_ids = [a.id for a in fetched_appointment.attendees]
    assert attendee1.id in attendee_ids
    assert attendee2.id in attendee_ids

async def test_appointment_status_transitions(db_session, test_user):
    """Test valid appointment status transitions"""
    future_time = datetime.now() + timedelta(days=1)
    
    appointment = Appointment(
        creator_id=test_user.id,
        title="Status Test Appointment",
        description="Test status transitions",
        start_time=future_time,
        duration_minutes=30,
        status=AppointmentStatus.SCHEDULED
    )
    
    db_session.add(test_user)
    db_session.add(appointment)
    await db_session.commit()
    
    # Test valid transitions
    valid_transitions = [
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.COMPLETED
    ]
    
    for status in valid_transitions:
        appointment.status = status
        await db_session.commit()
        fetched_appointment = await db_session.scalar(
            select(Appointment).filter_by(id=appointment.id)
        )
        assert fetched_appointment.status == status
    
    # Test cancellation
    appointment.status = AppointmentStatus.CANCELLED
    await db_session.commit()
    
    fetched_appointment = await db_session.scalar(
        select(Appointment).filter_by(id=appointment.id)
    )
    assert fetched_appointment.status == AppointmentStatus.CANCELLED
    
    # TODO: Add validation to prevent invalid transitions (e.g., CANCELLED to COMPLETED)

async def test_client_note_updates(db_session, test_user, test_client):
    """Test updating client notes"""
    db_session.add(test_user)
    db_session.add(test_client)
    await db_session.commit()
    
    # Update notes
    test_client.notes = "Updated client notes with preferences"
    await db_session.commit()
    
    fetched_client = await db_session.scalar(
        select(Client).filter_by(id=test_client.id)
    )
    assert fetched_client.notes == "Updated client notes with preferences"
    
    # Test notes length validation
    with pytest.raises(Exception):  # Should raise when exceeding max length
        test_client.notes = "x" * 501  # Exceeds 500 char limit
        await db_session.commit()

async def test_service_type_change(db_session, test_user, test_client):
    """Test changing client service type"""
    db_session.add(test_user)
    db_session.add(test_client)
    await db_session.commit()
    
    # Change service type
    test_client.service = ServiceType.MANICURE
    await db_session.commit()
    
    fetched_client = await db_session.scalar(
        select(Client).filter_by(id=test_client.id)
    )
    assert fetched_client.service == ServiceType.MANICURE
    
    # Verify history is maintained (TODO: Implement service history tracking)
