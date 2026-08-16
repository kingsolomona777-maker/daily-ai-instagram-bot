import os
from google import genai


def create_content(topic):
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not available.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a professional plumbing content creator.

Create one original Instagram post based on this topic:

{topic}

Return:
1. A short, interesting title.
2. A useful caption of 80-120 words.
3. A detailed image-generation prompt describing a realistic plumbing-related image.

The content should be practical, professional, friendly, and easy for ordinary homeowners to understand.

Do not use emojis.
Do not make exaggerated claims.
Do not repeat the topic word-for-word as the title.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()

    return {
        "topic": topic,
        "ai_content": text
    }


def check_content(content):
    text = content["ai_content"]

    if len(text) < 100:
        return False

    return True
