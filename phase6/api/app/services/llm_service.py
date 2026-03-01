import os
from typing import List, Optional

import httpx
from dotenv import load_dotenv

from app.models.schemas import RecommendationRequest, RestaurantOut

# Try to load the GROQ_API_KEY from the project-level .env file.
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_DOTENV_PATH = os.path.join(_BASE_DIR, ".env")
load_dotenv(dotenv_path=_DOTENV_PATH, override=False)


class LLMService:
    """
    Simple service for calling Groq LLM.

    For Phase 4 we only use the model to generate a natural-language
    summary of the recommendations (no complex parsing).
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("GROQ_API_KEY")
        # This is a commonly used Groq model name; you can change it later if needed.
        self.model_name = "llama-3.1-8b-instant"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    def is_configured(self) -> bool:
        """
        Returns True if the API key is present in the environment.
        """
        return bool(self.api_key)

    async def generate_summary(
        self,
        preferences: RecommendationRequest,
        restaurants: List[RestaurantOut],
    ) -> Optional[str]:
        """
        Call Groq to generate a human-friendly summary of the recommendations.

        If GROQ_API_KEY is not set or the request fails, this method
        returns None and the rest of the API still works.
        """
        if not self.is_configured():
            return None

        if not restaurants:
            return None

        # Build a very simple, beginner-friendly prompt.
        prefs_text = (
            f"Location: {preferences.location}\n"
            f"Price range: {preferences.price_range}\n"
            f"Minimum rating: {preferences.min_rating}\n"
            f"Cuisine: {preferences.cuisine or 'any'}\n"
        )

        restaurants_lines = []
        for idx, r in enumerate(restaurants, start=1):
            restaurants_lines.append(
                f"{idx}. {r.name} - location: {r.location}, rating: {r.rating}, "
                f"price: {r.price}, cuisine: {r.cuisine}"
            )
        restaurants_text = "\n".join(restaurants_lines)

        user_prompt = (
            "The user is looking for restaurant recommendations with the preferences below.\n"
            "Then you see a list of recommended restaurants.\n"
            "Write a short, friendly summary (3–5 sentences) that explains why these are good options "
            "for the user. Do not invent restaurants; only talk about the ones in the list.\n\n"
            "User preferences:\n"
            f"{prefs_text}\n"
            "Recommended restaurants:\n"
            f"{restaurants_text}\n"
        )

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful restaurant recommendation assistant. "
                        "Be concise, friendly, and clear."
                    ),
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": 0.4,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

            choices = data.get("choices", [])
            if not choices:
                return None

            message = choices[0].get("message", {})
            content = message.get("content")
            if not content:
                return None

            return content.strip()
        except Exception:  # noqa: BLE001
            # For this beginner-friendly project we simply swallow errors
            # and let the rest of the system run without LLM output.
            return None

