# Phase 3B pilot readiness

The PMSBY local draft is ready for human review and local staging rehearsal, not
publication or an unapproved remote import. No live database was accessed or
modified. The existing migrations, permissions, API and .env are unchanged.

## Files and workflow

- `ingestion/verification.py` extends the existing offline `ingestion.prepare`
  helpers. It reads the Phase 3A manifest, binds a research ledger to an exact
  original-record hash, preserves original assertions/conflicts/source register,
  validates source snapshot hashes and attribution, and emits a schema-mapped draft.
- `tests/test_verification.py` uses synthetic fixtures, never government records
  as fictional real data or a live database.
- `db-validation/validate-draft.mjs` applies the real migrations only to a fresh
  in-memory PGlite database, inserts the mapped rows there, forces deferred
  constraints, confirms zero published versions and rolls back. It never reads
  .env or connects to Supabase.
- Research ledger, captured sources, draft rows and bilingual sidecars remain
  under ignored `.phase3-output/`. No new dependency was installed.

The resulting pilot draft is
`.phase3-output/phase3b/afe9609bc2b9a0db/draft.json` with captured source files in
its `snapshots/` directory. Research inputs are in
`.phase3-output/phase3b-evidence/pmsby-review-v2.json` and its three original source
captures. Do not execute any scripts from output.zip. The local research assembly
script in this directory was newly written for this phase, not supplied by that
archive; the repeatable preparation command below needs only its JSON ledger.

From `engine`, prepare into a fresh output root (existing output is never replaced):

```powershell
.\.venv\Scripts\python.exe -m ingestion.verification --manifest .phase3-output/verified/b6c4262434a8dd3e/manifest.json --ledger .phase3-output/phase3b-evidence/pmsby-review-v2.json --output-root .phase3-output/phase3b-new-run --dry-run
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test db-validation/catalog.test.mjs
node db-validation/validate-draft.mjs .phase3-output/phase3b/afe9609bc2b9a0db/draft.json
```

Inputs and outputs are deterministic: timestamps originate in fixed source-capture
metadata, not the preparation run. UUIDv5 identifiers are provisional local keys,
not evidence of existing database identity. Duplicate IDs/codes/URLs/item keys,
unknown database columns, unresolved FKs, bad snapshot attribution/hash, mismatched
input-record hash, enabled rules and reviewed/published target versions are rejected.
The Python structural guards complement, not replace, the actual SQL constraint test.

## Schema mapping and limitations

The payload has rows for organizations, jurisdictions, official_sources,
source_snapshots, evidence, schemes, scheme_versions, scheme_jurisdictions,
translations, benefits, required_documents, eligibility_rules and rule_evidence.
It deliberately has no application_routes or ingestion_runs rows: an actual
provider mode/transaction URL is not verified, and no import has run.

All source-backed benefit/evidence rows use captured PIB sources. DFS was read
for verification, but its [policy](https://www.financialservices.gov.in/web-policies)
requires reproduction permission; no DFS raw snapshot is included. The PIB
[copyright policy](https://www.pib.gov.in/ContentPage.aspx?menuid=132&reg=48&lang=2)
permits attributed reuse of its own material, excluding third-party content.
Copyright/access permission and factual policy verification are distinct.

Version status=draft; reviewed_at/reviewer_reference/published_at and the version's
human verification date stay null. Claim checked_date records AI-assisted source
inspection, not human approval. Effective dates remain null where not established;
the 2022 premium effective date is not assigned as the effective date of the whole
scheme version. The scheme lifecycle remains unknown rather than inferring current
application availability from a dated anniversary release.

All original archive fields and both conflict groups remain in the payload. The
premium conflict has a narrowly supported chronology, while the cover-start
amendment chain and upper-age semantics remain unresolved. Rules are partial
necessary conditions and remain disabled even where a claim is corroborated.
Official Hindi fields are explicitly identified; combined translation rows and
all newly drafted content still require review. Bilingual child text has no
existing database column and is retained as a sidecar; Phase 2 will not magically
serve it. No schema change or extra column is introduced.

## Precise next step for a safe staging import

Have an independent human policy/bilingual reviewer approve or correct the
concrete ledger and rendered content, explicitly retaining the unresolved-age
and provider-document blockers. If only draft staging is desired, the reviewer
may approve an incomplete draft as such; it must not be promoted to reviewed or
published. Obtain explicit authorization for that specific staging target and
draft-only import preview through a separately authorized writer workflow.

Before writing, that future writer must resolve existing organization codes,
source URLs, jurisdiction code, stable_id and version numbers under transaction
locks. Remap provisional UUIDs to existing rows, allocate a new draft version
when appropriate, and use manifest/source-scoped idempotency keys. Never blindly
insert version 1 or update an existing reviewed record. Validate all captured-byte
hashes, permissions and references again; review a rollback plan and retain the
full sidecar. Do not use scheme_api, whose role stays read-only. No writer or
privileged credential collection is implemented in this task.

Publication additionally requires resolving the full policy/amendment/date
questions, latest forms, bilingual review, and complete reviewed rule scope.
Structural validation alone does not satisfy those gates.
