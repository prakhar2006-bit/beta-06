# Five-scheme draft status and publication checklist

Checked 2026-10-31. Scope: actual Phase 3D bundle files, their permitted source
captures/research ledgers, source spot checks, and isolated PGlite. **No live
Supabase access or writes; production population is pending explicit approval.**

## Actual bundle structure and validation

Each draft JSON is an unpublished preparation envelope with `mode`,
`publish_allowed:false`, `eligible_for_execution:false`, `rows`, `verification`,
`rule_review`, `original_record`, `unresolved_archive_conflicts`,
`bilingual_content` and audit digests. `rows` maps actual table names to UUID-keyed
rows, not one flattened scheme object. Source captures live beside each draft.
No scripts from source archives are executed.

All five collection entries and captures validate using the existing verifier.
The phase3d-repro payloads match all five digests exactly. All 21 rule nodes remain
UNCERTAIN and disabled in the sidecar; 17 original conflicts are preserved.
Version 1 and all payload UUIDs are provisional until importer resolution.

| Scheme | Stable ID | Benefits / documents / routes | Rule nodes | Local SQL result | Publication |
| --- | --- | --- | --- | --- | --- |
| PMJJBY | in-cen-000001 | 1 / 0 / 0 | 4 | Draft v1 | Blocked |
| PMSBY | in-cen-000002 | 3 / 1 / 0 | 5 | Draft v1 | Blocked |
| PM-SYM | in-cen-000003 | 1 / 3 / 1 | 5 | Draft v1 | Blocked |
| PMUY | in-cen-000004 | 1 / 2 / 1 | 4 | Draft v1 | Blocked |
| IGNOAPS | in-cen-000005 | 2 / 0 / 0 | 3 | Draft v1 | Blocked |

Row counts are stored draft content, not certification of document completeness
or working application links. In particular PM-SYM's mobile-number item is contact
information, not a document upload. No citizen data is imported or collected.

Exact importer rehearsal: 5 schemes, 5 draft versions, 5 ingestion receipts,
53 evidence rows, 0 published versions; repeated import added 0 rows. Default
rollback and a last-scheme constraint failure both left 0 scheme rows. Details:
`engine/.phase3-output/five-scheme-postgres-rehearsal-final.json` (ignored local output).

## Official source checks and remaining uncertainty

Existing detailed claim assertions, effective dates (including unknown/null),
evidence locators and verification statuses remain in the bound research ledgers
and PHASE3D_FIVE_SCHEME_REPORT.md. No approval or verification date was silently
rewritten during import preparation. The following bounded web spot checks were
accessible on 2026-10-31; they corroborate summaries but do not establish a complete
amendment chain, approved translations or executable policy.

| Scheme | Official evidence inspected | Findings and remaining blockers |
| --- | --- | --- |
| PMJJBY | [DFS FAQ](https://financialservices.gov.in/pmjjby), page dated 2025-12-24; existing PIB capture | Current FAQ corroborates life cover, annual premium and participating-account/consent structure. Exact birthday interpretation, complete current amendments, lien/rejoining/pro-rata/commencement treatment, latest provider KYC/nominee/claim forms and application route need policy review. Three archive conflicts remain. |
| PMSBY | [DFS FAQ](https://financialservices.gov.in/pmsby), page dated 2025-12-24; existing PIB capture | Accident/death/disability cover and auto-debit structure corroborated. Entry range versus termination birthday language and cover-start history remain unresolved. Complete current provider forms/KYC and application endpoint missing. Two archive conflicts remain. DFS raw-copy permission still not established; no new raw snapshot copied. |
| PM-SYM | [Ministry/PIB release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2293891&lang=2&reg=48), 2026-08-03; existing 2025/2026 captures | Entry-age, unorganised-worker pension and matching-contribution summary corroborated. Income boundary differs from other summaries; the exclusion paragraph's logical wording still requires reconciliation. Contribution-table discrepancy, pension/social-security coverage scope, occupation/citizenship and current mandate/forms remain. Four conflicts preserved. |
| PMUY | [PMUY FAQ](https://www.pmuy.gov.in/faq.html), no publication/effective date established; existing PIB capture | Poor-household adult-woman declaration/no-family-LPG summary, connection components and application/document descriptions corroborated. Current dated SOP/phase, older category routes versus declaration, household/eKYC definitions, exceptions, financial assistance and FY2026-27 subsidy remain unapproved. Five conflicts preserved. No new raw FAQ copy made. |
| IGNOAPS | [Ministry/PIB elderly-schemes release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2226202&lang=1&reg=6), 2026-02-11; existing NSAP capture | BPL/age and central assistance bands corroborated. Legacy BPL-list/category exceptions, exact age reference, title/date identity, state implementation/documents/routes/top-ups require review. Three conflicts preserved. |

All English/Hindi descriptions and question adaptations still require independent
human review. Existing official-title/excerpt provenance is retained, but it does
not approve newly drafted translations. The normalized schema cannot represent
all bilingual child fields; sidecar preservation is essential. There are no
reviewer attestations or server execution approvals for these real drafts.

## Publication and execution checklist

Every item below blocks public use when relevant; importing a draft satisfies none
of the human approval requirements automatically:

- [ ] Resolve each scheme's retained archive conflicts and explicit policy blockers;
  record the disposition and exact authoritative evidence/effective dates.
- [ ] Review complete deterministic conditions and coverage/termination semantics,
  including boundaries, exclusions and manual checks. Unverified rules stay off.
- [ ] Confirm current benefits/premiums; distinguish insurance cover, contributions,
  central pension shares and state top-ups from guaranteed disbursement.
- [ ] Obtain current application routes and complete provider/state document lists,
  verify actual official URLs and required permissions for reused evidence.
- [ ] Review English and Hindi text independently; resolve bilingual child-storage
  limitations through a separately approved schema/content design if necessary.
- [ ] Record genuine policy reviewer approval and reviewed bilingual translations;
  pass the existing database draft→reviewed guard (jurisdictions/tree/evidence).
- [ ] Obtain explicit publication authorization for the exact immutable version;
  transition reviewed→published through the existing workflow. Do not grant the
  importer or scheme_api permission to perform this transition.
- [ ] Produce the actual published policy projection hash, review completeness,
  dates and source provenance; add a real server-owned execution approval bound
  to that exact hash/version. Publication alone never enables eligibility.
- [ ] Attest published benefit/document/application guidance and approved-language
  hashes through the existing guidance mechanism. Missing sections stay unavailable.
- [ ] Re-run the local reviewer preview and deterministic API tests, then test the
  authorized live published catalogue, questionnaire and results in a browser.

Optional improvements after blockers: richer presentation, reviewed voice UX,
additional state schemes, and performance tuning. They do not justify weakening
the existing approval gates.

## Why the website remains empty

The public read-only repository reads published views only. Importing these five
drafts deliberately leaves them excluded. Drafts cannot feed approved questionnaire
decisions; no React-only catalogue or mock result is added. Missing execution or
guidance approval yields the existing unavailable/NEEDS_VERIFICATION behavior.

The next authorized operation is writer provisioning/inspection followed by the
exact draft-only plan in SUPABASE_DRAFT_IMPORT_RUNBOOK.md. Human review and separate
publication/execution/guidance approval are subsequent operations. Real five-scheme
browser end-to-end eligibility remains blocked, not claimed as verified.

## Regression results

- 129 Python tests passed (including 13 new PostgreSQL importer tests). Existing
  trusted-provider/questionnaire/results tests use explicitly approved synthetic
  fixtures; they do not approve or activate these five government drafts.
- 27 existing isolated database tests passed: 8 catalogue, 9 single staging,
  6 batch staging, 3 reviewer probes and 1 payload constraint check.
- 13 frontend tests and the Vite production build passed.
- Running backend health at `http://127.0.0.1:8001/health` returned 200 with CORS
  allowing `http://localhost:3001`; OpenAPI exposed the questionnaire/results
  endpoints and the frontend at port 3001 returned 200.
- No live catalogue/database-health query, government-rule execution or remote
  write occurred. These checks are not real five-scheme browser end-to-end proof.
