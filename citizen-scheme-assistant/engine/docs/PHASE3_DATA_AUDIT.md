# Phase 3 data audit

Audited locally on 31 October 2026. Statements about schemes below describe the archive, not independently verified government rules. No website requests, source scraping, archive-script execution or database connections were performed in this phase.

## Input and safety

- One workspace copy found: `citizen-scheme-assistant/output.zip` (not inside engine).
- Archive: 417,540 bytes; 28 outer entries (25 files, 3 directories); 1,371,461 declared outer uncompressed bytes.
- SHA-256: `b6c4262434a8dd3e82f2c03b60c476c96f09b34c2d7ae561413ecd8fa6648e94`.
- No corrupt CRCs, unsafe paths, duplicate/case-colliding entry names, symlinks, executable binaries or size/ratio violations detected.
- Three outer Python files were statically inspected as text/AST, never run: `build_batch.py`, `validate_and_package.py`, and `output/history/build_batch_initial.py`. Nested ZIPs also contain reproduction scripts; all remain unexecuted. The archived validator writes/repackages artifacts, so running it would not be a read-only audit.
- Both nested ZIPs contain 22 files each. The current nested copy is redundant packaging; the historical initial batch is not an extra set of schemes. Neither is merged into the active dataset.

```text
output.zip
  output/batch_001/                 20 current JSON/CSV/Markdown files
  output/batch_001.zip              current packaged copy, 22 entries
  output/history/batch_001_initial.zip  historical packaged copy, 22 entries
  output/history/build_batch_initial.py  quarantined
  build_batch.py                      quarantined
  validate_and_package.py              quarantined
```

## Independently computed counts

| Measure | Count |
| --- | ---: |
| citation_occurrences | 141 |
| conditions | 20 |
| conflicts | 17 |
| detailed_drafts | 5 |
| discovery_only | 11 |
| human_review_required | 16 |
| missing_hindi_names | 12 |
| official_host_citation_occurrences | 141 |
| official_host_source_rows | 65 |
| official_host_unique_urls | 65 |
| publication_ready | 0 |
| schemes | 16 |
| source_register_rows | 66 |
| unique_source_urls | 66 |

All 16 records are classified central/India by the archive. Rajasthan/Odisha mirror URLs are evidence hosts, not state-scheme coverage. No publication-ready record exists. The 53 archive review items are tasks, not 53 schemes. All human verification dates are null.

### File-level counts

| Artifact | Logical data rows |
| --- | ---: |
| condition_source_map.csv | 141 |
| coverage_register.csv | 676 |
| discovery_register.csv | 16 |
| review_queue.csv | 53 |
| scheme_catalogue.csv | 16 |
| source_register.csv | 66 |

Coverage JSON also has 676 rows; review JSON has 53 items; identity history has eight relationships; exclusions contain three umbrella/institution entries. All JSON parses, CSV widths/JSON cells pass, detailed rows match the canonical dataset, and the 19 current artifact hashes/lengths match the archive manifest. CRCRLF produces extra physical blank lines; the CSV audit counts logical nonblank rows. The tool performs independent structural checks plus archival required-key checks, not full Draft 2020-12 evaluation.

## Review candidates

These are the only five records containing extracted rules, benefits and guideline references. They span insurance, unorganised workers, household cooking fuel and old-age assistance. Within this set, deterministic priority uses fewer recorded conflict groups, then external ID; this is review triage, not a confidence score or factual approval.

| Priority | ID | Scheme | Conflicts |
| --- | --- | --- | ---: |
| 1 | IN-CEN-000002 | Pradhan Mantri Suraksha Bima Yojana | 2 |
| 2 | IN-CEN-000001 | Pradhan Mantri Jeevan Jyoti Bima Yojana | 3 |
| 3 | IN-CEN-000005 | Indira Gandhi National Old Age Pension Scheme | 3 |
| 4 | IN-CEN-000003 | Pradhan Mantri Shram Yogi Maan-dhan | 4 |
| 5 | IN-CEN-000004 | Pradhan Mantri Ujjwala Yojana | 5 |

## Every record

| ID | Name | Administering ministry (archive assertion) | Readiness | Hindi name |
| --- | --- | --- | --- | --- |
| IN-CEN-000001 | Pradhan Mantri Jeevan Jyoti Bima Yojana | Ministry of Finance | detailed_draft_requiring_verification | Missing |
| IN-CEN-000002 | Pradhan Mantri Suraksha Bima Yojana | Ministry of Finance | detailed_draft_requiring_verification | Missing |
| IN-CEN-000003 | Pradhan Mantri Shram Yogi Maan-dhan | Ministry of Labour and Employment | detailed_draft_requiring_verification | Missing |
| IN-CEN-000004 | Pradhan Mantri Ujjwala Yojana | Ministry of Petroleum and Natural Gas | detailed_draft_requiring_verification | Missing |
| IN-CEN-000005 | Indira Gandhi National Old Age Pension Scheme | Ministry of Rural Development | detailed_draft_requiring_verification | Approved-renaming name only |
| IN-CEN-000006 | Indira Gandhi National Widow Pension Scheme | Ministry of Rural Development | discovery_only | Approved-renaming name only |
| IN-CEN-000007 | Indira Gandhi National Disability Pension Scheme | Ministry of Rural Development | discovery_only | Approved-renaming name only |
| IN-CEN-000008 | National Family Benefit Scheme | Ministry of Rural Development | discovery_only | Approved-renaming name only |
| IN-CEN-000009 | Annapurna Scheme | Ministry of Rural Development | discovery_only | Missing |
| IN-CEN-000010 | Pradhan Mantri Kisan Samman Nidhi | Ministry of Agriculture and Farmers Welfare | discovery_only | Missing |
| IN-CEN-000011 | Pradhan Mantri Kisan Maan-dhan Yojana | Ministry of Agriculture and Farmers Welfare | discovery_only | Missing |
| IN-CEN-000012 | Pradhan Mantri Awaas Yojana - Gramin | Ministry of Rural Development | discovery_only | Missing |
| IN-CEN-000013 | Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana | Ministry of Health and Family Welfare | discovery_only | Missing |
| IN-CEN-000014 | National Pension Scheme for Traders and the Self-Employed Persons | Ministry of Labour and Employment | discovery_only | Missing |
| IN-CEN-000015 | Atal Pension Yojana | Ministry of Finance | discovery_only | Missing |
| IN-CEN-000016 | Pradhan Mantri Jan-Dhan Yojana | Ministry of Finance | discovery_only | Missing |

All 16 lack an explicit scheme description field and all have empty translations arrays. English names exist; English benefit/rule/application text exists for five drafts. Twelve Hindi names are absent. Four source-supplied Hindi names concern approved renamings whose implementation and human review remain unresolved; none supplies a reviewed Hindi description or eligibility translation.

## Per-record evidence and completeness

The full original record, unknown fields, precise citations, dates, conflicts and limitations are retained in each manifest records[].original_record. Missing means not collected, never no restriction. Source dates below are archive assertions and may have only year/day precision.

### IN-CEN-000001 ? Pradhan Mantri Jeevan Jyoti Bima Yojana

- Readiness: detailed_draft_requiring_verification; target status draft; all proposed rules disabled.
- Authority: Ministry of Finance / Department of Financial Services; authority verification: source_asserted.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Individual bank/post-office account holders; nominee receives death benefit
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: 2026-05-09 (not current verification).
- Application method: Participating bank/post-office enrolment with auto-debit consent; online Jan Suraksha enrolment reported by Finance Ministry, endpoint not verified.; application URL: None; information URL: https://financialservices.gov.in/pmjjby.

**Benefits**
- INR 200000 on insured death; annual renewable cover.
- Annual premium INR436; first-time entry Jun-Aug 436, Sep-Nov 342, Dec-Feb 228, Mar-May 114; renewal 436. Electronic-enrolment commission saving is passed on where applicable.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Individual participating bank/post-office account holder, entry age 18-50; exact age convention needs reconciliation with older rules.
  - Supplied structured assertion: `{"field": "age_years", "operator": "range_as_worded", "value": [18, 50], "period": null, "scope": null, "reference_date": "entry"}`; unverified.
- Enrol through only one account.
  - Supplied structured assertion: `{"field": "enrolment_accounts", "operator": "=", "value": 1, "period": null, "scope": null, "reference_date": null}`; unverified.
- Consent to enrolment and premium auto-debit required.
- NRI applicants need an eligible account at a bank branch in India.

**Required documents**
- Prescribed enrolment/auto-debit/consent declaration form. Aadhaar is primary bank KYC in old rules; current substitute KYC documents not established.
- Nominee details; guardian details if nominee is minor; witness if subscriber is illiterate. Historical form only; obtain current form from provider.

**Exclusions**
- Institutional accounts excluded. Non-accidental deaths within 30 days of first enrolment/rejoining are not covered.
- Cover ends at age 55 (age near birthday), account closure or insufficient balance. Duplicate coverage capped at INR200000; duplicate premiums liable to forfeiture.

**Conflict: premium_and_enrolment**
- Older rules/form: INR330, good-health declaration for late entry.
- DFS FAQ: INR436 and 30-day non-accidental lien.
- Archive proposed resolution (not accepted as verification): Premium revision corroborated by S10; all other historical/current differences require review. No automatic overwrite.

**Conflict: age_reference**
- 18 completed; 50 age nearer birthday.
- Entry range 18-50 without detailed birthday convention.
- Archive proposed resolution (not accepted as verification): Retain both; do not compute exact birthday eligibility until reviewed.

**Conflict: lien_scope**
- 30-day lien stated without accident exception in anniversary summary.
- Exception for accidental death is explicit.
- Archive proposed resolution (not accepted as verification): Summary omission; preserve references and review.

**Source references and date precision**
- S03: [Social Security Welfare Schemes](https://www.eshram.gov.in/Schemes); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S04: [PMJJBY FAQs](https://financialservices.gov.in/pmjjby); publication=2025-12-24; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S06: [Rules for Pradhan Mantri Jeevan Jyoti Bima Yojana](https://www.indiapost.gov.in/api/documents/file/1037n5x0mhoi3ii3d35sgn369dy04nii0s5ed0cnrf048xv0634s3l8933aghw); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S08: [PMJJBY Consent-cum-Declaration Form](https://www.indiapost.gov.in/api/documents/file/1037ncx2xts33h0rd3e8gn3eosm3ctmp0sjre0iatn01fyo0aayy0e2c708gea); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S09: [Three Jan Suraksha Schemes complete 11 years](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6); publication=2026-05-09; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S10: [First ever Revision of premium rates of PMJJBY and PMSBY](https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1829772&lang=2&reg=48); publication=None; effective=2022-06-01; retrieved=2026-10-31; human verification=None; access=search_index_excerpt.

**Missing / unresolved**
- Full amendment/supersession chain not established.
- Official Hindi name not safely transcribed/verified.
- Human verification outstanding.
- Complete original clauses not reproduced; short exact excerpts and locators provided.
- Current application endpoint and exact open/close dates not verified.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.
- Which later notifications modify this rule set?
- Which local implementation and claim-document requirements apply?

### IN-CEN-000002 ? Pradhan Mantri Suraksha Bima Yojana

- Readiness: detailed_draft_requiring_verification; target status draft; all proposed rules disabled.
- Authority: Ministry of Finance / Department of Financial Services; authority verification: source_asserted.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Individual account holders; survivors/nominees
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: 2026-05-09 (not current verification).
- Application method: Participating bank/post office with prescribed consent and premium auto-debit.; application URL: None; information URL: https://financialservices.gov.in/pmsby.

**Benefits**
- Accidental death: INR200000. INR200000 for specified irreversible bilateral eye/limb loss or one-eye plus one-limb loss; INR100000 for specified one-eye or one-limb loss. Annual premium INR20; electronic-enrolment commission-saving reduction where applicable.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Individual participating bank/post-office account holder, stated entry age 18-70.
  - Supplied structured assertion: `{"field": "age_years", "operator": "range_as_worded", "value": [18, 70], "period": null, "scope": null, "reference_date": "entry; age-70 termination also applies"}`; unverified.
- Only one enrolled account; each joint holder separately meets criteria and pays.
- Consent to enrol and enable auto-debit.
- NRI with eligible Indian-branch bank account may join.

**Required documents**
- Prescribed enrolment and auto-debit authorization; Aadhaar as primary account KYC in older rules.
- Accident evidence: police reporting for vehicular accidents/drowning/crime; immediate hospital record for snakebite/tree fall. Full claim-document checklist not collected.

**Exclusions**
- Institutional accounts, suicide, hospital-expense reimbursement, unconfirmed missing-person death and unlisted partial disability are outside cover.
- Cover terminates at age 70 (nearer birthday), account closure or insufficient balance; duplicate cover restricted and excess premiums liable to forfeiture.

**Conflict: premium_and_cover_start**
- Historical INR12; late cover starts following month.
- INR20; late/rejoining cover starts on debit date.
- Archive proposed resolution (not accepted as verification): Premium amendment corroborated by S10; cover-start rule amendment chain still needed.

**Conflict: age_70_boundary**
- Entry range includes wording 18-70; termination at attaining 70 near birthday.
- Archive proposed resolution (not accepted as verification): Do not reduce to a simple inclusive maximum-age boolean; insurer clarification required.

**Source references and date precision**
- S03: [Social Security Welfare Schemes](https://www.eshram.gov.in/Schemes); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S05: [PMSBY FAQs](https://financialservices.gov.in/pmsby); publication=2025-12-24; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S07: [Rules for the Pradhan Mantri Suraksha Bima Yojana](https://www.indiapost.gov.in/api/documents/file/103buv42xety3ixi13ighs04p3a0e32g0s5j40k56z35t1c02u6y0baz634tmu); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S09: [Three Jan Suraksha Schemes complete 11 years](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6); publication=2026-05-09; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S10: [First ever Revision of premium rates of PMJJBY and PMSBY](https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1829772&lang=2&reg=48); publication=None; effective=2022-06-01; retrieved=2026-10-31; human verification=None; access=search_index_excerpt.

**Missing / unresolved**
- Full amendment/supersession chain not established.
- Official Hindi name not safely transcribed/verified.
- Human verification outstanding.
- Complete original clauses not reproduced; short exact excerpts and locators provided.
- Current application endpoint and exact open/close dates not verified.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.
- Which later notifications modify this rule set?
- Which local implementation and claim-document requirements apply?

### IN-CEN-000003 ? Pradhan Mantri Shram Yogi Maan-dhan

- Readiness: detailed_draft_requiring_verification; target status draft; all proposed rules disabled.
- Authority: Ministry of Labour and Employment / None; authority verification: source_asserted.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Unorganised workers
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: 2026-08-03 (not current verification).
- Application method: CSC enrolment or Maandhan portal; first CSC contribution in cash then auto-debit.; application URL: https://maandhan.in/; information URL: None.

**Benefits**
- INR3000 minimum monthly pension at 60, subject to contributions until 60. Spouse-only family pension is 50% after pensioner death. Government matches contributions.
- Contribution varies by entry age, INR55-200 monthly. Exit/disability/spouse-continuation provisions exist; detailed exit calculations not extracted.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Applicant must be an unorganised worker.
  - Supplied structured assertion: `{"field": "employment_category", "operator": "=", "value": "unorganised_worker", "period": null, "scope": null, "reference_date": null}`; unverified.
- Worker monthly income <= INR15000; no household substitution.
  - Supplied structured assertion: `{"field": "income", "operator": "<=", "value": 15000, "period": "month", "scope": "individual_worker", "reference_date": null}`; unverified.
- Entry age at least 18 and at most 40.
  - Supplied structured assertion: `{"field": "age_years", "operator": "inclusive_range", "value": [18, 40], "period": null, "scope": null, "reference_date": "joining"}`; unverified.
- Savings account in own name and Aadhaar number.

**Required documents**
- Aadhaar, savings/Jan Dhan bank details with IFSC, and mobile number. First contribution cash and auto-debit set-up at CSC; exact alternative bank proofs not confirmed from fully accessible process form.

**Exclusions**
- Central-government-contributed NPS, ESIC, EPF coverage, or income-tax assessee excludes entry.
- Explainer additionally says no benefits from another government pension; this broader wording is unresolved.

**Conflict: income_operator**
- Monthly income below INR15000 (<).
- Monthly income <= INR15000.
- Archive proposed resolution (not accepted as verification): Both preserved. Notification proposal uses <=, still draft pending human approval.

**Conflict: contribution_at_age_20**
- Age 20 member contribution INR61/month.
- Age 20 member contribution INR65/month.
- Archive proposed resolution (not accepted as verification): No amendment found; do not calculate contributions automatically.

**Conflict: other_pensions_exclusion**
- Specified EPF/ESIC/Central-contributed NPS and tax exclusions.
- Broader any other government pension exclusion.
- Archive proposed resolution (not accepted as verification): Need authoritative clarification/amendment.

**Conflict: citizenship**
- Indian citizen criterion listed.
- No explicit citizenship wording in extracted English paragraph 4.
- Archive proposed resolution (not accepted as verification): Absence in this paragraph is not absence of restriction; review underlying Act and full amendment chain.

**Source references and date precision**
- S03: [Social Security Welfare Schemes](https://www.eshram.gov.in/Schemes); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S11: [S.O. 764(E): Pradhan Mantri Shram Yogi Maan-dhan, 2019](https://static.investindia.gov.in/s3fs-public/2019-08/Pradhan%20Mantri%20Shram%20Yogi%20Maan-dhan%20%28PM-%20SYM%29.pdf); publication=2019-02-07; effective=2019-02-15; retrieved=2026-10-31; human verification=None; access=readable_text.
- S12: [Pradhan Mantri Shram Yogi Maandhan Yojana: Ensuring Financial Security](https://www.labour.gov.in/static/uploads/2025/06/49a10165d1cf6f46e3bfbb52ba14f325.pdf); publication=2025-03-04; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S13: [Pradhan Mantri Shram Yogi Maandhan: over 54 lakh beneficiaries](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2293891&lang=2&reg=48); publication=2026-08-03; effective=None; retrieved=2026-10-31; human verification=None; access=search_index_excerpt.

**Missing / unresolved**
- Full amendment/supersession chain not established.
- Official Hindi name not safely transcribed/verified.
- Human verification outstanding.
- Complete original clauses not reproduced; short exact excerpts and locators provided.
- Current application endpoint and exact open/close dates not verified.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.
- Which later notifications modify this rule set?
- Which local implementation and claim-document requirements apply?

### IN-CEN-000004 ? Pradhan Mantri Ujjwala Yojana

- Readiness: detailed_draft_requiring_verification; target status draft; all proposed rules disabled.
- Authority: Ministry of Petroleum and Natural Gas / None; authority verification: source_asserted.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Adult women in poor households without LPG
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: Online via official PMUY landing page, CSC assistance, or LPG distributor.; application URL: https://www.pmuy.gov.in/faq.html; information URL: None.

**Benefits**
- 2023 expansion support per connection: INR2200 for 14.2kg single/5kg double bottle, INR1300 for 5kg single; equipment/deposit/installation support, not unrestricted cash to applicant. First refill and stove free.
- FAQ describes deposit-free equipment, first refill and two-burner stove. CSC-assisted application INR20; self-submission free; state stamp fee may apply.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Adult woman from poor household; deprivation declaration used in FAQ.
- Applicant age >=18.
  - Supplied structured assertion: `{"field": "age_years", "operator": ">=", "value": 18, "period": null, "scope": null, "reference_date": "application; exact measurement procedure not stated"}`; unverified.
- No household member has existing LPG connection; household composition document determines members.
- Indian citizenship and residence in India are declared in linked KYC.

**Required documents**
- Signed/photo KYC; applicant and adult-family Aadhaar; bank proof; family-composition proof; signed deprivation declaration. Address proof if Aadhaar address differs; migrant self-declaration may establish address/composition. Biometric Aadhaar authentication specified by FAQ.
- KYC lists bank passbook/statement/cancelled cheque and POA alternatives. Current version needs reconciliation with FAQ.

**Exclusions**
- PNG connection holders cannot receive PMUY; no new connection for existing LPG holder.
- 2023 poor-household declaration excludes listed assets/tax/employment categories; all 14 tests require current-form reconciliation before use.

**Conflict: eligibility_categories**
- SC/ST/PMAY-G/MBC/AAY/tea tribes/forest/islands/SECC/14-point poor-household routes.
- FAQ says no such categories under current scheme; deprivation declaration is basis.
- Archive proposed resolution (not accepted as verification): No dated replacement instruction collected; current phase rule set unresolved.

**Conflict: assistance**
- INR1600 (14.2kg), INR1150 (5kg).
- INR2200 (14.2kg single/5kg double), INR1300 (5kg single).
- Archive proposed resolution (not accepted as verification): Retain phase-specific assertions; do not publish single unqualified amount.

**Conflict: family_adult_boundary**
- KYC field uses above 18 for family members.
- FAQ uses adults at date of KYC and says members newly major must be added.
- Archive proposed resolution (not accepted as verification): Exact treatment of family member at 18 needs current form review.

**Conflict: ekyc**
- SOP allows biometric/demographic/OTP preference sequence.
- FAQ requires biometric authentication.
- Archive proposed resolution (not accepted as verification): Need dated amendment/current SOP.

**Conflict: document_version**
- Form uses category and 14-point declaration fields.
- FAQ calls for revised form and deprivation declaration.
- Archive proposed resolution (not accepted as verification): Latest form not confirmed.

**Source references and date precision**
- S14: [About PMUY](https://www.pmuy.gov.in/about.html); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S15: [Frequently Asked Questions on Ujjwala Scheme](https://www.pmuy.gov.in/faq.html); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S16: [SOP for release of additional 75 lakh LPG connections under PMUY](https://www.mopng.gov.in/files/marketing/lpg/75L-PMUY-SoP-10102023-(1).pdf); publication=2023-10-10; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S17: [Ujjwala KYC Application, Version 5.0](https://www.pmuy.gov.in/documents/Ujjwala-KYC.pdf); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.

**Missing / unresolved**
- Full amendment/supersession chain not established.
- Official Hindi name not safely transcribed/verified.
- Human verification outstanding.
- Complete original clauses not reproduced; short exact excerpts and locators provided.
- Current application endpoint and exact open/close dates not verified.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.
- Which later notifications modify this rule set?
- Which local implementation and claim-document requirements apply?

### IN-CEN-000005 ? Indira Gandhi National Old Age Pension Scheme

- Readiness: detailed_draft_requiring_verification; target status draft; all proposed rules disabled.
- Authority: Ministry of Rural Development / Department of Rural Development; authority verification: source_asserted.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Older individuals in BPL households
- Names/language: English name present; Hindi name present only as an approved-renaming assertion; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: Local-authority verification and designated state sanctioning authority; consult Gram Panchayat/municipality. State-specific application URL not yet collected.; application URL: None; information URL: None.

**Benefits**
- Central share INR200/month for ages 60-79 and INR500/month from 80, subject to applicable category exclusions; state top-ups separate and uncollected.
- 2014 central pension: INR200 monthly at 60-79; INR500 monthly at >=80.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Applicant age >=60, subject to category exclusions in the 2012 order.
  - Supplied structured assertion: `{"field": "age_years", "operator": ">=", "value": 60, "period": null, "scope": null, "reference_date": "application; explicit age-assessment date not collected"}`; unverified.
- Applicant belongs to BPL household under Government of India criteria; no invented numeric income threshold.
  - Supplied structured assertion: `{"field": "bpl_status", "operator": "=", "value": true, "period": null, "scope": "household", "reference_date": null}`; unverified.
- 2014 guideline: age >=60 and BPL category.
  - Supplied structured assertion: `{"field": "age_years", "operator": ">=", "value": 60, "period": null, "scope": "individual; BPL household status separately assessed", "reference_date": "not specified"}`; unverified.
- BPL-list omission requires eligibility assessment, not automatic rejection.
  - Supplied structured assertion: `{"field": "bpl_list_omission", "operator": "manual_assessment_required", "value": null, "period": null, "scope": null, "reference_date": null}`; unverified.

**Required documents**
- Application/verification process exists; age/BPL evidence must be confirmed with state implementation. A national mandatory document checklist was not established from retrieved sources.
- Age: birth/school certificate; absent these, ration card/EPIC may be considered; absent valid documents, authorized government-hospital medical officer certificate.
- Model form records identity, photograph, BPL details and bank/post-office details if available. Form fields do not establish every identifier as a mandatory attachment.

**Exclusions**
- 2012 order excludes BPL widows and BPL persons with severe and multiple disabilities aged 60-79 from IGNOAPS category; related pension scheme routing must be checked.

**Conflict: age_80_benefit_boundary**
- INR500 for 80 and above.
- Manual says above 80 for old-age pension.
- Archive proposed resolution (not accepted as verification): Keep both; draft amount uses >=80 from order, human review required.

**Conflict: category_exclusions**
- 2012 order excludes widow/severe-multiple-disability BPL group ages 60-79.
- Undated FAQ gives general 60+/BPL criteria without these exclusions.
- 2014 section 2.3 states general age/BPL criteria; historical category exclusions need reconciliation.
- Archive proposed resolution (not accepted as verification): Incomplete version chain; do not auto-reject based on historical exclusion.

**Conflict: legacy_bpl_exception**
- New eligibility requires BPL household.
- Previously eligible legacy beneficiaries not on BPL list may continue.
- Archive proposed resolution (not accepted as verification): Separate existing-beneficiary continuation from new application; applicable period needs review.

**Source references and date precision**
- S19: [OM J-11015/1/2012-NSAP: Guidelines for Central assistance under IGNOAPS](https://sje.rajasthan.gov.in/Schemes/Central%20Pension1.pdf); publication=2012-11-08; effective=2012-10-01; retrieved=2026-10-31; human verification=None; access=search_index_text; PDF opens but scan unreadable in text tool.
- S20: [NSAP Frequently Asked Questions](https://www.dord.gov.in/static/uploads/2024/07/1ff5b85d83a44d7b22cda3b40547ed4c.pdf); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S21: [NSAP Manual for District Level Functionaries, 2017](https://darpg.gov.in/sites/default/files/NSAP-District%20Manual_21.11.2017(1).pdf); publication=2017; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S59: [Guidelines on National Social Assistance Programme (NSAP), October 2014](https://ssepd.odisha.gov.in/sites/default/files/2026-03/GUIDELINES%20ON%20NATIONAL%20SOCIAL%20ASSISTANCE%20PROGRAMME%20%28NSAP%29.pdf); publication=2014-10; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S60: [Cabinet approves continuation of NSAP for 2026-27 to 2030-31](https://www.pib.gov.in/PressReleasepage.aspx?PRID=2323264&l=&lang=2&reg=48); publication=2026-10-14; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.

**Missing / unresolved**
- Full amendment/supersession chain not established.
- Human verification outstanding.
- Complete original clauses not reproduced; short exact excerpts and locators provided.
- Current application endpoint and exact open/close dates not verified.
- 2014 guideline now readable; 2012 scan remains indexed-only. Later amendments and state document checklist remain unverified.
- Renaming implementation date and revised guidelines not collected; original-source Hindi name awaits human review.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.
- Which later notifications modify this rule set?
- Which local implementation and claim-document requirements apply?

### IN-CEN-000006 ? Indira Gandhi National Widow Pension Scheme

- Readiness: discovery_only; target status draft; all proposed rules disabled.
- Authority: Ministry of Rural Development / Department of Rural Development; authority verification: provisional_pending_administering_source_check.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Widows in eligible households
- Names/language: English name present; Hindi name present only as an approved-renaming assertion; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: None; application URL: None; information URL: None.

**Benefits**
- Not collected; no absence of restriction inferred.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Not collected; no absence of restriction inferred.

**Required documents**
- Not collected; no absence of restriction inferred.

**Exclusions**
- Not collected; no absence of restriction inferred.

**Source references and date precision**
- S20: [NSAP Frequently Asked Questions](https://www.dord.gov.in/static/uploads/2024/07/1ff5b85d83a44d7b22cda3b40547ed4c.pdf); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S60: [Cabinet approves continuation of NSAP for 2026-27 to 2030-31](https://www.pib.gov.in/PressReleasepage.aspx?PRID=2323264&l=&lang=2&reg=48); publication=2026-10-14; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.

**Missing / unresolved**
- Detailed eligibility/exclusions/documents/amounts/application windows and current status not extracted.
- Administering source and current guideline version require verification.
- Renaming implementation date and revised guidelines not collected; original-source Hindi name awaits human review.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.

### IN-CEN-000007 ? Indira Gandhi National Disability Pension Scheme

- Readiness: discovery_only; target status draft; all proposed rules disabled.
- Authority: Ministry of Rural Development / Department of Rural Development; authority verification: provisional_pending_administering_source_check.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Persons with disabilities
- Names/language: English name present; Hindi name present only as an approved-renaming assertion; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: None; application URL: None; information URL: None.

**Benefits**
- Not collected; no absence of restriction inferred.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Not collected; no absence of restriction inferred.

**Required documents**
- Not collected; no absence of restriction inferred.

**Exclusions**
- Not collected; no absence of restriction inferred.

**Source references and date precision**
- S20: [NSAP Frequently Asked Questions](https://www.dord.gov.in/static/uploads/2024/07/1ff5b85d83a44d7b22cda3b40547ed4c.pdf); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S60: [Cabinet approves continuation of NSAP for 2026-27 to 2030-31](https://www.pib.gov.in/PressReleasepage.aspx?PRID=2323264&l=&lang=2&reg=48); publication=2026-10-14; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.

**Missing / unresolved**
- Detailed eligibility/exclusions/documents/amounts/application windows and current status not extracted.
- Administering source and current guideline version require verification.
- Renaming implementation date and revised guidelines not collected; original-source Hindi name awaits human review.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.

### IN-CEN-000008 ? National Family Benefit Scheme

- Readiness: discovery_only; target status draft; all proposed rules disabled.
- Authority: Ministry of Rural Development / Department of Rural Development; authority verification: provisional_pending_administering_source_check.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Bereaved eligible households
- Names/language: English name present; Hindi name present only as an approved-renaming assertion; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: None; application URL: None; information URL: None.

**Benefits**
- Not collected; no absence of restriction inferred.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Not collected; no absence of restriction inferred.

**Required documents**
- Not collected; no absence of restriction inferred.

**Exclusions**
- Not collected; no absence of restriction inferred.

**Source references and date precision**
- S20: [NSAP Frequently Asked Questions](https://www.dord.gov.in/static/uploads/2024/07/1ff5b85d83a44d7b22cda3b40547ed4c.pdf); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.
- S60: [Cabinet approves continuation of NSAP for 2026-27 to 2030-31](https://www.pib.gov.in/PressReleasepage.aspx?PRID=2323264&l=&lang=2&reg=48); publication=2026-10-14; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.

**Missing / unresolved**
- Detailed eligibility/exclusions/documents/amounts/application windows and current status not extracted.
- Administering source and current guideline version require verification.
- Renaming implementation date and revised guidelines not collected; original-source Hindi name awaits human review.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.

### IN-CEN-000009 ? Annapurna Scheme

- Readiness: discovery_only; target status draft; all proposed rules disabled.
- Authority: Ministry of Rural Development / Department of Rural Development; authority verification: provisional_pending_administering_source_check.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Older persons outside pension coverage
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: None; application URL: None; information URL: None.

**Benefits**
- Not collected; no absence of restriction inferred.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Not collected; no absence of restriction inferred.

**Required documents**
- Not collected; no absence of restriction inferred.

**Exclusions**
- Not collected; no absence of restriction inferred.

**Source references and date precision**
- S20: [NSAP Frequently Asked Questions](https://www.dord.gov.in/static/uploads/2024/07/1ff5b85d83a44d7b22cda3b40547ed4c.pdf); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.

**Missing / unresolved**
- Detailed eligibility/exclusions/documents/amounts/application windows and current status not extracted.
- Administering source and current guideline version require verification.
- Official Hindi name not collected.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.

### IN-CEN-000010 ? Pradhan Mantri Kisan Samman Nidhi

- Readiness: discovery_only; target status draft; all proposed rules disabled.
- Authority: Ministry of Agriculture and Farmers Welfare / Department of Agriculture and Farmers Welfare; authority verification: provisional_pending_administering_source_check.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Farmer households
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: None; application URL: None; information URL: None.

**Benefits**
- Not collected; no absence of restriction inferred.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Not collected; no absence of restriction inferred.

**Required documents**
- Not collected; no absence of restriction inferred.

**Exclusions**
- Not collected; no absence of restriction inferred.

**Source references and date precision**
- S24: [PM-KISAN Operational Guidelines revised 29.03.2020](https://pmkisan.gov.in/Documents/RevisedPM-KISANOperationalGuidelines%28English%29.pdf); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=indexed excerpt; direct open 502.

**Missing / unresolved**
- Detailed eligibility/exclusions/documents/amounts/application windows and current status not extracted.
- Administering source and current guideline version require verification.
- Official Hindi name not collected.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.

### IN-CEN-000011 ? Pradhan Mantri Kisan Maan-dhan Yojana

- Readiness: discovery_only; target status draft; all proposed rules disabled.
- Authority: Ministry of Agriculture and Farmers Welfare / Department of Agriculture and Farmers Welfare; authority verification: provisional_pending_administering_source_check.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Small and marginal farmers
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: None; application URL: None; information URL: None.

**Benefits**
- Not collected; no absence of restriction inferred.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Not collected; no absence of restriction inferred.

**Required documents**
- Not collected; no absence of restriction inferred.

**Exclusions**
- Not collected; no absence of restriction inferred.

**Source references and date precision**
- S03: [Social Security Welfare Schemes](https://www.eshram.gov.in/Schemes); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.

**Missing / unresolved**
- Detailed eligibility/exclusions/documents/amounts/application windows and current status not extracted.
- Administering source and current guideline version require verification.
- Official Hindi name not collected.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.

### IN-CEN-000012 ? Pradhan Mantri Awaas Yojana - Gramin

- Readiness: discovery_only; target status draft; all proposed rules disabled.
- Authority: Ministry of Rural Development / Department of Rural Development; authority verification: provisional_pending_administering_source_check.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Rural households
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: None; application URL: None; information URL: None.

**Benefits**
- Not collected; no absence of restriction inferred.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Not collected; no absence of restriction inferred.

**Required documents**
- Not collected; no absence of restriction inferred.

**Exclusions**
- Not collected; no absence of restriction inferred.

**Source references and date precision**
- S03: [Social Security Welfare Schemes](https://www.eshram.gov.in/Schemes); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.

**Missing / unresolved**
- Detailed eligibility/exclusions/documents/amounts/application windows and current status not extracted.
- Administering source and current guideline version require verification.
- Official Hindi name not collected.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.

### IN-CEN-000013 ? Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana

- Readiness: discovery_only; target status draft; all proposed rules disabled.
- Authority: Ministry of Health and Family Welfare / National Health Authority (implementing authority; department mapping pending); authority verification: provisional_pending_administering_source_check.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Eligible individuals and households
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: None; application URL: None; information URL: None.

**Benefits**
- Not collected; no absence of restriction inferred.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Not collected; no absence of restriction inferred.

**Required documents**
- Not collected; no absence of restriction inferred.

**Exclusions**
- Not collected; no absence of restriction inferred.

**Source references and date precision**
- S03: [Social Security Welfare Schemes](https://www.eshram.gov.in/Schemes); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.

**Missing / unresolved**
- Detailed eligibility/exclusions/documents/amounts/application windows and current status not extracted.
- Administering source and current guideline version require verification.
- Official Hindi name not collected.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.

### IN-CEN-000014 ? National Pension Scheme for Traders and the Self-Employed Persons

- Readiness: discovery_only; target status draft; all proposed rules disabled.
- Authority: Ministry of Labour and Employment / None; authority verification: provisional_pending_administering_source_check.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Individual traders and self-employed persons
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: None; application URL: None; information URL: None.

**Benefits**
- Not collected; no absence of restriction inferred.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Not collected; no absence of restriction inferred.

**Required documents**
- Not collected; no absence of restriction inferred.

**Exclusions**
- Not collected; no absence of restriction inferred.

**Source references and date precision**
- S03: [Social Security Welfare Schemes](https://www.eshram.gov.in/Schemes); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.

**Missing / unresolved**
- Detailed eligibility/exclusions/documents/amounts/application windows and current status not extracted.
- Administering source and current guideline version require verification.
- Official Hindi name not collected.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.

### IN-CEN-000015 ? Atal Pension Yojana

- Readiness: discovery_only; target status draft; all proposed rules disabled.
- Authority: Ministry of Finance / Department of Financial Services; authority verification: provisional_pending_administering_source_check.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Individual pension subscribers
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: None; application URL: None; information URL: None.

**Benefits**
- Not collected; no absence of restriction inferred.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Not collected; no absence of restriction inferred.

**Required documents**
- Not collected; no absence of restriction inferred.

**Exclusions**
- Not collected; no absence of restriction inferred.

**Source references and date precision**
- S09: [Three Jan Suraksha Schemes complete 11 years](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6); publication=2026-05-09; effective=None; retrieved=2026-10-31; human verification=None; access=readable_text.

**Missing / unresolved**
- Detailed eligibility/exclusions/documents/amounts/application windows and current status not extracted.
- Administering source and current guideline version require verification.
- Official Hindi name not collected.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.

### IN-CEN-000016 ? Pradhan Mantri Jan-Dhan Yojana

- Readiness: discovery_only; target status draft; all proposed rules disabled.
- Authority: Ministry of Finance / Department of Financial Services; authority verification: provisional_pending_administering_source_check.
- Central/state: central; jurisdiction: India.
- Description: no explicit description supplied; intended beneficiaries retained verbatim: Unbanked individuals
- Names/language: English name present; Hindi name missing; translation objects: 0.
- Human verification: None; extraction: 2026-10-31T01:11:27+05:30; status-as-of: None (not current verification).
- Application method: None; application URL: None; information URL: None.

**Benefits**
- Not collected; no absence of restriction inferred.

**Eligibility (age/income/gender/occupation/residency/household assertions; not normalized decisions)**
- Not collected; no absence of restriction inferred.

**Required documents**
- Not collected; no absence of restriction inferred.

**Exclusions**
- Not collected; no absence of restriction inferred.

**Source references and date precision**
- S25: [PMJDY scheme details](https://www.pmjdy.gov.in/scheme-detail.aspx); publication=None; effective=None; retrieved=2026-10-31; human verification=None; access=indexed excerpt; direct open timeout.

**Missing / unresolved**
- Detailed eligibility/exclusions/documents/amounts/application windows and current status not extracted.
- Administering source and current guideline version require verification.
- Official Hindi name not collected.
- No explicit scheme description field; intended_beneficiaries is not a substitute.
- Hindi name missing.
- English/Hindi description and eligibility translations are not established.
- Original source-document byte snapshots and current access/reuse permission not established.
- Human verification and reviewed publication prerequisites outstanding.

## Source register and provenance limitations

66 unique registered URLs: 65 end in .gov.in/.nic.in; one is LIC India (S47). This hostname heuristic is not publisher authentication or reuse permission. All 141 field-level citation occurrences use government-domain URLs. The registry includes failed/policy-blocked/discovery endpoints that are not usable eligibility evidence. Its claimed statuses are 29 checked, 36 blocked and one in progress; checked does not certify truth, completeness or current applicability.

No original government PDF/HTML byte snapshots are included. Artifact hashes certify local generated files only. Historical premium/age/phase differences, incomplete amendment chains, short quotation anchors, index-only reads and uncertain renamed-scheme implementation dates remain blockers. The current archive has zero verified current application transactions.

## Artifacts

Final verification: 32 Python tests (including all existing API tests) and eight
in-memory PGlite regression tests passed. The real dry run produced no structural
validation errors. Readiness warnings remain: zero human approvals, missing source
snapshots and bilingual descriptions/eligibility text, unresolved conflicts and
amendment chains. Ten conditions lack complete structured/quotation/evidence
components. No website or database verification was attempted in this phase.

- Final manifest: `../.phase3-output/verified/b6c4262434a8dd3e/manifest.json`.
- Compact readiness report: `../.phase3-output/verified/b6c4262434a8dd3e/readiness.json`.
- Full originals under the same directory in `extracted/`; scripts in `quarantine/` with disabled suffixes.
- No Supabase writes, source fetching, credentials or frontend changes occurred.
