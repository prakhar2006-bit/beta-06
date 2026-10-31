# Fifteen-scheme catalogue implementation and verification

Checked 2026-10-31. This report distinguishes real source-backed drafts, isolated
SQL rehearsal, synthetic workflow tests and live read-only observations.

**Deployment update:** the backend owner completed the live import and returned
the requested Supabase SQL verification: 15 schemes, 15 draft version-1 records,
63 evidence rows and zero published versions, covering in-cen-000001 through
in-cen-000015. The historic preparation/rehearsal observations below describe the
pre-import stage. No credentials were shared with the agent; the private-row
verification was executed in the owner's SQL Editor session. Handoff API checks
confirmed drafts remain excluded from the published catalogue.

## Counts

| Measure | Result |
| --- | --- |
| Real schemes collected/prepared | 15 (original five unchanged, ten added) |
| Structurally validated bundles | 15 |
| Reproducibility comparison | All 15 payloads identical in a second preparation |
| Imported in isolated PGlite | 15 draft schemes / 15 versions / 15 receipts |
| Evidence rows in local rehearsal | 63 |
| Duplicates after repeating import | 0 |
| Live Supabase schemes now imported by owner | 15 drafts (SQL result returned by owner) |
| Live schemes published by this work | 0 |
| Live published catalogue observed | Empty, through restricted published views |
| Publication-ready drafts | 0 of 15, using existing reviewer preview |

The local rehearsal was separate from the now-completed owner-executed live import.
All 28 stored rule proposals remain UNCERTAIN and disabled in
the sidecars. There are 22 retained policy-conflict objects (17 inherited and 5
new); an absent conflict object does not mean the full policy is resolved.

## Scheme inventory and readiness

All IDs were checked against the existing local draft collection. Their live
availability still requires the writer preflight; provisional IDs are not a claim
that the restricted reader has searched unpublished database records.

| ID suffix | Scheme | Document / route rows | Important remaining gaps |
| --- | --- | --- | --- |
| 000001 | PMJJBY | 0 / 0 | Birthday boundary; signed current amendments; lien/rejoining/commencement; current provider KYC/nominee/claim forms and route; English/Hindi review |
| 000002 | PMSBY | 1 / 0 | Age-70 interpretation, cover-start amendments, provider KYC/forms/application, bilingual child representation |
| 000003 | PM-SYM | 3 / 1 | Income boundary, contribution-table discrepancy, exclusion logic, current occupation/mandate verification |
| 000004 | PMUY | 2 / 1 | Current phase/SOP, household and eKYC definitions, declarations versus historical categories, current financial support |
| 000005 | IGNOAPS | 0 / 0 | Legacy BPL exceptions, age reference, state process, documents, route and top-ups |
| 000006 | PM-KISAN | 2 / 1 | Full exclusions, family/land reference dates, state records; direct portal inspection timed out |
| 000007 | Atal Pension Yojana | 0 / 0 | Upper birthday wording, current taxpayer amendment, contribution/KYC/nominee procedure; DFS observations retained separately |
| 000008 | Sukanya Samriddhi | 3 / 1 | Guardian/residency and multiple-birth exceptions, current interest quarter, document ownership/alternatives |
| 000009 | PMAY-G | 0 / 0 | Current selection framework, complete exclusions and housing deprivation, documents, assistance amounts and application route |
| 000010 | AB PM-JAY | 0 / 0 | Alternative beneficiary routes, state coverage, senior-route choices, documents; NHA page returned 403 |
| 000011 | PM Vishwakarma | 1 / 1 | Repaid-credit exceptions, full trade/family definitions, current forms, staged-credit conditions |
| 000012 | PM SVANidhi | 1 / 1 | Post-restructuring identification cutoffs, local rollout, LoR/CoV alternatives, current portal endpoint |
| 000013 | PM MUDRA | 0 / 1 | Lender appraisal, KYC/business evidence, Tarun Plus repayment prerequisite and current application endpoints |
| 000014 | PM Surya Ghar | 2 / 1 | Current operational guidelines/rates, DISCOM and ownership exceptions, previous-subsidy rules |
| 000015 | Kisan Credit Card | 1 / 1 | Tenant/group/allied routes, lender documents; distinguish sanctioned limits, MISS and collateral thresholds |

All full IDs are `in-cen-` plus the suffix. Document/route counts are draft rows,
not evidence of a complete current checklist or an attested application URL.
Missing lists/routes are explicit unknowns, never fabricated. Contact/consumer
details describe information required by government portals, not information our
assistant stores. All new document rows are conditional on their cited route/stage.

## Sources, evidence and translations

The existing myScheme access-policy audit prohibits bots/automatic collection
without written permission. Its discovery URL and restriction are retained in
`ingestion/catalog15_research.json`; no scheme page, private API, CAPTCHA or
blocked website was bypassed. New bounded captures were serial, at least one
second apart, capped at 3 MB with timeouts and no blind retry. PIB's
[copyright policy](https://www.pib.gov.in/content/132_2_Copyright-Policy.aspx?lang=1&reg=1)
permits attributed reuse of its own material, excluding third-party content.
Captures are private review evidence, not a license to republish embedded images.

Ten captured primary publications support the ten new drafts:

| Scheme | Publication | Publication date |
| --- | --- | --- |
| PM-KISAN | [21st instalment and eligibility/verification backgrounder](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=156092&lang=2&reg=3) | 2025-11-19 |
| APY | [Salient Features PDF](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/may/doc202558551701.pdf) | Not established; not inferred from URL |
| SSY | [Savings and account-opening backgrounder](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2216748&lang=1&reg=3) | 2026-01-21 |
| PMAY-G | [Revised exclusion criteria](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2080091&lang=2&reg=48) | 2024-12-03 |
| AB PM-JAY | [Universal health coverage backgrounder](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=160081&lang=3&reg=3) | 2026-09-22 |
| PM Vishwakarma | [Eligibility, registration and support](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=155216&id=155216&lang=2&reg=3) | 2025-09-16 |
| PM SVANidhi | [Restructured scheme FAQ](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2267102&lang=2&reg=48) | 2026-05-30 |
| PM MUDRA | [Loan categories and lender requirements](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2240159&lang=1&reg=3) | 2026-03-14 |
| PM Surya Ghar | [Eligibility and application stages](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2010757&lang=2&reg=48) | 2024-03-01 |
| KCC | [Beneficiary categories and onboarding](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=157771&lang=1&reg=3) | 2026-03-11 |

Capture dates, exact bytes and SHA-256 values are recorded in the ignored capture
manifests. Publication dates are not rule-effective dates; unknown effective dates
remain null. Source summaries are not proof that every policy amendment is covered.
DFS's [APY FAQ](https://financialservices.gov.in/atal-pension-yojana) was also read
without a new raw copy; its completed-age-40 wording is a retained conflict.
Departmental authority and geographical conditions are in each research record.
Country-level junction rows do not erase rural, local-rollout or route restrictions.

English and Hindi names, descriptions, benefit summaries, eligibility summaries,
document labels, application explanations, geography and proposed questions are
prepared. **All newly drafted translations require independent human review and
are not official translations.** No reviewed status was asserted. The existing
schema's child-language limitations remain; bilingual child content stays in the
bound sidecars rather than being silently discarded. Three complex schemes
(PM-JAY, MUDRA, KCC) intentionally have no proposed executable predicate.

## Live target inspection

Explicit read-only inspection confirmed configured project
`zqdcajmioiwtwtzaqgjt`, session-pooler host
`aws-0-ap-northeast-2.pooler.supabase.com:5432`, database `postgres`, login
`scheme_api`, transaction_read_only `on`, and no published schemes.
`scheme_draft_importer` does not exist in pg_roles. No role/policy was provisioned.

The reader deliberately cannot see base-table drafts. Consequently version maxima
and full stable-ID availability are **not live-verified**. The new plan expects
current version 0 and creates draft version 1; an authorised writer preflight must
confirm those expectations before import approval. If any differ, stop and prepare
a new plan/digest. Never reuse the old five-scheme approval digest.

## Tests and limitations

The local 15-scheme SQL rehearsal imported/repeated/rolled back the actual bundles
and retrieved PMJJBY's English/Hindi titles and draft status directly from PGlite.
It verified public-view exclusion and no activated rules. The existing reviewer
preview applied the unchanged SQL guards and reported 0/15 publication-ready.

Separate, clearly labelled synthetic PMJJBY-shaped fixtures exercise the existing
trusted provider, adaptive questionnaire and result service. Four API workflow
tests cover English/Hindi completion, decisive failure, unknowns, source-backed
synthetic explanations, document/application rendering contracts, invalid status
injection, exclusion of real unpublished PMJJBY and loopback-only fixture access.

Six additional local HTTP journeys use the **real frontend service/controller**
against that isolated FastAPI fixture: eligible/ineligible/uncertain in both
languages. Eligible/uncertain journeys ask three distinct questions; decisive
failure asks one. Recognized yes/हाँ is converted locally but not submitted until
an explicit controller action. This simulates recognition and checks confirmation
semantics; it does not test a microphone, browser permission or real speech vendor.
Synthetic guidance is labelled test-only; no real PMJJBY document checklist or
application link is invented.

Final regression results: **136 Python tests**, **27 existing database tests**
(8 catalogue, 9 single staging, 6 batch staging, 3 reviewer probes, 1 payload),
**13 frontend tests** and the production build passed. The six synthetic HTTP
journeys passed separately. Existing APIs, read-only API access and publication
gates remain unchanged. Seven Python tests were added for catalogue expansion and
the controlled first-scheme workflow.

Both browser/computer-use runtimes failed initialization with `failed to write
kernel assets ... path not found`. **No rendered-browser or microphone test is
claimed.** The production UI/backend remain at ports 3001/8001. The fixture uses
8011 and is not added to production routes or execution approvals.

## Stored artifacts and next gates

- `engine/.phase3-output/catalog15/collection.json`: validated 15-bundle index.
- `engine/.phase3-output/catalog15-repro/`: independent deterministic preparation.
- `engine/.phase3-output/catalog15-captures/`: bounded capture manifests and bytes.
- `engine/.phase3-output/catalog15-review/readiness.json` and `.md`: actual local reviewer results.
- `engine/.phase3-output/catalog15-postgres-rehearsal-verified.json`: local SQL results.
- `engine/.phase3-output/catalog15-target-readonly.json`: live read-only observations.
- `engine/.phase3-output/catalog15-postgres-plan.json`: new, provisional approval plan.

Before public use, resolve scheme-specific policy/document/application gaps, review
both languages, obtain actual reviewer attestations, pass the unchanged SQL
draft→reviewed→published workflow with explicit publication authorization, and
approve the exact published policy/guidance hashes through the server manifest.
Publication alone does not enable execution. PMJJBY must complete its form/provider
and birthday/amendment review before genuine publication approval can be requested.

Next operation requiring approval: provision the reviewed separate writer role/RLS
proposal, securely issue credentials, and run read-only writer preflight. Then
approve the final exact 15-scheme plan before any remote INSERT. Commands and scope
are in CATALOG15_RUNBOOK.md. No secrets, migrations, API grants or frontend files
were modified for this expansion, and nothing was committed or pushed.
