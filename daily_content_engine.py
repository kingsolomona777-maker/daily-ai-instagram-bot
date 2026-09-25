import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from content_batch_generator import (
    generate_content_pair,
    attach_plan_metadata,
)
from content_generator import check_content
from image_generator import (
    generate_image,
    make_vertical_image,
)
from reel_generator import generate_reel


OUTPUT_DIRECTORY = Path(
    "daily_generated_content"
)


def is_reel(item: Dict[str, Any]) -> bool:
    return item.get("content_type") == "reel"


def is_visual(item: Dict[str, Any]) -> bool:
    return (
        item.get("content_type")
        == "educational_visual"
    )


def generate_content_batches(
    daily_plan: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generate the 10 daily content lessons using
    five two-lesson Gemini batches.

    Expected structure:

        10 planned posts
              ↓
        5 pairs
              ↓
        5 Gemini requests
              ↓
        10 content lessons
    """

    if len(daily_plan) != 10:
        raise ValueError(
            "Daily content generation requires "
            "exactly 10 planned posts."
        )

    generated_posts = []

    for index in range(0, 10, 2):
        first_item = daily_plan[index]
        second_item = daily_plan[index + 1]

        print()
        print(
            "=========================================="
        )
        print(
            f"CONTENT BATCH "
            f"{(index // 2) + 1}/5"
        )
        print(
            "=========================================="
        )

        print(
            f"Lesson 1 slot: "
            f"{first_item['slot']}"
        )

        print(
            f"Lesson 2 slot: "
            f"{second_item['slot']}"
        )

        print(
            f"Lesson 1 topic: "
            f"{first_item['knowledge_area']}"
        )

        print(
            f"Lesson 2 topic: "
            f"{second_item['knowledge_area']}"
        )

        generated_pair = generate_content_pair(
            first_item=first_item,
            second_item=second_item,
        )

        pair_with_metadata = (
            attach_plan_metadata(
                generated_pair,
                [
                    first_item,
                    second_item,
                ],
            )
        )

        if len(pair_with_metadata) != 2:
            raise RuntimeError(
                "A content batch did not return "
                "exactly two lessons."
            )

        for content in pair_with_metadata:
            if not check_content(content):
                raise RuntimeError(
                    "Generated batch content failed "
                    "content validation."
                )

        generated_posts.extend(
            pair_with_metadata
        )

        print(
            f"Batch {(index // 2) + 1}/5 completed."
        )

    if len(generated_posts) != 10:
        raise RuntimeError(
            "Batch generation did not produce "
            "exactly 10 lessons."
        )

    reels = [
        item
        for item in generated_posts
        if is_reel(item)
    ]

    visuals = [
        item
        for item in generated_posts
        if is_visual(item)
    ]

    if len(reels) != 5:
        raise RuntimeError(
            "Batch generation did not produce "
            "exactly 5 Reels."
        )

    if len(visuals) != 5:
        raise RuntimeError(
            "Batch generation did not produce "
            "exactly 5 educational visuals."
        )

    return generated_posts


def generate_one_post(
    content: Dict[str, Any],
    output_directory: Path = OUTPUT_DIRECTORY,
) -> Dict[str, Any]:
    """
    Turn one already-generated content lesson into
    its final image and, when required, its Reel.

    No Gemini content request happens here.
    """

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    slot = int(content["slot"])
    content_type = content["content_type"]
    lesson_number = int(
        content["lesson_number"]
    )

    base_name = (
        f"lesson_{lesson_number:03d}"
        f"_slot_{slot:02d}"
    )

    raw_image = (
        output_directory
        / f"{base_name}_raw.jpg"
    )

    final_image = (
        output_directory
        / f"{base_name}.jpg"
    )

    reel_file = (
        output_directory
        / f"{base_name}.mp4"
    )

    print()
    print(
        "------------------------------------------"
    )
    print(
        f"Processing lesson {lesson_number}"
    )
    print(
        f"Slot: {slot}"
    )
    print(
        f"Type: {content_type}"
    )
    print(
        f"Topic: "
        f"{content['knowledge_area']}"
    )
    print(
        "------------------------------------------"
    )

    # ---------------------------------------------
    # Generate the source image.
    # ---------------------------------------------

    generated_image = generate_image(
        content["image_prompt"],
        str(raw_image),
    )

    if not Path(
        generated_image
    ).exists():
        raise RuntimeError(
            f"Image generation failed: "
            f"{generated_image}"
        )

    # ---------------------------------------------
    # Add educational text and prepare the final
    # vertical Instagram image.
    # ---------------------------------------------

    final_generated_image = (
        make_vertical_image(
            input_file=str(raw_image),
            output_file=str(final_image),
            on_image_text=content[
                "on_image_text"
            ],
        )
    )

    if not Path(
        final_generated_image
    ).exists():
        raise RuntimeError(
            f"Final image was not created: "
            f"{final_generated_image}"
        )

    # ---------------------------------------------
    # Generate Reel only for Reel slots.
    # ---------------------------------------------

    reel_enabled = False
    reel_path: Optional[str] = None

    if is_reel(content):
        teaching_text = {
            "hook": content[
                "on_image_text"
            ]["hook"],
            "explanation": content[
                "on_image_text"
            ]["explanation"],
            "takeaway": content[
                "on_image_text"
            ]["takeaway"],
        }

        generated_reel = generate_reel(
            input_file=str(final_image),
            output_file=str(reel_file),
            duration=8,
            teaching_text=teaching_text,
        )

        if not Path(
            generated_reel
        ).exists():
            raise RuntimeError(
                f"Reel generation failed: "
                f"{generated_reel}"
            )

        reel_enabled = True
        reel_path = str(reel_file)

    # ---------------------------------------------
    # Create the final package for this lesson.
    # ---------------------------------------------

    package = {
        "slot": slot,
        "content_type": content_type,
        "role": content.get(
            "role",
            "",
        ),
        "lesson_type": content.get(
            "lesson_type",
            "",
        ),
        "knowledge_path": content.get(
            "knowledge_path",
            "",
        ),
        "knowledge_area": content.get(
            "knowledge_area",
            "",
        ),
        "lesson_number": lesson_number,
        "title": content["title"],
        "description": content[
            "description"
        ],
        "image_prompt": content[
            "image_prompt"
        ],
        "hashtags": content[
            "hashtags"
        ],
        "visual_story": content[
            "visual_story"
        ],
        "on_image_text": content[
            "on_image_text"
        ],
        "image_file": str(
            final_image
        ),
        "reel_enabled": reel_enabled,
        "reel_file": reel_path,
    }

    return package


def generate_daily_content(
    daily_plan: List[Dict[str, Any]],
    output_directory: Path = OUTPUT_DIRECTORY,
) -> List[Dict[str, Any]]:
    """
    Generate the complete 10-post day.

    Stage 1:
        Generate 10 lessons through 5 Gemini batches.

    Stage 2:
        Generate images for all 10 lessons.

    Stage 3:
        Generate Reels for the 5 Reel lessons.
    """

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print(
        "=========================================="
    )
    print(
        "OROM PLAN1 DAILY CONTENT ENGINE"
    )
    print(
        "=========================================="
    )
    print(
        "Target: 10 posts"
    )
    print(
        "Reels: 5"
    )
    print(
        "Educational visuals: 5"
    )
    print(
        "Gemini batch requests: 5"
    )
    print(
        "=========================================="
    )

    # ---------------------------------------------
    # STAGE 1
    # Generate all 10 lessons using 5 batches.
    # ---------------------------------------------

    generated_content = (
        generate_content_batches(
            daily_plan
        )
    )

    if len(generated_content) != 10:
        raise RuntimeError(
            "Stage 1 did not produce 10 lessons."
        )

    print()
    print(
        "=========================================="
    )
    print(
        "STAGE 1 COMPLETE"
    )
    print(
        "10 lessons generated from 5 batches."
    )
    print(
        "=========================================="
    )

    # ---------------------------------------------
    # STAGE 2 + 3
    # Turn the generated lessons into media.
    # ---------------------------------------------

    generated_posts = []

    for content in generated_content:
        package = generate_one_post(
            content=content,
            output_directory=output_directory,
        )

        generated_posts.append(
            package
        )

    # ---------------------------------------------
    # Final validation.
    # ---------------------------------------------

    if len(generated_posts) != 10:
        raise RuntimeError(
            "Daily engine did not produce "
            "10 final posts."
        )

    reels = [
        item
        for item in generated_posts
        if is_reel(item)
    ]

    visuals = [
        item
        for item in generated_posts
        if is_visual(item)
    ]

    successful_images = [
        item
        for item in generated_posts
        if Path(
            item["image_file"]
        ).exists()
    ]

    successful_reels = [
        item
        for item in generated_posts
        if item["reel_enabled"]
        and item["reel_file"]
        and Path(
            item["reel_file"]
        ).exists()
    ]

    if len(reels) != 5:
        raise RuntimeError(
            "Final daily package must contain "
            "5 Reels."
        )

    if len(visuals) != 5:
        raise RuntimeError(
            "Final daily package must contain "
            "5 educational visuals."
        )

    if len(successful_images) != 10:
        raise RuntimeError(
            "All 10 posts must have valid images."
        )

    if len(successful_reels) != 5:
        raise RuntimeError(
            "All 5 Reel posts must have valid "
            "Reel files."
        )

    print()
    print(
        "=========================================="
    )
    print(
        "DAILY CONTENT GENERATION COMPLETE"
    )
    print(
        "=========================================="
    )
    print(
        "Posts: 10"
    )
    print(
        "Reels: 5"
    )
    print(
        "Educational visuals: 5"
    )
    print(
        "Images: 10"
    )
    print(
        "Reels generated: 5"
    )
    print(
        "Gemini content batches: 5"
    )
    print(
        "=========================================="
    )

    return generated_posts


def save_daily_package(
    generated_posts: List[Dict[str, Any]],
    output_file: Path = Path(
        "daily_generated_content.json"
    ),
) -> Path:
    """
    Save the complete daily content package.
    """

    reels = [
        item
        for item in generated_posts
        if is_reel(item)
    ]

    visuals = [
        item
        for item in generated_posts
        if is_visual(item)
    ]

    payload = {
        "total_posts": len(
            generated_posts
        ),
        "reels": len(reels),
        "educational_visuals": len(
            visuals
        ),
        "posts": generated_posts,
    }

    with Path(
        output_file
    ).open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"Daily package saved to: "
        f"{output_file}"
    )

    return Path(output_file)


def summarize_daily_content(
    generated_posts: List[Dict[str, Any]],
) -> Dict[str, int]:
    """
    Return a simple summary of the generated day.
    """

    reels = [
        item
        for item in generated_posts
        if is_reel(item)
    ]

    visuals = [
        item
        for item in generated_posts
        if is_visual(item)
    ]

    successful_images = [
        item
        for item in generated_posts
        if Path(
            item["image_file"]
        ).exists()
    ]

    successful_reels = [
        item
        for item in generated_posts
        if item.get("reel_enabled")
        and item.get("reel_file")
        and Path(
            item["reel_file"]
        ).exists()
    ]

    return {
        "total_posts": len(
            generated_posts
        ),
        "reels": len(reels),
        "educational_visuals": len(
            visuals
        ),
        "successful_images": len(
            successful_images
        ),
        "successful_reels": len(
            successful_reels
        ),
    }


if __name__ == "__main__":
    print(
        "Orom Plan1 daily content engine loaded."
    )
    print(
        "Architecture:"
    )
    print(
        "10 planned posts"
    )
    print(
        "-> 5 content batches"
    )
    print(
        "-> 10 lessons"
    )
    print(
        "-> 10 images"
    )
    print(
        "-> 5 Reels + 5 educational visuals"
    )
