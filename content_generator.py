import os
import json
from google import genai


def create_content(topic):

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not available."
        )

    client = genai.Client(
        api_key=api_key
    )


    prompt = f"""
You are a professional plumbing content creator
and social media strategist.

Create ONE original Instagram post for a professional
plumbing account.

TOPIC:
{topic}

CONTENT REQUIREMENTS:

1. TITLE
Create a short, interesting title.
Do not copy the topic word-for-word.

2. DESCRIPTION
Write a useful Instagram caption of approximately
80-120 words.

The caption should:
- Be practical.
- Be professional.
- Be friendly.
- Be easy for ordinary homeowners to understand.
- Give useful plumbing information.
- Avoid exaggerated claims.
- Never invent prices.
- Never give dangerous instructions.
- Encourage professional inspection when appropriate.

3. IMAGE PROMPT
Create a detailed prompt for a realistic plumbing-related
image.

The image must be designed specifically for a
VERTICAL 9:16 Instagram composition.

Important:
- Keep the main plumbing subject clearly visible.
- Keep important objects away from extreme edges.
- Use realistic professional photography.
- Use natural lighting.
- Use a clean, uncluttered background.
- Do not include text.
- Do not include words.
- Do not include logos.
- Do not include watermarks.
- Do not include labels.

4. HASHTAGS
Create 5-8 relevant Instagram hashtags.

Hashtags must:
- Be directly related to the topic.
- Be useful for plumbing/home-maintenance content.
- Avoid misleading claims.
- Avoid spammy or unrelated tags.
- Do not repeat the exact same generic hashtag list
  for every topic when more specific hashtags are possible.

Do not use emojis.

Return ONLY valid JSON with these fields:

title
description
image_prompt
hashtags

The hashtags field must be an array of strings.
Each hashtag must begin with #.
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

                    "description": {
                        "type": "string"
                    },

                    "image_prompt": {
                        "type": "string"
                    },

                    "hashtags": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },

                "required": [
                    "title",
                    "description",
                    "image_prompt",
                    "hashtags"
                ]
            }
        }
    )


    # ========================================================
    # READ GEMINI JSON
    # ========================================================

    try:
        data = json.loads(
            interaction.output_text
        )

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "Gemini returned invalid JSON."
        ) from error


    # ========================================================
    # VALIDATE REQUIRED FIELDS
    # ========================================================

    required_fields = [
        "title",
        "description",
        "image_prompt",
        "hashtags"
    ]

    for field in required_fields:

        if field not in data:
            raise RuntimeError(
                f"Gemini response is missing: {field}"
            )


    # ========================================================
    # CLEAN HASHTAGS
    # ========================================================

    hashtags = []

    for hashtag in data["hashtags"]:

        if not isinstance(hashtag, str):
            continue

        hashtag = hashtag.strip()

        if not hashtag:
            continue

        if not hashtag.startswith("#"):
            hashtag = "#" + hashtag

        hashtags.append(hashtag)


    # Remove duplicate hashtags
    hashtags = list(
        dict.fromkeys(hashtags)
    )


    return {
        "topic": topic,
        "title": data["title"].strip(),
        "description": data["description"].strip(),
        "image_prompt": data["image_prompt"].strip(),
        "hashtags": hashtags
    }


def check_content(content):

    title = content["title"]
    description = content["description"]
    image_prompt = content["image_prompt"]
    hashtags = content["hashtags"]


    if len(title) < 10:
        return False


    if len(description) < 50:
        return False


    if len(image_prompt) < 30:
        return False


    if not isinstance(hashtags, list):
        return False


    if len(hashtags) < 3:
        return False


    return True
