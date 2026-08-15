def create_content(topic):
    content = {
        "topic": topic,
        "title": f"Plumbing Tip: {topic}",
        "description": (
            f"Learn an important plumbing lesson about {topic}. "
            "Regular maintenance can help prevent expensive problems."
        )
    }

    return content


def check_content(content):
    title = content["title"]
    description = content["description"]

    if len(title) < 10:
        return False

    if len(description) < 30:
        return False

    return True
