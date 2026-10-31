from datetime import date
from decimal import Decimal
from typing import Generic, Literal, TypeVar

from app.schemas.eligibility import ConditionResult, EvaluationResponse, SourceReference, StrictModel
from app.schemas.questionnaire import MissingInformation, QuestionnaireState
from app.schemas.schemes import Language


class ResultRequest(StrictModel):
    state: QuestionnaireState


class DisplayText(StrictModel):
    text: str | None = None
    requested_language: Language
    content_language: Language | None = None
    translation_fallback: bool = False
    review_status: Literal['reviewed','system','unavailable'] = 'unavailable'
    origin: Literal['official','human','machine','source_text','system','unavailable'] = 'unavailable'
    is_official_translation: bool = False
    source_ids: tuple[str,...] = ()


class BenefitResult(StrictModel):
    item_id: str
    item_key: str
    description: DisplayText
    amount_min: Decimal | None
    amount_max: Decimal | None
    currency: str | None
    frequency: str | None
    source_ids: tuple[str,...]
    last_verified_date: date


class DocumentResult(StrictModel):
    item_id: str
    item_key: str
    title: DisplayText
    requirement: str
    requirement_explanation: DisplayText
    condition: DisplayText
    source_ids: tuple[str,...]
    last_verified_date: date


class ApplicationResult(StrictModel):
    item_id: str
    item_key: str
    mode: str
    steps: tuple[DisplayText,...]
    official_application_url: str | None
    url_status: Literal['available','unavailable']
    url_message: DisplayText
    source_ids: tuple[str,...]
    last_verified_date: date


class ApplicationURL(StrictModel):
    route_id: str
    url: str
    source_ids: tuple[str,...]


T=TypeVar('T')


class GuidanceSection(StrictModel,Generic[T]):
    status: Literal['available','partial','unavailable']
    reason_code: str | None
    message: DisplayText
    items: tuple[T,...] = ()


class ResultResponse(StrictModel):
    schema_version: Literal['1.0']='1.0'
    scheme_id: str
    language: Language
    scheme_name: DisplayText
    eligibility_status: Literal['ELIGIBLE','INELIGIBLE','NEEDS_VERIFICATION']
    explanation: DisplayText
    assessment_notice: DisplayText
    conditions_satisfied: tuple[ConditionResult,...]
    conditions_not_satisfied: tuple[ConditionResult,...]
    missing_information: MissingInformation
    benefits: GuidanceSection[BenefitResult]
    required_documents: GuidanceSection[DocumentResult]
    application_guidance: GuidanceSection[ApplicationResult]
    official_application_urls: GuidanceSection[ApplicationURL]
    sources: tuple[SourceReference,...]
    last_verification_date: date | None
    evaluation: EvaluationResponse
