# Phase 3D isolated staging report

Result: all five prepared schemes imported successfully into one fresh in-memory
PGlite database using the unchanged Supabase migrations. Default dry-runs rolled
back. Exact repeat wrote zero additional rows. No live Supabase connection, write,
permission change or publication occurred.

## Concrete collection and counts

Index: `.phase3-output/phase3d/collection.json`, with SHA-256 checks for each draft
and captured-source byte verification before database creation. Inputs are the
existing Phase 3A manifest, unchanged PMSBY ledger and four new Phase 3D ledgers.
The `in-cen-*` stable IDs are retained project/archive identifiers, not claimed
government-issued scheme codes.
The collection index SHA-256 is
`96ab15cb6cfd0f0ac66b7aafce03b3ea54e589d4a120257d5f3d6eb9269aef92`.
Preparing again into `.phase3-output/phase3d-repro/` reproduced a byte-identical
index and the same five bound draft hashes.

| Catalogue relation | Rows |
| --- | ---: |
| organizations | 5 |
| jurisdictions | 1 |
| official_sources | 8 |
| source_snapshots | 8 |
| evidence | 53 |
| schemes | 5 |
| scheme_versions | 5 |
| scheme_jurisdictions | 5 |
| translations | 10 |
| benefits | 8 |
| application_routes | 2 |
| required_documents | 6 |
| eligibility_rules | 21 |
| rule_evidence | 16 |
| **Catalogue content rows** | **153** |
| ingestion_runs (local only) | 5 |
| local_rehearsal.receipts (full payloads, local only) | 5 |
| **Total local table rows** | **163** |

All five versions and ten translations remain draft. All 21 rule nodes, including
16 predicates, remain UNCERTAIN/disabled. Zero published versions or enabled
unapproved rules. “Disabled” is retained sidecar metadata; no schema column or
database permission has been invented. Original source URLs, fetch hashes/times,
claim checked dates, bilingual metadata and all 17 archive conflicts are preserved
in the five full-payload receipts and original ignored bundles.

Shared organization/jurisdiction/source/snapshot identities are resolved by their
actual schema keys; they are reused only when incoming content agrees. This is
why PMSBY adds 37 rows in the batch after PMJJBY, versus its standalone 42-row run.
Each scheme still gets its own source-scoped idempotency receipt. Existing per-draft
receipt keys remain compatible with Phase 3C. No input record is overwritten.

## Reused and generalized components

- `ingestion/prepare.py` and `ingestion/verification.py`: reused unchanged. Their
  verification machinery was already generic; the Phase 3B research ledger was
  PMSBY-specific. The new ledgers use the same format and stable archive IDs.
- `ingestion/staging_validate.py`: reused unchanged as a one-record bundle protocol.
  Source ownership, byte hashes and original-record/conflict checks are retained.
- `ingestion/batch.py`: new thin collection layer. Sorts stable IDs, rejects
  duplicates, reuses prepare_verified, validates bundle hashes and confines index
  paths to the collection directory. Output includes no current-run timestamps.
  Existing output cannot be overwritten; use a fresh output root for another run.
- `db-validation/staging-import.mjs`: existing mapping/constraint/idempotency logic
  retained; adds validated collection loading and an atomic batch transaction.
  Schemes are processed in stable-ID order. Version previews are checked per scheme
  using `expectedVersions`; all newly imported rows and receipts roll back if any
  scheme fails. No existing record is updated or promoted.
- `db-validation/staging-batch.mjs`: local collection CLI, dry-run by default;
  optional in-memory commit/repeat verifies full receipts and unpublished status.
- New `tests/test_batch.py` and `db-validation/staging-batch.test.mjs` validate the
  collection layer and batch transactions with synthetic fixtures.

Only the batch wrapper owns BEGIN/COMMIT/ROLLBACK; per-scheme work runs within it.
Deferred constraints are reset while each tree is assembled and forced before
success. Local busy-guard serialization is not a multi-session remote lock. There
is still no remote adapter, DSN option, writer credential handling or live-write flag.

## Commands and validation

From `citizen-scheme-assistant/engine`, prepare into a **fresh** root:

```powershell
.\.venv\Scripts\python.exe -m ingestion.batch --manifest .phase3-output/verified/b6c4262434a8dd3e/manifest.json --ledger .phase3-output/phase3b-evidence/pmsby-review-v2.json --ledger .phase3-output/phase3d-evidence/pmjjby.json --ledger .phase3-output/phase3d-evidence/pm-sym.json --ledger .phase3-output/phase3d-evidence/pmuy.json --ledger .phase3-output/phase3d-evidence/ignoaps.json --output-root .phase3-output/phase3d-new-run
node db-validation/staging-batch.mjs .phase3-output/phase3d/collection.json
node db-validation/staging-batch.mjs .phase3-output/phase3d/collection.json --rehearse-local
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test db-validation/catalog.test.mjs
node db-validation/staging.test.mjs
node db-validation/staging-batch.test.mjs
node db-validation/validate-draft.mjs .phase3-output/phase3b/afe9609bc2b9a0db/draft.json
```

Results:

- 42 Python tests passed (39 existing plus three collection tests), including
  health/docs and Phase 2 API/repository tests with mocked database access.
- Eight existing catalogue database tests passed.
- Nine existing single-scheme staging tests passed.
- Six new batch staging tests passed: shared-ID/provenance deduplication, exact
  repeat, deterministic rollback-only previews, late SQL failure rolling back all
  earlier schemes, late version conflict preserving pre-existing data, duplicate
  identifiers/invalid references/changed hashes, draft/disabled status and blocked
  network calls. Some tests cover multiple closely related assertions.
- One isolated real PMSBY constraint test passed.
- Actual five-scheme rehearsal passed, including two equivalent dry-runs in
  opposite input order, an in-memory commit, zero-write repeat, full-payload receipt
  comparison and zero published versions.

Windows sandbox restrictions blocked temporary files/Node child processes on
initial attempts. Affected checks passed with local execution permission; these
were not database or scheme-data failures. No dependency was added. The .env,
existing migrations, permissions, frontend and existing prepared records remain
unchanged. No commit or push was performed.

## Readiness and precise next steps

The five-scheme pipeline is ready for **local draft preparation/rehearsal**.
Publication blockers by scheme are in PHASE3D_REVIEW_MATRIX.md. No human source or
translation review is implied by passing structural constraints.

1. Human policy and bilingual reviewers inspect each concrete ledger, preserved
   conflict, source snapshot and rendered text. Record a decision and effective
   dates per rule. Select an intended state for IGNOAPS implementation details.
   Any approval for incomplete draft staging must explicitly retain all blockers.
2. For a future live draft import, follow PHASE3C_LIVE_IMPORT_RUNBOOK.md: obtain
   explicit approval bound to staging project/database, collection/draft hashes,
   stable IDs and expected current version per scheme. Implement/review a remote
   adapter, durable full-sidecar receipts/artifacts, concurrency locks and actual
   writer RLS tests in a separately authorized task. Only then use a separately
   authorized least-privilege writer with verified TLS. Never use scheme_api,
   client/service-role keys or existing runtime credentials for writes. No live
   writer credential was created, requested or used here.
3. For eligibility-engine development, first approve the attribute vocabulary,
   units, individual/household scope, age reference date, policy effective dates,
   full exclusions and manual/provider checks. Specify explicit unknown/manual
   outcomes and tests at boundaries and missing answers. Use isolated synthetic
   fixtures until a complete reviewed rule set exists. Keep citizen inputs
   ephemeral, avoid an overall eligible verdict from these partial roots, and do
   not use an LLM to make final eligibility decisions. Publishing and activation
   require separate human-approved workflow changes; neither is part of ingestion.

The local_receipts schema is rehearsal-only and was not added to Supabase
migrations. Durable provenance storage and bilingual child serving are still
design/implementation gates before any remote adapter can be used.

The benefit table has descriptive text but no machine-readable age-band condition.
IGNOAPS's INR 200 and INR 500 rows are alternatives for different ages, not additive
payments. Do not calculate entitlement by summing benefit rows. A reviewed benefit
condition representation is required before benefit calculation or publication.
