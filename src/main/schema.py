from pydantic import BaseModel, EmailStr, Field, field_validator, validator
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"

class ServiceType(str, Enum):
    """Matches the ServiceTypeEnum in the models"""
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

class ClientCategory(str, Enum):
    NEW = "NEW"
    REGULAR = "REGULAR"
    VIP = "VIP"
    PREMIUM = "PREMIUM"

class ClientStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"

class Client(BaseModel):
    id: str
    user_id: str
    phone: str = Field(..., max_length=20, description="Client phone number")
    service: ServiceType = Field(..., description="Type of service requested")
    status: ClientStatus = Field(..., description="Client status")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes about the client")
    category: ClientCategory = Field(..., description="Client category based on spending/visits")
    loyalty_points: int = Field(default=0, description="Accumulated loyalty points")
    total_spent: float = Field(default=0.0, description="Total amount spent by client")
    visit_count: int = Field(default=0, description="Number of completed visits")
    last_visit: Optional[datetime] = Field(None, description="Date of last visit")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "LWx_ppZOLN2cQZzCWM3pq",
                "user_id": "KVc_mnPOLM1bRYwBVN2op",
                "phone": "(555) 123-4567",
                "service": "Hair Cut",
                "status": "ACTIVE",
                "notes": "Prefers afternoon appointments",
                "category": "REGULAR",
                "loyalty_points": 50,
                "total_spent": 250.0,
                "visit_count": 5,
                "last_visit": "2025-02-20T14:00:00Z"
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
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    enabled: bool

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "LWx_ppZOLN2cQZzCWM3pq",
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
    service_type: ServiceType = Field(..., description="Type of service")

    @field_validator("start_time")
    def validate_start_time(cls, v):
        """Enhanced start time validation"""
        now = datetime.now()
        min_notice = timedelta(hours=2)
        if v <= now + min_notice:
            raise ValueError("Appointments must be scheduled at least 2 hours in advance")
        
        # Business hours validation
        if v.hour < 9 or v.hour >= 19:
            raise ValueError("Appointments must be between 9 AM and 7 PM")
            
        # Weekend validation
        if v.weekday() >= 5:
            raise ValueError("Appointments cannot be scheduled on weekends")
        
        return v

    @field_validator("duration_minutes")
    def validate_duration(cls, v, values):
        """Validate duration based on service type"""
        if 'service_type' in values.data:
            service_type = values.data['service_type']
            min_duration = getattr(ServiceType, 'get_duration_minutes')(service_type)
            if v < min_duration:
                raise ValueError(f"Duration cannot be less than {min_duration} minutes for {service_type.value}")
        return v

class AppointmentCreate(AppointmentBase):
    attendee_ids: List[str] = Field(..., min_length=1, description="List of attendee user IDs")

class AppointmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100, description="Update appointment title")
    description: Optional[str] = Field(None, max_length=500, description="Update appointment description")
    start_time: Optional[datetime] = Field(None, description="Update start time")
    duration_minutes: Optional[int] = Field(None, ge=15, le=480, description="Update duration in minutes")
    status: Optional[AppointmentStatus] = Field(None, description="Update appointment status")

class AppointmentInDB(AppointmentBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    creator_id: str
    status: AppointmentStatus
    attendees: List[UserInDB]
    estimated_cost: float = Field(..., description="Estimated cost based on service type and duration")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "VWx_ppZOLN2cQZzCWM3pq",
                "title": "Haircut Appointment",
                "description": "Regular trim",
                "start_time": "2025-02-21T14:00:00Z",
                "duration_minutes": 30,
                "service_type": "Hair Cut",
                "created_at": "2025-02-20T12:00:00Z",
                "updated_at": "2025-02-20T12:00:00Z",
                "creator_id": "LWx_ppZOLN2cQZzCWM3pq",
                "status": "SCHEDULED",
                "estimated_cost": 30.0,
                "attendees": [
                    {
                        "id": "LWx_ppZOLN2cQZzCWM3pq",
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

class ServiceHistoryEntry(BaseModel):
    id: str
    client_id: str
    service_type: ServiceType
    provider_name: str
    date_of_service: datetime
    notes: Optional[str]
    service_cost: float
    loyalty_points_earned: int
    points_redeemed: int
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5, description="Service satisfaction rating")
    feedback: Optional[str]
    service_duration: int

class ServicePackage(BaseModel):
    id: str
    client_id: str
    service_type: ServiceType
    total_sessions: int = Field(..., ge=1, le=52, description="Total number of sessions in package")
    sessions_remaining: int
    purchase_date: datetime
    expiry_date: datetime
    package_cost: float
    minimum_interval: int = Field(default=1, description="Minimum days between sessions")
    last_session_date: Optional[datetime]
    average_satisfaction: Optional[float]

    @validator("expiry_date")
    def validate_expiry(cls, v, values):
        if "purchase_date" in values and v <= values["purchase_date"] + timedelta(days=30):
            raise ValueError("Package expiry must be at least 30 days after purchase")
        return v

    @validator("package_cost")
    def validate_cost(cls, v, values):
        if "service_type" in values and "total_sessions" in values:
            min_cost = getattr(ServiceType, 'get_base_cost')(values["service_type"]) * values["total_sessions"] * 0.8
            if v < min_cost:
                raise ValueError("Package cost is below minimum allowed value")
        return v
