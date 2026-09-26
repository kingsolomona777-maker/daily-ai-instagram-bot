import json
import os
import random
import re
import time
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from content_generator import MODEL_NAME, client


# ============================================================
# RETRY SETTINGS
# ============================================================

# 2 additional retries after the first request.
# Maximum total Gemini requests for one lesson pair = 3.
MAX_RETRIES = 2

# Exponential backoff:
# Retry 1 -> about 8-11 seconds
# Retry 2 -> about 16-19 seconds
BASE_RETRY_DELAY = 8
MAX_RETRY_DELAY = 30
MAX_JITTER = 3


RETRYABLE_STATUS_CODES = {
    408,
    429,
    500,
    502,
    503,
    504,
}


# ============================================================
# GEMINI RETRY HELPERS
# ============================================================

def get_error_status_code(error: Exception) -> Optional[int]:
    """
    Try to extract an HTTP/status code from a Gemini exception.
    """

    for attribute in (
        "code",
        "status_code",
        "http_status",
    ):
        value = getattr(error, attribute, None)

        if isinstance(value, int):
            return value

        if isinstance(value, str) and value.isdigit():
            return int(value)

    message = str(error)

    match = re.search(r"\b(408|429|500|502|503|504)\b", message)

    if match:
        return int(match.group(1))

    return None


def is_retryable_gemini_error(error: Exception) -> bool:
    """
    Return True only for errors that are reasonable to retry.
    """

    status_code = get_error_status_code(error)

    if status_code in RETRYABLE_STATUS_CODES:
        return True

    message = str(error).upper()

    transient_markers = (
        "UNAVAILABLE",
        "RESOURCE_EXHAUSTED",
        "SERVICE_UNAVAILABLE",
        "DEADLINE_EXCEEDED",
        "INTERNAL",
        "TIMEOUT",
        "TIMED OUT",
    )

    return any(marker in message for marker in transient_markers)


def get_retry_delay(retry_number: int) -> float:
    """
    Calculate exponential backoff with jitter.

    retry_number:
        1 = first retry
        2 = second retry
    """

    exponential_delay = BASE_RETRY_DELAY * (2 ** (retry_number - 1))

    base_delay = min(
        exponential_delay,
        MAX_RETRY_DELAY,
    )

    jitter = random.uniform(
        0,
        MAX_JITTER,
    )

    return base_delay + jitter


# ============================================================
# JSON HELPERS
# ============================================================

def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract a JSON object from Gemini's response.
    """

    cleaned = text.strip()

    # Remove markdown code fences if Gemini adds them.
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
    )

    try:
        parsed = json.loads(cleaned)

        if not isinstance(parsed, dict):
            raise ValueError("Gemini response JSON is not an object.")

        return parsed

    except json.JSONDecodeError:
        match = re.search(
            r"\{.*\}",
            cleaned,
            flags=re.DOTALL,
        )

        if not match:
            raise ValueError(
                "Could not find a valid JSON object in Gemini response."
            )

        parsed = json.loads(match.group(0))

        if not isinstance(parsed, dict):
            raise ValueError(
                "Extracted Gemini JSON is not an object."
            )

        return parsed


# ============================================================
# CONTENT VALIDATION
# ============================================================

REQUIRED_FIELDS = [
    "title",
    "description",
    "image_prompt",
    "hashtags",
    "visual_story",
    "on_image_text",
    "lesson_type",
    "content_type",
    "knowledge_area",
]


def validate_content(content: Dict[str, Any]) -> bool:
    """
    Validate the minimum structure required by Orom Plan1.
    """

    if not isinstance(content, dict):
        raise ValueError(
            "Generated content is not a dictionary."
        )

    missing = [
        field
        for field in REQUIRED_FIELDS
        if field not in content
    ]

    if missing:
        raise ValueError(
            f"Generated content is missing fields: {missing}"
        )

    if not isinstance(content["title"], str):
        raise ValueError(
            "title must be a string."
        )

    if not isinstance(content["description"], str):
        raise ValueError(
            "description must be a string."
        )

    if not isinstance(content["image_prompt"], str):
        raise ValueError(
            "image_prompt must be a string."
        )

    if not isinstance(content["hashtags"], list):
        raise ValueError(
            "hashtags must be a list."
        )

    if not isinstance(content["visual_story"], list):
        raise ValueError(
            "visual_story must be a list."
        )

    if not isinstance(content["on_image_text"], dict):
        raise ValueError(
            "on_image_text must be an object."
        )

    return True


# ============================================================
# GEMINI CONTENT GENERATION
# ============================================================

def generate_content_pair(
    lesson_a: Dict[str, Any],
    lesson_b: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Generate two related but independent educational lessons
    in one Gemini request.

    The request is retried only when the Gemini error appears
    transient.
    """

    prompt = f"""
You are the educational content engine for Orom Plan1,
a professional plumbing education platform.

Generate EXACTLY TWO different plumbing lessons.

The lessons must be technically responsible, useful,
educational, visually understandable, and suitable for
Instagram.

Do not invent technical standards.

Do not include unsafe instructions.

Do not place text, logos, watermarks, labels, arrows,
or typography inside the AI image prompt.

Each lesson must stand alone and teach the audience
something genuinely useful.

LESSON A PLAN
{json.dumps(lesson_a, indent=2)}

LESSON B PLAN
{json.dumps(lesson_b, indent=2)}

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
  "lessons": [
    {{
      "title": "Short educational title",
      "description": "Educational Instagram caption of about 80-120 words.",
      "image_prompt": "Detailed realistic vertical 9:16 plumbing image prompt with no text, no logo, and no watermark.",
      "hashtags": [
        "#plumbing",
        "#plumbingtips",
        "#plumber"
      ],
      "visual_story": [
        "Visual scene instruction 1",
        "Visual scene instruction 2",
        "Visual scene instruction 3"
      ],
      "on_image_text": {{
        "hook": "Short attention-grabbing teaching hook",
        "explanation": "Short explanation",
        "callout": "Useful visual callout",
        "takeaway": "Clear lesson takeaway"
      }},
      "lesson_type": "Lesson type",
      "content_type": "reel or educational_visual",
      "knowledge_area": "Plumbing knowledge area"
    }},
    {{
      "title": "Short educational title",
      "description": "Educational Instagram caption of about 80-120 words.",
      "image_prompt": "Detailed realistic vertical 9:16 plumbing image prompt with no text, no logo, and no watermark.",
      "hashtags": [
        "#plumbing",
        "#plumbingtips",
        "#plumber"
      ],
      "visual_story": [
        "Visual scene instruction 1",
        "Visual scene instruction 2",
        "Visual scene instruction 3"
      ],
      "on_image_text": {{
        "hook": "Short attention-grabbing teaching hook",
        "explanation": "Short explanation",
        "callout": "Useful visual callout",
        "takeaway": "Clear lesson takeaway"
      }},
      "lesson_type": "Lesson type",
      "content_type": "reel or educational_visual",
      "knowledge_area": "Plumbing knowledge area"
    }}
  ]
}}

IMPORTANT:

1. Return exactly two lessons.
2. Keep the two lessons different.
3. Respect the supplied lesson plans.
4. Do not repeat the same teaching point.
5. Use professional plumbing terminology.
6. Make the lesson understandable to ordinary homeowners.
7. Keep the visual concept realistic.
8. Do not put written text inside image_prompt.
9. Do not add markdown outside the JSON.
"""

    total_attempts = MAX_RETRIES + 1

    for attempt in range(1, total_attempts + 1):

        try:
            print(
                f"Gemini pair request: attempt "
                f"{attempt}/{total_attempts}"
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    response_mime_type="application/json",
                ),
            )

            response_text = getattr(
                response,
                "text",
                None,
            )

            if not response_text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            parsed = extract_json(response_text)

            lessons = parsed.get("lessons")

            if not isinstance(lessons, list):
                raise ValueError(
                    "Gemini response does not contain a lessons list."
                )

            if len(lessons) != 2:
                raise ValueError(
                    f"Expected exactly 2 lessons, got {len(lessons)}."
                )

            validated_lessons = []

            for index, lesson in enumerate(lessons, start=1):
                validate_content(lesson)

                validated_lessons.append(lesson)

                print(
                    f"  Lesson {index} validated: "
                    f"{lesson.get('title', 'Untitled')}"
                )

            print(
                "Gemini pair request succeeded."
            )

            return validated_lessons

        except Exception as error:

            retryable = is_retryable_gemini_error(error)
            status_code = get_error_status_code(error)

            print(
                f"Gemini pair request failed "
                f"(attempt {attempt}/{total_attempts})."
            )

            if status_code is not None:
                print(
                    f"Gemini status code: {status_code}"
                )

            print(
                f"Gemini error: {error}"
            )

            # Never retry permanent/client-side problems.
            if not retryable:
                print(
                    "Error is not considered transient. "
                    "Stopping without retry."
                )
                raise

            # No retry remains.
            if attempt >= total_attempts:
                print(
                    "All Gemini retry attempts exhausted."
                )
                raise

            retry_number = attempt

            delay = get_retry_delay(
                retry_number
            )

            print(
                f"Transient Gemini error detected. "
                f"Waiting {delay:.1f} seconds before retry "
                f"{retry_number}/{MAX_RETRIES}..."
            )

            time.sleep(delay)

    raise RuntimeError(
        "Gemini content generation failed unexpectedly."
    )


# ============================================================
# PLAN METADATA
# ============================================================

def attach_plan_metadata(
    content: Dict[str, Any],
    plan_item: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Attach the planner information to generated content.
    """

    result = dict(content)

    result["slot"] = plan_item.get("slot")
    result["role"] = plan_item.get("role")
    result["knowledge_path"] = plan_item.get(
        "knowledge_path"
    )
    result["lesson_number"] = plan_item.get(
        "lesson_number"
    )
    result["previous_lesson"] = plan_item.get(
        "previous_lesson"
    )

    return result


# ============================================================
# DAILY BATCH GENERATION
# ============================================================

def generate_daily_content_batches(
    daily_plan: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generate all 10 daily lessons in five Gemini pair requests.

    Pairing:
        1 + 2
        3 + 4
        5 + 6
        7 + 8
        9 + 10
    """

    if len(daily_plan) != 10:
        raise ValueError(
            f"Daily plan must contain 10 items. "
            f"Received {len(daily_plan)}."
        )

    generated_content: List[Dict[str, Any]] = []

    pair_count = 5

    print(
        f"Starting daily batch generation: "
        f"{len(daily_plan)} lessons in {pair_count} Gemini pairs."
    )

    for pair_index in range(0, len(daily_plan), 2):

        lesson_a = daily_plan[pair_index]
        lesson_b = daily_plan[pair_index + 1]

        pair_number = (pair_index // 2) + 1

        print()
        print(
            "=" * 60
        )
        print(
            f"Generating Gemini pair "
            f"{pair_number}/{pair_count}"
        )
        print(
            "=" * 60
        )

        lessons = generate_content_pair(
            lesson_a,
            lesson_b,
        )

        for lesson, plan_item in zip(
            lessons,
            (lesson_a, lesson_b),
        ):
            enriched = attach_plan_metadata(
                lesson,
                plan_item,
            )

            validate_content(enriched)

            generated_content.append(
                enriched
            )

    if len(generated_content) != 10:
        raise RuntimeError(
            "Daily batch generation did not produce exactly 10 lessons."
        )

    reel_count = sum(
        1
        for item in generated_content
        if item.get("content_type") == "reel"
    )

    visual_count = sum(
        1
        for item in generated_content
        if item.get("content_type") == "educational_visual"
    )

    if reel_count != 5:
        raise RuntimeError(
            f"Expected 5 reels, generated {reel_count}."
        )

    if visual_count != 5:
        raise RuntimeError(
            f"Expected 5 educational visuals, generated {visual_count}."
        )

    print()
    print(
        "=" * 60
    )
    print(
        "DAILY GEMINI BATCH GENERATION COMPLETE"
    )
    print(
        f"Total lessons: {len(generated_content)}"
    )
    print(
        f"Reels: {reel_count}"
    )
    print(
        f"Educational visuals: {visual_count}"
    )
    print(
        "=" * 60
    )

    return generated_content


# ============================================================
# SIMPLE MODULE TEST
# ============================================================

if __name__ == "__main__":
    print(
        "content_batch_generator.py loaded successfully."
    )
    print(
        f"Gemini model: {MODEL_NAME}"
    )
    print(
        f"Maximum outer retries: {MAX_RETRIES}"
    )
    print(
        f"Base retry delay: {BASE_RETRY_DELAY}s"
    )
    print(
        f"Maximum retry delay: {MAX_RETRY_DELAY}s"
    )
