# Immediate TODOs

## High Priority

### 1. Appointment Overlap Prevention
```python
def validate_appointment_overlap(mapper, connection, target):
    """
    Check if appointment overlaps with existing appointments
    for creator or attendees
    """
    # Implementation steps:
    # 1. Query existing appointments for same time period
    # 2. Check creator availability
    # 3. Check all attendees availability
    # 4. Raise ValueError if overlap found
```

### 2. Status Transition Validation
```python
def validate_status_transition(old_status, new_status):
    """
    Valid transitions:
    SCHEDULED -> CONFIRMED -> COMPLETED
    SCHEDULED -> CANCELLED
    CONFIRMED -> CANCELLED
    """
    valid_transitions = {
        AppointmentStatus.SCHEDULED: [AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED],
        AppointmentStatus.CONFIRMED: [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED],
        AppointmentStatus.CANCELLED: [],
        AppointmentStatus.COMPLETED: []
    }
```

### 3. Service History Tracking
```python
class ServiceHistory(Base):
    """
    Track service history for clients
    - Previous services
    - Service dates
    - Providers
    - Outcomes
    """
    __tablename__ = "service_history"
    id = Column(UUID, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    service_type = Column(SQLEnum(ServiceType))
    provider_id = Column(UUID, ForeignKey('users.id'))
    date_of_service = Column(DateTime)
    notes = Column(String)
```

## Medium Priority

### 4. Client Categories
- Implement client categorization
- Add loyalty program tracking
- Service package management

### 5. Enhanced Authorization Tests
- Test role-based access
- Provider specialty restrictions
- Admin override capabilities

### 6. Appointment Templates
- Create standard appointment durations
- Service type default settings
- Provider availability templates

## Low Priority

### 7. Reporting Capabilities
- Service history analytics
- Provider utilization
- Client retention metrics

### 8. Client Communication
- Appointment reminders
- Follow-up tracking
- Feedback collection

## Notes for Implementation

1. Overlap Prevention:
   - Consider timezone handling
   - Buffer times between appointments
   - Handle recurring appointments

2. Status Transitions:
   - Log all status changes
   - Notify relevant parties
   - Handle edge cases (e.g., no-shows)

3. Service History:
   - Keep immutable record
   - Link to appointments
   - Support reporting needs
