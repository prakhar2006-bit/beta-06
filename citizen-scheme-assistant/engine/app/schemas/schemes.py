from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

Language = Literal["en", "hi"]
Level = Literal["central", "state", "ut", "local"]


class SchemeSummary(BaseModel):
    id: str
    database_id: UUID
    version_id: UUID
    version_number: int
    requested_language: Language
    language: Language | None
    translation_fallback: bool
    name: str | None
    description: str | None
    level: Level
    lifecycle_status: str
    organization_code: str
    organization_name: str
    organization_url: str
    last_checked_date: date | None
    effective_from: date | None
    effective_to: date | None
    published_at: datetime


class SchemeList(BaseModel):
    items: list[SchemeSummary]
    total: int
    limit: int
    offset: int
    has_more: bool


class Benefit(BaseModel):
    id: UUID
    item_key: str
    benefit_type: str
    description: str
    amount_min: Decimal | None
    amount_max: Decimal | None
    currency: str | None
    frequency: str | None
    evidence_id: UUID
    content_language: None = None


class ApplicationRoute(BaseModel):
    id: UUID
    item_key: str
    mode: str
    original_url: str | None
    instructions: str
    last_checked_date: date
    evidence_id: UUID
    content_language: None = None


class RequiredDocument(BaseModel):
    id: UUID
    item_key: str
    document_type: str
    requirement: str
    condition_text: str | None
    evidence_id: UUID
    content_language: None = None


class Rule(BaseModel):
    id: UUID
    rule_key: str
    parent_id: UUID | None
    node_type: str
    attribute: str | None
    operator: str | None
    expected_value: Any
    unit: str | None
    time_basis: str | None
    confidence: str
    uncertainty_reason: str | None


class RuleEvidence(BaseModel):
    rule_id: UUID
    evidence_id: UUID


class Evidence(BaseModel):
    id: UUID
    locator: str
    supporting_text: str
    last_checked_date: date
    content_sha256: str
    fetched_at: datetime
    source_updated_at: datetime | None
    original_url: str
    source_title: str
    license_url: str | None


class Jurisdiction(BaseModel):
    jurisdiction_id: UUID
    code: str
    name: str
    kind: str


class SchemeDetail(SchemeSummary):
    eligibility_text: str | None
    translation_evidence_id: UUID | None
    benefits: list[Benefit]
    application_routes: list[ApplicationRoute]
    required_documents: list[RequiredDocument]
    eligibility_rules: list[Rule]
    rule_evidence: list[RuleEvidence]
    sources: list[Evidence]
    jurisdictions: list[Jurisdiction]
    unlocalized_fields: list[str] = Field(default_factory=lambda: [
        "organization_name", "benefits", "application_routes", "required_documents",
        "eligibility_rules", "sources", "jurisdictions",
    ])


class LanguageItem(BaseModel):
    code: Language
    name: str


class Languages(BaseModel):
    items: list[LanguageItem]


class DBHealth(BaseModel):
    status: Literal["ok"] = "ok"


class ErrorBody(BaseModel):
    code: str
    message: str
    fields: list[str] | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody
