import json
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# OROM PLAN1 - 10-POST DAILY CONTENT PLANNER
# ============================================================

CONTENT_HISTORY_FILE = Path("content_history.json")


# ============================================================
# EDUCATIONAL CONTENT STRUCTURE
# ============================================================

DAILY_CONTENT_STRUCTURE = [
    {
        "slot": 1,
        "content_type": "reel",
        "role": "problem_and_cause",
        "lesson_type": "problem_and_cause",
    },
    {
        "slot": 2,
        "content_type": "educational_visual",
        "role": "how_it_works",
        "lesson_type": "how_it_works",
    },
    {
        "slot": 3,
        "content_type": "reel",
        "role": "common_mistake",
        "lesson_type": "common_mistake",
    },
    {
        "slot": 4,
        "content_type": "educational_visual",
        "role": "professional_tip",
        "lesson_type": "professional_tip",
    },
    {
        "slot": 5,
        "content_type": "reel",
        "role": "troubleshooting",
        "lesson_type": "troubleshooting",
    },
    {
        "slot": 6,
        "content_type": "educational_visual",
        "role": "maintenance",
        "lesson_type": "maintenance",
    },
    {
        "slot": 7,
        "content_type": "reel",
        "role": "installation_principle",
        "lesson_type": "installation_principle",
    },
    {
        "slot": 8,
        "content_type": "educational_visual",
        "role": "material_knowledge",
        "lesson_type": "material_knowledge",
    },
    {
        "slot": 9,
        "content_type": "reel",
        "role": "myth_vs_fact",
        "lesson_type": "myth_vs_fact",
    },
    {
        "slot": 10,
        "content_type": "educational_visual",
        "role": "professional_knowledge",
        "lesson_type": "professional_tip",
    },
]


# ============================================================
# KNOWLEDGE PATHS
# ============================================================

KNOWLEDGE_PATHS = [
    {
        "name": "Drainage Fundamentals",
        "topics": [
            "drainage systems",
            "sink drainage",
            "waste pipes",
            "drain traps",
            "drain ventilation",
            "pipe slope and drainage",
            "common plumbing mistakes",
        ],
    },
    {
        "name": "Water Supply Fundamentals",
        "topics": [
            "water supply systems",
            "cold water plumbing",
            "hot water plumbing",
            "pipe sizing and flow",
            "pipe fittings and connections",
            "leak detection and repair",
        ],
    },
    {
        "name": "Bathroom Plumbing",
        "topics": [
            "WC discharge systems",
            "bathroom plumbing",
            "showers and mixers",
            "drain traps",
            "drain ventilation",
            "water supply systems",
        ],
    },
    {
        "name": "PPR Installation",
        "topics": [
            "PPR pipe installation",
            "pipe fittings and connections",
            "hot water plumbing",
            "cold water plumbing",
            "professional installation practices",
            "plumbing tools and materials",
        ],
    },
    {
        "name": "Soakaway and Wastewater",
        "topics": [
            "soakaway systems",
            "drainage systems",
            "WC discharge systems",
            "waste pipes",
            "drain ventilation",
            "pipe slope and drainage",
        ],
    },
    {
        "name": "Professional Plumbing",
        "topics": [
            "professional installation practices",
            "building plumbing design",
            "plumbing troubleshooting",
            "plumbing safety",
            "plumbing tools and materials",
            "common plumbing mistakes",
        ],
    },
]


# ============================================================
# HISTORY HELPERS
# ============================================================

def load_history(
    history_file: Path = CONTENT_HISTORY_FILE,
) -> List[Dict[str, Any]]:
    """
    Safely load content history.

    The function accepts both:
    - the newer list-based history format
    - older dictionary-based history formats
    """

    if not history_file.exists():
        return []

    try:
        with history_file.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        history = data.get("history")

        if isinstance(history, list):
            return history

        # Preserve older formats without crashing the planner.
        return [data]

    return []


def get_recent_topics(
    history: List[Dict[str, Any]],
    limit: int = 30,
) -> List[str]:
    """
    Extract recent topics/knowledge areas from history.
    """

    recent = []

    for item in reversed(history):
        if not isinstance(item, dict):
            continue

        topic = (
            item.get("knowledge_area")
            or item.get("topic")
            or item.get("idea")
        )

        if topic:
            recent.append(str(topic))

        if len(recent) >= limit:
            break

    return recent


def get_recent_titles(
    history: List[Dict[str, Any]],
    limit: int = 30,
) -> List[str]:
    """
    Extract recent titles to help avoid repetitive lessons.
    """

    titles = []

    for item in reversed(history):
        if not isinstance(item, dict):
            continue

        title = item.get("title")

        if title:
            titles.append(str(title))

        if len(titles) >= limit:
            break

    return titles


# ============================================================
# TOPIC SELECTION
# ============================================================

def choose_topic(
    knowledge_areas: List[str],
    recent_topics: List[str],
    preferred_topic: Optional[str] = None,
) -> str:
    """
    Select a topic while avoiding recent repetition.

    A preferred topic is used when supplied, provided it is valid.
    """

    if preferred_topic:
        if preferred_topic in knowledge_areas:
            return preferred_topic

    recent_lower = {
        topic.strip().lower()
        for topic in recent_topics
        if topic
    }

    for topic in knowledge_areas:
        if topic.strip().lower() not in recent_lower:
            return topic

    # If every topic was recently used, restart the cycle rather than
    # stopping the content engine.
    return knowledge_areas[0]


# ============================================================
# KNOWLEDGE PATH SELECTION
# ============================================================

def choose_knowledge_path(
    day_number: int = 1,
) -> Dict[str, Any]:
    """
    Rotate through educational knowledge paths.

    The same path can return again later, creating a learning loop.
    """

    if not KNOWLEDGE_PATHS:
        raise RuntimeError("No knowledge paths configured.")

    index = (max(day_number, 1) - 1) % len(KNOWLEDGE_PATHS)

    return KNOWLEDGE_PATHS[index]


# ============================================================
# DAILY PLAN CREATION
# ============================================================

def create_daily_plan(
    day_number: int = 1,
    history_file: Path = CONTENT_HISTORY_FILE,
) -> List[Dict[str, Any]]:
    """
    Create the complete 10-post educational plan for one day.

    The planner itself does NOT call Gemini, Cloudflare or Instagram.
    It only decides what should be generated.
    """

    history = load_history(history_file)

    recent_topics = get_recent_topics(history)
    recent_titles = get_recent_titles(history)

    knowledge_path = choose_knowledge_path(day_number)

    available_topics = knowledge_path["topics"]

    plan = []

    used_today = set()

    for structure in DAILY_CONTENT_STRUCTURE:

        topic = choose_topic(
            knowledge_areas=available_topics,
            recent_topics=recent_topics + list(used_today),
        )

        used_today.add(topic)

        item = {
            "slot": structure["slot"],
            "content_type": structure["content_type"],
            "role": structure["role"],
            "lesson_type": structure["lesson_type"],
            "knowledge_path": knowledge_path["name"],
            "knowledge_area": topic,
            "lesson_number": (
                ((day_number - 1) * 10)
                + structure["slot"]
            ),
            "previous_lesson": (
                recent_titles[0]
                if recent_titles
                else ""
            ),
        }

        plan.append(item)

    return plan


# ============================================================
# PLAN VALIDATION
# ============================================================

def validate_daily_plan(
    plan: List[Dict[str, Any]],
) -> bool:
    """
    Validate the 10-post structure before any API is used.
    """

    if not isinstance(plan, list):
        return False

    if len(plan) != 10:
        return False

    slots = [item.get("slot") for item in plan]

    if slots != list(range(1, 11)):
        return False

    reels = [
        item
        for item in plan
        if item.get("content_type") == "reel"
    ]

    visuals = [
        item
        for item in plan
        if item.get("content_type") == "educational_visual"
    ]

    if len(reels) != 5:
        return False

    if len(visuals) != 5:
        return False

    required_fields = [
        "slot",
        "content_type",
        "role",
        "lesson_type",
        "knowledge_path",
        "knowledge_area",
        "lesson_number",
    ]

    for item in plan:
        if not isinstance(item, dict):
            return False

        for field in required_fields:
            if field not in item:
                return False

            if item[field] is None:
                return False

    return True


# ============================================================
# HUMAN-READABLE PLAN SUMMARY
# ============================================================

def print_daily_plan(
    plan: List[Dict[str, Any]],
) -> None:
    """
    Print a clean summary useful for GitHub Actions logs.
    """

    print()
    print("=" * 60)
    print("OROM PLAN1 - DAILY 10-POST EDUCATION PLAN")
    print("=" * 60)

    for item in plan:
        content_type = item["content_type"]

        if content_type == "reel":
            icon = "🎬"
        else:
            icon = "🖼️"

        print(
            f'{icon} Slot {item["slot"]}: '
            f'{content_type} | '
            f'{item["knowledge_area"]} | '
            f'{item["lesson_type"]}'
        )

    print("=" * 60)
    print(
        f"Total posts: {len(plan)} | "
        f"Reels: {sum(i['content_type'] == 'reel' for i in plan)} | "
        f"Visuals: {sum(i['content_type'] == 'educational_visual' for i in plan)}"
    )
    print("=" * 60)
    print()


# ============================================================
# SIMPLE COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":
    plan = create_daily_plan(day_number=1)

    print_daily_plan(plan)

    if not validate_daily_plan(plan):
        raise SystemExit(
            "❌ Daily plan validation failed."
        )

    print("✅ Daily plan validation passed.")
