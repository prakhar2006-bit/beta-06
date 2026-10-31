"""Exact-version, reviewed published guidance through existing read-only views."""
from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import json
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ValidationError

from app.core.errors import APIError
from app.db.connection import open_connection
from app.eligibility.approvals import GuidanceApproval
from app.schemas.schemes import ApplicationRoute, Benefit, Evidence, RequiredDocument


class ReviewedTranslation(BaseModel):
    id: UUID
    language_code: Literal['en','hi']
    title: str
    summary: str
    translation_origin: Literal['official','human','machine']
    review_status: Literal['reviewed']
    evidence_id: UUID


class PublishedGuidance(BaseModel):
    scheme_id: str
    version_id: UUID
    version_number: int
    last_checked_date: date | None
    translations: tuple[ReviewedTranslation, ...]
    benefits: tuple[Benefit, ...]
    documents: tuple[RequiredDocument, ...]
    application_routes: tuple[ApplicationRoute, ...]
    sources: tuple[Evidence, ...]


@dataclass(frozen=True)
class GuidanceContext:
    snapshot: PublishedGuidance
    approval: GuidanceApproval | None
    allowed_source_hosts: tuple[str, ...]


def guidance_digest(snapshot):
    data=snapshot.model_dump(mode='json')
    for key in ('translations','benefits','documents','application_routes','sources'):
        data[key].sort(key=lambda item:item['id'])
    return sha256(json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')).hexdigest()


class PublishedGuidanceRepository:
    def get_for_version(self,scheme_id,version_id):
        with open_connection() as conn, conn.cursor() as cursor:
            params={'scheme_id':scheme_id,'version_id':version_id}
            cursor.execute('''SELECT s.stable_id AS scheme_id, v.id AS version_id,
                v.version_number, v.last_checked_date FROM scheme_catalog.published_schemes s
                JOIN scheme_catalog.published_versions v ON v.scheme_id=s.id
                WHERE s.stable_id=%(scheme_id)s AND v.id=%(version_id)s''',params)
            row=cursor.fetchone()
            if row is None:return None
            queries={
                'translations':'''SELECT id,language_code,title,summary,translation_origin,review_status,evidence_id
                    FROM scheme_catalog.published_translations WHERE scheme_version_id=%(version_id)s
                    AND review_status='reviewed' ORDER BY language_code,id''',
                'benefits':'SELECT * FROM scheme_catalog.published_benefits WHERE scheme_version_id=%(version_id)s ORDER BY id',
                'documents':'SELECT * FROM scheme_catalog.published_required_documents WHERE scheme_version_id=%(version_id)s ORDER BY id',
                'application_routes':'SELECT * FROM scheme_catalog.published_application_routes WHERE scheme_version_id=%(version_id)s ORDER BY id',
                'sources':'''SELECT e.* FROM scheme_catalog.published_evidence e WHERE e.id IN (
                    SELECT evidence_id FROM scheme_catalog.published_translations WHERE scheme_version_id=%(version_id)s AND review_status='reviewed'
                    UNION SELECT evidence_id FROM scheme_catalog.published_benefits WHERE scheme_version_id=%(version_id)s
                    UNION SELECT evidence_id FROM scheme_catalog.published_required_documents WHERE scheme_version_id=%(version_id)s
                    UNION SELECT evidence_id FROM scheme_catalog.published_application_routes WHERE scheme_version_id=%(version_id)s) ORDER BY e.id'''}
            for key,sql in queries.items():
                cursor.execute(sql,params);row[key]=cursor.fetchall()
            try:return PublishedGuidance.model_validate(row)
            except ValidationError:
                raise APIError(503,'GUIDANCE_INVALID','Published guidance is unavailable.') from None
