# Phase 3C staging rehearsal

31 October 2026. Result: the prepared PMSBY draft successfully rehearsed locally.
No live Supabase connection or write was performed. No .env, migration, permission,
frontend or existing scheme data was changed; no dependency was added.

## Inputs and result

The inspected Phase 3B reports, `ingestion/verification.py`, existing validation
tools and all three migrations were reused. Inputs remain:

- `.phase3-output/phase3b/afe9609bc2b9a0db/draft.json` and its three captured sources.
- `.phase3-output/phase3b-evidence/pmsby-review-v2.json` research ledger.

The importer uses canonical JSON hashing for a source-scoped ingestion key; its
digest is `32430ea95579b268171fe51f907ffdc3553ba35901496c5d5c269fe5516b82cc`.
This serialization differs from Phase 3B directory hashing; both identify their
specified representation, and neither is a claim of human approval.

The real PMSBY run produced:

| Step | Result |
| --- | --- |
| Default dry-run | Planned 42 catalogue rows, version 1, all rolled back |
| In-memory commit | 42 catalogue rows plus one ingestion run and one local receipt |
| Exact repeat | `already_imported`, zero new rows |
| Publication | Version remains draft; no publication operation |

The full original payload is stored transactionally in a local-only receipt:
claims, dates, source register, original record, both conflicts, disabled rules and
bilingual review metadata are retained. Source bytes remain hash-checked local
artifacts; they are not fetched or uploaded. Closing PGlite discards the rehearsal
database, while the original ignored bundle remains intact. No real ingestion
receipt is written to Supabase.

## Implementation

- `ingestion/staging_validate.py`: reuses existing Python validation; checks capture
  hashes, URL/time attribution, original-record hash, preserved conflicts and
  one-scheme/one-version scope. No database or network module is used.
- `db-validation/staging-import.mjs`: local-only, default rollback, parameterized
  transactional inserts. Reuses organization/jurisdiction codes, source URLs,
  snapshot source/hash, evidence snapshot/locator and stable scheme identifiers
  only when content agrees. Remaps provisional UUIDs, allocates the next version
  after checking the expected maximum, never updates existing content, forces
  deferred constraints, and commits receipts atomically. Conflicting natural-key
  content and stale version previews abort. Exact repeats verify mapped rows.
- `db-validation/staging.test.mjs`: isolated synthetic regression cases, separate
  from the unchanged real PMSBY bundle; no fabricated government records.
- `PMSBY_REVIEW_CHECKLIST.md`: unapproved publication gates versus optional work.
- `PHASE3C_LIVE_IMPORT_RUNBOOK.md`: reproducible local commands and future approval,
  role, durable receipt, concurrency and rollback requirements.

## Validation

From `engine`:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test db-validation/catalog.test.mjs
node db-validation/staging.test.mjs
node db-validation/validate-draft.mjs .phase3-output/phase3b/afe9609bc2b9a0db/draft.json
node db-validation/staging-import.mjs .phase3-output/phase3b/afe9609bc2b9a0db/draft.json --rehearse-local
```

- All 39 existing Python tests passed, including FastAPI health/docs and Phase 2
  repository tests using mocks; no live database smoke test was invoked.
- All eight existing database tests passed, covering constraints, workflow,
  published-only reader access, client-role restrictions and migration replay.
- The isolated actual PMSBY payload constraint test passed.
- Nine new staging tests cover default rollback, local success, exact repeat,
  provenance/sidecar preservation, late SQL failure rollback, invalid references,
  capture corruption, version conflicts/new versions, existing-ID remapping,
  content conflicts/drift, unpublished/disabled invariants and blocked networking.
- Windows sandbox child-process/temporary-directory restrictions required rerunning
  affected tests with execution permission; they were not database failures.

## Remaining blockers

PMSBY is ready for independent human review and another local rehearsal, not
publication. Age-boundary/termination interpretation, cover-start amendment chain,
current application/forms/KYC, full policy scope and bilingual review remain open.
The four partial necessary conditions are still disabled; none produces a final
eligibility decision. See the checklist for all review gates.

The importer is safe for its implemented **local-only** scope. It cannot yet be used
for a remote write. A future adapter needs explicit target/bundle/version approval,
a separately authorized least-privilege writer, real RLS/concurrency testing and
durable receipt/artifact storage. The precise next step is human draft-only review
of this concrete bundle, then a separately authorized implementation/review of that
adapter. No writer credentials should be created or requested in this phase.
