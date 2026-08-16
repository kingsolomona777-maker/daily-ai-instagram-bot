import os
import json
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
- title: a short, interesting title
- caption: a useful Instagram caption of 80-120 words
- image_prompt: a detailed prompt for a realistic plumbing-related image

The content must be practical, professional, friendly,
and easy for ordinary homeowners to understand.

Do not make exaggerated claims.
Do not copy the topic word-for-word as the title.
Do not use emojis.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "caption": {
                        "type": "string"
                    },
                    "image_prompt": {
                        "type": "string"
                    }
                },
                "required": [
                    "title",
                    "caption",
                    "image_prompt"
                ]
            }
        }
    )

    data = json.loads(interaction.output_text)

    return {
        "topic": topic,
        "title": data["title"],
        "description": data["caption"],
        "image_prompt": data["image_prompt"]
    }


def check_content(content):
    title = content["title"]
    description = content["description"]
    image_prompt = content["image_prompt"]

    if len(title) < 10:
        return False

    if len(description) < 50:
        return False

    if len(image_prompt) < 30:
        return False

    return True
