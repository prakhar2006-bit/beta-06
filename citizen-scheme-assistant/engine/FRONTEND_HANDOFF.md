# Citizen Scheme Assistant — frontend handoff

API: **http://127.0.0.1:8001** · Swagger: **http://127.0.0.1:8001/docs**
OpenAPI: **http://127.0.0.1:8001/openapi.json** · Frontend: **http://localhost:3001**

## Run

Backend owner, from `citizen-scheme-assistant/engine`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

Frontend teammates, from `citizen-scheme-assistant/frontend`:

```powershell
npm.cmd ci
$env:VITE_API_BASE_URL='http://127.0.0.1:8001'
npm.cmd run dev -- --port 3001 --strictPort
```

If dependencies are already installed, skip `npm.cmd ci`. The backend must remain
running. On another computer, 127.0.0.1 points to that computer: use an approved
shared backend HTTPS URL and have the backend owner allow the exact frontend
origin in CORS. Frontend developers need **no database URL, password, writer
credentials or Supabase service key**. VITE variables are public browser settings.
The backend owner alone maintains its private read-only database configuration.
For a fresh backend checkout, the owner creates `.venv`, installs
`requirements.txt`, copies `.env.example` to private `.env` and supplies only the
restricted `scheme_api` settings. No writer/admin connection is used by FastAPI.
Backend tests additionally use `requirements-test.txt` and
`npm.cmd ci --prefix db-validation` for the existing local PGlite checks.

## Contracts

For the local hackathon **unverified draft preview**, see [LOCAL_DEMO.md](docs/LOCAL_DEMO.md).
It requires explicit development flags on both servers; ordinary startup remains
published-only. No database status or eligibility approval is changed.

| Endpoint | Request / response |
| --- | --- |
| `GET /health` | Database-independent liveness JSON |
| `GET /api/v1/schemes` | Query `lang=en|hi`, optional `search`, `level=central|state|ut|local`, `limit`, `offset`; returns `items,total,limit,offset,has_more` |
| `GET /api/v1/schemes/{scheme_id}?lang=hi` | Published detail with sources and language/fallback metadata; unpublished/missing → 404 |
| `POST /api/v1/questionnaire/start` | `{scheme_id,language}` → questionnaire response |
| `POST /api/v1/questionnaire/next` | `{state}` → refreshed questionnaire response |
| `POST /api/v1/questionnaire/answer` | `{state,question_id,action:"answer",value}`; `null` means unknown |
| Same answer endpoint | `action:"skip"` or `"clear"`, **omit value** |
| `POST /api/v1/eligibility/evaluate` | `{scheme_id,answers,language}` → deterministic evaluation |
| `POST /api/v1/results/explain` | `{state}` → server-re-evaluated result and trusted guidance |

Questionnaire responses contain `state,current_question,completed,completion_reason,
progress,missing_information,evaluation`. Preserve the returned state including
`state_version,policy_fingerprint,skipped`; do not create session IDs or supply rules.
Render the returned question: integer/decimal/number/category/boolean, allowed
values, units and language metadata. Never advance using a fixed question count.

After completion, call `/results/explain`; navigate to Results only on success.
Results contain `eligibility_status`, scheme name, explanation, assessment notice,
condition results, missing information, benefits, required documents, application
guidance, official application URLs, sources and last verification date. Guidance
sections have `status,message,items`; display text has `text,content_language,
translation_fallback`. Exact nested models/examples are in Swagger. The local
frontend integration uses `services/sessionApi.js`, `screeningFlow.js` and
`adapters.js`; those frontend working changes are separate from this backend-only
commit. Frontend teammates should reuse their integration branch or implement the
requests above against Swagger. Backend startup/tests do not require those changes.

## Required UI behavior

- ELIGIBLE is preliminary screening, not government approval or payment assurance.
- NEEDS_VERIFICATION includes unknown answers or unapproved/incomplete policy;
  preserve missing information and review blockers.
- Missing reviewed Hindi uses labelled English fallback. Do not invent translations,
  required documents or application links.
- Keep answers/results in memory. Clear Data clears them; reload loses them.
  Voice recognition requires user confirmation before submission.
- Errors use `{error:{code,message,...}}`; handle 404, 409 stale policy, 422 validation
  and 503 service errors. Never silently substitute mock eligibility results.
- The catalogue serves **published views only**. An empty catalogue is valid.
  Importing drafts does not make them public or approve their eligibility rules.

## Verified handoff status

The running backend at 8001 returned 200 for health, OpenAPI and Swagger; CORS
allowed `http://localhost:3001`, and the frontend at 3001 returned 200.
The live transaction committed all 15 schemes as draft version 1. The backend
owner returned the requested read-only Supabase SQL verification: 15 schemes,
15 draft-v1 rows, 63 evidence rows and zero published versions. All IDs
in-cen-000001 through in-cen-000015 are present. No privileged credential was
shared with this agent or frontend teammates. Private-row verification was through
the owner's SQL Editor session. Draft records are never returned by published
catalogue endpoints. Writer
credentials remain only in the backend owner's separate PowerShell session and
are not included in this checkout. Generated bundles/captures under
`.phase3-output` are private ignored artifacts; teammates do not need them to use
the API or run the synthetic unit tests.
Public government-scheme screening remains unavailable until the existing review,
publication and execution-approval gates are satisfied.

The restricted API role cannot SELECT draft base tables. Handoff API checks
returned an empty published catalogue and NEEDS_VERIFICATION for the real PMJJBY
draft, as required. Import completion does not authorize publication or rule execution.
