# YojanaMitra AI Chatbot — Architecture Document

**YojanaMitra (योजना मित्र)**  
Document: **CHATBOT_ARCHITECTURE.md**  
Version: 1.0.0

---

## 1. Architectural Philosophy

### Core Tenet: Deterministic Eligibility & AI Explanation
* **Crucial Rule**: The Large Language Model (Google Gemini) is **strictly prohibited from independently deciding citizen eligibility**.
* All eligibility evaluations are computed deterministically by verified backend rules.
* Gemini's role is focused on:
  1. Natural language understanding across Hindi, English, and Hinglish.
  2. Synthesizing concise, empathetic explanations of deterministic outcomes.
  3. Guiding citizens through required official documentation and application routes.

```
       [ Citizen User Interface ]
                 │ (Prompt + Ephemeral Profile)
                 ▼
     [ FastAPI Backend Gateway ]
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
[ Intent Classifier ]  [ Profile Context ]
      │                     │
      ├─────────────────────┼─────────────────────┐
      ▼                     ▼                     ▼
[ Scheme Retrieval ] [ Eligibility Rules ] [ Document Analyzer ]
 (Database/Catalog)   (Deterministic Engine) (Aadhaar, Income, etc.)
      │                     │                     │
      └──────────┬──────────┴─────────────────────┘
                 │ (Verified Facts & Evaluation)
                 ▼
       [ Google Gemini AI ]
   (SDK: google-genai, Model: gemini-2.5-flash)
                 │ (Bilingual Dignified Explanation)
                 ▼
    [ Structured Response Payload ]
   (Message + Scheme Cards + Criteria + Actions)
                 │
                 ▼
      [ Floating Chatbot UI ]
```

---

## 2. Privacy & Security Invariants

1. **Zero Persistence of Personal Identifiers**:
   - The chatbot never accepts, stores, or logs real citizen names, Aadhaar numbers, PAN cards, or phone numbers.
   - Profile context relies strictly on anonymized attributes (e.g. State: MP, Occupation: Student, Annual Income: ₹2,00,000).
2. **Backend-Only Gemini Credentials**:
   - `GEMINI_API_KEY` is loaded strictly by FastAPI in `engine/app/core/config.py`.
   - Never exposed to Vite frontend, client bundles, or network headers.
3. **Controlled Tool Calling**:
   - The LLM cannot execute arbitrary SQL queries or shell commands.
   - All tool invocations map to validated backend Python functions.
4. **CORS & Rate Protection**:
   - Allowed origins strictly restricted to localhost:3000 and verified production frontend domains.

---

## 3. Database Schema

Tables created in `scheme_catalog` schema (`20261031000100_chatbot.sql`):
* `scheme_catalog.chat_conversations`: Holds conversation UUIDs, session links, and timestamps.
* `scheme_catalog.chat_messages`: Holds turn-by-turn user and assistant messages with structured JSON payloads.
* Indexes on `(conversation_id, created_at)` ensure $O(\log n)$ retrieval performance.

---

## 4. Multi-Language (i18n) Engine

* The system supports automatic script detection:
  * If the citizen types in Devanagari script (e.g. *"छात्रवृत्ति"*), responses are automatically produced in Hindi.
  * If the citizen types in Latin script (e.g. *"scholarships"*), responses are produced in English.
  * Natural Hinglish queries (e.g. *"b.tech ke liye koi scholarship hai?"*) are natively understood and addressed clearly.

