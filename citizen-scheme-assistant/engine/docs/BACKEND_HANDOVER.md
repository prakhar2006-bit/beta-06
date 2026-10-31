# Backend handover — Citizen Scheme Assistant / YojanaMitra

Audited 31 October 2026 on `chore/backend-collaboration-guards`, based on commit
`e79314da016518edf21ff9b894b75ecc72a5b967`. This document supersedes older phase
reports for setup and current backend readiness. No commit, push, publication,
database permission change or frontend change was performed for this audit.

## 1. Completion assessment

**Ready for a local hackathon API demonstration and integration, with the existing
catalogue artifacts. Not production-ready and not an officially approved eligibility
service.** There are two intentionally separate API modes:

| Area | Implemented and verified | Remaining boundary |
| --- | --- | --- |
| FastAPI startup | Real running HTTP server, health, Swagger and OpenAPI passed | Deploying, HTTPS, operational monitoring and load testing are not completed |
| Published catalogue | PostgreSQL read-only integration works; published-only mode returns zero published schemes | Local demo mode explicitly bridges the same paths to 15 unverified local records; no records are published |
| Full local catalogue | 15 actual bundles validated, with 63 unique evidence rows and draft-only gates | Full bundles/captures are Git-ignored and must accompany a fresh checkout |
| Preliminary screening | All 15 guides work deterministically in English and Hindi; original five preserved | Ten additional guides remain incomplete and require verification even when included checks pass; no publication approval |
| Adaptive questions | Known failure stops early; unknown/skip are distinct; answer changes and stale-state checks work | The preliminary five use necessary AND conditions and provider-only exceptions, not a general benefits entitlement adjudication |
| Reviewed policy engine | Typed AND/OR/NOT evaluation, explicit unknowns, bounded comparisons, citations and approval gates tested | Execution approval manifest is empty: no real scheme can return approved `ELIGIBLE` through this provider |
| Result guidance | All 15 local journeys return preliminary explanations and provider guidance | Missing documents/URLs are explicit unavailable sections; supported additional checklists are partial |
| Privacy/security | No citizen database writes; restricted SQL reader; verified TLS; sanitized errors; bounded state | No production rate limiting, comprehensive penetration test or authentication integration is claimed |
| Frontend integration | HTTP contracts and CORS verified for port 3001 | Current frontend/auth/Supabase-JS behavior was not built, changed or browser-tested in this audit |

The recorded government-source checks are dated **2026-10-31**. This audit tested
the implementation and preserved evidence; it did not perform a new legal/policy
verification or invent human approvals. All 28 original draft proposals remain
`UNCERTAIN` and disabled by their existing review/execution gates. Hindi guide
wording is project-authored, not an official translation.

## 2. Architecture and files

```text
citizen-scheme-assistant/
  data/schemes/preliminary-screening.json  # five server-owned advisory guides
  contracts/                             # existing shared schemas; unchanged
  engine/
    main.py                              # app, CORS, routers, /health
    app/api/routes/                      # published API and opt-in /demo API
    app/schemas/                         # strict requests, state, typed public responses
    app/eligibility/engine.py            # pure deterministic reviewed-rule evaluator
    app/eligibility/provider.py          # published-policy + execution approval boundary
    app/eligibility/questionnaire.py     # approved-policy adaptive orchestration
    app/eligibility/preliminary.py       # separate source-based likely/unknown advice
    app/eligibility/data/preliminary-additions.json # ten incomplete backend-owned guides
    app/eligibility/results.py           # published guidance attestations and presentation
    app/eligibility/execution_approvals.json  # currently zero approvals
    app/db/                              # parameterized, published-view-only repository
    app/core/                            # environment, CORS and sanitized errors
    ingestion/                           # validation and separately gated draft importer
    reviewer/                            # local review tools, not public endpoints
    db-validation/                       # isolated PGlite tests, fixtures and bridge
    supabase/                            # existing configuration/migrations; unchanged
    ops/                                 # existing reviewed provisioning proposals; unchanged
    tests/                               # unittest API, engine, ingestion and security tests
    database_smoke.py                     # opt-in read-only TLS/role verification
    .env.example                         # placeholders only; do not overwrite a filled .env
    .phase3-output/catalog15/             # existing private local catalogue, not in Git
```

No LLM makes an eligibility decision. Questionnaire state is held by the client;
there is no account/session database for citizen answers. The backend resolves its
own definitions and re-evaluates the submitted state. A fingerprint detects stale
definitions; it is not a signature, authentication token or proof that answers are true.

## 3. Prerequisites and exact Windows setup

Verified runtime: **Python 3.14.7**. Runtime requirements in `requirements.txt`:
FastAPI 0.162.0, Uvicorn 0.54.0, psycopg/binary 3.3.6 and python-dotenv 1.2.4.
Tests additionally use HTTPX (`requirements-test.txt`; installed 0.28.1) and the
standard-library unittest runner. Installed Pydantic is 2.14.2 and Starlette 1.10.0.
`pip check` passed. Node is only needed for isolated database tests, not HTTP serving;
use Node >=22 (verified 24.20.0), with PGlite 0.5.13 from the backend lockfile.

Open PowerShell at the existing repository root. Do not reset or pull over another
person's uncommitted work. These commands touch only the backend environment:

```powershell
git status --short --branch
cd citizen-scheme-assistant\engine
if (-not (Test-Path .venv\Scripts\python.exe)) { py -3.14 -m venv .venv }
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-test.txt
.\.venv\Scripts\python.exe -m pip check
npm.cmd ci --ignore-scripts --prefix db-validation
```

Do not recreate an existing `.venv` blindly. Activation is unnecessary. If the
proposed repository CI files have also been merged, the same dependency versions
can be constrained with `-c ../../.github/ci/constraints.txt` during installation.
Do not install frontend dependencies as part of backend setup.

## 4. Catalogue portability — required for the complete local demo

This machine has `.phase3-output/catalog15/collection.json` and all its referenced
drafts, ledgers and source captures. The archive validates as **15 schemes, 15 draft
versions, 63 unique evidence rows and 28 UNCERTAIN proposals**. It is not tracked
in Git. A fresh clone alone does **not** contain the complete runnable catalogue.

To run catalogue discovery on another computer, the backend owner must transfer
the **existing `catalog15` directory and its entire layout** through an approved
private team channel. Place it at `engine/.phase3-output/catalog15/`. Do not include
`.env`, certificates, writer settings, the rest of `.phase3-output`, `.venv`, or
unrelated ZIP files. Do not commit raw archives or re-scrape restricted sites to
work around a missing transfer. Keep original provenance and attribution.

From `engine`, validate the received directory without database access:

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from ingestion.batch import validate_collection; b=validate_collection(Path('.phase3-output/catalog15/collection.json')); ids=[x['payload']['rows']['schemes'][0]['stable_id'] for x in b]; assert len(ids)==len(set(ids))==15; assert set(ids)=={f'in-cen-{i:06}' for i in range(1,16)}; print('15 unique validated draft bundles')"
```

A missing or invalid archive produces `503 DEMO_DATA_UNAVAILABLE`; there is no fake
fallback catalogue. All fifteen questionnaires can operate directly from the
tracked original guide file plus backend extension without that archive, but catalogue-driven frontend
discovery needs the archive on its local backend. The owner's already-running
loopback service is usable on the owner's computer, not another teammate's machine.
For a remote judge, demonstrate on that machine or screen-share; do not bypass the
local-only guard to expose advisory endpoints over the network.

## 5. Startup, ports and environment modes

For the **current hackathon journey**, from `engine`:

```powershell
$env:SCHEME_APP_ENV='development'
$env:SCHEME_DEMO_ENABLED='1'
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload --no-access-log --no-proxy-headers
```

**Local catalogue bridge, verified 31 October 2026:** with both flags above and a
loopback request, `GET /api/v1/schemes` and `/api/v1/schemes/{id}` now return the
existing `/api/v1/demo/schemes` responses. The list keeps `items,total,limit,offset,
has_more` and adds explicit `catalog_mode: DEMO_UNVERIFIED`. Records retain
`is_demo: true`, `publication_status: draft`, `verification_status: UNVERIFIED`,
draft translation status and `published_at: null`. Local catalogue identity is a
stable scheme ID, not a claim to a database UUID or published version.

The same local gate bridges `/api/v1/questionnaire/start`, `/next`, `/answer` and
`/api/v1/results/explain` to the existing preliminary handlers. Thus the current
frontend can use its ordinary API paths without any frontend source/config change.
The explicit `/api/v1/demo/*` paths remain supported. `screening_available` and the
new `preliminary_screening_enabled` identify all fifteen working guides. The ten
additions are intentionally incomplete and never produce `ELIGIBLE_LIKELY`.
See [PRELIMINARY_SCREENING15.md](PRELIMINARY_SCREENING15.md) for exact checks,
official evidence, unresolved conditions and real HTTP verification commands. Meanwhile,
`eligibility_execution_enabled` remains **false**: it refers to complete reviewed
policy execution, not the separate preliminary mechanism. `/api/v1/eligibility/evaluate`
continues to use its unchanged trusted published-policy provider in every mode.

Outside the shared explicit-development/loopback gate, the ordinary paths use
only their existing published repository and reviewed provider. A failed local
bundle/freshness check returns an error, never a database or fabricated-data fallback.
The local-mode response DTOs are the existing `/demo` shapes, including preliminary
status enums and guidance text objects; the strict published OpenAPI response
models remain unchanged. Do not interpret those models as publication assertions
about the explicitly labelled local-mode responses. Restart an existing non-reload
server to load this change; changing files alone does not update that process.

Stop an older server gracefully in its owning terminal before replacing it. Do not
kill unknown processes or start competing servers on 8001. Bind the demo only to
loopback; do not put it behind a public proxy. The demo guard also checks the client
and request hostname. On another computer, `127.0.0.1` refers to that computer.

- API base: **http://127.0.0.1:8001** (also use http://localhost:8001).
- Health: **http://127.0.0.1:8001/health**.
- Swagger: **http://127.0.0.1:8001/docs**.
- OpenAPI: **http://127.0.0.1:8001/openapi.json**.

Expected health response, with no database connection:

```json
{"status":"ok","service":"Scheme Navigator","version":"0.1.0"}
```

For published-only operation, remove the demo flag and restart:

```powershell
Remove-Item Env:SCHEME_DEMO_ENABLED -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001 --no-access-log
```

This disables `/api/v1/demo/*` with 404; it does not approve or publish anything.
The public catalogue then remains empty until an authorized publication occurs.

| Variable | Requirement and purpose |
| --- | --- |
| `SCHEME_APP_ENV=development` | Required with the flag below for local advisory endpoints |
| `SCHEME_DEMO_ENABLED=1` | Explicit local advisory opt-in; absent/other value disables it |
| `CORS_ORIGINS` | Optional comma-separated exact frontend origins. Defaults now include localhost and 127.0.0.1 ports 3001, 3000 and 5173. An explicit setting replaces defaults |
| `DATABASE_URL` | Required only for PostgreSQL-backed published endpoints; server-side restricted reader connection |
| `DATABASE_SSL_ROOT_CERT` | Existing absolute CA file path for certificate-verified TLS |
| `DATABASE_EXPECTED_USER=scheme_api` | Required restricted runtime role, verified against actual PostgreSQL identity |
| `SUPABASE_PROJECT_REF` | Optional integration/admin CLI target identifier; not required to serve HTTP |
| `SCHEME_IMPORT_DATABASE_URL`, `SCHEME_IMPORT_SSLROOTCERT` | Administrative importer only. Never needed by FastAPI, frontend developers or this demo |

`engine/.env` is loaded with `override=False`; explicit process settings take priority.
Only the backend owner should create a filled `.env` from the placeholder example.
Never overwrite an existing `.env` or commit filled settings. The local advisory
journey needs no database credentials. Missing database settings produce sanitized
503 responses on DB-dependent endpoints while health and local advice remain usable.

## 6. Database requirements and observed state

The existing PostgreSQL/Supabase migrations, views, roles and RLS must already be
provisioned by the backend/database owner. No teammate setup command in this handover
applies migrations, provisions a writer or imports/publishes records.

FastAPI accepts only the expected `scheme_api` login, reader membership, a CA file
and `sslmode=verify-full`. It rejects privileged runtime roles and unexpected base
table access. Each request uses a read-only repeatable-read transaction, bounded
timeouts and rollback. Queries use parameters and published views. Pooler connection
strings can use `scheme_api.PROJECT_REF`; the actual database identity must still
be `scheme_api`. Never use `postgres`, a service role key or an importer writer.

Observed in the initial audit before the local-path bridge: `/api/v1/meta/health/db` returned **200**, and
`/api/v1/schemes` returned **200 with total 0**. Earlier owner SQL verification
reported 15 imported draft-v1 records and 63 evidence rows. The API reader cannot
count private base-table drafts, so that historical private-row count was **not
independently re-queried** in this audit. Local bundles were freshly validated.

Optional read-only smoke test, only for the owner with a configured private `.env`:

```powershell
.\.venv\Scripts\python.exe -c "from app.core.config import load_environment; load_environment(); from database_smoke import main; raise SystemExit(main())"
```

`database_smoke.py` intentionally does not load `.env` itself. The wrapper above
does so explicitly without printing configuration. Empty published views are a
successful connection check. Do not weaken TLS or RLS if the check fails.

## 7. All fifteen schemes and current implementation status

All fifteen local bundle versions are draft/unpublished; no execution approvals
exist for the production published-policy provider.

| Stable ID | Scheme | Local preliminary questionnaire | Normal path / checklist entries |
| --- | --- | --- | --- |
| in-cen-000001 | PMJJBY | Working, en/hi | 4 questions / 3 document entries |
| in-cen-000002 | PMSBY | Working, en/hi | 4 / 3 |
| in-cen-000003 | PM-SYM | Working, en/hi | 9 / 3 |
| in-cen-000004 | PMUY | Working, en/hi; verification required | 4 / 5 partial |
| in-cen-000005 | IGNOAPS | Working, en/hi; verification required | 2 / unavailable |
| in-cen-000006 | PM-KISAN | Working, en/hi; verification required | 3 / 2 partial |
| in-cen-000007 | Atal Pension Yojana | Working, en/hi | 6 / 3 |
| in-cen-000008 | Sukanya Samriddhi Account Scheme | Working, en/hi | 6 / 4, including a conditional exception entry |
| in-cen-000009 | PMAY–Gramin | Working, en/hi; verification required | 5 / unavailable |
| in-cen-000010 | Ayushman Bharat PM-JAY | Working, en/hi; alternative routes retained | 1 / unavailable |
| in-cen-000011 | PM Vishwakarma | Working, en/hi; verification required | 6 / 1 partial |
| in-cen-000012 | PM SVANidhi | Working, en/hi; verification required | 2 / 1 partial |
| in-cen-000013 | PM MUDRA Yojana | Working, en/hi; lender verification | 2 / unavailable |
| in-cen-000014 | PM Surya Ghar | Working, en/hi; current-rule verification | 4 / 2 partial |
| in-cen-000015 | Kisan Credit Card | Working, en/hi; lender verification | 1 / 1 conditional |

Question counts are observed full paths, not fixed UI progress targets. Decisive
failures or provider-only exceptions can stop after one question. Source-backed
benefits, document and application information for the five guides are available;
these are not official approval attestations or guarantees of complete current
bank-specific paperwork. Links marked `information` are reference/forms guidance,
not online application submission links. Follow the returned `link_kind`.

## 8. API endpoints and response contracts

### Published/reviewed namespace — database and approval gated outside local demo mode

| Method and endpoint | Input / behavior |
| --- | --- |
| `GET /health` | Liveness only, independent of PostgreSQL |
| `GET /api/v1/meta/languages` | English and Hindi metadata |
| `GET /api/v1/meta/health/db` | Restricted read-only DB reachability; 503 if unavailable |
| `GET /api/v1/schemes` | `lang=en|hi`, optional `search`, `level=central|state|ut|local`, `limit=1..100`, `offset>=0` |
| `GET /api/v1/schemes/{scheme_id}` | `?lang=en|hi`; unpublished/missing record returns 404 |
| `POST /api/v1/eligibility/evaluate` | `{scheme_id,answers,language}`; trusted provider only |
| `POST /api/v1/questionnaire/start` | `{scheme_id,language}` |
| `POST /api/v1/questionnaire/next` | `{state}` |
| `POST /api/v1/questionnaire/answer` | `{state,question_id,action,value}` |
| `POST /api/v1/results/explain` | `{state}`; re-evaluates server-side |

Actual published-only catalogue response (demo disabled or outside the local gate):

```json
{"items":[],"total":0,"limit":20,"offset":0,"has_more":false}
```

Example published-provider evaluation request:

```json
{"scheme_id":"in-cen-000001","answers":{},"language":"en"}
```

It currently returns `status: "NEEDS_VERIFICATION"`, no approved rule version and
`RULE_SET_UNAVAILABLE` in review blockers. Do not replace this with a simulated
approved result. `ELIGIBLE` is reserved for a complete reviewed, applicable,
published and execution-approved rule set; the current manifest has zero entries.

### Local advisory namespace — current hackathon journey

Use these endpoints **together**, or their ordinary-path aliases while the shared
local demo gate is active. Do not mix preliminary states/status enums with
published-only mode; discard the current state when changing modes:

| Endpoint | Input / important response fields |
| --- | --- |
| `GET /api/v1/demo/schemes?lang=en` | `items,total,limit,offset,has_more`; actual total 15, all items with `screening_available=true` |
| `GET /api/v1/demo/schemes/{id}?lang=hi` | Overview, benefits, entry conditions, documents, guidance, sources and language metadata |
| `POST /api/v1/demo/questionnaire/start` | `{scheme_id,language}` |
| `POST /api/v1/demo/questionnaire/next` | `{state}`; refresh/re-evaluate, including a language change |
| `POST /api/v1/demo/questionnaire/answer` | `{state,question_id,action,value}` |
| `POST /api/v1/demo/results/explain` | `{state}`; must be completed; returns explained preliminary result and guidance |

Start example:

```json
{"scheme_id":"in-cen-000001","language":"en"}
```

Actual response excerpt (state and other fields omitted here for readability):

```json
{
  "completed": false,
  "current_question": {
    "question_id": "age",
    "answer_type": "integer",
    "text": "What is your age in completed years on the day you plan to join?",
    "content_language": "en"
  },
  "progress": {"answered":0,"unknown":0,"skipped":0,"remaining":4},
  "evaluation": {"status":"NEEDS_VERIFICATION","scope":"preliminary_only"}
}
```

Always retain the **complete returned `state`**, including `state_version`,
`scheme_id`, `language`, `answers`, `skipped` and `policy_fingerprint`. Never
construct a fingerprint or submit client rules, eligibility status or approvals.
An answer operation is `{state: returnedState, question_id: current.question_id,
action: "answer", value: 30}`. `null` means explicitly unknown; it is not false.
For `skip` or `clear`, **omit `value` entirely**. Boolean fields need JSON booleans;
age needs an integer, not a quoted number; income accepts the validated decimal
format and explicit monthly-individual semantics from the question.

Questionnaire responses include `state,current_question,completed,completion_reason,
progress,missing_information,evaluation`. Advisory responses also supply readable
`field_labels` and `missing_information_labels`. Completion is not a fixed number
of answers: it can mean a likely result or that provider verification is necessary.

Results include `scheme_name,eligibility_status,explanation,assessment_notice`,
condition-level results, missing information, `benefits,required_documents,
application_guidance,official_application_urls,sources,last_verification_date`.
Text objects contain `text,content_language,translation_fallback` and provenance
metadata. Guidance sections contain `status,message,items`. An actual normal PMJJBY
path returned `ELIGIBLE_LIKELY`, three document entries and one official information
link; an early age failure returned `NOT_ELIGIBLE_LIKELY`; the uncertain boundary
returned `NEEDS_VERIFICATION`. None is government approval.

The demo endpoints currently return dictionaries rather than fully typed OpenAPI
response models. Swagger documents their typed requests but is not a complete
schema for every advisory response field. The examples above and existing journey
tests are important; no new contract was silently introduced in this audit.

| Error | Meaning / integration behavior |
| --- | --- |
| `404 DEMO_UNAVAILABLE` | Demo flags or loopback guard not satisfied |
| `404 SCREENING_UNAVAILABLE` | Unknown or unsupported scheme identifier; do not invent questions |
| `409 POLICY_CHANGED` | Discard old state and restart |
| `409 QUESTION_NOT_PENDING` | Only answer the pending question or edit a prior answer |
| `409 QUESTIONNAIRE_INCOMPLETE` | Finish relevant questions before requesting a result |
| `422 INVALID_REQUEST`, `INVALID_ANSWERS`, `INVALID_STATE` | Correct types/state; do not treat invalid data as false |
| `503 DEMO_DATA_UNAVAILABLE` | Local catalogue archive absent or invalid |
| `503 PRELIMINARY_REVIEW_REQUIRED` | Source review is outside its freshness window |
| `503 DATABASE_UNAVAILABLE`, `DATABASE_TIMEOUT`, `DATABASE_QUERY_FAILED` | DB-dependent request failed safely; do not bypass TLS or RLS |

Errors use `{"error":{"code":"...","message":"..."}}`, sometimes with sanitized
field names. They do not echo submitted values or connection strings. Citizen
questionnaire/result responses and corresponding errors use `Cache-Control: no-store`.

## 9. Adaptive questions, language and frontend integration

1. Discover a scheme and check `screening_available` before starting local advice.
2. Render `current_question` using `answer_type`, `allowed_values` and language
   metadata. Ask no questions of your own and perform no eligibility logic in React.
3. Submit one answer, skip or unknown disposition with the returned state.
4. Replace the state/question with the server response. Do not re-ask unknown or
   skipped questions automatically. A previous answer can be changed/cleared.
5. Stop on `completed=true`; always permit a verification outcome. Call explain
   with that state and render the checklist, sources and provider instructions.
6. Language changes use `/next` with the current state and `language` changed to
   `en` or `hi`, then re-request explanation for a completed state. Keep answer values.

The generic reviewed engine supports AND/OR/NOT short-circuit relevance and
conflicting-rule detection. The advisory guides use mandatory AND checks,
shared strict comparison primitives and explicit manual exceptions. Missing
income/age, skipped answers and unresolved exceptions cannot produce likely eligibility.

All fifteen local guides' questions, descriptions, result messages and guidance
have English and Hindi wording. The added ten guides' translations are not human-approved.
The published guidance service uses reviewed translations and labelled English
fallback; do not apply that review claim to project-authored advisory wording.
Errors are machine codes with English developer messages; translate them in the UI.
Original official document titles can remain in their source language.

Backend base URL for teammates is `http://127.0.0.1:8001`; CORS supports
`http://localhost:3001` and `http://127.0.0.1:3001`. Frontend teammates need **no
database, importer, admin or service-role credentials**. Browser requests use JSON
and do not require credentialed cookies. The backend has no user/login/JWT/profile
API; frontend authentication does not automatically authorize backend operations.

For the existing Vite development integration, the frontend team can set process
variables `VITE_API_BASE_URL=http://127.0.0.1:8001` and
`VITE_SCHEME_CATALOG_MODE=demo`, then restart their own frontend process on 3001.
Its demo selector works only in Vite development; selecting it is now optional
because the backend's local bridge also supports ordinary paths. Production
deployments must leave backend demo mode disabled and use published endpoints,
which currently return an empty catalogue.
No frontend installation, build, authentication repair or source edit was performed
by this audit. Any frontend Supabase import/UI failure remains with its owners.

Voice is a browser concern: confirmed transcripts may be submitted as normal typed
answers. FastAPI has no speech recognition/TTS/upload endpoint. Provide browser
capability checks, microphone permission handling, text entry and confirmation.
Physical microphone capture, audio playback and the current frontend were not
tested here; previous synthetic speech-event checks are not hardware verification.

## 10. Verification commands and actual results

From `engine`, after installing backend/test requirements and PGlite:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test "db-validation/*.test.mjs"
.\.venv\Scripts\python.exe -m pip check
```

If the proposed repository checks are present, from the repository root:

```powershell
.\citizen-scheme-assistant\engine\.venv\Scripts\python.exe -B .github/ci/check_repository.py api
.\citizen-scheme-assistant\engine\.venv\Scripts\python.exe -B .github/ci/check_repository.py catalog --collection citizen-scheme-assistant/engine/.phase3-output/catalog15/collection.json
```

Initial handover audit results (before the local-path bridge):

- **159 Python tests passed**, including all three new CORS tests and all existing
  eligibility, bilingual, state-validation, publication and privacy tests.
- **35 isolated PGlite tests passed**: schema/FKs, RLS, restricted reader/writer,
  publication guards, idempotency, rollback and local-only import behavior.
- Actual 8001 HTTP: health, docs, OpenAPI, languages and DB health returned 200;
  published list returned total 0; demo lists returned all 15 expected IDs in en/hi.
- **16 actual HTTP scenarios passed**, then the same 16 passed against an isolated
  freshly started Uvicorn instance with `.env` loading disabled and database
  settings absent. These include ten full bilingual five-scheme paths, early
  ineligibility, age uncertainty and unknown income. Explanations/checklists/source
  references were present, and repeated identical states returned identical results.
- Negative HTTP requests rejected invalid language/type, overlapping answer/skip,
  stale fingerprints, injected result status, premature results and unsupported schemes.
- Fresh defaults allowed both 3001 loopback origins and rejected an untrusted
  origin. With demo disabled, demo returned 404. With no DB settings, DB routes
  returned sanitized 503 while health/advisory stayed functional. A missing archive
  returned sanitized `DEMO_DATA_UNAVAILABLE` without leaking paths.
- Existing API baseline stayed unchanged: **16 operations and 42 components**.
  `pip check` passed. No new dependency was needed for the fix.

Tests use synthetic citizen answers and isolated fixtures; they are not government
policy approvals or a new live draft-base-table audit. The local supporting HTTP
summaries are in ignored `.phase3-output/final-backend-audit/`; they store counts
and outcomes, not citizen answer payloads. Windows sandbox restrictions initially
blocked temporary fixtures/child processes; the full suite passed when rerun with
the required process/filesystem permissions. No application workaround was added.

Local-path bridge regression results: **170 Python tests passed** (11 additional
bridge tests), **35 isolated PGlite tests passed**, and the existing API baseline
still checks **16 operations and 42 components**. The actual restarted API on port
8001 returned all 15 IDs in English and Hindi through `/api/v1/schemes`. Sixteen
real HTTP scenarios using ordinary questionnaire/result paths passed, including
all five full journeys in both languages, early rejection, age uncertainty and
unknown income. Explanations, document checklists and official-provider guidance
were returned with preliminary disclaimers. No live database write or publication
was performed. Summaries are ignored under `.phase3-output/catalog-bridge-audit/`.
All 7,780 frontend files compared byte-identically against this bridge task's
starting snapshot, including ignored files. All pre-existing changed/untracked
paths remain present, the index is empty, and branch/HEAD are unchanged. The
concurrent frontend activity noted in the initial audit below predates this task.

The subsequent fifteen-guide extension passed **181 Python tests**, **35 isolated
PGlite tests**, and **74 real HTTP journey scenarios** across the ordinary and
explicit demo namespaces. All fifteen were exercised in both languages. The
original five inventory interface and fingerprints are preserved; all ten new
guides enforce incomplete-criteria verification gates. See
[PRELIMINARY_SCREENING15.md](PRELIMINARY_SCREENING15.md) for the current evidence
and reproducible integration commands. The extension's fresh comparison again
confirmed all 7,780 frontend files unchanged, no staged files and unchanged HEAD.

## 11. Defect fixed and known limits

**Fixed:** `app/core/config.py` did not allow the documented frontend port 3001
when `CORS_ORIGINS` was unset. A machine with a filled `.env` hid this fresh-setup
failure. Added the two 3001 loopback defaults and `tests/test_config.py`. Explicit
deployment origins still replace defaults, wildcard/credential origins remain
rejected, credentialed cookies remain disabled, and API schemas did not change.

Remaining limits/blockers:

- **Public publication/eligibility:** zero published records and zero execution
  approvals. Complete human policy, translation, evidence and guidance review is
  required before any authorized publication; this audit does not perform it.
- **Portability:** obtain the existing catalogue archive for a fresh machine's
  discovery flow. All fifteen questionnaire guides are tracked (the original five
  plus the backend extension), but not all original full bundles/captures.
- **Policy edge cases:** PMJJBY's upper entry boundary, PMSBY near termination age,
  APY/PM-SYM boundary dates, the PM-SYM exact income conflict and SSY multiple-birth
  exceptions require provider confirmation. Existing pension/cover interactions can
  also produce verification. These are intentional uncertainty outcomes.
- **Freshness:** guides checked 2026-10-31 fail closed after their 90-day window
  (currently through 2027-01-29 inclusive). The demo catalogue can also return 503
  when a guide expires. Do not just advance dates or override the guard. Definitions
  are cached in-process: restart the API after a legitimate source/content update;
  old questionnaire fingerprints must be discarded.
- **Deployment:** no remote access to local-only advice, production hardening,
  load/availability target, rate limiter or external identity integration is promised.
- **Frontend:** its existing package modifications and any import/authentication
  problems were preserved and are not certified by backend HTTP tests.

Final scope check: no tracked frontend file changed from this audit's starting
snapshot, and the Git index is empty. Pre-existing frontend `package.json` and
`package-lock.json` edits remain untouched. Concurrent changes were observed in
ignored frontend `.env.local`, `src/lib/supabaseClient.js`, build output and Vite
cache files. This audit neither generated nor restored them and did not inspect
their credentials. Therefore the complete frontend tree is not claimed to be
byte-identical to the starting snapshot. Existing untracked collaboration and
teammate files remain present; the branch and HEAD are unchanged.

## 12. Security and privacy

- Keep database URLs and CA paths server-side; never put them in `VITE_*`, a PR,
  screenshot, browser log or Git history. `.env.example` contains placeholders only.
- The API reader cannot write or inspect private catalogue base tables. The
  administrative importer/reviewer are separate, require their existing gates,
  and are not invoked by citizen requests. Do not request writer credentials for integration.
- Questionnaire inputs are bounded and strict. No dynamic `eval`, answer-derived SQL,
  LLM decision, persistent citizen profile or answer logging was found in runtime code.
- Responses contain client-held answers by design; keep them only in volatile
  memory, clear them on request and do not log requests/responses or use persistent
  browser storage/analytics for answers. No name, Aadhaar/account number or document
  upload is required for these checks; the checklist asks what to take to the provider.
- Published rule and guidance hashes/attestations must agree; local preliminary
  labels and source checks must never be promoted into human publication approval.
- This is a source/code/test audit, not a formal security certification. Do not
  publicly expose the development server or disable TLS/RLS to make a demo work.

A bounded literal-secret scan of 40 backend Python files (runtime, ingestion and
review tools) found no credential-bearing PostgreSQL URL, service secret, JWT
literal or private-key block; AST inspection found no `eval`/`exec` calls there.
This is not an exhaustive secret-history scan or dependency vulnerability audit.

## 13. Judge demo without changing the frontend

With the backend running in local advisory mode, first open Swagger and execute:

1. `GET /health` — show the service is alive.
2. `GET /api/v1/demo/schemes?lang=en` — show 15 screenable records; ten require further verification even on matching answers.
3. `POST /api/v1/demo/questionnaire/start` for PMJJBY with `language: "en"`.
4. Answer only the returned questions: synthetic age **30**, existing cover **false**,
   participating savings account **true**, auto-debit consent **true**. Preserve
   returned state after every operation.
5. Explain the completed state — show likely eligibility, reasons, three checklist
   entries, official information link and preliminary disclaimer.
6. Repeat with `language: "hi"`; show the actual Hindi responses.
7. Start again with age **16** to demonstrate stopping after one question; age **50**
   demonstrates verification rather than an invented approval. For PM-SYM, an
   unknown income demonstrates an incomplete-answer result.

The following PowerShell helper handles UTF-8 correctly in Windows PowerShell 5.1
as well as PowerShell 7, without writing answers to disk:

```powershell
$api = 'http://127.0.0.1:8001'
function Invoke-SchemeApi {
    param([string]$Path, $Body = $null)
    $params = @{ Uri = "$api$Path"; Method = 'GET'; UseBasicParsing = $true }
    if ($null -ne $Body) {
        $params.Method = 'POST'
        $params.ContentType = 'application/json; charset=utf-8'
        $params.Body = [Text.Encoding]::UTF8.GetBytes(($Body | ConvertTo-Json -Depth 100 -Compress))
    }
    $response = Invoke-WebRequest @params
    $response.RawContentStream.Position = 0
    $reader = New-Object IO.StreamReader($response.RawContentStream, [Text.Encoding]::UTF8)
    try { $reader.ReadToEnd() | ConvertFrom-Json } finally { $reader.Dispose() }
}
$catalog = Invoke-SchemeApi '/api/v1/demo/schemes?lang=en'
$catalog.total
$q = Invoke-SchemeApi '/api/v1/demo/questionnaire/start' @{scheme_id='in-cen-000001'; language='en'}
$sample = @{age=30; existing_account=$false; savings_account=$true; contributions=$true}
while (-not $q.completed) {
    $questionId = $q.current_question.question_id
    if (-not $sample.ContainsKey($questionId)) { throw 'Unexpected question; review rather than guess an answer.' }
    $q = Invoke-SchemeApi '/api/v1/demo/questionnaire/answer' @{
        state=$q.state; question_id=$questionId; action='answer'; value=$sample[$questionId]
    }
}
$result = Invoke-SchemeApi '/api/v1/demo/results/explain' @{state=$q.state}
$result.eligibility_status
$result.explanation.text
$result.required_documents.items | ForEach-Object { $_.title.text }
$result.application_guidance.items | ForEach-Object { $_.steps | ForEach-Object { $_.text } }
$result.official_application_urls.items | Select-Object url,link_kind
Remove-Variable q,result,sample -ErrorAction SilentlyContinue
```

Use only these clearly synthetic sample answers for the judge script. Never guess
answers for a real citizen. The frontend team may demonstrate its own compatible
screens, but this backend audit does not certify the current frontend build.

## 14. Safe handover commit — commands only, not executed

From the repository root, after explicit user approval, stage **only these backend
handover and local-bridge files**. Earlier collaboration proposals and frontend changes remain
separate and uncommitted:

```powershell
git branch --show-current
git status --short
git add -- citizen-scheme-assistant/engine/app/core/config.py citizen-scheme-assistant/engine/tests/test_config.py citizen-scheme-assistant/engine/docs/BACKEND_HANDOVER.md citizen-scheme-assistant/engine/app/api/routes/demo.py citizen-scheme-assistant/engine/app/api/routes/schemes.py citizen-scheme-assistant/engine/app/api/routes/questionnaire.py citizen-scheme-assistant/engine/app/api/routes/results.py citizen-scheme-assistant/engine/tests/test_demo_bridge.py citizen-scheme-assistant/engine/app/eligibility/preliminary.py citizen-scheme-assistant/engine/app/eligibility/data/preliminary-additions.json citizen-scheme-assistant/engine/tests/test_preliminary.py citizen-scheme-assistant/engine/tests/test_screening15.py citizen-scheme-assistant/engine/tests/screening15_fixtures.py citizen-scheme-assistant/engine/tests/verify_screening15_http.py citizen-scheme-assistant/engine/docs/PRELIMINARY_SCREENING15.md
git diff --cached --name-status
git diff --cached --check
$frontendStaged = git diff --cached --name-only -- citizen-scheme-assistant/frontend/
if ($frontendStaged) { throw 'Frontend files are staged; stop and preserve the work for its owner.' }
git diff --cached
# Only after reviewing the staged list and receiving approval:
git commit -m "fix(backend): verify local integration and document handover"
git fetch origin
git push -u origin chore/backend-collaboration-guards
```

Open a reviewed PR into `main` after approval. Do not push directly to `main`,
force-push, reset, stash away teammates' changes or merge automatically. The proposed
CI/CODEOWNERS/branch-protection work has its own pending review and is not silently
included in this backend-only commit.

The final Git status below distinguishes the backend handover/bridge files from
pre-existing work. `M` is unstaged; `??` is untracked. No file is staged. The
unusual root filename is Git's quoted representation and was preserved.

```text
 M citizen-scheme-assistant/CONTRIBUTING.md
 M citizen-scheme-assistant/engine/app/api/routes/demo.py
 M citizen-scheme-assistant/engine/app/api/routes/questionnaire.py
 M citizen-scheme-assistant/engine/app/api/routes/results.py
 M citizen-scheme-assistant/engine/app/api/routes/schemes.py
 M citizen-scheme-assistant/engine/app/core/config.py
 M citizen-scheme-assistant/engine/app/eligibility/preliminary.py
 M citizen-scheme-assistant/engine/tests/test_preliminary.py
 M citizen-scheme-assistant/frontend/package-lock.json
 M citizen-scheme-assistant/frontend/package.json
?? .github/CODEOWNERS
?? .github/PULL_REQUEST_TEMPLATE.md
?? .github/api-surface.json
?? .github/backend-policy.json
?? .github/ci/check_repository.py
?? .github/ci/constraints.txt
?? .github/ci/test_repository_checks.py
?? .github/workflows/backend-safety.yml
?? .vscode/settings.json
?? CONTRIBUTING.md
?? "cheme discovery and preliminary eligibility screening\357\200\242"
?? citizen-scheme-assistant/engine/docs/BACKEND_HANDOVER.md
?? citizen-scheme-assistant/engine/docs/PRELIMINARY_SCREENING15.md
?? citizen-scheme-assistant/engine/app/eligibility/data/preliminary-additions.json
?? citizen-scheme-assistant/engine/tests/screening15_fixtures.py
?? citizen-scheme-assistant/engine/tests/test_config.py
?? citizen-scheme-assistant/engine/tests/test_demo_bridge.py
?? citizen-scheme-assistant/engine/tests/test_screening15.py
?? citizen-scheme-assistant/engine/tests/verify_screening15_http.py
?? citizen-scheme-assistant/output.zip
?? citizen-scheme-assistant/package-lock.json
```

Supporting audit scripts, hashes and HTTP outcome summaries were generated only
under the existing Git-ignored `engine/.phase3-output/final-backend-audit/`; none
belong in the proposed commit. No existing untracked path was removed.
