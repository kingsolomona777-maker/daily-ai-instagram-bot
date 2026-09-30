import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from content_batch_generator import (
    generate_content_batches,
    attach_plan_metadata,
)
from content_generator import check_content
from image_generator import (
    generate_image,
    make_vertical_image,
)
from reel_generator import generate_reel


OUTPUT_DIRECTORY = Path("daily_generated_content")


def is_reel(item: Dict[str, Any]) -> bool:
    return item.get("content_type") == "reel"


def is_visual(item: Dict[str, Any]) -> bool:
    return item.get("content_type") == "educational_visual"


def get_reel_audio_file() -> Optional[Path]:
    """
    Find the optional local Reel audio file.

    The audio path is supplied through:

        OROM_PLAN1_AUDIO_FILE

    If the variable is missing or the file does not exist,
    Reel generation continues without audio.

    This keeps the engine compatible with existing tests
    while allowing production audio to be connected later.
    """

    configured_audio = os.getenv(
        "OROM_PLAN1_AUDIO_FILE",
        "",
    ).strip()

    if not configured_audio:
        return None

    audio_path = Path(configured_audio)

    if not audio_path.exists():
        raise RuntimeError(
            "OROM_PLAN1_AUDIO_FILE was configured, "
            f"but the audio file does not exist: {audio_path}"
        )

    if not audio_path.is_file():
        raise RuntimeError(
            "OROM_PLAN1_AUDIO_FILE does not point to a file: "
            f"{audio_path}"
        )

    print(
        f"Reel audio enabled: {audio_path}"
    )

    return audio_path


def validate_content_list(
    generated_content: List[Dict[str, Any]],
) -> None:
    """
    Validate an already-generated 10-post content package.

    This function performs validation only.
    It does NOT call Gemini.
    """

    if len(generated_content) != 10:
        raise RuntimeError(
            "Content package must contain exactly 10 lessons."
        )

    reels = [
        item
        for item in generated_content
        if is_reel(item)
    ]

    visuals = [
        item
        for item in generated_content
        if is_visual(item)
    ]

    if len(reels) != 5:
        raise RuntimeError(
            "Content package must contain exactly 5 Reels."
        )

    if len(visuals) != 5:
        raise RuntimeError(
            "Content package must contain exactly 5 educational visuals."
        )

    for index, content in enumerate(
        generated_content,
        start=1,
    ):

        if not isinstance(content, dict):
            raise RuntimeError(
                f"Lesson {index} is not a valid content object."
            )

        if not check_content(content):
            raise RuntimeError(
                f"Lesson {index} failed content validation."
            )

        required_fields = [
            "title",
            "description",
            "image_prompt",
            "hashtags",
            "visual_story",
            "on_image_text",
            "content_type",
            "lesson_number",
            "slot",
        ]

        for field in required_fields:
            if field not in content:
                raise RuntimeError(
                    f"Lesson {index} is missing required field: {field}"
                )


def generate_one_post(
    content: Dict[str, Any],
    output_directory: Path = OUTPUT_DIRECTORY,
    audio_file: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Turn one already-generated lesson into its final media.

    IMPORTANT:
    No Gemini request happens inside this function.

    For Reel lessons:
        - generate the Reel
        - optionally attach the supplied local audio file

    Educational visual lessons receive only the final image.
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
    print("------------------------------------------")
    print(
        f"PROCESSING LESSON {lesson_number}"
    )
    print(f"Slot: {slot}")
    print(f"Type: {content_type}")
    print(
        f"Topic: {content.get('knowledge_area', '')}"
    )
    print("------------------------------------------")

    # ------------------------------------------------
    # STEP 1: Generate source image
    # ------------------------------------------------

    print("Generating source image...")

    generated_image = generate_image(
        content["image_prompt"],
        str(raw_image),
    )

    if not Path(
        generated_image
    ).exists():
        raise RuntimeError(
            f"Image generation failed: {generated_image}"
        )

    # ------------------------------------------------
    # STEP 2: Create final 1080x1920 image
    # ------------------------------------------------

    print("Creating 9:16 educational image...")

    final_generated_image = make_vertical_image(
        input_file=str(raw_image),
        output_file=str(final_image),
        on_image_text=content["on_image_text"],
    )

    if not Path(
        final_generated_image
    ).exists():
        raise RuntimeError(
            f"Final image was not created: "
            f"{final_generated_image}"
        )

    # ------------------------------------------------
    # STEP 3: Generate Reel for Reel lessons
    # ------------------------------------------------

    reel_enabled = False
    reel_path: Optional[str] = None
    reel_audio_path: Optional[str] = None

    if is_reel(content):

        print("Generating Reel...")

        on_image_text = content[
            "on_image_text"
        ]

        teaching_text = {
            "hook": on_image_text.get(
                "hook",
                "",
            ),
            "explanation": on_image_text.get(
                "explanation",
                "",
            ),
            "takeaway": on_image_text.get(
                "takeaway",
                "",
            ),
        }

        if audio_file is not None:
            print(
                f"Using Reel audio: {audio_file}"
            )

            reel_audio_path = str(
                audio_file
            )

        else:
            print(
                "No Reel audio configured. "
                "Generating silent Reel."
            )

        generated_reel = generate_reel(
            input_file=str(final_image),
            output_file=str(reel_file),
            duration=8,
            teaching_text=teaching_text,
            audio_file=(
                str(audio_file)
                if audio_file is not None
                else None
            ),
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

    # ------------------------------------------------
    # STEP 4: Build final package
    # ------------------------------------------------

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
        "description": content["description"],
        "image_prompt": content["image_prompt"],
        "hashtags": content["hashtags"],
        "visual_story": content["visual_story"],
        "on_image_text": content["on_image_text"],
        "image_file": str(final_image),
        "reel_enabled": reel_enabled,
        "reel_file": reel_path,
        "reel_audio_file": reel_audio_path,
    }

    return package


def generate_media_from_content(
    generated_content: List[Dict[str, Any]],
    output_directory: Path = OUTPUT_DIRECTORY,
    audio_file: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Generate all media from an EXISTING 10-post content package.

    Gemini is NOT called here.

    If audio_file is supplied, it is attached to every Reel.
    """

    print()
    print("==========================================")
    print("OROM PLAN1 MEDIA GENERATION")
    print("==========================================")
    print("Existing lessons received: 10")
    print("Gemini requests from this stage: 0")
    print("Target images: 10")
    print("Target Reels: 5")
    print("Target educational visuals: 5")

    if audio_file is not None:
        print(
            f"Reel audio: {audio_file}"
        )
    else:
        print(
            "Reel audio: NOT CONFIGURED"
        )

    print("==========================================")

    validate_content_list(
        generated_content
    )

    generated_posts = []

    for content in generated_content:

        package = generate_one_post(
            content=content,
            output_directory=output_directory,
            audio_file=audio_file,
        )

        generated_posts.append(
            package
        )

    # ------------------------------------------------
    # Final media validation
    # ------------------------------------------------

    if len(generated_posts) != 10:
        raise RuntimeError(
            "Media generation did not produce "
            "exactly 10 posts."
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
        if (
            item["reel_enabled"]
            and item["reel_file"]
            and Path(
                item["reel_file"]
            ).exists()
        )
    ]

    if len(reels) != 5:
        raise RuntimeError(
            "Final package must contain exactly 5 Reels."
        )

    if len(visuals) != 5:
        raise RuntimeError(
            "Final package must contain exactly "
            "5 educational visuals."
        )

    if len(successful_images) != 10:
        raise RuntimeError(
            "All 10 posts must have valid images."
        )

    if len(successful_reels) != 5:
        raise RuntimeError(
            "All 5 Reel posts must have valid Reel files."
        )

    print()
    print("==========================================")
    print("MEDIA GENERATION COMPLETE")
    print("==========================================")
    print("Posts: 10")
    print("Images: 10")
    print("Reels: 5")
    print("Educational visuals: 5")

    if audio_file is not None:
        print("Reel audio: ENABLED")
    else:
        print("Reel audio: NOT CONFIGURED")

    print("Gemini requests during media stage: 0")
    print("==========================================")

    return generated_posts


def generate_daily_content(
    daily_plan: List[Dict[str, Any]],
    output_directory: Path = OUTPUT_DIRECTORY,
    generated_content: Optional[
        List[Dict[str, Any]]
    ] = None,
    audio_file: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Generate the complete daily 10-post package.

    If generated_content is supplied:
        use it directly and DO NOT call Gemini again.

    If generated_content is not supplied:
        generate the 10 lessons using five Gemini batches,
        then generate the media.

    Audio can be supplied explicitly with audio_file.

    If audio_file is not supplied, the engine checks:

        OROM_PLAN1_AUDIO_FILE

    If no audio is configured, Reels remain silent.
    """

    if len(daily_plan) != 10:
        raise ValueError(
            "Daily content generation requires exactly 10 plan items."
        )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------
    # Resolve optional Reel audio
    # ------------------------------------------------

    if audio_file is None:
        audio_file = get_reel_audio_file()

    if audio_file is not None:
        audio_file = Path(audio_file)

        if not audio_file.exists():
            raise RuntimeError(
                f"Reel audio file does not exist: {audio_file}"
            )

    print()
    print("==========================================")
    print("OROM PLAN1 DAILY CONTENT ENGINE")
    print("==========================================")
    print("Target: 10 posts")
    print("Reels: 5")
    print("Educational visuals: 5")

    if audio_file is not None:
        print(
            f"Reel audio: {audio_file}"
        )
    else:
        print(
            "Reel audio: NOT CONFIGURED"
        )

    print("==========================================")

    # ------------------------------------------------
    # STAGE 1
    # ------------------------------------------------

    if generated_content is None:

        print()
        print("STAGE 1: GENERATING 10 LESSONS")
        print("------------------------------------------")

        generated_content = generate_content_batches(
            daily_plan
        )

        print()
        print(
            "STAGE 1 COMPLETE: "
            "10 lessons generated."
        )

    else:

        print()
        print("STAGE 1: EXISTING CONTENT RECEIVED")
        print("------------------------------------------")
        print(
            "Skipping Gemini generation."
        )
        print(
            "Using the 10 lessons already generated "
            "by the test/workflow."
        )

    # ------------------------------------------------
    # Attach plan metadata if necessary
    # ------------------------------------------------

    if len(generated_content) != 10:
        raise RuntimeError(
            "Content stage did not provide exactly 10 lessons."
        )

    metadata_complete = all(
        "slot" in item
        and "lesson_number" in item
        and "content_type" in item
        for item in generated_content
    )

    if not metadata_complete:
        generated_content = attach_plan_metadata(
            generated_content,
            daily_plan,
        )

    # ------------------------------------------------
    # STAGE 2 + 3
    # ------------------------------------------------

    generated_posts = generate_media_from_content(
        generated_content=generated_content,
        output_directory=output_directory,
        audio_file=audio_file,
    )

    return generated_posts


def save_daily_package(
    generated_posts: List[Dict[str, Any]],
    output_file: Path = Path(
        "daily_generated_content.json"
    ),
) -> Path:

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

    audio_reels = [
        item
        for item in reels
        if item.get("reel_audio_file")
    ]

    payload = {
        "total_posts": len(
            generated_posts
        ),
        "reels": len(reels),
        "educational_visuals": len(
            visuals
        ),
        "audio_reels": len(
            audio_reels
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
        f"Daily package saved to: {output_file}"
    )

    return Path(
        output_file
    )


def summarize_daily_content(
    generated_posts: List[Dict[str, Any]],
) -> Dict[str, int]:

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
        if (
            item.get("reel_enabled")
            and item.get("reel_file")
            and Path(
                item["reel_file"]
            ).exists()
        )
    ]

    audio_reels = [
        item
        for item in generated_posts
        if (
            item.get("reel_enabled")
            and item.get("reel_audio_file")
        )
    ]

    return {
        "total_posts": len(
            generated_posts
        ),
        "reels": len(reels),
        "educational_visuals": len(visuals),
        "successful_images": len(
            successful_images
        ),
        "successful_reels": len(
            successful_reels
        ),
        "audio_reels": len(
            audio_reels
        ),
    }


if __name__ == "__main__":

    print(
        "Orom Plan1 daily content engine loaded."
    )

    print()
    print("Architecture:")
    print("10 planned posts")
    print("-> 5 Gemini content batches")
    print("-> 10 lessons")
    print("-> 10 images")
    print("-> 5 Reels + 5 educational visuals")
    print("-> optional local Reel audio")

    print()
    print(
        "Media generation can also consume "
        "already-generated lessons without "
        "calling Gemini again."
    )
