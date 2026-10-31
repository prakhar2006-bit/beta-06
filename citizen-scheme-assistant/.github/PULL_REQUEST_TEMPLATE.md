## Pull Request Description

### Summary of Changes
<!-- Provide a brief summary of what this PR introduces or fixes. -->

### Domain / Scope
- [ ] `frontend/` (React + Vite UI, i18n, Web Speech API)
- [ ] `engine/` (Decision tree, eligibility evaluation logic)
- [ ] `data/schemes/` (Government scheme JSON definitions)
- [ ] `contracts/` (JSON schemas)
- [ ] `docs/` (PRD, Architecture, Decisions, Glossary)

---

## Pre-Merge Quality & Governance Checklist

- [ ] **Boundary Adherence**: I have only edited files within my assigned folder ownership.
- [ ] **No Hardcoded Strings**: All new UI strings in `frontend/` are added to both `en` and `hi` localization files.
- [ ] **Bilingual Glossary Compliance**: Official terms adhere to `docs/GLOSSARY.md`.
- [ ] **Contract Change Governance**:
  - [ ] This PR does NOT touch `contracts/`, OR
  - [ ] This PR updates `contracts/` AND includes a corresponding approved ADR in `docs/DECISIONS.md`.
- [ ] **Rule & Threshold Grounding**: No government scheme rules or URLs were invented. All sources point to verified government domains (`.gov.in` / `.nic.in`).
- [ ] **Privacy Check**: No personal data (income, caste, contact details) is logged to remote telemetry or persisted across browser restarts.
- [ ] **Schema Validation**: Any sample or new scheme JSON passes schema validation against `contracts/`.

---

## Testing & Demonstration
<!-- Describe the manual or automated tests performed to verify this change. -->
- How was this tested:
- Target resolution / browser tested (e.g., Mobile Android Chrome 360x640):

