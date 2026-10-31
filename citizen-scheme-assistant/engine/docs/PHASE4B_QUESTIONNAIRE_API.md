# Phase 4B questionnaire API

All routes are POST, documented in `/docs`:

| Endpoint | Body | Purpose |
| --- | --- | --- |
| `/api/v1/questionnaire/start` | `{scheme_id, language?}` | Start with empty answers |
| `/api/v1/questionnaire/next` | `{state}` | Recompute current question; safe to repeat |
| `/api/v1/questionnaire/answer` | `{state, question_id, action?, value?}` | Answer, skip, edit or clear |

No server session, cookie, profile, token, database write or answer log is created.
Keep returned `state` only in frontend memory or session storage with Clear Data;
clear it on logout, session end or shared-phone handover. Do not put it in URLs,
localStorage, analytics, console logs or persistent caches. State is sensitive
plain JSON returned only to the requesting client; it is not encrypted or signed.
Use HTTPS when deployed and disable request/response-body logging in infrastructure.
Responses, including errors, carry `Cache-Control: no-store`.

No government scheme is currently execution-approved. Starting any of the five
drafts produces a completed NEEDS_VERIFICATION response with no question. The
interactive examples below require an independently approved policy or the
isolated synthetic test override; synthetic fixtures are not exposed by the
normal server. No draft rules or government translations were activated.

## Start and inspect the response

```javascript
const base = "http://localhost:8000/api/v1/questionnaire";
async function post(action, body) {
  const response = await fetch(`${base}/${action}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw data.error; // Display a localized error; do not log state.
  return data;
}
let q = await post("start", { scheme_id: "in-cen-000002", language: "en" });
```

For the present PMSBY draft, the response includes:

```json
{
  "schema_version": "1.0",
  "state": {
    "scheme_id": "in-cen-000002",
    "answers": {},
    "language": "en",
    "state_version": "1.0",
    "policy_fingerprint": null,
    "skipped": []
  },
  "current_question": null,
  "completed": true,
  "completion_reason": "VERIFICATION_REQUIRED",
  "progress": {"answered": 0, "unknown": 0, "skipped": 0, "remaining": 0}
}
```

This is an excerpt: the full response also includes `evaluation` and
`missing_information`. `evaluation.status` is NEEDS_VERIFICATION and its policy
blocker is RULE_SET_UNAVAILABLE. Never interpret `completed` as ELIGIBLE.

## Answer, skip, unknown and change

For an interactive approved questionnaire, always send the most recently returned
state and the server's question ID. The client supplies answers, not rules,
eligibility flags, source citations or progress calculations.

```javascript
// Example age answer: number 30, not string "30".
q = await post("answer", {
  state: q.state, question_id: q.current_question.question_id,
  action: "answer", value: 30
});

// Skip: omit value entirely. Moves to the next relevant question.
q = await post("answer", {
  state: q.state, question_id: q.current_question.question_id, action: "skip"
});

// Explicit "I don't know": null is retained and is not treated as false.
q = await post("answer", {
  state: q.state, question_id: q.current_question.question_id,
  action: "answer", value: null
});

// Change an earlier age answer (use the saved question ID, not a guessed key).
q = await post("answer", {
  state: q.state, question_id: savedAgeQuestionId, action: "answer", value: 35
});

// Clear a previous answer/skip so the question may be asked again if relevant.
q = await post("answer", {
  state: q.state, question_id: savedAgeQuestionId, action: "clear"
});

// Refresh without changing answers. This never advances past an unanswered question.
q = await post("next", {state: q.state});
```

Each snippet is a separate operation guarded by `current_question !== null` where
needed; do not run them blindly in sequence. Answering a previous question may
reopen a completed questionnaire. Skip and null dispositions suppress automatic
repetition but can be replaced or cleared. `clear` does not accept a value. A field
cannot be both skipped and present in answers. Changes do not delete other answers;
the evaluator decides which remain relevant. Discard older concurrent responses
client-side so a slow request cannot overwrite newer state.

`current_question` contains:

- `question_id` (stable attribute key within the bound policy), affected `rule_ids`,
  `text`, `answer_type` and `kind`.
- `allowed_values`: Boolean true/false or reviewed category codes. Empty means a
  scalar numeric input, not that no answer is allowed. `choices` repeats category
  codes for compatibility with the Phase 4A Question DTO.
- `unit`, `period`, `scope`, `reference_basis` and exact `source_ids`.
- `content_language` and `translation_fallback`; no translation is generated.

Types: age is a nonnegative JSON integer; Boolean requires true/false; categories
require an exact allowed string. Income accepts a plain decimal string (preferred)
or finite JSON number, up to six fractional digits, with no period/currency
conversion. General numbers are finite. Phase 4A magnitude bounds apply. Empty
strings, invalid categories and malformed values are rejected rather than skipped.

## Hindi and fallback

```javascript
q = await post("start", {scheme_id: approvedSchemeId, language: "hi"});
// Switch the display language without changing answers:
q = await post("next", {state: {...q.state, language: "hi"}});
```

The trusted AnswerField model now has `question_reviewed_languages`, default
`["en"]` for compatibility with existing trusted English question definitions.
Hindi is used only when both text and explicit `"hi"` review metadata exist.
Otherwise reviewed English is returned with `content_language="en"` and
`translation_fallback=true`. If neither a requested Hindi nor fallback English
prompt is reviewed, that question is withheld and flagged in
`missing_information.unreviewed_question_fields`. No unreviewed Hindi prompt is
exposed through the nested `evaluation.questions_needed` either.

Use language metadata for display and speech selection. Reviewed question text
does not imply that the translation is an official government translation.

## Completion and NEEDS_VERIFICATION

Example completed eligible synthetic flow (response excerpt):

```json
{
  "current_question": null,
  "completed": true,
  "completion_reason": "DECISION_REACHED",
  "progress": {"answered": 1, "unknown": 0, "skipped": 0, "remaining": 0},
  "evaluation": {"status": "ELIGIBLE"}
}
```

Render the actual `evaluation.explanation`, condition results and source references
from the full response; the excerpt is not the entire EvaluationResponse schema.
There are three completion reasons:

| Reason | Frontend action |
| --- | --- |
| QUESTIONS_REMAIN | Render current_question; evaluation may still be NEEDS_VERIFICATION |
| DECISION_REACHED | Show ELIGIBLE/INELIGIBLE explanation and provenance; retain edit controls |
| VERIFICATION_REQUIRED | No more automatic questions; show missing information/manual-review needs, never success |

`missing_information` distinguishes unanswered, explicit unknown, skipped and
unreviewed-question fields from policy review blockers. `evaluation` preserves
Phase 4A policy status, evaluated conditions, source references and explanations.
Its question list is filtered to reviewed, non-disposed relevant candidates.
`progress` counts known answers, explicit unknowns, skips and remaining askable
questions; remaining includes the current question. These counts adapt as branches
resolve, so there is no fixed percentage or guaranteed total. A completed session
can still require verification after all questions were skipped or policy review
is incomplete. Never manufacture an eligibility result client-side.

## Error responses

Errors use the existing sanitized envelope, for example:

```json
{"error":{"code":"POLICY_CHANGED","message":"The policy changed. Start a new questionnaire."}}
```

| HTTP / code | Meaning |
| --- | --- |
| 422 INVALID_REQUEST | Malformed state/request, unsupported language, overlapping dispositions, nested values or injected fields |
| 422 INVALID_STATE | State contains fields not referenced by the resolved policy |
| 422 INVALID_ANSWERS | Answer type/category does not match the reviewed field |
| 409 POLICY_CHANGED | Content, approval, wording or source metadata changed; restart and clear old state |
| 409 QUESTION_NOT_PENDING | Question is neither currently relevant nor previously answered/skipped, or invalid clear |
| 409 QUESTION_NOT_REVIEWED | No reviewed question text for a new answer operation |
| 503 RULE_SET_INVALID | Provider returned invalid/mismatched policy identity |
| 500 INTERNAL_ERROR | Sanitized server failure; no answer values echoed |

Do not automatically replay stale answers after a policy change. Preserve no claim
that answers are externally verified: the public SHA-256 fingerprint detects
policy changes, not client-state tampering or identity. Self-declared answers are
validated and all outcomes recomputed using the current trusted provider. The
server never trusts client-supplied rules, approval, completion or progress.

## Implementation and next integration steps

`app/eligibility/questionnaire.py` wraps the existing evaluator. Selection uses
only its relevant questions, prioritizing NOT paths, shared-rule coverage, simpler
answer types, then attribute key. This is deterministic, not a probability or
minimum-question guarantee. Answered/null/skipped fields are not selected again;
AND/OR/NOT short-circuits and early ineligibility come from Phase 4A. Incomplete
policies can never produce ELIGIBLE through questionnaire actions.

New DTOs are in `app/schemas/questionnaire.py`; routes are in
`app/api/routes/questionnaire.py`. `main.py` registers them. No state table, session
registry, credentials or new dependency exists. Existing JSON contracts/frontend
are unchanged; use these OpenAPI DTOs rather than the legacy bulk result contract.

Before a real interactive scheme is available, complete policy/bilingual review
and connect the Phase 4A trusted provider to version-bound published execution
approvals. Frontend work can use in-process synthetic fixtures in automated tests.
Render one current question, add answer/skip/unknown/edit/clear controls and a
prominent Clear Data action; keep all logic on the backend.

For voice, use `content_language` to choose speech output. Confirm recognized
answers visibly before submitting typed values, provide a text alternative, and
keep recordings/transcripts ephemeral. Speech assistance must not generate policy
conditions or eligibility verdicts. No speech service, audio storage or voice
dependency is introduced in Phase 4B.

## Files and validation

Added questionnaire models, orchestration and routes in the three files listed
above, `tests/test_questionnaire.py`, and this guide. Updated
`app/schemas/eligibility.py` with question-language review metadata, `main.py`
with router registration, and `app/core/errors.py` with nested-state error
redaction and no-store error headers. The Phase 4A evaluation engine is unchanged.

All 17 focused questionnaire tests passed. The complete suite then ran once:
81 Python tests plus 24 isolated database/staging checks passed (105 total).
Coverage includes skip/unknown/edit/clear, nested logic, early termination,
duplicate prevention, language review/fallback, unavailable drafts, invalid types,
rule injection, policy changes, no persistence and existing endpoint compatibility.
No new dependency, .env change, migration, permission change, frontend change,
live Supabase access, commit or push was performed.
