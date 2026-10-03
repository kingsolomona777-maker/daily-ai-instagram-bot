import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# OROM PLAN1
# DAILY PACKAGE MANAGER
#
# PURPOSE:
#
# Take the 10 already-generated posts from
# daily_content_engine.py and organize them into
# a permanent daily package.
#
# IMPORTANT:
#
# This file DOES NOT:
#
# - call Gemini
# - call Cloudflare
# - generate images
# - generate Reels
# - publish to Instagram
#
# It only packages already-generated media.
#
# Architecture:
#
# daily_content_engine.py
#          ↓
#     10 finished posts
#          ↓
# daily_package_manager.py
#          ↓
# daily_packages/YYYY-MM-DD/
#          ↓
# individual post folders
#          ↓
# schedule.json
#
# Instagram publishing will be handled later.
# ============================================================


PACKAGE_ROOT = Path(
    "daily_packages"
)


# ============================================================
# PROVISIONAL DAILY SCHEDULE
#
# These times are configuration only.
#
# They do NOT publish anything by themselves.
#
# All times are Nigeria time (Africa/Lagos).
#
# We can change these later without changing the
# package architecture.
# ============================================================

DEFAULT_SCHEDULE = [
    "07:00",
    "09:00",
    "11:00",
    "13:00",
    "15:00",
    "17:00",
    "19:00",
    "21:00",
    "22:00",
    "23:30",
]


# ============================================================
# BASIC HELPERS
# ============================================================


def is_reel(post: Dict[str, Any]) -> bool:
    return post.get("content_type") == "reel"


def is_visual(post: Dict[str, Any]) -> bool:
    return (
        post.get("content_type")
        == "educational_visual"
    )


def validate_schedule(
    schedule: List[str],
) -> None:
    """
    Validate that exactly 10 publishing times
    have been supplied.

    Times must use HH:MM format.
    """

    if len(schedule) != 10:
        raise RuntimeError(
            "Publishing schedule must contain exactly "
            "10 time slots."
        )

    for index, value in enumerate(
        schedule,
        start=1,
    ):

        if not isinstance(value, str):
            raise RuntimeError(
                f"Schedule item {index} must be a string."
            )

        parts = value.split(":")

        if len(parts) != 2:
            raise RuntimeError(
                f"Invalid schedule time at slot "
                f"{index}: {value}"
            )

        hour_text, minute_text = parts

        if not (
            hour_text.isdigit()
            and minute_text.isdigit()
        ):
            raise RuntimeError(
                f"Invalid schedule time at slot "
                f"{index}: {value}"
            )

        hour = int(hour_text)
        minute = int(minute_text)

        if not (
            0 <= hour <= 23
            and 0 <= minute <= 59
        ):
            raise RuntimeError(
                f"Invalid schedule time at slot "
                f"{index}: {value}"
            )


# ============================================================
# VALIDATE GENERATED POSTS
# ============================================================


def validate_generated_posts(
    generated_posts: List[Dict[str, Any]],
) -> None:
    """
    Make sure the media generation stage produced
    the complete 10-post package.

    This function does not generate anything.
    """

    if len(generated_posts) != 10:
        raise RuntimeError(
            "Daily package must contain exactly "
            "10 generated posts."
        )

    reels = [
        post
        for post in generated_posts
        if is_reel(post)
    ]

    visuals = [
        post
        for post in generated_posts
        if is_visual(post)
    ]

    if len(reels) != 5:
        raise RuntimeError(
            "Daily package must contain exactly "
            "5 Reels."
        )

    if len(visuals) != 5:
        raise RuntimeError(
            "Daily package must contain exactly "
            "5 educational visuals."
        )

    for index, post in enumerate(
        generated_posts,
        start=1,
    ):

        if not isinstance(post, dict):
            raise RuntimeError(
                f"Generated post {index} "
                "is not a valid dictionary."
            )

        required_fields = [
            "slot",
            "content_type",
            "lesson_number",
            "title",
            "description",
            "hashtags",
            "image_file",
        ]

        for field in required_fields:

            if field not in post:
                raise RuntimeError(
                    f"Post {index} is missing "
                    f"required field: {field}"
                )

        image_file = Path(
            post["image_file"]
        )

        if not image_file.exists():
            raise RuntimeError(
                f"Post {index} image does not exist: "
                f"{image_file}"
            )

        if is_reel(post):

            reel_file = post.get(
                "reel_file"
            )

            if not reel_file:
                raise RuntimeError(
                    f"Reel post {index} "
                    "does not have a Reel file."
                )

            reel_path = Path(
                reel_file
            )

            if not reel_path.exists():
                raise RuntimeError(
                    f"Reel file does not exist "
                    f"for post {index}: "
                    f"{reel_path}"
                )


# ============================================================
# BUILD CAPTION
# ============================================================


def build_caption(
    post: Dict[str, Any],
) -> str:
    """
    Build the Instagram caption from the
    already-generated content.

    No AI request is made here.
    """

    title = str(
        post.get(
            "title",
            "",
        )
    ).strip()

    description = str(
        post.get(
            "description",
            "",
        )
    ).strip()

    hashtags = post.get(
        "hashtags",
        [],
    )

    if isinstance(
        hashtags,
        list,
    ):

        hashtag_text = " ".join(
            str(tag).strip()
            for tag in hashtags
            if str(tag).strip()
        )

    else:

        hashtag_text = str(
            hashtags
        ).strip()

    parts = [
        title,
        description,
        hashtag_text,
    ]

    caption = "\n\n".join(
        part
        for part in parts
        if part
    )

    return caption[:2200]


# ============================================================
# BUILD ONE POST PACKAGE
# ============================================================


def package_one_post(
    post: Dict[str, Any],
    package_directory: Path,
    schedule_time: str,
    package_date: str,
) -> Dict[str, Any]:
    """
    Copy one finished post into its permanent
    daily package folder.
    """

    lesson_number = int(
        post["lesson_number"]
    )

    slot = int(
        post["slot"]
    )

    post_directory = (
        package_directory
        / f"post_{slot:02d}"
    )

    post_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Copy final image
    # --------------------------------------------------------

    source_image = Path(
        post["image_file"]
    )

    image_destination = (
        post_directory
        / "image.jpg"
    )

    shutil.copy2(
        source_image,
        image_destination,
    )

    # --------------------------------------------------------
    # Copy Reel if this is a Reel post
    # --------------------------------------------------------

    reel_destination: Optional[
        Path
    ] = None

    if is_reel(post):

        source_reel = Path(
            post["reel_file"]
        )

        reel_destination = (
            post_directory
            / "reel.mp4"
        )

        shutil.copy2(
            source_reel,
            reel_destination,
        )

    # --------------------------------------------------------
    # Build caption
    # --------------------------------------------------------

    caption = build_caption(
        post
    )

    # --------------------------------------------------------
    # Build post metadata
    # --------------------------------------------------------

    metadata = {
        "package_date": package_date,
        "slot": slot,
        "lesson_number": lesson_number,
        "content_type": post[
            "content_type"
        ],
        "role": post.get(
            "role",
            "",
        ),
        "lesson_type": post.get(
            "lesson_type",
            "",
        ),
        "knowledge_path": post.get(
            "knowledge_path",
            "",
        ),
        "knowledge_area": post.get(
            "knowledge_area",
            "",
        ),
        "title": post[
            "title"
        ],
        "description": post[
            "description"
        ],
        "hashtags": post[
            "hashtags"
        ],
        "caption": caption,
        "schedule_time": schedule_time,
        "timezone": "Africa/Lagos",
        "image_file": str(
            image_destination
        ),
        "reel_enabled": bool(
            post.get(
                "reel_enabled",
                False,
            )
        ),
        "reel_file": (
            str(reel_destination)
            if reel_destination
            else None
        ),
        "reel_audio_file": post.get(
            "reel_audio_file"
        ),
        "publication_status": "pending",
        "instagram_media_id": None,
        "published_at": None,
    }

    # --------------------------------------------------------
    # Save individual content.json
    # --------------------------------------------------------

    content_file = (
        post_directory
        / "content.json"
    )

    with content_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return metadata


# ============================================================
# BUILD DAILY PACKAGE
# ============================================================


def build_daily_package(
    generated_posts: List[Dict[str, Any]],
    package_date: Optional[str] = None,
    schedule: Optional[
        List[str]
    ] = None,
    package_root: Path = PACKAGE_ROOT,
) -> Path:
    """
    Convert the completed 10-post media generation
    result into a permanent daily package.

    IMPORTANT:

    This function does NOT:

    - call Gemini
    - call Cloudflare
    - generate images
    - generate Reels
    - contact Instagram

    It only packages already-generated media.
    """

    validate_generated_posts(
        generated_posts
    )

    if schedule is None:
        schedule = list(
            DEFAULT_SCHEDULE
        )

    validate_schedule(
        schedule
    )

    # --------------------------------------------------------
    # Determine package date
    # --------------------------------------------------------

    if package_date is None:

        package_date = date.today().isoformat()

    package_date = str(
        package_date
    ).strip()

    if not package_date:
        raise RuntimeError(
            "Package date cannot be empty."
        )

    # --------------------------------------------------------
    # Create package directory
    # --------------------------------------------------------

    daily_directory = (
        Path(package_root)
        / package_date
    )

    if daily_directory.exists():

        raise RuntimeError(
            "Daily package already exists: "
            f"{daily_directory}"
        )

    daily_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    # --------------------------------------------------------
    # Sort posts by slot
    # --------------------------------------------------------

    sorted_posts = sorted(
        generated_posts,
        key=lambda item: int(
            item["slot"]
        ),
    )

    # --------------------------------------------------------
    # Build individual post packages
    # --------------------------------------------------------

    packaged_posts = []

    for index, post in enumerate(
        sorted_posts
    ):

        schedule_time = schedule[
            index
        ]

        metadata = package_one_post(
            post=post,
            package_directory=daily_directory,
            schedule_time=schedule_time,
            package_date=package_date,
        )

        packaged_posts.append(
            metadata
        )

    # --------------------------------------------------------
    # Build schedule.json
    # --------------------------------------------------------

    schedule_entries = []

    for metadata in packaged_posts:

        entry = {
            "slot": metadata[
                "slot"
            ],
            "lesson_number": metadata[
                "lesson_number"
            ],
            "content_type": metadata[
                "content_type"
            ],
            "title": metadata[
                "title"
            ],
            "schedule_time": metadata[
                "schedule_time"
            ],
            "timezone": metadata[
                "timezone"
            ],
            "post_directory": (
                f"post_"
                f"{metadata['slot']:02d}"
            ),
            "publication_status": (
                metadata[
                    "publication_status"
                ]
            ),
            "instagram_media_id": None,
            "published_at": None,
        }

        schedule_entries.append(
            entry
        )

    schedule_payload = {
        "package_date": package_date,
        "timezone": "Africa/Lagos",
        "status": "ready",
        "total_posts": 10,
        "reels": 5,
        "educational_visuals": 5,
        "schedule": schedule_entries,
    }

    schedule_file = (
        daily_directory
        / "schedule.json"
    )

    with schedule_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            schedule_payload,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # --------------------------------------------------------
    # Final package validation
    # --------------------------------------------------------

    post_directories = [
        path
        for path in daily_directory.iterdir()
        if path.is_dir()
        and path.name.startswith(
            "post_"
        )
    ]

    if len(
        post_directories
    ) != 10:

        raise RuntimeError(
            "Daily package validation failed. "
            "Expected exactly 10 post directories."
        )

    if not schedule_file.exists():

        raise RuntimeError(
            "Daily package validation failed. "
            "schedule.json was not created."
        )

    print()
    print(
        "=========================================="
    )

    print(
        "OROM PLAN1 DAILY PACKAGE CREATED"
    )

    print(
        "=========================================="
    )

    print(
        f"Date: {package_date}"
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
        f"Package: {daily_directory}"
    )

    print(
        f"Schedule: {schedule_file}"
    )

    print(
        "Status: READY"
    )

    print(
        "=========================================="
    )

    return daily_directory


# ============================================================
# LOAD DAILY PACKAGE
# ============================================================


def load_daily_package(
    package_date: str,
    package_root: Path = PACKAGE_ROOT,
) -> Dict[str, Any]:
    """
    Load a previously-created daily package.

    This will be used later by the publishing workflow.
    """

    daily_directory = (
        Path(package_root)
        / package_date
    )

    schedule_file = (
        daily_directory
        / "schedule.json"
    )

    if not schedule_file.exists():

        raise FileNotFoundError(
            "Daily package schedule does not exist: "
            f"{schedule_file}"
        )

    with schedule_file.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(
            file
        )


# ============================================================
# MAIN TEST
# ============================================================


if __name__ == "__main__":

    print(
        "Orom Plan1 Daily Package Manager loaded."
    )

    print()
    print(
        "This module packages already-generated "
        "10-post media."
    )

    print()
    print(
        "It does NOT generate content."
    )

    print(
        "It does NOT generate images."
    )

    print(
        "It does NOT generate Reels."
    )

    print(
        "It does NOT publish to Instagram."
    )

    print()
    print(
        "Default publishing schedule:"
    )

    for index, time_value in enumerate(
        DEFAULT_SCHEDULE,
        start=1,
    ):

        print(
            f"Post {index:02d}: "
            f"{time_value}"
        )
