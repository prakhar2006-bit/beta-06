# Product Requirements Document (PRD)

**Project**: Citizen Scheme Assistant (नागरिक योजना सहायक)  
**Hackathon Problem Statement**: 2 — Multilingual Citizen Scheme Eligibility & Application Assistant  
**Status**: Ready for Implementation  
**Version**: 1.0.0  

---

## 1. Problem Overview
Hundreds of millions of citizens across India qualify for central and state welfare initiatives (pensions, healthcare coverage, farming income support, vendor credit, housing subsidies). However, uptake remains low because:
1. Eligibility rules are buried in dense official government jargon.
2. Central and state rules often differ or overlap in complex ways.
3. Information is fragmented across dozens of departmental websites.
4. Language barriers: Many citizens are comfortable only in spoken or written Hindi and feel intimidated by complex bureaucratic forms.
5. High penalty for errors: Telling someone they qualify when they do not causes wasted travel, loss of daily wages, and disappointment. Telling someone they do not qualify when they do robs them of essential welfare.

---

## 2. Target User & Environment Constraints

### Primary Persona: Suresh (The Citizen)
- **Profile**: 42-year-old smallholder farmer or street vendor based in a tier-2/3 district.
- **Language**: Comfortably speaks and understands conversational Hindi. Struggles with English and formal Sanskritized/bureaucratic Hindi terminology.
- **Device**: Low-end Android smartphone (1.5GB–3GB RAM, small 5.5" screen, running Android Chrome).
- **Network**: Unstable 3G/4G connectivity with intermittent dropouts.
- **Context of Use**: Often using a shared or borrowed smartphone (e.g., from a son, neighbor, or local shopkeeper/CSC kiosk). Needs confidence that their personal financial details will not remain on the phone.

### Secondary Persona: Priya (Common Service Centre / Kiosk Operator)
- Assists 30–50 walk-in citizens per day.
- Needs rapid screening with minimum questions to recommend schemes and print a concrete document checklist immediately.

---

## 3. Product Goals & Non-Goals

### Core Goals
- Deliver a 100% bilingual (Hindi and English) experience with instant language toggling at any step.
- Offer voice-first interactions: voice input (STT) for answers and voice readout (TTS) for questions and results in both languages.
- Minimize question fatigue: Dynamically sequence questions so citizens answer only what alters the eligibility outcome.
- Provide crystal-clear explanations: Explain why a citizen qualified (or did not qualify) based on specific rules.
- Maintain absolute intellectual honesty: State clearly when information is insufficient or borderline; **never hallucinate an "Eligible" verdict**.
- Provide official source provenance: Display exact `.gov.in` source links and dates last verified.
- Deliver an actionable document checklist ready for offline saving or printing.
- Zero-leakage privacy: Guarantee that no personal inputs linger on a shared or borrowed device.
- Modular maintainability: Adding or updating a scheme must require only editing a single JSON file without altering application code.

### Non-Goals
- We do **not** support user accounts, passwords, login, phone numbers, or registration. The tool serves one citizen per session and stores nothing across visits.
- We do **not** use official-look branding or government impersonation. We never use the National Emblem of India, state/central seals, ministry logos, or existing portal branding (e.g., myScheme, India.gov.in). Every screen displays: *"Independent project, not an official government website."*
- We are **not** an official application filing portal; we do not submit forms to government ministries.
- We do **not** verify identity credentials (no biometric Aadhaar e-KYC or OTP banking integration).
- We do **not** scrape live government portals in real-time during user queries (all rules are pre-structured and versioned to ensure determinism and zero downtime).

---

## 4. Requirements Matrix (R1 – R11)

| Req ID | Requirement Description | Acceptance Criteria | Priority | Owner |
| :--- | :--- | :--- | :--- | :--- |
| **R1** | **Bilingual Interface (Hindi / English)** | • Complete parity between Hindi and English for all screens, questions, results, document checklists, and error states.<br>• A sticky, one-tap language switcher available on every screen that persists the current view state without resetting answers. | P0 | Frontend (User) |
| **R2** | **Voice Input & Read-Aloud Support** | • Citizens can speak answers in Hindi or English using Web Speech Recognition (STT).<br>• Every question, decision explanation, and document list can be read aloud using SpeechSynthesis (TTS) in the selected language.<br>• Clear visual indicators for microphone listening and speaking status. | P0 | Frontend (User) |
| **R3** | **Minimal Question Decision Engine** | • The engine evaluates a directed decision tree to ask only questions that eliminate or qualify schemes.<br>• Irrelevant questions (e.g., asking land size to a non-farmer) are skipped.<br>• Minimum 5 central/state schemes supported at launch (e.g., PM-KISAN, Ayushman Bharat PM-JAY, PM-SVANidhi, PMAY-G, NSAP Old Age Pension). | P0 | Engine (Owner: TBD) |
| **R4** | **Transparent Rule Explanations** | • Every scheme evaluated returns a clear status: `ELIGIBLE`, `INELIGIBLE`, or `UNCERTAIN`.<br>• The user sees a simple, jargon-free explanation highlighting which exact rule qualified or disqualified them (e.g., *"You qualify because your annual household income is under ₹2.5 Lakh and you do not own a pucca house"*). | P0 | Engine + Data (Owner: TBD) |
| **R5** | **Explicit Uncertainty & Boundary Handling** | • If a citizen answers "Don't know" or has borderline income/age, the tool outputs `UNCERTAIN`.<br>• It explicitly lists what single fact would clarify the result.<br>• If a scheme's verified rule data is outdated (> 180 days), an explicit staleness alert is displayed.<br>• **Zero Guessing Invariant**: Never output `ELIGIBLE` based on missing or assumed data. | P0 | Engine (Owner: TBD) |
| **R6** | **Official Source Provenance & Staleness Tracking** | • Every scheme result card displays the official `.gov.in` portal URL.<br>• Displays the exact `last_checked_date` and official gazette/portal reference.<br>• Visual warning banner if a scheme rule has not been audited recently. | P0 | Data (Owner: TBD) |
| **R7** | **Printable / Downloadable Document Checklist** | • For every scheme a citizen may qualify for, generate an exact list of documents (Aadhaar, Bank Passbook, Land Records, Ration Card, etc.).<br>• One-click browser print view and text/PDF download formatted cleanly for mobile and CSC desktop printing. | P1 | Frontend (User) |
| **R8** | **Zero-Code Scheme Extensibility** | • Adding or modifying a scheme requires creating/editing only one JSON file in `data/schemes/`.<br>• Requires no changes to `frontend/` or `engine/` logic.<br>• Strict automated schema validation via `contracts/scheme.schema.json`. | P0 | Data + Engine (Owner: TBD) |
| **R9** | **Shared-Phone Privacy & Ephemeral Data** | • No personal data (income, age, caste, land) stored in permanent databases, remote servers, or persistent cookies.<br>• Prominent "Clear My Data / नया नागरिक" button on all screens.<br>• Automatic session wipe on inactivity timeout (5 minutes) or browser tab close. | P0 | Frontend + Docs (User & Owner: TBD) |
| **R10** | **Graceful Offline / Low-Bandwidth Handling** | • Frontend bundle loads reliably under slow 3G network conditions.<br>• Scheme assets and rule evaluations happen client-side or with minimal payload round-trips. | P1 | Frontend (User) |
| **R11** | **Entry Onboarding (Language & Device Mode)** | • Entry screen prompts for two fundamental choices before asking any personal questions:<br>&nbsp;&nbsp;1. Language: Hindi (हिंदी) or English.<br>&nbsp;&nbsp;2. Device Mode: "My own phone" (मेरा अपना फ़ोन) vs "Someone else's / Shared phone" (किसी और का / साझा फ़ोन).<br>• "Shared phone" mode activates strict defenses: shorter idle auto-wipe (2 mins), immediate purge on tab blur/hidden state, and disabled form history.<br>• Every screen displays the mandatory independent disclaimer: *"Independent project, not an official government website."* | P0 | Frontend (User) |

---

## 5. Screen Inventory

1. **Screen 1: Welcome & Onboarding (`/`)**
   - Independent branding with mandatory disclaimer: *"Independent project, not an official government website / स्वतंत्र परियोजना, आधिकारिक सरकारी वेबसाइट नहीं।"*
   - Immediate audio greeting in Hindi: *"नमस्ते! जानिए आपके लिए सरकारी योजनाएं।"*
   - Language switch buttons: **हिंदी** / **English**.
   - Device Ownership Selector: **"मेरा अपना फ़ोन (My own phone)"** vs **"किसी और का / साझा फ़ोन (Shared phone)"**.
   - Reassurance banner: *"कोई खाता या पासवर्ड नहीं। आपका डेटा इस फ़ोन पर कभी सेव नहीं होगा।"*

2. **Screen 2: Guided Question Flow (`/check`)**
   - Single-question-at-a-time focus for low-cognitive burden.
   - Large buttons for choices (हाँ / नहीं / पता नहीं).
   - Voice mic button for speech input.
   - Read-question-aloud speaker icon.
   - Live progress indicator showing remaining critical questions.

3. **Screen 3: Scheme Discovery Dashboard (`/results`)**
   - Segmented summary:
     - **Qualified Schemes (आप इन योजनाओं के पात्र हो सकते हैं)**
     - **Need More Info / Borderline (इनके लिए अधिक जानकारी चाहिए)**
     - **Not Qualified (वर्तमान में अपात्र)**
   - Plain-language explanation pill on each card.
   - Source badge with link and verification date.
   - Read results aloud button.

4. **Screen 4: Scheme Detail & Document Checklist (`/scheme/:id`)**
   - Step-by-step breakdown of qualifications met.
   - Required document checklist with checkboxes.
   - Official portal link and physical CSC guidance.
   - "Print / Save Checklist" action button.

5. **Screen 5: Session Termination / Privacy Shield (`/clear`)**
   - Visual confirmation that all responses have been purged from memory.
   - Option to start afresh for the next citizen.

---

## 6. Extra-Points Exploration (Decisions TBD)

The problem statement proposes 5 specific edge scenarios. Our designated responses and approaches are outlined below for team decision:

| Situation | Proposed Strategic Approach | Status |
| :--- | :--- | :--- |
| **1. Unknown Household Income** | Rather than forcing a guess or declining outright, ask deterministic physical proxies: Ration card color/category (Antyodaya/BPL/APL), land area owned, or vehicle ownership. If still unknown, output `UNCERTAIN` and explain the exact cutoff threshold. | Strategy: Proposed (Decision TBD) |
| **2. Contradictory Answers / Unverifiable Criteria** | Display an explicit advisory banner: *"यह योजना स्थानीय सत्यापन पर निर्भर करती है"* (e.g., Gram Sabha resolution). Highlight the exact conflict and provide CSC/Tehsil referral instructions. | Strategy: Proposed (Decision TBD) |
| **3. Shared/Borrowed Device Protection** | Implement a floating "Exit & Wipe (डेटा मिटाएं)" button, disable form autocomplete/caching headers, clear volatile state on browser tab blur, and offer zero persistent analytics. | Strategy: Proposed (Decision TBD) |
| **4. Post-Qualification Dropout Prevention** | Provide clear "Next Steps" (अगला कदम): Where to walk in (nearest CSC/Gram Panchayat), what physical forms to ask for, and what fee (if any) is officially mandated. | Strategy: Proposed (Decision TBD) |
| **5. Adding Another Language** | Recommend adding **Bengali** or **Marathi** based on high rural smartphone density. Validate translations using official state gazettes and NIC portal lexicons rather than raw automated translation. | Strategy: Proposed (Decision TBD) |

---

## 7. Success Measures

1. **Question Minimization**: Citizen answers fewer than 8 questions on average to screen across 5+ schemes.
2. **Zero False Positives from Incomplete Data**: 0% rate of `ELIGIBLE` status when required criteria are flagged unknown or borderline.
3. **Bilingual Completeness**: 100% of text and audio speech prompts verified in both Hindi and English.
4. **Zero Data Residue**: 0 residual local storage keys or form autofill values after session wipe.
5. **Time to Screen**: Citizen completes eligibility check in under 3 minutes on mobile.

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Speech API browser incompatibility** | High on old Android webviews | Gracefully fall back to prominent one-tap high-contrast buttons if Web Speech API is unavailable. |
| **Government rule changes during hackathon** | Medium | Schemes maintain a `last_checked_date` field in JSON. Rules are decoupled from frontend code. |
| **Dialect & accent variations in Hindi** | Medium | Offer simple numeric/tap options alongside voice input. Handle standard Hindi synonyms in speech parsing. |
| **Team merge collisions** | High | Rigid folder separation enforced by `AGENTS.md` and schema contracts. |

