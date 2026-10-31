# Phase 3 archive to Supabase mapping

Audit date: 31 October 2026. This is a preparation mapping, not executable SQL.
The existing migrations and permissions are unchanged. All database tables below
are in `scheme_catalog` and use UUID primary keys; archive IDs are not UUIDs.

| Archive field | Existing destination | Transformation / blocker |
| --- | --- | --- |
| administering_ministry / department | organizations.code, name, government_level, official_url | Verify actual authority and authoritative URL; do not substitute discovery publisher for administrator. code is unique; no guessed organization URL. |
| classification, jurisdiction | schemes.government_level; jurisdictions.code/name/kind/parent_id; scheme_jurisdictions | All 16 are labelled central/India. State mirrors do not make them state schemes. Resolve verified jurisdiction codes and organization FK first. |
| scheme_id | schemes.stable_id | Proposed lowercase `IN-CEN-000001` -> `in-cen-000001`, preserving external ID in sidecar manifest. UUID assigned/resolved at authorized import; never rename existing scheme identity. |
| record_stage / human_verification_date | scheme_versions.status, last_checked_date, reviewed_at, reviewer_reference | Every target is draft. Null verification is unknown; extraction/retrieval dates must not become verification dates. |
| extraction_timestamp / version_history | ingestion_runs.importer_version/started_at; sidecar | Archive history is not a database version number. Allocate version_number per scheme under lock after comparing canonical input hashes. |
| status = verified_active | schemes.lifecycle_status | Archive label is untrusted and not a database enum. Proposed unknown until a human verifies current applicability. Preserve dated status assertions and limitations in sidecar. |
| official_name | translations.title, language_code=en | English name exists for all records; no complete reviewed translation. Requires evidence UUID. |
| official_hindi_name, hindi_name_evidence | translations.title, language_code=hi | Four names concern approved renamings with unknown implementation dates; retain historical name/approved-name roles. Do not silently use the new name for the old version. |
| description / translations | translations.summary, eligibility_text, translation_origin, review_status | No explicit description field or translation objects in this batch. summary is NOT NULL. Do not synthesize it from beneficiaries or fabricate Hindi text. A missing field is an import blocker, not permission to insert a guessed value. |
| benefits[].text/amount/currency/frequency | benefits.description, amount_min/amount_max, currency, frequency, benefit_type, item_key | Review semantic type: some entries contain premiums/costs, phase-specific amounts and death-benefit conditions. Do not treat each numeric amount as unconditional citizen entitlement. Each row needs evidence_id. |
| eligibility_conditions | eligibility_rules.rule_key/node_type/attribute/operator/expected_value/unit/time_basis/confidence/uncertainty_reason | A reviewed operator vocabulary is required. `=` could map to eq; `>=` to gte; `<=` to lte. inclusive_range needs two predicates under AND after review. `range_as_worded` and manual_assessment_required cannot be converted automatically. All proposals remain disabled/UNCERTAIN. |
| rule evidence[] | rule_evidence.rule_id/evidence_id/scheme_version_id | Resolve evidence after snapshot; composite FK forbids cross-version association. Multiple citations must not be reduced to one. |
| exclusions / historical_deprivation_tests | no dedicated exclusions/history table | Preserve complete source structures in manifest. Exclusions need separately reviewed rule-tree semantics (NOT/AND/OR), not silent inversion or treating an empty array as no restrictions. Historical tests must not become current conditions. |
| documents[].text/condition | required_documents.document_type/requirement/condition_text/item_key | Composite descriptive text is not a canonical document type. Verify alternatives, current forms and conditionality first. Requires evidence_id. |
| application.method / official_application_url / window | application_routes.mode/original_url/instructions/last_checked_date | No explicit mode in archive; do not infer it from prose. Null verified URL cannot be invented. Online/both modes require original_url. Information/landing URL is not proof of a working transaction or open application window. |
| source register | official_sources.organization_id/original_url/title/source_kind/external_resource_id/license_url/access_policy_url/access_status | Original URL stays exact; source_type needs reviewed enum mapping. Sxx is a batch-local source ID, not necessarily global. Archive checked is not a reuse license or written authorization. |
| source bytes | source_snapshots.source_id/content_sha256/fetched_at/source_updated_at/resolved_url/artifact_path/media_type | Original website/PDF snapshots are absent. Local artifact hashes must NOT be used as government-document hashes. Unknown day/year-precision times cannot become fabricated exact timestamps. |
| evidence[].source_id/url/locator and original_source_wording | evidence.snapshot_id/locator/supporting_text/last_checked_date | Preserve exact quotation vs extracted paraphrase distinctions. No snapshot/evidence UUID is presently resolved. Different assertions at the same locator must be retained for review, not overwritten under UNIQUE(snapshot_id, locator). |
| record hash / batch hash | ingestion_runs.source_id/idempotency_key/importer_version/status | Future key includes reviewed manifest and importer version. This tool creates no ingestion_runs row. |

Unmapped data (alternate names, announced changes, approved-name dates, status
limitations, conflicts/assertions/resolutions, version history, coverage tasks,
review queue and unknown future fields) is preserved losslessly in the manifest
and extracted originals. No existing JSON contract is changed to accommodate it.

## Relationships, uniqueness and publication

Resolve organizations/jurisdictions -> sources -> immutable source snapshots ->
evidence -> schemes/versions -> localized and detail children -> rule evidence.
Organization and jurisdiction codes, source URL and stable scheme ID are unique.
Versions are unique by `(scheme_id, version_number)`. Snapshot uniqueness is
`(source_id, content_sha256)`; evidence is `(snapshot_id, locator)`. Child item keys
and rule keys are version-scoped. Ingestion keys are unique per source. Consult
the migrations for exact check constraints and node arity; do not bypass them.

Version insertion starts at draft. Transition to reviewed requires reviewed en/hi
translations, jurisdiction coverage, a rule root, evidence for every predicate,
review metadata and last_checked_date. Deferred checks reject invalid trees and
cycles. Reviewed content freezes; publishing changes only permitted publication
metadata. No archive status can authorize either transition.

The ten existing read-only views are published_versions, published_schemes,
published_jurisdictions, published_translations, published_benefits,
published_application_routes, published_required_documents,
published_eligibility_rules, published_rule_evidence and published_evidence.
Phase 2 reads only these views and selects the latest effective version. Draft
preparation output cannot appear in the API. The scheme_api runtime role remains
read-only and must never be repurposed as an importer.
