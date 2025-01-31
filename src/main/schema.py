# src/main/schema.py
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

class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)  # Ensures password is at least 8 chars

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enabled: Optional[bool] = None

class UserInDB(UserBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    enabled: bool

    model_config = {
        "from_attributes": True  # New configuration style in Pydantic v2
    }

class AppointmentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_time: datetime
    duration_minutes: int = Field(..., ge=15, le=480)  # Min 15 minutes, max 8 hours
    
    @field_validator('start_time')
    def start_time_must_be_future(cls, v):
        if v <= datetime.now():
            raise ValueError('Start time must be in the future')
        return v

class AppointmentCreate(AppointmentBase):
    attendee_ids: List[UUID] = Field(..., min_length=1)

class AppointmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    status: Optional[AppointmentStatus] = None

class AppointmentInDB(AppointmentBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    creator_id: UUID
    status: AppointmentStatus
    attendees: List[UserInDB]

    model_config = {
        "from_attributes": True  # New configuration style in Pydantic v2
    }

    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(minutes=self.duration_minutes)
