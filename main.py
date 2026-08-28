import random
import json
from pathlib import Path

from content_generator import create_content, check_content
from image_generator import generate_image, make_vertical_image


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

history_file = Path("content_history.json")
latest_content_file = Path("latest_content.json")


# ============================================================
# LOAD CONTENT HISTORY
# ============================================================

if history_file.exists():
    try:
        with open(history_file, "r", encoding="utf-8") as file:
            history = json.load(file)

        if not isinstance(history, list):
            history = []

    except (json.JSONDecodeError, OSError):
        history = []
else:
    history = []


# ============================================================
# FIND UNUSED IDEAS
# ============================================================

unused_ideas = [
    idea for idea in ideas
    if idea not in history
]


# ============================================================
# START NEW CYCLE WHEN ALL IDEAS ARE USED
# ============================================================

if not unused_ideas:
    print("All topics have been used.")
    print("Starting a new content cycle.")

    history = []
    unused_ideas = ideas


# ============================================================
# SELECT TODAY'S IDEA
# ============================================================

today_idea = random.choice(unused_ideas)

history.append(today_idea)


# ============================================================
# SAVE HISTORY
# ============================================================

with open(history_file, "w", encoding="utf-8") as file:
    json.dump(history, file, indent=2, ensure_ascii=False)


# ============================================================
# GENERATE CONTENT
# ============================================================

print()
print("==========================================")
print("OROM PLAN1 CONTENT GENERATION")
print("==========================================")
print()

print("Today's idea:")
print(today_idea)
print()

content = create_content(today_idea)


# ============================================================
# QUALITY CHECK
# ============================================================

if check_content(content):
    print("Content passed quality check.")
else:
    raise RuntimeError(
        "Generated content failed quality check."
    )


# ============================================================
# DISPLAY GENERATED CONTENT
# ============================================================

print()
print("Title:")
print(content["title"])

print()
print("Description:")
print(content["description"])

print()
print("Image prompt:")
print(content["image_prompt"])

print()
print("Hashtags:")
print(" ".join(content["hashtags"]))


# ============================================================
# SAVE LATEST CONTENT
# ============================================================

latest_content = {
    "idea": today_idea,
    "title": content["title"],
    "description": content["description"],
    "image_prompt": content["image_prompt"],
    "hashtags": content["hashtags"]
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
print("Latest content saved.")


# ============================================================
# GENERATE IMAGE
# ============================================================

print()
print("Generating image...")

image_file = generate_image(
    content["image_prompt"],
    "daily_image.png"
)

print("Image generated successfully.")
print(f"Image saved as: {image_file}")


# ============================================================
# CREATE INSTAGRAM 9:16 IMAGE
# ============================================================

vertical_image = make_vertical_image(
    image_file,
    "instagram_image.jpg"
)

print()
print("Instagram image created.")
print(f"Image saved as: {vertical_image}")


# ============================================================
# COMPLETE
# ============================================================

print()
print("==========================================")
print("OROM PLAN1 CONTENT GENERATION COMPLETE")
print("==========================================")
