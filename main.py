import random
import json
from pathlib import Path

ideas = [
    "Professional Plumbing Tip",
    "Water-Saving Tip",
    "Bathroom Maintenance Tip",
    "Kitchen Plumbing Tip",
    "Drainage Maintenance Tip"
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

print("🤖 Daily AI Instagram Bot")
print("Today's content idea:")
print(today_idea)
print("Saved to history.")
