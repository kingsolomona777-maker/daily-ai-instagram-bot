import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from content_generator import create_content, check_content
from image_generator import generate_image, make_vertical_image
from reel_generator import generate_reel


# ============================================================
# OROM PLAN1 - DAILY CONTENT GENERATION ENGINE
# ============================================================

OUTPUT_DIRECTORY = Path("daily_generated_content")


# ============================================================
# CONTENT TYPE HELPERS
# ============================================================

def is_reel(item: Dict[str, Any]) -> bool:
    return item.get("content_type") == "reel"


def is_visual(item: Dict[str, Any]) -> bool:
    return item.get("content_type") == "educational_visual"


# ============================================================
# CONTENT GENERATION
# ============================================================

def generate_one_post(
    plan_item: Dict[str, Any],
    output_directory: Path = OUTPUT_DIRECTORY,
    previous_lesson: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate one complete Orom Plan1 post from a planner item.

    This function handles:
        planner item
            ↓
        Gemini lesson
            ↓
        AI image
            ↓
        educational image overlay
            ↓
        optional Reel
    """

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    slot = int(plan_item["slot"])
    content_type = plan_item["content_type"]
    topic = plan_item["knowledge_area"]
    lesson_type = plan_item["lesson_type"]
    lesson_number = int(plan_item["lesson_number"])

    previous = (
        previous_lesson
        or plan_item.get("previous_lesson")
        or ""
    )

    print()
    print("=" * 60)
    print(
        f"GENERATING SLOT {slot}/10 | "
        f"{content_type.upper()}"
    )
    print("=" * 60)
    print(f"Knowledge path: {plan_item.get('knowledge_path', '')}")
    print(f"Knowledge area: {topic}")
    print(f"Lesson type: {lesson_type}")
    print(f"Lesson number: {lesson_number}")

    # --------------------------------------------------------
    # Generate the educational lesson.
    # --------------------------------------------------------

    content = create_content(
        topic=topic,
        content_type=content_type,
        lesson_type=lesson_type,
        lesson_number=lesson_number,
        previous_lesson=previous,
    )

    if not check_content(content):
        raise RuntimeError(
            f"Content quality check failed for slot {slot}."
        )

    # --------------------------------------------------------
    # File names.
    # --------------------------------------------------------

    base_name = (
        f"lesson_{lesson_number:03d}_"
        f"slot_{slot:02d}"
    )

    raw_image = (
        output_directory /
        f"{base_name}_raw.jpg"
    )

    final_image = (
        output_directory /
        f"{base_name}.jpg"
    )

    reel_file = (
        output_directory /
        f"{base_name}.mp4"
    )

    # --------------------------------------------------------
    # Generate the AI image.
    # --------------------------------------------------------

    print()
    print("Generating educational image...")

    generated_image = generate_image(
        content["image_prompt"],
        str(raw_image)
    )

    if not Path(generated_image).exists():
        raise RuntimeError(
            f"Image generator did not create an image for slot {slot}."
        )

    # --------------------------------------------------------
    # Add educational text to the image.
    # --------------------------------------------------------

    print("Creating final educational visual...")

    final_generated_image = make_vertical_image(
        input_file=str(raw_image),
        output_file=str(final_image),
        on_image_text=content["on_image_text"],
    )

    if not Path(final_generated_image).exists():
        raise RuntimeError(
            f"Final educational image was not created for slot {slot}."
        )

    # --------------------------------------------------------
    # Generate Reel when this is a Reel slot.
    # --------------------------------------------------------

    reel_enabled = False
    reel_path = None

    if is_reel(plan_item):
        print()
        print("Generating educational Reel...")

        teaching_text = {
            "hook": content["on_image_text"]["hook"],
            "explanation": content["on_image_text"]["explanation"],
            "takeaway": content["on_image_text"]["takeaway"],
        }

        generated_reel = generate_reel(
            input_file=str(final_image),
            output_file=str(reel_file),
            duration=8,
            teaching_text=teaching_text,
        )

        if not Path(generated_reel).exists():
            raise RuntimeError(
                f"Reel was not created for slot {slot}."
            )

        reel_enabled = True
        reel_path = str(reel_file)

    # --------------------------------------------------------
    # Build the completed content package.
    # --------------------------------------------------------

    package = {
        "slot": slot,
        "content_type": content_type,
        "role": plan_item.get("role", ""),
        "lesson_type": lesson_type,
        "knowledge_path": plan_item.get(
            "knowledge_path",
            ""
        ),
        "knowledge_area": topic,
        "lesson_number": lesson_number,

        "title": content["title"],
        "description": content["description"],
        "image_prompt": content["image_prompt"],
        "hashtags": content["hashtags"],
        "visual_story": content["visual_story"],
        "on_image_text": content["on_image_text"],

        "image_file": str(final_image),

        "reel_enabled": reel_enabled,
        "reel_file": reel_path,
    }

    print()
    print(
        f"✅ Slot {slot} generated successfully."
    )

    return package


# ============================================================
# DAILY GENERATION
# ============================================================

def generate_daily_content(
    daily_plan: List[Dict[str, Any]],
    output_directory: Path = OUTPUT_DIRECTORY,
) -> List[Dict[str, Any]]:
    """
    Generate all posts in a supplied daily plan.

    The planner decides WHAT should be created.
    This engine decides HOW to create it.
    """

    if not daily_plan:
        raise ValueError(
            "Daily plan is empty."
        )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    generated_posts = []

    previous_lesson = None

    total = len(daily_plan)

    print()
    print("=" * 60)
    print("OROM PLAN1 - DAILY CONTENT GENERATION")
    print("=" * 60)
    print(f"Posts planned: {total}")
    print("=" * 60)

    for index, plan_item in enumerate(
        daily_plan,
        start=1
    ):
        print()
        print(
            f"Progress: {index}/{total}"
        )

        package = generate_one_post(
            plan_item=plan_item,
            output_directory=output_directory,
            previous_lesson=previous_lesson,
        )

        generated_posts.append(package)

        previous_lesson = package["title"]

    print()
    print("=" * 60)
    print("DAILY CONTENT GENERATION COMPLETE")
    print("=" * 60)
    print(
        f"Completed packages: "
        f"{len(generated_posts)}"
    )

    reels = sum(
        1
        for item in generated_posts
        if item["content_type"] == "reel"
    )

    visuals = sum(
        1
        for item in generated_posts
        if item["content_type"] == "educational_visual"
    )

    print(f"Reels: {reels}")
    print(f"Educational visuals: {visuals}")
    print("=" * 60)

    return generated_posts


# ============================================================
# DAILY PACKAGE STORAGE
# ============================================================

def save_daily_package(
    generated_posts: List[Dict[str, Any]],
    output_file: Path = Path(
        "daily_generated_content.json"
    ),
) -> Path:
    """
    Save the complete day's generated content metadata.
    """

    payload = {
        "total_posts": len(generated_posts),
        "reels": sum(
            1
            for item in generated_posts
            if item["content_type"] == "reel"
        ),
        "educational_visuals": sum(
            1
            for item in generated_posts
            if item["content_type"]
            == "educational_visual"
        ),
        "posts": generated_posts,
    }

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Daily package saved to: {output_file}"
    )

    return output_file


# ============================================================
# SUMMARY
# ============================================================

def summarize_daily_content(
    generated_posts: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Produce a compact summary for logs and future automation.
    """

    return {
        "total_posts": len(generated_posts),
        "reels": sum(
            1
            for item in generated_posts
            if item["content_type"] == "reel"
        ),
        "educational_visuals": sum(
            1
            for item in generated_posts
            if item["content_type"]
            == "educational_visual"
        ),
        "successful_images": sum(
            1
            for item in generated_posts
            if item.get("image_file")
        ),
        "successful_reels": sum(
            1
            for item in generated_posts
            if item.get("reel_enabled")
            and item.get("reel_file")
        ),
    }


# ============================================================
# SAFE MODULE TEST
# ============================================================

if __name__ == "__main__":
    print(
        "daily_content_engine.py loaded successfully."
    )

    print()
    print("Available functions:")
    print("- generate_one_post()")
    print("- generate_daily_content()")
    print("- save_daily_package()")
    print("- summarize_daily_content()")

    print()
    print(
        "No AI generation was started by this module test."
    )
