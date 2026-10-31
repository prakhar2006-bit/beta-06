# Supabase integration runbook

No commands in the remote sections below have been run. Project creation,
remote access, migration application and runtime-login provisioning require
the user's approval. No remote credentials are needed for offline tests.

## Review findings

The original two migrations are unchanged. They use standard PostgreSQL SQL,
PL/pgSQL, UUID defaults, JSONB, GIN, partial indexes and deferred constraint
triggers supported by Supabase PostgreSQL. No extension installation or access
to Supabase-managed tables is required. Foreign keys default to NO ACTION,
avoiding deletion of cited records. Child uniqueness indexes cover version joins;
migration 003 adds the missing version-leading rule-evidence index and a partial
index for published-version lookup.

Draft -> reviewed -> published is enforced. Reviewed and published content is
frozen. Review requires bilingual reviewed translations, a jurisdiction, a rule
root, review metadata and evidence for every predicate. Deferred rule checks
reject cycles, cross-version parents and invalid node arity at commit. Build
complete trees in a transaction. Child writes lock the version row to serialize
with review. Native concurrent-transaction testing remains outstanding.

Every base table has RLS enabled without client policies. Migration 003 also
revokes schema/table/function privileges from existing `anon`, `authenticated`
and `service_role` roles, including defaults for the migration owner. RLS is a
second barrier; the service role's BYPASSRLS does not bypass missing SQL grants.
Do not grant these roles catalogue access or expose this schema in Data API
settings. These revocations are scoped to `scheme_catalog`, not other apps.

The runtime uses the `scheme_catalog_reader` NOLOGIN group through a dedicated
`scheme_api` LOGIN. It can read only ten `published_*` views. These views use
the trusted migration owner's permissions deliberately, since the reader has no
base-table grants. Each view enforces publication through its definition or a
join to `published_versions`; do not change it to `security_invoker` without
redesigning grants/RLS. Security barriers prevent unsafe predicate pushdown.
The views omit reviewer references, ingestion errors, permission references and
artifact paths. The backend role cannot ingest, review, publish or mutate data.
Maintain the views under the trusted migration owner; do not transfer ownership
to the runtime role or add unreviewed writable views/functions.

All published historical versions remain visible. FastAPI should select the
highest applicable version_number per scheme with effective-date filtering.
Publication does not prove a scheme is active or accepting applications.

## Offline checks (safe to run now)

From `beta-06` in PowerShell:

```powershell
Set-Location .\citizen-scheme-assistant\engine
npm.cmd --prefix db-validation ci
npm.cmd --prefix db-validation test
python -m unittest discover -s tests -v
```

Node >=22 and Python >=3.10 are required. PGlite tests run migrations against
fresh in-memory PostgreSQL, simulate Supabase API roles and test migration-history
replay. The local history harness is not an end-to-end test of Supabase CLI.

## Prepare local Supabase tooling

Install the Supabase CLI using its official installation instructions, and
Docker Desktop if running the local stack. From `engine`:

```powershell
supabase --version
supabase init
```

This creates `engine/supabase/config.toml` beside the existing migrations.
Do not overwrite a teammate's existing config. Keep `scheme_catalog` out of
`[api].schemas` and `extra_search_path`. Set `[db.seed].enabled = false`.
If using a disposable local Docker stack, `supabase start` applies migrations.
Then run `supabase db lint --local --schema scheme_catalog` and inspect the result.
Only use `supabase db reset --local` on a disposable local database: it deletes
local data. Custom cluster-wide roles can survive some reset workflows; if
`scheme_catalog_reader` already exists, stop and inspect its ownership/grants
rather than automatically dropping it or suppressing the conflict.

## Link an existing project (requires approval)

Obtain the project reference from its Dashboard. Do not create a project as
part of this runbook. Use a development project first. From `engine`:

```powershell
supabase login
supabase link --project-ref YOUR_PROJECT_REF
supabase migration list --linked
supabase db push --linked --dry-run
```

Use the CLI's login/password prompts, not credentials in command arguments or
committed files. Inspect the project identity and pending migrations. If the
project has unrelated migration history, existing `scheme_catalog` objects or
an existing reader role, stop and reconcile the baseline with the team. Do not
use `migration repair`, `--include-all`, or manual SQL replay to hide a mismatch.

## Apply (separate approval required)

After reviewing the dry-run and the project's backup/recovery plan:

```powershell
supabase db push --linked
supabase migration list --linked
supabase db push --linked --dry-run
```

Expected history: `20261030000100`, `20261030000200`, `20261030000300`.
The final dry-run should have no pending migrations. Supabase tracks applied
versions in `supabase_migrations.schema_migrations`; subsequent pushes skip them.
The SQL is intentionally fail-fast on raw replay (duplicate schema/role/object),
not filled with `IF NOT EXISTS` clauses that could silently conceal schema drift.
Never edit an applied migration: add a new forward migration. Apply through
the CLI's migration system, not by pasting fragments into Dashboard SQL Editor.

## Provision the runtime login (requires approval)

Use a trusted admin **direct** connection, or Dashboard-provided **session**
pooler connection if IPv4 access requires it. Do not use transaction pooling
for administration/migrations. Connect with psql using connection parameters
from Dashboard > Connect, a downloaded project CA and a prompted password:

```powershell
psql "host=YOUR_HOST port=5432 dbname=postgres user=YOUR_ADMIN_USER sslmode=verify-full sslrootcert=C:/secure/path/supabase-ca.crt" -W
```

Inside psql, run the following only after approval (no password in SQL history):

```sql
CREATE ROLE scheme_api LOGIN INHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 10;
GRANT scheme_catalog_reader TO scheme_api;
ALTER ROLE scheme_api SET default_transaction_read_only = on;
ALTER ROLE scheme_api SET statement_timeout = '5s';
ALTER ROLE scheme_api SET search_path = pg_catalog;
\password scheme_api
```

Enter a new strong password in the protected prompt. The LOGIN inherits the
reader's SELECT grants. Never grant it membership in postgres, service_role or
other admin roles. Do not grant base-table access. Do not use the database-owner
password in FastAPI. Ingestion/review requires a separately reviewed writer
role or an isolated administrative workflow, not this application login.

## Configure and run the smoke check (requires remote-access approval)

Copy `engine/.env.example` to ignored `engine/.env` locally, then fill it privately.
No settings are read automatically by the script. Use your process secret manager
to export `DATABASE_URL`, `DATABASE_EXPECTED_USER` and `DATABASE_SSL_ROOT_CERT`,
or Python's `--env-file` feature below. URI-encode password characters. Use the
actual host and port from Dashboard, not a guessed pooler hostname. The direct
username is `scheme_api`; the session-pooler username is usually
`scheme_api.PROJECT_REF`. Expected SQL current_user remains `scheme_api`.

Use verified TLS for every remote connection. Download the project's CA from
Database settings; `sslmode=require` alone does not verify server identity.
The script supplies `verify-full` and the CA path explicitly and rejects URI
query parameters that could override connection options. No Supabase HTTP API
key is needed. Keep these settings server-side; never use a `VITE_` prefix.

From `engine` (Python >=3.12 for `--env-file`):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-db.txt
.\.venv\Scripts\python.exe --env-file=.env database_smoke.py
```

On Python 3.10/3.11, export the three variables through the process environment
and omit `--env-file`. No command above contains an actual credential. Do not
paste the filled environment, CLI token, connection string or driver logs into
chat or Git. The smoke test has bounded connection/query timeouts, disables
prepared statements for pooler compatibility, uses only SELECTs in a read-only
transaction and rolls back. It verifies role identity, membership, lack of admin
attributes/base-table grants and access to a published view. An empty catalogue
passes; the test does not seed data or prove a scheme record exists.

FastAPI may reuse `check_connection`'s secure connection options as a starting
point for a bounded server connection pool. Use schema-qualified published views
and parameterized queries. No API endpoint or connection pool is implemented here.

## Remaining integration checks

Run the real CLI/local-stack checks, the approved remote dry-run/apply sequence,
and the read-only smoke test after provisioning the login. Verify inherited
privileges in the target project, TLS connectivity and native concurrency behavior.
None of these remote checks has been performed by this change.

References: [Supabase CLI](https://supabase.com/docs/reference/cli/supabase-db-push),
[migrations](https://supabase.com/docs/guides/local-development/database-migrations),
[connections and TLS](https://supabase.com/docs/guides/database/connecting-to-postgres),
[roles](https://supabase.com/docs/guides/database/postgres/roles),
[custom-role privilege caveats](https://supabase.com/kb/troubleshooting/custom-role-inherits-privileges-that-were-not-explicitly-granted),
[Psycopg transactions](https://www.psycopg.org/psycopg3/docs/basic/transactions.html).
