"""Approval boundary. Publication does not imply complete execution approval."""
from typing import Protocol
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

from pydantic import ValidationError

from app.schemas.eligibility import RuleNode, RuleSet, SourceReference
from app.db.policies import PublishedPolicyRepository, snapshot_digest
from app.db.guidance import GuidanceContext, PublishedGuidanceRepository
from app.core.errors import APIError
from app.eligibility.approvals import ApprovalManifest, approval_digest, load_approvals
from app.eligibility.engine import evaluate


class RuleProvider(Protocol):
    def get_rule_set(self, scheme_id: str) -> RuleSet | None: ...


class UnavailableRuleProvider:
    def get_rule_set(self, scheme_id: str) -> RuleSet | None:
        # No government rule set is currently approved. Never load ignored drafts.
        return None


class TrustedPolicyProvider:
    def __init__(self, repository: PublishedPolicyRepository, manifest: ApprovalManifest, *, as_of=None, guidance_repository=None):
        self.repository = repository
        self.approvals = {a.scheme_id:a for a in manifest.approvals}
        self.as_of = as_of
        self.guidance_repository = guidance_repository

    def get_rule_set(self, scheme_id: str) -> RuleSet | None:
        today = self.as_of or datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
        approval = self.approvals.get(scheme_id)
        if (approval is None or not approval.execution_approved or not approval.complete
                or approval.conflicts or approval.unresolved_conditions
                or not approval.reviewed_on <= today <= approval.valid_until
                or today < approval.effective_from or approval.effective_to and today > approval.effective_to):
            return None
        snapshot = self.repository.get_latest(scheme_id)
        if snapshot is None:
            return None
        try:
            if (snapshot.scheme_id != scheme_id or snapshot.version_id != approval.version_id
                    or snapshot.version_number != approval.version_number
                    or snapshot.lifecycle_status != 'active'
                    or snapshot.effective_from is None or today < snapshot.effective_from
                    or snapshot.effective_to and today > snapshot.effective_to
                    or snapshot.last_checked_date is None or snapshot.last_checked_date > today
                    or snapshot.published_at.date() > today
                    or snapshot_digest(snapshot) != approval.snapshot_sha256):
                return None
            nodes = {n.id:n for n in snapshot.rules}
            reviews = {n.rule_id:n for n in approval.nodes}
            evidence = {e.id:e for e in snapshot.sources}
            if not nodes or len(nodes) != len(snapshot.rules) or set(nodes) != set(reviews) or len(evidence) != len(snapshot.sources):
                return None
            used_fields = {n.attribute for n in snapshot.rules if n.node_type == 'predicate'}
            fields = {f.key:f for f in approval.fields}
            if used_fields != set(fields):
                return None
            citations = {n.id:[] for n in snapshot.rules}
            seen = set()
            for link in snapshot.rule_evidence:
                pair = (link.rule_id, link.evidence_id)
                if pair in seen or link.rule_id not in nodes or link.evidence_id not in evidence:
                    return None
                seen.add(pair)
                citations[link.rule_id].append(str(link.evidence_id))
            if {e for _,e in seen} != set(evidence):
                return None
            sources = []
            for e in sorted(snapshot.sources, key=lambda e:str(e.id)):
                url = urlsplit(e.original_url)
                if (url.scheme != 'https' or url.hostname not in approval.allowed_source_hosts
                        or url.username or url.password or url.port not in (None,443)
                        or e.last_checked_date > today):
                    return None
                sources.append(SourceReference(reference_id=str(e.id),original_url=e.original_url,
                    title=e.source_title,locator=e.locator,last_checked_date=e.last_checked_date,content_sha256=e.content_sha256))
            mapped = []
            for n in sorted(snapshot.rules, key=lambda n:str(n.id)):
                review = reviews[n.id]
                if (n.confidence != 'VERIFIED' or n.uncertainty_reason and n.uncertainty_reason.strip()
                        or not review.enabled or not review.applicability_confirmed
                        or n.node_type == 'predicate' and not citations[n.id]):
                    return None
                if n.node_type == 'predicate' and n.unit is not None and fields[n.attribute].unit != n.unit:
                    return None
                mapped.append(RuleNode(rule_id=str(n.id),parent_id=str(n.parent_id) if n.parent_id else None,
                    node_type=n.node_type,label=review.label,attribute=n.attribute,operator=n.operator,expected_value=n.expected_value,
                    enabled=True,confidence='VERIFIED',applicability_confirmed=True,effective_from=review.effective_from,
                    effective_to=review.effective_to,source_ids=tuple(sorted(citations[n.id]))))
            rules = RuleSet(scheme_id=scheme_id,version=f'{snapshot.version_number}:{approval_digest(approval)}',
                publication_status='published',approval_status='approved',execution_enabled=True,complete=True,
                reviewer_reference=approval.reviewer_reference,reviewed_on=approval.reviewed_on,
                review_valid_until=approval.valid_until,applicability_confirmed=True,
                effective_from=max(approval.effective_from,snapshot.effective_from),
                effective_to=min(d for d in (approval.effective_to,snapshot.effective_to) if d is not None)
                    if approval.effective_to or snapshot.effective_to else None,
                fields=approval.fields,nodes=tuple(mapped),sources=tuple(sources))
            # Reuse engine readiness/type/conflict checks, with no citizen answers.
            if evaluate(rules,scheme_id,{},as_of=today).policy_review.blockers:
                return None
            return rules
        except (ValueError, TypeError, KeyError, ArithmeticError, ValidationError):
            return None

    def get_guidance(self,scheme_id: str,rule_set_version: str) -> GuidanceContext | None:
        approval=self.approvals.get(scheme_id)
        if approval is None or rule_set_version != f'{approval.version_number}:{approval_digest(approval)}':
            return None
        snapshot=(self.guidance_repository or PublishedGuidanceRepository()).get_for_version(scheme_id,approval.version_id)
        if snapshot is None:
            raise APIError(409,'POLICY_CHANGED','The policy changed. Start a new questionnaire.')
        if snapshot.scheme_id != scheme_id or snapshot.version_id != approval.version_id or snapshot.version_number != approval.version_number:
            raise APIError(503,'GUIDANCE_INVALID','Published guidance is unavailable.')
        return GuidanceContext(snapshot,approval.guidance,approval.allowed_source_hosts)


def get_rule_provider() -> RuleProvider:
    # Reload server-owned approvals on each request, so removal/revocation is effective.
    return TrustedPolicyProvider(PublishedPolicyRepository(), load_approvals())
