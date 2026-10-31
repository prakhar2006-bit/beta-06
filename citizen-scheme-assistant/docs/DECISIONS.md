# Architecture Decision Records (ADRs)

**Citizen Scheme Assistant (नागरिक योजना सहायक)**  
Document Version: 1.0.0

---

## ADR-001: Frontend Framework Selection (React + Vite, JavaScript)

- **Date**: 2026-10-30
- **Status**: **ACCEPTED**
- **Decision**: The frontend application is built using **React** bundled with **Vite** in standard **JavaScript**.
- **Context**: The target user is using low-end mobile devices on unpredictable mobile bandwidth. The interface requires rapid re-renders for bilingual switches, interactive Web Speech API triggers, and zero build complexity.
- **Consequences**:
  - Extremely fast hot-module replacement and lightweight production bundles.
  - Straightforward integration with modern Web Speech APIs without heavy framework overhead.
  - All team members can inspect and review frontend components easily.

---

## ADR-002: Backend / Engine Technology Selection

- **Date**: 2026-10-30
- **Status**: **OPEN (TBD)**
- **Decision**: The programming language and runtime execution environment for the evaluation engine (`engine/`) is currently open and to be decided by the Engine Lead.
- **Context**: The engine could be implemented as a client-side JavaScript module directly bundled into the PWA (enabling 100% offline functionality), or as a lightweight serverless/REST service (e.g., Python FastAPI or Node.js Express).
- **Consequences**:
  - The team communicates strictly across the boundaries defined in `contracts/`.
  - The engine implementation language does not constrain the frontend development, as long as input and output payloads strictly satisfy `contracts/citizen-profile.schema.json` and `contracts/eligibility-result.schema.json`.

---

## ADR-003: Declarative Rule Architecture in `data/schemes/`

- **Date**: 2026-10-30
- **Status**: **ACCEPTED**
- **Decision**: Government scheme criteria, eligibility thresholds, required documents, and official source links must be stored exclusively in declarative JSON files inside `data/schemes/`.
- **Context**: Government welfare schemes update their rules periodically (budgetary changes, revised income cutoffs). If logic is hardcoded inside application code or UI components, updating a single scheme requires code refactoring, testing, and redeployment.
- **Consequences**:
  - Adding or updating a scheme does not touch frontend or engine code.
  - The Data Lead can update schemes independently.
  - Schemas are strictly validated against `contracts/scheme.schema.json` in CI.

---

## ADR-004: Ephemeral Zero-Persistence Architecture for Shared Devices

- **Date**: 2026-10-30
- **Status**: **ACCEPTED**
- **Decision**: The application will not store any citizen financial, demographic, or eligibility data in persistent storage (`localStorage`, server database, persistent cookies). State is strictly held in memory during the active session.
- **Context**: In target communities, smartphones and computers are frequently shared among family members, local agents, or kiosk visitors. Leaving personal data behind exposes vulnerable citizens to privacy breaches.
- **Consequences**:
  - Zero risk of personal data leakage to subsequent users of the phone.
  - The citizen must complete their evaluation in a single session.
  - Explicit "Clear Data" and auto-wipe handlers are enforced.

---

## ADR-005: Contract Revision and Governance Protocol

- **Date**: 2026-10-30
- **Status**: **ACCEPTED**
- **Decision**: Any change to schemas in `contracts/` requires an explicit Architecture Decision Record entry in this document (`docs/DECISIONS.md`) and sign-off from all module owners.
- **Context**: Because four teammates work simultaneously on frontend, engine, and data, unannounced schema modifications cause breaking changes and wasted hackathon time.
- **Consequences**:
  - Eliminates silent schema drift.
  - Guarantees that mock data and production payloads stay aligned.

---

## ADR-006: No User Accounts or Login (Single-Citizen Ephemeral Sessions)

- **Date**: 2026-10-30
- **Status**: **ACCEPTED**
- **Decision**: The application will have **no user accounts, passwords, phone OTPs, signups, or login mechanisms**. The product serves exactly one citizen per session, operates entirely in-memory, and stores nothing across visits. The entry screen prompts the user for two selections only:
  1. Preferred Language (Hindi or English).
  2. Device Ownership Mode ("My own phone" vs "Someone else's / Shared phone").
- **Reasons**:
  - **Privacy Guarantee**: Citizens routinely refuse to sign up or fear entering phone numbers due to spam, surveillance, or fraud concerns.
  - **Shared-Phone & Kiosk Reality**: Citizens frequently use a shopkeeper's, neighbor's, relative's, or CSC kiosk phone. Eliminating accounts guarantees no login session, password, or profile is left behind for the next user.
  - **Simplicity & Zero Barrier**: Enables an immediate 30-second start with zero friction.
- **Consequences**:
  - No database or backend authentication infrastructure required.
  - "Shared phone" mode activates heightened privacy protections (accelerated idle auto-wipe, immediate purge on tab blur).
  - All data vanishes when the session terminates or when "Clear Data" is clicked.

---

## ADR-007: Independent Civic Branding & Anti-Impersonation Disclaimers

- **Date**: 2026-10-30
- **Status**: **ACCEPTED**
- **Decision**: The application adopts standard, accessible civic-portal design conventions (clean cards, accessible high contrast, clear typography) but maintains **independent branding** using its own name ("Citizen Scheme Assistant / नागरिक योजना सहायक"), bespoke logo, and neutral civic color palette. We **never** use the National Emblem of India (State Emblem / Ashoka Lion Capital), state government seals, ministry crests, or visual assets of existing government portals (like myScheme or India.gov.in). Every screen must visibly include the disclaimer:
  > *"Independent project, not an official government website."* / *"स्वतंत्र परियोजना, आधिकारिक सरकारी वेबसाइट नहीं।"*
- **Reasons**:
  - **Citizen Protection & Trust**: Prevents citizens from mistaking an advisory hackathon tool for an official government portal where formal applications are registered.
  - **Legal & Ethical Compliance**: Strict adherence to the State Emblem of India (Prohibition of Improper Use) Act and ethical civic-tech design standards.
- **Consequences**:
  - All UI headers/footers must prominently display the disclaimer banner.
  - Scheme results must clearly separate our independent evaluation from the clickable official government source link (`.gov.in`).


