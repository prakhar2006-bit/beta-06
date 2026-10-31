"""Server-owned execution approvals, separate from publication and citizen input."""
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, StrictBool, StrictInt, ValidationError, model_validator

from app.core.errors import APIError
from app.schemas.eligibility import AnswerField, SchemeID, StrictModel, Text

APPROVAL_FILE = Path(__file__).with_name('execution_approvals.json')


class NodeApproval(StrictModel):
    rule_id: UUID
    label: Text
    enabled: StrictBool = False
    applicability_confirmed: StrictBool = False
    effective_from: date | None = None
    effective_to: date | None = None


class GuidanceItemApproval(StrictModel):
    item_id: UUID
    language: Literal['en', 'hi']
    application_url_verified: StrictBool = False


class GuidanceApproval(StrictModel):
    snapshot_sha256: Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]
    reviewer_reference: Annotated[str, Field(min_length=1, max_length=200)]
    reviewed_on: date
    valid_until: date
    benefits: tuple[GuidanceItemApproval, ...] = ()
    documents: tuple[GuidanceItemApproval, ...] = ()
    application_routes: tuple[GuidanceItemApproval, ...] = ()
    allowed_application_hosts: tuple[str, ...] = ()

    @model_validator(mode='after')
    def valid_review(self):
        if self.valid_until < self.reviewed_on:
            raise ValueError('Invalid guidance review interval')
        for items in (self.benefits,self.documents,self.application_routes):
            if len({i.item_id for i in items}) != len(items):
                raise ValueError('Duplicate guidance item review')
        if any(i.application_url_verified for i in (*self.benefits,*self.documents)):
            raise ValueError('Only application routes can approve a URL')
        if any(not re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*',host) for host in self.allowed_application_hosts):
            raise ValueError('Application hosts must be exact DNS names')
        return self


class ExecutionApproval(StrictModel):
    scheme_id: SchemeID
    version_id: UUID
    version_number: Annotated[StrictInt, Field(ge=1, le=2147483647)]
    snapshot_sha256: Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]
    execution_approved: StrictBool = False
    complete: StrictBool = False
    reviewer_reference: Annotated[str, Field(min_length=1, max_length=200)]
    reviewed_on: date
    valid_until: date
    effective_from: date
    effective_to: date | None = None
    conflicts: tuple[str, ...] = ()
    unresolved_conditions: tuple[str, ...] = ()
    allowed_source_hosts: Annotated[tuple[str, ...], Field(min_length=1, max_length=64)]
    fields: Annotated[tuple[AnswerField, ...], Field(max_length=64)]
    nodes: Annotated[tuple[NodeApproval, ...], Field(min_length=1, max_length=128)]
    guidance: GuidanceApproval | None = None

    @model_validator(mode='after')
    def identities(self):
        if len({n.rule_id for n in self.nodes}) != len(self.nodes) or len({f.key for f in self.fields}) != len(self.fields):
            raise ValueError('Duplicate approval identifier')
        if self.valid_until < self.reviewed_on or self.effective_to and self.effective_to < self.effective_from:
            raise ValueError('Invalid approval interval')
        if any(not re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*', host) for host in self.allowed_source_hosts):
            raise ValueError('Source hosts must be exact lowercase DNS names')
        return self


class ApprovalManifest(StrictModel):
    schema_version: Literal['1.0']
    approvals: Annotated[tuple[ExecutionApproval, ...], Field(max_length=1000)]

    @model_validator(mode='after')
    def unique_schemes(self):
        if len({a.scheme_id for a in self.approvals}) != len(self.approvals):
            raise ValueError('Only one approved candidate per stable scheme')
        return self


def approval_digest(approval):
    return sha256(json.dumps(approval.model_dump(mode='json'), sort_keys=True,
        separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')).hexdigest()


def load_approvals() -> ApprovalManifest:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    try:
        if APPROVAL_FILE.stat().st_size > 1_000_000:
            raise ValueError('Approval file too large')
        data = json.loads(APPROVAL_FILE.read_text(encoding='utf-8'), object_pairs_hook=unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
        return ApprovalManifest.model_validate(data)
    except (OSError, ValueError, ValidationError, RecursionError):
        raise APIError(503, 'POLICY_CONFIGURATION_UNAVAILABLE', 'Execution approval configuration is unavailable.') from None
