"""Profile Context Service for YojanaMitra AI Chatbot.
Extracts and sanitizes citizen profile information for intelligent personalization.
Strictly respects Zero-Persistence privacy: never stores or forwards personal identifiers (names, Aadhaar).
"""
from typing import Any
from app.schemas.chatbot import ChatProfileContext


class ProfileContextService:
    """Safely extracts and formats profile context for the chatbot."""

    def build_context_summary(self, profile: ChatProfileContext | None) -> dict[str, Any]:
        """Convert profile model into a sanitized context dictionary for AI personalization."""
        if not profile:
            return {"has_profile": False, "summary_text": "No citizen profile provided."}

        parts: list[str] = []
        if profile.state:
            parts.append(f"State: {profile.state.upper()}")
        if profile.area_type:
            parts.append(f"Area: {profile.area_type.title()}")
        if profile.age is not None:
            parts.append(f"Age: {profile.age} years")
        if profile.gender:
            parts.append(f"Gender: {profile.gender.title()}")
        if profile.occupation:
            parts.append(f"Occupation: {profile.occupation.replace('_', ' ').title()}")
        if profile.education_level:
            parts.append(f"Education: {profile.education_level.title()}")
        if profile.annual_income is not None:
            parts.append(f"Annual Income: ₹{int(profile.annual_income):,}")
        if profile.caste_category:
            parts.append(f"Category: {profile.caste_category.upper()}")
        if profile.owns_agricultural_land is not None:
            parts.append(f"Owns Agricultural Land: {'Yes' if profile.owns_agricultural_land else 'No'}")
        if profile.housing_type:
            parts.append(f"Housing: {profile.housing_type.replace('_', ' ').title()}")
        if profile.has_bpl_card:
            parts.append("Holds BPL/Antyodaya Ration Card: Yes")
        if profile.has_existing_lpg is not None:
            parts.append(f"Has Active LPG Connection: {'Yes' if profile.has_existing_lpg else 'No'}")
        if profile.pays_income_tax is not None:
            parts.append(f"Household Pays Income Tax: {'Yes' if profile.pays_income_tax else 'No'}")

        summary = "; ".join(parts) if parts else "Anonymous citizen profile."
        return {
            "has_profile": bool(parts),
            "summary_text": summary,
            "profile_data": profile.model_dump(exclude_none=True),
        }


profile_context_service = ProfileContextService()

