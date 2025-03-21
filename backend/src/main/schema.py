from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = 'SCHEDULED'
    CONFIRMED = 'CONFIRMED'
    CANCELLED = 'CANCELLED'
    COMPLETED = 'COMPLETED'
    DECLINED = 'DECLINED'
