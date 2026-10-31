# Restricted draft writer: SQL Editor review and credential setup

Prepared for project **zqdcajmioiwtwtzaqgjt**. No Supabase SQL, credentials, grants,
imports or publication were executed by this task. Tests used disposable local
PGlite only. FastAPI's read-only connection, scheme_api and migrations are unchanged.

## Security assessment

Review `ops/draft_writer_PROPOSAL.sql` in full. It creates a fresh **NOLOGIN,
NOINHERIT, NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOREPLICATION, NOBYPASSRLS** role.
It deliberately fails if the role/policies already exist; no replacement, drop,
ownership transfer, RLS disablement or broad default privilege changes occur.

| Capability | Assessment |
| --- | --- |
| Read catalogue drafts/published rows | Yes: necessary SELECT for deduplication and version checks. Private administrative credential only. |
| Insert scheme versions | Draft only; review/publication metadata must be null. Existing insert trigger also rejects non-draft status. |
| Approve/publish | No UPDATE on status, reviewed_at, reviewer_reference or published_at. No publication function or server-manifest access. |
| Insert reviewed translations/verified executable rule nodes | Rejected by new restrictive RLS fences: translation review_status must be draft; rule confidence UNCERTAIN. |
| Extend reviewed/published versions | Rejected by restrictive child INSERT policies and the existing parent-lock trigger. |
| Change existing content/provenance, delete, truncate | No such grants. Existing content and identity guards remain. |
| UPDATE(id) on scheme_versions | Required for the existing child trigger's SELECT FOR UPDATE. Only unreviewed drafts are visible to that UPDATE policy; changing identity is rejected by the existing trigger. A no-op id=id on a draft is possible. |
| Change RLS, owners or role memberships | Not an owner, no CREATE/schema ownership/CREATEROLE and no memberships in other roles. |
| Unrelated application schemas | No explicit grants; provisioning audits effective PUBLIC/schema/column/relation/sequence/routine privileges and rolls back if exposure exists. |
| Standard PostgreSQL metadata/TEMP | Normal public system metadata and database CONNECT/TEMP are not an isolation sandbox. No access to unrelated application data is intentionally allowed. |

The old permissive INSERT policy alone could be widened by another permissive
policy. The revised proposal keeps the necessary permissive grants but adds
**restrictive** fences, which remain AND requirements even if another permissive
policy allows more. PostgreSQL's [RLS documentation](https://www.postgresql.org/docs/17/ddl-rowsecurity.html)
explains this composition.

The corrected child policies correlate the actual outer `scheme_version_id` with
`v.id`; no invented child-table alias is used. Provisioning asserts all seven child
FKs reference `scheme_versions(id)` before creating the role. Existing composite
rule/version FKs remain intact. INSERT does not require granting REFERENCES (that
privilege is for defining foreign keys). Table UPDATE and column UPDATE are tested
separately: only id column UPDATE is allowed. Column REFERENCES, grant options and
mutable-view grants, including column-only INSERT, are rejected by the SQL and
writer preflight. None of these corrections alter a migration or bundle.

`NOINHERIT` does not remove PUBLIC privileges. PostgreSQL has no per-role DENY that
cancels a PUBLIC grant; see [privileges](https://www.postgresql.org/docs/current/ddl-priv.html).
The proposal therefore fails closed if the new role could create schemas/objects,
access unrelated application relations or call unrelated routines (including
SECURITY DEFINER RPCs), with the reviewed event-hook exception below. It does **not** automatically revoke PUBLIC grants and risk
breaking existing clients. Supabase's live unrelated schemas/functions have not
been inspected in this task. If the audit fails, do not bypass it: a project owner
must separately review the reported shared privilege and its legitimate users.
Future PUBLIC grants or role memberships can change access; rerun verification
immediately before enabling/importing. No blanket future isolation is claimed.

### Fixed live false positive: public.rls_auto_enable

Read-only inspection of project zqdcajmioiwtwtzaqgjt confirmed a stored, non-null
function ACL with PUBLIC EXECUTE (and postgres/anon/authenticated/service_role
entries). The writer role was absent after rollback, so this was not a direct
writer grant. A non-null ACL does not reveal whether its PUBLIC entry originated
from an explicit GRANT or retained function defaults; it proves the effective
PUBLIC route. A writer-only REVOKE cannot override that PUBLIC permission.

The inspected function is a zero-argument PL/pgSQL SECURITY DEFINER returning
event_trigger, owned by postgres, with search_path=pg_catalog. Its ensure_rls
binding is postgres-owned ddl_command_end, limited to CREATE TABLE, CREATE TABLE AS
and SELECT INTO. Its reviewed body only enables RLS for newly created public
tables; it excludes temporary/system schemas. It cannot be called as a normal
SQL/RPC function. The restricted writer cannot create event triggers, change this
function, create public tables, or acquire memberships/ownership.

The corrected SQL does **not** trust the function name or exempt all trigger
functions. It requires all reviewed metadata/bindings plus this exact SHA-256 of
pg_proc.prosrc:

`325ae266d9b166715ef5230ceaf7ff9d523e483cf5610dfb9779ab3f183f4af9`

Changing the body, owner, language, search_path, return type or binding scope fails
closed. Arbitrary row-trigger SECURITY DEFINER functions stay blocked: a caller
with TEMP could otherwise attach such a function to its own temporary table.
Ordinary callable functions/procedures remain subject to the original strict
audit. No global PUBLIC grant or existing Supabase function is modified.
The verification script applies the identical exception and separately displays
ACL provenance/hook metadata as information, not as an unsafe-RPC finding.

The read-only evidence is in `.phase3-output/rls-auto-enable-reviewed-body.json`;
the copied reviewed definition is a local test fixture only. PostgreSQL's
[event-trigger contract](https://www.postgresql.org/docs/17/sql-createeventtrigger.html)
and Supabase's [auto-enable RLS example](https://supabase.com/docs/guides/database/postgres/event-triggers)
explain the function category. No remote function or trigger was executed by this
inspection. Do not replace the expected hash just to clear a future failure;
review any changed body/bindings first.

### Exactly what to rerun after the reported failure

In the same project's SQL Editor, as administrator:

1. Execute `ROLLBACK;` to clear any remaining aborted transaction. The observed
   failed attempt left no writer role; do not drop any existing role/function.
2. Execute the **entire corrected** `ops/draft_writer_PROPOSAL.sql`, including its
   BEGIN/COMMIT. No manual REVOKE, function edit or bypass flag is needed.
3. Execute the **entire corrected** `ops/draft_writer_VERIFY.sql`. Its unsafe
   unrelated-routine result should omit this exact reviewed hook; its informational
   ACL section can still list PUBLIC EXECUTE. That is expected, not a failure.

Then follow the existing private-password/short-login procedure below and run
--check-target. This fix does not authorize a remote data import or publication.

## Supabase steps — only after you approve provisioning

1. Open the Supabase Dashboard and select project `zqdcajmioiwtwtzaqgjt`.
   Open **SQL Editor** using the project's administrative `postgres` role. Confirm
   the project reference from Dashboard settings/Connect; current_database() alone
   identifies `postgres`, not the project.
2. Paste the **entire** reviewed `ops/draft_writer_PROPOSAL.sql` into a new query.
   It contains no passwords. Execute once, including BEGIN/COMMIT. If any assertion
   fails, the transaction cannot commit: issue `ROLLBACK` if the editor reports an
   open aborted transaction, and review the error. Do not remove safety checks or
   blindly rerun against an existing role. The role remains NOLOGIN on success.
3. In another query run `ops/draft_writer_VERIFY.sql` in full. This is read-only and
   rolls back. Expected results:
   - Exactly one role row; login/inherit/superuser/createdb/createrole/replication/
     bypassrls all false before activation.
   - Zero memberships in other roles.
   - 15 base tables with SELECT/INSERT and RLS true; owner/mutation flags false.
   - Exactly one updatable column, scheme_versions.id; table-level UPDATE false.
   - Restrictive version/child/translation/rule/lock fences present.
   - Database CREATE false; zero unrelated-object/routine exposures.
   - The final query returns actual maxima/status counts for all 15 scheme IDs.
4. If the checks pass, generate/store a strong unique writer password in your
   password manager. **Do not paste it into SQL Editor, saved SQL, shell arguments,
   chat, Git or the frontend.** Do not reset the project's postgres password to set
   this custom role's password. Use an interactive trusted PostgreSQL client for
   this role-specific operation. For example, connect to the administrative session
   pooler with a password prompt (replace only the CA path):

   ```powershell
   psql "host=aws-0-ap-northeast-2.pooler.supabase.com port=5432 dbname=postgres user=postgres.zqdcajmioiwtwtzaqgjt sslmode=verify-full sslrootcert=C:/secure/path/supabase-ca.crt" -W
   ```

   In that private psql session, with terminal recording/echo disabled:

   ```text
   SET password_encryption = 'scram-sha-256';
   \password scheme_draft_importer
   ```

   Enter the new writer password at the two hidden prompts, then `\q`. This avoids
   a plaintext password in command/SQL Editor history. `\password` still sets a
   credential via PostgreSQL; protect logs and SCRAM verifiers as sensitive too.
   Consult [psql](https://www.postgresql.org/docs/current/app-psql.html) and Supabase's
   [credential logging guidance](https://supabase.com/kb/troubleshooting/provisioning-credentials-without-log-exposure).
   If your managed project does not permit this administrative password operation,
   stop and use its supported secure credential-provisioning channel; do not work
   around it with dynamic SQL containing a secret.
5. After verification/password setup, enable a short import window in SQL Editor
   using this **secret-free** statement, only with your provisioning approval:

   ```sql
   DO $$
   BEGIN
     EXECUTE format(
       'ALTER ROLE scheme_draft_importer LOGIN CONNECTION LIMIT 1 VALID UNTIL %L',
       (clock_timestamp() + interval '2 hours')::text
     );
   END $$;
   ```

   Repeat the role verification query: only LOGIN becomes true; connection limit
   becomes 1 and expiry is about two hours ahead. Expiry prevents new password
   authentication, not already established sessions. Keep the role off Supabase's
   API/authenticator role memberships; do not grant it to anon/authenticated/
   service_role/scheme_api. No REST API key is needed.
6. Inject `SCHEME_IMPORT_DATABASE_URL` and `SCHEME_IMPORT_SSLROOTCERT` into the
   private importer process using your secure environment/secret manager. Pooler
   login is `scheme_draft_importer.zqdcajmioiwtwtzaqgjt`. The importer requires verified
   TLS and a URL matching the exact plan target; percent-encode credential URL
   characters. Keep the existing DATABASE_URL, engine/.env and frontend unchanged.
   Remove the writer environment after use.
7. Run the **read-only** version preflight below. Do not run --commit yet. After
   the approved import window, execute `ALTER ROLE scheme_draft_importer NOLOGIN;`
   as administrator; close the importer connection and expire/revoke its credential
   through your secure process. NOLOGIN does not terminate existing connections.

## Verification query and next preflight

The full query is `ops/draft_writer_VERIFY.sql`. For a compact initial flag check:

```sql
SELECT rolname, rolcanlogin, rolinherit, rolsuper, rolcreatedb, rolcreaterole,
       rolreplication, rolbypassrls, rolconnlimit, rolvaliduntil
FROM pg_roles WHERE rolname = 'scheme_draft_importer';
```

This flag query alone does not verify grants, PUBLIC exposure or policies. Use the
complete file and its 15-ID version query before declaring the role safe.

From engine, after secure credential setup:

```powershell
.\.venv\Scripts\python.exe -m ingestion.postgres_import --collection .phase3-output/catalog15/collection.json --plan .phase3-output/catalog15-postgres-plan.json --check-target
```

This checks the actual writer identity, TLS, RLS/grants and current version maxima
inside a read-only transaction. The provisional plan expects 0→1 for all 15 IDs.
If any maximum or existing content differs, prepare a new plan/digest and obtain
explicit import approval. Even if every maximum is zero, the separate remote-write
approval is still required. Provisioning permission never approves import,
publication, translations or eligibility execution.

## Local validation

`node db-validation/draft-writer-security.test.mjs`: nine tests cover role
attributes, verification SQL, restrictive fences despite broad policies, published
content protection, row_security=off rejection, and transactional rollback on
unrelated PUBLIC schema/table/routine exposure, invalid parent correlation and
schema/composite FK mismatches, the exact live hook/PUBLIC ACL false positive,
direct-call and DDL restrictions, preserved hook ACL/body, malicious same-name and
row-trigger lookalikes, changed body/search_path and widened bindings. The 14 PostgreSQL importer tests also passed
against the revised proposal, including privilege-escalation rejection. No real project changes or
credentials were used. Future live inspection may reveal shared grants requiring
an independently approved decision.

All nine SQL security tests and all 14 importer tests passed after this fix.
The full 15-scheme collection also passed import/repeat/rollback in PGlite with
the reviewed Supabase hook installed locally: 15 drafts, 63 evidence rows, zero
duplicates and zero published versions. Result:
`.phase3-output/catalog15-shared-hook-rehearsal.json`.
