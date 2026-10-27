from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


# Language mapping for Sarvam / Bhashini
LANG_MAP = {
    "mr": "mr-IN",
    "hi": "hi-IN",
    "en": "en-IN",
}


class BaseASRAdapter(ABC):
    """Abstract interface for Speech-to-Text / ASR providers."""

    @abstractmethod
    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str = "mr",
    ) -> dict[str, Any]:
        """
        Transcribe audio bytes to text.
        Returns: {
            "text": str,
            "confidence": float,
            "language": str,
            "provider": str,
        }
        """
        pass


class MockASRAdapter(BaseASRAdapter):
    """
    Deterministic Mock ASR Adapter for offline development and unit tests.
    Audio is processed without external network calls.
    """

    def __init__(self, preset_text: str | None = None, confidence: float = 0.95):
        self.preset_text = preset_text
        self.confidence = confidence

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str = "mr",
    ) -> dict[str, Any]:
        if self.preset_text:
            text = self.preset_text
        else:
            # Default fallback text by language
            if language == "mr":
                text = "दीड लाख रुपये"
            elif language == "hi":
                text = "डेढ़ लाख रुपये"
            else:
                text = "one lakh fifty thousand rupees"

        return {
            "text": text,
            "confidence": self.confidence,
            "language": language,
            "provider": "mock",
        }


class SarvamASRAdapter(BaseASRAdapter):
    """
    Production ASR adapter using Sarvam AI (leading Marathi/Hindi Indic speech model).
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_url: str | None = None,
        timeout: float = 12.0,
        max_retries: int = 2,
    ):
        self.api_key = api_key or settings.sarvam_api_key
        self.api_url = api_url or settings.sarvam_asr_url
        self.timeout = timeout
        self.max_retries = max_retries

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str = "mr",
    ) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("Sarvam API key not configured")

        lang_code = LANG_MAP.get(language, "mr-IN")
        headers = {
            "api-subscription-key": self.api_key,
        }
        files = {
            "file": (filename, audio_bytes, "audio/wav"),
        }
        data = {
            "language_code": lang_code,
            "model": "saaras:v1",
        }

        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(
                        self.api_url,
                        headers=headers,
                        files=files,
                        data=data,
                    )
                    resp.raise_for_status()
                    payload = resp.json()
                    transcript = payload.get("transcript", "").strip()
                    confidence = float(payload.get("confidence", 0.92))
                    return {
                        "text": transcript,
                        "confidence": confidence,
                        "language": language,
                        "provider": "sarvam",
                    }
            except Exception as e:
                last_exc = e
                logger.warning(
                    f"Sarvam ASR attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )

        raise RuntimeError(f"Sarvam ASR transcription failed: {last_exc}")


class BhashiniASRAdapter(BaseASRAdapter):
    """
    Fallback ASR adapter using Government of India Bhashini / IndicConformer pipeline.
    """

    def __init__(
        self,
        api_key: str | None = None,
        user_id: str | None = None,
        pipeline_id: str | None = None,
        timeout: float = 15.0,
    ):
        self.api_key = api_key or settings.bhashini_api_key
        self.user_id = user_id or settings.bhashini_user_id
        self.pipeline_id = pipeline_id or settings.bhashini_pipeline_id
        self.timeout = timeout

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str = "mr",
    ) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("Bhashini API key not configured")

        # Bhashini ULCA ASR pipeline invocation
        headers = {
            "Authorization": self.api_key,
            "userID": self.user_id,
            "Content-Type": "application/json",
        }
        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {"sourceLanguage": language},
                    },
                }
            ],
            "inputData": {
                "audio": [{"audioContent": audio_b64}],
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                "https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            res = resp.json()
            output_text = res["pipelineResponse"][0]["output"][0]["source"]
            return {
                "text": output_text,
                "confidence": 0.88,
                "language": language,
                "provider": "bhashini",
            }


class ResilientASRAdapter(BaseASRAdapter):
    """
    Composite resilient ASR adapter: tries primary provider (Sarvam),
    falls back to secondary (Bhashini), and falls back to deterministic mock if needed.
    """

    def __init__(
        self,
        primary: BaseASRAdapter,
        fallback: BaseASRAdapter | None = None,
    ):
        self.primary = primary
        self.fallback = fallback or MockASRAdapter()

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str = "mr",
    ) -> dict[str, Any]:
        try:
            return await self.primary.transcribe(audio_bytes, filename=filename, language=language)
        except Exception as e:
            logger.warning(
                f"Primary ASR provider ({type(self.primary).__name__}) failed: {e}. "
                f"Falling back to {type(self.fallback).__name__}."
            )
            return await self.fallback.transcribe(audio_bytes, filename=filename, language=language)


def get_asr_adapter() -> BaseASRAdapter:
    """Factory creating configured ASR adapter according to environment settings."""
    if settings.asr_provider == "mock" or (settings.asr_provider == "auto" and not settings.sarvam_api_key):
        return MockASRAdapter()

    if settings.asr_provider == "sarvam" or (settings.asr_provider == "auto" and settings.sarvam_api_key):
        primary = SarvamASRAdapter()
        fallback = BhashiniASRAdapter() if settings.bhashini_api_key else MockASRAdapter()
        return ResilientASRAdapter(primary=primary, fallback=fallback)

    if settings.asr_provider == "bhashini":
        return ResilientASRAdapter(primary=BhashiniASRAdapter(), fallback=MockASRAdapter())

    return MockASRAdapter()
