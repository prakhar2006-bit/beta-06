"""Chatbot Service for YojanaMitra.
Orchestrates AI intents, tool calling, deterministic eligibility evaluation, and document analysis.
Conforms strictly to YojanaMitra AI Architecture and Intent-Based Response Guidelines.
"""
from datetime import datetime, timezone
import uuid
from typing import Any
import re

from app.schemas.chatbot import (
    ApplicationGuidanceData,
    ChatMessageRequest,
    ChatMessageResponse,
    CriterionEvaluationItem,
    DocumentCheckItem,
    EligibilityCardData,
    IntentAnalysis,
    SchemeCardData,
)
from app.services.gemini_service import gemini_service, detect_language
from app.services.profile_context_service import profile_context_service
from app.services.scheme_retrieval_service import scheme_retrieval_service


class ChatbotService:
    """Core orchestration service for YojanaMitra AI Assistant."""

    def __init__(self) -> None:
        # In-memory ephemeral conversation store (keyed by conversation_id)
        # Bounded to protect server memory while supporting active dialogue
        self._conversations: dict[str, list[dict[str, Any]]] = {}
        self._conversation_facts: dict[str, dict[str, Any]] = {}

    def get_conversation_history(self, conversation_id: str) -> list[dict[str, Any]]:
        """Retrieve previous messages in a conversation."""
        return self._conversations.get(conversation_id, [])

    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a conversation session and associated facts."""
        cleared = False
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            cleared = True
        if conversation_id in self._conversation_facts:
            del self._conversation_facts[conversation_id]
            cleared = True
        return cleared

    def _extract_facts(self, text: str, lang: str) -> dict[str, str]:
        """Extract personal facts from user message using pattern matching."""
        facts: dict[str, str] = {}
        t = text.strip()
        tl = t.lower()

        # English patterns
        # Name: "my name is Prakhar", "i am Prakhar", "i'm Prakhar", "call me Prakhar"
        m = re.search(r"(?:my name is|i am|i'm|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", t)
        if not m:
            m = re.search(r"(?:my name is|i am|i'm|call me)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)", tl)
        if m:
            name_val = m.group(1).strip()
            # Avoid matching adjectives/roles like "eligible", "student", "farmer", "looking"
            if name_val.lower() not in ("eligible", "interested", "a", "an", "the", "looking", "here"):
                facts["name"] = name_val.title()

        # Location: "i live in Bhopal", "i stay in Bhopal", "i am from Bhopal", "my city is Bhopal"
        m = re.search(r"(?:i live in|i stay in|i am from|i'm from|i reside in|my city is|my village is)\s+([a-zA-Z\s]+?)(?:\.|$|,)", tl)
        if m:
            facts["location"] = m.group(1).strip().title()

        # Age: "my age is 24", "i am 24 years old"
        m = re.search(r"(?:my age is|i am|i'm)\s+(\d{1,3})\s*(?:years?\s*old)?", tl)
        if m:
            age_val = int(m.group(1))
            if 1 <= age_val <= 120:
                facts["age"] = str(age_val)

        # Occupation
        m = re.search(r"(?:i am a|i'm a|i work as a?|my occupation is|my job is)\s+(student|farmer|teacher|engineer|doctor|worker|laborer|labourer|artisan|homemaker)", tl)
        if m:
            facts["occupation"] = m.group(1).strip()

        # Hindi patterns
        m = re.search(r"मेरा नाम\s+(.+?)(?:\s+है|$)", t)
        if m:
            facts["name"] = m.group(1).strip()

        m = re.search(r"मैं\s+(.+?)\s+(?:में|से)\s+(?:रहता|रहती|हूँ|हूं)", t)
        if m and "नाम" not in t:
            facts["location"] = m.group(1).strip()

        m = re.search(r"मेरी उम्र\s+(\d{1,3})\s*(?:साल|वर्ष)?", t)
        if m:
            age_val = int(m.group(1))
            if 1 <= age_val <= 120:
                facts["age"] = str(age_val)

        return facts

    def _recall_fact(self, query: str, conv_id: str) -> tuple[str | None, str | None]:
        """Look up a conversational fact. Returns (fact_key, fact_value) or (None, None)."""
        facts = self._conversation_facts.get(conv_id, {})
        if not facts:
            return None, None

        q = query.lower()

        # English & Hindi recall patterns
        if any(w in q for w in ["my name", "who am i", "मेरा नाम", "मुझे किस नाम", "मेरा क्या नाम"]):
            val = facts.get("name")
            return ("name", val) if val else (None, None)

        if any(w in q for w in ["where do i live", "where i live", "my city", "my location", "कहाँ रहता", "कहां रहता", "मेरा शहर", "मेरा राज्य"]):
            val = facts.get("location")
            return ("location", val) if val else (None, None)

        if any(w in q for w in ["my age", "how old am i", "मेरी उम्र", "मेरी आयु"]):
            val = facts.get("age")
            return ("age", val) if val else (None, None)

        if any(w in q for w in ["my occupation", "my job", "what do i do", "मेरा व्यवसाय", "मेरा काम"]):
            val = facts.get("occupation")
            return ("occupation", val) if val else (None, None)

        return None, None

    def process_message(self, request: ChatMessageRequest) -> ChatMessageResponse:
        """Process incoming user prompt through intent detection, tool execution, and response synthesis."""
        conv_id = request.conversation_id or str(uuid.uuid4())
        user_text = request.message.strip()
        lang = request.language or detect_language(user_text)

        # 1. Profile Context
        profile_summary = profile_context_service.build_context_summary(request.profile)
        p_data = profile_summary.get("profile_data", {})

        # 2. Conversation History Context
        history = self._conversations.get(conv_id, [])

        # 3. Comprehensive Intent Analysis Layer (Part 3)
        analysis = self._analyze_intent(user_text, lang, history)

        # 4. Initialize Structured Outputs
        schemes_cards: list[SchemeCardData] = []
        eligibility_card: EligibilityCardData | None = None
        missing_docs: list[DocumentCheckItem] = []
        app_guidance: ApplicationGuidanceData | None = None
        suggested_followups: list[str] = []
        assistant_message = ""
        resolved_target_scheme: dict[str, Any] | None = None

        # 5. Intent-Based Routing and Execution (Part 4)

        # A. GREETINGS (Must NEVER display scheme cards or execute scheme search)
        if analysis.intent == "greeting":
            if lang == "hi":
                assistant_message = "नमस्ते! Sahayak में आपका स्वागत है। मैं सरकारी योजनाओं के बारे में आपकी सहायता कर सकता हूँ।"
                suggested_followups = [
                    "मेरे लिए छात्रवृत्ति योजनाएं खोजें",
                    "किसानों के लिए सरकारी योजनाएं दिखाएं",
                    "मेरी पात्रता की जांच करें",
                    "आवश्यक दस्तावेज़ क्या हैं?",
                ]
            else:
                assistant_message = "Hello! Welcome to Sahayak. How can I help you explore government schemes?"
                suggested_followups = [
                    "Find scholarships for me",
                    "Show schemes for farmers",
                    "Check my eligibility",
                    "Which documents do I need?",
                ]

        # A1. ISOLATED SCHEME INQUIRY (Clarify specific category instead of generic welcome)
        elif analysis.intent == "scheme_category_clarification":
            if lang == "hi":
                assistant_message = (
                    "आप किस श्रेणी की सरकारी योजना के बारे में जानना चाहते हैं? "
                    "कृपया अपनी रुचि बताएं: छात्रवृत्ति (विद्यार्थी), कृषि और किसान सहायता (PM-KISAN), "
                    "आवास योजना (PMAY), स्वास्थ्य सेवा (आयुष्मान भारत), अथवा महिला कल्याण (लाड़ली बहना)।"
                )
                suggested_followups = [
                    "छात्रवृत्ति योजनाएं (विद्यार्थियों के लिए)",
                    "किसान योजनाएं (PM-KISAN)",
                    "आवास योजनाएं (PMAY)",
                    "स्वास्थ्य योजनाएं (आयुष्मान भारत)",
                ]
            else:
                assistant_message = (
                    "Which category of government schemes are you interested in? "
                    "Please choose or tell me your category: Scholarships (Students), Agriculture & Farmer Welfare (PM-KISAN), "
                    "Rural Housing (PMAY), Healthcare (Ayushman Bharat), or Women Welfare (Ladli Behna)."
                )
                suggested_followups = [
                    "Scholarships for students",
                    "Farmer schemes (PM-KISAN)",
                    "Housing schemes (PMAY)",
                    "Healthcare schemes (Ayushman Bharat)",
                ]

        # A2. PERSONAL INFORMATION (User sharing name, location, age, etc.)
        elif analysis.intent == "personal_information":
            extracted = self._extract_facts(user_text, lang)
            if conv_id not in self._conversation_facts:
                self._conversation_facts[conv_id] = {}
            self._conversation_facts[conv_id].update(extracted)

            if "name" in extracted:
                assistant_message = (
                    f"आपसे मिलकर खुशी हुई, {extracted['name']}!"
                    if lang == "hi"
                    else f"Nice to meet you, {extracted['name']}!"
                )
            elif "location" in extracted:
                assistant_message = (
                    f"अच्छा, आप {extracted['location']} में रहते हैं। मैं इसे याद रखूँगा!"
                    if lang == "hi"
                    else f"Got it, you live in {extracted['location']}. I'll remember that!"
                )
            elif "age" in extracted:
                assistant_message = (
                    f"धन्यवाद! मैंने आपकी उम्र ({extracted['age']} वर्ष) नोट कर ली है।"
                    if lang == "hi"
                    else f"Thanks! I've noted your age ({extracted['age']} years)."
                )
            elif "occupation" in extracted:
                assistant_message = (
                    f"अच्छा, आप एक {extracted['occupation']} हैं। मैं इसे याद रखूँगा!"
                    if lang == "hi"
                    else f"Great, you're a {extracted['occupation']}. I'll remember that!"
                )
            else:
                assistant_message = (
                    "धन्यवाद! मैं आपकी किस प्रकार सहायता कर सकता हूँ?"
                    if lang == "hi"
                    else "Thanks for sharing! How can I help you explore government schemes?"
                )
            suggested_followups = (
                ["मेरे लिए योजनाएं खोजें", "मेरी पात्रता जांचें", "छात्रवृत्ति दिखाएं"]
                if lang == "hi"
                else ["Find schemes for me", "Check my eligibility", "Show scholarships"]
            )

        # A3. PERSONAL QUESTION (Recalling previously shared facts from conversation memory)
        elif analysis.intent == "personal_question":
            fact_key, fact_value = self._recall_fact(user_text, conv_id)
            if fact_value:
                if fact_key == "name":
                    assistant_message = (
                        f"आपका नाम {fact_value} है।"
                        if lang == "hi"
                        else f"Your name is {fact_value}."
                    )
                elif fact_key == "location":
                    assistant_message = (
                        f"आप {fact_value} में रहते हैं।"
                        if lang == "hi"
                        else f"You live in {fact_value}."
                    )
                elif fact_key == "age":
                    assistant_message = (
                        f"आपकी उम्र {fact_value} वर्ष है।"
                        if lang == "hi"
                        else f"Your age is {fact_value} years."
                    )
                else:
                    assistant_message = (
                        f"आपका {fact_key} {fact_value} है।"
                        if lang == "hi"
                        else f"Your {fact_key} is {fact_value}."
                    )
            else:
                assistant_message = (
                    "मुझे अभी यह जानकारी नहीं है। क्या आप मुझे बता सकते हैं?"
                    if lang == "hi"
                    else "I don't have that information yet. Could you please tell me?"
                )
            suggested_followups = (
                ["मेरे लिए योजनाएं खोजें", "मेरी पात्रता जांचें"]
                if lang == "hi"
                else ["Find schemes for me", "Check my eligibility"]
            )

        # A4. FAKE SCHEME & MYTH DEBUNKING
        elif analysis.intent == "myth_debunking":
            if lang == "hi":
                assistant_message = (
                    "सावधानी: इस नाम से संबंधित कोई आधिकारिक सरकारी योजना (जैसे 'मुफ्त स्मार्टफोन / टैबलेट योजना' या 'सार्वभौमिक बुनियादी आय') "
                    "केंद्र या राज्य सरकार द्वारा संचालित नहीं है। सोशल मीडिया पर फैलने वाले फर्जी संदेशों और अनधिकृत लिंक से सावधान रहें। "
                    "सरकार की आधिकारिक योजनाएं केवल .gov.in या .nic.in पोर्टलों पर उपलब्ध होती हैं और इनके लिए कोई पंजीकरण शुल्क नहीं लिया जाता है।"
                )
            else:
                assistant_message = (
                    "Caution: There is no officially verified central or state welfare scheme matching this inquiry "
                    "(such as 'Free Smartphone / Free Tablet Yojana 2026' or 'Universal Basic Income'). Please be vigilant against "
                    "misleading viral messages and fraudulent registration links. Genuine government welfare schemes are hosted "
                    "strictly on official .gov.in and .nic.in domains and never require registration fees or bank OTPs through unofficial agents."
                )
            suggested_followups = (
                ["सत्यापित छात्रवृत्ति योजनाएं खोजें", "मेरी पात्रता जांचें", "आधिकारिक किसान योजनाएं दिखाएं"]
                if lang == "hi"
                else ["Find verified scholarships", "Check my eligibility", "Show official farmer schemes"]
            )

        # A5. HINDI EXPLANATION / TRANSLATION REQUEST
        elif analysis.intent == "hindi_explanation":
            lang = "hi"
            target_scheme = self._resolve_target_scheme(user_text, p_data, history)
            last_msg = ""
            for m in reversed(history):
                if m.get("role") == "assistant" and m.get("content"):
                    last_msg = m["content"]
                    break

            if target_scheme:
                card = self._to_card(target_scheme, "hi", "हिंदी में विस्तृत विवरण।")
                schemes_cards = [card]
                scheme_name_hi = target_scheme["name"].get("hi", target_scheme["name"]["en"])
                benefits_hi = target_scheme["benefits"].get("hi", target_scheme["benefits"]["en"])
                instructions = target_scheme.get("application_instructions", {})
                steps_hi = instructions.get("steps", [])

                steps_formatted = "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps_hi)])
                assistant_message = (
                    f"**{scheme_name_hi}** की मुख्य जानकारी हिंदी में:\n\n"
                    f"**योजना के लाभ:** {benefits_hi}\n\n"
                    f"**आवेदन प्रक्रिया:**\n{steps_formatted}\n\n"
                    f"**आधिकारिक वेबसाइट:** {target_scheme.get('official_url', 'उपलब्ध नहीं')}"
                )
            elif last_msg:
                assistant_message = (
                    f"पिछली जानकारी का हिंदी विवरण:\n\n{last_msg}\n\n"
                    "यदि आप किसी विशिष्ट सरकारी योजना के लाभ, पात्रता अथवा दस्तावेज़ों के बारे में विस्तार से जानना चाहते हैं, तो कृपया उसका नाम बताएं।"
                )
            else:
                assistant_message = "हाँ, मैं आपको सभी सरकारी योजनाओं की जानकारी सरल हिन्दी में समझा सकता हूँ। आप किस योजना के बारे में जानना चाहते हैं?"

            suggested_followups = [
                "मेरी पात्रता की जांच करें",
                "आवश्यक दस्तावेज़ क्या हैं?",
                "आवेदन कैसे करें?",
            ]

        # A6. BROAD CITIZEN OVERVIEW (Ordinary citizens asking general availability)
        elif analysis.intent == "citizen_overview":
            if lang == "hi":
                assistant_message = (
                    "भारत सरकार एवं राज्य सरकारों द्वारा सामान्य नागरिकों के लिए कई प्रमुख क्षेत्रों में कल्याणकारी योजनाएं चलाई जा रही हैं:\n\n"
                    "1. **स्वास्थ्य बीमा (Healthcare)**: आयुष्मान भारत (PM-JAY) — सूचीबद्ध अस्पतालों में ₹5 लाख तक का निःशुल्क कैशलेस इलाज।\n"
                    "2. **आवास योजना (Housing)**: प्रधानमंत्री आवास योजना (PMAY) — पक्का मकान निर्माण हेतु ₹1.20 से ₹2.50 लाख तक वित्तीय अनुदान।\n"
                    "3. **शिक्षा एवं छात्रवृत्ति (Education)**: पोस्ट-मैट्रिक एवं प्री-मैट्रिक छात्रवृत्तियां — शुल्क प्रतिपूर्ति व भत्ता।\n"
                    "4. **कृषि सहायता (Agriculture)**: पीएम-किसान (PM-KISAN) — भूमिधारक किसानों को ₹6,000 वार्षिक आय सहायता।\n"
                    "5. **कौशल एवं रोजगार (Skill & Jobs)**: पीएम कौशल विकास योजना (PMKVY 4.0) — निःशुल्क रोजगारोन्मुख प्रशिक्षण व सरकारी प्रमाण पत्र।\n"
                    "6. **महिला कल्याण व ऊर्जा (Women & Energy)**: लाड़ली बहना योजना (मासिक सहायता) एवं उज्ज्वला योजना (निःशुल्क गैस कनेक्शन)।\n\n"
                    "कृपया बताएं कि आप किस श्रेणी (जैसे आवास, छात्रवृत्ति, या रोजगार) में योजनाएं खोजना चाहते हैं?"
                )
                suggested_followups = [
                    "आवास योजनाएं दिखाएं",
                    "छात्रवृत्ति योजनाएं खोजें",
                    "कौशल विकास योजनाएं दिखाएं",
                    "स्वास्थ्य योजनाएं दिखाएं",
                ]
            else:
                assistant_message = (
                    "The Government of India and State Governments provide targeted welfare schemes across several core sectors for ordinary citizens:\n\n"
                    "1. **Healthcare**: Ayushman Bharat (PM-JAY) — up to ₹5,00,000 annual cashless hospitalization coverage per family.\n"
                    "2. **Housing**: Pradhan Mantri Awaas Yojana (PMAY) — financial grants up to ₹2.5 Lakh for constructing a permanent pucca house.\n"
                    "3. **Education**: Post-Matric Scholarships & National Scholarship Portal grants for college & school students.\n"
                    "4. **Agriculture**: PM-KISAN — ₹6,000 annual direct income support for landholding farming families.\n"
                    "5. **Skill & Employment**: PM Kaushal Vikas Yojana (PMKVY 4.0) — 100% free industry skill training and NSQF certificate.\n"
                    "6. **Women Welfare & Energy**: Ladli Behna Yojana (monthly assistance) and PM Ujjwala (deposit-free LPG connection).\n\n"
                    "Please let me know which area you are interested in (e.g., housing, scholarships, employment, or healthcare) so I can guide you!"
                )
                suggested_followups = [
                    "Show housing schemes",
                    "Find scholarships for me",
                    "Show skill development programs",
                    "Show healthcare schemes",
                ]

        # B. GENERAL CONVERSATION & CLARIFICATION (About bot or platform capabilities; no scheme cards)
        elif analysis.intent in ("general_conversation", "clarification"):
            assistant_message = self._handle_general_conversation(user_text, lang)
            suggested_followups = (
                ["छात्रवृत्ति योजनाएं दिखाएं", "किसानों के लिए योजनाएं", "मेरी पात्रता जांचें"]
                if lang == "hi"
                else ["Find scholarships for me", "Show schemes for farmers", "Check my eligibility"]
            )

        # C. OUT OF SCOPE / UNRELATED (Strict GovTech scope enforcement - NO scheme cards)
        elif analysis.intent in ("out_of_scope", "unrelated"):
            if lang == "hi":
                assistant_message = (
                    "मुझे आपके प्रश्न से संबंधित कोई सत्यापित सरकारी योजना हमारे डेटाबेस में नहीं मिली। "
                    "कृपया योजना का नाम जांचें या उपलब्ध श्रेणियों (जैसे छात्रवृत्ति, कृषि, आवास और स्वास्थ्य सेवा) में से चुनें।"
                )
                suggested_followups = [
                    "छात्रवृत्ति योजनाएं खोजें",
                    "किसानों के लिए सरकारी योजनाएं",
                    "आवास योजनाएं (PMAY)",
                    "स्वास्थ्य योजनाएं (आयुष्मान भारत)",
                ]
            else:
                assistant_message = (
                    "I could not find a verified government scheme matching your query in the database. "
                    "Please verify the scheme name or explore our available categories (e.g., scholarships, agriculture, housing, healthcare)."
                )
                suggested_followups = [
                    "Find scholarships for me",
                    "Show schemes for farmers",
                    "Housing schemes (PMAY)",
                    "Healthcare schemes (Ayushman Bharat)",
                ]
            schemes_cards = []
            eligibility_card = None
            missing_docs = []
            app_guidance = None

        # D. PROFILE INFORMATION
        elif analysis.intent == "profile_information":
            assistant_message = self._handle_profile_inquiry(p_data, lang)
            suggested_followups = (
                ["मेरी पात्रता जांचें", "मेरे लिए उपयुक्त योजनाएं खोजें"]
                if lang == "hi"
                else ["Check my eligibility", "Find schemes matching my profile"]
            )

        # E. SCHEME INFORMATION (Details of a specific scheme requested by name)
        elif analysis.intent in ("scheme_information", "scheme_details"):
            target_scheme = self._resolve_target_scheme(user_text, p_data, history)
            resolved_target_scheme = target_scheme
            if not target_scheme:
                # Case B: Government scheme question, but scheme not found in database
                if lang == "hi":
                    assistant_message = (
                        "हमारे डेटाबेस में इस योजना का कोई सत्यापित रिकॉर्ड नहीं मिला। कृपया योजना का नाम जांचें या संबंधित योजनाओं को देखें।"
                    )
                else:
                    if "scholarship" in user_text.lower() or "छात्रवृत्ति" in user_text:
                        assistant_message = "I couldn't find a verified record for this scheme in our database. Please check the scheme name or explore related scholarship schemes."
                    else:
                        assistant_message = "I couldn't find a verified record for this scheme in our database. Please check the scheme name or explore related government schemes."
                suggested_followups = (
                    ["छात्रवृत्ति योजनाएं दिखाएं", "किसान योजनाएं दिखाएं", "मेरी पात्रता जांचें"]
                    if lang == "hi"
                    else ["Find scholarships for me", "Show schemes for farmers", "Check my eligibility"]
                )
            else:
                card = self._to_card(target_scheme, lang, "Requested scheme details.")
                schemes_cards = [card]
                assistant_message, _ = gemini_service.generate_response(
                    user_message=user_text,
                    conversation_history=history,
                    profile_context=profile_summary.get("summary_text", ""),
                    retrieved_schemes=[target_scheme],
                    preferred_language=lang,
                )
                suggested_followups = (
                    [f"क्या मैं {card.name.split('(')[0].strip()} के लिए पात्र हूँ?", "आवश्यक दस्तावेज़ क्या हैं?", "आवेदन कैसे करें?"]
                    if lang == "hi"
                    else [f"Am I eligible for {card.name.split('(')[0].strip()}?", "Which documents do I need?", "How do I apply?"]
                )

        # F. SCHEME DISCOVERY (Finding matching schemes by category, state, or keywords)
        elif analysis.intent == "scheme_discovery":
            raw_schemes = scheme_retrieval_service.search_schemes(
                query=user_text,
                state=p_data.get("state"),
                occupation=p_data.get("occupation"),
                gender=p_data.get("gender"),
                limit=4,
            )
            if raw_schemes:
                schemes_cards = [
                    self._to_card(item["scheme"], lang, item["match_reason"])
                    for item in raw_schemes
                ]
                assistant_message, _ = gemini_service.generate_response(
                    user_message=user_text,
                    conversation_history=history,
                    profile_context=profile_summary.get("summary_text", ""),
                    retrieved_schemes=[item["scheme"] for item in raw_schemes],
                    preferred_language=lang,
                )
                first_name = schemes_cards[0].name.split("(")[0].strip()
                suggested_followups = (
                    [f"क्या मैं {first_name} के लिए पात्र हूँ?", "आवश्यक दस्तावेज़ क्या हैं?", "आवेदन कैसे करें?"]
                    if lang == "hi"
                    else [f"Am I eligible for {first_name}?", "Which documents do I need?", "How do I apply?"]
                )
            else:
                if lang == "hi":
                    assistant_message = (
                        "आपकी खोज के अनुसार डेटाबेस में कोई योजना नहीं मिली। "
                        "आप छात्रवृत्ति, किसान सहायता, आवास, या महिला कल्याण श्रेणियों में खोज कर सकते हैं।"
                    )
                else:
                    assistant_message = (
                        "No government schemes matching this specific request were found in the database. "
                        "You can try searching by category such as scholarships, agriculture, housing, healthcare, or women empowerment."
                    )
                suggested_followups = (
                    ["छात्रवृत्ति योजनाएं खोजें", "किसानों के लिए योजनाएं", "आवास योजनाएं"]
                    if lang == "hi"
                    else ["Find scholarships for me", "Show schemes for farmers", "Show housing schemes"]
                )

        # G. ELIGIBILITY CHECK (Deterministic engine evaluation)
        elif analysis.intent == "eligibility_check":
            target_scheme = self._resolve_target_scheme(user_text, p_data, history)
            resolved_target_scheme = target_scheme
            eval_profile = dict(p_data)
            # Detect inline hypothetical or stated condition: e.g. "what if I do not own agricultural land"
            if any(w in user_text.lower() for w in ["do not own", "don't own", "without land", "no land", "landless", "zameen nahi", "bhoomiheen"]):
                eval_profile["owns_agricultural_land"] = False

            if target_scheme:
                eligibility_card = self._evaluate_deterministic_eligibility(target_scheme, eval_profile, lang)
                assistant_message, _ = gemini_service.generate_response(
                    user_message=user_text,
                    conversation_history=history,
                    profile_context=profile_summary.get("summary_text", ""),
                    retrieved_schemes=[target_scheme],
                    eligibility_context=eligibility_card.model_dump(),
                    preferred_language=lang,
                )
                suggested_followups = (
                    ["इसके लिए कौन-से दस्तावेज़ चाहिए?", "आवेदन करने की प्रक्रिया क्या है?", "अन्य संबंधित योजनाएं खोजें"]
                    if lang == "hi"
                    else ["Which documents are required?", "How can I apply?", "Explore more schemes for me"]
                )
            else:
                if lang == "hi":
                    assistant_message = (
                        "कृपया बताएं कि आप किस योजना के लिए पात्रता जांचना चाहते हैं (जैसे PM-KISAN, पोस्ट-मैट्रिक छात्रवृत्ति, लाड़ली बहना, या PMAY)?"
                    )
                else:
                    assistant_message = (
                        "Please specify which scheme you would like to check eligibility for (e.g., PM-KISAN, Post-Matric Scholarship, Ladli Behna, or PMAY)."
                    )
                suggested_followups = (
                    ["पीएम किसान की पात्रता जांचें", "छात्रवृत्ति की पात्रता जांचें"]
                    if lang == "hi"
                    else ["Check PM-KISAN eligibility", "Check scholarship eligibility"]
                )

        # H. DOCUMENT ASSISTANCE / MISSING DOCUMENTS
        elif analysis.intent in ("document_assistance", "missing_documents"):
            target_scheme = self._resolve_target_scheme(user_text, p_data, history)
            resolved_target_scheme = target_scheme
            # Check if user asks about a specific document (e.g., income certificate, caste certificate)
            specific_doc_guide = self._handle_specific_document_query(user_text, lang)
            if target_scheme:
                missing_docs = self._analyze_missing_documents(target_scheme, p_data, lang)

            if specific_doc_guide:
                assistant_message = specific_doc_guide
            elif target_scheme:
                assistant_message, _ = gemini_service.generate_response(
                    user_message=user_text,
                    conversation_history=history,
                    profile_context=profile_summary.get("summary_text", ""),
                    retrieved_schemes=[target_scheme],
                    preferred_language=lang,
                )
            else:
                assistant_message = (
                    "सरकारी योजनाओं के लिए सामान्यतः आधार कार्ड, आय प्रमाण पत्र, निवास प्रमाण (समग्र आईडी/राशन कार्ड), "
                    "और आधार-लिंक बैंक पासबुक आवश्यक होते हैं। विशिष्ट योजना के दस्तावेज़ जानने हेतु योजना का नाम बताएं।"
                    if lang == "hi"
                    else "Standard documents required for government welfare schemes include Aadhaar Card, Income Certificate, Resident/Domicile Proof, and a DBT-enabled bank account. To see exact requirements, please name the specific scheme."
                )

            suggested_followups = (
                ["आवेदन कैसे करें?", "मेरी पात्रता जांचें", "अन्य योजनाएं दिखाएं"]
                if lang == "hi"
                else ["How do I apply?", "Check my eligibility", "Show other schemes"]
            )

        # I. APPLICATION GUIDANCE
        elif analysis.intent == "application_guidance":
            target_scheme = self._resolve_target_scheme(user_text, p_data, history)
            resolved_target_scheme = target_scheme
            if target_scheme:
                app_guidance = self._get_application_guidance(target_scheme, lang)
                assistant_message, _ = gemini_service.generate_response(
                    user_message=user_text,
                    conversation_history=history,
                    profile_context=profile_summary.get("summary_text", ""),
                    retrieved_schemes=[target_scheme],
                    preferred_language=lang,
                )
            else:
                assistant_message = (
                    "आप अधिकांश सरकारी योजनाओं के लिए आधिकारिक .gov.in पोर्टल अथवा अपने नजदीकी ग्राम पंचायत सीएससी (CSC) केंद्र के माध्यम से आवेदन कर सकते हैं। विशिष्ट योजना के आवेदन चरण जानने के लिए योजना का नाम बताएं।"
                    if lang == "hi"
                    else "You can apply for most government schemes either online via official .gov.in portals or in person at your nearest Common Service Centre (CSC). Please specify a scheme for exact steps."
                )
            suggested_followups = (
                ["आवश्यक दस्तावेज़ क्या हैं?", "मेरी पात्रता जांचें"]
                if lang == "hi"
                else ["Which documents are needed?", "Check my eligibility"]
            )

        # J. SCHEME FOLLOW-UP
        elif analysis.intent in ("scheme_follow_up", "follow_up"):
            target_scheme = self._resolve_target_scheme(user_text, p_data, history)
            resolved_target_scheme = target_scheme
            if target_scheme:
                schemes_cards = [self._to_card(target_scheme, lang, "Follow-up discussion.")]
                assistant_message, _ = gemini_service.generate_response(
                    user_message=user_text,
                    conversation_history=history,
                    profile_context=profile_summary.get("summary_text", ""),
                    retrieved_schemes=[target_scheme],
                    preferred_language=lang,
                )
            else:
                assistant_message = (
                    "कृपया स्पष्ट करें कि आप किस सरकारी योजना के बारे में जानना चाहते हैं?"
                    if lang == "hi"
                    else "Could you please clarify which government scheme you are referring to?"
                )

        # Fallback default: Strict Scope Enforcement (Never hallucinate or answer unrelated questions)
        else:
            if lang == "hi":
                assistant_message = (
                    "मुझे आपके प्रश्न से संबंधित कोई सत्यापित सरकारी योजना हमारे डेटाबेस में नहीं मिली। "
                    "कृपया योजना का नाम जांचें या उपलब्ध श्रेणियों (जैसे छात्रवृत्ति, कृषि, आवास और स्वास्थ्य सेवा) में से चुनें।"
                )
            else:
                assistant_message = (
                    "I could not find a verified government scheme matching your query in the database. "
                    "Please verify the scheme name or explore our available categories (e.g., scholarships, agriculture, housing, healthcare)."
                )
            suggested_followups = (
                ["छात्रवृत्ति योजनाएं खोजें", "किसानों के लिए सरकारी योजनाएं"]
                if lang == "hi"
                else ["Find scholarships for me", "Show schemes for farmers"]
            )
            schemes_cards = []

        # 6. Record Conversation History in Memory
        if conv_id not in self._conversations:
            self._conversations[conv_id] = []

        now_iso = datetime.now(timezone.utc).isoformat()
        self._conversations[conv_id].append({
            "role": "user",
            "content": user_text,
            "timestamp": now_iso,
        })
        recorded_target_id = None
        if resolved_target_scheme:
            recorded_target_id = resolved_target_scheme.get("id")
        elif schemes_cards:
            recorded_target_id = schemes_cards[0].scheme_id
        else:
            recorded_target_id = self._get_last_assistant_target_id(history)

        self._conversations[conv_id].append({
            "role": "assistant",
            "content": assistant_message,
            "intent": analysis.intent,
            "schemes": [s.model_dump() for s in schemes_cards],
            "target_scheme_id": recorded_target_id,
            "timestamp": now_iso,
        })

        # Cap memory to 20 turns
        if len(self._conversations[conv_id]) > 20:
            self._conversations[conv_id] = self._conversations[conv_id][-20:]

        return ChatMessageResponse(
            conversation_id=conv_id,
            message=assistant_message,
            language=lang,
            intent=analysis.intent,
            intent_details=analysis,
            schemes=schemes_cards,
            eligibility=eligibility_card,
            missing_documents=missing_docs,
            application_guidance=app_guidance,
            suggested_followups=suggested_followups,
        )

    def _analyze_intent(self, text: str, lang: str, history: list[dict[str, Any]]) -> IntentAnalysis:
        """Deterministic, highly accurate intent classifier supporting all 11 Part 3 intents."""
        t = text.lower().strip()

        # 0.5 FAKE SCHEME & MYTH DEBUNKING TRAP
        fake_scheme_keywords = [
            "free android smartphone", "free smartphone", "free tablet", "free laptop yojana",
            "universal citizen basic income", "universal basic income", "5 lakh bina document",
            "bina document loan", "instant cash without document",
        ]
        if any(f in t for f in fake_scheme_keywords):
            return IntentAnalysis(
                intent="myth_debunking",
                language=lang,
                requires_profile=False,
                requires_scheme_search=False,
                requires_eligibility_check=False,
                requires_document_check=False,
            )

        # 0.6 HINDI EXPLANATION / TRANSLATION REQUEST
        hindi_explanation_patterns = [
            "explain it in hindi", "explain in hindi", "tell me in hindi", "in hindi please",
            "translate to hindi", "translate in hindi", "simple hindi", "hindi mein samjhao",
            "hindi me samjhao", "hindi mein batao", "hindi me batao", "हिंदी में समझाओ", "हिंदी में बताओ"
        ]
        if any(p in t for p in hindi_explanation_patterns):
            return IntentAnalysis(
                intent="hindi_explanation",
                language="hi",
                requires_profile=False,
                requires_scheme_search=False,
                requires_eligibility_check=False,
                requires_document_check=False,
            )

        # 0.7 BROAD CITIZEN OVERVIEW (Ordinary citizens asking general availability)
        broad_citizen_patterns = [
            "ordinary citizen", "ordinary citizens", "general citizen", "general citizens",
            "available for ordinary", "schemes for ordinary", "aam nagrik", "आम नागरिक",
            "available schemes for all",
        ]
        if any(p in t for p in broad_citizen_patterns):
            return IntentAnalysis(
                intent="citizen_overview",
                language=lang,
                requires_profile=False,
                requires_scheme_search=False,
                requires_eligibility_check=False,
                requires_document_check=False,
            )

        # 0.8 ISOLATED SCHEME / CATEGORY INQUIRY (Single word "scheme", "schemes", "योजना")
        if t.strip() in [
            "scheme", "schemes", "yojana", "yojna", "yojanaen",
            "योजना", "योजनाएं", "government scheme", "government schemes",
            "sarkari yojana", "सरकारी योजना", "सरकारी योजनाएं"
        ]:
            return IntentAnalysis(
                intent="scheme_category_clarification",
                language=lang,
                requires_profile=False,
                requires_scheme_search=False,
                requires_eligibility_check=False,
                requires_document_check=False,
            )

        # 1. GREETING (Strict word boundaries for English; exact substring for Hindi Devanagari)
        english_greeting_patterns = [
            r"\bhi\b", r"\bhello\b", r"\bhey\b", r"\bnamaste\b", r"\bgreetings\b",
            r"\bgood\s*morning\b", r"\bgood\s*afternoon\b", r"\bgood\s*evening\b",
            r"\bhow\s*are\s*you\b", r"\bhow\s*do\s*you\s*do\b",
        ]
        hindi_greeting_words = ["नमस्ते", "प्रणाम", "सुप्रभात", "आप कैसे हैं", "क्या हाल है", "जय हिंद", "जय हिन्द"]

        is_eng_greeting = any(re.search(pat, t, re.IGNORECASE) for pat in english_greeting_patterns)
        is_hindi_greeting = any(w in t for w in hindi_greeting_words)

        if is_eng_greeting or is_hindi_greeting:
            # Ensure it's not a compound question starting with hi like "hi, show me scholarships"
            if not any(k in t for k in ["scholarship", "scheme", "farmer", "kisan", "eligible", "apply", "document", "छात्रवृत्ति", "योजना", "पात्रता", "दस्तावेज़", "आवेदन"]):
                return IntentAnalysis(
                    intent="greeting",
                    language="hi" if is_hindi_greeting else lang,
                    requires_profile=False,
                    requires_scheme_search=False,
                    requires_eligibility_check=False,
                    requires_document_check=False,
                )

        # 1.5 PERSONAL QUESTION (Recall personal facts; must be checked before scheme_information)
        personal_question_patterns = [
            "what is my name", "what's my name", "who am i", "where do i live",
            "where i live", "what is my age", "how old am i", "what do i do",
            "what is my occupation", "what is my job", "do you know my name",
            "do you remember my name", "remember me", "tell me my name",
            "मेरा नाम क्या है", "मैं कहाँ रहता", "मैं कहां रहता", "मेरी उम्र क्या है",
            "क्या तुम मेरा नाम जानते हो", "मेरा नाम बताओ", "मुझे याद है",
        ]
        if any(p in t for p in personal_question_patterns):
            return IntentAnalysis(
                intent="personal_question",
                language=lang,
                requires_profile=False,
                requires_scheme_search=False,
                requires_eligibility_check=False,
                requires_document_check=False,
            )

        # 1.6 PERSONAL INFORMATION (User sharing name, location, age, occupation)
        personal_info_patterns = [
            r"\bmy name is\s+[a-zA-Z]+",
            r"\bi am\s+[a-zA-Z]+",
            r"\bi'm\s+[a-zA-Z]+",
            r"\bcall me\s+[a-zA-Z]+",
            r"\bi live in\s+[a-zA-Z]+",
            r"\bi stay in\s+[a-zA-Z]+",
            r"\bi am from\s+[a-zA-Z]+",
            r"\bi'm from\s+[a-zA-Z]+",
            r"\bmy age is\s+\d+",
            r"\bi am\s+\d+\s*years?\s*old",
        ]
        hindi_personal_info = ["मेरा नाम", "मैं रहता हूँ", "मैं रहती हूँ", "मेरी उम्र"]
        is_personal_info_en = any(re.search(p, t, re.IGNORECASE) for p in personal_info_patterns)
        is_personal_info_hi = any(w in t for w in hindi_personal_info)

        # Ensure bot identity questions like "what is your name" are NOT treated as user personal info
        is_bot_question = any(p in t for p in ["your name", "who are you", "tum kaun", "आप कौन", "what can you"])

        if (is_personal_info_en or is_personal_info_hi) and not is_bot_question:
            # Check if this is actually a scheme or eligibility query e.g. "i am eligible for pm-kisan"
            scheme_signal_words = ["eligible", "scheme", "scholarship", "kisan", "apply", "योजना", "पात्र", "छात्रवृत्ति"]
            has_scheme_signal = any(w in t for w in scheme_signal_words)
            if not has_scheme_signal:
                return IntentAnalysis(
                    intent="personal_information",
                    language=lang,
                    requires_profile=False,
                    requires_scheme_search=False,
                    requires_eligibility_check=False,
                    requires_document_check=False,
                )

        # 2. BOT IDENTITY & CLARIFICATION (Questions about Sahayak or platform capabilities)
        general_patterns = [
            "what is sahayak", "who is sahayak", "what is shayak", "who is shayak", "what is yojanamitra", "who are you", "what can you do", "how can you help",
            "can you speak hindi", "are you an ai", "what is your name", "who made you",
            "सहायक क्या है", "सहायक कौन है", "शायक क्या है", "शायक कौन है", "योजना मित्र क्या है", "तुम कौन हो", "आप कौन हैं", "आप क्या कर सकते हैं",
            "क्या आप हिंदी बोल सकते हैं", "क्या तुम एआई हो",
        ]
        if any(p in t for p in general_patterns):
            return IntentAnalysis(
                intent="clarification",
                language=lang,
                requires_profile=False,
                requires_scheme_search=False,
                requires_eligibility_check=False,
                requires_document_check=False,
            )

        # 3. OUT OF SCOPE (Strict non-welfare questions: politics, general trivia, code, math, jokes, poems)
        unrelated_patterns = [
            "who is the pm", "who is pm of india", "who is prime minister", "prime minister of india",
            "who is the president", "who is president of", "president of india",
            "capital of france", "capital of", "weather today", "what is the weather", "weather",
            "write a poem", "tell a joke", "tell me a joke", "joke sunao", "mujhe joke", "chutkula",
            "solve 25", "25 x 45", "25 × 45", "25 * 45", "mathematics", "solve this", "who won the cricket",
            "cricket match", "cricket", "football", "ipl", "score",
            "explain machine learning", "machine learning", "explain artificial intelligence",
            "what is java", "what is python", "python code", "def ", "java code", "programming in",
            "chocolate cake", "recipe", "movie", "song",
            "भारत का प्रधानमंत्री कौन है", "प्रधानमंत्री कौन", "राष्ट्रपति कौन", "कविता लिखो",
            "चुटकुला सुनाओ", "क्रिकेट मैच", "मौसम कैसा है",
        ]
        if any(p in t for p in unrelated_patterns):
            return IntentAnalysis(
                intent="out_of_scope",
                language=lang,
                requires_profile=False,
                requires_scheme_search=False,
                requires_eligibility_check=False,
                requires_document_check=False,
            )

        # 4. PROFILE INFORMATION
        if any(w in t for w in ["my profile", "my details", "what is my income", "what is my occupation", "मेरी प्रोफाइल", "मेरी जानकारी"]):
            return IntentAnalysis(
                intent="profile_information",
                language=lang,
                requires_profile=True,
                requires_scheme_search=False,
            )

        # 5. APPLICATION GUIDANCE (Check before eligibility so 'how can i apply' is not confused with 'can i apply')
        apply_keywords = [
            "how to apply", "how do i apply", "how can i apply", "where can i apply",
            "how can i register", "how do i register", "how to register", "how to enroll",
            "official website", "portal", "registration", "application form",
            "apply online", "apply offline", "apply kaise", "aavedan kaise",
            "registration kaise", "register kaise", "आवेदन कैसे करें", "फॉर्म कैसे भरें",
            "कहाँ आवेदन करें", "आधिकारिक पोर्टल",
        ]
        if any(w in t for w in apply_keywords):
            return IntentAnalysis(
                intent="application_guidance",
                language=lang,
                requires_profile=False,
            )

        # 6. ELIGIBILITY CHECK (Prioritize before generic follow-up)
        eligibility_keywords = [
            "eligible", "eligibility", "am i eligible", "qualify",
            "conditions do i need", "why am i not eligible", "check my eligibility",
            "eligibility conditions", "eligibility criteria", "what are the eligibility",
            "patrata", "patra", "yogyata", "jaanchi", "jaanch", "check karo",
            "what if i do not own", "what if i don't have", "without land", "no land",
            "landless", "zameen nahi", "bhoomiheen", "पात्र", "पात्रता", "क्या मैं पात्र हूँ",
            "मेरी पात्रता", "पात्रता शर्तें",
        ]
        has_eligibility_keyword = any(w in t for w in eligibility_keywords)
        can_i_apply = "can i apply" in t and "how" not in t
        if has_eligibility_keyword or can_i_apply or "क्या मैं आवेदन कर सकता हूँ" in t:
            return IntentAnalysis(
                intent="eligibility_check",
                language=lang,
                requires_profile=True,
                requires_scheme_search=False,
                requires_eligibility_check=True,
            )

        # 7. DOCUMENT ASSISTANCE / MISSING DOCUMENTS (Prioritize before generic follow-up)
        doc_keywords = [
            "document", "documents", "dastavez", "certificate", "marksheet",
            "income certificate", "caste certificate", "passbook", "missing document",
            "don't have", "do not have", "obtain", "दस्तावेज़", "कागजात", "प्रमाण पत्र",
            "आय प्रमाण पत्र", "जाति प्रमाण पत्र", "पासबुक",
        ]
        if any(w in t for w in doc_keywords):
            return IntentAnalysis(
                intent="document_assistance",
                language=lang,
                requires_profile=True,
                requires_document_check=True,
            )

        # 8. SCHEME INFORMATION (Specific named scheme inquiries or 'What is <Scheme>')
        known_scheme_signals = [
            "pm-kisan", "pmkisan", "किसान सम्मान निधि",
            "post matric", "post-matric", "पोस्ट मैट्रिक",
            "ladli behna", "ladli bahna", "लाड़ली बहना", "लाडली बहना",
            "pmay", "pmay-g", "pm awas", "आवास योजना",
            "ujjwala", "उज्ज्वला",
            "vishwakarma", "विश्वकर्मा",
            "ayushman", "pm-jay", "pmjay", "आयुष्मान",
            "pmkvy", "kaushal vikas",
            "pmegp",
        ]
        has_known_scheme = any(s in t for s in known_scheme_signals)
        scheme_benefit_signal = any(b in t for b in ["what are its benefits", "what benefits", "benefits kya", "ke benefits", "के लाभ", "इसके लाभ"])

        # Check explicit scheme phrase (e.g., "Tell me about XYZ Scholarship Scheme", "XYZ scheme details")
        scheme_term_present = any(w in t for w in ["scheme", "schemes", "scholarship", "scholarships", "yojana", "yojna", "योजना", "छात्रवृत्ति", "कल्याण"])
        inquiry_starter = any(t.startswith(prefix) for prefix in ["tell me about ", "what is ", "explain ", "details of ", "information on ", "info about "])
        is_unknown_scheme_inquiry = inquiry_starter and scheme_term_present

        if has_known_scheme or scheme_benefit_signal or is_unknown_scheme_inquiry or "पीएम किसान क्या है" in t or "लाड़ली बहना क्या है" in t or "आयुष्मान भारत क्या है" in t:
            return IntentAnalysis(
                intent="scheme_information",
                language=lang,
                requires_profile=False,
                requires_scheme_search=False,
            )

        # 9. SCHEME FOLLOW-UP (Referring to previous conversation items)
        followup_patterns = [
            "first one", "first scheme", "second one", "second scheme", "third one",
            "the first", "the second", "explain this one", "tell me about that",
            "पहला वाला", "पहली योजना", "दूसरा वाला", "दूसरी योजना", "इसके बारे में बताओ",
            "first scholarship", "second scholarship",
        ]
        if any(p in t for p in followup_patterns) and history:
            return IntentAnalysis(
                intent="scheme_follow_up",
                language=lang,
                requires_profile=True,
                requires_scheme_search=False,
            )

        # 10. SCHEME DISCOVERY (Finding and exploring schemes across categories)
        discovery_keywords = [
            "scholarship", "scholarships", "scheme", "schemes", "find", "show", "list",
            "farmer", "farmers", "women", "student", "students", "housing", "awas",
            "unemployed", "job", "jobs", "skill", "skills", "kaushal", "training",
            "business", "self-employed", "madhya pradesh", "central government",
            "healthcare", "health", "hospital", "pension", "bpl", "kisan", "ladli",
            "छात्रवृत्ति", "योजना", "योजनाएं", "दिखाओ", "बताओ", "खोजो", "किसान", "महिला",
            "बेरोजगार", "रोजगार", "कौशल", "स्वरोजगार", "स्वास्थ्य", "आवास", "पेंशन",
        ]
        welfare_signals = [
            "scholarship", "scheme", "farmer", "kisan", "housing", "awas", "health",
            "women", "student", "unemployed", "skill", "kaushal", "pension", "bpl",
            "ladli", "yojana", "yojna", "छात्रवृत्ति", "योजना", "किसान", "महिला", "आवास", "स्वास्थ्य",
        ]
        if any(w in t for w in discovery_keywords) and any(w in t for w in welfare_signals):
            return IntentAnalysis(
                intent="scheme_discovery",
                language=lang,
                requires_profile=True,
                requires_scheme_search=True,
            )

        # 11. STRICT SCOPE ENFORCEMENT - OUT OF SCOPE DEFAULT
        return IntentAnalysis(
            intent="out_of_scope",
            language=lang,
            requires_profile=False,
            requires_scheme_search=False,
            requires_eligibility_check=False,
            requires_document_check=False,
        )

    def _resolve_target_scheme(
        self, query: str, profile: dict[str, Any], history: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Resolve target scheme from text, aliases, or prior conversation context."""
        q = query.lower()

        # 1. Scheme name in text
        if any(w in q for w in ["pm-kisan", "pmkisan", "किसान सम्मान निधि"]) or ("kisan" in q and ("pm" in q or "सम्मान" in q or "scheme" in q)):
            return scheme_retrieval_service.get_scheme_by_id("pm-kisan")
        if any(w in q for w in ["post-matric", "post matric", "पोस्ट मैट्रिक"]):
            return scheme_retrieval_service.get_scheme_by_id("post-matric-scholarship")
        if any(w in q for w in ["ladli", "behna", "लाड़ली", "बहना", "mp women"]):
            return scheme_retrieval_service.get_scheme_by_id("ladli-behna-mp")
        if any(w in q for w in ["pmay", "pmay-g", "pm awas", "आवास योजना", "प्रधानमंत्री आवास"]):
            return scheme_retrieval_service.get_scheme_by_id("pmay-g")
        if any(w in q for w in ["ujjwala", "उज्ज्वला"]):
            return scheme_retrieval_service.get_scheme_by_id("pm-ujjwala")
        if any(w in q for w in ["vishwakarma", "विश्वकर्मा"]):
            return scheme_retrieval_service.get_scheme_by_id("pm-vishwakarma")
        if any(w in q for w in ["ayushman", "pm-jay", "pmjay", "आयुष्मान"]):
            return scheme_retrieval_service.get_scheme_by_id("ayushman-bharat")
        if any(w in q for w in ["pmkvy", "kaushal vikas", "कौशल विकास"]):
            return scheme_retrieval_service.get_scheme_by_id("pmkvy")
        if any(w in q for w in ["pmegp"]):
            return scheme_retrieval_service.get_scheme_by_id("pmegp")

        # 2. Check previous conversation turns for ordinal references ("first one", "second one", "first scholarship")
        last_schemes = self._get_last_assistant_schemes(history)
        if last_schemes:
            if any(w in q for w in ["first", "1st", "पहला", "पहली"]):
                return scheme_retrieval_service.get_scheme_by_id(last_schemes[0].get("scheme_id", ""))
            if len(last_schemes) > 1 and any(w in q for w in ["second", "2nd", "दूसरा", "दूसरी"]):
                return scheme_retrieval_service.get_scheme_by_id(last_schemes[1].get("scheme_id", ""))
            if len(last_schemes) > 2 and any(w in q for w in ["third", "3rd", "तीसरा", "तीसरी"]):
                return scheme_retrieval_service.get_scheme_by_id(last_schemes[2].get("scheme_id", ""))
            # Default reference like "this scheme" or "it"
            if any(w in q for w in ["this", "that", "it", "इस", "यह"]):
                return scheme_retrieval_service.get_scheme_by_id(last_schemes[0].get("scheme_id", ""))

        # 3. Check last target scheme recorded in assistant history
        last_target_id = self._get_last_assistant_target_id(history)
        if last_target_id:
            return scheme_retrieval_service.get_scheme_by_id(last_target_id)

        # 4. If query explicitly asks about an unknown named scheme (e.g., "XYZ Scholarship Scheme"), do not fallback to profile
        if any(w in q for w in ["tell me about", "what is", "explain", "scheme", "scholarship", "yojana", "योजना", "छात्रवृत्ति"]):
            return None

        # 4. Contextual fallback based on active profile occupation/gender
        occ = profile.get("occupation", "")
        if occ == "farmer":
            return scheme_retrieval_service.get_scheme_by_id("pm-kisan")
        if occ == "student":
            return scheme_retrieval_service.get_scheme_by_id("post-matric-scholarship")
        if occ in ("unemployed", "jobseeker"):
            return scheme_retrieval_service.get_scheme_by_id("pmkvy")
        if occ in ("self-employed", "business"):
            return scheme_retrieval_service.get_scheme_by_id("pmegp")
        if profile.get("gender") == "female" and profile.get("state") == "MP":
            return scheme_retrieval_service.get_scheme_by_id("ladli-behna-mp")

        return None

    def _get_last_assistant_schemes(self, history: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Retrieve schemes returned in the most recent assistant message."""
        for msg in reversed(history):
            if msg.get("role") == "assistant" and msg.get("schemes"):
                return msg["schemes"]
        return []

    def _get_last_assistant_target_id(self, history: list[dict[str, Any]]) -> str | None:
        """Retrieve target scheme ID from the most recent assistant message."""
        for msg in reversed(history):
            if msg.get("role") == "assistant":
                if msg.get("target_scheme_id"):
                    return msg["target_scheme_id"]
                if msg.get("schemes") and len(msg["schemes"]) > 0:
                    first = msg["schemes"][0]
                    if isinstance(first, dict):
                        return first.get("scheme_id") or first.get("id")
        return None

    def _to_card(self, scheme: dict[str, Any], lang: str, reason: str | None = None) -> SchemeCardData:
        """Convert catalog scheme to frontend SchemeCardData."""
        name_dict = scheme.get("name", {})
        benefits_dict = scheme.get("benefits", {})
        return SchemeCardData(
            scheme_id=scheme["id"],
            code=scheme.get("code", scheme["id"]),
            name=name_dict.get(lang, name_dict.get("en", scheme["id"])),
            category=scheme.get("category", "general"),
            level=scheme.get("level", "central"),
            benefits_summary=benefits_dict.get(lang, benefits_dict.get("en", "")),
            official_url=scheme.get("official_url"),
            match_reason=reason or "Verified government scheme.",
        )

    def _handle_general_conversation(self, query: str, lang: str) -> str:
        """Concise direct responses for general conversation queries."""
        q = query.lower()
        if "can you speak hindi" in q or "हिंदी बोल सकते" in q:
            return (
                "हाँ, मैं हिन्दी और English दोनों भाषाओं में पूरी तरह सहायता कर सकता हूँ। "
                "आप किसी भी सरकारी योजना, छात्रवृत्ति या पात्रता के बारे में अपनी भाषा में पूछ सकते हैं।"
                if lang == "hi"
                else "Yes, I can communicate fluently in both Hindi and English. Feel free to ask about any government scheme in your preferred language."
            )
        if "what is sahayak" in q or "who is sahayak" in q or "what is shayak" in q or "who is shayak" in q or "सहायक क्या है" in q or "सहायक कौन है" in q or "शायक क्या है" in q or "शायक कौन है" in q:
            return (
                "सहायक (Sahayak) योजना मित्र मंच पर एक AI-सक्षम सरकारी योजना सहायक है। "
                "यह नागरिकों को उनकी व्यक्तिगत प्रोफ़ाइल के आधार पर केंद्र व राज्य सरकार की योजनाएं खोजने, "
                "पात्रता जांचने, आवश्यक दस्तावेज़ समझने और आधिकारिक पोर्टल से आवेदन करने में सहायता करता है।"
                if lang == "hi"
                else "Sahayak is an AI-powered Indian Government Scheme Assistant on the YojanaMitra platform. It helps citizens discover Central and State welfare schemes, check eligibility through deterministic rules, identify required documents, and access verified application links."
            )
        if "what is yojanamitra" in q or "योजना मित्र क्या है" in q:
            return (
                "योजना मित्र (YojanaMitra) एक AI-सक्षम सरकारी योजना मंच है, और मैं सहायक (Sahayak) इस पर आपका वर्चुअल सहायक हूँ। "
                "यह नागरिकों को उनकी व्यक्तिगत प्रोफ़ाइल के आधार पर केंद्र व राज्य सरकार की योजनाएं खोजने, "
                "पात्रता जांचने, आवश्यक दस्तावेज़ समझने और आधिकारिक पोर्टल से आवेदन करने में सहायता करता है।"
                if lang == "hi"
                else "YojanaMitra is an AI-powered Indian Government Scheme discovery platform, and I am Sahayak, your virtual assistant here to guide you through welfare schemes, verify eligibility, and help you prepare documents."
            )
        if "how can you help students" in q or "छात्रों" in q:
            return (
                "मैं विद्यार्थियों को उनकी शैक्षणिक श्रेणी और पारिवारिक आय के अनुसार छात्रवृत्तियां (जैसे पोस्ट-मैट्रिक छात्रवृत्ति) खोजने, "
                "पात्रता जांचने, आवश्यक दस्तावेज़ (अंकसूची, आय प्रमाण पत्र) समझने और राष्ट्रीय छात्रवृत्ति पोर्टल (NSP) पर आवेदन करने में सहायता करता हूँ।"
                if lang == "hi"
                else "I help students discover government scholarships (such as the Post-Matric Scholarship Scheme), verify eligibility based on family income and course level, review required academic and category documents, and provide official National Scholarship Portal (NSP) guidance."
            )
        if "who are you" in q or "what can you do" in q or "आप कौन हैं" in q or "क्या कर सकते" in q or "who made you" in q:
            return (
                "मैं सहायक (Sahayak) हूँ, आपका AI-सक्षम सरकारी योजना सहायक। मैं आपको छात्रवृत्ति, किसान सहायता (PM-KISAN), आवास योजना (PMAY), "
                "महिला कल्याण, और स्वास्थ्य बीमा (आयुष्मान भारत) योजनाओं की जानकारी, पात्रता सत्यापन और आधिकारिक आवेदन लिंक प्रदान कर सकता हूँ।"
                if lang == "hi"
                else "I am Sahayak, your AI-powered Indian Government Scheme Assistant. I can help you discover Central and State welfare schemes (scholarships, farming, housing, healthcare), verify eligibility criteria, prepare required documents, and guide your online application."
            )
        if "are you an ai" in q or "एआई" in q:
            return (
                "हाँ, मैं सहायक (Sahayak) AI सहायक हूँ। मेरा उद्देश्य हर भारतीय नागरिक के लिए सरकारी योजनाओं की जानकारी को सरल और सुलभ बनाना है।"
                if lang == "hi"
                else "Yes, I am Sahayak, an AI assistant developed to make Indian Government schemes and welfare benefits easy to understand and accessible for every citizen."
            )
        # Default concise greeting/help
        return (
            "सहायक (Sahayak) में आपका स्वागत है। आप छात्रवृत्ति, किसान सहायता, आवास या स्वास्थ्य योजनाओं के बारे में पूछ सकते हैं।"
            if lang == "hi"
            else "Welcome to Sahayak. You can ask me about scholarships, farmer support, rural housing, or healthcare schemes."
        )

    def _handle_profile_inquiry(self, profile: dict[str, Any], lang: str) -> str:
        """Explain active citizen profile details without leaking private identifiers."""
        if not profile:
            return (
                "वर्तमान में आपकी प्रोफ़ाइल में कोई जानकारी दर्ज नहीं है। आप होमपेज पर 10-प्रश्नों की प्रश्नावली पूरी करके अपनी प्रोफ़ाइल सहेज सकते हैं।"
                if lang == "hi"
                else "No profile data is currently stored in your active session. You can complete the 10-question screening on the homepage to personalize your scheme recommendations."
            )
        parts = []
        if profile.get("state"):
            parts.append(f"राज्य: {profile['state']}" if lang == "hi" else f"State: {profile['state']}")
        if profile.get("occupation"):
            parts.append(f"व्यवसाय: {profile['occupation']}" if lang == "hi" else f"Occupation: {profile['occupation']}")
        if profile.get("annual_income") is not None:
            parts.append(f"वार्षिक आय: ₹{int(profile['annual_income']):,}" if lang == "hi" else f"Annual Income: ₹{int(profile['annual_income']):,}")
        if profile.get("owns_agricultural_land") is not None:
            land_val = "हाँ" if profile["owns_agricultural_land"] else "नहीं"
            parts.append(f"कृषि भूमि: {land_val}" if lang == "hi" else f"Agricultural Land: {'Yes' if profile['owns_agricultural_land'] else 'No'}")

        summary = " | ".join(parts)
        if lang == "hi":
            return f"आपकी सक्रिय सत्र प्रोफ़ाइल जानकारी: **{summary}**। इस जानकारी का उपयोग आपकी योजना पात्रता जांचने के लिए किया जाता है।"
        return f"Your active session profile: **{summary}**. This profile context is used to evaluate your scheme eligibility."

    def _handle_specific_document_query(self, query: str, lang: str) -> str | None:
        """Provide detailed, trustworthy guidance on obtaining specific missing documents."""
        q = query.lower()
        if "income certificate" in q or "आय प्रमाण पत्र" in q:
            return (
                "**आय प्रमाण पत्र (Income Certificate) प्राप्त करने की प्रक्रिया:**\n"
                "1. **कहाँ जाएं:** अपने स्थानीय तहसील कार्यालय अथवा राज्य के ई-डिस्ट्रिक्ट (e-District / लोक सेवा केंद्र) पोर्टल पर जाएं।\n"
                "2. **आवश्यक दस्तावेज़:** आधार कार्ड, राशन कार्ड/निवास प्रमाण, और स्व-घोषणा पत्र (Affidavit) अथवा वेतन पर्ची।\n"
                "3. **समय सीमा:** आवेदन के 7 से 15 दिनों के भीतर तहसीलदार/सक्षम प्राधिकारी द्वारा डिजिटल रूप से हस्ताक्षरित प्रमाण पत्र जारी किया जाता है।"
                if lang == "hi"
                else "**How to Obtain an Income Certificate:**\n"
                "1. **Where to Apply:** Visit your local Tehsil Revenue Office or your state's online e-District / Lok Seva Kendra portal.\n"
                "2. **Documents Needed:** Aadhaar Card, Ration Card / Address Proof, and an Income Affidavit / Salary Slip.\n"
                "3. **Timeline:** Digitally signed by the Tehsildar/Revenue Officer within 7-15 business days."
            )
        if "caste certificate" in q or "जाति प्रमाण पत्र" in q:
            return (
                "**जाति प्रमाण पत्र (Caste Certificate) प्राप्त करने की प्रक्रिया:**\n"
                "1. **कहाँ जाएं:** अनुविभागीय अधिकारी (SDM) / तहसीलदार कार्यालय अथवा राज्य ई-डिस्ट्रिक्ट पोर्टल पर आवेदन करें।\n"
                "2. **आवश्यक दस्तावेज़:** आधार कार्ड, पिता का जाति प्रमाण पत्र या 1950/1984 से पहले का भूमि/राजस्व रिकॉर्ड, और मूल निवास प्रमाण पत्र।\n"
                "3. **सत्यापन:** राजस्व निरीक्षक/पटवारी द्वारा स्थानीय सत्यापन के पश्चात डिजिटल प्रमाण पत्र प्राप्त होता है।"
                if lang == "hi"
                else "**How to Obtain a Caste Certificate:**\n"
                "1. **Where to Apply:** Apply through your Sub-Divisional Magistrate (SDM) / Tehsildar office or state e-District portal.\n"
                "2. **Documents Needed:** Aadhaar Card, Father's Caste Certificate or ancestral land record prior to cut-off year, and Domicile proof.\n"
                "3. **Timeline:** Issued upon revenue inspection/Patwari verification within 15-30 days."
            )
        return None

    def _evaluate_deterministic_eligibility(
        self, scheme: dict[str, Any], profile: dict[str, Any], lang: str
    ) -> EligibilityCardData:
        """Deterministic rule evaluator. AI never makes final eligibility determinations."""
        scheme_id = scheme["id"]
        scheme_name = scheme["name"].get(lang, scheme["name"]["en"])

        breakdown: list[CriterionEvaluationItem] = []
        is_eligible = True
        needs_verification = False

        if scheme_id == "pm-kisan":
            owns_land = profile.get("owns_agricultural_land")
            if owns_land is False:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Cultivable Land Ownership",
                    satisfied=False,
                    explanation="Requires cultivable agricultural land registered in revenue records."
                ))
                is_eligible = False
            elif owns_land is True:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Cultivable Land Ownership",
                    satisfied=True,
                    explanation="You reported owning agricultural land."
                ))
            else:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Cultivable Land Ownership",
                    satisfied=False,
                    explanation="Land ownership status is not specified in profile."
                ))
                needs_verification = True

            is_taxpayer = profile.get("pays_income_tax")
            if is_taxpayer is True:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Non-Taxpaying Household",
                    satisfied=False,
                    explanation="Families with an income tax-paying member are excluded."
                ))
                is_eligible = False
            else:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Non-Taxpaying Household",
                    satisfied=True,
                    explanation="No household member filed income tax."
                ))

        elif scheme_id == "post-matric-scholarship":
            occ = profile.get("occupation")
            is_student = occ == "student" or profile.get("education_level") is not None
            breakdown.append(CriterionEvaluationItem(
                criterion_name="Enrolled in Post-Matric / Higher Education",
                satisfied=is_student,
                explanation="Applicable for students enrolled in Class 11, B.Tech, Degree, or Diploma programs."
            ))
            if not is_student:
                is_eligible = False

            income = profile.get("annual_income")
            if income is not None and income > 250000:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Annual Household Income <= ₹2.5 Lakhs",
                    satisfied=False,
                    explanation=f"Your annual income (₹{int(income):,}) exceeds the ₹2.5 Lakhs threshold."
                ))
                is_eligible = False
            else:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Annual Household Income <= ₹2.5 Lakhs",
                    satisfied=True,
                    explanation="Annual family income satisfies the required economic ceiling."
                ))

        elif scheme_id == "ladli-behna-mp":
            gender = profile.get("gender")
            if gender and gender.lower() == "male":
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Female Applicant",
                    satisfied=False,
                    explanation="This scheme is strictly for women applicants."
                ))
                is_eligible = False
            else:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Female Applicant",
                    satisfied=True,
                    explanation="Applicant matches the required gender."
                ))

            state = profile.get("state")
            if state and state.upper() != "MP":
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Permanent Resident of Madhya Pradesh",
                    satisfied=False,
                    explanation="Exclusively for permanent residents of Madhya Pradesh."
                ))
                is_eligible = False
            else:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Permanent Resident of Madhya Pradesh",
                    satisfied=True,
                    explanation="Requires Samagra ID and MP resident verification."
                ))
                needs_verification = True

        elif scheme_id == "pmay-g":
            area = profile.get("area_type")
            if area and area.lower() == "urban":
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Rural Resident",
                    satisfied=False,
                    explanation="PMAY-G is for rural village residents. For cities, check PMAY-Urban."
                ))
                is_eligible = False
            else:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Rural Resident",
                    satisfied=True,
                    explanation="Resident of rural Gram Panchayat area."
                ))

            housing = profile.get("housing_type")
            if housing and housing.lower() == "pucca":
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Kutcha / Homeless Deprivation",
                    satisfied=False,
                    explanation="Families owning pucca concrete houses are not eligible."
                ))
                is_eligible = False
            else:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Kutcha / Homeless Deprivation",
                    satisfied=True,
                    explanation="Satisfies primary housing deprivation criteria."
                ))

        elif scheme_id == "pmkvy":
            age = profile.get("age")
            if age is not None and (age < 15 or age > 45):
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Age Eligibility (15-45 Years)",
                    satisfied=False,
                    explanation=f"Your age ({age}) is outside the 15-45 years guideline."
                ))
                is_eligible = False
            else:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Age Eligibility (15-45 Years)",
                    satisfied=True,
                    explanation="Meets standard youth skill age requirements."
                ))

            breakdown.append(CriterionEvaluationItem(
                criterion_name="Aadhaar-Linked Candidate",
                satisfied=True,
                explanation="Valid for any unemployed youth or jobseeker with Aadhaar e-KYC."
            ))

        elif scheme_id == "pmegp":
            age = profile.get("age")
            if age is not None and age < 18:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Minimum Age 18 Years",
                    satisfied=False,
                    explanation="Must be at least 18 years of age to apply for PMEGP business loans."
                ))
                is_eligible = False
            else:
                breakdown.append(CriterionEvaluationItem(
                    criterion_name="Minimum Age 18 Years",
                    satisfied=True,
                    explanation="Satisfies adult entrepreneur age criteria."
                ))

            breakdown.append(CriterionEvaluationItem(
                criterion_name="New Project / Enterprise",
                satisfied=True,
                explanation="Applicable for setting up new manufacturing or service micro-enterprises."
            ))

        # Overall Status Computation
        if not is_eligible:
            final_status = "NOT_ELIGIBLE"
            conf = 0.95
            summary_msg = f"You do not meet one or more mandatory eligibility requirements for {scheme_name}."
        elif needs_verification:
            final_status = "NEEDS_VERIFICATION"
            conf = 0.70
            summary_msg = f"You satisfy initial profile checks for {scheme_name}, but local revenue/document verification is required."
        else:
            final_status = "POTENTIALLY_ELIGIBLE"
            conf = 0.90
            summary_msg = f"Based on your profile responses, you appear eligible for {scheme_name} under standard guidelines."

        return EligibilityCardData(
            scheme_id=scheme_id,
            scheme_name=scheme_name,
            status=final_status,
            confidence_score=conf,
            summary_explanation=summary_msg,
            criteria_breakdown=breakdown,
        )

    def _analyze_missing_documents(
        self, scheme: dict[str, Any], profile: dict[str, Any], lang: str
    ) -> list[DocumentCheckItem]:
        """Analyze document requirements against citizen profile data."""
        docs = scheme.get("required_documents", [])
        results: list[DocumentCheckItem] = []

        for d in docs:
            d_name = d["name"]
            status = "NEEDS_VERIFICATION"

            if "aadhaar" in d_name.lower():
                status = "AVAILABLE"
            elif "income" in d_name.lower():
                status = "AVAILABLE" if profile.get("annual_income") else "MISSING"
            elif "caste" in d_name.lower():
                status = "AVAILABLE" if profile.get("caste_category") in ("sc", "st", "obc") else "NOT_APPLICABLE"
            elif "land" in d_name.lower():
                status = "AVAILABLE" if profile.get("owns_agricultural_land") else "MISSING"
            elif "samagra" in d_name.lower():
                status = "AVAILABLE" if profile.get("state") == "MP" else "MISSING"
            else:
                status = "MISSING"

            results.append(DocumentCheckItem(
                document_name=d_name,
                is_required=True,
                status=status,
                purpose=d.get("purpose"),
                where_to_obtain=d.get("where_to_obtain"),
                official_portal_url=scheme.get("official_url"),
            ))

        return results

    def _get_application_guidance(self, scheme: dict[str, Any], lang: str) -> ApplicationGuidanceData:
        """Extract step-by-step verified application guidance."""
        instructions = scheme.get("application_instructions", {})
        steps = instructions.get("steps", [
            "Visit the official government portal.",
            "Complete online registration with Aadhaar e-KYC.",
            "Upload verified document proofs and submit for nodal verification."
        ])
        req_docs = [d["name"] for d in scheme.get("required_documents", [])]

        return ApplicationGuidanceData(
            scheme_id=scheme["id"],
            scheme_name=scheme["name"].get(lang, scheme["name"]["en"]),
            mode=instructions.get("mode", "both"),
            official_portal_url=scheme.get("official_url"),
            steps=steps,
            documents_needed=req_docs,
            caution_notes=[instructions.get("caution", "Government scheme application is free. Never pay unofficial agents.")],
        )


chatbot_service = ChatbotService()
