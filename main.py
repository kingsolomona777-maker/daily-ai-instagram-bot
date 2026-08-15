import random
import json
from pathlib import Path
from content_generator import create_content

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

history_file = Path("content_history.json")

# Load previous history
if history_file.exists():
    with open(history_file, "r") as file:
        history = json.load(file)
else:
    history = []

# Find ideas that have not been used
unused_ideas = [idea for idea in ideas if idea not in history]

# If all ideas have been used, start a new cycle
if not unused_ideas:
    history = []
    unused_ideas = ideas

# Choose today's idea
today_idea = random.choice(unused_ideas)

# Remember today's idea
history.append(today_idea)

with open(history_file, "w") as file:
    json.dump(history, file, indent=2)

content = create_content(today_idea)

print("🤖 Daily AI Instagram Bot")
print("Today's content idea:")
print(today_idea)
print()
print("Title:")
print(content["title"])
print()
print("Description:")
print(content["description"])
print()
print("Saved to history.")
