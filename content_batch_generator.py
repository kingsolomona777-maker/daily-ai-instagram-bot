import json
import random
import re
import time
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "gemini-3.6-flash"
FALLBACK_MODEL_NAME = "gemini-3.5-flash-lite"

MAX_RETRIES = 2

BASE_RETRY_DELAY = 8
MAX_RETRY_DELAY = 30
MAX_JITTER = 3


# ============================================================
# GEMINI CLIENT
# ============================================================

import os


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is missing."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# ERROR HELPERS
# ============================================================

def get_error_status_code(error: Exception) -> Optional[int]:
    """
    Try to extract an HTTP/status code from a Gemini error.
    """

    for attribute in (
        "code",
        "status_code",
        "http_status",
    ):
        value = getattr(error, attribute, None)

        if isinstance(value, int):
            return value

    message = str(error)

    match = re.search(
        r"\b(429|500|502|503|504)\b",
        message,
    )

    if match:
        return int(match.group(1))

    return None


def is_retryable_gemini_error(error: Exception) -> bool:
    """
    Return True when the error appears to be temporary.
    """

    status_code = get_error_status_code(error)

    if status_code in (
        429,
        500,
        502,
        503,
        504,
    ):
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

    return any(
        marker in message
        for marker in transient_markers
    )


def get_retry_delay(retry_number: int) -> float:
    """
    Exponential backoff with small random jitter.

    retry_number:
        1 = approximately 8 seconds
        2 = approximately 16 seconds
    """

    delay = min(
        BASE_RETRY_DELAY * (2 ** (retry_number - 1)),
        MAX_RETRY_DELAY,
    )

    delay += random.uniform(
        0,
        MAX_JITTER,
    )

    return delay


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract JSON safely from Gemini output.
    """

    text = text.strip()

    if not text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    # Direct JSON
    try:
        data = json.loads(text)

        if isinstance(data, dict):
            return data

    except json.JSONDecodeError:
        pass

    # Remove markdown code fences if present
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    ).strip()

    try:
        data = json.loads(cleaned)

        if isinstance(data, dict):
            return data

    except json.JSONDecodeError:
        pass

    # Find first JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start:end + 1]

        try:
            data = json.loads(candidate)

            if isinstance(data, dict):
                return data

        except json.JSONDecodeError:
            pass

    raise ValueError(
        "Could not extract valid JSON from Gemini response."
    )


# ============================================================
# CONTENT VALIDATION
# ============================================================

REQUIRED_CONTENT_FIELDS = [
    "title",
    "description",
    "image_prompt",
    "hashtags",
    "visual_story",
    "on_image_text",
    "lesson_type",
    "content_type",
    "knowledge_area",
    "lesson_number",
]


def validate_generated_content(
    content: Dict[str, Any]
) -> bool:
    """
    Validate the structure returned by Gemini.
    """

    if not isinstance(content, dict):
        return False

    for field in REQUIRED_CONTENT_FIELDS:
        if field not in content:
            return False

    if not isinstance(
        content["title"],
        str,
    ):
        return False

    if not isinstance(
        content["description"],
        str,
    ):
        return False

    if not isinstance(
        content["image_prompt"],
        str,
    ):
        return False

    if not isinstance(
        content["hashtags"],
        list,
    ):
        return False

    if not isinstance(
        content["on_image_text"],
        dict,
    ):
        return False

    required_text_fields = [
        "hook",
        "explanation",
        "callout",
        "takeaway",
    ]

    for field in required_text_fields:
        if field not in content["on_image_text"]:
            return False

    return True


# ============================================================
# PROMPT BUILDER
# ============================================================

def build_pair_prompt(
    first_lesson: Dict[str, Any],
    second_lesson: Dict[str, Any],
) -> str:
    """
    Build the prompt for two related lessons.

    The pair shares one broader teaching path while each
    lesson remains independently useful.
    """

    return f"""
You are the educational content engine for Orom Plan1,
a professional plumbing education platform.

Generate TWO distinct plumbing lessons.

The goal is to teach the audience practical, accurate,
professional plumbing knowledge.

LESSON 1 PLAN:
{json.dumps(first_lesson, indent=2, ensure_ascii=False)}

LESSON 2 PLAN:
{json.dumps(second_lesson, indent=2, ensure_ascii=False)}

IMPORTANT TECHNICAL RULES:

1. Information must be technically responsible.
2. Do not invent pipe sizes, slopes, dimensions, standards,
   regulations, or product specifications.
3. If a measurement depends on local code, building design,
   manufacturer instructions, or site conditions, do not
   invent a universal number.
4. Avoid unsafe instructions.
5. Keep each lesson focused on one main teaching idea.
6. Each lesson must be useful as a standalone piece of content.
7. The image prompt must describe a realistic plumbing scene.
8. AI-generated images must contain no text, logo, or watermark.
9. Image prompts should describe a vertical 9:16 composition.
10. The educational text will be added separately by Python.

For EACH lesson return:

- title
- description
- image_prompt
- hashtags
- visual_story
- on_image_text
- lesson_type
- content_type
- knowledge_area
- lesson_number

The "on_image_text" object must contain:

- hook
- explanation
- callout
- takeaway

The description should normally be approximately 80 to 120
words and should teach rather than merely advertise.

Return ONLY valid JSON.

The JSON must have exactly this top-level structure:

{{
  "lessons": [
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
      "lesson_number": 1
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
      }},
      "lesson_type": "...",
      "content_type": "...",
      "knowledge_area": "...",
      "lesson_number": 2
    }}
  ]
}}
"""


# ============================================================
# MODEL REQUEST
# ============================================================

def generate_pair_with_model(
    model_name: str,
    first_lesson: Dict[str, Any],
    second_lesson: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Generate one pair using the specified Gemini model.

    This function contains bounded retries.
    """

    prompt = build_pair_prompt(
        first_lesson,
        second_lesson,
    )

    last_error: Optional[Exception] = None

    for attempt in range(
        MAX_RETRIES + 1
    ):
        attempt_number = attempt + 1

        print(
            f"  Model: {model_name}"
        )

        print(
            f"  Attempt: "
            f"{attempt_number}/{MAX_RETRIES + 1}"
        )

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )

            response_text = (
                response.text or ""
            ).strip()

            if not response_text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            parsed = extract_json(
                response_text
            )

            lessons = parsed.get(
                "lessons"
            )

            if not isinstance(
                lessons,
                list,
            ):
                raise ValueError(
                    "Gemini response does not contain "
                    "a valid 'lessons' list."
                )

            if len(lessons) != 2:
                raise ValueError(
                    "Gemini response must contain exactly "
                    "two lessons."
                )

            validated_lessons = []

            for lesson in lessons:
                if not validate_generated_content(
                    lesson
                ):
                    raise ValueError(
                        "Generated lesson failed "
                        "content validation."
                    )

                lesson = dict(lesson)

                lesson["_model_used"] = (
                    model_name
                )

                validated_lessons.append(
                    lesson
                )

            print(
                f"  SUCCESS: {model_name}"
            )

            return validated_lessons

        except Exception as error:
            last_error = error

            status_code = (
                get_error_status_code(error)
            )

            print(
                f"  ERROR from {model_name}"
            )

            print(
                f"  Status: {status_code}"
            )

            print(
                f"  Error: {error}"
            )

            retry_allowed = (
                attempt < MAX_RETRIES
                and is_retryable_gemini_error(
                    error
                )
            )

            if retry_allowed:
                delay = get_retry_delay(
                    attempt_number
                )

                print(
                    f"  Temporary Gemini error."
                )

                print(
                    f"  Waiting approximately "
                    f"{delay:.1f}s before retry..."
                )

                time.sleep(delay)

            else:
                break

    if last_error is None:
        raise RuntimeError(
            f"{model_name} failed without "
            "returning an error."
        )

    raise last_error


# ============================================================
# PRIMARY + FALLBACK GENERATION
# ============================================================

def generate_content_pair(
    first_lesson: Dict[str, Any],
    second_lesson: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Generate two lessons.

    Strategy:

    1. Try Gemini 3.6 Flash.
    2. Retry transient failures with exponential backoff.
    3. If the primary model still fails because of a
       transient problem, switch to Gemini 3.5 Flash-Lite.
    4. Retry the fallback model.
    5. Stop safely if both models fail.

    Non-transient errors are not unnecessarily retried
    or sent to the fallback model.
    """

    print("")
    print(
        "================================================"
    )
    print(
        "GENERATING CONTENT PAIR"
    )
    print(
        "================================================"
    )

    primary_error: Optional[Exception] = None

    # --------------------------------------------------------
    # PRIMARY MODEL
    # --------------------------------------------------------

    try:
        print("")
        print(
            f"PRIMARY MODEL: {MODEL_NAME}"
        )

        return generate_pair_with_model(
            MODEL_NAME,
            first_lesson,
            second_lesson,
        )

    except Exception as error:
        primary_error = error

        print("")
        print(
            "Primary model exhausted its "
            "allowed attempts."
        )

        print(
            f"Primary error: {error}"
        )

    # --------------------------------------------------------
    # ONLY FALL BACK FOR TRANSIENT GEMINI ERRORS
    # --------------------------------------------------------

    if not is_retryable_gemini_error(
        primary_error
    ):
        raise primary_error

    # --------------------------------------------------------
    # FALLBACK MODEL
    # --------------------------------------------------------

    print("")
    print(
        "================================================"
    )
    print(
        "SWITCHING TO FALLBACK MODEL"
    )
    print(
        "================================================"
    )

    print(
        f"Fallback model: {FALLBACK_MODEL_NAME}"
    )

    try:
        return generate_pair_with_model(
            FALLBACK_MODEL_NAME,
            first_lesson,
            second_lesson,
        )

    except Exception as fallback_error:
        print("")
        print(
            "Fallback model also failed."
        )

        print(
            f"Fallback error: {fallback_error}"
        )

        raise RuntimeError(
            "Both Gemini models failed. "
            f"Primary: {primary_error} | "
            f"Fallback: {fallback_error}"
        ) from fallback_error


# ============================================================
# PLAN METADATA
# ============================================================

def attach_plan_metadata(
    content: Dict[str, Any],
    plan_item: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Attach planner metadata without destroying generated
    content.
    """

    result = dict(content)

    result["slot"] = plan_item.get(
        "slot"
    )

    result["role"] = plan_item.get(
        "role"
    )

    result["knowledge_path"] = (
        plan_item.get(
            "knowledge_path"
        )
    )

    result["previous_lesson"] = (
        plan_item.get(
            "previous_lesson"
        )
    )

    if plan_item.get("lesson_type"):
        result["lesson_type"] = (
            plan_item["lesson_type"]
        )

    if plan_item.get("content_type"):
        result["content_type"] = (
            plan_item["content_type"]
        )

    if plan_item.get("knowledge_area"):
        result["knowledge_area"] = (
            plan_item["knowledge_area"]
        )

    if plan_item.get("lesson_number"):
        result["lesson_number"] = (
            plan_item["lesson_number"]
        )

    return result


# ============================================================
# BATCH GENERATION
# ============================================================

def generate_content_batches(
    daily_plan: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate a complete 10-post content batch.

    The daily plan contains 10 lessons.

    Gemini is called in five pairs:

        Pair 1 -> posts 1 + 2
        Pair 2 -> posts 3 + 4
        Pair 3 -> posts 5 + 6
        Pair 4 -> posts 7 + 8
        Pair 5 -> posts 9 + 10

    This reduces the number of Gemini requests while
    preserving 10 independent pieces of content.
    """

    if not isinstance(
        daily_plan,
        list,
    ):
        raise TypeError(
            "daily_plan must be a list."
        )

    if len(daily_plan) != 10:
        raise ValueError(
            "daily_plan must contain exactly 10 items."
        )

    all_content: List[Dict[str, Any]] = []

    for pair_index in range(5):
        first_index = pair_index * 2
        second_index = first_index + 1

        first_plan = daily_plan[
            first_index
        ]

        second_plan = daily_plan[
            second_index
        ]

        print("")
        print(
            "================================================"
        )
        print(
            f"CONTENT PAIR "
            f"{pair_index + 1}/5"
        )
        print(
            f"Posts {first_index + 1} "
            f"and {second_index + 1}"
        )
        print(
            "================================================"
        )

        pair_content = generate_content_pair(
            first_plan,
            second_plan,
        )

        if len(pair_content) != 2:
            raise RuntimeError(
                "Content pair did not return "
                "exactly two lessons."
            )

        first_content = attach_plan_metadata(
            pair_content[0],
            first_plan,
        )

        second_content = attach_plan_metadata(
            pair_content[1],
            second_plan,
        )

        if not validate_generated_content(
            first_content
        ):
            raise ValueError(
                f"Post {first_index + 1} "
                "failed final validation."
            )

        if not validate_generated_content(
            second_content
        ):
            raise ValueError(
                f"Post {second_index + 1} "
                "failed final validation."
            )

        all_content.append(
            first_content
        )

        all_content.append(
            second_content
        )

        print("")
        print(
            f"Pair {pair_index + 1} completed."
        )

    if len(all_content) != 10:
        raise RuntimeError(
            "Batch generation did not produce "
            "exactly 10 posts."
        )

    reel_count = sum(
        1
        for item in all_content
        if item.get("content_type")
        == "reel"
    )

    visual_count = sum(
        1
        for item in all_content
        if item.get("content_type")
        == "educational_visual"
    )

    if reel_count != 5:
        raise RuntimeError(
            f"Expected 5 reels, got {reel_count}."
        )

    if visual_count != 5:
        raise RuntimeError(
            "Expected 5 educational visuals, "
            f"got {visual_count}."
        )

    print("")
    print(
        "================================================"
    )
    print(
        "10-POST CONTENT BATCH COMPLETE"
    )
    print(
        "================================================"
    )

    print(
        f"Total posts: {len(all_content)}"
    )

    print(
        f"Reels: {reel_count}"
    )

    print(
        f"Educational visuals: {visual_count}"
    )

    return all_content
