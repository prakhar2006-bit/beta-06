# Future staging import runbook

This phase authorizes local PGlite only. There is no remote adapter, DSN argument,
credential prompt or live-write switch. `--rehearse-local` commits only to a fresh
in-memory database that is closed at process exit. Do not repurpose `scheme_api`.

## Available local commands

From `citizen-scheme-assistant/engine`:

```powershell
# Default: validate files, rehearse all inserts, force constraints, roll back.
node db-validation/staging-import.mjs .phase3-output/phase3b/afe9609bc2b9a0db/draft.json
# Dry-run, commit in memory, repeat as no-op, then discard the local database.
node db-validation/staging-import.mjs .phase3-output/phase3b/afe9609bc2b9a0db/draft.json --rehearse-local
```

The existing venv Python validator and existing db-validation PGlite installation
are required. No new dependencies. Remote flags are rejected. The module's
`expectedVersion` defaults to 0; a nonempty catalogue requires an explicit current
maximum from the preview. An exact successful retry is recognized before allocating
another version. Local runs serialize through a busy guard; this is not a substitute
for locks across remote sessions.

## Preconditions before a future live write

1. A human policy/bilingual reviewer must sign the checklist's **draft-only staging**
   approval, retaining all unresolved policy blockers. No publication approval is
   inferred. Freeze the concrete payload and captures by digest.
2. Implement and independently review a remote adapter in a separately authorized
   task. Preserve dry-run by default. Require explicit write confirmation bound to
   target project/database, stable ID, full bundle digest and expected current
   version; refuse a changed preview or missing confirmation. A suggested approval
   statement is: “Approve draft-only import of in-cen-000002, bundle DIGEST, into
   staging PROJECT/DATABASE at expected maximum version N; no publication.”
   This document is not that approval, and no live command exists today.
3. Obtain explicit operator approval for any required permission/schema setup.
   The local `local_rehearsal.receipts` table is not a Supabase migration. Design
   durable transactional receipt/sidecar storage or an immutable artifact store
   plus atomic database reference before adapting this workflow. Never drop the
   conflicts, bilingual text or disabled-rule metadata to fit existing columns.
4. Only after authorization, an administrator supplies a separate narrowly scoped
   staging writer LOGIN through server-side secret storage. Required connection
   material: exact staging host/port/database, dedicated writer username/password,
   trusted CA certificate path and `sslmode=verify-full`. Do not paste secrets in
   chat, CLI arguments, Git, browser code or the existing runtime `.env`.
   The writer needs reviewed schema USAGE, SELECT for identity/conflict resolution,
   INSERT on import tables and appropriate RLS policies/controlled routines. It must
   not be `scheme_api`, an anon/authenticated client, superuser or service-role key;
   no general UPDATE/DELETE, DDL, role administration or publication privilege.
   Existing RLS will not become writable merely by adding a LOGIN; exact grants and
   policies require a separate reviewed authorization. No credentials requested now.
5. Verify target identity, migration history, TLS, role and least privileges with
   sanitized logs. Start a transaction with bounded timeouts and appropriate
   isolation. Serialize per stable scheme and idempotency key using reviewed locks,
   including the absent-scheme case; handle shared natural-key insertion races.
   Re-resolve IDs inside the lock, compare the expected maximum, then allocate N+1.
   On conflict abort and require a new preview, never silently overwrite.
6. Use parameterized inserts, force deferred constraints, compare all citations and
   source hashes, and persist the complete immutable bundle/receipt. Record the
   source-scoped ingestion key and actual inserted counts. Verify draft-only status,
   unchanged published views, and reader invisibility before commit. No automatic
   retry after a version/content conflict; exact idempotent retries must verify
   stored content and receipt integrity.
7. On failure before commit, roll back the whole transaction. After an uncertain
   commit, inspect the idempotency receipt before retrying. For post-commit errors,
   stop and seek a correction plan; append-only evidence must not be deleted as an
   improvised rollback. Take an authorized staging backup/export beforehand and
   verify the restore procedure separately. Revoke/rotate temporary writer access
   after the approved operation.

The local prototype proves mapping and transactional behavior on embedded
PostgreSQL. It does not prove Supabase networking, actual writer RLS, concurrent
remote imports, durable artifact delivery or policy readiness. Those are explicit
remaining gates, not reasons to obtain privileged credentials during this phase.
