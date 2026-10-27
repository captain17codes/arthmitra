from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class BaseLLMAdapter(ABC):
    """Abstract interface for LLM Advisory generation."""

    @abstractmethod
    async def generate_advisory_text(
        self,
        facts: dict[str, Any],
        language: str = "mr",
        retry_feedback: str | None = None,
    ) -> dict[str, Any]:
        """Generate structured advisory JSON grounded strictly in provided facts."""
        pass


class MockLLMAdapter(BaseLLMAdapter):
    """
    Deterministic Mock LLM Adapter for testing and offline execution.
    Produces valid JSON strictly following the advisory schema.
    """

    def __init__(self, should_inject_bad_number: bool = False):
        self.should_inject_bad_number = should_inject_bad_number

    async def generate_advisory_text(
        self,
        facts: dict[str, Any],
        language: str = "mr",
        retry_feedback: str | None = None,
    ) -> dict[str, Any]:
        village = facts.get("village_name", "गावात")
        biz_name = facts.get("business_name", {}).get("mr", "व्यवसाय")

        # Bad number injection for testing validator
        injected_bad_val = 999999.0 if self.should_inject_bad_number else None

        res: dict[str, Any]
        if language == "mr":
            res = {
                "market_reach": f"{village} मध्ये {biz_name} साठी ग्राहकांची चांगली मागणी आहे.",
                "opportunities": [
                    "स्थानिक ग्राहकांना नियमित दर्जेदार माल पुरवणे.",
                    "शासकीय योजनेचा आर्थिक लाभ घेऊन वेळेत कर्जफेड करणे.",
                ],
                "swot": {
                    "s": ["मजबूत व्यावसायिक मागणी", "स्थानिक उपस्थिती"],
                    "w": ["खेळत्या भांडवलाची गरज"],
                    "o": ["बाजारपेठेचा विस्तार"],
                    "t": ["स्थानिक स्पर्धा"],
                },
                "threats": [
                    {
                        "risk": "उधार विक्री वाढणे",
                        "type": "financial",
                        "mitigation": "उधार २०% पेक्षा कमी ठेवणे",
                    }
                ],
                "pricing": {
                    "strategy": "स्थानिक चालू दराप्रमाणे वाजवी किंमत आकारणे.",
                    "items": [
                        {
                            "item": "मुख्य उत्पादन",
                            "benchmark_price": "स्थानिक दर",
                            "unit": "नग",
                            "rationale": "ग्राहकांना परवडणारे दर",
                        }
                    ],
                },
                "complementary": ["पूरक कृषी प्रक्रिया किंवा शेळीपालन"],
                "next_steps": [
                    "१. बँक डीपीआर पूर्ण करणे.",
                    "२. मार्जिन रक्कम तयार ठेवणे.",
                    "३. बँकेत अर्ज दाखल करणे.",
                ],
            }
        else:
            res = {
                "market_reach": f"In {village}, there is steady demand for {biz_name}.",
                "opportunities": [
                    "Provide reliable service to local village households.",
                    "Utilize government scheme benefits to maintain financial discipline.",
                ],
                "swot": {
                    "s": ["Strong local market presence", "Accessible location"],
                    "w": ["Initial working capital monitoring required"],
                    "o": ["Market expansion across neighbouring villages"],
                    "t": ["Local price competition"],
                },
                "threats": [
                    {
                        "risk": "Customer credit expansion",
                        "type": "financial",
                        "mitigation": "Cap credit sales to 20% of monthly turnover",
                    }
                ],
                "pricing": {
                    "strategy": "Competitive pricing aligned with local benchmarks.",
                    "items": [
                        {
                            "item": "Primary Service",
                            "benchmark_price": "Local benchmark",
                            "unit": "unit",
                            "rationale": "Ensures customer uptake and positive gross margin",
                        }
                    ],
                },
                "complementary": ["Allied livestock and small retail"],
                "next_steps": [
                    "1. Finalize documentation and DPR.",
                    "2. Ensure promoter margin is available.",
                    "3. Submit formal application to the bank.",
                ],
            }

        if injected_bad_val is not None:
            res["market_reach"] = str(res["market_reach"]) + f" Unauthorized estimate: ₹{injected_bad_val:,.0f}."

        return res


class GeminiLLMAdapter(BaseLLMAdapter):
    """Adapter connecting to Google Gemini REST API with retry and timeouts."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        )

    async def generate_advisory_text(
        self,
        facts: dict[str, Any],
        language: str = "mr",
        retry_feedback: str | None = None,
    ) -> dict[str, Any]:
        prompt = (
            f"You are ArthMitra, an expert rural enterprise financial advisor in Maharashtra.\n"
            f"LANGUAGE: Respond in {language} (Marathi if 'mr', English if 'en', Hindi if 'hi').\n"
            f"CRITICAL RULE: You MUST ONLY use the provided facts. DO NOT invent, hallucinate, or calculate any new numbers.\n"
            f"FACTS:\n{json.dumps(facts, indent=2, ensure_ascii=False)}\n"
        )
        if retry_feedback:
            prompt += f"\nATTENTION PREVIOUS ATTEMPT FAILED NUMBER VALIDATION: {retry_feedback}\nDo not include any numbers outside the allowed numbers list.\n"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.endpoint, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_text)


def get_llm_adapter() -> BaseLLMAdapter:
    """Factory returning configured LLM adapter or fallback mock adapter."""
    if settings.gemini_api_key and settings.gemini_api_key.strip():
        return GeminiLLMAdapter(api_key=settings.gemini_api_key, model=settings.gemini_model)
    return MockLLMAdapter()
