import os
import json
from google import genai


# ============================================================
# CONTENT GENERATOR
# OROM PLAN1
# GEMINI 3.6 FLASH
#
# VERSION:
# Technical Image Accuracy Upgrade
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
- visual-scene designer

Create ONE original Instagram post for a professional
residential plumbing account.

The content must be technically responsible, visually
realistic, useful to homeowners, and suitable for a
professional plumbing brand.

============================================================
TOPIC
============================================================

{topic}

============================================================
IMPORTANT PRINCIPLE
============================================================

The IMAGE must visually communicate the ACTUAL plumbing
subject or procedure.

Do NOT create a generic image that is merely related to
plumbing.

Before writing the image prompt, mentally determine:

1. What exact plumbing problem, component, system or
   procedure is being discussed?

2. What would a professional plumber actually need to see
   to understand that subject?

3. Which plumbing component should be visible?

4. If a procedure is being discussed, what is the correct
   physical procedure?

5. What environment would realistically contain the
   plumbing equipment?

The image prompt must then describe THAT exact scene.

============================================================
TECHNICAL ACCURACY IS MORE IMPORTANT THAN DECORATION
============================================================

The image must represent physically possible plumbing.

Use:

- realistic pipe sizes
- realistic pipe positions
- realistic fittings
- realistic valves
- realistic joints
- realistic connections
- realistic plumbing components
- realistic water behavior
- realistic equipment
- realistic installation methods

Never invent impossible plumbing arrangements merely to make
the image look interesting.

Do not connect unrelated pipes together.

Do not place fittings where they would not realistically be
installed.

Do not create floating pipes.

Do not create impossible pipe bends.

Do not create duplicated plumbing components.

Do not merge several plumbing components into one object.

Do not create equipment with physically impossible shapes.

============================================================
PROCEDURE ACCURACY
============================================================

If the topic describes a plumbing TEST, REPAIR,
INSTALLATION, INSPECTION, MAINTENANCE or DIAGNOSTIC
procedure, the image must show the procedure correctly.

The photograph should show what a professional plumber or
homeowner would actually do.

Do not merely show an object associated with the procedure.

For example:

A topic about testing a toilet for a silent leak should NOT
show dye being poured directly into the toilet bowl.

Instead, show the correct procedure:

- toilet cistern/tank visible
- cistern/tank lid removed when appropriate
- water inside the tank
- a small amount of suitable dye/food colouring being added
  to the tank water
- toilet bowl remaining clear initially
- realistic toilet components
- realistic residential bathroom

The image should communicate the actual diagnostic method.

============================================================
TOPIC-SPECIFIC VISUAL RULES
============================================================

Use the following rules whenever they apply.

------------------------------------------------------------
TOILET TOPICS
------------------------------------------------------------

For toilet-related topics, identify the actual component
involved.

Possible components include:

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

Do not randomly show the toilet bowl when the topic is
actually about the cistern or internal mechanism.

If the topic concerns a toilet leak, visually identify where
the leak would actually occur.

If the topic concerns a dye test, show dye being placed in
the cistern/tank rather than directly into the bowl.

------------------------------------------------------------
WATER PUMP TOPICS
------------------------------------------------------------

For water-pump topics, show a realistic residential pump
installation.

When appropriate, include:

- actual water pump
- inlet pipe
- outlet pipe
- isolation valves
- unions or fittings
- pressure-related components
- realistic pipe connections
- realistic surrounding environment

Do not show a random industrial pump if the topic concerns
ordinary residential water supply.

If the topic concerns pump cycling, show a believable pump
installation that could actually experience the described
problem.

------------------------------------------------------------
LEAK TOPICS
------------------------------------------------------------

For leak topics, clearly show:

- the actual leaking component
- the approximate leak location
- visible water where appropriate
- realistic surrounding plumbing

Do not show a random puddle with no identifiable source.

------------------------------------------------------------
DRAINAGE TOPICS
------------------------------------------------------------

For drainage topics, show the actual drainage system or
problem.

Depending on the topic, this may include:

- waste pipe
- drain pipe
- floor drain
- inspection chamber
- drain fitting
- blockage
- standing water
- drainage connection
- appropriate underground or exposed drainage pipe

The scene must make the drainage problem understandable.

------------------------------------------------------------
PPR PIPE TOPICS
------------------------------------------------------------

For PPR installation topics, show realistic PPR pipes and
fittings.

Possible components include:

- PPR straight pipe
- elbow
- tee
- socket
- reducer
- valve
- correctly fused joint

Connections must look physically possible.

Do not create impossible fitting combinations.

------------------------------------------------------------
PVC / SOIL / WASTE PIPE TOPICS
------------------------------------------------------------

Show realistic pipe diameters and fittings.

Use appropriate:

- elbows
- tees
- reducers
- sockets
- traps
- connectors
- inspection fittings

The pipe arrangement should look like something that could
actually be installed in a building.

------------------------------------------------------------
WATER TANK TOPICS
------------------------------------------------------------

For water-tank topics, show realistic:

- overhead water tank
- inlet pipe
- outlet pipe
- float valve
- overflow pipe
- isolation valve
- supporting structure

Do not create impossible pipe connections around the tank.

------------------------------------------------------------
VALVE TOPICS
------------------------------------------------------------

If the topic concerns a valve, make the valve clearly visible.

The image should show:

- correct valve type when identifiable
- realistic pipe connections
- realistic handle or actuator
- believable installation position

Do not hide the main component.

------------------------------------------------------------
PIPE REPAIR TOPICS
------------------------------------------------------------

If a plumber is repairing a pipe:

- show the actual damaged section
- show the plumber working on that section
- show realistic tools when useful
- show realistic hands
- show believable pipe positioning

Do not show a plumber posing beside an unrelated pipe.

============================================================
PEOPLE
============================================================

Only include a plumber/person when the person helps explain
the topic.

If a plumber appears:

- realistic human proportions
- realistic hands
- realistic fingers
- realistic work clothing
- realistic protective equipment where appropriate
- natural working position
- actually performing the relevant task

Do not make the plumber unnecessarily pose toward the camera.

Avoid hands completely when they are not needed.

This is especially important for technical equipment images.

============================================================
PHOTOGRAPHIC REALISM
============================================================

The final image must look like a real professional photograph.

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

The image must NOT look like:

- cartoon
- illustration
- digital painting
- CGI
- 3D render
- game graphics
- advertisement artwork
- plastic-looking equipment
- fantasy plumbing

============================================================
CAMERA
============================================================

Describe an appropriate professional camera perspective.

Use:

- realistic focal length
- natural perspective
- realistic depth of field
- sharp focus on the important plumbing component
- natural background blur where appropriate
- professional interior or natural lighting

Do not use extreme cinematic effects that make the plumbing
difficult to understand.

The plumbing subject is more important than dramatic style.

============================================================
VERTICAL INSTAGRAM COMPOSITION
============================================================

The final image will be used as a vertical 9:16 Instagram
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
- keep important plumbing details visible
- make the scene understandable on a smartphone

============================================================
NO TEXT OR BRANDING
============================================================

The image must contain:

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

Do not place written instructions inside the image.

============================================================
IMAGE PROMPT STRUCTURE
============================================================

The image_prompt must describe the scene in a way that an
image-generation model can understand.

It should clearly include:

1. Exact plumbing subject.
2. Correct plumbing component.
3. Correct physical action, if applicable.
4. Correct environment.
5. Realistic materials.
6. Realistic plumbing arrangement.
7. Professional photography.
8. Vertical composition.
9. Important visual details.
10. Restrictions against impossible geometry.

Do not write a vague image prompt such as:

"A plumber working on plumbing."

Instead write a specific scene that visually demonstrates
the topic.

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
FINAL OUTPUT
============================================================

Return ONLY valid JSON.

The JSON must contain exactly these fields:

title
description
image_prompt
hashtags

The hashtags field must be an array of strings.

Each hashtag must begin with #.

Do not include markdown.

Do not include explanations outside the JSON.
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

                    "hashtags": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }

                },

                "required": [
                    "title",
                    "description",
                    "image_prompt",
                    "hashtags"
                ]
            }
        }
    )

    # ========================================================
    # PARSE GEMINI RESPONSE
    # ========================================================

    try:

        data = json.loads(
            interaction.output_text
        )

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "Gemini returned invalid JSON."
        ) from error

    # ========================================================
    # CHECK REQUIRED FIELDS
    # ========================================================

    required_fields = [
        "title",
        "description",
        "image_prompt",
        "hashtags"
    ]

    for field in required_fields:

        if field not in data:

            raise RuntimeError(
                f"Gemini response is missing: {field}"
            )

    # ========================================================
    # CLEAN HASHTAGS
    # ========================================================

    hashtags = []

    for hashtag in data["hashtags"]:

        if not isinstance(
            hashtag,
            str
        ):
            continue

        hashtag = hashtag.strip()

        if not hashtag:
            continue

        if not hashtag.startswith("#"):

            hashtag = "#" + hashtag

        hashtags.append(
            hashtag
        )

    # Remove duplicate hashtags while preserving order.

    hashtags = list(
        dict.fromkeys(
            hashtags
        )
    )

    # ========================================================
    # RETURN CONTENT
    # ========================================================

    return {

        "topic": topic,

        "title":
            data["title"].strip(),

        "description":
            data["description"].strip(),

        "image_prompt":
            data["image_prompt"].strip(),

        "hashtags":
            hashtags
    }


# ============================================================
# CONTENT QUALITY CHECK
# ============================================================

def check_content(
    content
):

    title = content[
        "title"
    ]

    description = content[
        "description"
    ]

    image_prompt = content[
        "image_prompt"
    ]

    hashtags = content[
        "hashtags"
    ]

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    if len(title) < 10:

        return False

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    if len(description) < 50:

        return False

    # --------------------------------------------------------
    # IMAGE PROMPT
    # --------------------------------------------------------

    if len(image_prompt) < 30:

        return False

    # --------------------------------------------------------
    # HASHTAGS
    # --------------------------------------------------------

    if not isinstance(
        hashtags,
        list
    ):

        return False

    if len(hashtags) < 3:

        return False

    # --------------------------------------------------------
    # ALL CHECKS PASSED
    # --------------------------------------------------------

    return True
