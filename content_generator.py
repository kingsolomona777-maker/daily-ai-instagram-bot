import json
import os
import re
from typing import Any, Dict, Optional

from google import genai


# ============================================================
# OROM PLAN1 - EDUCATIONAL CONTENT ENGINE
# ============================================================

MODEL_NAME = "gemini-3.6-flash"

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


# ============================================================
# PLUMBING KNOWLEDGE SYSTEM
# ============================================================

PLUMBING_KNOWLEDGE_AREAS = [
    "water supply systems",
    "cold water plumbing",
    "hot water plumbing",
    "PPR pipe installation",
    "pipe fittings and connections",
    "drainage systems",
    "WC discharge systems",
    "bathroom plumbing",
    "showers and mixers",
    "kitchen plumbing",
    "sink drainage",
    "waste pipes",
    "drain traps",
    "drain ventilation",
    "soakaway systems",
    "pipe sizing and flow",
    "pipe slope and drainage",
    "leak detection and repair",
    "plumbing tools and materials",
    "common plumbing mistakes",
    "preventive plumbing maintenance",
    "professional installation practices",
    "building plumbing design",
    "plumbing troubleshooting",
    "plumbing safety",
]


CONTENT_TYPES = [
    "reel",
    "educational_visual",
]


LESSON_TYPES = [
    "problem_and_cause",
    "how_it_works",
    "common_mistake",
    "professional_tip",
    "maintenance",
    "troubleshooting",
    "installation_principle",
    "material_knowledge",
    "tool_knowledge",
    "myth_vs_fact",
]


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract the first valid JSON object from Gemini output.
    Handles occasional markdown code fences.
    """

    if not text:
        raise ValueError("Gemini returned an empty response.")

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned
    )

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    if not match:
        raise ValueError(
            "Could not find a valid JSON object in Gemini response."
        )

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_content(content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Makes Gemini output safe and predictable for the rest
    of the Orom Plan1 pipeline.
    """

    content.setdefault("title", "")
    content.setdefault("description", "")
    content.setdefault("image_prompt", "")
    content.setdefault("hashtags", [])
    content.setdefault("visual_story", "")

    on_image_text = content.get("on_image_text")

    if not isinstance(on_image_text, dict):
        on_image_text = {}

    on_image_text.setdefault("hook", "")
    on_image_text.setdefault("explanation", "")
    on_image_text.setdefault("callout", "")
    on_image_text.setdefault("takeaway", "")

    content["on_image_text"] = on_image_text

    if not isinstance(content["hashtags"], list):
        content["hashtags"] = [str(content["hashtags"])]

    content["hashtags"] = [
        str(tag).strip()
        for tag in content["hashtags"]
        if str(tag).strip()
    ]

    content["title"] = str(content["title"]).strip()
    content["description"] = str(content["description"]).strip()
    content["image_prompt"] = str(content["image_prompt"]).strip()
    content["visual_story"] = str(content["visual_story"]).strip()

    return content


# ============================================================
# CONTENT GENERATOR
# ============================================================

def create_content(
    topic: str,
    content_type: str = "educational_visual",
    lesson_type: Optional[str] = None,
    lesson_number: Optional[int] = None,
    previous_lesson: Optional[str] = None,
) -> Dict[str, Any]:

    if content_type not in CONTENT_TYPES:
        content_type = "educational_visual"

    if lesson_type not in LESSON_TYPES:
        lesson_type = "professional_tip"

    if not lesson_number:
        lesson_number = 1

    previous_context = (
        previous_lesson
        if previous_lesson
        else "No previous lesson supplied."
    )

    if content_type == "reel":
        format_instruction = """
Create this as a short educational Instagram Reel.

The Reel must teach ONE clear plumbing lesson.

The lesson should work as:
1. Strong opening hook
2. Problem or question
3. Clear explanation
4. Practical takeaway

Keep the lesson understandable when watched without sound.

The on-image text should be concise because it will be displayed
inside a vertical video.
"""
    else:
        format_instruction = """
Create this as a standalone educational Instagram visual.

The image must teach something useful even if the viewer never reads
the caption.

Use a strong hook, realistic plumbing visual, clear callout,
short explanation and practical takeaway.

The image should feel like a professional plumbing teaching card,
not an advertisement.
"""

    prompt = f"""
You are the educational content intelligence system for Orom Plan1,
a professional plumbing education Instagram account.

The goal is NOT simply to generate attractive social media posts.

The goal is to TEACH the audience.

Every lesson must be:
- technically responsible
- physically realistic
- practical
- easy to understand
- useful to homeowners, apprentices and plumbing workers
- visually teachable
- specific rather than vague
- free from invented plumbing facts
- free from dangerous installation advice
- free from exaggerated claims

CURRENT KNOWLEDGE AREA:
{topic}

LESSON TYPE:
{lesson_type}

LESSON NUMBER:
{lesson_number}

PREVIOUS LESSON CONTEXT:
{previous_context}

{format_instruction}

IMPORTANT EDUCATIONAL RULES:

1. Teach one main idea.
2. Explain the cause, principle or reason.
3. Do not merely say "call a plumber".
4. Do not invent pipe sizes or engineering requirements.
5. If a measurement depends on local code, building design,
   fixture type or manufacturer instructions, phrase it carefully.
6. Do not recommend unsafe shortcuts.
7. Do not show impossible plumbing arrangements.
8. Keep plumbing terminology accurate.
9. The generated image must be physically possible.
10. Never put text, logos or watermarks inside the AI-generated
    plumbing scene itself. Text will be added later by the system.
11. Use realistic materials, fittings, tools and pipe geometry.
12. The main plumbing subject must be clearly visible.
13. Use a vertical 9:16 composition.
14. Keep the main subject near the visual center.
15. Avoid clutter.
16. Do not repeat the exact wording of previous lessons.
17. Make the lesson valuable as a standalone piece.
18. Prefer explanation over hype.
19. Use Nigerian/African plumbing realities where appropriate,
    but do not make unsupported regional claims.
20. Never pretend a common practice is automatically correct
    if proper design or local requirements may differ.

CAPTION REQUIREMENT:

Create an educational caption of approximately 80-120 words.

The caption should:
- begin naturally
- explain the plumbing lesson
- provide useful practical context
- include a clear takeaway
- encourage a meaningful comment or question
- avoid empty engagement bait

HASHTAGS:

Generate 5-8 relevant plumbing hashtags.

Do not use generic unrelated viral hashtags.

IMAGE PROMPT:

Create a detailed photorealistic prompt for an image generator.

The image prompt must describe:
- the plumbing environment
- materials
- pipe arrangement
- relevant fittings
- realistic lighting
- realistic construction details
- camera composition
- the exact educational subject

The image prompt must explicitly require:
- photorealistic
- physically accurate plumbing
- realistic materials
- realistic geometry
- vertical 9:16 composition
- no text
- no logo
- no watermark
- no arrows
- no labels

ON-IMAGE EDUCATIONAL TEXT:

Create four short elements:

hook:
A strong educational opening.

explanation:
One short sentence explaining the lesson.

callout:
The specific plumbing component or principle being taught.

takeaway:
A practical final lesson.

The text must be concise enough to fit naturally on a vertical
Instagram image.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "title": "...",
  "description": "...",
  "image_prompt": "...",
  "hashtags": ["...", "..."],
  "visual_story": "...",
  "on_image_text": {{
    "hook": "...",
    "explanation": "...",
    "callout": "...",
    "takeaway": "..."
  }},
  "lesson_type": "...",
  "content_type": "...",
  "knowledge_area": "...",
  "lesson_number": {lesson_number}
}}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    content = extract_json(response.text)

    content = normalize_content(content)

    content["lesson_type"] = lesson_type
    content["content_type"] = content_type
    content["knowledge_area"] = topic
    content["lesson_number"] = lesson_number

    return content


# ============================================================
# QUALITY CHECK
# ============================================================

def check_content(content: Dict[str, Any]) -> bool:
    """
    Basic structural quality gate.

    This intentionally checks structure rather than trying to
    replace human/technical review of every plumbing lesson.
    """

    if not isinstance(content, dict):
        return False

    required_fields = [
        "title",
        "description",
        "image_prompt",
        "hashtags",
        "visual_story",
        "on_image_text",
    ]

    for field in required_fields:
        if field not in content:
            return False

    for field in [
        "title",
        "description",
        "image_prompt",
        "visual_story",
    ]:
        if not isinstance(content[field], str):
            return False

        if not content[field].strip():
            return False

    if not isinstance(content["hashtags"], list):
        return False

    if len(content["hashtags"]) < 3:
        return False

    on_image_text = content["on_image_text"]

    if not isinstance(on_image_text, dict):
        return False

    for field in [
        "hook",
        "explanation",
        "callout",
        "takeaway",
    ]:
        if field not in on_image_text:
            return False

        if not isinstance(on_image_text[field], str):
            return False

        if not on_image_text[field].strip():
            return False

    return True


# ============================================================
# SAFE DEFAULT TOPIC LIST
# ============================================================

def get_knowledge_areas():
    """
    Returns the available Orom Plan1 plumbing knowledge areas.
    """

    return list(PLUMBING_KNOWLEDGE_AREAS)


def get_content_types():
    """
    Returns the content formats supported by the engine.
    """

    return list(CONTENT_TYPES)


def get_lesson_types():
    """
    Returns the available educational lesson structures.
    """

    return list(LESSON_TYPES)
