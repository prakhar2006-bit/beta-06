# Preflight TLS correction and final import command

**Handoff update:** the owner subsequently ran the live import successfully and
returned SQL verification of 15 draft-v1 schemes, 63 evidence rows and zero
published versions. The execution/credential limitations below describe the
earlier preflight session. No additional import is needed for this handoff.

The old preflight queried `pg_stat_ssl` behind the Supabase session pooler. That
reports the pooler-to-Postgres hop, not this client's TLS connection. Live read-only
inspection confirmed the current client uses TLS while that internal hop reports
false. The resulting `InputError('TLS required')` was a false rejection for this
pooler topology.

The importer now checks `conn.pgconn.ssl_in_use` after psycopg has connected with
the unchanged `sslmode='verify-full'` and explicit CA file. Plaintext is still
rejected. No RLS/role/draft restrictions or FastAPI connection settings changed.
Owned static preflight errors are now displayed safely; raw psycopg/server errors
and arbitrary validation exceptions remain redacted. Passwords and DSNs are never
included in diagnostics.

Read-only catalogue metadata inspection showed all writer permission guards pass.
Authenticated writer preflight is **not claimed**: its credentials are in the
owner's existing PowerShell session and are intentionally unavailable to the agent.
No credential file was created, and no secret was searched for or copied.

From the existing credential-bearing PowerShell session, change to engine and run:

```powershell
Set-Location -LiteralPath 'C:\Users\Asus\OneDrive\Desktop\version beta 6\beta-06\citizen-scheme-assistant\engine'
.\.venv\Scripts\python.exe -m ingestion.postgres_import --collection .phase3-output/catalog15/collection.json --plan .phase3-output/catalog15-postgres-plan.json --check-target
```

The importer reads SCHEME_IMPORT_DATABASE_URL and SCHEME_IMPORT_SSLROOTCERT from
that session, overriding generic PGSSL settings with verify-full and the provided
CA. The CA path supplied by the owner is `C:\Users\Asus\secure\supabase-ca.crt`.
No password, connection string or variable echo is needed.

Expected preflight: all 15 IDs report maximum version 0 and this exact plan hash:

`3da3943c7eb059dd3ea1ebccc8ae3414a2cb1fc9320cb90363edb73a873d0e6a`

If preflight succeeds, the following is the **prepared command requiring separate
explicit commit approval**; it has not been executed:

```powershell
.\.venv\Scripts\python.exe -m ingestion.postgres_import --collection .phase3-output/catalog15/collection.json --plan .phase3-output/catalog15-postgres-plan.json --commit --approve-plan-sha256 3da3943c7eb059dd3ea1ebccc8ae3414a2cb1fc9320cb90363edb73a873d0e6a --confirm-target zqdcajmioiwtwtzaqgjt/aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres
```

Scope: project zqdcajmioiwtwtzaqgjt, database postgres on the confirmed session
pooler, in-cen-000001 through in-cen-000015, expected 0→1, all draft. Any mismatch
requires a new approved plan. No publication or unverified-rule activation.
