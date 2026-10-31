# Citizen Scheme Assistant (नागरिक योजना सहायक)

> **Bilingual (Hindi/English) Citizen Scheme Eligibility & Application Assistant**  
> Hackathon Problem Statement 2: Helping citizens discover government schemes they qualify for, explaining *why* in simple language, handling uncertainty responsibly, and preparing a printable document checklist.

---

## 🎯 Problem Statement Overview
Many citizens qualify for central and state government schemes but never apply due to dense bureaucratic language, disparate portals, and fear of rejection or wasted effort. This tool provides:
1. **Bilingual Simplicity**: Full interface, audio speech-to-text, and read-aloud capabilities in both Hindi (हिंदी) and English.
2. **Minimal Question Burden**: An intelligent question ordering engine that asks only what affects the outcome.
3. **Transparent Decisioning**: Explains eligibility criteria in plain words and clearly flags uncertainties without guessing.
4. **Actionable Document Checklist**: Generates an offline-ready checklist of required documents before visiting an office or portal.
5. **Shared-Phone Privacy**: Zero persistent server-side storage of personal information.

---

## 👥 Team & Ownership

| Area | Primary Directory | Owner | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Frontend** | `frontend/` | User (Frontend Owner) | React + Vite UI, bilingual toggle, Web Speech API (STT/TTS), responsive mobile design. |
| **Eligibility Engine** | `engine/` | Owner: TBD | Decision logic, rule evaluation, question minimisation, uncertainty scoring. |
| **Data & Schemes** | `data/schemes/` | Owner: TBD | Scheme rule schemas, verification of official sources, criteria translation. |
| **Documentation & Quality** | `docs/` | Owner: TBD | PRD maintenance, test coverage, PR reviews, accessibility audits. |

---

## 📁 Repository Layout

```
citizen-scheme-assistant/
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md       # PR guidelines & sanity checks
├── .env.example                       # Reference environment variables
├── .gitignore                         # Multi-language ignore patterns
├── README.md                          # Repository overview & navigation
├── CONTEXT.md                         # 1-page summary for teammates & AI agents
├── AGENTS.md                          # Hard rules for AI coding assistants
├── CONTRIBUTING.md                    # Git conventions, PR flow, merge order
├── docs/
│   ├── PRD.md                         # Product Requirements Document & Matrix
│   ├── ARCHITECTURE.md                # Component architecture & data flow
│   ├── CONTRACTS.md                   # JSON schema specifications
│   ├── PRIVACY.md                     # Data handling & shared device policy
│   ├── DECISIONS.md                   # Architecture Decision Records (ADRs)
│   └── GLOSSARY.md                    # Hindi <-> English government terminology
├── contracts/
│   ├── scheme.schema.json             # JSON schema for scheme definition
│   ├── citizen-profile.schema.json    # JSON schema for citizen input answers
│   ├── eligibility-result.schema.json # JSON schema for engine evaluation outputs
│   └── examples/                      # Valid sample payload files
├── data/
│   └── schemes/                       # Scheme rule JSON files (one file per scheme)
├── engine/                            # Eligibility decision engine (language: TBD)
└── frontend/                          # Client web application (React + Vite, JS)
```

---

## 🚀 Quick Start & Documentation Links
- **Teammates & AI Agents**: Read [CONTEXT.md](./CONTEXT.md) first before opening any file.
- **AI Agents**: Read [AGENTS.md](./AGENTS.md) for strict operational boundaries.
- **Product Requirements**: See [docs/PRD.md](./docs/PRD.md).
- **System Architecture**: See [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).
- **Contributing Guidelines**: See [CONTRIBUTING.md](./CONTRIBUTING.md).
- **Technical Decisions**: See [docs/DECISIONS.md](./docs/DECISIONS.md).

