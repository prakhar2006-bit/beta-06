"""Bounded client-held state. It contains answers, never trusted policy or decisions."""
from typing import Annotated, Literal

from pydantic import Field, model_validator

from app.schemas.eligibility import (EvaluationRequest, EvaluationResponse, Key,
    Question, Scalar, SchemeID, StrictModel)
from app.schemas.schemes import Language


class StartRequest(StrictModel):
    scheme_id: SchemeID
    language: Language = 'en'


class QuestionnaireState(EvaluationRequest):
    state_version: Literal['1.0'] = '1.0'
    policy_fingerprint: Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')] | None = None
    skipped: Annotated[tuple[Key, ...], Field(max_length=64)] = ()

    @model_validator(mode='after')
    def dispositions(self):
        if len(set(self.skipped)) != len(self.skipped) or set(self.skipped) & set(self.answers):
            raise ValueError('A field cannot be both answered and skipped, or skipped twice')
        if len(set(self.skipped) | set(self.answers)) > 64:
            raise ValueError('Too many answer dispositions')
        return self


class NextRequest(StrictModel):
    state: QuestionnaireState


class AnswerRequest(NextRequest):
    question_id: Key
    action: Literal['answer', 'skip', 'clear'] = 'answer'
    value: Scalar | None = None

    @model_validator(mode='after')
    def operation(self):
        if self.action == 'answer':
            if 'value' not in self.model_fields_set:
                raise ValueError('An answer requires an explicit value; null means unknown')
            EvaluationRequest(scheme_id=self.state.scheme_id, answers={self.question_id: self.value})
        elif 'value' in self.model_fields_set:
            raise ValueError('Skip/clear must not include a value')
        return self


class CurrentQuestion(Question):
    question_id: str
    answer_type: Literal['integer', 'decimal', 'number', 'category', 'boolean']
    allowed_values: tuple[Scalar, ...] = ()
    source_ids: tuple[str, ...] = ()


class Progress(StrictModel):
    answered: int
    unknown: int
    skipped: int
    remaining: int


class MissingInformation(StrictModel):
    unanswered_fields: tuple[str, ...] = ()
    unknown_fields: tuple[str, ...] = ()
    skipped_fields: tuple[str, ...] = ()
    unreviewed_question_fields: tuple[str, ...] = ()
    review_blockers: tuple[str, ...] = ()


class QuestionnaireResponse(StrictModel):
    schema_version: Literal['1.0'] = '1.0'
    state: QuestionnaireState
    current_question: CurrentQuestion | None
    completed: bool
    completion_reason: Literal['QUESTIONS_REMAIN', 'DECISION_REACHED', 'VERIFICATION_REQUIRED']
    progress: Progress
    missing_information: MissingInformation
    evaluation: EvaluationResponse
