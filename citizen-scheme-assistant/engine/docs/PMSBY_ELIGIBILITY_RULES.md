# PMSBY pilot rule review — 31 October 2026

Stable ID proposal: `in-cen-000002`; archive ID: `IN-CEN-000002`.
No eligibility evaluator or final decision is implemented. Every prepared rule
remains disabled in the review sidecar, confidence UNCERTAIN in the mapped rows,
and attached to an unpublished draft version. The database has no enabled column;
do not add one to an INSERT or treat the absence of that column as authorization.

## Necessary conditions supported by official guidance

The [Ministry of Finance's 9 May 2026 PIB release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259251&lang=1&reg=6),
section 2, supports a participating individual bank/post-office account, enrolment
and auto-debit consent, one enrolment account, and an entry range beginning at 18.
These are necessary conditions, not a complete sufficient eligibility definition.

| Draft predicate | Proposed citizen field | Operator/value | Remaining check |
| --- | --- | --- | --- |
| minimum-age | age_years_at_enrolment | gte / 18 | Completed-age/date convention requires reviewer approval; does not resolve maximum age. |
| account | participating_individual_account | eq / true | Provider must confirm account ownership/type/participation; self-report is not certification. |
| consent | enrolment_and_autodebit_consent | eq / true | Affirmative consent to both items; no implication that premium was paid. |
| single-account | scheme_enrolment_account_count | eq / 1 | Includes proposed enrolment; not a count of all bank accounts. Renewal does not create another account. |

These four predicates are children of an AND node. The node explicitly says the
set is incomplete. All have rule_evidence links to captured official material.
Unknown answers must result in UNCERTAIN; no citizen inputs are persisted.
The attributes above are proposals, not additions to the shared citizen-profile
contract. A future reviewed adapter/question vocabulary is required.

## No executable upper-age condition

The [2025 PIB explainer PDF](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/may/doc202558551401.pdf),
pages 3–4, combines an 18–70 entry range with termination at 70 using a nearest
birthday convention. [DFS guidance](https://financialservices.gov.in/pmsby)
and the historical India Post rules carry the same issue. No `age <= 70`,
`age < 70`, nearest-birthday function, or inferred date-of-birth cutoff is emitted.
The unresolved condition has expression=null and enabled=false in the ledger.
An age-69 example would not establish overall eligibility either: provider,
coverage and other policy checks remain necessary.

## Manual/unresolved conditions

- Full amendment chain, actual risk commencement and provider-specific policy terms.
- Current KYC/form version, account participation, available balance and premium debit.
- Documentary and medical assessment for a claim, including covered disability
  definitions. Claim eligibility is separate from scheme enrolment eligibility.
- NRI circumstances: DFS guidance allows qualifying India-branch accounts subject
  to terms; do not invent an Indian-citizenship exclusion.
- Do not add income, occupation, caste, gender or state predicates from silence in
  a summary. No such numeric/Boolean gate is established by this pilot.
- Consent forms are supported, but the current complete provider KYC checklist
  and a universal usable application URL are not verified.

## Bilingual questions and explanations

The machine-readable draft contains four English/Hindi question pairs, benefits,
documents, descriptions and explanations. Official Hindi title and a short
description excerpt are identified by field-level provenance. All other drafted
summaries, adaptations, questions and explanations are marked AI-drafted,
nonofficial and requiring human review. Translation rows remain review_status=draft
and translation_origin=machine because the combined row includes drafted text.

The schema stores only scheme-level translations. Bilingual benefit/document/
question/explanation text therefore stays in a retained sidecar, not invented
columns or silently discarded strings. Phase 2 does not currently serve that
sidecar. Its existing source-language fallback remains unchanged.

Before enabling any deterministic check, a human must approve the cited rule
scope, time basis, attribute semantics, unresolved conditions and translations.
Passing the four checks must never be returned as an overall ELIGIBLE decision.
