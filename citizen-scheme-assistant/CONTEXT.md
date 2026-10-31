# Context: Citizen Scheme Assistant (1-Page Brief)

This document is the **single source of ground truth** for any teammate or AI coding agent joining this project. Read this before writing or editing any code.

---

## 1. Mission & What We Are Building
A lightweight, bilingual (Hindi/English) web application that helps Indian citizens discover which government schemes they qualify for. The tool explains **why** they qualify in simple terms, lists the exact **documents required**, explicitly admits when it is **uncertain**, and preserves citizen privacy on **shared or borrowed mobile phones**.

Target User: A citizen or Common Service Centre (CSC) operator in semi-urban/rural India using a low-end Android device with low bandwidth, primarily comfortable in Hindi.

---

## 2. Team Architecture & Ownership Boundaries
Do not cross boundaries. Each team member owns their dedicated directory:

| Directory | Area | Owner | Stack / Format |
| :--- | :--- | :--- | :--- |
| `frontend/` | UI, i18n, Web Speech API | User (Frontend Owner) | React + Vite (JavaScript) |
| `engine/` | Eligibility & Question Tree Logic | Owner: TBD | Decision logic (Language: Open / TBD) |
| `data/schemes/` | Scheme rules (1 JSON per scheme) | Owner: TBD | JSON validating against `contracts/` |
| `contracts/` | Shared JSON schemas | All (PR Required) | JSON Schema Draft 7 |
| `docs/` | Requirements, ADRs, Glossaries | All | Markdown |

---

## 3. Critical Invariants (Non-Negotiable Rules)
1. **Zero Scheme Logic in Frontend**: `frontend/` renders UI and collects answers. It must **never** contain scheme eligibility thresholds, conditions, or hardcoded scheme rules.
2. **Rules Live Only in `data/schemes/`**: All scheme thresholds, age limits, required documents, and official URLs reside strictly in individual JSON files under `data/schemes/`.
3. **No Hardcoded UI Strings**: All user-facing text in `frontend/` must use localized string keys (`hi` and `en`).
4. **Never Guess or Invent**: Never say "Eligible" when data is missing/borderline (use `"UNCERTAIN"`). Never hallucinate government URLs, income limits, or rules.
5. **No Accounts or Persistent PII**: Serves one citizen per session; stores zero data across visits. The entry screen asks only for Language (`hi`/`en`) and Device Mode (Own phone vs Shared phone).
6. **Independent Branding & Disclaimer**: Use our own name, logo, and palette. Never use the National Emblem, official seals, or government logos. Every screen displays: *"Independent project, not an official government website."*
7. **Contracts are Sacred**: Changes to `contracts/` break cross-team integration. Any change requires unanimous team consent and an entry in `docs/DECISIONS.md`.

---

## 4. How the Flow Works
```
[Entry Screen: Language (hi/en) + Device Mode (Own vs Shared Phone)]
           │
           ▼
[Citizen Answers via Voice/Tap]
           │
           ▼
     frontend/ (React + Vite)
           │ Validates profile against contracts/citizen-profile.schema.json
           ▼
     engine/ (Decision Engine) ◄──── Reads data/schemes/*.json
           │ Evaluates rules & detects missing/borderline facts
           ▼
[Output: contracts/eligibility-result.schema.json]
           │
           ▼
     frontend/ renders:
     ├── Prominent Disclaimer: "Independent project, not an official government website"
     ├── Simple eligibility status (Eligible / Not Eligible / Uncertain)
     ├── "Why" rule explanation in Hindi/English
     ├── Printable / Downloadable Document Checklist
     └── Official source portal link + last-checked date
```

---

## 5. Current Project Status
- Phase: **Repository & Documentation Setup** (No application code is written yet).
- Next Step: Finalize contracts and initial 5 scheme JSON definitions in `data/schemes/`.

