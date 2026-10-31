# Phase 4C trusted policy provider

The eligibility and questionnaire endpoints now resolve through
`TrustedPolicyProvider`. No government execution approval was created. The
server-owned `app/eligibility/execution_approvals.json` ships with an empty list;
all five real drafts remain unavailable, with no database connection for IDs that
have no eligible approval entry. Existing API DTOs and routes are unchanged.

## Architecture and approval boundary

1. `get_rule_provider` reloads a bounded, strictly validated server-owned approval
   file on every request. Duplicate JSON keys, nonfinite values, unknown fields,
   duplicate scheme entries and malformed metadata fail with sanitized HTTP 503.
   This file path is fixed in backend code, not supplied by clients or new env vars.
2. An entry must explicitly approve execution and completeness, identify a human
   review reference/date, have a current validity/effective interval and have no
   unresolved conditions or conflicts. Otherwise no database query is made.
3. `PublishedPolicyRepository.get_latest` resolves the stable ID using only the
   existing published views. It loads the latest published version, full rule tree,
   rule-evidence links and relevant evidence within one existing read-only
   REPEATABLE READ connection. It never searches drafts or falls back to an older
   version whose approval happens to match.
4. Provider checks exact scheme identity, version UUID/number, active lifecycle,
   current effective dates, publication/verification metadata and full snapshot
   SHA-256. Changed/missing conditions, links or source details invalidate approval.
5. Each rule UUID needs an explicit enabled/applicable node annotation. Every
   database node must be VERIFIED and have no remaining uncertainty. All predicate
   fields need reviewed typed descriptors; every predicate needs checked evidence.
   Unknown/duplicate links, unapproved source hosts, invalid hashes, unsupported
   operators, incompatible units and malformed trees are rejected.
6. The provider builds the existing RuleSet with original UUIDs, AND/OR/NOT parent
   relationships and source evidence IDs/URLs. It calls the existing pure engine
   with no citizen answers to reuse readiness, type and mandatory-conflict guards.
   Any blocker rejects the policy; no partial root is substituted.

Missing/rejected approvals return no RuleSet, preserving NEEDS_VERIFICATION and no
question collection. Database failures propagate existing sanitized HTTP 503
errors; they do not trigger cached, draft or fabricated fallback policies.
The implementation does not log citizen input or write any database/file data.

## Existing schema compatibility and gaps

No existing migration or permission was changed. Queries use real columns only:

| Existing view | Used information |
| --- | --- |
| published_schemes | stable_id, scheme UUID, lifecycle_status |
| published_versions | version UUID/number, effective dates, last_checked_date, published_at |
| published_eligibility_rules | UUID/key/parent, node_type, attribute/operator/value, unit/time_basis, confidence/uncertainty |
| published_rule_evidence | version-bound rule/evidence links |
| published_evidence | evidence UUID, locator/supporting text, source URL/title, verification/fetch/source dates, capture hash/license |

The published version view does **not** expose reviewer_reference/reviewed_at.
The database has no execution-enabled flag, completeness attestation, execution
approval expiry, typed answer descriptors, per-rule labels, reviewed question
languages or full unresolved-policy ledger. Published content is immutable under
the existing review workflow, but that workflow does not enforce all policy
review blockers. Publication or VERIFIED alone is never execution approval.

The safe solution for this phase is a supplemental, server-owned approval manifest
bound to exact database content. This avoids an unnecessary parallel database
schema or new remote grants. No migration is required for this approach and no
proposed SQL is placed in the auto-applied migrations directory.

If centralized database approvals are needed later, propose a separately reviewed
migration in `scheme_catalog` for immutable approval metadata tied to an exact
version/content hash, explicit expiry/revocation and reviewed field/node metadata.
Expose it through a dedicated publication-filtered read-only view, preserving no
base-table grants for scheme_api. Its ownership, revocation semantics, constraints,
RLS, reader grants and migration tests need separate review before application.
This is an optional future design, not a missing column silently queried today.

## Approval data requirements

`ExecutionApproval` in `app/eligibility/approvals.py` defines the exact schema:

- `scheme_id`, `version_id`, `version_number`, `snapshot_sha256`.
- Explicit `execution_approved=true`, `complete=true`, reviewer_reference,
  reviewed_on, valid_until, effective_from and optional effective_to.
- Empty conflicts and unresolved_conditions after independent review.
- Exact allowed_source_hosts (no wildcards). Human review must establish the
  authority/reuse of these sources; a hostname allowlist is not proof of policy law.
- Typed fields using the existing AnswerField model: key, kind, reviewed question
  text/languages, category choices, units, income period/scope and age reference.
- One NodeApproval per database rule UUID: reviewed bilingual label,
  enabled=true, applicability_confirmed=true and any node-specific effective dates.

No operator, expected threshold, parent edge or citation can be overridden in the
manifest. These come from the published database snapshot. Per-node annotation
must match the full set of rule UUIDs. Field definitions must match exactly the
attributes used by predicates. Stored units must agree with typed descriptors;
time_basis and other raw fields are included in the reviewed content digest.
There is no automatic income conversion, age-date inference or operator fallback.
The existing unsupported `exists` operator remains unavailable until an explicitly
reviewed semantic adapter is implemented.

`snapshot_digest` serializes all snapshot header fields, every rule column, every
link and every relevant evidence field using canonical JSON, sorting row arrays
by UUID. This includes supporting text, capture hash, URL, checked/fetched/source
dates, unit/time basis and lifecycle state. The approval binds exact content, not
just a scheme name or version number. Generate/review this digest from an
authorized read-only export; this phase includes no approval generator or command
that turns exported drafts into approved rules.

The manifest is trusted deployment configuration, not a cryptographic certificate.
Only authorized policy reviewers/deployers may change it; do not accept a manifest
from an API request, uploaded citizen file or writable public directory. Deploy
updates atomically. No secrets or citizen answers belong in this file. The empty
manifest in this task is not authorization to approve any government policy.

## Version and questionnaire safety

RuleSet.version is `database-version-number:SHA256(execution-approval-entry)`.
The entry digest binds the exact database version UUID/content digest and all
execution approval, field, wording and source-host metadata. Each response already
includes rule_set_version, each condition includes its original rule UUID and
source IDs, and each source includes its checked date and original URL. No extra
credentials or SQL details are exposed.

Phase 4B fingerprints the complete resulting RuleSet. Approval revocation/removal,
expiry, a new published version, changed source content or a new approval changes
the fingerprint or makes the policy unavailable. An ongoing /next or /answer then
fails with POLICY_CHANGED (409), requiring restart rather than silently substituting
rules. A configuration/database outage returns 503 instead; it cannot create a
definitive eligibility result. Clients cannot submit version IDs, rules, approval
flags or outcome metadata; existing DTO validation rejects these fields.

One request uses a single approval snapshot and one REPEATABLE READ database
snapshot. Updates committed during that request are detected at the next request,
not by switching a tree halfway through evaluation. No cross-request policy cache
or server session is introduced. The latest-published check is conservative: a
newer future-effective/unapproved version blocks an older approval instead of
silently falling back to it.

## Restricted connection and runtime behavior

The repository reuses `app/db/connection.py`: dedicated scheme_api login checks,
scheme_catalog_reader membership, no admin/base-table access, TLS verify-full,
read-only transactions, REPEATABLE READ, bounded connect/statement timeouts and
rollback on exit. Queries are fixed and parameterized; citizen answers are never
passed to SQL or the provider. Empty registry lookups require no connection.
No live Supabase access, smoke command, migration or permission operation was run.

All four endpoints are wired through the unchanged dependency key:

- POST /api/v1/eligibility/evaluate
- POST /api/v1/questionnaire/start
- POST /api/v1/questionnaire/next
- POST /api/v1/questionnaire/answer

Existing response contracts and error privacy/cache handling remain in place.
The legacy bulk frontend JSON contract still needs its separately documented
adapter; Phase 4C does not modify frontend files or contracts.

## Five real schemes: prerequisites to execution

Follow PHASE3D_REVIEW_MATRIX.md and the existing draft-import/review runbooks:

1. Independently resolve PMSBY age/cover-start questions; PMJJBY birthday/lien/form
   questions; PM-SYM income/contribution/exclusion conflicts; PMUY current phase,
   KYC/family definitions and support; IGNOAPS state/legacy/category/name issues.
2. Complete the full necessary rule/exclusion sets, typed descriptors, temporal
   scope, source verification and English/Hindi review. Current partial AND roots
   are not complete policies; do not approve them by toggling booleans.
3. Separately authorize eventual draft import/review/publication through the
   existing controlled workflow. No draft or unpublished record is executable.
4. Review the exact published snapshot and its digest, all source hosts and node
   labels/questions. Only then may authorized reviewers create a concrete,
   time-bounded execution approval in the trusted manifest.
5. Test boundary/unknown/exclusion cases on that reviewed policy before deployment.
   Recheck actual restricted role/TLS with an authorized read-only integration test.

Until those gates are complete, the five schemes intentionally remain unavailable
for executable eligibility decisions. The provider does not approve policy facts
or resolve legal ambiguity itself.

## Files and validation

Added `app/db/policies.py`, `app/eligibility/approvals.py`, empty
`app/eligibility/execution_approvals.json`, `tests/test_policy_provider.py` and this
report. Updated only `app/eligibility/provider.py` for runtime integration.
No dependency was added; the evaluator and questionnaire orchestration are reused.

Focused command:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_policy_provider.py -v
```

Tests use synthetic snapshots/approval records and mocked read-only connections,
not government approvals. Coverage includes approved publication, absent/draft
publication, unapproved/incomplete/conflicting/stale policies, missing nodes/source
provenance, malformed trees, unsupported operators, AND/OR/NOT, version/content
substitution, client injection, multi-step questionnaire consistency, SQL parameters,
published-only reads and sanitized database failure. The existing connection tests
also verify TLS, restricted role, read-only isolation and rollback.

Results: 13 focused provider tests passed. The complete suite then ran once:
94 Python tests plus eight catalogue, nine single-scheme staging, six batch staging
and one isolated payload check passed (118 total). Existing endpoints remain
compatible. No live connection/write, scheme activation, migration application,
permission change, frontend modification, commit or push occurred.
