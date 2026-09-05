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
You are an expert plumbing content creator, residential plumbing
specialist, professional photographer, and Instagram content strategist.

Create ONE original Instagram post for a professional plumbing account.

TOPIC:
{topic}

============================================================
1. TITLE
============================================================

Create a short, interesting title that makes a homeowner want to
read the post.

Do not simply copy the topic word-for-word.

============================================================
2. DESCRIPTION
============================================================

Write a useful Instagram caption of approximately 80-120 words.

The caption must:
- Be practical and accurate.
- Be professional but friendly.
- Be easy for ordinary homeowners to understand.
- Explain useful plumbing information.
- Avoid exaggerated claims.
- Never invent prices.
- Never make unsafe recommendations.
- Encourage professional inspection when appropriate.
- Sound naturally written by an experienced plumber.
- Avoid repetitive openings such as "Did you know..."
- Do not use emojis.

============================================================
3. IMAGE PROMPT
============================================================

Create a HIGH-QUALITY, PHOTOREALISTIC image prompt that visually
represents the exact plumbing topic.

The image is extremely important.

Do NOT create a generic "plumbing" image.

The scene must clearly communicate the specific topic.

For example:

- If the topic is about a water pump, show an appropriate realistic
  residential water-pump installation, including relevant pipes,
  valves, pressure equipment or other components when appropriate.

- If the topic is about a leaking tap, show a realistic household
  faucet with visible water leakage in an appropriate sink area.

- If the topic is about drainage, show a realistic drainage system,
  drain pipe, inspection point, blockage or relevant plumbing scene
  that actually represents the topic.

- If the topic is about pipe installation, show realistic pipes,
  fittings, joints and installation conditions.

- If the topic is about a toilet, show an appropriate realistic
  bathroom plumbing environment and the relevant toilet components.

- If the topic is about maintenance or repair, show the actual
  equipment being inspected or repaired rather than a random plumber
  standing beside unrelated equipment.

============================================================
IMAGE REALISM
============================================================

The image should look like a real professional photograph taken by
a skilled commercial photographer.

Use:
- Photorealistic appearance.
- Realistic plumbing materials.
- Correct-looking plumbing components.
- Realistic pipe proportions.
- Realistic connections and fittings.
- Natural surface textures.
- Realistic water behavior.
- Natural shadows.
- Natural reflections.
- Realistic skin, hands and clothing if a person appears.
- Professional photographic lighting.
- Subtle depth of field.
- Sharp focus on the main plumbing subject.
- Natural background blur where appropriate.
- Clean but believable residential or professional plumbing environment.

Do not make the image look like:
- Digital art.
- Cartoon art.
- 3D render.
- Illustration.
- Advertisement artwork.
- CGI.
- Plastic-looking equipment.

============================================================
PEOPLE
============================================================

Only include a plumber/person when the topic benefits from showing
someone performing an action.

If a plumber is shown:
- Show realistic work clothing.
- Show realistic protective gloves when appropriate.
- Show natural human proportions.
- Show realistic hands.
- Show the person actually inspecting, installing or repairing the
  relevant plumbing equipment.
- Do not make the person pose unnecessarily for the camera.

If a person is not necessary, focus on the plumbing equipment itself.

============================================================
COMPOSITION
============================================================

The final image will be used as a VERTICAL 9:16 Instagram image.

Design the scene specifically for vertical composition.

Important:
- Keep the main subject large enough to be clearly understood.
- Keep the most important plumbing equipment near the central
  composition.
- Keep important details away from the extreme top, bottom, left
  and right edges.
- Leave reasonable visual breathing room around the main subject.
- Do not place the main subject partially outside the frame.
- Use a natural professional camera perspective.
- Avoid awkward cropping.
- Avoid excessive empty space.
- Create a visually balanced vertical photograph.

The image should remain understandable even when viewed on a
smartphone screen.

============================================================
CAMERA AND LIGHTING
============================================================

Use realistic professional photography language.

Choose an appropriate:
- Camera perspective.
- Focal length.
- Depth of field.
- Focus point.
- Lighting direction.
- Exposure.
- Background.

Prefer natural daylight or realistic professional interior lighting.

The lighting should reveal the plumbing equipment clearly without
making the scene look artificially dramatic.

============================================================
ENVIRONMENT
============================================================

Choose an environment that makes sense for the topic.

Possible environments include:
- Modern residential bathroom.
- Residential kitchen.
- Utility room.
- Pump room.
- Outdoor residential water system.
- Building construction site.
- Professional plumbing workspace.
- Residential drainage area.

Do not add unrelated objects simply to make the scene complicated.

The background should support the subject without distracting from it.

============================================================
NO TEXT OR BRANDING
============================================================

The generated image must contain:

NO text.
NO words.
NO letters.
NO numbers.
NO captions.
NO labels.
NO signs.
NO logos.
NO watermarks.
NO brand names.
NO social-media graphics.
NO UI elements.

============================================================
IMAGE QUALITY
============================================================

Prioritize:
photorealism, professional photography, realistic plumbing
equipment, accurate materials, realistic proportions, natural
lighting, sharp details, realistic textures, believable environment,
clean composition, high visual quality.

Do not describe the image as an illustration.

============================================================
4. HASHTAGS
============================================================

Create 5-8 relevant Instagram hashtags.

Hashtags must:
- Be directly related to the topic.
- Be useful for plumbing and home-maintenance content.
- Prefer specific topic-related hashtags when appropriate.
- Avoid misleading claims.
- Avoid spammy or unrelated tags.
- Do not use the exact same hashtag list for every topic.

Do not use emojis.

============================================================
OUTPUT
============================================================

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
