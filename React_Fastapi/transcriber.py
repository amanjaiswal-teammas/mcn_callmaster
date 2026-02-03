import httpx
import os
import logging
from dotenv import load_dotenv

load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

async def transcribe_with_deepgram_async(audio_file_path: str) -> str:
    url = "https://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/wav"
    }
    params = {
        "punctuate": "true",
        "model": "nova",
        "language": "hi-Latn"
    }

    try:
        with open(audio_file_path, "rb") as audio:
            audio_data = audio.read()

        timeout = httpx.Timeout(60.0)  # You can increase this as needed

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                headers=headers,
                params=params,
                content=audio_data
            )

        if response.status_code == 200:
            result = response.json()
            return result["results"]["channels"][0]["alternatives"][0].get("transcript", "")
        else:
            logging.error(f"Error transcribing audio: {response.status_code} - {response.text}")
            return ""

    except httpx.ReadTimeout:
        logging.error("Deepgram request timed out.")
        return "Transcription failed: Request timed out."

    except Exception as e:
        logging.exception("Exception during transcription")
        return "Transcription failed due to an internal error."
