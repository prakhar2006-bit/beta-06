# YojanaMitra AI Chatbot — API Specification

**YojanaMitra (योजना मित्र)**  
Document: **CHATBOT_API.md**  
Version: 1.0.0

---

## 1. Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/chatbot/message` | Send message and receive AI response with structured scheme cards. |
| `GET` | `/api/v1/chatbot/conversations/{conversation_id}` | Retrieve conversation history turns. |
| `DELETE` | `/api/v1/chatbot/conversations/{conversation_id}` | Wipe and delete an active conversation session. |
| `GET` | `/api/v1/chatbot/suggested-questions` | Get starter/quick-prompt questions for the UI. |
| `GET` | `/api/v1/chatbot/status` | Get operational status and active AI model. |

---

## 2. Detailed Endpoint Specs

### 2.1 Send Message
**Endpoint:** `POST /api/v1/chatbot/message`  
**Headers:**
* `Content-Type: application/json`
* `X-Session-ID: <optional-session-uuid>`

**Request Body (`ChatMessageRequest`):**
```json
{
  "conversation_id": null,
  "message": "Find scholarships for me",
  "language": "en",
  "session_id": "sess_demo123",
  "profile": {
    "state": "MP",
    "area_type": "rural",
    "age": 20,
    "gender": "male",
    "occupation": "student",
    "annual_income": 200000,
    "caste_category": "obc",
    "education_level": "b.tech"
  }
}
```

**Response Body (`ChatMessageResponse`):**
```json
{
  "conversation_id": "673f8e56-2db1-4e44-8d4a-39c895d98fa2",
  "message": "I found 1 relevant government welfare schemes tailored to your inquiry. Please check the details and official application links below.",
  "language": "en",
  "intent": "scheme_discovery",
  "schemes": [
    {
      "scheme_id": "post-matric-scholarship",
      "code": "post-matric-scholarship",
      "name": "Post Matric Scholarships Scheme for Students (SC/ST/OBC)",
      "category": "education",
      "level": "central",
      "benefits_summary": "Full tuition fee reimbursement + monthly maintenance allowance up to ₹13,500 per year.",
      "official_url": "https://scholarships.gov.in",
      "match_reason": "Tailored for Student livelihood needs."
    }
  ],
  "eligibility": null,
  "missing_documents": [],
  "application_guidance": null,
  "suggested_followups": [
    "Am I eligible for Post Matric Scholarships?",
    "Which documents do I need?",
    "How do I apply for this?"
  ],
  "created_at": "2026-10-31T13:30:00Z"
}
```

---

### 2.2 Eligibility Evaluation Response (When intent is `eligibility_check`)
```json
{
  "conversation_id": "673f8e56-2db1-4e44-8d4a-39c895d98fa2",
  "message": "Based on your profile information, you appear to satisfy the primary eligibility criteria for PM-KISAN.",
  "language": "en",
  "intent": "eligibility_check",
  "schemes": [],
  "eligibility": {
    "scheme_id": "pm-kisan",
    "scheme_name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
    "status": "POTENTIALLY_ELIGIBLE",
    "confidence_score": 0.9,
    "summary_explanation": "Based on your profile responses, you appear eligible for PM-KISAN under standard guidelines.",
    "criteria_breakdown": [
      {
        "criterion_name": "Cultivable Land Ownership",
        "satisfied": true,
        "explanation": "You reported owning agricultural land."
      },
      {
        "criterion_name": "Non-Taxpaying Household",
        "satisfied": true,
        "explanation": "No household member filed income tax."
      }
    ]
  },
  "missing_documents": [],
  "application_guidance": null,
  "suggested_followups": [
    "Which documents are required?",
    "How can I apply?",
    "Explore more schemes for me"
  ]
}
```

---

### 2.3 Suggested Questions
**Endpoint:** `GET /api/v1/chatbot/suggested-questions?lang=hi`  
**Response:**
```json
{
  "language": "hi",
  "questions": [
    "मेरे लिए छात्रवृत्ति योजनाएं खोजें",
    "मेरी पात्रता की जांच करें",
    "इसके लिए कौन-से दस्तावेज़ चाहिए?",
    "छात्रों के लिए सरकारी योजनाएं दिखाएं",
    "मध्य प्रदेश की सरकारी योजनाएं दिखाएं"
  ]
}
```

---

### 2.4 Chatbot Status
**Endpoint:** `GET /api/v1/chatbot/status`  
**Response:**
```json
{
  "status": "online",
  "service": "YojanaMitra AI Assistant",
  "gemini_configured": true,
  "model": "gemini-2.5-flash",
  "languages_supported": ["en", "hi"],
  "features": [
    "scheme_discovery",
    "eligibility_engine",
    "missing_document_assistance",
    "application_guidance"
  ]
}
```

