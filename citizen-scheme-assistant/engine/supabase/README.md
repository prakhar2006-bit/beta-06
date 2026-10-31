# Scheme catalogue database

This is an empty, PostgreSQL-compatible Supabase migration set owned by the
backend. Frontend components, JSON contracts, and `data/schemes/` are unchanged.
No scheme facts or citizen profiles are seeded. The existing JSON contracts
remain the API boundary; this schema does not change the current engine flow.

## Layout and local validation

- `migrations/20261030000100_catalog.sql`: 15 normalized catalogue tables and indexes.
- `migrations/20261030000200_integrity.sql`: review lifecycle, immutable provenance,
  rule-tree checks, and backend-only access controls.
- `migrations/20261030000300_backend_access.sql`: backend reader group role,
  published-only views, explicit Supabase client revocations and join indexes.
- `../db-validation/`: pinned PGlite dependency and Node tests that execute all
  migrations in an ephemeral in-memory PostgreSQL engine. Fixtures are synthetic,
  use `example.invalid`, and are rolled back; they are not government records.

From the repository's `citizen-scheme-assistant` directory:

```sh
npm --prefix engine/db-validation ci
npm --prefix engine/db-validation test
```

Requires Node 22 or later. On Windows with blocked PowerShell npm scripts, use
`npm.cmd`. PGlite verifies SQL execution and database constraints, but does not
replace a later native Supabase/PostgreSQL integration check (roles, PostgREST,
and concurrent transactions). No Supabase project configuration or remote link
is included. An approved deployment should integrate these ordered files into
the team's Supabase migration history; do not reapply them as an ingestion job.
Never run remote `db push`, remote SQL, or deployment as part of these tests.

## Access and privacy

`scheme_catalog` is a private schema: PUBLIC has no schema access; every table
has RLS enabled and no client policies. Do not add it to Supabase's exposed API
schemas or grant browser roles access. Connect from FastAPI using a server-only
database role. The credential-free `scheme_catalog_reader` group can SELECT only
the ten `published_*` views, with no base-table or write privileges. Provisioning
the separate LOGIN and password is an approved administrative step documented in
[Supabase integration](INTEGRATION.md). The migration owner can perform
ingestion/review. No Supabase-specific role or
extension is required; UUID defaults use PostgreSQL `gen_random_uuid()`.

There are no citizen, account, profile, uploaded-document or eligibility-answer
tables. Required documents store document *types*, not citizen document copies.
Reviewer references are opaque staff identifiers. Source URLs, artifact paths,
permission references and ingestion keys must never contain API keys, signed
URLs, personal data, or authentication tokens. Ingestion errors store codes,
not arbitrary response bodies. No raw response payload column is provided.

## Version and rule workflow

Scheme `stable_id` and UUID never change. Every correction creates a new
`scheme_versions` row with the next version number, initially `draft`. A draft
may be edited. Transition to `reviewed` requires reviewed `en` and `hi`
translations, jurisdiction coverage, a rule tree, evidence for each predicate,
human review metadata and `last_checked_date`. Transition from reviewed to
published only changes `status` and `published_at`. Reviewed/published content
cannot be edited or deleted. Multiple historical published versions are retained;
consumers must select the latest applicable published version per scheme, taking
effective dates into account. Publication does not imply the scheme is active or
accepting applications; lifecycle and application availability need verification.

Rules are trees scoped to a version: `and`/`or` require children, `not` requires
one child, and predicates cannot have children. Composite foreign keys prevent
cross-version parents and evidence associations. Deferred triggers reject cycles
and invalid arity at transaction commit. Build a complete tree in one transaction.
Predicates contain an attribute, explicit operator and JSON expected value;
numeric comparisons require JSON numbers, set membership requires arrays,
and `exists` requires a boolean. Store a unit and time basis where relevant.
The evaluator must validate domain-specific attributes, scalar types and units
against its vocabulary before use. Missing citizen values or `UNCERTAIN` rules
must produce uncertainty, never automatic eligibility. An uncertain rule requires
an explanation. No rule thresholds are supplied by these migrations.

Benefits, application routes, documents and translations each cite evidence.
Each evidence row cites an immutable snapshot and locator. Snapshot hashes
deduplicate content per source. `fetched_at`, publisher update time,
`last_checked_date`, and effective dates have distinct meanings. Rechecking or
correcting evidence creates a new evidence row rather than rewriting a citation.
Source policy status is metadata, not an automatic permission grant. Only ingest
from approved public exports, documented APIs, or written permission.

## Idempotent ingestion contract

1. Resolve a source by its exact original URL; retain redirect URL separately.
2. Use `(source_id, idempotency_key)` to claim a run. A conflict means resume or
   inspect the existing run, not start another worker. Keys must identify the
   input manifest and importer version; keep them stable across retries.
3. Insert snapshots with `ON CONFLICT (source_id, content_sha256) DO NOTHING`,
   then select the existing snapshot. Evidence deduplicates by snapshot/locator.
4. Resolve schemes by stable ID. Allocate version numbers while holding a lock
   on the scheme row; the unique constraint is a final duplicate safeguard.
5. Upsert child records by `(scheme_version_id, item_key)` or rule key only while
   draft. Never overwrite reviewed data. Complete a run with status and finish
   timestamp together. Commit related writes atomically.

The database enforces uniqueness; importer retry orchestration, authoritative
source review, translation quality, geographic hierarchy validation, and checking
for superseding notifications remain backend/reviewer responsibilities.
