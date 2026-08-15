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
