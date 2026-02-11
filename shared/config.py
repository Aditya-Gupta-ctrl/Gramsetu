"""
Shared configuration management for GramSetu
Loads environment variables and provides centralized config access
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    environment: str = "development"
    
    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # AWS
    aws_region: str = "ap-south-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # AWS Bedrock
    bedrock_agent_id: Optional[str] = None
    bedrock_agent_alias_id: Optional[str] = None
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    bedrock_llm_model: str = "anthropic.claude-3-haiku-20240307-v1:0"
    
    # Bhashini
    bhashini_api_key: Optional[str] = None
    bhashini_user_id: Optional[str] = None
    bhashini_pipeline_id: Optional[str] = None
    bhashini_base_url: str = "https://meity-auth.ulcacontrib.org"
    
    # Sarvam AI (Fallback)
    sarvam_api_key: Optional[str] = None
    
    # OpenAI (Fallback)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    
    # WhatsApp (Twilio)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_number: Optional[str] = None
    
    # WhatsApp (Meta)
    meta_whatsapp_token: Optional[str] = None
    meta_whatsapp_phone_id: Optional[str] = None
    meta_verify_token: Optional[str] = None
    
    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "gramsetu"
    postgres_user: str = "gramsetu_user"
    postgres_password: str = "gramsetu_pass"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # S3 Storage
    s3_bucket_name: Optional[str] = None
    s3_lifecycle_days: int = 1
    
    # Local Storage
    local_storage_path: str = "./storage"
    upload_max_size_mb: int = 10
    
    # Security
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:19006"
    
    # Privacy & Compliance
    data_retention_hours: int = 24
    audit_log_retention_days: int = 90
    aadhaar_mask_digits: int = 8
    pii_detection_threshold: float = 0.8
    
    # Browser Agent
    headless_browser: bool = True
    browser_timeout_ms: int = 30000
    screenshot_quality: int = 80
    session_timeout_minutes: int = 5
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 2
    captcha_max_attempts: int = 3
    captcha_confidence_threshold: float = 0.7
    
    # Voice Processing
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    audio_format: str = "wav"
    vad_threshold: float = 0.5
    vad_min_speech_duration_ms: int = 250
    enable_noise_suppression: bool = True
    
    # Mobile App
    mobile_api_base_url: str = "http://localhost:8000"
    mobile_websocket_url: str = "ws://localhost:8000/ws"
    sync_interval_minutes: int = 5
    max_offline_jobs: int = 50
    
    # Monitoring
    log_level: str = "INFO"
    log_format: str = "json"
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "development"
    
    # Feature Flags
    enable_voice_biometrics: bool = False
    enable_video_kyc: bool = False
    enable_mock_portals: bool = True
    enable_wizard_of_oz: bool = False
    
    # Demo Mode
    demo_mode: bool = True
    demo_vle_id: str = "VLE001"
    demo_citizen_phone: str = "+919876543210"
    
    @property
    def database_url(self) -> str:
        """PostgreSQL connection URL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def async_database_url(self) -> str:
        """Async PostgreSQL connection URL"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
