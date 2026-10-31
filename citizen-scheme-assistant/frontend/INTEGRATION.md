# Frontend integration — Phase 5

The React UI uses the public published catalogue and the existing stateless backend
contracts. No mock fallback, demo policy, publication bypass or browser eligibility
calculation is enabled. Input checks validate transport types only.

## Run locally

From `citizen-scheme-assistant/engine`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

From `citizen-scheme-assistant/frontend`:

```powershell
npm.cmd run dev
```

The default API origin is `http://127.0.0.1:8000`; optionally set
`$env:VITE_API_BASE_URL='http://127.0.0.1:8000'` before starting Vite.
Use the frontend origin already allowed by backend CORS (normally
`http://localhost:5173`). Swagger is at `http://127.0.0.1:8000/docs`.
Never put database credentials in Vite variables or browser code.

## Requests and state

| Operation | Request |
| --- | --- |
| List published schemes | `GET /api/v1/schemes?lang=en&limit=20&offset=0` (optional `search`, `level`) |
| Published detail | `GET /api/v1/schemes/{id}?lang=hi` |
| Start | `POST /api/v1/questionnaire/start` with `{scheme_id, language}` |
| Refresh / change language / restore history | `POST /api/v1/questionnaire/next` with `{state}` |
| Answer | `POST /api/v1/questionnaire/answer` with `{state, question_id, action:"answer", value}` |
| Unknown | Same answer request with `value:null` |
| Skip / clear | Same endpoint with `action:"skip"` or `"clear"`; omit `value` |
| Explain completed questionnaire | `POST /api/v1/results/explain` with `{state}` |

The returned state, including version, fingerprint, answers and skipped fields, is
passed back unchanged except for an explicit language change. No session ID is
used. The backend decides the next question, progress, completion and eligibility.
Booleans stay booleans, integer/number answers are numeric, decimal answers use a
decimal string, and categories must be backend allowed values. A voice answer is
shown for confirmation before submission; unrecognized speech is rejected.

## User journey

1. Browse published schemes or choose one on Screening. A deep link carries
   `scheme_id`; a published detail lookup validates selections beyond the first
   catalogue page. There is one scheme per questionnaire.
2. Render `current_question` and backend progress. Skip, unknown and clear remain
   distinct. Back restores a prior server state via `/next`, discarding later
   answers rather than editing question indexes.
3. On completion show verification needs accurately. Only after `/results/explain`
   succeeds does the UI navigate to Results. Failed explanations can be retried.
4. Display qualified screening status, backend assessment notice, conditions,
   missing information, benefits, documents, application guidance and citations.
   Missing guidance is unavailable, not fabricated. External links require HTTPS
   without embedded credentials; application links come from the backend's
   official application URL section.

`services/adapters.js` centralizes result mapping; the raw response is retained
for guidance metadata. `screeningFlow.js` owns ephemeral state and history;
`apiClient.js` supplies timeouts and sanitized HTTP/network errors. English/Hindi
navigation and errors use i18n. Backend content-language/fallback metadata is
shown explicitly; no browser translations are generated or called official.
Speech synthesis reads the actual question language. Browser speech recognition
depends on browser/OS support and may use the browser vendor's remote service.

Answers, results and document ticks stay in memory. Reload loses them. Clear Data
invalidates pending responses and clears memory plus legacy answer/session keys.
Only the existing language preference may persist; no answers are logged or
sent to analytics. HTTP errors do not expose submitted answer values.

## Verification and demo limits

```powershell
npm.cmd test
npm.cmd run build
```

13 tests cover request/state contracts, adaptive selection, data types, skip,
clear, unknown, history, completion modes, failed explanations, network/422 errors,
empty catalogue, fallback languages and safe React rendering. Fixtures are
explicitly synthetic and run only in tests. No additional dependency was added.
The production build passes. These are service/controller and server-rendering
tests, not browser end-to-end tests.

Local backend health and OpenAPI were reachable. No live catalogue/Supabase query
or real government-scheme screening was performed. Five local government drafts
remain blocked by review/publication requirements. An empty published catalogue
is a valid demo state; it must not be filled with drafts to unlock screening.

For a real demo, authorized reviewers must resolve policy/translation/guidance
blockers, publish through the existing workflow, and approve exact execution
hashes separately. Then verify in a browser: catalogue → selected scheme →
adaptive questions → explanation; test English/Hindi fallback, voice confirmation,
skip/back/clear, offline errors and refresh privacy. Publishing alone does not
grant execution approval. This integration changes no backend contracts or gates.
Build output and the optional generated OpenAPI snapshot are Git-ignored.
