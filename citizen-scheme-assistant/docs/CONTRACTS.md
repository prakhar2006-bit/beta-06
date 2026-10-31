# API & Data Contracts Specification

**Citizen Scheme Assistant (नागरिक योजना सहायक)**  
Document Version: 1.0.0

All data moving between the frontend, engine, and data storage layers is strictly governed by JSON Schemas defined in the `/contracts` directory.

---

## 1. Schema Inventory

| Schema File | Purpose | Consumers / Producers |
| :--- | :--- | :--- |
| `contracts/scheme.schema.json` | Defines the structure of government scheme rules, thresholds, official links, and document checklists. | **Producer**: Data Lead<br>**Consumer**: Engine |
| `contracts/citizen-profile.schema.json` | Defines the structured answers provided by the citizen (demographics, occupation, income, land). | **Producer**: Frontend<br>**Consumer**: Engine |
| `contracts/eligibility-result.schema.json` | Encapsulates the output of the eligibility evaluation for all schemes, including reasons, uncertainty flags, and required documents. | **Producer**: Engine<br>**Consumer**: Frontend |

---

## 2. Scheme Rule Contract (`contracts/scheme.schema.json`)

Each scheme file inside `data/schemes/<scheme-id>.json` must conform to this schema:
- `id` (string): Unique identifier (e.g., `pm-kisan`).
- `name` (object): Bilingual name `{ "en": "PM-KISAN", "hi": "पीएम किसान सम्मान निधि" }`.
- `description` (object): Bilingual simple summary.
- `official_source`:
  - `url`: Must be a valid `.gov.in` / `.nic.in` link.
  - `last_checked_date`: ISO 8601 date string (e.g., `2026-01-15`).
  - `gazette_or_order_ref`: Official order number or notification citation.
- `criteria`: Array of condition objects containing:
  - `field`: The attribute from the citizen profile (e.g., `annual_income_inr`, `is_farmer`).
  - `operator`: `EQUALS`, `LESS_THAN_OR_EQUAL`, `GREATER_THAN_OR_EQUAL`, `IN_LIST`, `NOT_IN_LIST`.
  - `value`: Target comparison value.
  - `criticality`: `MANDATORY` or `DISQUALIFIER`.
  - `explanation_if_met` (bilingual): Simple reason when condition passes.
  - `explanation_if_violated` (bilingual): Simple reason when condition fails.
- `required_documents`: Array of document objects with bilingual titles and issuing authorities.

---

## 3. Citizen Profile Contract (`contracts/citizen-profile.schema.json`)

Encapsulates all answers collected during the session:
- `language`: `"hi"` or `"en"`.
- `age`: integer (optional/null if unknown).
- `gender`: `"male"`, `"female"`, `"transgender"`, `"other"`, or `"unknown"`.
- `occupation`: `"farmer"`, `"street_vendor"`, `"daily_wage_laborer"`, `"salaried"`, `"unemployed"`, `"other"`.
- `annual_income_inr`: number (optional/null if unknown).
- `income_bracket`: `"bpl"`, `"antyodaya"`, `"lower_middle"`, `"unknown"`.
- `owns_agricultural_land`: boolean (or null).
- `land_size_hectares`: number (or null).
- `owns_pucca_house`: boolean (or null).
- `state_of_residence`: ISO Indian state code (e.g., `"IN-MP"`).
- `is_taxpayer`: boolean (or null).

---

## 4. Eligibility Result Contract (`contracts/eligibility-result.schema.json`)

The engine responds with a list of evaluated scheme verdicts:
- `citizen_summary`: Echoed non-sensitive metadata.
- `results`: Array of scheme evaluations:
  - `scheme_id`: string.
  - `scheme_name`: Bilingual object.
  - `status`: `"ELIGIBLE"`, `"INELIGIBLE"`, or `"UNCERTAIN"`.
  - `confidence_score`: float (0.0 to 1.0).
  - `decisive_rule`: Bilingual text explaining the specific rule that determined this verdict.
  - `uncertainty_details` (null if status is ELIGIBLE or INELIGIBLE):
    - `reason`: Bilingual explanation of why the tool is uncertain.
    - `missing_fields`: Array of field names that would resolve the uncertainty.
    - `is_stale_rule`: boolean (true if rule last checked > 180 days ago).
  - `official_source`: URL and last checked date.
  - `document_checklist`: Array of required documents with bilingual titles and notes.

---

## 5. Contract Change Governance

1. Schemas in `contracts/` are shared code assets.
2. Any modification requires an entry in `docs/DECISIONS.md` under an Architecture Decision Record (ADR).
3. Any pull request touching `contracts/` must be reviewed and approved by all module owners (Frontend, Engine, Data).

