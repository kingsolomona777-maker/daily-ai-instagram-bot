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

    Handles:
    - normal JSON
    - JSON inside markdown code fences
    - occasional surrounding text
    """

    if not text:
        raise ValueError(
            "Gemini returned an empty response."
        )

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
        result = json.loads(cleaned)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    match = re.search(
        r"\{.*\}",
        cleaned,
        re.DOTALL
    )

    if not match:
        raise ValueError(
            "Could not find a valid JSON object in Gemini response."
        )

    try:
        result = json.loads(match.group(0))

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError(
            "Gemini response must contain a JSON object."
        )

    return result


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_content(
    content: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Makes Gemini output safe and predictable for the rest
    of the Orom Plan1 pipeline.
    """

    if not isinstance(content, dict):
        raise ValueError(
            "Generated content must be a dictionary."
        )

    content.setdefault("title", "")
    content.setdefault("description", "")
    content.setdefault("image_prompt", "")
    content.setdefault("hashtags", [])
    content.setdefault("visual_story", "")

    on_image_text = content.get(
        "on_image_text"
    )

    if not isinstance(on_image_text, dict):
        on_image_text = {}

    on_image_text.setdefault(
        "hook",
        ""
    )

    on_image_text.setdefault(
        "explanation",
        ""
    )

    on_image_text.setdefault(
        "callout",
        ""
    )

    on_image_text.setdefault(
        "takeaway",
        ""
    )

    content["on_image_text"] = on_image_text

    if not isinstance(
        content["hashtags"],
        list
    ):
        content["hashtags"] = [
            str(content["hashtags"])
        ]

    content["hashtags"] = [
        str(tag).strip()
        for tag in content["hashtags"]
        if str(tag).strip()
    ]

    content["title"] = str(
        content["title"]
    ).strip()

    content["description"] = str(
        content["description"]
    ).strip()

    content["image_prompt"] = str(
        content["image_prompt"]
    ).strip()

    content["visual_story"] = str(
        content["visual_story"]
    ).strip()

    for field in [
        "hook",
        "explanation",
        "callout",
        "takeaway",
    ]:
        content["on_image_text"][field] = str(
            content["on_image_text"][field]
        ).strip()

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

Structure the teaching as:

1. Strong opening hook
2. Problem, question or observation
3. Clear explanation
4. Practical takeaway

The viewer should learn something useful even when watching
without sound.

The visual sequence should support the lesson instead of
being random motion applied to an unrelated picture.

Keep all on-image text concise because it will appear inside
a vertical video.
"""

    else:
        format_instruction = """
Create this as a standalone educational Instagram visual.

The image must have educational value even if the viewer
never reads the caption.

Use:

1. Strong educational hook
2. Clear plumbing visual
3. Short explanation
4. Specific callout
5. Practical takeaway

The image should feel like a professional plumbing teaching
resource, not an advertisement.
"""

    if lesson_type == "myth_vs_fact":
        lesson_type_instruction = """
This is a MYTH vs FACT lesson.

The hook must clearly identify the claim as a myth or
question rather than presenting the false claim as established
fact.

Prefer a structure such as:

MYTH: [short claim]

FACT: [accurate correction]

Do not create a false myth simply to make the post more
dramatic.

If the subject depends on pipe material, manufacturer
instructions, local code, chemical compatibility or building
conditions, explain that limitation rather than making an
absolute statement.
"""

    else:
        lesson_type_instruction = """
This is a normal educational lesson.

Do not manufacture controversy.

Prioritize accurate explanation over sensational wording.
"""

    prompt = f"""
You are the educational content intelligence system for
Orom Plan1, a professional plumbing education Instagram
account.

The goal is NOT simply to generate attractive social media
posts.

The goal is to TEACH the audience.

Every lesson must be:

- technically responsible
- physically realistic
- practical
- easy to understand
- useful to homeowners
- useful to apprentices
- useful to plumbing workers
- visually teachable
- specific rather than vague
- free from invented plumbing facts
- free from dangerous installation advice
- free from exaggerated claims

============================================================
CURRENT LESSON INFORMATION
============================================================

KNOWLEDGE AREA:
{topic}

LESSON TYPE:
{lesson_type}

LESSON NUMBER:
{lesson_number}

PREVIOUS LESSON CONTEXT:
{previous_context}

============================================================
CONTENT FORMAT
============================================================

{format_instruction}

============================================================
LESSON-TYPE INSTRUCTION
============================================================

{lesson_type_instruction}

============================================================
CORE EDUCATIONAL RULES
============================================================

1. Teach ONE main plumbing idea.

2. Explain the cause, principle, reason or process behind
   the lesson.

3. Do not merely tell the audience to "call a plumber".
   Give useful educational information first.

4. Do not invent pipe sizes, pressure values, flow rates,
   slopes, distances or engineering requirements.

5. When a measurement depends on local plumbing code,
   building design, fixture type, manufacturer instructions
   or site conditions, say so clearly.

6. Never present an uncertain technical claim as a universal
   rule.

7. Avoid words such as "always", "never", "100%", "harmless"
   or "guaranteed" unless the statement is genuinely universal
   and technically justified.

8. Do not recommend unsafe shortcuts.

9. Do not recommend bypassing required safety procedures,
   plumbing codes or manufacturer instructions.

10. Do not encourage dangerous chemical mixing.

11. If discussing drain-cleaning chemicals, never suggest
    mixing different chemical products.

12. Do not claim that every chemical drain cleaner damages
    every type of pipe. Explain compatibility and usage
    limitations accurately.

13. Do not show impossible plumbing arrangements.

14. Do not connect pipes in physically impossible ways.

15. Do not invent valves, fittings, traps, pumps or other
    components merely to make an image look complicated.

16. Pipe connections must have realistic geometry.

17. Water flow direction must make physical sense.

18. Drainage systems must visually distinguish drainage from
    pressurized water supply systems.

19. Wastewater, venting and water-supply components must not
    be mixed together incorrectly.

20. Use realistic plumbing materials and fittings.

21. When showing a cutaway or exploded view, clearly treat it
    as an educational illustration rather than pretending it
    is an ordinary photograph of an exposed installation.

22. If the lesson is better explained by a cutaway, sectional
    view or simplified diagram, use that approach.

23. The main plumbing subject must be immediately recognizable.

24. Do not make the image visually complicated simply for
    decoration.

25. Keep the main educational subject near the visual center.

26. Use a vertical 9:16 composition.

27. Leave enough clean visual space for text overlays.

28. Do not place important plumbing details directly behind
    large text panels.

29. The image itself must remain useful without the overlay.

30. Never place educational text inside the AI-generated image.
    The Orom Plan1 system adds text separately.

31. Never place arrows, labels, diagrams or annotations inside
    the AI-generated image unless the prompt explicitly calls
    for an educational diagram. In that case, keep them
    minimal and do not duplicate the later text overlay.

32. Never generate watermarks.

33. Never generate logos.

34. Never generate fake company branding.

35. Never generate recognizable commercial product labels
    unless the lesson specifically requires a real product and
    the information is verified.

36. Avoid invented product names and fake-looking labels.

37. If a bottle, tool, fitting or package is shown, use a
    generic unbranded version unless a real product is required.

38. Human subjects may appear when they help explain the lesson,
    but the plumbing subject must remain the main focus.

39. Do not make a person's face the main attraction of a
    plumbing lesson.

40. Prefer professional, realistic working environments.

41. Use Nigerian or African plumbing realities when appropriate,
    but do not invent unsupported regional claims.

42. Do not assume that a common local practice is automatically
    technically correct.

43. Explain differences between recommended professional
    practice and common shortcuts when relevant.

44. Never repeat the exact wording of previous lessons.

45. Build a useful learning progression.

46. Prefer explanation over hype.

47. Every lesson must contain a clear practical takeaway.

============================================================
IMAGE REALISM RULES
============================================================

Create an image prompt for a high-quality image generator.

The image prompt must describe:

- exact plumbing subject
- plumbing environment
- realistic materials
- realistic pipe geometry
- relevant fittings
- realistic connections
- realistic lighting
- camera position
- composition
- educational purpose

The image prompt must explicitly require:

- photorealistic appearance when showing a real installation
- physically accurate plumbing
- realistic materials
- realistic geometry
- believable construction details
- vertical 9:16 composition
- main subject clearly visible
- no text
- no logo
- no watermark
- no fake branding
- no random labels
- no impossible fittings
- no impossible pipe connections

If a cutaway, sectional or exploded educational illustration
is more appropriate, explicitly describe it as an educational
technical illustration while keeping the plumbing geometry
physically believable.

============================================================
CAPTION REQUIREMENT
============================================================

Create an educational caption of approximately 80-120 words.

The caption should:

- begin naturally
- explain the plumbing lesson
- provide useful practical context
- explain why the lesson matters
- include a clear takeaway
- encourage a meaningful comment or question
- avoid empty engagement bait
- avoid exaggerated claims
- avoid repeating the exact title word-for-word

The caption should sound like a knowledgeable plumbing educator,
not a generic AI marketing account.

============================================================
HASHTAGS
============================================================

Generate 5-8 relevant plumbing hashtags.

Use hashtags related to:

- the plumbing subject
- plumbing education
- the relevant skill
- homeowners or tradespeople where appropriate

Do not use unrelated viral hashtags.

============================================================
ON-IMAGE EDUCATIONAL TEXT
============================================================

Create four short elements.

HOOK:
A strong educational opening.

EXPLANATION:
One short sentence explaining the actual plumbing principle.

CALLOUT:
The specific plumbing component, cause, mistake or principle
being taught.

TAKEAWAY:
A practical final lesson.

Keep every element concise enough for a vertical Instagram
image.

Avoid turning the image into a wall of text.

The hook should attract attention through useful information,
not fear or exaggerated claims.

============================================================
VISUAL STORY
============================================================

Describe how the visual should teach the lesson.

The visual story should explain:

- what the viewer should notice
- what plumbing component matters
- what process or problem is being demonstrated
- why the visual supports the lesson

============================================================
OUTPUT FORMAT
============================================================

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

    content = extract_json(
        response.text
    )

    content = normalize_content(
        content
    )

    content["lesson_type"] = lesson_type
    content["content_type"] = content_type
    content["knowledge_area"] = topic
    content["lesson_number"] = lesson_number

    return content


# ============================================================
# QUALITY CHECK
# ============================================================

def check_content(
    content: Dict[str, Any]
) -> bool:
    """
    Structural quality gate.

    This checks whether the generated content has the minimum
    structure required by the Orom Plan1 pipeline.

    It does NOT claim to replace human or professional technical
    review of every plumbing lesson.
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
        if not isinstance(
            content[field],
            str
        ):
            return False

        if not content[field].strip():
            return False

    if not isinstance(
        content["hashtags"],
        list
    ):
        return False

    if len(content["hashtags"]) < 3:
        return False

    on_image_text = content[
        "on_image_text"
    ]

    if not isinstance(
        on_image_text,
        dict
    ):
        return False

    for field in [
        "hook",
        "explanation",
        "callout",
        "takeaway",
    ]:
        if field not in on_image_text:
            return False

        if not isinstance(
            on_image_text[field],
            str
        ):
            return False

        if not on_image_text[field].strip():
            return False

    if (
        content.get("content_type")
        not in CONTENT_TYPES
    ):
        return False

    if (
        content.get("lesson_type")
        not in LESSON_TYPES
    ):
        return False

    return True


# ============================================================
# SAFE DEFAULT TOPIC LIST
# ============================================================

def get_knowledge_areas():
    """
    Returns the available Orom Plan1 plumbing knowledge areas.
    """

    return list(
        PLUMBING_KNOWLEDGE_AREAS
    )


def get_content_types():
    """
    Returns the content formats supported by the engine.
    """

    return list(
        CONTENT_TYPES
    )


def get_lesson_types():
    """
    Returns the available educational lesson structures.
    """

    return list(
        LESSON_TYPES
    )
