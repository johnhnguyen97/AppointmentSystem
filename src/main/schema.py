from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional, List
from enum import Enum


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ServiceType(str, Enum):
    """Matches the ServiceTypeEnum in the Strawberry schema and SQLAlchemy models"""
    HAIRCUT = "Hair Cut"
    MANICURE = "Manicure"
    PEDICURE = "Pedicure"
    FACIAL = "Facial"
    MASSAGE = "Massage"
    HAIRCOLOR = "Hair Color"
    HAIRSTYLE = "Hair Style"
    MAKEUP = "Makeup"
    WAXING = "Waxing"
    OTHER = "Other"


class Client(BaseModel):
    id: int
    user_id: UUID
    phone: str = Field(..., max_length=20, description="Client phone number")
    service: ServiceType = Field(..., description="Type of service requested")
    status: str = Field(..., max_length=20, description="Client status (e.g., active, inactive)")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes about the client")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "phone": "(555) 123-4567",
                "service": "Hair Cut",
                "status": "active",
                "notes": "Prefers afternoon appointments"
            }
        }
    }


class UserBase(BaseModel):
    username: str = Field(..., max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., max_length=50, description="User's first name")
    last_name: str = Field(..., max_length=50, description="User's last name")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50, description="Update username")
    email: Optional[EmailStr] = Field(None, description="Update email address")
    first_name: Optional[str] = Field(None, max_length=50, description="Update first name")
    last_name: Optional[str] = Field(None, max_length=50, description="Update last name")
    enabled: Optional[bool] = Field(None, description="Enable/disable user account")


class UserInDB(UserBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    enabled: bool

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "created_at": "2025-02-20T12:00:00Z",
                "updated_at": "2025-02-20T12:00:00Z",
                "enabled": True
            }
        }
    }


class AppointmentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Appointment title")
    description: Optional[str] = Field(None, max_length=500, description="Appointment description")
    start_time: datetime = Field(..., description="Start time of the appointment")
    duration_minutes: int = Field(..., ge=15, le=480, description="Duration in minutes (15 min to 8 hours)")

    @field_validator("start_time")
    def start_time_must_be_future(cls, v):
        """Ensures the start time is in the future"""
        if v <= datetime.now():
            raise ValueError("Start time must be in the future")
        return v


class AppointmentCreate(AppointmentBase):
    attendee_ids: List[UUID] = Field(..., min_length=1, description="List of attendee user IDs")


class AppointmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100, description="Update appointment title")
    description: Optional[str] = Field(None, max_length=500, description="Update appointment description")
    start_time: Optional[datetime] = Field(None, description="Update start time")
    duration_minutes: Optional[int] = Field(None, ge=15, le=480, description="Update duration in minutes")
    status: Optional[AppointmentStatus] = Field(None, description="Update appointment status")


class AppointmentInDB(AppointmentBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    creator_id: UUID
    status: AppointmentStatus
    attendees: List[UserInDB]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "456e7890-e89b-12d3-a456-426614174000",
                "title": "Haircut Appointment",
                "description": "Regular trim",
                "start_time": "2025-02-21T14:00:00Z",
                "duration_minutes": 30,
                "created_at": "2025-02-20T12:00:00Z",
                "updated_at": "2025-02-20T12:00:00Z",
                "creator_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "scheduled",
                "attendees": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "username": "johndoe",
                        "email": "john.doe@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "created_at": "2025-02-20T12:00:00Z",
                        "updated_at": "2025-02-20T12:00:00Z",
                        "enabled": True
                    }
                ]
            }
        }
    }

    @property
    def end_time(self) -> datetime:
        """Calculates the end time based on start time and duration"""
        return self.start_time + timedelta(minutes=self.duration_minutes)