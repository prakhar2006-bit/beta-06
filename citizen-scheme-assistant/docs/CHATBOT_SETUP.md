# YojanaMitra AI Chatbot — Setup & Run Guide

**YojanaMitra (योजना मित्र)** — AI-Assisted Government Scheme Discovery and Eligibility Platform  
Document: **CHATBOT_SETUP.md**

---

## 1. Overview
The YojanaMitra AI Assistant is an intelligent, bilingual (English & Hindi) conversational assistant integrated directly into the YojanaMitra platform. It enables citizens to:
* Discover Central and State Government schemes matching their profiles.
* Evaluate eligibility through the deterministic backend rules engine.
* Identify missing, required, and available documents with issuance guidance.
* Receive verified step-by-step application instructions and official portal links.

---

## 2. Prerequisites
* **Python**: 3.11+ (verified up to Python 3.14)
* **Node.js**: v18+ (verified with Node.js v24)
* **npm**: v9+
* **Google Gemini API Key**: (Optional for local testing; required for live Gemini LLM generation).

---

## 3. Backend Setup (`engine/`)

### 3.1 Install Dependencies
Navigate to the `citizen-scheme-assistant/engine` directory:
```bash
cd citizen-scheme-assistant/engine
pip install -r requirements.txt
```

### 3.2 Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `engine/.env` and configure:
```env
# Google Gemini AI Configuration (Backend-only; never exposed to browser)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Optional PostgreSQL Database Configuration
DATABASE_URL=postgresql://scheme_api:PASSWORD@HOST:5432/postgres
DATABASE_EXPECTED_USER=scheme_api

# CORS Allowed Origins
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
```
> **Note**: If `GEMINI_API_KEY` is not provided, the backend automatically operates in High-Quality Deterministic Mode, allowing complete functional testing, rule evaluation, and scheme discovery without crashing.

### 3.3 Run the Backend Server
From `citizen-scheme-assistant/engine`:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The API documentation is available at `http://localhost:8000/docs`.

---

## 4. Frontend Setup (`frontend/`)

### 4.1 Install Dependencies
```bash
cd citizen-scheme-assistant/frontend
npm install
```

### 4.2 Start the Frontend Development Server
```bash
npm run dev
```
The application will launch on `http://localhost:3000`.

---

## 5. Running Automated Tests

### Backend Tests
From project root:
```bash
python -m pytest citizen-scheme-assistant/engine/tests/test_chatbot.py -o pythonpath=citizen-scheme-assistant/engine -v
```

### Frontend Build Verification
```bash
npm run build --prefix citizen-scheme-assistant/frontend
```

---

## 6. How to Use the Chatbot
1. Open `http://localhost:3000` in any web browser.
2. Click the floating **YojanaMitra AI Assistant** button at the bottom-right corner.
3. Choose a suggested question pill or type inquiries such as:
   * *"Find scholarships for me"*
   * *"Am I eligible for PM-KISAN?"*
   * *"Which documents do I need for Ladli Behna?"*
   * *"मुझे मध्य प्रदेश की छात्रवृत्ति योजनाओं के बारे में बताओ।"*
4. Click on any scheme card or official portal link to proceed.

