import os
import json
from google import genai


# ============================================================
# CONTENT GENERATOR
# OROM PLAN1
# GEMINI 3.6 FLASH
#
# VERSION:
# Educational Visual Content Upgrade
#
# PURPOSE:
# Gemini creates:
# 1. Professional Instagram content
# 2. Technically accurate image scene
# 3. Exact teaching text for later Python overlay
#
# IMPORTANT:
# FLUX should generate the clean photograph.
# Python will later place exact text onto the image.
# ============================================================


def create_content(topic):

    # --------------------------------------------------------
    # GET GEMINI API KEY
    # --------------------------------------------------------

    api_key = os.environ.get(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is not available."
        )

    # --------------------------------------------------------
    # CREATE GEMINI CLIENT
    # --------------------------------------------------------

    client = genai.Client(
        api_key=api_key
    )

    # ========================================================
    # MAIN PROMPT
    # ========================================================

    prompt = f"""
You are an expert:

- residential plumber
- plumbing engineer
- plumbing educator
- technical writer
- professional photographer
- Instagram content strategist
- visual teaching designer
- homeowner education specialist

Create ONE original Instagram post for a professional
residential plumbing account.

The content must be:

- technically responsible
- visually realistic
- educational
- easy for ordinary homeowners to understand
- useful
- attention-grabbing without deception
- suitable for a professional Nigerian plumbing brand

============================================================
TOPIC
============================================================

{topic}

============================================================
CORE VISUAL TEACHING PRINCIPLE
============================================================

People often notice what is visible inside the image before
they read the caption.

Therefore, the post must communicate an important part of
the lesson visually.

The final design will eventually use:

HOOK
+
REALISTIC PLUMBING SCENE
+
SHORT EXPLANATION
+
OPTIONAL VISUAL CALLOUT
+
TAKEAWAY

The image itself should make a person curious enough to stop
and understand the lesson.

However:

DO NOT use fake danger.

DO NOT exaggerate a normal plumbing issue into an emergency.

DO NOT invent statistics.

DO NOT claim that something will definitely cause damage when
that is not technically established.

Use genuine plumbing education to create curiosity.

============================================================
IMPORTANT CONTENT SEPARATION
============================================================

There are TWO separate outputs:

A. IMAGE SCENE

This describes what the image-generation model should
photograph.

B. ON-IMAGE TEXT

This is the exact educational wording that Python will later
place on top of the generated photograph.

DO NOT ask the image-generation model to create text.

The image_prompt must contain NO written text.

The on-image text must contain the exact words that should
eventually appear on the finished Instagram image.

============================================================
IMAGE STORY
============================================================

Before creating the image prompt, determine:

1. What is the real plumbing subject?

2. What problem, component, mistake, test, repair,
   installation, or maintenance lesson is involved?

3. What would a professional plumber actually see?

4. What visual detail would immediately help a homeowner
   understand the lesson?

5. What should the viewer notice first?

6. What should the viewer understand after looking at the
   image?

The photograph must visually support the teaching message.

============================================================
TECHNICAL ACCURACY
============================================================

The plumbing shown must be physically possible.

Use:

- realistic pipe sizes
- realistic pipe positions
- realistic fittings
- realistic valves
- realistic joints
- realistic connections
- realistic plumbing components
- realistic water behaviour
- realistic equipment
- realistic installation methods

Never invent impossible plumbing arrangements simply to make
the image interesting.

Do not connect unrelated pipes together.

Do not place fittings where they would not realistically be
installed.

Do not create floating pipes.

Do not create impossible pipe bends.

Do not create duplicated plumbing components.

Do not merge several plumbing components into one object.

Do not create impossible equipment shapes.

============================================================
PROCEDURE ACCURACY
============================================================

If the topic describes:

- testing
- repair
- installation
- inspection
- maintenance
- diagnosis
- troubleshooting

the image must show the actual procedure correctly.

Do not merely show an object associated with the procedure.

Show what a professional plumber or homeowner would actually
do.

------------------------------------------------------------
TOILET DYE TEST EXAMPLE
------------------------------------------------------------

If the topic concerns testing a toilet for a silent leak:

CORRECT:

- toilet cistern/tank visible
- cistern/tank lid removed when appropriate
- water inside the tank
- small amount of suitable dye or food colouring being added
  to the tank water
- toilet bowl initially clear
- realistic toilet components
- realistic residential bathroom

INCORRECT:

- pouring dye directly into the toilet bowl
- random blue water in the bowl
- impossible toilet mechanisms
- duplicated toilet parts

============================================================
TOPIC-SPECIFIC VISUAL RULES
============================================================

------------------------------------------------------------
TOILET TOPICS
------------------------------------------------------------

Identify the actual component involved.

Possible components:

- toilet cistern/tank
- flush valve
- fill valve
- flapper
- flush button
- flush handle
- overflow tube
- supply connection
- toilet bowl
- trap
- waste connection

Do not randomly show the toilet bowl when the topic is about
the cistern or internal mechanism.

------------------------------------------------------------
WATER PUMP TOPICS
------------------------------------------------------------

Show a realistic residential pump installation.

When appropriate include:

- actual water pump
- inlet pipe
- outlet pipe
- isolation valves
- unions or fittings
- pressure-related components
- realistic pipe connections
- realistic surrounding environment

Do not show a random industrial pump when discussing normal
home water supply.

------------------------------------------------------------
LEAK TOPICS
------------------------------------------------------------

Show:

- actual leaking component
- approximate leak location
- visible water where appropriate
- realistic surrounding plumbing

Do not show a random puddle with no identifiable source.

------------------------------------------------------------
DRAINAGE TOPICS
------------------------------------------------------------

Show the actual drainage problem.

Possible elements:

- waste pipe
- drain pipe
- floor drain
- inspection chamber
- drain fitting
- blockage
- standing water
- drainage connection
- underground or exposed drainage pipe

------------------------------------------------------------
PPR TOPICS
------------------------------------------------------------

Show realistic:

- PPR pipe
- elbow
- tee
- socket
- reducer
- valve
- correctly fused joint

Connections must look physically possible.

------------------------------------------------------------
PVC / SOIL / WASTE TOPICS
------------------------------------------------------------

Use realistic:

- pipe diameters
- elbows
- tees
- reducers
- sockets
- traps
- connectors
- inspection fittings

------------------------------------------------------------
WATER TANK TOPICS
------------------------------------------------------------

Show realistic:

- overhead tank
- inlet pipe
- outlet pipe
- float valve
- overflow pipe
- isolation valve
- support structure

------------------------------------------------------------
VALVE TOPICS
------------------------------------------------------------

Make the actual valve clearly visible.

Show:

- correct valve type when identifiable
- realistic pipe connections
- realistic handle or actuator
- believable installation position

------------------------------------------------------------
PIPE REPAIR TOPICS
------------------------------------------------------------

If a plumber is repairing a pipe:

- show actual damaged section
- show plumber working on that section
- show realistic tools when useful
- show realistic hands
- show believable pipe positioning

Do not show a plumber posing beside unrelated plumbing.

============================================================
PEOPLE
============================================================

Only include a plumber/person when useful.

If a person appears:

- realistic human proportions
- realistic hands
- realistic fingers
- realistic work clothing
- realistic protective equipment where appropriate
- natural working position
- actually performing the relevant task

Avoid unnecessary hands when they do not help explain the
subject.

============================================================
PHOTOGRAPHIC REALISM
============================================================

The final image must look like a genuine professional
photograph.

Use:

- photorealistic appearance
- professional commercial photography
- realistic materials
- realistic textures
- natural lighting
- realistic shadows
- realistic reflections
- realistic water
- realistic metal
- realistic plastic
- realistic ceramic
- realistic concrete
- realistic skin
- realistic clothing

Do NOT create:

- cartoon
- illustration
- digital painting
- CGI
- 3D render
- game graphics
- fantasy plumbing
- plastic-looking equipment

============================================================
CAMERA
============================================================

Use an appropriate professional camera perspective.

Use:

- realistic focal length
- natural perspective
- realistic depth of field
- sharp focus on important plumbing component
- natural background blur when appropriate
- professional interior or natural lighting

The plumbing lesson is more important than dramatic
cinematic effects.

============================================================
VERTICAL INSTAGRAM COMPOSITION
============================================================

The photograph will be used as a vertical 9:16 Instagram
image.

Design the scene specifically for vertical composition.

Requirements:

- main subject clearly visible
- main subject reasonably large
- important component near the central composition
- avoid extreme edges
- avoid awkward cropping
- avoid excessive empty space
- maintain natural perspective
- important plumbing details remain visible
- scene understandable on a smartphone
- leave reasonable clean visual space where text can later be
  overlaid

IMPORTANT:

Do not place important plumbing components behind the future
text area.

============================================================
NO TEXT IN THE GENERATED IMAGE
============================================================

The image_prompt must explicitly require:

NO text
NO words
NO letters
NO numbers
NO labels
NO logos
NO watermarks
NO signs
NO advertisements
NO social-media graphics
NO UI elements

The image-generation model must create a clean photograph.

Python will add the educational text later.

============================================================
ON-IMAGE TEACHING STRATEGY
============================================================

Create short educational text for the finished image.

The text should follow this structure:

HOOK:
A short statement that immediately creates curiosity.

EXPLANATION:
A short sentence explaining the important visual lesson.

CALLOUT:
An optional short label pointing attention toward the
important plumbing component.

TAKEAWAY:
A short practical lesson the viewer can remember.

============================================================
HOOK RULES
============================================================

The hook should normally be:

3-8 words.

Examples of the style:

"That small leak matters."

"Your pump may not be the problem."

"This is where the blockage starts."

"Don't ignore this pipe joint."

"Your toilet can leak silently."

Do NOT copy these examples automatically.

Create wording specifically for the topic.

Avoid:

- fake emergencies
- fearmongering
- impossible claims
- exaggerated promises
- misleading statements
- clickbait that contradicts the actual lesson

============================================================
EXPLANATION RULES
============================================================

The explanation should normally be:

8-15 words.

It must teach something genuinely useful.

Avoid repeating the hook.

Avoid complicated engineering language unless necessary.

============================================================
CALLOUT RULES
============================================================

The callout should normally be:

1-5 words.

It should identify an important visible component.

Examples:

"Fill valve"

"Blocked section"

"Leaking joint"

"Isolation valve"

"Overflow pipe"

Only use a callout when it adds genuine visual value.

If a callout is unnecessary, return an empty string.

============================================================
TAKEAWAY RULES
============================================================

The takeaway should normally be:

5-12 words.

It should communicate a practical lesson.

Examples of style:

"Check the valve before replacing the pump."

"Find the source before repairing the leak."

"Small blockages can reduce drainage flow."

Again, create topic-specific wording.

============================================================
TOTAL ON-IMAGE TEXT
============================================================

Keep the total amount of text visually light.

Normally:

- Hook: 3-8 words
- Explanation: 8-15 words
- Callout: 1-5 words
- Takeaway: 5-12 words

Do not turn the image into a full article.

The caption can contain the deeper explanation.

============================================================
VISUAL STORY
============================================================

Create a short description explaining:

- what the viewer sees
- what the viewer should notice first
- what plumbing detail proves the lesson
- how the photograph supports the teaching text

This is NOT the image prompt.

It is a planning description for the visual composition.

============================================================
TITLE
============================================================

Create a short, interesting title that makes a homeowner
want to read the post.

Do not simply copy the topic word-for-word.

The title should sound natural and professional.

Avoid exaggerated clickbait.

============================================================
DESCRIPTION
============================================================

Write a useful Instagram caption of approximately
80-120 words.

The caption must:

- be practical
- be technically responsible
- be accurate
- be professional but friendly
- be easy for ordinary homeowners to understand
- explain useful plumbing information
- avoid exaggerated claims
- never invent prices
- never make unsafe recommendations
- encourage professional inspection when appropriate
- sound naturally written by an experienced plumber
- avoid repetitive openings
- avoid "Did you know..."
- avoid unnecessary emojis
- add useful information beyond the image
- not simply repeat the on-image text

============================================================
HASHTAGS
============================================================

Create 5-8 relevant Instagram hashtags.

Hashtags must:

- directly relate to the topic
- be relevant to plumbing
- be useful for home-maintenance content
- use specific topic-related hashtags when appropriate
- avoid misleading claims
- avoid spammy tags
- avoid unrelated popular hashtags

Do not use emojis.

Do not use the exact same hashtag list for every topic.

============================================================
LANGUAGE STYLE
============================================================

Use clear natural English suitable for Nigerian homeowners.

Do not force Pidgin into every post.

Use Nigerian expressions only when they sound natural.

The content should still look professional.

Do not use an em dash.

Do not use an en dash.

Do not use decorative long dash punctuation.

Prefer:

- commas
- full stops
- question marks
- colons
- parentheses

============================================================
FINAL OUTPUT
============================================================

Return ONLY valid JSON.

The JSON must contain exactly these top-level fields:

title
description
image_prompt
visual_story
on_image_text
hashtags

The "on_image_text" field must be an object containing exactly:

hook
explanation
callout
takeaway

The hashtags field must be an array of strings.

Each hashtag must begin with #.

Do not include markdown.

Do not include explanations outside the JSON.

============================================================
FINAL QUALITY CHECK BEFORE ANSWERING
============================================================

Before returning the JSON, silently verify:

1. Is the plumbing technically possible?

2. Does the image actually show the topic?

3. Is the correct component visible?

4. If this is a procedure, is the procedure physically correct?

5. Does the visual story support the teaching message?

6. Is the hook interesting without being misleading?

7. Does the explanation teach something real?

8. Is the callout actually visible in the scene?

9. Is the takeaway practical?

10. Is the total image text short enough for a smartphone?

11. Does the caption add useful information?

12. Are the hashtags topic-specific?

13. Is there no em dash?

14. Is there no unnecessary decorative punctuation?

15. Does the image_prompt contain no text instructions that
would cause the image model to generate words?

Only return the final JSON.
"""

    # ========================================================
    # GEMINI REQUEST
    # ========================================================

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": {
                "type": "object",
                "properties": {

                    "title": {
                        "type": "string"
                    },

                    "description": {
                        "type": "string"
                    },

                    "image_prompt": {
                        "type": "string"
                    },

                    "visual_story": {
                        "type": "string"
                    },

                    "on_image_text": {
                        "type": "object",
                        "properties": {

                            "hook": {
                                "type": "string"
                            },

                            "explanation": {
                                "type": "string"
                            },

