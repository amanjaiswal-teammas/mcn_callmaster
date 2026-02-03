import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

async def analyze_transcript(transcript: str) -> str:
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a sales call quality analyst."},
            {"role": "user", "content": f"Analyze this call transcript:\n\n{transcript}"}
        ]
    )
    return response['choices'][0]['message']['content']
