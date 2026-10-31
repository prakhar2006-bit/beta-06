"""Strict Phase 4A DTOs and trusted-server rule definitions; no citizen persistence."""
from datetime import date
from math import isfinite
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator, model_validator

from app.schemas.schemes import Language

Key = Annotated[str, Field(pattern=r'^[a-z][a-z0-9_]*$', max_length=100)]
SchemeID = Annotated[str, Field(pattern=r'^[a-z0-9]+(-[a-z0-9]+)*$', max_length=200)]
Scalar = StrictBool | StrictInt | StrictFloat | Annotated[StrictStr, Field(max_length=200)]
Truth = Literal['SATISFIED', 'FAILED', 'UNKNOWN']


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, allow_inf_nan=False)


class Text(StrictModel):
    en: Annotated[str, Field(min_length=1, max_length=1000)]
    hi: Annotated[str, Field(min_length=1, max_length=1000)] | None = None


class SourceReference(StrictModel):
    reference_id: Annotated[str, Field(min_length=1, max_length=200)]
    original_url: Annotated[str, Field(pattern=r'^https://[^\s]+$', max_length=2048)]
    title: Annotated[str, Field(min_length=1, max_length=500)]
    locator: Annotated[str, Field(min_length=1, max_length=1000)]
    last_checked_date: date
    content_sha256: Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')] | None = None


class AnswerField(StrictModel):
    key: Key
    kind: Literal['age', 'income', 'number', 'category', 'boolean']
    question: Text
    question_reviewed_languages: tuple[Language, ...] = ('en',)
    choices: tuple[Annotated[str, Field(min_length=1, max_length=200)], ...] = ()
    unit: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    period: Literal['monthly', 'annual', 'one_time'] | None = None
    scope: Literal['individual', 'household'] | None = None
    reference_basis: Annotated[str, Field(min_length=1, max_length=300)] | None = None

    @model_validator(mode='after')
    def semantics(self):
        if len(set(self.question_reviewed_languages)) != len(self.question_reviewed_languages):
            raise ValueError('Duplicate question review language')
        if 'hi' in self.question_reviewed_languages and self.question.hi is None:
            raise ValueError('Reviewed Hindi question text is missing')
        if self.kind == 'category' and (not self.choices or len(set(self.choices)) != len(self.choices)):
            raise ValueError('Category fields require distinct reviewed choices')
        if self.kind != 'category' and self.choices:
            raise ValueError('Only category fields have choices')
        if self.kind == 'income' and not all((self.unit, self.period, self.scope)):
            raise ValueError('Income requires explicit currency/unit, period and scope')
        if self.kind == 'age' and not self.reference_basis:
            raise ValueError('Age requires a reviewed reference basis')
        return self


class RuleNode(StrictModel):
    rule_id: Annotated[str, Field(pattern=r'^[a-z0-9][a-z0-9_-]*$', max_length=100)]
    parent_id: str | None = None
    node_type: Literal['predicate', 'and', 'or', 'not']
    label: Text
    attribute: Key | None = None
    operator: Literal['eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'in', 'not_in'] | None = None
    expected_value: Scalar | tuple[Scalar, ...] | None = None
    enabled: StrictBool = False
    confidence: Literal['VERIFIED', 'UNCERTAIN'] = 'UNCERTAIN'
    applicability_confirmed: StrictBool = False
    effective_from: date | None = None
    effective_to: date | None = None
    source_ids: tuple[str, ...] = ()

    @model_validator(mode='after')
    def shape(self):
        if self.node_type == 'predicate':
            if self.attribute is None or self.operator is None or self.expected_value is None:
                raise ValueError('Predicate requires attribute/operator/value')
            if (self.operator in ('in', 'not_in')) != isinstance(self.expected_value, tuple):
                raise ValueError('Membership requires an explicit nonempty set')
            if isinstance(self.expected_value, tuple) and not self.expected_value:
                raise ValueError('Membership set is empty')
        elif any(v is not None for v in (self.attribute, self.operator, self.expected_value)):
            raise ValueError('Groups cannot contain predicate expressions')
        if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
            raise ValueError('Invalid rule effective interval')
        return self


class RuleSet(StrictModel):
    """Loaded only by a trusted provider. Clients cannot submit this object."""
    scheme_id: SchemeID
    version: Annotated[str, Field(min_length=1, max_length=100)]
    publication_status: Literal['draft', 'reviewed', 'published'] = 'draft'
    approval_status: Literal['unreviewed', 'approved'] = 'unreviewed'
    execution_enabled: StrictBool = False
    complete: StrictBool = False
    root_failure_is_decisive: StrictBool = False
    reviewer_reference: Annotated[str, Field(min_length=1, max_length=200)] | None = None
    reviewed_on: date | None = None
    applicability_confirmed: StrictBool = False
    effective_from: date | None = None
    effective_to: date | None = None
    review_valid_until: date | None = None
    unresolved_conditions: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    fields: Annotated[tuple[AnswerField, ...], Field(max_length=64)] = ()
    nodes: Annotated[tuple[RuleNode, ...], Field(min_length=1, max_length=128)]
    sources: Annotated[tuple[SourceReference, ...], Field(max_length=256)] = ()

    @model_validator(mode='after')
    def tree(self):
        nodes = {n.rule_id: n for n in self.nodes}
        fields = {f.key: f for f in self.fields}
        sources = {s.reference_id for s in self.sources}
        if len(nodes) != len(self.nodes) or len(fields) != len(self.fields) or len(sources) != len(self.sources):
            raise ValueError('Duplicate rule, field or source identifier')
        if len([n for n in self.nodes if n.parent_id is None]) != 1:
            raise ValueError('Exactly one root required')
        for node in self.nodes:
            if node.attribute is not None and node.attribute not in fields:
                raise ValueError('Unknown answer field')
            if any(s not in sources for s in node.source_ids):
                raise ValueError('Unknown source reference')
            seen, current = set(), node
            while current.parent_id is not None:
                if current.rule_id in seen or current.parent_id not in nodes or len(seen) >= 16:
                    raise ValueError('Cyclic, missing or excessively deep parent')
                seen.add(current.rule_id)
                current = nodes[current.parent_id]
            count = sum(n.parent_id == node.rule_id for n in self.nodes)
            if (node.node_type == 'predicate' and count or node.node_type == 'not' and count != 1
                    or node.node_type in ('and', 'or') and count == 0):
                raise ValueError('Invalid group arity')
        if not any(n.node_type == 'predicate' for n in self.nodes):
            raise ValueError('At least one predicate required')
        return self


class EvaluationRequest(StrictModel):
    scheme_id: SchemeID
    answers: Annotated[dict[Key, Scalar | None], Field(max_length=64)] = Field(default_factory=dict)
    language: Language = 'en'

    @field_validator('answers')
    @classmethod
    def finite_bounded(cls, answers):
        for value in answers.values():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if abs(value) > 10**18 or not isfinite(value):
                    raise ValueError('Answer outside supported numeric bounds')
        return answers


class ConditionResult(StrictModel):
    rule_id: str
    node_type: str
    attribute: str | None
    result: Truth
    reason_code: str
    label: str
    explanation: str
    content_language: Language
    translation_fallback: bool
    source_ids: tuple[str, ...] = ()


class Question(StrictModel):
    attribute: str
    rule_ids: tuple[str, ...]
    text: str
    kind: str
    choices: tuple[str, ...]
    unit: str | None
    period: str | None
    scope: str | None
    reference_basis: str | None
    content_language: Language
    translation_fallback: bool


class PolicyReview(StrictModel):
    publication_status: str
    approval_status: str
    execution_enabled: bool
    complete: bool
    applicable: bool
    reviewed_on: date | None = None
    blockers: tuple[str, ...] = ()


class EvaluationResponse(StrictModel):
    schema_version: Literal['1.0'] = '1.0'
    scheme_id: str
    rule_set_version: str | None = None
    language: Language
    status: Literal['ELIGIBLE', 'INELIGIBLE', 'NEEDS_VERIFICATION']
    policy_review: PolicyReview
    evaluated_conditions: tuple[ConditionResult, ...] = ()
    satisfied_rules: tuple[str, ...] = ()
    failed_rules: tuple[str, ...] = ()
    unknown_conditions: tuple[str, ...] = ()
    missing_answers: tuple[str, ...] = ()
    questions_needed: tuple[Question, ...] = ()
    sources: tuple[SourceReference, ...] = ()
    explanation: str
