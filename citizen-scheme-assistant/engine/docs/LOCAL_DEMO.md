# Local citizen journey

The local Vite/FastAPI app supports source-based preliminary screening for
**PMJJBY, PMSBY, PM-SYM, Atal Pension Yojana and Sukanya Samriddhi**.
The other ten schemes remain information guides. The five guides show benefits,
entry conditions, documents, provider instructions and deduplicated official sources.
Hindi wording is project-authored and is not an official government translation.

This is a separate advisory scope: it returns `ELIGIBLE_LIKELY`,
`NOT_ELIGIBLE_LIKELY` or `NEEDS_VERIFICATION`, never an approved `ELIGIBLE`.
It reuses the existing engine's strict answer types and deterministic comparison
operators. It does not activate the 28 draft proposals, manufacture publication or
translation attestations, or change the trusted published-policy provider.
Age boundaries, the PM-SYM income boundary and SSY family exceptions require
provider verification. New enrolment is screened; renewal and claims are not.

## Run in two PowerShell terminals

Backend, from `citizen-scheme-assistant/engine`:

```powershell
$env:SCHEME_APP_ENV='development'
$env:SCHEME_DEMO_ENABLED='1'
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload --no-access-log
```

Frontend, from `citizen-scheme-assistant/frontend`:

```powershell
$env:VITE_API_BASE_URL='http://127.0.0.1:8001'
$env:VITE_SCHEME_CATALOG_MODE='demo'
npm.cmd run dev -- --port 3001 --strictPort
```

Stop existing processes on these ports before starting replacements.
Open http://localhost:3001/schemes, choose one of the first five schemes, and click
**Check my eligibility**. Answer the adaptive questions, select **See my result**,
check off documents and follow the official provider's instructions.
You can skip, choose unknown, edit answers, switch language or clear your data.
Answers stay in memory; no accounts or citizen database records are created.
Speech input requires confirmation before submission and has a typed fallback.

## API and safeguards

Development endpoints under `/api/v1/demo`:

- `GET /schemes?lang=en|hi` and `GET /schemes/{stable_id}?lang=en|hi`.
- `POST /questionnaire/start`: `{scheme_id, language}`.
- `POST /questionnaire/next`: `{state}`.
- `POST /questionnaire/answer`: `{state, question_id, action, value}`.
  Actions are `answer`, `skip`, `clear`; omit value for skip/clear.
- `POST /results/explain`: `{state}`. Results are recomputed server-side.

Keep the returned state and fingerprint; never send rules, result status or approval.
The existing production endpoints and read-only Supabase connection are unchanged.
Both development flags and loopback access are required. Production Vite builds
use only the published API. The actual published catalogue still has zero results.
No Supabase data, permissions, credentials or statuses were changed.

Catalogue bundles remain in the existing ignored `engine/.phase3-output/catalog15`
directory. The five source-checked advisory guides live in
`data/schemes/preliminary-screening.json`. Checked sources are dated 2026-10-31;
screening fails closed after a 90-day freshness window until a new source review.
They are server-owned content, not an import or execution approval manifest.

Verification: 156 backend tests, 20 frontend tests and the production build passed.
The real headless browser completed all five journeys in English and Hindi plus
likely-ineligible, verification and keyboard-fallback journeys. Checklists and
official guidance links were checked. Private evidence is in
`engine/.phase3-output/citizen-browser-report.json` and `citizen-*.png`.
Recognition and TTS event handlers were exercised with synthetic browser adapters;
physical microphone capture and speaker output were not verified.
