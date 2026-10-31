# PMSBY human review checklist

No item below is approved automatically. Record reviewer name/reference, date,
decision, evidence locator, source issue/effective dates and bundle digest for
each decision. Use `PMSBY_VERIFICATION_REPORT.md` and the full research ledger.
An AI checked date is not a human approval date.

## Publication blockers (all remain open pending human review)

- [ ] Verify issuing authority, complete current policy/amendment chain and
  applicability of the cited official guidance; distinguish publication from
  effective dates. Recheck source access/reuse permissions. Keep unavailable
  Jan Suraksha sources explicitly unverified; obtain documents through permitted channels.
- [ ] Resolve entry versus termination age, including nearest/completed birthday
  conventions. Do not approve an inclusive `age <= 70` shortcut.
- [ ] Resolve debit-date versus following-month risk commencement, late entry,
  rejoining, renewal and the June–May coverage cycle against current provider terms.
- [ ] Review account closure, insufficient balance/premium debit, age termination
  and multiple-account provisions; distinguish enrolment from claim assessment.
- [ ] Approve individual participating account, consent, minimum-age and single
  scheme-enrolment-account semantics. Review NRI/provider circumstances. The four
  proposed necessary checks are incomplete and must not imply overall eligibility.
- [ ] Confirm premium chronology (historical INR 12 versus standard INR 20),
  effective date and any provider adjustment. Review exact accidental death and
  covered irreversible disability definitions, INR 200000/100000 amounts and
  exclusions. Do not describe all disability or hospitalization as insured.
- [ ] Verify a current provider application route/form and its usability; an
  announcement or informational homepage is not a transaction endpoint.
- [ ] Verify prescribed consent form and complete current provider KYC/document
  checklist, with conditional requirements. Do not infer mandatory universal
  Aadhaar from historical text.
- [ ] Review English descriptions, benefits, questions and explanations for policy
  fidelity and distinction between insurance cover and a cash entitlement.
- [ ] Have a Hindi reviewer approve every drafted/adapted field. Preserve the
  provenance of official title/excerpts; new translations are not official.
- [ ] Preserve both original archive conflicts and the current unresolved-condition
  ledger. Document resolutions without deleting contradictory historical evidence.
- [ ] Approve a complete deterministic rule scope and citizen-question/time-basis
  specification. No LLM final decisions. Keep all existing proposed rules disabled
  until a separate reviewed implementation authorizes their use.
- [ ] Resolve how bilingual child content and disabled-rule review metadata will
  be retained and served. The current schema/API has no sidecar fields or rule
  `enabled` column; draft visibility is currently the protection.
- [ ] Complete an independent release review. SQL constraints alone do not enforce
  every policy gate above and do not constitute publication approval.

## Draft-only staging approval (does not approve publication)

- [ ] Reviewer explicitly accepts this incomplete draft and enumerates retained blockers.
- [ ] Bind approval to the full input digest, source hashes, version preview and
  named isolated staging target; retain the complete ledger and bilingual sidecar.
- [ ] Confirm separate writer authorization, transactional receipt storage, target
  identity, existing-record conflicts and rollback procedure per the live runbook.
- [ ] Keep status `draft`, translation status `draft`, confidence `UNCERTAIN`,
  no review/publication timestamps, and no executable rules.

## Optional improvements (not substitutes for blockers)

- [ ] Add reviewed plain-language examples and accessibility wording.
- [ ] Add more provider-specific routes after verification rather than requiring
  every provider route before the first supported route is released.
- [ ] Broaden official language support beyond English/Hindi.
- [ ] Add monitoring for source changes and periodic reviewer reminders.

Reviewer reference: __________  Date: __________  Bundle digest: __________

Decision: pending / corrections required / draft-only staging approved.
Publication is a separate decision and is not offered by the import tool.
