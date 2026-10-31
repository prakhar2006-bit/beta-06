# Phase 3 local preparation and Phase 3B gates

Only local dry-run preparation is implemented. No SQL writer, database dependency,
credentials, network client, publishing action or archive-script execution exists
in `ingestion/prepare.py`. The module uses Python's standard library; no new
dependency is required. Existing FastAPI modules and migrations are unchanged.

## Run from engine

```powershell
.\.venv\Scripts\python.exe -m ingestion.prepare --archive ..\output.zip --dry-run --output-root .phase3-output\new-run
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The completed audit output is:
`.phase3-output/verified/b6c4262434a8dd3e/manifest.json` and `readiness.json`.
`extracted/` preserves current raw artifacts and unopened nested ZIP copies;
`quarantine/` retains script bytes with `.disabled` suffixes. All are Git-ignored.
Never execute these scripts. Nested archives are recursively safety/CRC inspected
and their JSON/CSV/text files parsed for audit, not merged as additional schemes.

Output directories are exclusive: rerunning against an existing destination
fails instead of overwriting it. Choose a new ignored output root for another
run. The same archive yields byte-identical manifest content in different output
roots: no current timestamps, machine paths or random IDs enter the manifest.
The archive SHA-256 identifies the input; record hashes identify semantic JSON.

## Validation performed

- ZIP preflight rejects traversal, absolute paths, drive/ADS names, Windows reserved
  names, trailing dot/space components, backslashes, Unicode/case collisions,
  encryption, symlinks/special files, executable binaries and excessive expansion.
- Limits: 50 MiB archive/cumulative expanded budget, 10 MiB per entry, 1,000 total
  nested entries, nesting depth at most two and maximum 200:1 compression ratio.
- CRC is checked by reading each bounded entry. Scripts are flagged/quarantined,
  never imported or executed. No extractall call is used. Output path links and
  Windows junctions are rejected; files use exclusive creation.
- JSON rejects duplicate keys, nonfinite numbers, invalid encoding and syntax.
  CSV rejects inconsistent row widths, duplicate headers and malformed embedded
  JSON cells. All current/nested JSON/CSV/Markdown artifacts were inspected.
- Independently validate record identity, classification, collection shape, rule
  IDs/text, source joins and exact URL consistency. Duplicate IDs, malformed
  records and missing structural fields fail before extraction/output creation.
- The detailed subset must agree exactly with canonical scheme_records.json.
  Current artifact_manifest file lengths and checksums are independently checked.
  Archive validation_report and claimed review statuses are untrusted inputs.
- The supplied schema's required keys are checked. This is explicitly NOT a full
  JSON Schema Draft 2020-12 validation engine. No code from the archive validator
  or remote schema references is executed. Independent domain checks define the
  accepted preparation format; full standards validation can be added separately.

The manifest retains every original scheme field, complete source register,
conflict assertions, proposed disabled conditions/questions, auxiliary parsed JSON
artifacts and hashes of all raw files. Missing content remains missing. Local
artifact integrity does not establish official-document authenticity or recency.
Preparation readiness warnings do not mean a structurally valid batch is ready
to write to Supabase.

## Required before Phase 3B

1. Human reviewer verifies current official guidelines, full amendment chains,
   source issuer/authenticity, current-phase applicability and access/reuse policy.
   Resolve the 17 conflict groups with retained evidence, including age boundaries,
   premiums/coverage dates, pension exclusions and announced renaming dates.
2. Obtain permitted original source snapshots, actual media type/hash/retrieval
   provenance and valid evidence locators. Separate publication, effective,
   retrieval, extraction and human-verification dates; preserve date precision.
3. Complete real descriptions and reviewed English/Hindi translations. The four
   approved Hindi names alone do not satisfy bilingual content requirements.
4. Review mappings in PHASE3_SCHEMA_MAPPING.md. Resolve organization and
   jurisdiction keys, permanent stable-ID ledger, source enums, document types,
   benefit vs premium semantics, application mode and URLs. Do not import planning
   coverage rows or excluded umbrella/institution entries as schemes.
5. Review complete rules AND exclusions as one applicable version. Define attribute
   vocabulary, units, individual/household scope, reference dates and missing-input
   handling. Every predicate needs source evidence. Do not enable draft proposals.
6. Obtain explicit approval for a separate least-privilege administrative import
   workflow/connection. Do not request/generate privileged credentials in Phase 3A,
   alter permissions or grant write access to scheme_api. Decide staging, rollback,
   transaction boundaries and manifest/source-scoped idempotency keys first.
7. Implement a separately reviewed writer that imports drafts only, enforces
   all constraints and can compare/retry without duplicates. Keep raw conflict and
   unmatched fields in a retained review sidecar; never silently drop them.
8. Test that writer against a disposable local database using synthetic fixtures,
   then review a concrete import preview before any approved remote write.
   Publication is a later explicit human action through the existing workflow.

All 16 schemes currently require human review. This change does not claim any
record is importable without completing the mapping/evidence blockers.
