from typing import Optional, List
from app.config import settings
from openai import OpenAI


class AIService:
    """
    Service for AI-generated responses using OpenAI API
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens

        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        self.client = OpenAI(api_key=self.api_key)

    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate AI response using OpenAI
        """

        try:
            full_prompt = prompt

            if context:
                full_prompt = f"Context: {context}\n\nUser: {prompt}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a compassionate and insightful quote recommendation assistant. "
                            "You help users find meaningful quotes based on their emotional state. "
                            "Keep responses warm, encouraging, and concise."
                        ),
                    },
                    {"role": "user", "content": full_prompt},
                ],
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    # --------------------------------------

    def generate_quote_explanation(self, quote_text: str, emotion: str) -> str:
        """
        Explain why a quote matches user's emotion
        """

        prompt = f"""
Explain why this quote might resonate with someone feeling {emotion}:

"{quote_text}"

Keep explanation empathetic and under 2 sentences.
"""

        return self.generate_response(prompt)

    # --------------------------------------

    def generate_follow_up_questions(self, user_input: str) -> List[str]:
        """
        Generate follow-up questions
        """

        prompt = f"""
User said: "{user_input}"

Generate 2-3 short follow-up questions to better understand their emotional state.
Return each question on a new line.
"""

        response = self.generate_response(prompt)

        questions = [
            q.strip().strip("•-").strip()
            for q in response.split("\n")
            if q.strip()
        ]

        return questions[:3]

    # --------------------------------------

    def enhance_chatbot_response(
        self,
        intent: str,
        detected_emotion: str,
        quote_text: str,
    ) -> str:
        """
        Generate personalized chatbot response
        """

        prompt = f"""
Someone is feeling {detected_emotion.lower()}.

They asked for a {intent.replace('_', ' ')} quote.

Include this quote naturally in your response:

"{quote_text}"

Respond warmly in 2-3 sentences.
"""

        return self.generate_response(prompt)

    # --------------------------------------

    def summarize_conversation(self, messages: List[str]) -> str:
        """
        Summarize conversation
        """

        conversation = "\n".join([f"- {msg}" for msg in messages])

        prompt = f"""
Summarize the emotional journey in this conversation in 2-3 sentences:

{conversation}
"""

        return self.generate_response(prompt, temperature=0.5)

    # --------------------------------------

    def health_check(self) -> bool:
        """
        Check OpenAI API connectivity
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )
            return True

        except Exception as e:
            print(f"OpenAI health check failed: {e}")
            return False


# Singleton instance
try:
    ai_service = AIService()
except Exception as e:
    print(f"Failed to initialize AI Service: {e}")
    ai_service = None