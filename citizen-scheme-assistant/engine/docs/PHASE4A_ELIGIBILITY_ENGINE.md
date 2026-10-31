# Phase 4A deterministic eligibility engine

The engine evaluates trusted server-side rule trees without an LLM, network
access, SQL, arbitrary expressions or citizen-data storage. New endpoint:
`POST /api/v1/eligibility/evaluate`; Swagger remains at `/docs`.

No government scheme is execution-approved in this phase. The default provider
returns no rule set, so all five prepared schemes receive NEEDS_VERIFICATION.
Synthetic policies exist only in tests and dependency overrides; there is no
public demo/fixture activation switch. Existing read-only scheme routes are
unchanged. CORS now permits POST from the existing configured origins.

## Request and response contract

The additive Phase 4A DTOs live in `app/schemas/eligibility.py` and OpenAPI. The
request accepts only `scheme_id`, `answers`, and `language` (`en`/`hi`, default en).
Clients cannot submit rules, approval flags, source URLs or review metadata.
Scheme IDs follow the existing slug syntax. Answers are a bounded dictionary of
scalar Booleans, integers, finite numbers, strings or null. Extra top-level fields,
nested/list answers and more than 64 answer fields are rejected.

The existing `contracts/eligibility-result.schema.json` describes a different,
multi-scheme response with `UNCERTAIN` and mandatory scheme-name/document/source
objects. It is unchanged. This new per-scheme DTO uses the explicitly requested
`NEEDS_VERIFICATION` status. It must not be passed to a frontend expecting the
legacy bulk contract without an explicit adapter/approved contract alignment.
No placeholder official source, scheme name, document or confidence score is
invented to fill legacy fields. A future adapter should map NEEDS_VERIFICATION to
UNCERTAIN explicitly while preserving the condition/provenance details.

Example usable against the normal backend:

```http
POST /api/v1/eligibility/evaluate
Content-Type: application/json

{
  "scheme_id": "in-cen-000002",
  "answers": {"age_years_at_enrolment": 35},
  "language": "en"
}
```

Response (HTTP 200):

```json
{
  "schema_version": "1.0",
  "scheme_id": "in-cen-000002",
  "rule_set_version": null,
  "language": "en",
  "status": "NEEDS_VERIFICATION",
  "policy_review": {
    "publication_status": "unavailable",
    "approval_status": "unavailable",
    "execution_enabled": false,
    "complete": false,
    "applicable": false,
    "reviewed_on": null,
    "blockers": ["RULE_SET_UNAVAILABLE"]
  },
  "evaluated_conditions": [],
  "satisfied_rules": [],
  "failed_rules": [],
  "unknown_conditions": [],
  "missing_answers": [],
  "questions_needed": [],
  "sources": [],
  "explanation": "Eligibility cannot be confirmed. Missing answers or policy review may still be required."
}
```

No questions or citations are fabricated for unavailable schemes. Unknown scheme
IDs and unavailable draft schemes receive the same conservative response. When
an approved rule set is supplied by a trusted provider, typed answer errors return
HTTP 422 with `INVALID_ANSWERS`; structural request errors use existing
`INVALID_REQUEST`. Invalid provider identity returns sanitized HTTP 503. Responses
include no submitted answer values, and successful evaluation responses use
`Cache-Control: no-store`. The application does not log request bodies or retain
answers between requests. Error fields also suppress answer-dictionary keys.

## Rule schema

RuleSet is an immutable server-side model, separate from citizen requests:

| Field | Meaning |
| --- | --- |
| scheme_id / version | Stable scheme identity and exact reviewed rule-set version |
| publication_status | draft, reviewed or published; only published may execute |
| approval_status / execution_enabled | Explicit human approval and activation; default unreviewed/false |
| complete | Reviewer assertion that all necessary policy conditions/exclusions are represented; default false |
| root_failure_is_decisive | Explicit approval that failure of this partial root is sufficient for rejection; default false |
| reviewer_reference / reviewed_on | Approval provenance; missing or future review blocks decisions |
| applicability_confirmed / effective_from / effective_to | Explicit policy scope and inclusive effective interval; missing start or applicability confirmation blocks decisions |
| review_valid_until | Optional reviewer-specified expiry; the engine does not invent a universal expiry interval |
| unresolved_conditions / conflicts | Remaining manual requirements versus contradictory/applicability evidence; conflicts block all definitive outcomes |
| fields | Typed answer descriptors, questions and reviewed category codes |
| nodes / sources | Bounded rule tree and exact supplied evidence references |

Each node has `rule_id`, `parent_id`, `node_type`, a bilingual `label`,
`enabled`, `confidence`, `applicability_confirmed`, optional effective interval
and `source_ids`. Predicates additionally have `attribute`, `operator` and
`expected_value`. Groups cannot contain predicate expressions. Source references
preserve ID, original URL, title, locator, checked date and optional capture hash.
Missing, unknown or future-dated evidence cannot authorize a predicate.

The tree requires one root, unique rule IDs, valid parents, no cycles, no detached
roots, no more than 128 nodes and bounded depth (16 parent edges). AND/OR groups
require at least one child; NOT requires exactly one; predicates have no children.
Identifiers are dictionary keys, never object paths or Python expressions.

Synthetic predicate example (not a government condition):

```json
{
  "rule_id": "age_min",
  "parent_id": "root",
  "node_type": "predicate",
  "label": {"en": "Synthetic minimum age is 18.", "hi": "परीक्षण में न्यूनतम आयु 18 वर्ष है।"},
  "attribute": "age",
  "operator": "gte",
  "expected_value": 18,
  "enabled": true,
  "confidence": "VERIFIED",
  "applicability_confirmed": true,
  "source_ids": ["fixture-source"]
}
```

The enclosing synthetic RuleSet still needs its own approval, completeness,
effective-date, field-definition and source metadata; a predicate alone cannot
establish eligibility. Test citations use `example.invalid` and are explicitly
synthetic, never represented as official scheme evidence.

## Supported conditions and operators

| Condition | Representation |
| --- | --- |
| Minimum/maximum age | age field with gte/gt/lte/lt; nonnegative integer at reviewed reference date |
| Income threshold | income field with numeric comparison; explicit currency/unit, period and individual/household scope |
| State residency | category code with eq/in; the policy must define what residency means |
| Gender / occupation | category field only when explicitly required by the approved policy |
| Defined category membership | in/not_in against an explicit reviewed nonempty set |
| Boolean condition | eq/ne with a strict Boolean |
| Exclusion | NOT over an approved predicate or group, included in the necessary root |
| Combined conditions | Nested AND / OR / NOT groups |

Operators are exactly `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`.
Only numeric fields allow ordering. Operators are dispatched through a fixed
allowlist. `exists`, arbitrary expressions, SQL fragments, fuzzy matching,
automatic category aliases and automatic income conversions are not supported.
An adapter must explicitly reject unsupported database operators, not reinterpret
missing data as a failed presence test.

Income accepts finite JSON numbers or plain decimal strings (recommended for
exact amounts), at most six fractional digits and absolute magnitude 10^18;
income is nonnegative. Decimal comparisons perform no rounding. Boolean values
cannot serve as ages/income, strings cannot serve as ages/Booleans, and scientific
notation strings are rejected. Categories match exact reviewed codes. The limits
are implementation bounds, not government eligibility thresholds. No birth date,
income amount, address or other citizen attribute is persisted.

## Evaluation semantics

Every node returns SATISFIED, FAILED or UNKNOWN. Absent answers and explicit null
are equivalent UNKNOWN; a missing answer never becomes false. Invalid typed values
are rejected rather than guessed. Disabled, unverified, unapproved, uncited or
inapplicable predicates are UNKNOWN regardless of the submitted answer.

- AND: any FAILED child proves FAILED; otherwise any UNKNOWN gives UNKNOWN;
  otherwise SATISFIED.
- OR: any SATISFIED child proves SATISFIED; otherwise any UNKNOWN gives UNKNOWN;
  otherwise FAILED.
- NOT: reverses SATISFIED/FAILED and preserves UNKNOWN. This supports exclusions
  without turning missing information into rejection.

All nodes are visited; response lists are sorted by rule ID for deterministic
explanations. Simple impossible mandatory AND bounds/sets (including direct NOT
predicates) trigger policy review. OR alternatives are not flattened together.
This consistency guard complements human policy review, not a general-purpose
SAT solver or a complete amendment/conflict detector.

| Outcome | Required evidence |
| --- | --- |
| ELIGIBLE | Published, explicitly approved/enabled/applicable policy; complete rule set; no unresolved policy conditions/conflicts or unready nodes; root SATISFIED |
| INELIGIBLE | Same overall approval/applicability gates; root FAILED from verified applicable conditions; complete policy or explicit root_failure_is_decisive approval |
| NEEDS_VERIFICATION | Every other case: missing decisive answers, incomplete/unapproved rules, unknown applicability, conflicts, unavailable policy or unresolved manual scope |

An incomplete rule set can therefore prove rejection only when a reviewer has
explicitly established its necessary/decisive scope. It can never prove eligibility.
A failed leaf in an OR is not an automatic rejection. A known true OR alternative
may resolve the group despite missing answers in another **approved** alternative;
an unverified alternative still blocks a positive decision. Conflicting/unpublished
policies never produce definitive outcomes.

`satisfied_rules` and `failed_rules` describe individual node expressions, not
independent overall decisions: an exclusion predicate may match while its NOT
group fails. `evaluated_conditions` includes labels, reason codes, result,
explanation, language/fallback and source IDs. `unknown_conditions` reports all
unknown nodes. `missing_answers` reports all missing evaluated input fields;
`questions_needed` includes only missing answers on still-unknown decision paths.
No unnecessary questions are asked after a definitive result. Incomplete policy
may need human review even when there are no remaining citizen questions.

Hindi system explanations are available. Reviewed labels/questions use Hindi when
present, otherwise preserve English with explicit `content_language` and
`translation_fallback`. The engine does not generate scheme translations.

## Synthetic example through tests

`tests/test_eligibility.py` defines an isolated synthetic policy covering all
supported condition types. Its thresholds are invented test values, not imported
government rules. Tests override `get_rule_provider` in-process only.

```json
{
  "scheme_id": "synthetic-only",
  "language": "en",
  "answers": {
    "age": 30,
    "monthly_income": "999.99",
    "state": "state_a",
    "gender": "female",
    "occupation": "worker",
    "category": "group_a",
    "has_existing_benefit": false
  }
}
```

With the test override this produces ELIGIBLE; changing age to 17 produces
INELIGIBLE; omitting age produces NEEDS_VERIFICATION with `missing_answers=["age"]`
and a reviewed age question. The normal server returns RULE_SET_UNAVAILABLE for
this synthetic ID, just as for other unavailable policies. See the tests for
complete condition-level responses and source-preservation assertions.

## Connecting reviewed government policies later

Implement a trusted RuleProvider adapter using the existing published-only,
read-only SchemeRepository. Never read drafts through a privileged connection.
Publication alone is insufficient: bind the exact version and content/evidence
hashes to a separately approved execution manifest with completeness, necessary
root scope, reviewer identity/date, effective dates, applicability, unresolved
conflicts and explicit per-node activation. The current database has neither an
enabled column nor all this approval metadata; do not infer it from VERIFIED or
published status. No adapter auto-approves the Phase 3D partial roots.

Map rule UUIDs/parents, evidence IDs, checked dates and original URLs without
inventing references. Preserve uncertainty, require evidence for every predicate,
define reviewed typed answer descriptors and reject unsupported operators. Keep
the existing rule/evidence vocabulary adapter explicit, especially income scope,
age reference date, household definitions and residency/category codes. Use a
repeatable read snapshot and verify that execution approval still matches that
exact published version. Missing/mismatched approval must remain unavailable.

Policy reviewers must first resolve the blockers in PHASE3D_REVIEW_MATRIX.md.
No migration, role change, live writer or database write is needed by the pure
engine. An eventual evaluation remains advisory; it does not enrol a citizen,
determine an insurer's claim, calculate a payment, or replace provider verification.

## Adaptive-question integration

The endpoint already returns stable attribute keys, affected rule IDs, reviewed
prompts, choices, units/period/scope/reference basis and explicit language fallback.
Next, add a session-ephemeral questionnaire layer that selects among those pending
questions, preserves explicit unknown/refused answers, and re-evaluates after each
answer. Keep policy-review blockers separate from questions a citizen can answer.
Do not ask for extra personal information when the policy itself is unavailable.

Review ordering by question burden and logical relevance; test AND/OR paths,
exclusions, skipped answers and boundary values. Do not use an LLM to decide
eligibility or create new thresholds. Any language assistance must preserve the
reviewed question meaning. Contract alignment with the frontend is a separate
reviewed integration step. Engine system messages and drafted Hindi test labels
can be improved linguistically without changing government criteria.

## Validation

Focused tests run first:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_eligibility.py -v
```

Then run the existing Python/database/staging suites once. All tests use synthetic
fixtures or isolated PGlite; the database smoke command is not invoked. Coverage
includes eligible/ineligible/unknown, all supported operators/types, boundary
ages/income, nested groups and truth tables, verified exclusions, conflicting and
incomplete rules, review/effective-date gates, draft isolation, input sanitization,
language fallback, provenance and existing API compatibility.

Implemented validation results: all 22 focused eligibility tests passed. The full
suite was then run once: 64 Python tests, eight catalogue database tests, nine
single-scheme staging tests, six batch staging tests and one isolated payload test
passed (88 total). No live database smoke test, connection or write was performed.
No new dependency was added.

Files added: `app/schemas/eligibility.py`, `app/eligibility/__init__.py`,
`app/eligibility/engine.py`, `app/eligibility/provider.py`,
`app/api/routes/eligibility.py`, `tests/test_eligibility.py` and this report.
`main.py` registers the router and permits POST through existing CORS settings;
`app/core/errors.py` suppresses untrusted answer/extra-field keys in validation
errors. Existing database models, repositories, migrations, credentials,
permissions, frontend and JSON contracts were not changed.
