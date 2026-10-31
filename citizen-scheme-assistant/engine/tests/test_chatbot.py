"""Comprehensive Automated Tests for YojanaMitra AI Chatbot.
Covers all Part 10 Test Specifications:
- TEST GROUP A — GREETINGS (hi, hello, hey, good morning, namaste, नमस्ते, etc.)
- TEST GROUP B — GENERAL QUESTIONS (What is YojanaMitra?, What can you do?, etc.)
- TEST GROUP C — SCHEME DISCOVERY (Scholarships, Farmers, Women, Housing, MP, Central)
- TEST GROUP D — SCHEME INFORMATION (What is PM-KISAN?, specific scheme details)
- TEST GROUP E — ELIGIBILITY (Deterministic backend evaluation)
- TEST GROUP F — DOCUMENTS (Required documents, missing documents, certificate guidance)
- TEST GROUP G — CONVERSATION CONTEXT (Multi-turn ordinal references, switching topics)
- TEST GROUP H — NEGATIVE TESTS (No scheme on greeting, unrelated deflection, validation)
- TEST GROUP I — LANGUAGE TESTS (English, Hindi, Hinglish)
- TEST GROUP J — REGRESSION (Status, questions, error handling)
"""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# --------------------------------------------------------------------------
# REGRESSION & STATUS ENDPOINTS
# --------------------------------------------------------------------------
def test_suggested_questions():
    """Verify suggested starter questions in English and Hindi."""
    res_en = client.get("/api/v1/chatbot/suggested-questions?lang=en")
    assert res_en.status_code == 200
    data_en = res_en.json()
    assert data_en["language"] == "en"
    assert len(data_en["questions"]) >= 5
    assert "Find scholarships for me" in data_en["questions"]

    res_hi = client.get("/api/v1/chatbot/suggested-questions?lang=hi")
    assert res_hi.status_code == 200
    data_hi = res_hi.json()
    assert data_hi["language"] == "hi"
    assert len(data_hi["questions"]) >= 5


def test_chatbot_status():
    """Verify live status endpoint metadata."""
    res = client.get("/api/v1/chatbot/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["service"] in ("Sahayak AI Assistant", "Shayak AI Assistant")
    assert "scheme_discovery" in data["features"]
    assert "eligibility_engine" in data["features"]


# --------------------------------------------------------------------------
# TEST GROUP A — GREETINGS (Must NEVER display scheme cards)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("msg,expected_lang", [
    ("hi", "en"),
    ("hello", "en"),
    ("hey", "en"),
    ("good morning", "en"),
    ("namaste", "en"),
    ("नमस्ते", "hi"),
    ("आप कैसे हैं?", "hi"),
    ("how are you?", "en"),
])
def test_group_a_greetings(msg: str, expected_lang: str):
    """Verify that every greeting returns a short natural response with ZERO scheme cards."""
    res = client.post("/api/v1/chatbot/message", json={"message": msg, "language": expected_lang})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "greeting"
    assert ("Sahayak" in data["message"] or "Shayak" in data["message"] or "सहायक" in data["message"])
    # Critical requirement: Never display scheme cards on greeting
    assert data["schemes"] == []
    assert data["eligibility"] is None
    assert data["missing_documents"] == []
    assert len(data["suggested_followups"]) > 0


# --------------------------------------------------------------------------
# TEST GROUP B — GENERAL QUESTIONS (No scheme cards)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("question", [
    "What is Shayak?",
    "What is YojanaMitra?",
    "What can you do?",
    "Can you speak Hindi?",
    "How can you help students?",
    "Are you an AI assistant?",
])
def test_group_b_general_questions(question: str):
    """Verify direct concise answers without unrequested scheme recommendations."""
    res = client.post("/api/v1/chatbot/message", json={"message": question, "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] in ("general_conversation", "clarification")
    assert len(data["message"]) > 20
    # Must not dump scheme cards for general conversation
    assert data["schemes"] == []
    assert data["eligibility"] is None


# --------------------------------------------------------------------------
# TEST GROUP C — SCHEME DISCOVERY
# --------------------------------------------------------------------------
def test_group_c_scholarship_discovery():
    """Verify asking for scholarships returns ONLY education schemes and NEVER PM-KISAN."""
    res = client.post("/api/v1/chatbot/message", json={"message": "Find scholarships for me.", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "scheme_discovery"
    assert len(data["schemes"]) > 0
    # All returned schemes must be education schemes
    for s in data["schemes"]:
        assert s["category"] == "education"
        assert "kisan" not in s["scheme_id"]


def test_group_c_farmer_discovery():
    """Verify farmer query returns agriculture schemes (PM-KISAN)."""
    res = client.post("/api/v1/chatbot/message", json={"message": "Show schemes for farmers.", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "scheme_discovery"
    assert len(data["schemes"]) > 0
    categories = [s["category"] for s in data["schemes"]]
    assert "agriculture" in categories
    pm_kisan = next((s for s in data["schemes"] if s["scheme_id"] == "pm-kisan"), None)
    assert pm_kisan is not None


def test_group_c_women_discovery():
    """Verify query for women schemes returns women-child schemes."""
    res = client.post("/api/v1/chatbot/message", json={"message": "Show schemes for women.", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "scheme_discovery"
    assert len(data["schemes"]) > 0
    for s in data["schemes"]:
        assert s["category"] == "women-child"


def test_group_c_housing_discovery():
    """Verify query for housing schemes returns housing category (PMAY-G)."""
    res = client.post("/api/v1/chatbot/message", json={"message": "Show housing schemes.", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "scheme_discovery"
    assert len(data["schemes"]) > 0
    assert any(s["category"] == "housing" for s in data["schemes"])


def test_group_c_mp_discovery():
    """Verify schemes in Madhya Pradesh returns MP schemes like Ladli Behna."""
    res = client.post("/api/v1/chatbot/message", json={"message": "Show government schemes in Madhya Pradesh.", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "scheme_discovery"
    assert len(data["schemes"]) > 0
    assert any(s["scheme_id"] == "ladli-behna-mp" for s in data["schemes"])


def test_group_c_hindi_discovery():
    """Verify Hindi discovery queries."""
    res1 = client.post("/api/v1/chatbot/message", json={"message": "मुझे छात्रों के लिए छात्रवृत्ति बताओ।", "language": "hi"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["intent"] == "scheme_discovery"
    assert all(s["category"] == "education" for s in data1["schemes"])

    res2 = client.post("/api/v1/chatbot/message", json={"message": "किसानों के लिए योजनाएं बताओ।", "language": "hi"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["intent"] == "scheme_discovery"
    assert any(s["scheme_id"] == "pm-kisan" for s in data2["schemes"])


# --------------------------------------------------------------------------
# TEST GROUP D — SCHEME INFORMATION
# --------------------------------------------------------------------------
def test_group_d_scheme_information_pm_kisan():
    """Verify asking about a specific scheme returns ONLY that scheme's details."""
    res = client.post("/api/v1/chatbot/message", json={"message": "What is PM-KISAN?", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "scheme_information"
    assert len(data["schemes"]) == 1
    assert data["schemes"][0]["scheme_id"] == "pm-kisan"
    assert data["schemes"][0]["official_url"] == "https://pmkisan.gov.in"


def test_group_d_scheme_information_benefits():
    """Verify asking for benefits of a specific scheme."""
    res = client.post("/api/v1/chatbot/message", json={"message": "What benefits does this scheme provide for Post Matric Scholarship?", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] in ("scheme_information", "scheme_discovery")
    assert len(data["schemes"]) >= 1
    assert data["schemes"][0]["scheme_id"] == "post-matric-scholarship"


# --------------------------------------------------------------------------
# TEST GROUP E — DETERMINISTIC ELIGIBILITY
# --------------------------------------------------------------------------
def test_group_e_eligibility_pm_kisan_eligible():
    """Eligible farmer with land."""
    res = client.post("/api/v1/chatbot/message", json={
        "message": "Am I eligible for PM-KISAN?",
        "language": "en",
        "profile": {
            "occupation": "farmer",
            "owns_agricultural_land": True,
            "pays_income_tax": False,
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "eligibility_check"
    assert data["eligibility"] is not None
    assert data["eligibility"]["status"] == "POTENTIALLY_ELIGIBLE"
    assert data["eligibility"]["scheme_id"] == "pm-kisan"


def test_group_e_eligibility_pm_kisan_ineligible():
    """Ineligible non-farmer without land."""
    res = client.post("/api/v1/chatbot/message", json={
        "message": "Am I eligible for PM-KISAN?",
        "language": "en",
        "profile": {
            "occupation": "salaried",
            "owns_agricultural_land": False,
            "pays_income_tax": True,
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "eligibility_check"
    assert data["eligibility"]["status"] == "NOT_ELIGIBLE"


def test_group_e_eligibility_hindi():
    """Eligibility query in Hindi."""
    res = client.post("/api/v1/chatbot/message", json={
        "message": "क्या मैं इस योजना के लिए पात्र हूं?",
        "language": "hi",
        "profile": {"occupation": "student", "annual_income": 150000}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "eligibility_check"


# --------------------------------------------------------------------------
# TEST GROUP F — DOCUMENTS
# --------------------------------------------------------------------------
def test_group_f_missing_documents():
    """Verify identifying required and missing documents."""
    res = client.post("/api/v1/chatbot/message", json={
        "message": "Which documents are required for Post Matric Scholarship?",
        "language": "en",
        "profile": {"occupation": "student", "annual_income": 150000}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] in ("document_assistance", "missing_documents")
    assert len(data["missing_documents"]) > 0


def test_group_f_income_certificate_guidance():
    """Verify clear guidance when citizen lacks an income certificate."""
    res = client.post("/api/v1/chatbot/message", json={
        "message": "I don't have an income certificate. How can I obtain an income certificate?",
        "language": "en"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] in ("document_assistance", "missing_documents")
    assert "Tehsil" in data["message"] or "e-District" in data["message"]


def test_group_f_caste_certificate_hindi():
    """Verify Hindi caste certificate guidance."""
    res = client.post("/api/v1/chatbot/message", json={
        "message": "मेरे पास जाति प्रमाण पत्र नहीं है।",
        "language": "hi"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] in ("document_assistance", "missing_documents")
    assert "तहसीलदार" in data["message"] or "एसडीएम" in data["message"] or "ई-डिस्ट्रिक्ट" in data["message"]


# --------------------------------------------------------------------------
# TEST GROUP G — CONVERSATION CONTEXT & FOLLOW-UPS
# --------------------------------------------------------------------------
def test_group_g_multi_turn_first_scheme_reference():
    """Scenario 1: Find scholarships -> ask about documents for the first one."""
    # Turn 1: Find scholarships
    res1 = client.post("/api/v1/chatbot/message", json={
        "message": "Find scholarships for me.",
        "language": "en"
    })
    assert res1.status_code == 200
    conv_id = res1.json()["conversation_id"]
    assert len(res1.json()["schemes"]) > 0
    first_scheme_id = res1.json()["schemes"][0]["scheme_id"]

    # Turn 2: What are the documents required for the first one?
    res2 = client.post("/api/v1/chatbot/message", json={
        "conversation_id": conv_id,
        "message": "What are the documents required for the first one?",
        "language": "en"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["conversation_id"] == conv_id
    assert len(data2["missing_documents"]) > 0


def test_group_g_switching_topics():
    """Scenario 3: Show schemes for farmers -> Now show me scholarships."""
    # Turn 1: Farmers
    res1 = client.post("/api/v1/chatbot/message", json={"message": "Show me schemes for farmers.", "language": "en"})
    conv_id = res1.json()["conversation_id"]
    assert any(s["category"] == "agriculture" for s in res1.json()["schemes"])

    # Turn 2: Switch to scholarships
    res2 = client.post("/api/v1/chatbot/message", json={
        "conversation_id": conv_id,
        "message": "Now show me scholarships.",
        "language": "en"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    # Must perform a fresh scholarship search and not continue showing farmer schemes
    assert len(data2["schemes"]) > 0
    for s in data2["schemes"]:
        assert s["category"] == "education"
        assert "pm-kisan" not in s["scheme_id"]


# --------------------------------------------------------------------------
# TEST GROUP H — NEGATIVE TESTS
# --------------------------------------------------------------------------
def test_group_h_random_greeting_never_returns_scheme():
    """Verify random greeting 'hi' never returns scheme cards."""
    res = client.post("/api/v1/chatbot/message", json={"message": "hi", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["schemes"] == []
    assert data["eligibility"] is None


def test_group_h_unrelated_question_deflection():
    """Verify unrelated questions (cricket, movie, recipes) return exact out-of-scope response with NO schemes."""
    res = client.post("/api/v1/chatbot/message", json={"message": "Who won the cricket match yesterday?", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] in ("out_of_scope", "unrelated")
    assert data["schemes"] == []
    assert data["eligibility"] is None
    assert "I could not find a verified government scheme matching your query in the database" in data["message"]


def test_group_h_unknown_scheme_name():
    """Verify non-existent scheme name does not fabricate information."""
    res = client.post("/api/v1/chatbot/message", json={"message": "Tell me about XYZ Scholarship Scheme.", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["schemes"] == []
    assert "I couldn't find a verified record for this scheme in our database" in data["message"]


def test_group_h_empty_message_validation():
    """Verify empty message payload is rejected with HTTP 422."""
    res = client.post("/api/v1/chatbot/message", json={"message": "", "language": "en"})
    assert res.status_code == 422


# --------------------------------------------------------------------------
# TEST GROUP I — MULTILINGUAL CONSISTENCY
# --------------------------------------------------------------------------
def test_group_i_multilingual_intent_consistency():
    """Verify English, Hindi, and Hinglish all resolve scholarship intent consistently."""
    res_en = client.post("/api/v1/chatbot/message", json={"message": "Find scholarships for me.", "language": "en"})
    assert res_en.json()["intent"] == "scheme_discovery"
    assert any(s["category"] == "education" for s in res_en.json()["schemes"])

    res_hi = client.post("/api/v1/chatbot/message", json={"message": "मेरे लिए छात्रवृत्ति ढूंढो।", "language": "hi"})
    assert res_hi.json()["intent"] == "scheme_discovery"
    assert any(s["category"] == "education" for s in res_hi.json()["schemes"])

    res_hinglish = client.post("/api/v1/chatbot/message", json={"message": "Mere liye scholarship find karo", "language": "en"})
    assert res_hinglish.json()["intent"] == "scheme_discovery"
    assert any(s["category"] == "education" for s in res_hinglish.json()["schemes"])


# --------------------------------------------------------------------------
# TEST GROUP K — PERSONAL INFORMATION (Conversation Memory)
# --------------------------------------------------------------------------
def test_group_k_personal_name_english():
    """User says 'My name is Prakhar' — must acknowledge name, NO scheme search."""
    res = client.post("/api/v1/chatbot/message", json={"message": "My name is Prakhar", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "personal_information"
    assert "Prakhar" in data["message"]
    assert data["schemes"] == []
    assert data["eligibility"] is None


def test_group_k_personal_name_hindi():
    """User says 'मेरा नाम प्रखर है' — must acknowledge in Hindi."""
    res = client.post("/api/v1/chatbot/message", json={"message": "मेरा नाम प्रखर है", "language": "hi"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "personal_information"
    assert "प्रखर" in data["message"]
    assert data["schemes"] == []


def test_group_k_personal_location():
    """User says 'I live in Bhopal' — must acknowledge location."""
    res = client.post("/api/v1/chatbot/message", json={"message": "I live in Bhopal", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "personal_information"
    assert "Bhopal" in data["message"]
    assert data["schemes"] == []


# --------------------------------------------------------------------------
# TEST GROUP L — PERSONAL QUESTION (Fact Recall from Memory)
# --------------------------------------------------------------------------
def test_group_l_recall_name():
    """Multi-turn: share name -> ask 'what is my name?' -> must recall from memory."""
    # Turn 1: Share name
    res1 = client.post("/api/v1/chatbot/message", json={"message": "My name is Prakhar", "language": "en"})
    conv_id = res1.json()["conversation_id"]
    assert res1.json()["intent"] == "personal_information"

    # Turn 2: Ask name
    res2 = client.post("/api/v1/chatbot/message", json={
        "conversation_id": conv_id,
        "message": "What is my name?",
        "language": "en"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["intent"] == "personal_question"
    assert "Prakhar" in data2["message"]
    assert data2["schemes"] == []


def test_group_l_recall_location():
    """Multi-turn: share location -> ask where I live -> must recall."""
    res1 = client.post("/api/v1/chatbot/message", json={"message": "I live in Bhopal", "language": "en"})
    conv_id = res1.json()["conversation_id"]

    res2 = client.post("/api/v1/chatbot/message", json={
        "conversation_id": conv_id,
        "message": "Where do I live?",
        "language": "en"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["intent"] == "personal_question"
    assert "Bhopal" in data2["message"]
    assert data2["schemes"] == []


def test_group_l_unknown_fact():
    """Ask personal question without sharing first — must politely inform, NOT scheme search."""
    res = client.post("/api/v1/chatbot/message", json={"message": "What is my name?", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "personal_question"
    assert data["schemes"] == []
    assert "scheme" not in data["message"].lower()


def test_group_l_conversation_isolation():
    """Different conversation IDs must NOT share facts."""
    # Conv A: share name Alice
    res_a = client.post("/api/v1/chatbot/message", json={"message": "My name is Alice", "language": "en"})
    conv_a = res_a.json()["conversation_id"]

    # Conv B (new empty conversation): ask name -> must not know Alice
    res_b = client.post("/api/v1/chatbot/message", json={"message": "What is my name?", "language": "en"})
    data_b = res_b.json()
    assert "Alice" not in data_b["message"]


# --------------------------------------------------------------------------
# TEST GROUP M — FULL CONVERSATION FLOW (End-to-End Master Acceptance)
# --------------------------------------------------------------------------
def test_group_m_full_conversation_flow():
    """Verify entire requested conversational journey:
    1. 'hi' -> natural greeting, no schemes
    2. 'My name is Prakhar' -> acknowledge name, no scheme search
    3. 'What is my name?' -> recalls name from conversation memory
    4. 'I live in Bhopal' -> acknowledge location
    5. 'Where do I live?' -> recalls location
    6. 'Find scholarships for me' -> scheme discovery succeeds seamlessly
    """
    # 1. Greeting
    r1 = client.post("/api/v1/chatbot/message", json={"message": "hi", "language": "en"})
    assert r1.status_code == 200
    conv = r1.json()["conversation_id"]
    assert r1.json()["intent"] == "greeting"
    assert r1.json()["schemes"] == []

    # 2. Name
    r2 = client.post("/api/v1/chatbot/message", json={
        "conversation_id": conv, "message": "My name is Prakhar", "language": "en"
    })
    assert r2.status_code == 200
    assert r2.json()["intent"] == "personal_information"
    assert "Prakhar" in r2.json()["message"]
    assert r2.json()["schemes"] == []

    # 3. Ask Name
    r3 = client.post("/api/v1/chatbot/message", json={
        "conversation_id": conv, "message": "What is my name?", "language": "en"
    })
    assert r3.status_code == 200
    assert r3.json()["intent"] == "personal_question"
    assert "Prakhar" in r3.json()["message"]
    assert r3.json()["schemes"] == []

    # 4. Location
    r4 = client.post("/api/v1/chatbot/message", json={
        "conversation_id": conv, "message": "I live in Bhopal", "language": "en"
    })
    assert r4.status_code == 200
    assert r4.json()["intent"] == "personal_information"
    assert "Bhopal" in r4.json()["message"]
    assert r4.json()["schemes"] == []

    # 5. Ask Location
    r5 = client.post("/api/v1/chatbot/message", json={
        "conversation_id": conv, "message": "Where do I live?", "language": "en"
    })
    assert r5.status_code == 200
    assert r5.json()["intent"] == "personal_question"
    assert "Bhopal" in r5.json()["message"]
    assert r5.json()["schemes"] == []

    # 6. Scholarship Search
    r6 = client.post("/api/v1/chatbot/message", json={
        "conversation_id": conv, "message": "Find scholarships for me.", "language": "en"
    })
    assert r6.status_code == 200
    assert r6.json()["intent"] == "scheme_discovery"
    assert len(r6.json()["schemes"]) > 0
    assert all(s["category"] == "education" for s in r6.json()["schemes"])


# --------------------------------------------------------------------------
# TEST GROUP N — CITIZEN OVERVIEW
# --------------------------------------------------------------------------
def test_group_n_citizen_overview():
    """Asking 'What schemes are available for ordinary citizens?' must provide categorized overview without scheme cards."""
    res = client.post("/api/v1/chatbot/message", json={"message": "What government schemes are available for ordinary citizens?", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "citizen_overview"
    assert data["schemes"] == []
    assert "ayushman" in data["message"].lower()
    assert "housing" in data["message"].lower()


# --------------------------------------------------------------------------
# TEST GROUP O — UNEMPLOYED & PMKVY SKILL PROGRAMS
# --------------------------------------------------------------------------
def test_group_o_unemployed_pmkvy():
    """Unemployed citizen query must discover PMKVY 4.0."""
    res = client.post("/api/v1/chatbot/message", json={"message": "I am unemployed. Are there any government schemes for me?", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "scheme_discovery"
    assert any(s["scheme_id"] in ("pmkvy", "pmegp") for s in data["schemes"])


# --------------------------------------------------------------------------
# TEST GROUP P — LANDLESS FARMER ELIGIBILITY EXCLUSION
# --------------------------------------------------------------------------
def test_group_p_landless_kisan():
    """Querying 'What if I do not own agricultural land?' must explain mandatory land ownership."""
    res = client.post("/api/v1/chatbot/message", json={
        "message": "What if I do not own agricultural land?",
        "language": "en",
        "profile": {"occupation": "farmer"}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "eligibility_check"
    assert "mandatory" in data["message"].lower() or "not eligible" in data["message"].lower() or "ownership" in data["message"].lower()


# --------------------------------------------------------------------------
# TEST GROUP Q — HINGLISH QUERIES
# --------------------------------------------------------------------------
def test_group_q_hinglish_queries():
    """Verify Hinglish queries resolve accurate intents."""
    # 1. Scheme info
    r1 = client.post("/api/v1/chatbot/message", json={"message": "Mujhe PM-KISAN ke baare mein batao.", "language": "en"})
    assert r1.status_code == 200
    assert r1.json()["intent"] == "scheme_information"
    assert r1.json()["schemes"][0]["scheme_id"] == "pm-kisan"

    # 2. Eligibility
    r2 = client.post("/api/v1/chatbot/message", json={"message": "Meri patrata kaise jaanchi jaayegi?", "language": "en"})
    assert r2.status_code == 200
    assert r2.json()["intent"] == "eligibility_check"

    # 3. Hindi explanation
    r3 = client.post("/api/v1/chatbot/message", json={"message": "Mujhe simple Hindi mein samjhao.", "language": "en"})
    assert r3.status_code == 200
    assert r3.json()["intent"] == "hindi_explanation"
    assert r3.json()["language"] == "hi"


# --------------------------------------------------------------------------
# TEST GROUP R — MYTH DEBUNKING / FAKE SCHEMES
# --------------------------------------------------------------------------
def test_group_r_fake_scheme_debunking():
    """Fake viral scheme probes must be explicitly rejected with fraud cautions."""
    res1 = client.post("/api/v1/chatbot/message", json={"message": "How do I apply for the Pradhan Mantri Free Android Smartphone & Tablet Yojana 2026?", "language": "en"})
    assert res1.status_code == 200
    assert res1.json()["intent"] == "myth_debunking"
    assert res1.json()["schemes"] == []
    assert "caution" in res1.json()["message"].lower() or "no officially" in res1.json()["message"].lower()

    res2 = client.post("/api/v1/chatbot/message", json={"message": "Can you give me the link to apply for the Universal Citizen Basic Income Scheme for MP?", "language": "en"})
    assert res2.status_code == 200
    assert res2.json()["intent"] == "myth_debunking"
    assert res2.json()["schemes"] == []


# ==========================================================================
# MASTER BATTERY TESTS (Section 8 Verification)
# ==========================================================================

EXACT_OUT_OF_SCOPE_EN = (
    "I could not find a verified government scheme matching your query in the database. "
    "Please verify the scheme name or explore our available categories (e.g., scholarships, agriculture, housing, healthcare)."
)

EXACT_OUT_OF_SCOPE_HI = (
    "मुझे आपके प्रश्न से संबंधित कोई सत्यापित सरकारी योजना हमारे डेटाबेस में नहीं मिली। "
    "कृपया योजना का नाम जांचें या उपलब्ध श्रेणियों (जैसे छात्रवृत्ति, कृषि, आवास और स्वास्थ्य सेवा) में से चुनें।"
)


# --------------------------------------------------------------------------
# BATTERY A — UNRELATED QUESTIONS (Strictly return EXACT fallback response)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("question", [
    "Who is the PM of India?",
    "Who is the President of India?",
    "What is the capital of France?",
    "Explain artificial intelligence.",
    "Write a poem.",
    "Tell me a joke.",
    "Solve 25 × 45.",
    "Who won the cricket match?",
    "What is Java?",
    "What is the weather today?",
])
def test_battery_a_unrelated_questions(question: str):
    """Every unrelated English query returns the exact specified fallback response with ZERO schemes."""
    res = client.post("/api/v1/chatbot/message", json={"message": question, "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] in ("out_of_scope", "unrelated")
    assert data["message"] == EXACT_OUT_OF_SCOPE_EN
    assert data["schemes"] == []
    assert data["eligibility"] is None
    assert data["missing_documents"] == []


# --------------------------------------------------------------------------
# BATTERY B — VALID SCHEME QUESTIONS
# --------------------------------------------------------------------------
def test_battery_b_valid_scheme_questions():
    """Verify all valid scheme questions return relevant verified scheme information."""
    # 1. Tell me about PM-KISAN
    r1 = client.post("/api/v1/chatbot/message", json={"message": "Tell me about PM-KISAN.", "language": "en"})
    assert r1.status_code == 200
    assert r1.json()["intent"] in ("scheme_information", "scheme_details")
    assert r1.json()["schemes"][0]["scheme_id"] == "pm-kisan"

    # 2. Find scholarships for students
    r2 = client.post("/api/v1/chatbot/message", json={"message": "Find scholarships for students.", "language": "en"})
    assert r2.status_code == 200
    assert r2.json()["intent"] == "scheme_discovery"
    assert any(s["category"] == "education" for s in r2.json()["schemes"])

    # 3. Show schemes for farmers
    r3 = client.post("/api/v1/chatbot/message", json={"message": "Show schemes for farmers.", "language": "en"})
    assert r3.status_code == 200
    assert r3.json()["intent"] == "scheme_discovery"
    assert any(s["category"] == "agriculture" for s in r3.json()["schemes"])

    # 4. What are the housing schemes?
    r4 = client.post("/api/v1/chatbot/message", json={"message": "What are the housing schemes?", "language": "en"})
    assert r4.status_code == 200
    assert r4.json()["intent"] == "scheme_discovery"
    assert any(s["category"] == "housing" for s in r4.json()["schemes"])

    # 5. Which healthcare schemes are available?
    r5 = client.post("/api/v1/chatbot/message", json={"message": "Which healthcare schemes are available?", "language": "en"})
    assert r5.status_code == 200
    assert r5.json()["intent"] == "scheme_discovery"
    assert any(s["category"] in ("health", "healthcare") for s in r5.json()["schemes"])

    # 6. Find women welfare schemes
    r6 = client.post("/api/v1/chatbot/message", json={"message": "Find women welfare schemes.", "language": "en"})
    assert r6.status_code == 200
    assert r6.json()["intent"] == "scheme_discovery"
    assert any(s["category"] == "women-child" for s in r6.json()["schemes"])


# --------------------------------------------------------------------------
# BATTERY C — SCHEME-RELATED FOLLOW-UPS
# --------------------------------------------------------------------------
def test_battery_c_scheme_related_followups():
    """Verify correct conversation context and relevant backend tools across sequential turns:
    1. Tell me about PM-KISAN.
    2. What are its benefits?
    3. Am I eligible?
    4. Which documents are required?
    5. How do I apply?
    """
    # Turn 1: Tell me about PM-KISAN.
    t1 = client.post("/api/v1/chatbot/message", json={"message": "Tell me about PM-KISAN.", "language": "en"})
    assert t1.status_code == 200
    conv_id = t1.json()["conversation_id"]
    assert t1.json()["schemes"][0]["scheme_id"] == "pm-kisan"

    # Turn 2: What are its benefits?
    t2 = client.post("/api/v1/chatbot/message", json={"conversation_id": conv_id, "message": "What are its benefits?", "language": "en"})
    assert t2.status_code == 200
    assert "6,000" in t2.json()["message"] or "income" in t2.json()["message"].lower() or "benefit" in t2.json()["message"].lower()

    # Turn 3: Am I eligible?
    t3 = client.post("/api/v1/chatbot/message", json={
        "conversation_id": conv_id,
        "message": "Am I eligible?",
        "language": "en",
        "profile": {"occupation": "farmer", "owns_agricultural_land": True, "pays_income_tax": False}
    })
    assert t3.status_code == 200
    assert t3.json()["intent"] == "eligibility_check"
    assert t3.json()["eligibility"] is not None
    assert t3.json()["eligibility"]["scheme_id"] == "pm-kisan"

    # Turn 4: Which documents are required?
    t4 = client.post("/api/v1/chatbot/message", json={"conversation_id": conv_id, "message": "Which documents are required?", "language": "en"})
    assert t4.status_code == 200
    assert t4.json()["intent"] in ("document_assistance", "missing_documents")
    assert len(t4.json()["missing_documents"]) > 0

    # Turn 5: How do I apply?
    t5 = client.post("/api/v1/chatbot/message", json={"conversation_id": conv_id, "message": "How do I apply?", "language": "en"})
    assert t5.status_code == 200
    assert t5.json()["intent"] == "application_guidance"
    assert t5.json()["application_guidance"] is not None
    assert t5.json()["application_guidance"]["scheme_id"] == "pm-kisan"


# --------------------------------------------------------------------------
# BATTERY D — PERSONAL CONVERSATION & MEMORY
# --------------------------------------------------------------------------
def test_battery_d_personal_conversation():
    """Verify conversation memory:
    1. My name is Prakhar. -> Nice to meet you, Prakhar!
    2. What is my name? -> Your name is Prakhar.
    3. I live in Bhopal. -> Got it, you live in Bhopal. I'll remember that!
    4. Where do I live? -> You live in Bhopal.
    """
    # 1. My name is Prakhar.
    r1 = client.post("/api/v1/chatbot/message", json={"message": "My name is Prakhar.", "language": "en"})
    assert r1.status_code == 200
    conv_id = r1.json()["conversation_id"]
    assert r1.json()["intent"] == "personal_information"
    assert r1.json()["message"] == "Nice to meet you, Prakhar!"
    assert r1.json()["schemes"] == []

    # 2. What is my name?
    r2 = client.post("/api/v1/chatbot/message", json={"conversation_id": conv_id, "message": "What is my name?", "language": "en"})
    assert r2.status_code == 200
    assert r2.json()["intent"] == "personal_question"
    assert r2.json()["message"] == "Your name is Prakhar."
    assert r2.json()["schemes"] == []

    # 3. I live in Bhopal.
    r3 = client.post("/api/v1/chatbot/message", json={"conversation_id": conv_id, "message": "I live in Bhopal.", "language": "en"})
    assert r3.status_code == 200
    assert r3.json()["intent"] == "personal_information"
    assert r3.json()["message"] == "Got it, you live in Bhopal. I'll remember that!"
    assert r3.json()["schemes"] == []

    # 4. Where do I live?
    r4 = client.post("/api/v1/chatbot/message", json={"conversation_id": conv_id, "message": "Where do I live?", "language": "en"})
    assert r4.status_code == 200
    assert r4.json()["intent"] == "personal_question"
    assert r4.json()["message"] == "You live in Bhopal."
    assert r4.json()["schemes"] == []


# --------------------------------------------------------------------------
# BATTERY E — HINDI AND HINGLISH
# --------------------------------------------------------------------------
def test_battery_e_hindi_and_hinglish():
    """Verify out-of-scope Hindi receives Hindi fallback and Hinglish schemes receive assistance."""
    # 1. भारत का प्रधानमंत्री कौन है? -> Hindi out_of_scope
    r1 = client.post("/api/v1/chatbot/message", json={"message": "भारत का प्रधानमंत्री कौन है?", "language": "hi"})
    assert r1.status_code == 200
    assert r1.json()["intent"] in ("out_of_scope", "unrelated")
    assert r1.json()["message"] == EXACT_OUT_OF_SCOPE_HI
    assert r1.json()["schemes"] == []

    # 2. Mujhe joke sunao. -> out_of_scope
    r2 = client.post("/api/v1/chatbot/message", json={"message": "Mujhe joke sunao.", "language": "en"})
    assert r2.status_code == 200
    assert r2.json()["intent"] in ("out_of_scope", "unrelated")
    assert r2.json()["message"] == EXACT_OUT_OF_SCOPE_EN
    assert r2.json()["schemes"] == []

    # 3. Main student hu, scholarship schemes batao. -> scheme_discovery
    r3 = client.post("/api/v1/chatbot/message", json={"message": "Main student hu, scholarship schemes batao.", "language": "en"})
    assert r3.status_code == 200
    assert r3.json()["intent"] == "scheme_discovery"
    assert any(s["category"] == "education" for s in r3.json()["schemes"])

    # 4. PM-KISAN ke benefits kya hain? -> scheme_information
    r4 = client.post("/api/v1/chatbot/message", json={"message": "PM-KISAN ke benefits kya hain?", "language": "en"})
    assert r4.status_code == 200
    assert r4.json()["intent"] in ("scheme_information", "scheme_details", "scheme_follow_up")
    assert r4.json()["schemes"][0]["scheme_id"] == "pm-kisan"

    # 5. Mujhe eligibility check karni hai. -> eligibility_check
    r5 = client.post("/api/v1/chatbot/message", json={"message": "Mujhe eligibility check karni hai.", "language": "en"})
    assert r5.status_code == 200
    assert r5.json()["intent"] == "eligibility_check"


# --------------------------------------------------------------------------
# CASE B — UNKNOWN SCHEME VS UNRELATED QUESTION
# --------------------------------------------------------------------------
def test_case_b_unknown_scheme_vs_unrelated():
    """Verify Case B: Government scheme question, but scheme not found."""
    res = client.post("/api/v1/chatbot/message", json={"message": "Tell me about XYZ Scholarship Scheme.", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] in ("scheme_information", "scheme_details")
    assert data["schemes"] == []
    assert data["message"] == "I couldn't find a verified record for this scheme in our database. Please check the scheme name or explore related scholarship schemes."


# --------------------------------------------------------------------------
# VOICE ASSISTANT & ELEVENLABS TTS TESTS
# --------------------------------------------------------------------------
def test_voice_status_endpoint():
    """Verify voice status endpoint returns configured metadata."""
    res = client.get("/api/v1/chatbot/voice/status")
    assert res.status_code == 200
    data = res.json()
    assert "configured" in data
    assert data["voice_id"] == "21m00Tcm4TlvDq8ikWAM"
    assert "languages_supported" in data
    assert "hi" in data["languages_supported"]
    assert "en" in data["languages_supported"]


def test_voice_tts_sanitization_unit():
    """Verify TTS text sanitization strips markdown, bullets, and converts symbols."""
    from app.services.elevenlabs_service import elevenlabs_service
    raw_markdown = "### PM-KISAN Benefits\n- Citizens receive ₹6,000 annually.\nVisit [portal](https://pmkisan.gov.in)!"
    sanitized = elevenlabs_service.sanitize_for_speech(raw_markdown, "en")
    assert "###" not in sanitized
    assert "₹" not in sanitized
    assert "rupees" in sanitized.lower()
    assert "https://" not in sanitized
    assert "PM-KISAN Benefits" in sanitized


def test_voice_tts_endpoint_fallback():
    """Verify TTS endpoint gracefully handles unconfigured ElevenLabs keys by returning sanitized text for browser TTS."""
    res = client.post(
        "/api/v1/chatbot/voice/tts",
        json={"text": "Hello! I am Sahayak, your government scheme assistant.", "language": "en"}
    )
    assert res.status_code == 200
    # If ELEVENLABS_API_KEY is not set in test environment, it returns browser fallback JSON
    # If set, it returns audio/mpeg. Both are valid.
    content_type = res.headers.get("content-type", "")
    if "application/json" in content_type:
        data = res.json()
        assert data["provider"] == "browser_fallback"
        assert "Sahayak" in data["sanitized_text"]
    else:
        assert "audio/mpeg" in content_type



