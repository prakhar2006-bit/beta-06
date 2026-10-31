# Phase 3 eligibility readiness

All proposals are disabled and confidence UNCERTAIN. No citizen is declared eligible. Review priority and question prompts are local proposals, not official scheme translations. No user answers or personal data are collected.

## Structural assessment

The independent preparation checks flag ten conditions as structurally incomplete
(missing a structured field/operator/value, an exact-wording anchor or evidence).
Five conditions have a mechanically representable form after review; this is not
a factual approval. The categories can overlap with conflicts, and all 20 remain
disabled. Record-specific incomplete_condition_ids are retained in the manifest.

The five detailed records supply 20 conditions (four each); eleven discovery records have none. Missing exclusions must not be treated as verified none. All five detailed drafts contain conflicts: therefore every condition remains in the conservative ambiguous_or_conflicting review bucket. A separate mechanically_representable_after_review flag marks supplied comparisons/ranges that could become deterministic after a reviewer validates source, units, scope, reference dates and exclusions.

Existing JSON contracts use a different attribute/operator vocabulary (for example age versus age_years, annual income versus individual-worker monthly income). Do not substitute fields or multiply thresholds without a reviewed contract adapter. No machine expression or target JSON rule is emitted for execution.

## Five candidate question structures

Each question carries question_id, field, prompt_source_text, question_template_en, evidence, requires_human_review=true and enabled=false. Questions without structured attributes remain reviewer-defined. Hindi prompts are absent and must be translated/reviewed separately.

### IN-CEN-000002 ? Pradhan Mantri Suraksha Bima Yojana

| Rule | Supplied field/operator | Mechanically representable after review | Proposed question |
| --- | --- | --- | --- |
| SB-E1 | age_years / range_as_worded | False | What is the applicant age in years at the reviewed reference date? |
| SB-E2 | None / None | False | Reviewer must define a question and evidence requirements for this source assertion. |
| SB-E3 | None / None | False | Reviewer must define a question and evidence requirements for this source assertion. |
| SB-E4 | None / None | False | Reviewer must define a question and evidence requirements for this source assertion. |

- Additional information: applicant answers for reviewed attributes; no values are collected in this phase.
- Human verification: complete rule/exclusion set, full source clause, amendments and current version; documents are assertions until checked.
- Ambiguities: premium_and_cover_start; age_70_boundary.
- Exact source statements, values, period, currency, reference date and citations remain in manifest condition_proposals[].source_assertion.

### IN-CEN-000001 ? Pradhan Mantri Jeevan Jyoti Bima Yojana

| Rule | Supplied field/operator | Mechanically representable after review | Proposed question |
| --- | --- | --- | --- |
| JJ-E1 | age_years / range_as_worded | False | What is the applicant age in years at the reviewed reference date? |
| JJ-E2 | enrolment_accounts / = | True | How many accounts are enrolled in this scheme? |
| JJ-E3 | None / None | False | Reviewer must define a question and evidence requirements for this source assertion. |
| JJ-E4 | None / None | False | Reviewer must define a question and evidence requirements for this source assertion. |

- Additional information: applicant answers for reviewed attributes; no values are collected in this phase.
- Human verification: complete rule/exclusion set, full source clause, amendments and current version; documents are assertions until checked.
- Ambiguities: premium_and_enrolment; age_reference; lien_scope.
- Exact source statements, values, period, currency, reference date and citations remain in manifest condition_proposals[].source_assertion.

### IN-CEN-000005 ? Indira Gandhi National Old Age Pension Scheme

| Rule | Supplied field/operator | Mechanically representable after review | Proposed question |
| --- | --- | --- | --- |
| OLD-E1 | age_years / >= | False | What is the applicant age in years at the reviewed reference date? |
| OLD-E2 | bpl_status / = | True | Has household BPL status been established under the applicable official process? |
| OLD-E3 | age_years / >= | False | What is the applicant age in years at the reviewed reference date? |
| OLD-E4 | bpl_list_omission / manual_assessment_required | False | Is the household missing from the applicable BPL list? |

- Additional information: applicant answers for reviewed attributes; no values are collected in this phase.
- Human verification: complete rule/exclusion set, full source clause, amendments and current version; documents are assertions until checked.
- Ambiguities: age_80_benefit_boundary; category_exclusions; legacy_bpl_exception.
- Exact source statements, values, period, currency, reference date and citations remain in manifest condition_proposals[].source_assertion.

### IN-CEN-000003 ? Pradhan Mantri Shram Yogi Maan-dhan

| Rule | Supplied field/operator | Mechanically representable after review | Proposed question |
| --- | --- | --- | --- |
| SYM-E1 | employment_category / = | True | What is the applicant employment category? |
| SYM-E2 | income / <= | True | What is the applicant income for the reviewed currency, period and person/household scope? |
| SYM-E3 | age_years / inclusive_range | True | What is the applicant age in years at the reviewed reference date? |
| SYM-E4 | None / None | False | Reviewer must define a question and evidence requirements for this source assertion. |

- Additional information: applicant answers for reviewed attributes; no values are collected in this phase.
- Human verification: complete rule/exclusion set, full source clause, amendments and current version; documents are assertions until checked.
- Ambiguities: income_operator; contribution_at_age_20; other_pensions_exclusion; citizenship.
- Exact source statements, values, period, currency, reference date and citations remain in manifest condition_proposals[].source_assertion.

### IN-CEN-000004 ? Pradhan Mantri Ujjwala Yojana

| Rule | Supplied field/operator | Mechanically representable after review | Proposed question |
| --- | --- | --- | --- |
| UY-E1 | None / None | False | Reviewer must define a question and evidence requirements for this source assertion. |
| UY-E2 | age_years / >= | False | What is the applicant age in years at the reviewed reference date? |
| UY-E3 | None / None | False | Reviewer must define a question and evidence requirements for this source assertion. |
| UY-E4 | None / None | False | Reviewer must define a question and evidence requirements for this source assertion. |

- Additional information: applicant answers for reviewed attributes; no values are collected in this phase.
- Human verification: complete rule/exclusion set, full source clause, amendments and current version; documents are assertions until checked.
- Ambiguities: eligibility_categories; assistance; family_adult_boundary; ekyc; document_version.
- Exact source statements, values, period, currency, reference date and citations remain in manifest condition_proposals[].source_assertion.

## What can become deterministic

- Age: explicit >= or reviewed inclusive_range can become comparisons only after defining the measurement date. range_as_worded and the PMSBY age-70 termination boundary are blocked.
- Income: PM-SYM supplies an individual-worker monthly INR comparison; strict versus inclusive boundary is conflicting. Do not replace it with annual household income.
- Occupation: PM-SYM supplies equality to unorganised_worker; a reviewed occupation vocabulary and definition are required.
- Household: IGNOAPS supplies BPL status; omission from the BPL list requires human assessment and must not become automatic rejection. No numeric poverty threshold is invented.
- Gender, residence and existing LPG connection: PMUY has cited prose, not a complete structured condition. Reviewer must establish current household/adult definitions, phase and document applicability before defining attributes.
- Existing pension/benefit enrollment: preserve exclusions and competing versions. Current statements do not justify automatic rules.

## Language fallback compatible with Phase 2

Retain every supplied English/Hindi field. Prefer requested reviewed translation, fall back to the other stored language and expose actual language plus translation_fallback. If neither exists, return null, never invent text. The archive has no full translation objects; four approved Hindi renaming names cannot be promoted to complete translations. Existing child text has no language column, so Phase 2 must keep it verbatim and explicitly unlocalized. Nothing is published by this tool.

See PHASE3_IMPORT_PLAN.md for the review and authorization gates before any writer or publication workflow is implemented.
