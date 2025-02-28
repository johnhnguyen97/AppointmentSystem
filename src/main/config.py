from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any, cast
from enum import StrEnum
import os
import json
from functools import lru_cache
import logging

# Import Bitwarden utility functions
try:
    from src.utils.bitwarden import get_bitwarden_credentials, get_service_config, get_database_credentials
    BITWARDEN_AVAILABLE = True
except ImportError:
    BITWARDEN_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define service types as an enum for type safety
class ServiceType(StrEnum):
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

class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

    # Database and authentication settings
    DATABASE_URL: str
    TEST_DATABASE_URL: Optional[str] = None
    PASSWORD_MIN_LENGTH: int = 8
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Business hours configuration
    BUSINESS_HOUR_START: int = 9  # 9 AM
    BUSINESS_HOUR_END: int = 19   # 7 PM
    ALLOW_WEEKEND_APPOINTMENTS: bool = False
    
    # Appointment configuration
    APPOINTMENT_MIN_NOTICE_HOURS: int = 2
    APPOINTMENT_MIN_DURATION_MINUTES: int = 15
    APPOINTMENT_MAX_DURATION_MINUTES: int = 480  # 8 hours
    
    # Service package configuration
    PACKAGE_MIN_DURATION_DAYS: int = 30
    PACKAGE_MAX_SESSIONS: int = 52
    PACKAGE_DISCOUNT_PERCENTAGE: float = 20.0  # 20% discount
    
    # Service type durations (in minutes)
    SERVICE_DURATIONS: Dict[str, int] = {}
    
    # Service type base costs
    SERVICE_BASE_COSTS: Dict[str, float] = {}
    
    # Service type loyalty points
    SERVICE_LOYALTY_POINTS: Dict[str, int] = {}
    
    # Client category thresholds
    CLIENT_PREMIUM_SPEND: float = 1000.0
    CLIENT_PREMIUM_VISITS: int = 20
    CLIENT_VIP_SPEND: float = 500.0
    CLIENT_VIP_VISITS: int = 10
    CLIENT_REGULAR_VISITS: int = 3
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_from_bitwarden()
        self._set_default_service_values()
    
    def _load_from_bitwarden(self):
        """Load sensitive configuration from Bitwarden"""
        if not BITWARDEN_AVAILABLE:
            logger.warning("Bitwarden utilities not available, using environment variables only")
            return
        
        try:
            # Try to load app configuration from Bitwarden
            app_config = get_service_config("Appointment System")
            
            # Update settings from Bitwarden if available
            if app_config:
                # Update business hours
                if 'business_hours' in app_config:
                    hours = app_config['business_hours']
                    if isinstance(hours, dict):
                        self.BUSINESS_HOUR_START = int(hours.get('start', self.BUSINESS_HOUR_START))
                        self.BUSINESS_HOUR_END = int(hours.get('end', self.BUSINESS_HOUR_END))
                
                # Update appointment settings
                if 'appointment' in app_config:
                    appt = app_config['appointment']
                    if isinstance(appt, dict):
                        self.APPOINTMENT_MIN_NOTICE_HOURS = int(appt.get('min_notice_hours', self.APPOINTMENT_MIN_NOTICE_HOURS))
                        self.APPOINTMENT_MIN_DURATION_MINUTES = int(appt.get('min_duration', self.APPOINTMENT_MIN_DURATION_MINUTES))
                        self.APPOINTMENT_MAX_DURATION_MINUTES = int(appt.get('max_duration', self.APPOINTMENT_MAX_DURATION_MINUTES))
                
                # Update service package settings
                if 'service_package' in app_config:
                    pkg = app_config['service_package']
                    if isinstance(pkg, dict):
                        self.PACKAGE_MIN_DURATION_DAYS = int(pkg.get('min_duration_days', self.PACKAGE_MIN_DURATION_DAYS))
                        self.PACKAGE_MAX_SESSIONS = int(pkg.get('max_sessions', self.PACKAGE_MAX_SESSIONS))
                        self.PACKAGE_DISCOUNT_PERCENTAGE = float(pkg.get('discount_percentage', self.PACKAGE_DISCOUNT_PERCENTAGE))
                
                # Update client category thresholds
                if 'client_categories' in app_config:
                    cat = app_config['client_categories']
                    if isinstance(cat, dict):
                        self.CLIENT_PREMIUM_SPEND = float(cat.get('premium_spend', self.CLIENT_PREMIUM_SPEND))
                        self.CLIENT_PREMIUM_VISITS = int(cat.get('premium_visits', self.CLIENT_PREMIUM_VISITS))
                        self.CLIENT_VIP_SPEND = float(cat.get('vip_spend', self.CLIENT_VIP_SPEND))
                        self.CLIENT_VIP_VISITS = int(cat.get('vip_visits', self.CLIENT_VIP_VISITS))
                        self.CLIENT_REGULAR_VISITS = int(cat.get('regular_visits', self.CLIENT_REGULAR_VISITS))
                
                # Load service type configurations
                if 'service_types' in app_config:
                    service_types = app_config['service_types']
                    if isinstance(service_types, dict):
                        # Load durations
                        if 'durations' in service_types:
                            for service, duration in service_types['durations'].items():
                                self.SERVICE_DURATIONS[service] = int(duration)
                        
                        # Load costs
                        if 'costs' in service_types:
                            for service, cost in service_types['costs'].items():
                                self.SERVICE_BASE_COSTS[service] = float(cost)
                        
                        # Load loyalty points
                        if 'loyalty_points' in service_types:
                            for service, points in service_types['loyalty_points'].items():
                                self.SERVICE_LOYALTY_POINTS[service] = int(points)
            
            # Try to load database configuration from Bitwarden
            db_creds = get_database_credentials()
            if db_creds and 'username' in db_creds and 'password' in db_creds:
                # Construct database URL from credentials
                host = db_creds.get('host', 'localhost')
                port = db_creds.get('port', '5432')
                database = db_creds.get('database', 'appointment_system')
                username = db_creds['username']
                password = db_creds['password']
                
                # Only override DATABASE_URL if not already set in environment
                if not os.environ.get('DATABASE_URL'):
                    self.DATABASE_URL = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
                    logger.info("Database URL loaded from Bitwarden")
            
        except Exception as e:
            logger.warning(f"Failed to load configuration from Bitwarden: {str(e)}")
            logger.warning("Using environment variables and defaults instead")
    
    def _set_default_service_values(self):
        """Set default values for service configurations if not loaded from Bitwarden"""
        # Default service durations if not set
        if not self.SERVICE_DURATIONS:
            self.SERVICE_DURATIONS = {
                ServiceType.HAIRCUT: 30,
                ServiceType.MANICURE: 45,
                ServiceType.PEDICURE: 60,
                ServiceType.FACIAL: 60,
                ServiceType.MASSAGE: 60,
                ServiceType.HAIRCOLOR: 120,
                ServiceType.HAIRSTYLE: 45,
                ServiceType.MAKEUP: 60,
                ServiceType.WAXING: 30,
                ServiceType.OTHER: 30
            }
        
        # Default service costs if not set
        if not self.SERVICE_BASE_COSTS:
            self.SERVICE_BASE_COSTS = {
                ServiceType.HAIRCUT: 30.0,
                ServiceType.MANICURE: 25.0,
                ServiceType.PEDICURE: 35.0,
                ServiceType.FACIAL: 65.0,
                ServiceType.MASSAGE: 75.0,
                ServiceType.HAIRCOLOR: 100.0,
                ServiceType.HAIRSTYLE: 45.0,
                ServiceType.MAKEUP: 55.0,
                ServiceType.WAXING: 30.0,
                ServiceType.OTHER: 40.0
            }
        
        # Default loyalty points if not set
        if not self.SERVICE_LOYALTY_POINTS:
            self.SERVICE_LOYALTY_POINTS = {
                ServiceType.HAIRCUT: 10,
                ServiceType.MANICURE: 8,
                ServiceType.PEDICURE: 12,
                ServiceType.FACIAL: 15,
                ServiceType.MASSAGE: 20,
                ServiceType.HAIRCOLOR: 25,
                ServiceType.HAIRSTYLE: 12,
                ServiceType.MAKEUP: 15,
                ServiceType.WAXING: 10,
                ServiceType.OTHER: 10
            }

    def get_test_db_url(self) -> str:
        """Get test database URL with correct format"""
        base_url = self.TEST_DATABASE_URL or self.DATABASE_URL

        if not base_url:
            raise ValueError("DATABASE_URL must be set in the environment or .env file")

        # Ensure correct prefix
        if base_url.startswith('postgres://'):
            base_url = base_url.replace('postgres://', 'postgresql+asyncpg://', 1)

        # Replace default database name with test database if no TEST_DATABASE_URL is provided
        if self.TEST_DATABASE_URL is None and 'defaultdb' in base_url:
            base_url = base_url.replace('defaultdb', 'testdb')

        # Remove SSL parameters from the URL (asyncpg uses an SSL context)
        base_url = base_url.split('?')[0]

        return base_url  # Do NOT append `?sslmode=require`

settings = Settings()
