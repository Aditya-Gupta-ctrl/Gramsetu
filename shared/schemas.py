"""
Shared Pydantic schemas for inter-service communication
Ensures type safety and validation across all 4 components
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


# ============================================
# Enums
# ============================================

class JobStatus(str, Enum):
    """Job processing status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    SOLVING_CAPTCHA = "solving_captcha"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SchemeType(str, Enum):
    """Government scheme types"""
    PM_KISAN = "pm_kisan"
    E_SHRAM = "e_shram"
    EPFO = "epfo"
    WIDOW_PENSION = "widow_pension"
    RATION_CARD = "ration_card"
    AYUSHMAN_BHARAT = "ayushman_bharat"


class IntentType(str, Enum):
    """User intent classification"""
    CHECK_STATUS = "check_status"
    APPLY_NEW = "apply_new"
    UPDATE_DETAILS = "update_details"
    DOWNLOAD_CERTIFICATE = "download_certificate"
    REGISTER = "register"


class DocumentType(str, Enum):
    """Document types for OCR"""
    AADHAAR = "aadhaar"
    PAN = "pan"
    RATION_CARD = "ration_card"
    LAND_DEED = "land_deed"
    CASTE_CERTIFICATE = "caste_certificate"
    INCOME_CERTIFICATE = "income_certificate"
    BANK_PASSBOOK = "bank_passbook"


# ============================================
# Voice Interface Schemas (Member 1)
# ============================================

class VoiceInput(BaseModel):
    """Input for voice processing"""
    audio_base64: str = Field(..., description="Base64 encoded audio")
    vle_id: str = Field(..., description="VLE identifier")
    session_id: Optional[str] = Field(None, description="Session for context")
    language_hint: Optional[str] = Field("hi", description="Expected language code")


class VoiceOutput(BaseModel):
    """Output from voice processing"""
    transcript: str = Field(..., description="Transcribed text")
    intent: IntentType = Field(..., description="Classified intent")
    scheme: Optional[SchemeType] = Field(None, description="Identified scheme")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    missing_info: List[str] = Field(default_factory=list, description="Required missing fields")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


# ============================================
# Document Processing Schemas (Member 3)
# ============================================

class DocumentInput(BaseModel):
    """Input for document processing"""
    image_base64: str = Field(..., description="Base64 encoded image")
    document_type: DocumentType = Field(..., description="Type of document")
    vle_id: str = Field(..., description="VLE identifier")
    apply_masking: bool = Field(True, description="Apply PII masking")


class DocumentOutput(BaseModel):
    """Output from document processing"""
    document_type: DocumentType
    extracted_data: Dict[str, Any] = Field(default_factory=dict, description="Extracted fields")
    masked_image_url: Optional[str] = Field(None, description="S3 URL of masked image")
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Field confidence")
    is_authentic: bool = Field(True, description="Passed authenticity checks")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


# ============================================
# Browser Agent Schemas (Member 2)
# ============================================

class AgentTask(BaseModel):
    """Task for browser agent"""
    task_id: str = Field(..., description="Unique task identifier")
    scheme: SchemeType = Field(..., description="Target portal")
    action: IntentType = Field(..., description="Action to perform")
    form_data: Dict[str, Any] = Field(default_factory=dict, description="Form field values")
    session_state: Optional[Dict[str, Any]] = Field(None, description="Cached session state")


class AgentResult(BaseModel):
    """Result from browser agent"""
    task_id: str
    status: JobStatus
    result_data: Optional[Dict[str, Any]] = Field(None, description="Scraped/submitted data")
    screenshot_url: Optional[str] = Field(None, description="Final screenshot")
    acknowledgement_number: Optional[str] = Field(None, description="Application reference")
    error_message: Optional[str] = Field(None, description="Error if failed")
    steps_completed: List[str] = Field(default_factory=list, description="Execution log")


# ============================================
# Orchestrator Schemas (Member 4)
# ============================================

class JobRequest(BaseModel):
    """Complete job request from VLE"""
    vle_id: str = Field(..., description="VLE identifier")
    citizen_name: str = Field(..., description="Beneficiary name")
    citizen_phone: str = Field(..., description="Beneficiary phone")
    voice_input: Optional[VoiceInput] = None
    documents: List[DocumentInput] = Field(default_factory=list)
    consent_recorded: bool = Field(False, description="Verbal consent obtained")


class JobResponse(BaseModel):
    """Job creation response"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus
    estimated_completion_seconds: int = Field(60, description="Estimated time")
    message: str = Field(..., description="User-friendly status message")


class JobStatusResponse(BaseModel):
    """Job status query response"""
    job_id: str
    status: JobStatus
    progress_percentage: int = Field(0, ge=0, le=100)
    current_step: str = Field("", description="Human-readable current step")
    result: Optional[AgentResult] = None
    created_at: datetime
    updated_at: datetime


# ============================================
# WhatsApp Notification Schema
# ============================================

class WhatsAppNotification(BaseModel):
    """WhatsApp message to citizen"""
    recipient_phone: str = Field(..., description="Citizen phone number")
    message_text: str = Field(..., description="Message content")
    image_url: Optional[str] = Field(None, description="Attachment URL")
    job_id: str = Field(..., description="Related job ID")


# ============================================
# Consent & Audit Schema
# ============================================

class ConsentRecord(BaseModel):
    """DPDP Act consent artifact"""
    citizen_phone: str
    vle_id: str
    consent_text: str = Field(..., description="What user consented to")
    audio_hash: str = Field(..., description="SHA256 of consent audio")
    timestamp: datetime
    ip_address: Optional[str] = None
    scheme: SchemeType


# ============================================
# Error Response Schema
# ============================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error_code: str = Field(..., description="Machine-readable error code")
    error_message: str = Field(..., description="Human-readable message")
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
