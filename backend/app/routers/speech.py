from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from adapters.asr import get_asr_adapter
from engines.voice.number_parser import IndianNumberParser, parse_indian_number

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Speech & Voice"])


@router.post("/speech/transcribe", status_code=status.HTTP_200_OK)
@router.post("/api/speech/transcribe", status_code=status.HTTP_200_OK)
async def transcribe_speech(
    file: Annotated[UploadFile | None, File()] = None,
    language: Annotated[str, Form()] = "mr",
    parse_number: Annotated[bool, Form()] = True,
) -> dict[str, Any]:
    """
    Transcribe spoken voice audio using ASR and optionally parse Indian numbers.
    TECH_SPEC §8:
      - Audio is discarded immediately after processing (never stored, except consent audio).
      - Numbers spoken in words ('दीड लाख') are deterministically parsed.
      - Return structured response with text, confidence, parsed_number, formatted_inr.
    """
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is required for transcription",
        )

    # Read audio bytes into memory (discarded after function return)
    try:
        audio_bytes = await file.read()
    except Exception as e:
        logger.error(f"Failed to read audio payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audio payload",
        ) from e

    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file cannot be empty",
        )

    asr = get_asr_adapter()
    try:
        result = await asr.transcribe(
            audio_bytes=audio_bytes,
            filename=file.filename or "audio.wav",
            language=language,
        )
    except Exception as e:
        logger.error(f"ASR transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech transcription failed: {str(e)}",
        ) from e

    transcript = result.get("text", "")
    parsed_num = None
    formatted_inr = None

    if parse_number and transcript:
        val = parse_indian_number(transcript)
        if val is not None:
            parsed_num = int(val)
            formatted_inr = IndianNumberParser.format_inr(val)

    return {
        "text": transcript,
        "confidence": result.get("confidence", 0.95),
        "language": language,
        "provider": result.get("provider", "mock"),
        "parsed_number": parsed_num,
        "formatted_inr": formatted_inr,
    }


@router.post("/speech/parse-number", status_code=status.HTTP_200_OK)
@router.post("/api/speech/parse-number", status_code=status.HTTP_200_OK)
async def parse_spoken_number_endpoint(
    text: Annotated[str, Form()],
) -> dict[str, Any]:
    """
    Endpoint for live parsing of transcript strings without re-uploading audio.
    Used for instant UI feedback as the user edits or confirms the transcript.
    """
    val = parse_indian_number(text)
    if val is not None:
        return {
            "raw_text": text,
            "parsed_number": int(val),
            "formatted_inr": IndianNumberParser.format_inr(val),
            "success": True,
        }
    return {
        "raw_text": text,
        "parsed_number": None,
        "formatted_inr": None,
        "success": False,
    }
