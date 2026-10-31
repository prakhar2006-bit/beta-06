"""Schemas for YojanaMitra AI Chatbot API."""
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field


class ChatProfileContext(BaseModel):
    """Citizen profile context provided by active session or authentication."""
    state: str | None = Field(default=None, description="State of residence (e.g. MP, UP, DL)")
    area_type: str | None = Field(default=None, description="rural or urban")
    age: int | None = Field(default=None, ge=0, le=125)
    gender: str | None = Field(default=None, description="female, male, transgender, other")
    occupation: str | None = Field(default=None, description="student, farmer, artisan, unemployed, etc.")
    annual_income: float | None = Field(default=None, ge=0)
    owns_agricultural_land: bool | None = None
    housing_type: str | None = Field(default=None, description="kutcha, pucca, homeless_rented")
    caste_category: str | None = Field(default=None, description="general, obc, sc, st")
    has_bpl_card: bool | None = None
    has_existing_lpg: bool | None = None
    pays_income_tax: bool | None = None
    education_level: str | None = None


class ChatMessageRequest(BaseModel):
    """Request payload to send a message to YojanaMitra AI Chatbot."""
    conversation_id: str | None = Field(default=None, description="Existing conversation UUID, or null for new")
    message: str = Field(..., min_length=1, max_length=2000, description="Citizen user prompt in Hindi or English")
    language: Literal["en", "hi"] | None = Field(default=None, description="Preferred response language")
    session_id: str | None = Field(default=None, description="Active screening session ID")
    profile: ChatProfileContext | None = Field(default=None, description="Ephemeral citizen profile context")


class SchemeCardData(BaseModel):
    """Structured scheme card rendered in chatbot UI."""
    scheme_id: str
    code: str
    name: str
    category: str
    level: str  # central or state
    benefits_summary: str
    official_url: str | None = None
    match_reason: str | None = None


class CriterionEvaluationItem(BaseModel):
    """Criterion check explanation."""
    criterion_name: str
    satisfied: bool
    explanation: str


class EligibilityCardData(BaseModel):
    """Deterministic eligibility check outcome card."""
    scheme_id: str
    scheme_name: str
    status: Literal["POTENTIALLY_ELIGIBLE", "NOT_ELIGIBLE", "NEEDS_VERIFICATION", "INSUFFICIENT_INFO"]
    confidence_score: float = Field(ge=0.0, le=1.0)
    summary_explanation: str
    criteria_breakdown: list[CriterionEvaluationItem] = []


class DocumentCheckItem(BaseModel):
    """Document item status for missing document assistance."""
    document_name: str
    is_required: bool = True
    status: Literal["AVAILABLE", "MISSING", "NEEDS_VERIFICATION", "NOT_APPLICABLE"]
    purpose: str | None = None
    where_to_obtain: str | None = None
    official_portal_url: str | None = None


class ApplicationGuidanceData(BaseModel):
    """Step-by-step application instructions."""
    scheme_id: str
    scheme_name: str
    mode: Literal["online", "offline", "both"]
    official_portal_url: str | None = None
    steps: list[str] = []
    documents_needed: list[str] = []
    caution_notes: list[str] = []


class IntentAnalysis(BaseModel):
    """Structured intent analysis conforming to Part 3 specifications."""
    intent: str
    language: str = "en"
    requires_profile: bool = False
    requires_scheme_search: bool = False
    requires_eligibility_check: bool = False
    requires_document_check: bool = False
    target_scheme_id: str | None = None
    target_category: str | None = None
    target_state: str | None = None


class ChatMessageResponse(BaseModel):
    """Response payload returned by YojanaMitra AI Chatbot."""
    conversation_id: str
    message: str
    language: Literal["en", "hi"]
    intent: str
    intent_details: IntentAnalysis | None = None
    schemes: list[SchemeCardData] = []
    eligibility: EligibilityCardData | None = None
    missing_documents: list[DocumentCheckItem] = []
    application_guidance: ApplicationGuidanceData | None = None
    suggested_followups: list[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatMessageRecord(BaseModel):
    """Single message item in conversation history."""
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    schemes: list[SchemeCardData] = []
    eligibility: EligibilityCardData | None = None
    missing_documents: list[DocumentCheckItem] = []
    application_guidance: ApplicationGuidanceData | None = None
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    """History of messages in a conversation."""
    conversation_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageRecord] = []


class SuggestedQuestionsResponse(BaseModel):
    """Suggested starter questions for the chatbot."""
    language: str
    questions: list[str]


class VoiceTTSRequest(BaseModel):
    """Payload to request audio synthesis for Shayak voice assistant."""
    text: str = Field(..., min_length=1, max_length=5000, description="Assistant text to synthesize")
    language: str | None = Field(default="en", description="Spoken language code (en or hi)")
    voice_id: str | None = Field(default=None, description="Optional override voice ID")


class VoiceStatusResponse(BaseModel):
    """Metadata about the voice assistant provider and configuration."""
    configured: bool
    provider: str
    voice_id: str
    model_id: str
    gender: str
    persona: str
    languages_supported: list[str]

