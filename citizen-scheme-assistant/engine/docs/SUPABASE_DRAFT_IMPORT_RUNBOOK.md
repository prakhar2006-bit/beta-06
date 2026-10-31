# Five-scheme PostgreSQL draft import

Status: implemented and rehearsed in isolated PGlite. **Not run against Supabase.**
No changes to migrations, API credentials/connection, live roles, policies or data.
No new package dependency. This tool is not imported by FastAPI.

## Approval package

Prepared from the existing API configuration's non-secret host/project identity,
without using its credentials or connecting:

- Project: `zqdcajmioiwtwtzaqgjt`
- Target: `aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres`
- Plan: `engine/.phase3-output/five-scheme-postgres-plan.json`
- SHA-256: `26277ee834c25bd2ae6f5611007a4f911fe14599327232a420a2aaf648174902`
- Exactly `in-cen-000001` through `in-cen-000005`, expected current version **0**,
  proposed new version **1**, status **draft**, no publication or activation.
- The plan contains all five full payload digests. Version 0 is an expectation,
  not a claim about the live database; the transaction validates it.

Explicit owner approval is required for **both** provisioning any missing writer
permissions and committing the exact plan above. Import approval does not approve
policy, translations, guidance, publication or execution. The CLI flags are an
operator confirmation mechanism, not a substitute for owner authorization.

## Permissions and credentials

`ops/draft_writer_PROPOSAL.sql` is an unapplied, separately reviewable proposal,
not a migration or an automatically executed file. It has been tested only in
ephemeral PGlite. It creates a NOLOGIN role and scoped RLS policies; an authorized
administrator would separately provision secure LOGIN credentials. Never execute
it without permission. It intentionally fails if the role/policies already exist:
inspect them rather than replacing or broadening them.

The writer must be `scheme_draft_importer`, non-owner, non-superuser,
NOBYPASSRLS/NOCREATEROLE/NOCREATEDB/NOREPLICATION. It needs schema usage,
SELECT/INSERT on the existing 15 base tables and SELECT on published_versions.
The existing child guard uses `SELECT ... FOR UPDATE`, so narrowly scoped
`UPDATE(id)` on scheme_versions plus a draft-only UPDATE RLS policy is necessary.
No UPDATE permission on status/review/content columns, no DELETE/TRUNCATE and no
scheme_api grants are proposed. The importer verifies these restrictions.

Inject these **server-side process environment** values securely (not command-line
secrets, frontend variables, committed files or chat messages):

| Variable | Value |
| --- | --- |
| `SCHEME_IMPORT_DATABASE_URL` | PostgreSQL URL for the separate writer; session-pooler username `scheme_draft_importer.zqdcajmioiwtwtzaqgjt` |
| `SCHEME_IMPORT_SSLROOTCERT` | Existing trusted Supabase CA certificate file's absolute path |

The importer does not load or change `.env`, does not use DATABASE_URL, and never
uses scheme_api, postgres, service_role or an owner connection. The URL must have
no query overrides and must match the plan's host/port/database/project. TLS uses
`verify-full`; session pooling/direct PostgreSQL is supported. Use session pooler
5432, not a transaction-pooler setup for this administrative operation.
Current process: separate writer URL not configured. Live role existence/grants
have not been inspected. Secure provisioning/approval remains a real blocker.

## Commands (from engine)

Offline dry-run, default: validates bundles, captures, conflicts, plan digests and
archives them; **no connection and no SQL, even if writer credentials are set**:

```powershell
.\.venv\Scripts\python.exe -m ingestion.postgres_import --collection .phase3-output/phase3d/collection.json --plan .phase3-output/five-scheme-postgres-plan.json
```

After approved writer provisioning, inspect current versions through a genuinely
read-only transaction (does not rehearse INSERT then roll back remotely):

```powershell
.\.venv\Scripts\python.exe -m ingestion.postgres_import --collection .phase3-output/phase3d/collection.json --plan .phase3-output/five-scheme-postgres-plan.json --check-target
```

If all versions match and the owner explicitly approves the target, five IDs,
digests and expected versions, the future write command is:

```powershell
.\.venv\Scripts\python.exe -m ingestion.postgres_import --collection .phase3-output/phase3d/collection.json --plan .phase3-output/five-scheme-postgres-plan.json --commit --approve-plan-sha256 26277ee834c25bd2ae6f5611007a4f911fe14599327232a420a2aaf648174902 --confirm-target zqdcajmioiwtwtzaqgjt/aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres
```

That command has **not** been executed. Approval flags are checked before any
connection. To prepare a new plan, use a fresh output path with `--prepare
--target-host HOST --project-ref REF`, optional `--target-port` and
`--target-database`, and `--expected-versions path.json` containing the exact
scheme→current-maximum-version mapping. Never overwrite an existing plan or
automatically increment after a conflict; inspect and obtain approval again.

## Transaction and provenance guarantees

- Existing Python collection/bundle validation is reused before connecting.
  Invalid references, duplicate identifiers, changed captures, enabled rules and
  non-draft versions fail validation.
- A single SERIALIZABLE transaction covers the batch. Ordered advisory locks,
  unique constraints and expected versions protect against races. Serialization,
  timeout, permission or content conflicts abort; no automatic blind retry.
- Parameterized INSERT/SELECT only. Natural identifiers are resolved and exact
  supplied columns compared; no UPSERT/UPDATE or overwrite. New version numbers
  are assigned under transaction locks, not copied from provisional draft IDs.
- UUIDs are deterministically mapped; rule parents and evidence/FKs are remapped.
  Existing ingestion_runs stores per-scheme successful receipts bound to the
  payload and full approval plan digest. Repeating the same plan checks every
  expected row and child count and writes zero rows. Missing/changed content,
  extra children or a later scheme version cause rejection.
- Every version remains draft. Published-view exclusion and immediate constraints
  are checked before commit. No rules are activated; sidecar disabled flags stay
  false and the server execution approval manifest is unchanged.
- The immutable local archive at `.phase3-output/postgres-import/PLAN_SHA/`
  retains the original collection, full draft payloads, 17 conflicts, research
  ledger, bilingual child drafts and permitted captures. Snapshot artifact paths
  remain relative to their draft's directory. Preserve this archive securely and
  back it up with its digest; copying SQL rows alone loses the review package.
  The existing schema has no full sidecar column; no misleading source rows or
  new tables have been created to hide that limitation.
- On uncertain network failure around COMMIT, do not assume rollback. Re-run
  read-only verification and the same approved plan: the durable receipt and
  row checks distinguish a completed import. Sanity-check outputs do not print
  connection strings or raw database exception text.

## Local verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_postgres_import.py -v
.\.venv\Scripts\python.exe tests/rehearse_postgres_import.py --collection .phase3-output/phase3d/collection.json --plan .phase3-output/five-scheme-postgres-plan.json --output .phase3-output/FRESH-rehearsal.json
```

The second command uses the exact PostgreSQL import SQL and proposed role/RLS
in ephemeral PGlite. No network driver connection is permitted. Its `committed`
field means committed **only inside the isolated local test database**.

After a separately approved real import, retain the command's returned version
UUIDs; verify five draft versions, five successful receipts and zero published
rows for those UUIDs using the writer's read-only check/audited admin query.
`GET http://127.0.0.1:8001/api/v1/schemes` must still omit these drafts.
Publication requires the independent checklist in FIVE_SCHEME_IMPORT_STATUS.md.
Revoke the temporary writer LOGIN/access after the approved import window.
