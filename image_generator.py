import os
import base64
import requests
from PIL import Image, ImageStat


# ============================================================
# CLOUDFLARE IMAGE GENERATION
# TEST 5 - FLUX.1 SCHNELL
# ============================================================

def generate_image(
    image_prompt,
    output_file="daily_image.png"
):

    account_id = os.environ.get(
        "CLOUDFLARE_ACCOUNT_ID"
    )

    api_token = os.environ.get(
        "CLOUDFLARE_API_TOKEN"
    )

    if not account_id:
        raise RuntimeError(
            "CLOUDFLARE_ACCOUNT_ID is not available."
        )

    if not api_token:
        raise RuntimeError(
            "CLOUDFLARE_API_TOKEN is not available."
        )

    # --------------------------------------------------------
    # FLUX.1 SCHNELL
    # --------------------------------------------------------

    model = (
        "@cf/black-forest-labs/"
        "flux-1-schnell"
    )

    url = (
        "https://api.cloudflare.com/client/v4/"
        f"accounts/{account_id}/ai/run/{model}"
    )

    headers = {
        "Authorization":
            f"Bearer {api_token}",

        "Content-Type":
            "application/json"
    }

    # --------------------------------------------------------
    # FLUX PROMPT
    #
    # FLUX.1 Schnell does not use the same negative_prompt
    # parameter as our previous Stable Diffusion models.
    #
    # Therefore the important physical constraints are placed
    # directly into the positive prompt.
    # --------------------------------------------------------

    flux_prompt = f"""
Create a highly realistic professional photograph for a
professional residential plumbing Instagram account.

SUBJECT:
{image_prompt}

PHYSICAL ACCURACY IS EXTREMELY IMPORTANT.

The plumbing equipment must look physically real and correctly
assembled.

Show:
- correct plumbing geometry
- realistic pipe proportions
- correctly connected fittings
- believable joints
- realistic PVC or metal materials
- realistic household construction
- physically possible plumbing arrangement
- natural perspective
- realistic shadows
- realistic reflections
- realistic textures

There must be ONE coherent plumbing system.

Do not invent additional plumbing fixtures.

Do not duplicate the main plumbing object.

Do not merge separate objects together.

Do not create impossible connections.

If pipes are shown, each pipe must have a believable beginning
and ending point.

If a P-trap is shown, it must be ONE correctly shaped continuous
P-trap with realistic connections.

If a faucet is shown, it must be ONE correctly assembled faucet.

If a toilet is shown, it must be ONE physically correct toilet
with one bowl, one seat and one lid.

Avoid people and human hands unless they are absolutely necessary
for the subject.

The image should look like a real photograph taken by a
professional photographer, not digital art, CGI or a 3D render.

Use realistic residential materials and natural lighting.

COMPOSITION:

Create a vertical-friendly composition.

Keep the main plumbing subject large, clearly visible and near
the center of the image.

Keep important plumbing components away from the extreme edges.

Do not crop the main subject.

Do not leave excessive empty space.

The image must remain clear and understandable on a smartphone.

IMAGE STYLE:

photorealistic professional plumbing photography,
realistic materials, realistic proportions, natural lighting,
natural shadows, realistic depth of field, sharp subject,
believable residential environment.

ABSOLUTELY NO:
text, words, letters, numbers, labels, logos, watermarks,
advertisements, posters, UI graphics, cartoon appearance,
anime appearance, illustration, painting, CGI appearance,
3D-render appearance, duplicated objects, impossible geometry,
floating objects, melted objects, warped plumbing,
extra plumbing fixtures.

Generate ONE coherent realistic photograph.
"""

    # --------------------------------------------------------
    # FLUX.1 SCHNELL SETTINGS
    # --------------------------------------------------------

    steps = 8

    payload = {
        "prompt": flux_prompt,
        "steps": steps
    }

    print()
    print("==========================================")
    print("CLOUDFLARE IMAGE GENERATION - TEST 5")
    print("==========================================")
    print(f"Model: {model}")
    print("Generation model: FLUX.1 Schnell")
    print(f"Steps: {steps}")
    print("Output will be prepared as 9:16")
    print()
    print(
        "Requesting image from Cloudflare AI..."
    )
    print()

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=180
    )

    # --------------------------------------------------------
    # API ERROR
    # --------------------------------------------------------

    if not response.ok:

        print()
        print(
            "Cloudflare image generation failed:"
        )

        print(
            response.text
        )

        response.raise_for_status()

    # --------------------------------------------------------
    # READ CLOUDFLARE RESPONSE
    # --------------------------------------------------------

    try:

        data = response.json()

    except Exception as error:

        raise RuntimeError(
            "Cloudflare returned an invalid JSON response."
        ) from error

    # --------------------------------------------------------
    # CHECK API SUCCESS
    # --------------------------------------------------------

    if data.get("success") is False:

        raise RuntimeError(
            "Cloudflare AI reported a failed generation:\n"
            + str(data)
        )

    result = data.get(
        "result"
    )

    if not isinstance(
        result,
        dict
    ):

        raise RuntimeError(
            "Cloudflare response did not contain "
            "a valid result object."
        )

    # --------------------------------------------------------
    # FLUX IMAGE IS BASE64
    # --------------------------------------------------------

    image_base64 = result.get(
        "image"
    )

    if not image_base64:

        raise RuntimeError(
            "Cloudflare FLUX response did not contain "
            "the generated image."
        )

    try:

        image_bytes = base64.b64decode(
            image_base64
        )

    except Exception as error:

        raise RuntimeError(
            "Could not decode the FLUX image."
        ) from error

    if not image_bytes:

        raise RuntimeError(
            "Cloudflare returned an empty decoded image."
        )

    # --------------------------------------------------------
    # SAVE IMAGE
    # --------------------------------------------------------

    with open(
        output_file,
        "wb"
    ) as image_file:

        image_file.write(
            image_bytes
        )

    print(
        "FLUX image decoded and saved successfully."
    )

    # --------------------------------------------------------
    # VERIFY IMAGE
    # --------------------------------------------------------

    try:

        with Image.open(
            output_file
        ) as image:

            image.verify()

    except Exception as error:

        raise RuntimeError(
            "FLUX returned data that is not a valid image."
        ) from error

    print(
        "Generated file passed image validation."
    )

    # --------------------------------------------------------
    # BLANK IMAGE PROTECTION
    # --------------------------------------------------------

    check_generated_image(
        output_file
    )

    return output_file


# ============================================================
# BASIC IMAGE QUALITY CHECK
# ============================================================

def check_generated_image(
    image_file
):

    print()
    print(
        "Checking generated image..."
    )

    image = Image.open(
        image_file
    ).convert("RGB")

    sample = image.resize(
        (
            100,
            100
        )
    )

    stat = ImageStat.Stat(
        sample
    )

    mean_rgb = stat.mean

    average_brightness = (
        sum(mean_rgb) / 3
    )

    pixels = list(
        sample.getdata()
    )

    near_white_pixels = 0

    for pixel in pixels:

        r, g, b = pixel

        if (
            r >= 245
            and g >= 245
            and b >= 245
        ):

            near_white_pixels += 1

    near_white_percentage = (
        near_white_pixels
        / len(pixels)
        * 100
    )

    print(
        f"Average brightness: "
        f"{average_brightness:.2f}"
    )

    print(
        f"Near-white pixels: "
        f"{near_white_percentage:.2f}%"
    )

    # --------------------------------------------------------
    # REJECT EXTREMELY BLANK IMAGE
    # --------------------------------------------------------

    if (
        average_brightness >= 248
        and near_white_percentage >= 97
    ):

        raise RuntimeError(
            "Generated image appears to be almost completely "
            "white or blank. Instagram publishing stopped."
        )

    print(
        "Image passed blank-image protection."
    )


# ============================================================
# PREPARE INSTAGRAM 9:16 IMAGE
# ============================================================

def make_vertical_image(
    input_file="daily_image.png",
    output_file="instagram_image.jpg"
):

    print()
    print(
        "Preparing Instagram image..."
    )

    image = Image.open(
        input_file
    ).convert("RGB")

    print(
        f"Generated image size: "
        f"{image.width} x {image.height}"
    )

    target_width = 1080
    target_height = 1920

    target_ratio = (
        target_width / target_height
    )

    image_ratio = (
        image.width / image.height
    )

    # --------------------------------------------------------
    # CROP TO 9:16 IF REQUIRED
    # --------------------------------------------------------

    if abs(
        image_ratio - target_ratio
    ) > 0.01:

        print(
            "Adjusting image to exact 9:16 ratio..."
        )

        if image_ratio > target_ratio:

            # Image is wider than 9:16.
            # Crop the sides.

            new_width = int(
                image.height * target_ratio
            )

            left = (
                image.width - new_width
            ) // 2

            right = (
                left + new_width
            )

            image = image.crop(
                (
                    left,
                    0,
                    right,
                    image.height
                )
            )

        else:

            # Image is taller than 9:16.
            # Crop top and bottom.

            new_height = int(
                image.width / target_ratio
            )

            top = (
                image.height - new_height
            ) // 2

            bottom = (
                top + new_height
            )

            image = image.crop(
                (
                    0,
                    top,
                    image.width,
                    bottom
                )
            )

    # --------------------------------------------------------
    # FINAL INSTAGRAM SIZE
    # --------------------------------------------------------

    image = image.resize(
        (
            target_width,
            target_height
        ),
        Image.Resampling.LANCZOS
    )

    # --------------------------------------------------------
    # SAVE FINAL JPEG
    # --------------------------------------------------------

    image.save(
        output_file,
        "JPEG",
        quality=95,
        optimize=True
    )

    print()
    print(
        f"Instagram image saved: "
        f"{target_width} x {target_height}"
    )

    print(
        "Final aspect ratio: 9:16"
    )

    print(
        "=========================================="
    )

    return output_file
