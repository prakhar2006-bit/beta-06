# Phase 3D five-scheme verification report

Checked 31 October 2026. Five source-backed **drafts** were prepared, with no human approvals or publication. Official guidance corroboration is not a complete signed policy/amendment audit.

## Inputs, provenance and reuse

The Phase 3A archive, manifest, source register and all original fields/conflicts are retained unchanged. Phase 3B PMSBY is reused byte-for-byte (its draft SHA-256 still starts `afe9609bc2b9a0db`). Four new ledgers and five newly captured PIB response bodies are under ignored `.phase3-output/phase3d-evidence/`. The PMJJBY capture is reused from Phase 3B, with its original fetch time/hash rather than a fabricated new retrieval.

Collection: `.phase3-output/phase3d/collection.json`. Each entry binds a stable ID to a SHA-256 checked draft. Each draft has original_record, archive_source_register, unresolved_archive_conflicts, claim verification, source dates, bilingual review sidecars and schema rows. Draft paths and full hashes are recorded below.

Only already inspected public sources were downloaded with bounded GETs; no crawler, private endpoint, access-control bypass or archive script was used. The [PIB copyright policy](https://www.pib.gov.in/content/132_2_Copyright-Policy.aspx?lang=1&reg=1) permits attributed reuse of its own content, excluding third-party content. Captures are local review evidence, not a blanket license to republish embedded third-party material. DFS and PMUY pages were read for comparison but not copied into new raw snapshots; permissions/current document reuse remain review items.

All claim assertions below are research paraphrases. Effective dates remain **unknown/null** unless explicitly established; a publication date is not an effective date. Claim checked dates record AI-assisted inspection, not human review. The archive conflict IDs associated with claims are scheme-wide context, not assertions that every claim conflicts with every ID.

## PMJJBY

- Stable ID: `in-cen-000001`; draft: `schemes/in-cen-000001/0f56dbe413363723/draft.json`.
- SHA-256: `0f56dbe4133637230c6856866ec7924f75e7f3508dff0e7170624c7a77e36c38`.
- Claim statuses: {'verified_official_guidance': 10, 'unverified': 1}; original conflicts preserved: 3.
- All target versions and translations remain draft; all rule nodes remain disabled/UNCERTAIN.

### Sources checked

| Source | Official document | Published | Effective | Capture/access |
| --- | --- | --- | --- | --- |
| PIB-2026-EN | [Three Jan Suraksha Schemes complete 11 years — Ministry of Finance](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6) | 2026-05-09 | Unknown | readable_captured |
| DFS-PMJJBY | [PMJJBY FAQs](https://financialservices.gov.in/pmjjby) | 2025-12-24 | Unknown | readable_permission_required |

### Assertions and verification

| Claim | Exact research assertion | Status | Evidence locator |
| --- | --- | --- | --- |
| nature | Renewable life cover for death from any cause. | verified_official_guidance | [PIB-2026-EN](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6), Section 1 PMJJBY: key feature and benefits |
| premium | Standard annual premium: INR 436. | verified_official_guidance | [PIB-2026-EN](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6), Section 1 PMJJBY: premium |
| benefit | Insured death benefit: INR 200000, subject to terms. | verified_official_guidance | [PIB-2026-EN](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6), Section 1 PMJJBY: benefits |
| account | Individual participating bank/post-office account is required. | verified_official_guidance | [PIB-2026-EN](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6), Section 1 PMJJBY: eligibility |
| consent | Consent to enrolment and premium auto-debit is required. | verified_official_guidance | [PIB-2026-EN](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6), Section 1 PMJJBY: eligibility |
| single-account | Only one account may be used for scheme enrolment. | verified_official_guidance | [PIB-2026-EN](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6), Section 1 PMJJBY: eligibility |
| entry-age | Published entry range: 18 to 50; birthday convention unresolved. | verified_official_guidance | [PIB-2026-EN](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6), Section 1 PMJJBY: eligibility |
| lien | Release describes a 30-day waiting period; see detailed accident exception. | verified_official_guidance | [PIB-2026-EN](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6), Section 1 PMJJBY: benefits |
| lien-detail | DFS specifies non-accidental death exclusion in first 30 days and debit-date commencement. | verified_official_guidance | [DFS-PMJJBY](https://financialservices.gov.in/pmjjby), Benefits/premium FAQ |
| termination | DFS gives termination at 55 near birthday, account closure or insufficient balance. | verified_official_guidance | [DFS-PMJJBY](https://financialservices.gov.in/pmjjby), When can assurance terminate? |
| documents | Complete current provider KYC, nomination and claim document list not verified. | unverified | [DFS-PMJJBY](https://financialservices.gov.in/pmjjby), Provider forms outstanding |

All rows above: checked 2026-10-31; rule/claim effective date not established. The full ledger carries uncertainty, conflict context and source publication dates. Corroborated claims remain unapproved.

### Preserved conflicts and remaining work

- **C-JJ-01 / premium_and_enrolment**:
  - Archive assertion, not newly confirmed: Older rules/form: INR330, good-health declaration for late entry. Sources: [S06](https://www.indiapost.gov.in/api/documents/file/1037n5x0mhoi3ii3d35sgn369dy04nii0s5ed0cnrf048xv0634s3l8933aghw) (pp.1-2).
  - Archive assertion, not newly confirmed: DFS FAQ: INR436 and 30-day non-accidental lien. Sources: [S04](https://financialservices.gov.in/pmjjby) (benefits; rejoining).
- **C-JJ-02 / age_reference**:
  - Archive assertion, not newly confirmed: 18 completed; 50 age nearer birthday. Sources: [S06](https://www.indiapost.gov.in/api/documents/file/1037n5x0mhoi3ii3d35sgn369dy04nii0s5ed0cnrf048xv0634s3l8933aghw) (p.2 Eligibility Conditions).
  - Archive assertion, not newly confirmed: Entry range 18-50 without detailed birthday convention. Sources: [S04](https://financialservices.gov.in/pmjjby) (Who will be eligible to subscribe?).
- **C-JJ-03 / lien_scope**:
  - Archive assertion, not newly confirmed: 30-day lien stated without accident exception in anniversary summary. Sources: [S09](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6) (PMJJBY Benefits).
  - Archive assertion, not newly confirmed: Exception for accidental death is explicit. Sources: [S04](https://financialservices.gov.in/pmjjby) (benefits/premium).

Publication blockers:

- Exact entry/termination birthday conventions and full current amendment chain.
- Lien accident exception, rejoining, pro-rata premium and risk commencement need policy/provider sign-off.
- Current enrolment/KYC/nominee and claim forms and usable application route.
- Independent bilingual review; archived premium/age/lien conflicts remain preserved.

### Content and rule readiness

English: Annual renewable life insurance covering death from any cause, subject to policy terms and lien conditions.

Hindi draft: पॉलिसी और प्रतीक्षा अवधि की शर्तों के अधीन किसी भी कारण से मृत्यु पर सुरक्षा देने वाला वार्षिक नवीकरणीय जीवन बीमा।

Both translations, all questions and child descriptions are AI-drafted/nonofficial and require independent bilingual review. Canonical English scheme naming is evidence-backed, but the combined translation row remains machine/draft. Original names, including historical/announced Hindi names, remain untouched in original_record.

Mapped document items: 0; benefits: 1; offline route descriptions: 0. Empty document/route arrays mean unverified or unmapped, not that no documents/application process are required. No transaction endpoint is asserted.

| Proposed necessary check | Machine expression | Verified supporting claim | Effective date | Execution |
| --- | --- | --- | --- | --- |
| account | `participating_individual_account eq true` | account | Unknown | Disabled; human review required |
| consent | `enrolment_and_autodebit_consent eq true` | consent | Unknown | Disabled; human review required |
| single-account | `scheme_enrolment_account_count eq 1` | single-account | Unknown | Disabled; human review required |

These partial checks are neither a complete rule set nor an eligibility verdict. Unknown/missing citizen information must not be coerced to false. Provider/state/declaration checks remain manual, and no citizen answers are collected.

## PMSBY

- Stable ID: `in-cen-000002`; draft: `schemes/in-cen-000002/afe9609bc2b9a0db/draft.json`.
- SHA-256: `afe9609bc2b9a0db06a13442d3762fb080f93ccfd4b2fc050359cdaaa3a8ae38`.
- Claim statuses: {'verified_official_guidance': 14, 'unresolved': 4, 'unverified': 1}; original conflicts preserved: 2.
- All target versions and translations remain draft; all rule nodes remain disabled/UNCERTAIN.

The unchanged claim-by-claim audit is in [PMSBY_VERIFICATION_REPORT.md](PMSBY_VERIFICATION_REPORT.md), with the rules in [PMSBY_ELIGIBILITY_RULES.md](PMSBY_ELIGIBILITY_RULES.md). Its 19 claims retain their original verification dates/statuses and both archive conflicts. No new policy approval is implied by collection membership.

## PM-SYM

- Stable ID: `in-cen-000003`; draft: `schemes/in-cen-000003/fa9dc8a90fdc4bfc/draft.json`.
- SHA-256: `fa9dc8a90fdc4bfcbcf3e2525d69f9f30627f4e407e8e266e857ecc67f217710`.
- Claim statuses: {'verified_official_guidance': 11, 'unresolved': 3}; original conflicts preserved: 4.
- All target versions and translations remain draft; all rule nodes remain disabled/UNCERTAIN.

### Sources checked

| Source | Official document | Published | Effective | Capture/access |
| --- | --- | --- | --- | --- |
| SYM-2025 | [Pradhan Mantri Shram Yogi Maandhan Yojana](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2108082&lang=2&reg=3) | 2025-03-04 | Unknown | readable_captured |
| SYM-2026 | [PRADHAN MANTRI SHRAM YOGI MAANDHAN (PM-SYM)](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2293891&lang=2&reg=48) | 2026-08-03 | Unknown | readable_captured |
| ESHRAM | [e-Shram scheme summaries](https://www.eshram.gov.in/Schemes) | Unknown | Unknown | readable_not_captured |

### Assertions and verification

| Claim | Exact research assertion | Status | Evidence locator |
| --- | --- | --- | --- |
| nature | Voluntary contributory pension for unorganised workers. | verified_official_guidance | [SYM-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2293891&lang=2&reg=48), Opening scheme description |
| minimum-age | Entry age starts at 18. | verified_official_guidance | [SYM-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2293891&lang=2&reg=48), Eligibility paragraph |
| maximum-age | Published maximum entry age is 40. | verified_official_guidance | [SYM-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2293891&lang=2&reg=48), Eligibility paragraph |
| occupation | Scheme targets workers in the unorganised sector. | verified_official_guidance | [SYM-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2293891&lang=2&reg=48), Eligibility paragraph |
| income | Monthly income stated as INR 15000 or less. | verified_official_guidance | [SYM-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2293891&lang=2&reg=48), Eligibility paragraph |
| pension | Minimum assured pension: INR 3000 monthly from age 60. | verified_official_guidance | [SYM-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2293891&lang=2&reg=48), Opening scheme description |
| contributions | Monthly contributions depend on entry age; government matches. | verified_official_guidance | [SYM-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2293891&lang=2&reg=48), Contribution paragraphs |
| tax | Income taxpayers are excluded in 2025 guidance. | verified_official_guidance | [SYM-2025](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2108082&lang=2&reg=3), Eligibility criteria, exclusions |
| coverage | EPF/ESIC/NPS and other government-pension exclusions are described. | verified_official_guidance | [SYM-2025](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2108082&lang=2&reg=3), Eligibility criteria, exclusions |
| documents | Aadhaar, savings/Jan Dhan account with IFSC and mobile number are listed. | verified_official_guidance | [SYM-2025](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2108082&lang=2&reg=3), Documents required |
| enrolment | Common Service Centres facilitate enrolment. | verified_official_guidance | [SYM-2025](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2108082&lang=2&reg=3), Enrolment process |
| income-conflict | e-Shram uses below INR15000 while PIB uses INR15000 or less. | unresolved | [ESHRAM](https://www.eshram.gov.in/Schemes), PM-SYM eligibility |
| contribution-conflict | 2019 and 2025 contribution tables differ at entry age 20; no calculator authorized. | unresolved | [SYM-2025](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2108082&lang=2&reg=3), Monthly contribution table; archive C-SYM-02 |
| coverage-scope | Government-pension exclusion and AND/OR wording need current notification reconciliation. | unresolved | [SYM-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2293891&lang=2&reg=48), Eligibility paragraph and 2025 exclusions |

All rows above: checked 2026-10-31; rule/claim effective date not established. The full ledger carries uncertainty, conflict context and source publication dates. Corroborated claims remain unapproved.

### Preserved conflicts and remaining work

- **C-SYM-01 / income_operator**:
  - Archive assertion, not newly confirmed: Monthly income below INR15000 (<). Sources: [S03](https://www.eshram.gov.in/Schemes) (PM-SYM Eligibility).
  - Archive assertion, not newly confirmed: Monthly income <= INR15000. Sources: [S11](https://static.investindia.gov.in/s3fs-public/2019-08/Pradhan%20Mantri%20Shram%20Yogi%20Maan-dhan%20%28PM-%20SYM%29.pdf) (English p.6 para 4(1)).
- **C-SYM-02 / contribution_at_age_20**:
  - Archive assertion, not newly confirmed: Age 20 member contribution INR61/month. Sources: [S11](https://static.investindia.gov.in/s3fs-public/2019-08/Pradhan%20Mantri%20Shram%20Yogi%20Maan-dhan%20%28PM-%20SYM%29.pdf) (English p.7 Annexure).
  - Archive assertion, not newly confirmed: Age 20 member contribution INR65/month. Sources: [S12](https://www.labour.gov.in/static/uploads/2025/06/49a10165d1cf6f46e3bfbb52ba14f325.pdf) (p.3 Contribution Structure).
- **C-SYM-03 / other_pensions_exclusion**:
  - Archive assertion, not newly confirmed: Specified EPF/ESIC/Central-contributed NPS and tax exclusions. Sources: [S11](https://static.investindia.gov.in/s3fs-public/2019-08/Pradhan%20Mantri%20Shram%20Yogi%20Maan-dhan%20%28PM-%20SYM%29.pdf) (English p.6 para 4(3)).
  - Archive assertion, not newly confirmed: Broader any other government pension exclusion. Sources: [S12](https://www.labour.gov.in/static/uploads/2025/06/49a10165d1cf6f46e3bfbb52ba14f325.pdf) (p.3 Eligibility Criteria).
- **C-SYM-04 / citizenship**:
  - Archive assertion, not newly confirmed: Indian citizen criterion listed. Sources: [S03](https://www.eshram.gov.in/Schemes) (PM-SYM Eligibility).
  - Archive assertion, not newly confirmed: No explicit citizenship wording in extracted English paragraph 4. Sources: [S11](https://static.investindia.gov.in/s3fs-public/2019-08/Pradhan%20Mantri%20Shram%20Yogi%20Maan-dhan%20%28PM-%20SYM%29.pdf) (English p.6 para 4).

Publication blockers:

- Income < versus <= boundary; contribution table discrepancy at age 20.
- Full notification/amendment chain; pension/EPFO/ESIC/NPS exclusion scope and citizenship.
- Current enrolment procedure, contribution mandate and occupation classification.
- Independent English/Hindi review; no contribution calculator or complete eligibility verdict.

### Content and rule readiness

English: Voluntary contributory old-age pension for unorganised workers; contributions and exclusions apply.

Hindi draft: असंगठित कामगारों के लिए स्वैच्छिक अंशदायी वृद्धावस्था पेंशन; अंशदान और अपवर्जन संबंधी शर्तें लागू हैं।

Both translations, all questions and child descriptions are AI-drafted/nonofficial and require independent bilingual review. Canonical English scheme naming is evidence-backed, but the combined translation row remains machine/draft. Original names, including historical/announced Hindi names, remain untouched in original_record.

Mapped document items: 3; benefits: 1; offline route descriptions: 1. Empty document/route arrays mean unverified or unmapped, not that no documents/application process are required. No transaction endpoint is asserted.

| Proposed necessary check | Machine expression | Verified supporting claim | Effective date | Execution |
| --- | --- | --- | --- | --- |
| minimum-age | `age_years_at_enrolment gte 18` | minimum-age | Unknown | Disabled; human review required |
| maximum-age | `age_years_at_enrolment lte 40` | maximum-age | Unknown | Disabled; human review required |
| occupation | `is_unorganised_worker eq true` | occupation | Unknown | Disabled; human review required |
| tax | `is_income_taxpayer eq false` | tax | Unknown | Disabled; human review required |

These partial checks are neither a complete rule set nor an eligibility verdict. Unknown/missing citizen information must not be coerced to false. Provider/state/declaration checks remain manual, and no citizen answers are collected.

## PMUY

- Stable ID: `in-cen-000004`; draft: `schemes/in-cen-000004/cfd3b87792d2b0dc/draft.json`.
- SHA-256: `cfd3b87792d2b0dc52121a3df42260739c6ab2aed5f50135b743859da4a7477c`.
- Claim statuses: {'verified_official_guidance': 8, 'unresolved': 2, 'unverified': 1}; original conflicts preserved: 5.
- All target versions and translations remain draft; all rule nodes remain disabled/UNCERTAIN.

### Sources checked

| Source | Official document | Published | Effective | Capture/access |
| --- | --- | --- | --- | --- |
| UY-2025 | [Government approves release of 25 lakh additional LPG connections under Ujjwala](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=276350) | 2025-09-22 | Unknown | readable_captured |
| PMUY-FAQ | [Frequently asked questions on Ujjwala Scheme](https://www.pmuy.gov.in/faq.html) | Unknown | Unknown | readable_reuse_not_assessed |
| PMUY-ABOUT | [About PMUY](https://www.pmuy.gov.in/about.html) | Unknown | Unknown | readable_all_rights_reserved |

### Assertions and verification

| Claim | Exact research assertion | Status | Evidence locator |
| --- | --- | --- | --- |
| woman | Applicant is an adult woman from a poor household. | verified_official_guidance | [UY-2025](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=276350), Eligibility/application paragraph |
| poor | Simplified deprivation declaration is required. | verified_official_guidance | [UY-2025](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=276350), Eligibility/application paragraph |
| no-lpg | Family must have no existing LPG connection. | verified_official_guidance | [UY-2025](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=276350), Eligibility/application paragraph |
| benefit | Deposit-free connection, first refill and stove are provided. | verified_official_guidance | [UY-2025](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=276350), Connection package paragraph |
| documents | Simplified KYC and deprivation declaration are described. | verified_official_guidance | [UY-2025](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=276350), Eligibility/application paragraph |
| verification | De-duplication and physical OMC verification precede connection. | verified_official_guidance | [UY-2025](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=276350), Verification paragraph |
| enrolment | Public-sector OMC LPG distributors accept applications. | verified_official_guidance | [UY-2025](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=276350), Eligibility/application paragraph |
| adult-age | About page states attained 18; current dated phase applicability needs review. | unresolved | [PMUY-ABOUT](https://www.pmuy.gov.in/about.html), Eligibility criteria item 2 |
| kyc-detail | FAQ lists applicant/adult-family Aadhaar, bank, family and address proofs with migrant alternatives. | verified_official_guidance | [PMUY-FAQ](https://www.pmuy.gov.in/faq.html), Q6/Q9 |
| categories | About retains category/14-point routes; FAQ and 2025 PIB describe simplified declaration. | unresolved | [PMUY-ABOUT](https://www.pmuy.gov.in/about.html), Eligibility criteria versus FAQ Q1/Q2/Q29 |
| current-support | Current phase assistance rates and FY2026-27 refill subsidy were not established. | unverified | [UY-2025](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=276350), FY2025-26 announcement scope |

All rows above: checked 2026-10-31; rule/claim effective date not established. The full ledger carries uncertainty, conflict context and source publication dates. Corroborated claims remain unapproved.

### Preserved conflicts and remaining work

- **C-UY-01 / eligibility_categories**:
  - Archive assertion, not newly confirmed: SC/ST/PMAY-G/MBC/AAY/tea tribes/forest/islands/SECC/14-point poor-household routes. Sources: [S16](https://www.mopng.gov.in/files/marketing/lpg/75L-PMUY-SoP-10102023-(1).pdf) (p.2 section 1).
  - Archive assertion, not newly confirmed: FAQ says no such categories under current scheme; deprivation declaration is basis. Sources: [S15](https://www.pmuy.gov.in/faq.html) (Q1,Q2,Q29).
- **C-UY-02 / assistance**:
  - Archive assertion, not newly confirmed: INR1600 (14.2kg), INR1150 (5kg). Sources: [S14](https://www.pmuy.gov.in/about.html) (PMUY Benefits).
  - Archive assertion, not newly confirmed: INR2200 (14.2kg single/5kg double), INR1300 (5kg single). Sources: [S16](https://www.mopng.gov.in/files/marketing/lpg/75L-PMUY-SoP-10102023-(1).pdf) (p.2 section 2.1).
- **C-UY-03 / family_adult_boundary**:
  - Archive assertion, not newly confirmed: KYC field uses above 18 for family members. Sources: [S17](https://www.pmuy.gov.in/documents/Ujjwala-KYC.pdf) (p.1 field (c)).
  - Archive assertion, not newly confirmed: FAQ uses adults at date of KYC and says members newly major must be added. Sources: [S15](https://www.pmuy.gov.in/faq.html) (Q9,Q20).
- **C-UY-04 / ekyc**:
  - Archive assertion, not newly confirmed: SOP allows biometric/demographic/OTP preference sequence. Sources: [S16](https://www.mopng.gov.in/files/marketing/lpg/75L-PMUY-SoP-10102023-(1).pdf) (p.4 section 4(x)).
  - Archive assertion, not newly confirmed: FAQ requires biometric authentication. Sources: [S15](https://www.pmuy.gov.in/faq.html) (Q17).
- **C-UY-05 / document_version**:
  - Archive assertion, not newly confirmed: Form uses category and 14-point declaration fields. Sources: [S17](https://www.pmuy.gov.in/documents/Ujjwala-KYC.pdf) (p.1(f); p.2 category table).
  - Archive assertion, not newly confirmed: FAQ calls for revised form and deprivation declaration. Sources: [S15](https://www.pmuy.gov.in/faq.html) (Q19).

Publication blockers:

- Dated replacement SOP/form and current phase validity; category and deprivation declaration conflict.
- Family/adult boundary, Aadhaar/eKYC alternatives and latest document version.
- Phase-specific assistance amounts and current refill subsidy; do not reuse FY2025-26 cap for FY2026-27.
- Independent translations, full exclusions (including PNG) and usable online provider endpoint.

### Content and rule readiness

English: Deposit-free LPG connection support for adult women from poor households, subject to household and provider verification.

Hindi draft: गरीब परिवारों की वयस्क महिलाओं के लिए जमा राशि रहित एलपीजी कनेक्शन की सहायता; परिवार और प्रदाता द्वारा सत्यापन की शर्तें लागू हैं।

Both translations, all questions and child descriptions are AI-drafted/nonofficial and require independent bilingual review. Canonical English scheme naming is evidence-backed, but the combined translation row remains machine/draft. Original names, including historical/announced Hindi names, remain untouched in original_record.

Mapped document items: 2; benefits: 1; offline route descriptions: 1. Empty document/route arrays mean unverified or unmapped, not that no documents/application process are required. No transaction endpoint is asserted.

| Proposed necessary check | Machine expression | Verified supporting claim | Effective date | Execution |
| --- | --- | --- | --- | --- |
| woman | `is_adult_woman eq true` | woman | Unknown | Disabled; human review required |
| poor | `poor_household_declaration_accepted eq true` | poor | Unknown | Disabled; human review required |
| no-lpg | `household_has_existing_lpg eq false` | no-lpg | Unknown | Disabled; human review required |

These partial checks are neither a complete rule set nor an eligibility verdict. Unknown/missing citizen information must not be coerced to false. Provider/state/declaration checks remain manual, and no citizen answers are collected.

## IGNOAPS

- Stable ID: `in-cen-000005`; draft: `schemes/in-cen-000005/c64fff83bbc661f2/draft.json`.
- SHA-256: `c64fff83bbc661f2035e18f44805d2a9ac1bddfa6ccdd86e4e1fa6d7ce81d57a`.
- Claim statuses: {'verified_official_guidance': 6, 'unverified': 1, 'unresolved': 2}; original conflicts preserved: 3.
- All target versions and translations remain draft; all rule nodes remain disabled/UNCERTAIN.

### Sources checked

| Source | Official document | Published | Effective | Capture/access |
| --- | --- | --- | --- | --- |
| OLD-2026 | [ELDERLY SCHEMES AND BENEFICIARIES](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2226202&lang=1&reg=6) | 2026-02-11 | Unknown | readable_captured |
| OLD-2025 | [National Social Assistance Programme](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=155928&id=155928&lang=2&reg=48) | 2025-11-07 | Unknown | readable_captured |

### Assertions and verification

| Claim | Exact research assertion | Status | Evidence locator |
| --- | --- | --- | --- |
| age | IGNOAPS includes eligible BPL persons aged 60 and above. | verified_official_guidance | [OLD-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2226202&lang=1&reg=6), MoRD information paragraph |
| bpl | Eligibility is subject to household BPL criteria. | verified_official_guidance | [OLD-2025](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=155928&id=155928&lang=2&reg=48), IGNOAPS section |
| lower-benefit | Central share: INR 200 monthly for ages 60–79. | verified_official_guidance | [OLD-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2226202&lang=1&reg=6), MoRD information paragraph |
| higher-benefit | Central share: INR 500 monthly from age 80. | verified_official_guidance | [OLD-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2226202&lang=1&reg=6), MoRD information paragraph |
| state-topups | States/UTs are encouraged to supplement the central share. | verified_official_guidance | [OLD-2025](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=155928&id=155928&lang=2&reg=48), IGNOAPS section |
| local-process | Gram Panchayats and municipalities help identify beneficiaries. | verified_official_guidance | [OLD-2025](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=155928&id=155928&lang=2&reg=48), Features: selection |
| documents | Current state application and age/BPL evidence checklist remains unverified. | unverified | [OLD-2025](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=155928&id=155928&lang=2&reg=48), State implementation context |
| legacy | Legacy BPL-list exceptions and historical pension-category exclusions need reconciliation. | unresolved | [OLD-2025](https://www.pib.gov.in/PressNoteDetails.aspx?ModuleId=3&NoteId=155928&id=155928&lang=2&reg=48), Current summary omits archive legacy/category provisions |
| name | Archive renamed Hindi label and current cited IGNOAPS title need identity/date review. | unresolved | [OLD-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2226202&lang=1&reg=6), IGNOAPS name in current release |

All rows above: checked 2026-10-31; rule/claim effective date not established. The full ledger carries uncertainty, conflict context and source publication dates. Corroborated claims remain unapproved.

### Preserved conflicts and remaining work

- **C-OLD-01 / age_80_benefit_boundary**:
  - Archive assertion, not newly confirmed: INR500 for 80 and above. Sources: [S19](https://sje.rajasthan.gov.in/Schemes/Central%20Pension1.pdf) (II(ii)).
  - Archive assertion, not newly confirmed: Manual says above 80 for old-age pension. Sources: [S21](https://darpg.gov.in/sites/default/files/NSAP-District%20Manual_21.11.2017(1).pdf) (printed p.2 Table 1).
- **C-OLD-02 / category_exclusions**:
  - Archive assertion, not newly confirmed: 2012 order excludes widow/severe-multiple-disability BPL group ages 60-79. Sources: [S19](https://sje.rajasthan.gov.in/Schemes/Central%20Pension1.pdf) (I(i)).
  - Archive assertion, not newly confirmed: Undated FAQ gives general 60+/BPL criteria without these exclusions. Sources: [S20](https://www.dord.gov.in/static/uploads/2024/07/1ff5b85d83a44d7b22cda3b40547ed4c.pdf) (Q13,Q16).
  - Archive assertion, not newly confirmed: 2014 section 2.3 states general age/BPL criteria; historical category exclusions need reconciliation. Sources: [S59](https://ssepd.odisha.gov.in/sites/default/files/2026-03/GUIDELINES%20ON%20NATIONAL%20SOCIAL%20ASSISTANCE%20PROGRAMME%20%28NSAP%29.pdf) (PDF p.12 / printed p.6 section 2.3).
- **C-OLD-03 / legacy_bpl_exception**:
  - Archive assertion, not newly confirmed: New eligibility requires BPL household. Sources: [S20](https://www.dord.gov.in/static/uploads/2024/07/1ff5b85d83a44d7b22cda3b40547ed4c.pdf) (Q13).
  - Archive assertion, not newly confirmed: Previously eligible legacy beneficiaries not on BPL list may continue. Sources: [S20](https://www.dord.gov.in/static/uploads/2024/07/1ff5b85d83a44d7b22cda3b40547ed4c.pdf) (Q9).

Publication blockers:

- Historical category exclusions, legacy BPL-list exceptions and age-80 wording remain preserved.
- Verify one intended state application route, documentary alternatives, state top-ups and beneficiary selection process.
- Exact reference date and no automatic rejection for BPL-list omission; central share is not total entitlement.
- Name/renaming identity and effective date, complete current policy and bilingual review.

### Content and rule readiness

English: Central old-age pension assistance under NSAP for eligible older people in BPL households; state support is separate.

Hindi draft: गरीबी रेखा से नीचे के परिवारों के पात्र बुजुर्गों के लिए एनएसएपी के अंतर्गत केंद्रीय वृद्धावस्था पेंशन सहायता; राज्य की सहायता अलग है।

Both translations, all questions and child descriptions are AI-drafted/nonofficial and require independent bilingual review. Canonical English scheme naming is evidence-backed, but the combined translation row remains machine/draft. Original names, including historical/announced Hindi names, remain untouched in original_record.

Mapped document items: 0; benefits: 2; offline route descriptions: 0. Empty document/route arrays mean unverified or unmapped, not that no documents/application process are required. No transaction endpoint is asserted.

| Proposed necessary check | Machine expression | Verified supporting claim | Effective date | Execution |
| --- | --- | --- | --- | --- |
| age | `age_years_at_application gte 60` | age | Unknown | Disabled; human review required |
| bpl | `bpl_household_officially_assessed eq true` | bpl | Unknown | Disabled; human review required |

These partial checks are neither a complete rule set nor an eligibility verdict. Unknown/missing citizen information must not be coerced to false. Provider/state/declaration checks remain manual, and no citizen answers are collected.

## Aggregate and publication status

Five drafts; claim-status counts: `{'verified_official_guidance': 49, 'unverified': 4, 'unresolved': 11}`. All 17 original conflict groups across these five detailed records are retained.

The local rehearsal contains 153 unique catalogue rows, five local ingestion-run rows and five full-payload receipts. It has ten draft translation rows, 21 disabled rule nodes (16 predicates and five AND roots), and zero published versions. See PHASE3D_STAGING_REPORT.md for validation and transaction results.

All five require human review before any live draft import authorization. The PMUY 2025 release corroborates a simplified declaration but does not establish the full amendment chain or FY2026-27 subsidy. IGNOAPS amounts are central shares, with state top-ups deliberately uncollected. PM-SYM conflicting figures are retained without a contribution calculator. PMJJBY accident-lien and birthday details are not silently generalized.
