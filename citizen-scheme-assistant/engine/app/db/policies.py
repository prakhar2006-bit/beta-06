"""Published policy snapshots through the existing restricted read-only connection."""
from datetime import date, datetime
from hashlib import sha256
import json
from uuid import UUID

from pydantic import BaseModel, ConfigDict, ValidationError

from app.core.errors import APIError
from app.db.connection import open_connection
from app.schemas.schemes import Evidence, Rule, RuleEvidence


class PublishedPolicy(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    scheme_id: str
    scheme_database_id: UUID
    lifecycle_status: str
    version_id: UUID
    version_number: int
    effective_from: date | None
    effective_to: date | None
    last_checked_date: date | None
    published_at: datetime
    rules: tuple[Rule, ...]
    rule_evidence: tuple[RuleEvidence, ...]
    sources: tuple[Evidence, ...]


def snapshot_digest(snapshot: PublishedPolicy) -> str:
    data = snapshot.model_dump(mode='json')
    data['rules'].sort(key=lambda r:r['id'])
    data['rule_evidence'].sort(key=lambda r:(r['rule_id'],r['evidence_id']))
    data['sources'].sort(key=lambda r:r['id'])
    return sha256(json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                             allow_nan=False).encode('utf-8')).hexdigest()


class PublishedPolicyRepository:
    def get_latest(self, scheme_id: str) -> PublishedPolicy | None:
        # Latest published version overall: never fall back to an older approval.
        with open_connection() as conn, conn.cursor() as cursor:
            cursor.execute('''SELECT s.stable_id AS scheme_id, s.id AS scheme_database_id,
                s.lifecycle_status, v.id AS version_id, v.version_number,
                v.effective_from, v.effective_to, v.last_checked_date, v.published_at
                FROM scheme_catalog.published_schemes s
                JOIN scheme_catalog.published_versions v ON v.scheme_id = s.id
                WHERE s.stable_id = %(scheme_id)s
                ORDER BY v.version_number DESC, v.id LIMIT 1''', {'scheme_id':scheme_id})
            row = cursor.fetchone()
            if row is None:
                return None
            params = {'version_id':row['version_id']}
            cursor.execute('''SELECT id, rule_key, parent_id, node_type, attribute, operator,
                expected_value, unit, time_basis, confidence, uncertainty_reason
                FROM scheme_catalog.published_eligibility_rules
                WHERE scheme_version_id = %(version_id)s ORDER BY id''', params)
            row['rules'] = cursor.fetchall()
            cursor.execute('''SELECT rule_id, evidence_id FROM scheme_catalog.published_rule_evidence
                WHERE scheme_version_id = %(version_id)s ORDER BY rule_id, evidence_id''', params)
            row['rule_evidence'] = cursor.fetchall()
            cursor.execute('''SELECT e.* FROM scheme_catalog.published_evidence e WHERE e.id IN
                (SELECT evidence_id FROM scheme_catalog.published_rule_evidence
                 WHERE scheme_version_id = %(version_id)s) ORDER BY e.id''', params)
            row['sources'] = cursor.fetchall()
            try:
                return PublishedPolicy.model_validate(row)
            except ValidationError:
                raise APIError(503, 'RULE_SET_INVALID', 'Published policy definitions are unavailable.') from None
