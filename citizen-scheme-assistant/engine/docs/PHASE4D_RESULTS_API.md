# Phase 4D bilingual results and application guidance

`POST /api/v1/results/explain` re-evaluates a validated questionnaire state through
the existing trusted provider. It then reads guidance for the exact approved
published version. It accepts neither client eligibility results/statuses nor
rules. There is no LLM, new execution approval, publication or persistent citizen
profile. The default approval manifest remains empty: the five real schemes
continue to return NEEDS_VERIFICATION with explicit unavailable guidance.

## Frontend request

Use the most recently returned Phase 4B `state`, including its policy fingerprint:

```javascript
const questionnaire = await fetch("http://localhost:8000/api/v1/questionnaire/start", {
  method: "POST", headers: {"Content-Type": "application/json"},
  body: JSON.stringify({scheme_id: "in-cen-000002", language: "hi"})
}).then(response => response.json());

const response = await fetch("http://localhost:8000/api/v1/results/explain", {
  method: "POST", headers: {"Content-Type": "application/json"}, cache: "no-store",
  body: JSON.stringify({state: questionnaire.state})
});
const result = await response.json();
// Handle non-2xx responses before rendering. Do not log state or answer bodies.
```

For an approved interactive policy, send the state from the last answer instead.
Call before completion if needed: missing answers remain NEEDS_VERIFICATION.
Switch language by changing only `state.language` to en/hi. The fingerprint still
binds the exact policy. On POLICY_CHANGED (409), restart the questionnaire; do not
silently replay old answers against different rules. Skips and explicit null
answers retain their Phase 4B meaning. Invalid language, injected results/rules or
invalid answer state return sanitized HTTP 422. Database/configuration failures
return existing sanitized HTTP 503 errors.

The exact request/response DTOs are in `/docs` and `app/schemas/results.py`. This
is additive to the existing APIs and is not the legacy bulk eligibility contract;
no frontend or `contracts/` file was changed.

## Response fields

| Field | Meaning |
| --- | --- |
| scheme_id / language | Requested stable ID and display language |
| scheme_name | Reviewed published name, reviewed English fallback, or unavailable |
| eligibility_status | Server-recomputed ELIGIBLE, INELIGIBLE or NEEDS_VERIFICATION |
| explanation / assessment_notice | Bilingual system explanation and no-guarantee notice |
| conditions_satisfied / conditions_not_satisfied | Existing deterministic condition results, with rule IDs, source IDs and language metadata |
| missing_information | Unanswered, unknown, skipped, unreviewed-question fields and review blockers |
| benefits | Reviewed descriptions and original amounts/currency/frequency; no payment calculation |
| required_documents | Reviewed document names, requirement codes and original conditional wording |
| application_guidance | Alternative routes, each with source-backed instructions in steps, mode, URL availability and verification date |
| official_application_urls | Only separately verified application URLs, with route/source IDs |
| sources | Deduplicated exact source references, locators, checked dates and capture hashes |
| last_verification_date | Earliest available checked date among returned sources/version metadata; null when unavailable |
| evaluation | Full Phase 4A evaluation, policy version/review status and supporting evidence |

Responses do not echo citizen answer values or state. Every successful response
and error uses `Cache-Control: no-store`. Answers are neither stored nor passed
to the guidance repository. Keep frontend state ephemeral and disable body logging
in deployment infrastructure as described in the questionnaire guide.

### Current draft behavior

For the present unapproved PMSBY state, the response includes the following
excerpt (the full DTO also contains the condition lists, evaluation and sources):

```json
{
  "scheme_id": "in-cen-000002",
  "language": "hi",
  "scheme_name": {
    "text": null,
    "requested_language": "hi",
    "content_language": null,
    "translation_fallback": false,
    "review_status": "unavailable",
    "origin": "unavailable",
    "is_official_translation": false,
    "source_ids": []
  },
  "eligibility_status": "NEEDS_VERIFICATION",
  "last_verification_date": null,
  "benefits": {
    "status": "unavailable",
    "reason_code": "GUIDANCE_UNAVAILABLE",
    "items": []
  },
  "required_documents": {
    "status": "unavailable",
    "reason_code": "GUIDANCE_UNAVAILABLE",
    "items": []
  },
  "application_guidance": {
    "status": "unavailable",
    "reason_code": "GUIDANCE_UNAVAILABLE",
    "items": []
  }
}
```

Section excerpts omit their localized `message`. An unavailable section never
means “no documents/benefits are required.” No draft text, name or application
URL is borrowed from the local research output.

### Approved content and fallback

For an approved synthetic fixture requesting Hindi, a reviewed English benefit
description is represented like this (test content, not a government claim):

```json
{
  "text": "Synthetic conditional support",
  "requested_language": "hi",
  "content_language": "en",
  "translation_fallback": true,
  "review_status": "reviewed",
  "origin": "source_text",
  "is_official_translation": false,
  "source_ids": ["the-actual-evidence-id"]
}
```

The illustrative evidence ID above is a placeholder; actual responses preserve
the published UUID. Render `content_language` and fallback explicitly. All system
availability, requirement, outcome and disclaimer messages support en/hi. System
text is labeled `origin=system`, never an official scheme translation.

Names use only `published_translations` rows with review_status=reviewed: requested
language first, then English. A reviewed machine/human translation remains labeled
machine/human; only an explicitly official-origin reviewed row gets
is_official_translation=true. Missing reviewed English is not silently replaced
by Hindi for an English request. Child text is returned in its attested source
language; English is an explicit fallback for Hindi, not a generated translation.

## Trusted data and guidance review

The existing catalogue lacks child-language/review columns and structured ordered
application steps. Phase 4D does not invent database columns or assume that all
unlocalized text is approved English. `ExecutionApproval.guidance` is an optional
server-owned review object, default null, containing:

- Exact normalized guidance snapshot SHA-256, reviewer reference/date and expiry.
- Per-benefit/document/route item UUIDs and reviewed source language (en/hi).
- An explicit application_url_verified flag for route URLs and an exact allowed
  application-host list, separate from the policy's source-host list.

The snapshot binds the exact version, all reviewed translation rows, benefits,
documents, routes and their source evidence. Each returned child must have a
matching item review, checked provenance and suitable reviewed wording. Sections
are available, partial or unavailable according to how much can safely be shown.
Expired, absent or mismatched guidance review withholds children; reviewed names
can still be shown independently from published reviewed translations.

The manifest contains no copied benefit/document/application text and cannot
override the database wording or URLs. Language review attests all relevant text
fields of that row; mixed-language rows require correction/review before use.
No real guidance review entry is created by this task. Adding/changing guidance
review changes the existing execution-approval digest and therefore invalidates
old questionnaire fingerprints; a restart is required. The optional field is
additive but introduces this deliberate version-safety behavior on deployment.

`PublishedGuidanceRepository` uses only existing published views and the restricted
read-only connection, with exact stable ID/version UUID parameters. No latest
translation or guidance from another version is substituted. The provider checks
identity/version before exposing context. Changed source metadata between policy
and guidance reads is rejected if the same evidence ID no longer matches; two
different references are never silently merged.

No additional migration or permissions are needed. A future centralized approval
store can include these review attestations as part of the separately reviewed
design described in PHASE4C_TRUSTED_POLICY_PROVIDER.md.

## Application and eligibility safeguards

Each route's original instructions are returned intact as one source-backed step.
Separate routes are alternatives, not invented sequential steps. No LLM rewrites
or splits instructions. An offline route may have verified instructions while its
URL status remains unavailable. No URL is derived from an evidence URL, ministry
homepage or scheme name. Application URLs require explicit role verification,
approved HTTPS host and no embedded credentials. The API does not visit links or
guarantee that applications are currently open.

Benefits are descriptive published values, not calculated entitlements. Never sum
alternative benefit rows or interpret a central contribution as a state's total.
Conditional documents preserve their original condition; unknown requirement codes
remain unknown. A missing condition is not replaced with an invented explanation.

Condition lists include individual AND/OR/NOT expressions. A failed optional OR
leaf does not overrule an ELIGIBLE root; an exclusion predicate can match while its
NOT group fails. Use `eligibility_status` and `evaluation.explanation` for the
overall decision. The bilingual notice explicitly says assessment does not
guarantee government approval, enrolment or benefit disbursement.

## Integration and remaining work

Frontend should render the outcome, notice, missing-information state and section
availability before listing items, preserve language labels and support reviewed
English fallback. Use source_ids to link to sources. No frontend implementation
is included here. Real use remains blocked by the Phase 3D policy/bilingual review,
authorized publication and exact execution approval. Guidance additionally needs
source-language attestations, document/route review and verified application URLs.

Next backend work: build read-only reviewer previews for exact policy/guidance
digests and missing attestations, followed by reviewed per-item bilingual content
support. Do not auto-approve registry entries, publish drafts or introduce a live
writer as part of that preview workflow.

## Files and validation

Added `app/db/guidance.py`, `app/schemas/results.py`,
`app/eligibility/results.py`, `app/api/routes/results.py`,
`tests/test_results.py` and this guide. Updated `app/eligibility/approvals.py`
with optional guidance review metadata, `app/eligibility/provider.py` with the
exact-version guidance lookup, `main.py` with router registration, and
`app/core/errors.py` with no-store handling for results errors.

All 14 focused result tests passed. The complete suite ran once: 108 Python tests,
eight catalogue checks, nine single-scheme staging checks, six batch staging checks
and one isolated payload check passed (132 total). Coverage includes en/hi/fallback,
all outcomes, missing guidance/URLs, unapproved/unpublished schemes, invalid and
tampered requests, stale versions, review expiry, source preservation and privacy.
Existing endpoints remain compatible. No dependency was added and no .env,
migration, permission, frontend or real approval record was changed. No live
Supabase access, scheme publication, commit or push occurred.
