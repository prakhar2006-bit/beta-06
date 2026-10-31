"""FastAPI Router for YojanaMitra AI Chatbot."""
import io
import json
from typing import Annotated, Any
from fastapi import APIRouter, Depends, Header, Path, Query, Response
from fastapi.responses import StreamingResponse

from app.core.errors import APIError
from app.schemas.chatbot import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationHistoryResponse,
    SuggestedQuestionsResponse,
    VoiceStatusResponse,
    VoiceTTSRequest,
)
from app.schemas.schemes import ErrorResponse
from app.services.chatbot_service import chatbot_service
from app.services.elevenlabs_service import elevenlabs_service
from app.services.gemini_service import gemini_service

router = APIRouter(
    prefix="/api/v1/chatbot",
    tags=["Chatbot"],
    responses={
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)


@router.post("/message", response_model=ChatMessageResponse)
def send_chat_message(
    request: ChatMessageRequest,
    response: Response,
    x_session_id: Annotated[str | None, Header()] = None,
) -> ChatMessageResponse:
    """Send a message to YojanaMitra AI Assistant and receive an intelligent, personalized response."""
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"

    # Associate session header if not passed in body
    if x_session_id and not request.session_id:
        request.session_id = x_session_id

    try:
        return chatbot_service.process_message(request)
    except Exception as e:
        print(f"[ChatbotRoute] Error processing message: {e}")
        raise APIError(500, "CHATBOT_ERROR", "Failed to process chat message. Please try again.") from None


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: Annotated[str, Path(description="Conversation UUID")],
    response: Response,
) -> dict[str, Any]:
    """Retrieve history of an existing conversation."""
    response.headers["Cache-Control"] = "no-store"
    history = chatbot_service.get_conversation_history(conversation_id)
    return {
        "conversation_id": conversation_id,
        "total_messages": len(history),
        "messages": history,
    }


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: Annotated[str, Path(description="Conversation UUID")],
) -> dict[str, bool]:
    """Clear and delete an ephemeral conversation session."""
    success = chatbot_service.clear_conversation(conversation_id)
    return {"success": success, "deleted": True}


@router.get("/suggested-questions", response_model=SuggestedQuestionsResponse)
def get_suggested_questions(
    lang: Annotated[str, Query(description="Language code (en or hi)")] = "en",
) -> SuggestedQuestionsResponse:
    """Return localized suggested quick-start questions."""
    if lang == "hi":
        questions = [
            "मेरे लिए छात्रवृत्ति योजनाएं खोजें",
            "मेरी पात्रता की जांच करें",
            "इसके लिए कौन-से दस्तावेज़ चाहिए?",
            "छात्रों के लिए सरकारी योजनाएं दिखाएं",
            "मध्य प्रदेश की सरकारी योजनाएं दिखाएं",
        ]
    else:
        questions = [
            "Find scholarships for me",
            "Check my eligibility",
            "Which documents do I need?",
            "Show government schemes for students",
            "Find schemes available in my state",
        ]
    return SuggestedQuestionsResponse(language=lang, questions=questions)


@router.get("/status")
def get_chatbot_status() -> dict[str, Any]:
    """Return live availability and operational metadata for the chatbot."""
    return {
        "status": "online",
        "service": "Sahayak AI Assistant",
        "gemini_configured": gemini_service.is_configured(),
        "model": gemini_service.model_name,
        "languages_supported": ["en", "hi"],
        "features": [
            "scheme_discovery",
            "eligibility_engine",
            "missing_document_assistance",
            "application_guidance",
            "voice_assistant",
            "elevenlabs_tts",
        ],
    }


@router.post("/voice/tts")
def synthesize_voice_speech(
    request: VoiceTTSRequest,
    response: Response,
) -> Any:
    """Generate crystal clear, sweet female voice audio for Shayak Assistant using ElevenLabs.

    Returns streaming audio/mpeg if ElevenLabs is configured and succeeds,
    or a structured JSON fallback directing the browser to use Web SpeechSynthesis.
    """
    audio_bytes, sanitized = elevenlabs_service.synthesize_speech(
        text=request.text,
        lang=request.language or "en",
        voice_id=request.voice_id,
    )

    if audio_bytes:
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "public, max-age=86400",
                "X-Audio-Length": str(len(audio_bytes)),
            },
        )

    # Return graceful JSON fallback with sanitized speech text
    return Response(
        content=json.dumps({
            "success": False,
            "provider": "browser_fallback",
            "message": "ElevenLabs audio unavailable or unconfigured; use browser speech synthesis",
            "sanitized_text": sanitized,
            "language": request.language or "en",
        }),
        status_code=200,
        media_type="application/json",
    )


@router.get("/voice/status", response_model=VoiceStatusResponse)
def get_voice_status() -> VoiceStatusResponse:
    """Check configuration and voice details of Shayak's ElevenLabs voice engine."""
    status = elevenlabs_service.get_status()
    return VoiceStatusResponse(**status)
