import io

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_transcribe_marathi_speech():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create dummy WAV byte buffer
        audio_content = b"RIFF....WAVEfmt ....data...."
        files = {
            "file": ("test_speech.wav", io.BytesIO(audio_content), "audio/wav")
        }
        data = {
            "language": "mr",
            "parse_number": "true",
        }

        response = await client.post("/speech/transcribe", files=files, data=data)
        assert response.status_code == 200
        payload = response.json()
        assert "text" in payload
        assert payload["language"] == "mr"
        assert payload["confidence"] > 0.0
        # Mock adapter returns "दीड लाख रुपये" which parses to 150000
        assert payload["parsed_number"] == 150000
        assert payload["formatted_inr"] == "₹1,50,000"


@pytest.mark.asyncio
async def test_transcribe_hindi_speech():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        audio_content = b"dummy_hindi_audio_bytes"
        files = {
            "file": ("hindi.wav", io.BytesIO(audio_content), "audio/wav")
        }
        data = {
            "language": "hi",
            "parse_number": "true",
        }

        response = await client.post("/speech/transcribe", files=files, data=data)
        assert response.status_code == 200
        payload = response.json()
        assert payload["language"] == "hi"
        assert payload["parsed_number"] == 150000


@pytest.mark.asyncio
async def test_transcribe_english_speech():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        audio_content = b"dummy_en_audio_bytes"
        files = {
            "file": ("english.wav", io.BytesIO(audio_content), "audio/wav")
        }
        data = {
            "language": "en",
            "parse_number": "true",
        }

        response = await client.post("/speech/transcribe", files=files, data=data)
        assert response.status_code == 200
        payload = response.json()
        assert payload["language"] == "en"
        assert payload["parsed_number"] == 150000


@pytest.mark.asyncio
async def test_transcribe_empty_file_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "file": ("empty.wav", io.BytesIO(b""), "audio/wav")
        }
        response = await client.post("/speech/transcribe", files=files)
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_live_parse_number_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Spoken Marathi idiom
        resp1 = await client.post("/speech/parse-number", data={"text": "साडे तीन हजार"})
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["success"] is True
        assert data1["parsed_number"] == 3500
        assert data1["formatted_inr"] == "₹3,500"

        # 2. Spoken Hindi idiom
        resp2 = await client.post("/speech/parse-number", data={"text": "पौने दो लाख"})
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["success"] is True
        assert data2["parsed_number"] == 175000
        assert data2["formatted_inr"] == "₹1,75,000"

        # 3. Non-number text
        resp3 = await client.post("/speech/parse-number", data={"text": "शुभ प्रभात"})
        assert resp3.status_code == 200
        data3 = resp3.json()
        assert data3["success"] is False
        assert data3["parsed_number"] is None
