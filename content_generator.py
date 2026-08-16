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

Create:
1. An interesting short title.
2. A useful caption of about 80-120 words.
3. A detailed prompt for a realistic Instagram image related to the post.

The content should be practical, professional, friendly,
and easy for ordinary homeowners to understand.

Do not make exaggerated claims.
Do not copy the topic as the title.
Do not use emojis.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    text = interaction.output_text.strip()

    return {
        "topic": topic,
        "ai_content": text
    }


def check_content(content):
    text = content["ai_content"]

    if len(text) < 100:
        return False

    return True
