# Version Beta 9.0: local reviewer preview

This is an offline CLI, not an administrative/public HTTP API. It reads existing
verified draft bundles and the server-owned execution-approval manifest. No .env,
live connection, reviewer LOGIN, migration or permission change is needed.

From `engine`, with existing Python/PGlite dependencies installed:

```powershell
.\.venv\Scripts\python.exe -m reviewer.preview --local-review --collection .phase3-output/phase3d/collection.json --output .phase3-output/phase4e-new-run --as-of 2026-10-31
```

Choose a fresh output directory inside ignored `.phase3-output`. Missing input is
an error, never a reason to create a substitute scheme. `--local-review` is required
before files are read. It acknowledges local reviewer intent; filesystem access is
the security boundary, not this flag. There is no remote/DSN/credential switch.
No public route exposes reviewer data. Reviewer identities and artifact paths are
not included in the report; reviewer-reference presence is reported as a Boolean.

Outputs are `readiness.json` and `readiness.md`. The JSON includes scope/live_verified,
stable ID, provisional local version UUID/number, lifecycle/publication status,
review metadata presence, translation statuses, unresolved claims/conflict IDs,
missing rule evidence, uncertain/disabled node counts, missing guidance item
attestations, runtime approval status, hashes where available, blockers and
ready_for_publication. These are local observations, not an authorization to publish.

The preview reuses collection/bundle validation and the existing local importer.
PGlite applies unchanged migrations only in a fresh disposable in-memory database.
`guard_version` runs against **temporary copies** of version metadata and actual
isolated child rows. Probe operations are rolled back and original version rows
are compared before/after. No catalogue version is approved or published. The
database guard reports its first real failure; other known policy blockers remain
visible from the source ledger. A successful SQL probe is not policy approval.

TrustedPolicyProvider and the results service are reused with injected local
snapshot repositories for execution/guidance diagnostics. No second eligibility
engine is introduced. SQL publication readiness and execution approval are reported
separately: the database workflow does not itself require the execution manifest,
rule completeness or all guidance attestations. Unverified rules and unresolved
policy review must not be bypassed merely because SQL permits a transition.

Drafts have no actual published projection or publication timestamp, so executable
policy/guidance hashes are null. The verified original payload hash is reported;
the CLI does not fabricate publication metadata to manufacture a runtime digest.
The pure private snapshot preview can inspect genuinely available published
exports using the existing canonical policy/guidance hash functions. No export
from live Supabase was requested or fetched in this phase.

The five actual local drafts were found. The final artifact is under
`.phase3-output/phase4e-final/`. All five are draft version 1, lifecycle unknown,
with unreviewed English/Hindi translations, uncertain disabled rule nodes and no
execution/guidance approval entries. All isolated review-transition probes fail
with `Reviewed English and Hindi translations required`. Exact scheme-specific
remaining questions are in PHASE4E_PUBLICATION_READINESS.md. These findings are
implemented/local-tested, **not live-verified**; they do not assert the current
contents of Supabase.

Run tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_reviewer.py -v
node db-validation/reviewer-preview.test.mjs
```

Final regression verification passed: 116 Python tests and 27 isolated database
tests (8 catalogue, 9 single-scheme staging, 6 batch staging, 3 reviewer probes,
1 payload constraint check), 143 total. No live database was accessed.

Eight focused Python tests and three SQL-probe tests cover incomplete/stale
approvals, missing/stale guidance attestations, fully reviewed synthetic snapshots,
SQL guard success/failure without original mutations, denied reader access and no
public reviewer endpoints. Existing migrations and APIs remain unchanged. The only
runtime adjustment is optional guidance-repository injection in TrustedPolicyProvider;
its default production behavior is preserved.

Next backend phase: a controlled human policy/bilingual review workflow that
records resolutions and exact version/digest decisions. Live exports/imports,
publication and credential provisioning require separate explicit authorization.
Frontend integration may proceed against public APIs and isolated synthetic test
fixtures while the real drafts remain blocked.
