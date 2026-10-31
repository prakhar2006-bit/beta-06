# Scheme Navigator Phase 2 API

Run all commands from `citizen-scheme-assistant/engine`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-test.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Base URL: `http://127.0.0.1:8000`. Swagger: `/docs`. Machine-readable schema:
`/openapi.json`. These catalogue response models are a new read API, not a
replacement for `contracts/scheme.schema.json` (the offline rule-definition
contract) or the citizen-profile/eligibility-result contracts. The database has
no category, issuing-document authority, or bilingual rule explanation columns
required by those older contracts. No shared contract or frontend was changed.

## Endpoints

| Method and path | Behavior |
| --- | --- |
| `GET /health` | Existing liveness response; no database dependency |
| `GET /api/v1/meta/languages` | English and Hindi interface language metadata |
| `GET /api/v1/schemes` | Latest currently effective published version per scheme |
| `GET /api/v1/schemes/{scheme_id}` | Detail by stable slug (`id` in list output), not the database UUID |
| `GET /api/v1/meta/health/db` | Minimal read-only connectivity/view-access check; 503 on failure |

Listing parameters:

- `lang`: `en` (default) or `hi`; details accepts this too.
- `search`: optional literal, case-insensitive substring in the returned title
  or summary; maximum 200 characters. SQL wildcard characters are escaped.
- `level`: optional `central`, `state`, `ut`, or `local` (actual database values).
- `limit`: 1–100, default 20.
- `offset`: 0–1,000,000, default 0.

Selection uses the highest published `version_number` whose effective date
range includes the current Indian date. Null boundaries are unbounded; date
endpoints are inclusive. Search applies after version and language selection,
so obsolete translations cannot replace the current version. Ordering is stable
by slug and database UUID. Count and page queries use one REPEATABLE READ
snapshot. Offset pagination can still shift between separate requests if new
records are published. `has_more` uses the filtered total. No active/open status
is inferred from publication: lifecycle status is returned as stored.

Examples (empty-list response shape, not invented government records):

```http
GET /api/v1/schemes?lang=hi&level=state&limit=20&offset=0
```

```json
{"items":[],"total":0,"limit":20,"offset":0,"has_more":false}
```

```json
{"status":"ok","service":"Scheme Navigator","version":"0.1.0"}
```

```json
{"items":[{"code":"en","name":"English"},{"code":"hi","name":"हिन्दी"}]}
```

List items expose the stable `id`, `database_id`, `version_id`, version number,
requested/returned language, fallback flag, name, description, government level,
lifecycle, organization code/name/URL, last checked date, effective dates and
publication time. Details add `eligibility_text`, `translation_evidence_id`,
`benefits`, `application_routes`, `required_documents`, `eligibility_rules`,
`rule_evidence`, `jurisdictions`, and `sources`. Consult `/docs` for exact typed
fields. Monetary decimals serialize as strings to preserve precision. Dates use
ISO 8601. Missing optional values are `null`; absent child collections are `[]`.
Application URLs are returned per route, including null for offline-only routes.

## Language and source limitations

The requested translation is preferred; if absent, return the other stored
English/Hindi translation. `language` states the actual returned language and
`translation_fallback` reports the mismatch. If neither exists, localized text
and `language` are null; the catalogue record remains visible. No text is generated
or translated. Reviewed publication normally requires both translations; fallback
is defensive against legacy data and applies only to the selected version.

Only title, summary and eligibility text have a recorded language. Organization
names, benefits, application instructions, document text, evidence and jurisdiction
names have no language metadata. They are returned verbatim, listed under
`unlocalized_fields` on details; benefit/document/application entries explicitly
use `content_language: null`. Do not present these fields as verified Hindi/English
translations. The structured rule tree is data, not an eligibility decision.

`sources` contains only evidence cited by the selected version, preserving original
URL, source title, locator, supporting text, verification date, hash, retrieval and
publisher update timestamps and license URL. No ingestion metadata, artifact paths,
reviewer identifiers, credentials or base-table records are exposed.

## Errors

All handled API errors use `error.code` and `error.message`. Validation adds
`error.fields` with field locations, never submitted values or internal context.
Messages are currently fixed English developer-facing text; React should map
stable error codes to its own bilingual i18n strings.

```json
{"error":{"code":"SCHEME_NOT_FOUND","message":"Published scheme not found."}}
```

```json
{"error":{"code":"INVALID_REQUEST","message":"Invalid request parameters.","fields":["query.limit"]}}
```

| Status | Code | Meaning |
| --- | --- | --- |
| 404 | `SCHEME_NOT_FOUND` | Unknown, unpublished, or no currently effective version |
| 422 | `INVALID_REQUEST` | Unsupported language/level or invalid pagination/slug |
| 503 | `DATABASE_UNAVAILABLE` | Missing configuration, TLS/network/role failure |
| 503 | `DATABASE_TIMEOUT` | Database statement timed out |
| 503 | `DATABASE_QUERY_FAILED` | Query, missing view, permission or schema mismatch |
| 500 | `INTERNAL_ERROR` | Unexpected internal failure |

An empty catalogue is HTTP 200 with an empty page, never a connectivity error.
The development DB-health endpoint returns only `{"status":"ok"}` on success;
it does not count data or disclose server details. Consider restricting this
diagnostic endpoint at the deployment proxy. Unknown routes/methods use the same
envelope with `HTTP_ERROR`; CORS preflight is middleware-controlled.

## React integration

Use the frontend's existing `VITE_API_BASE_URL` setting. In local development set
it to `http://127.0.0.1:8000`; for deployment set the backend HTTPS origin and
rebuild Vite. This variable contains no database credentials.

```javascript
const base = import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '');
const params = new URLSearchParams({ lang: 'hi', limit: '20', offset: '0' });
const response = await fetch(`${base}/api/v1/schemes?${params}`);
const body = await response.json();
if (!response.ok) throw new Error(body.error?.code ?? 'REQUEST_FAILED');
// Render body.items; use body.total/body.has_more for pagination.
// Follow /api/v1/schemes/{item.id}?lang=hi for details.
```

Set server `CORS_ORIGINS` to a comma-separated list of exact origins. Defaults
allow localhost/127.0.0.1 on ports 3000/5173. Production must specify its explicit
HTTPS frontend origins. Wildcards are rejected. Cookies/credentialed requests
are not enabled; this read-only catalogue API does not implement authentication.

## Configuration, security and testing

`app/core/config.py` loads `engine/.env` with no interpolation and never overrides
already exported process variables. Production should inject environment variables.
Only runtime code consumes the existing file; no secret values are printed.
`DATABASE_URL`, `DATABASE_EXPECTED_USER` and `DATABASE_SSL_ROOT_CERT` retain the
smoke-test meaning. No database validation or connection occurs at import time
or in `/health`. Bad/missing DB configuration becomes 503 only on DB routes.

`app/db/connection.py` reuses the smoke configuration validator and enforces the
scheme_api login, reader membership, no admin attributes or base-table grants,
verified TLS, read-only transactions, a 10-second connect timeout and 5-second
statement timeout. All repository reads use parameterized, schema-qualified,
allowlisted published views. One connection serves an entire list/detail request;
no per-row connection or unbounded pool is created. Sync routes run in FastAPI's
worker thread pool; a bounded persistent pool can be considered after load testing.
Cursors/connections close and transactions roll back even on exceptions. Driver
errors are mapped without forwarding SQL, connection strings or driver messages.

Unit/API tests override the repository or mock connections and need no Supabase
credentials. In-memory PGlite migration tests remain separate and unchanged:

```powershell
node --test db-validation/catalog.test.mjs
```

The existing `database_smoke.py` remains an opt-in remote integration check, not
part of unit test discovery. No migration, role, permission, production data,
frontend file or shared contract is modified by Phase 2.

Read-only verification on 31 October 2026: all ten approved views were readable;
`published_schemes` and `published_versions` each contained zero rows. DB health
returned 200, English/Hindi filtered list requests returned valid empty pages,
and an unknown slug returned 404. The existing local Uvicorn server served the
new language metadata route with HTTP 200. Populated scheme details were tested
with synthetic unit fixtures, not real production records.

For Phase 3, curate verified official scheme facts with permission/license
evidence and dated source snapshots. Use an independently approved ingestion
role/workflow, never scheme_api. Import drafts with real evidence and human-reviewed
English/Hindi content, verify complete rule trees and effective dates, then review
and publish through the existing workflow. Do not scrape restricted sources or
seed synthetic test fixtures into Supabase. Resolve the unlocalized child-text
limitation through a separately reviewed schema/contract change if full bilingual
detail presentation is required.
