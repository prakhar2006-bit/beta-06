# Fifteen-scheme preparation, isolated workflow and future import

**Handoff status:** live import completed by the backend owner. The requested
read-only SQL result confirmed 15 schemes, 15 draft-v1 rows, 63 evidence rows and
zero published versions. Commands below are retained for reproducibility, not an
instruction to reimport or reapprove the already completed transaction.

Run commands from `citizen-scheme-assistant/engine` unless stated otherwise.
Existing SUPABASE_DRAFT_IMPORT_RUNBOOK.md describes the unchanged importer and
unapplied `ops/draft_writer_PROPOSAL.sql` role/RLS proposal. This batch requires a
**new authorization**; the five-scheme digest must not be reused.

For the audited SQL Editor sequence, restrictive RLS fences, inherited PUBLIC
privilege checks, credential setup and complete verification query, read
`DRAFT_WRITER_PROVISIONING.md`. The SQL proposal is revised and remains unapplied;
never paste a password into SQL Editor. Provisioning fails closed on unrelated
application access rather than changing shared PUBLIC permissions automatically.

If provisioning previously failed on `public.rls_auto_enable`, use the corrected
proposal and verifier. Run `ROLLBACK;`, then the complete proposal, then the complete
verifier in the confirmed project's SQL Editor. The audit now recognizes only the
reviewed event-hook body/type/owner/search_path/bindings; callable RPCs and altered
lookalikes still fail. Do not revoke global PUBLIC grants or edit the Supabase hook.
See the exact rerun section in DRAFT_WRITER_PROVISIONING.md.

## Final deployment order

1. Project owner authorizes the restricted writer setup; execute the corrected
   `ops/draft_writer_PROPOSAL.sql` once in the confirmed project. It validates the
   real child FKs and aborts transactionally on unsafe effective permissions.
2. Run `ops/draft_writer_VERIFY.sql`, then set the writer password privately with
   interactive `psql \password` and enable the short login window as documented
   in DRAFT_WRITER_PROVISIONING.md. Do not change the FastAPI connection or .env.
3. Make the writer URL/CA available only to the private importer process. Run
   --check-target below; validate actual current versions against the plan. If
   versions/content differ, generate a fresh plan and obtain its approval.
4. After explicit approval of the exact final target, 15 IDs, digests and expected
   versions, execute the --commit command below once. Repeat the same approved
   command only for an idempotent retry after checking any uncertain outcome.
5. Verify 15 returned draft version IDs, successful receipts and evidence preservation;
   public listings must still omit drafts. Close the connection, disable writer
   LOGIN and remove its process credentials. No publication or execution approval
   is part of this operation.

The corrected role and writer preflight were tested with all 15 unchanged bundles:
15 drafts, 63 evidence rows, no duplicates on repeat, rollback on failure and no
published versions. Local result: `.phase3-output/catalog15-deployment-final-rehearsal.json`.
Final verification passed: 137 Python tests (including 14 importer tests), six
dedicated SQL security/FK tests, and the full 15-bundle rehearsal using the final
role proposal and writer preflight. No Supabase permissions/data were changed.

## Offline validation and review

The cached capture and collection directories already exist. Do not overwrite
them. To reproduce, choose a fresh output directory:

```powershell
.\.venv\Scripts\python.exe -m ingestion.catalog15 --captures .phase3-output/catalog15-captures --existing .phase3-output/phase3d/collection.json --output .phase3-output/FRESH-catalog15
.\.venv\Scripts\python.exe -m ingestion.postgres_import --collection .phase3-output/catalog15/collection.json --plan .phase3-output/catalog15-postgres-plan.json
.\.venv\Scripts\python.exe -m reviewer.preview --local-review --collection .phase3-output/catalog15/collection.json --output .phase3-output/FRESH-catalog15-review --as-of 2026-10-31
.\.venv\Scripts\python.exe tests/rehearse_postgres_import.py --collection .phase3-output/catalog15/collection.json --plan .phase3-output/catalog15-postgres-plan.json --output .phase3-output/FRESH-catalog15-rehearsal.json
```

Default importer dry-run does not connect or issue any SQL. Capturing is a separate
explicit `--capture-public-pib` mode, restricted to the ten inspected reusable
publications, bounded and serial. Do not collect myScheme pages without the written
authorization required by its terms. Do not use captured content as reviewed policy.

## Exact provisional plan

- Project `zqdcajmioiwtwtzaqgjt`.
- `aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres`.
- IDs `in-cen-000001` through `in-cen-000015`, all expected current version 0,
  target version 1, draft only.
- Plan SHA-256:
  `3da3943c7eb059dd3ea1ebccc8ae3414a2cb1fc9320cb90363edb73a873d0e6a`.
- Each complete content digest is in `.phase3-output/catalog15-postgres-plan.json`.
- Full sidecars/captures are archived at `.phase3-output/postgres-import/PLAN_SHA/`.

Live read-only inspection found no writer role and no published records. It could
not verify unpublished maxima. Approve writer provisioning/secure credentials and
read-only preflight first. The role is non-owner/NOBYPASSRLS, with scoped SELECT/
INSERT and the existing guard's narrow UPDATE(id) row-lock requirement. No changes
to scheme_api, migrations or RLS bypass are needed or authorized automatically.
The proposal is not a migration and has never been applied remotely.

After separately approved provisioning, inject `SCHEME_IMPORT_DATABASE_URL` and
`SCHEME_IMPORT_SSLROOTCERT` into the server process through a secure mechanism.
Use the writer's session-pooler login, not scheme_api/postgres/service_role. Do not
paste credentials into chat or put them in Vite configuration. Then:

```powershell
.\.venv\Scripts\python.exe -m ingestion.postgres_import --collection .phase3-output/catalog15/collection.json --plan .phase3-output/catalog15-postgres-plan.json --check-target
```

If every current version is zero and the owner explicitly approves this final
target/ID/digest/version set, the future draft-only write command is:

```powershell
.\.venv\Scripts\python.exe -m ingestion.postgres_import --collection .phase3-output/catalog15/collection.json --plan .phase3-output/catalog15-postgres-plan.json --commit --approve-plan-sha256 3da3943c7eb059dd3ea1ebccc8ae3414a2cb1fc9320cb90363edb73a873d0e6a --confirm-target zqdcajmioiwtwtzaqgjt/aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres
```

**Not executed.** If maxima or existing content differ, prepare a fresh plan with
the correct expected-versions JSON and obtain new approval. Never automatically
overwrite or increment around a conflict. Retain returned mapped UUIDs/receipts
and verify evidence counts and published-view exclusion. All 15 remain drafts;
do not grant this writer publication/review permissions.

## Controlled PMJJBY-shaped platform workflow

This fixture uses synthetic conditions and approvals **only in a separate app**,
under `pmjjby-workflow-fixture`. It is not complete government eligibility, and
the actual `in-cen-000001` remains unavailable. It exposes no live credentials or
database access. Bind only to loopback:

```powershell
.\.venv\Scripts\python.exe -m uvicorn pmjjby_workflow_fixture:create_app --factory --app-dir tests --host 127.0.0.1 --port 8011 --no-access-log
```

In another terminal from engine:

```powershell
node db-validation/pmjjby-http-workflow.mjs
```

This tests real frontend service/controller code over HTTP, not browser rendering.
This optional harness requires the separate Phase 5 frontend integration files;
those frontend working changes are not included in the backend-only handoff commit.
The backend Python and database regression suites have no dependency on them.
For a manual isolated browser test, start a **second frontend process** from
`frontend` with a process-scoped fixture base URL; do not change production `.env`:

```powershell
$env:VITE_API_BASE_URL='http://127.0.0.1:8011'
npm.cmd run dev -- --host 127.0.0.1 --port 3011 --strictPort
```

Open `http://localhost:3011/screening?scheme_id=pmjjby-workflow-fixture`. Confirm
the SIMULATED scheme title, complete one all-yes journey in each language, one
first-answer-no journey and an all-unknown journey. Check skip/back/clear, source
and fallback notices, synthetic checklist, and absence of a real application URL.
For voice, grant microphone access only intentionally, review recognized text and
confirm it explicitly. Actual speech/browser testing remains unperformed because
both available automation runtimes failed to initialize. Stop both fixture
processes after the test. Production ports 8001 and 3001 stay unchanged.

After real PMJJBY policy/documents/translations/guidance are genuinely reviewed,
prepare its exact version for explicit publication approval. Only after publication
and server execution/guidance attestations should the same browser sequence be
repeated against the production published catalogue. Synthetic fixture success is
not authorization to replace those gates.
