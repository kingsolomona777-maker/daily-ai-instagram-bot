import os
import random
import json
from pathlib import Path

from content_generator import create_content, check_content
from image_generator import generate_image, make_vertical_image
from reel_generator import generate_reel


# ============================================================
# OROM PLAN1
# MAIN CONTENT PIPELINE
#
# VERSION:
# Premium Educational Visual + Teaching Reel System
#
# PIPELINE:
#
# Topic
#   ↓
# Gemini content generation
#   ↓
# Technical content validation
#   ↓
# FLUX clean plumbing photograph
#   ↓
# Python educational text overlay
#   ↓
# 1080 x 1920 Instagram image
#   ↓
# Optional Teaching Reel
#   ↓
# latest_content.json
#
# IMPORTANT:
# Reel generation is controlled by:
#
# OROM_PLAN1_GENERATE_REEL=true
#
# The default is false so the existing production
# Instagram pipeline remains protected until Reel
# generation has been fully tested.
# ============================================================


# ============================================================
# PLUMBING CONTENT IDEAS
# ============================================================

ideas = [
    "How to prevent blocked drains",
    "Signs of a hidden water leak",
    "How to save water at home",
    "Why low water pressure happens",
    "How to maintain a water tank",
    "Common causes of leaking taps",
    "How to prevent bathroom pipe problems",
    "Why a toilet may keep running",
    "How to maintain kitchen drainage",
    "When to replace old plumbing pipes",
    "How to detect a leaking toilet",
    "Common causes of blocked sinks",
    "Why water pipes make unusual noises",
    "How to maintain a home water system",
    "Simple ways to protect plumbing during renovation",
    "Why proper pipe sizing matters",
    "Common plumbing mistakes homeowners make",
    "How to prevent bad smells from drains",
    "Why professional plumbing installation matters",
    "Basic plumbing maintenance every homeowner should know"
]


# ============================================================
# FILES
# ============================================================

history_file = Path(
    "content_history.json"
)

latest_content_file = Path(
    "latest_content.json"
)


# ============================================================
# LOAD CONTENT HISTORY
# ============================================================

if history_file.exists():

    try:

        with open(
            history_file,
            "r",
            encoding="utf-8"
        ) as file:

            history = json.load(
                file
            )

        if not isinstance(
            history,
            list
        ):

            history = []

    except (
        json.JSONDecodeError,
        OSError
    ):

        history = []

else:

    history = []


# ============================================================
# FIND UNUSED IDEAS
# ============================================================

unused_ideas = [
    idea
    for idea in ideas
    if idea not in history
]


# ============================================================
# START NEW CYCLE WHEN ALL IDEAS ARE USED
# ============================================================

if not unused_ideas:

    print(
        "All topics have been used."
    )

    print(
        "Starting a new content cycle."
    )

    history = []

    unused_ideas = ideas


# ============================================================
# SELECT TODAY'S IDEA
# ============================================================

today_idea = random.choice(
    unused_ideas
)

history.append(
    today_idea
)


# ============================================================
# SAVE HISTORY
# ============================================================

with open(
    history_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        history,
        file,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# START CONTENT GENERATION
# ============================================================

print()

print(
    "=========================================="
)

print(
    "OROM PLAN1 CONTENT GENERATION"
)

print(
    "=========================================="
)

print()

print(
    "Today's idea:"
)

print(
    today_idea
)

print()


# ============================================================
# GEMINI CONTENT GENERATION
# ============================================================

content = create_content(
    today_idea
)


# ============================================================
# QUALITY CHECK
# ============================================================

if check_content(
    content
):

    print(
        "Content passed quality check."
    )

else:

    raise RuntimeError(
        "Generated content failed quality check."
    )


# ============================================================
# DISPLAY GENERATED CONTENT
# ============================================================

print()

print(
    "Title:"
)

print(
    content["title"]
)

print()

print(
    "Description:"
)

print(
    content["description"]
)

print()

print(
    "Image prompt:"
)

print(
    content["image_prompt"]
)


# ============================================================
# DISPLAY VISUAL STORY
# ============================================================

print()

print(
    "Visual story:"
)

print(
    content["visual_story"]
)


# ============================================================
# DISPLAY ON-IMAGE TEACHING TEXT
# ============================================================

on_image_text = content[
    "on_image_text"
]


print()

print(
    "On-image teaching text:"
)

print(
    f"Hook: {on_image_text['hook']}"
)

print(
    f"Explanation: {on_image_text['explanation']}"
)

print(
    f"Callout: {on_image_text['callout']}"
)

print(
    f"Takeaway: {on_image_text['takeaway']}"
)


# ============================================================
# DISPLAY HASHTAGS
# ============================================================

print()

print(
    "Hashtags:"
)

print(
    " ".join(
        content["hashtags"]
    )
)


# ============================================================
# SAVE LATEST CONTENT
# ============================================================

latest_content = {

    "idea":
        today_idea,

    "title":
        content["title"],

    "description":
        content["description"],

    "image_prompt":
        content["image_prompt"],

    "visual_story":
        content["visual_story"],

    "on_image_text":
        content["on_image_text"],

    "hashtags":
        content["hashtags"],

    "reel_enabled":
        False,

    "reel_file":
        None
}


with open(
    latest_content_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        latest_content,
        file,
        indent=2,
        ensure_ascii=False
    )


print()

print(
    "Latest content saved."
)


# ============================================================
# GENERATE CLEAN FLUX IMAGE
# ============================================================

print()

print(
    "Generating clean plumbing photograph..."
)


image_file = generate_image(
    content["image_prompt"],
    "daily_image.png"
)


print(
    "Clean plumbing image generated successfully."
)

print(
    f"Image saved as: {image_file}"
)


# ============================================================
# CREATE INSTAGRAM 9:16 IMAGE
#
# IMPORTANT:
# The on-image teaching text is passed here.
#
# Python adds the exact words to the photograph.
# FLUX does NOT generate the words.
# ============================================================

print()

print(
    "Creating premium educational Instagram image..."
)


vertical_image = make_vertical_image(
    image_file,
    "instagram_image.jpg",
    content["on_image_text"]
)


print()

print(
    "Instagram educational image created."
)

print(
    f"Image saved as: {vertical_image}"
)


# ============================================================
# OPTIONAL TEACHING REEL
#
# The Reel uses the SAME Gemini teaching content:
#
# Hook
#   ↓
# Explanation
#   ↓
# Takeaway
#
# This means one content-generation call can eventually
# power both the educational image and the Reel.
#
# The feature is OFF by default.
# ============================================================

generate_reel_enabled = (
    os.getenv(
        "OROM_PLAN1_GENERATE_REEL",
        "false"
    ).strip().lower()
    == "true"
)


if generate_reel_enabled:

    print()

    print(
        "=========================================="
    )

    print(
        "CREATING TEACHING REEL"
    )

    print(
        "=========================================="
    )

    reel_teaching_text = {

        "hook":
            on_image_text["hook"],

        "explanation":
            on_image_text["explanation"],

        "takeaway":
            on_image_text["takeaway"]
    }


    reel_file = generate_reel(
        input_file=vertical_image,
        output_file="orom_plan1_reel.mp4",
        duration=8,
        teaching_text=reel_teaching_text
    )


    print()

    print(
        "Teaching Reel created successfully."
    )

    print(
        f"Reel saved as: {reel_file}"
    )


    # ========================================================
    # UPDATE LATEST CONTENT WITH REEL INFORMATION
    # ========================================================

    latest_content["reel_enabled"] = True

    latest_content["reel_file"] = str(
        reel_file
    )


    with open(
        latest_content_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            latest_content,
            file,
            indent=2,
            ensure_ascii=False
        )


else:

    print()

    print(
        "Teaching Reel generation is currently OFF."
    )

    print(
        "Set OROM_PLAN1_GENERATE_REEL=true to enable it."
    )


# ============================================================
# COMPLETE
# ============================================================

print()

print(
    "=========================================="
)

print(
    "OROM PLAN1 CONTENT GENERATION COMPLETE"
)

print(
    "=========================================="
)

print()

print(
    "Pipeline completed:"
)

print(
    "1. Topic selected"
)

print(
    "2. Gemini created educational content"
)

print(
    "3. Content quality checked"
)

print(
    "4. FLUX generated clean plumbing photograph"
)

print(
    "5. Python added educational text"
)

print(
    "6. Final image prepared at 1080 x 1920"
)

if generate_reel_enabled:

    print(
        "7. Teaching Reel generated from the same lesson"
    )

    print(
        "8. latest_content.json updated"
    )

else:

    print(
        "7. Teaching Reel generation remains safely disabled"
    )

    print(
        "8. latest_content.json updated"
    )

print()

print(
    "Ready for Instagram publishing."
)
