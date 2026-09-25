import json
import re
from typing import Any, Dict, List

from content_generator import MODEL_NAME, client


REQUIRED_FIELDS = [
    "title",
    "description",
    "image_prompt",
    "hashtags",
    "visual_story",
    "on_image_text",
]


def extract_json_array(text: str) -> List[Dict[str, Any]]:
    """
    Extract a JSON array from Gemini's response.
    Handles responses that contain markdown fences or extra text.
    """

    if not text:
        raise ValueError("Gemini returned an empty response.")

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "Could not find a JSON array in Gemini response."
        )

    json_text = cleaned[start:end + 1]

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(data, list):
        raise ValueError(
            "Gemini response was not a JSON array."
        )

    return data


def validate_batch_content(
    content: List[Dict[str, Any]],
    expected_count: int = 2,
) -> bool:
    """
    Validate a batch of generated lessons before they
    are allowed into the production pipeline.
    """

    if len(content) != expected_count:
        return False

    for item in content:
        if not isinstance(item, dict):
            return False

        for field in REQUIRED_FIELDS:
            if field not in item:
                return False

        if not isinstance(item["hashtags"], list):
            return False

        if not isinstance(item["on_image_text"], dict):
            return False

        required_text_fields = [
            "hook",
            "explanation",
            "callout",
            "takeaway",
        ]

        for field in required_text_fields:
            if field not in item["on_image_text"]:
                return False

    return True


def build_pair_prompt(
    first_item: Dict[str, Any],
    second_item: Dict[str, Any],
) -> str:
    """
    Build a two-lesson Gemini request.

    The two lessons are deliberately related but must remain
    independently useful to the Instagram audience.
    """

    first = json.dumps(
        first_item,
        ensure_ascii=False,
        indent=2,
    )

    second = json.dumps(
        second_item,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
You are the educational content engine for Orom Plan1,
a professional plumbing education Instagram system.

Generate EXACTLY TWO distinct plumbing lessons in ONE response.

The lessons must follow the supplied lesson plans.

LESSON 1 PLAN:
{first}

LESSON 2 PLAN:
{second}

IMPORTANT:

1. Both lessons must teach something genuinely useful.
2. Each lesson must work independently as an Instagram post.
3. Do not simply rewrite the same lesson twice.
4. Keep the two lessons connected where appropriate, but
   make their teaching points clearly different.
5. Respect the lesson type and knowledge path supplied.
6. Do not invent unsafe plumbing information.
7. Do not invent pipe sizes unless technically justified.
8. Do not claim that a practice is universally correct when
   installation conditions can change the answer.
9. Keep plumbing materials and fittings physically realistic.
10. Image prompts must describe realistic plumbing scenes.
11. AI-generated images must contain NO text, NO logo and
    NO watermark.
12. Image composition should be vertical 9:16.
13. Keep the main plumbing subject visually clear.
14. The educational text will be added later by Python.
15. Captions should be useful and natural, approximately
    80 to 120 words.
16. Provide 5 to 8 relevant hashtags.
17. Avoid repeating generic filler.
18. Do not mention that AI was used.
19. Do not mention this prompt.
20. Return ONLY valid JSON.

Return exactly this structure:

[
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
    }}
  }},
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
    }}
  }}
]
"""


def generate_content_pair(
    first_item: Dict[str, Any],
    second_item: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Generate two related but independent lessons with
    one Gemini request.
    """

    prompt = build_pair_prompt(
        first_item,
        second_item,
    )

    print()
    print("Requesting one Gemini batch for two lessons...")
    print(
        f"Lesson 1: "
        f"{first_item.get('knowledge_area', '')}"
    )
    print(
        f"Lesson 2: "
        f"{second_item.get('knowledge_area', '')}"
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    response_text = getattr(response, "text", "")

    generated = extract_json_array(
        response_text
    )

    if not validate_batch_content(
        generated,
        expected_count=2,
    ):
        raise ValueError(
            "Gemini batch content failed validation."
        )

    print(
        "Gemini batch returned two valid lessons."
    )

    return generated


def attach_plan_metadata(
    generated_content: List[Dict[str, Any]],
    plan_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Attach planner metadata to the generated lessons.
    """

    if len(generated_content) != len(plan_items):
        raise ValueError(
            "Generated content count does not match "
            "plan item count."
        )

    results = []

    for content, plan in zip(
        generated_content,
        plan_items,
    ):
        package = dict(content)

        package["lesson_type"] = plan.get(
            "lesson_type",
            "",
        )

        package["content_type"] = plan.get(
            "content_type",
            "",
        )

        package["knowledge_area"] = plan.get(
            "knowledge_area",
            "",
        )

        package["knowledge_path"] = plan.get(
            "knowledge_path",
            "",
        )

        package["lesson_number"] = int(
            plan.get(
                "lesson_number",
                0,
            )
        )

        package["slot"] = int(
            plan.get(
                "slot",
                0,
            )
        )

        results.append(package)

    return results


def generate_daily_content_batches(
    daily_plan: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generate a full 10-post content plan using pairs.

    Five Gemini requests are used for ten planned posts.
    """

    if len(daily_plan) != 10:
        raise ValueError(
            "Daily batch generation requires exactly "
            "10 plan items."
        )

    generated_posts = []

    for index in range(0, 10, 2):
        first_item = daily_plan[index]
        second_item = daily_plan[index + 1]

        pair_content = generate_content_pair(
            first_item,
            second_item,
        )

        pair_with_metadata = attach_plan_metadata(
            pair_content,
            [
                first_item,
                second_item,
            ],
        )

        generated_posts.extend(
            pair_with_metadata
        )

    if len(generated_posts) != 10:
        raise RuntimeError(
            "Batch generation did not produce "
            "exactly 10 posts."
        )

    return generated_posts


if __name__ == "__main__":
    print(
        "Orom Plan1 content batch generator loaded."
    )
    print(
        "Target: 10 lessons using 5 Gemini requests."
    )
