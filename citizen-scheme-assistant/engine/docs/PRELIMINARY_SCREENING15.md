# Fifteen-scheme preliminary screening

All 15 local schemes have bilingual backend questionnaire/result journeys. This
extends the existing local demo mechanism and ordinary-path bridge; it does not
publish records or activate the 28 disabled draft proposals. No frontend, shared
contract, Supabase, authentication or dependency file was changed.

The original five guides remain byte-for-byte unchanged outside `engine/`, and
their fingerprints, questions, boundary handling and outcomes are preserved. The
ten additions are in `app/eligibility/data/preliminary-additions.json`, entirely
within the permitted backend ownership boundary.

## Outcomes and scope

- `ELIGIBLE_LIKELY`: available only for the original five when their existing
  preliminary checks pass. This is never official approval or guaranteed payment.
- `NOT_ELIGIBLE_LIKELY`: a source-supported mandatory condition fails. Only
  applicable, unambiguous failures are decisive; remaining questions stop early.
- `NEEDS_VERIFICATION`: missing/skipped answers, exceptions or incomplete criteria.
  **All ten new guides are explicitly incomplete. Matching every included condition
  still returns this outcome**, with a bilingual explanation of the checks remaining.

The extension loader rejects a new guide with `preliminary_complete=true`, missing
verification requirements, duplicate/missing IDs, unsupported sources or uncited
questions. A source-text check is not a human publication attestation. The source
check date is 2026-10-31; unknown rule effective dates remain null. The existing
90-day freshness check applies per guide, independently of its source publication
date, and expires rather than silently refreshing dates.

`catalog()` preserves its five-guide inventory interface for existing repository
checks. Runtime calls use `catalog(include_additions=True)`, validating the full
15-ID set. Full backend tests cover the extension as well as the original inventory.

## Implementation matrix

Counts are observed normal paths, not fixed UI targets. A decisive failure or an
exception can finish earlier. The normal samples below are synthetic test inputs.

| ID suffix | Scheme | Questions | Normal result | Remaining verification |
| --- | --- | ---: | --- | --- |
| 000001 | PMJJBY | 4 | ELIGIBLE_LIKELY | Existing provider checks, age convention, coverage terms |
| 000002 | PMSBY | 4 | ELIGIBLE_LIKELY | Existing age/termination and provider checks |
| 000003 | PM-SYM | 9 | ELIGIBLE_LIKELY | Existing income-boundary, contribution and exclusion exceptions |
| 000004 | PMUY | 4 | NEEDS_VERIFICATION | Household/deprivation declaration, duplicate connection and current OMC process |
| 000005 | IGNOAPS | 2 | NEEDS_VERIFICATION | State selection, BPL/age records, continuation exceptions and state additions |
| 000006 | PM-KISAN | 3 | NEEDS_VERIFICATION | Complete family exclusions, land dates/records and e-KYC |
| 000007 | Atal Pension Yojana | 6 | ELIGIBLE_LIKELY | Existing age-boundary, tax history and bank checks |
| 000008 | Sukanya Samriddhi | 6 | ELIGIBLE_LIKELY | Existing family/birth exceptions and post-office/bank checks |
| 000009 | PMAY-G | 5 | NEEDS_VERIFICATION | Remaining revised exclusions, deprivation and official selection |
| 000010 | PM-JAY | 1 | NEEDS_VERIFICATION | Alternative beneficiary routes, State implementation and enrolment |
| 000011 | PM Vishwakarma | 6 | NEEDS_VERIFICATION | Full trade list, family record, repaid-loan exceptions and CSC verification |
| 000012 | PM SVANidhi | 2 | NEEDS_VERIFICATION | CoV/LoR alternatives, local coverage, tranche and lender checks |
| 000013 | PM MUDRA | 2 | NEEDS_VERIFICATION | Business appraisal, credit category and Tarun Plus repayment condition |
| 000014 | PM Surya Ghar | 4 | NEEDS_VERIFICATION | Current MNRE/DISCOM rules, prior subsidy and technical feasibility |
| 000015 | Kisan Credit Card | 1 | NEEDS_VERIFICATION | Cultivator/tenant/group/allied route and bank assessment |

PM-JAY's age question identifies the senior route. **Under 70 is never a blanket
rejection**; it directs the citizen to official lookup of alternative routes.
KCC does not impose universal land ownership or invent an age limit. Missing
CoV/LoR, unconfirmed BPL listing and previous business credit with possible
exceptions lead to verification. PMAY-G does not reintroduce deleted two-wheeler,
refrigerator or landline exclusions.

## Official evidence reviewed

Each included condition carries source IDs; result sections preserve those IDs,
official URLs and checked dates. Original draft bundles, ledgers and conflicts
are unchanged. No restricted-site bypass or myScheme scraping was used. Only
permitted public official text was inspected. These are deliberately limited
screens, not a claim that the complete legal scheme was reviewed.

| Guide | Official evidence and publication date | Clauses used / deliberate limits |
| --- | --- | --- |
| PMUY | [PMUY official portal](https://www.pmuy.gov.in/index.aspx), publication date unavailable; corroborated with [official FAQ](https://www.pmuy.gov.in/faq.html) | Adult woman, household LPG and deprivation declaration; no conflicting cash-assistance amount asserted |
| IGNOAPS | [PIB NSAP overview](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=155928&id=155928&lang=2&reg=48), 2025-11-07 | Central age/BPL summary; no invented nationwide document checklist or State-specific sanction rule |
| PM-KISAN | [PIB PM-KISAN](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=156092&lang=2&reg=3), 2025-11-19 | Landholding-family and exclusion indicators; incomplete exceptions never treated as definitive rejection |
| PMAY-G | [PIB revised exclusions](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2080091&lang=2&reg=48), 2024-12-03 | Pucca roof/wall, more than two rooms, government employee, member income above ₹15,000/month and motorised three/four-wheeler exclusions; remaining checks unresolved |
| PM-JAY | [PIB coverage overview](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=160081&lang=3&reg=3), 2026-09-22 | Senior route plus explicit recognition of alternative routes; no universal age gate or beneficiary lookup impersonation |
| PM Vishwakarma | [PIB eligibility overview](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=155216&id=155216&lang=2&reg=3), 2025-09-16 | Entry age, traditional work and family/employment/credit indicators; repaid-loan and trade classification require verification |
| PM SVANidhi | [PIB FAQ](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2267102&lang=2&reg=48), 2026-05-30 | Street-vendor scope and CoV OR LoR path; missing identification is not automatic rejection |
| PM MUDRA | [PIB PMMY](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2240159&lang=1&reg=3), 2026-03-14 | Business purpose, requested amount and lender/category verification; no credit sanction inferred |
| PM Surya Ghar | [PIB application overview](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2010757&lang=2&reg=48), 2024-03-01 | Citizenship, roof, connection and prior-subsidy indicators; the older overview is insufficient to confirm all current operational rules |
| KCC | [PIB KCC overview](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=157771&lang=1&reg=3), 2026-03-11 | Owner/tenant/group and allied-activity routes; no conflation of interest-subvention or collateral thresholds with a sanctioned limit |

New English/Hindi text is project-authored and requires human translation review;
it is never labelled an official translation. No human reviewer or government
approval was invented. A reviewed source passage can support a narrow check while
the overall scheme and its translations remain unapproved.

## Documents and links

New guides return `required_documents.status=partial` when supported document
items exist; otherwise `unavailable`. The partial checklist message is bilingual.
IGNOAPS, PMAY-G, PM-JAY and MUDRA have no complete national checklist established
here; no mandatory documents were fabricated for those guides.

Application steps are source-backed provider guidance. Only established official
information URLs are returned, with `link_kind=information`; they are not claimed
to be online submission endpoints. Missing URLs return an empty list with an
explicit `unavailable` status. A conditional KCC crop-route document is not a
universal land-ownership requirement. No citizen document upload is requested.

## Run and verify

From `engine`, after stopping the current backend instance if starting another:

```powershell
$env:SCHEME_APP_ENV='development'
$env:SCHEME_DEMO_ENABLED='1'
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload --no-access-log --no-proxy-headers
```

Both `/api/v1` and `/api/v1/demo` support the same local catalogue, detail,
questionnaire `start/next/answer`, and `results/explain` workflows. Client-held
state and the existing response shapes are reused. `eligibility_execution_enabled`
remains false; `screening_available` and `preliminary_screening_enabled` are true
for all 15 in local demo mode. Public `/api/v1/eligibility/evaluate` still requires
the unchanged trusted published-policy provider. Production and nonlocal requests
never receive these local drafts or preliminary substitutions.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test "db-validation/*.test.mjs"
.\.venv\Scripts\python.exe -B tests/verify_screening15_http.py --base http://127.0.0.1:8001
.\.venv\Scripts\python.exe -B tests/verify_screening15_http.py --base http://127.0.0.1:8001 --prefix /api/v1/demo
```

The HTTP verifier makes real loopback requests with synthetic citizen inputs.
Each run verifies 30 bilingual complete journeys and seven additional decision
cases, deterministic repeat results, detail paths, citations, disclaimers, input
rejection and honest unavailable sections. It does not mock server responses,
query Supabase, or store answers/state. Optional `--output` stores summary counts
and outcomes only; use the ignored `.phase3-output/` directory.

Actual final verification: **181 Python tests passed**, **35 isolated PGlite
tests passed**, and both HTTP-verifier runs passed on the real port-8001 service:
**60 full bilingual journeys plus 14 additional decision cases**. The API baseline
(16 operations, 42 components), existing five-guide inventory guard, actual
15-bundle validation and `pip check` passed. All **7,780 frontend files** matched
the task's initial SHA-256 snapshot, including ignored files. No pre-existing
changed/untracked path disappeared, nothing is staged, and the existing
`chore/backend-collaboration-guards` branch and HEAD remain unchanged. No commit,
push, live database write, permission change or publication was performed.

No frontend install, build, UI/auth repair or physical microphone test was
performed. The current frontend already accepts these question types, preliminary
status enums and guidance sections; no frontend change is required for the backend
workflow. UI or voice defects remain with the frontend owners. Full catalogue
discovery on a fresh machine still requires the existing private catalogue archive,
as explained in `BACKEND_HANDOVER.md`; questionnaires use tracked guide data.
