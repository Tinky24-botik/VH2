import os
import io
import wave
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


def recognize_with_groq(audio_bytes: bytes, samplerate: int = 16000) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("Не найден GROQ_API_KEY в .env")

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(samplerate)
        wav_file.writeframes(audio_bytes)
    wav_buffer.seek(0)

    response = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        files={"file": ("audio.wav", wav_buffer, "audio/wav")},
        data={
            "model": "whisper-large-v3-turbo",
            "language": "ru",
        },
        timeout=15,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Groq вернул ошибку {response.status_code}: {response.text}"
        )

    result = response.json()
    return result.get("text", "").strip()