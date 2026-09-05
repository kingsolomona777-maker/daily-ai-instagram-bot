import os
import requests
from PIL import Image, ImageStat


# ============================================================
# CLOUDFLARE IMAGE GENERATION
# TEST 4 - DREAMSHAPER 8 LCM
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
    # DREAMSHAPER 8 LCM
    # --------------------------------------------------------

    model = (
        "@cf/lykon/"
        "dreamshaper-8-lcm"
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
    # NEGATIVE PROMPT
    #
    # Keep this relatively short for the LCM test.
    # We don't want an enormous negative prompt fighting
    # against the model.
    # --------------------------------------------------------

    negative_prompt = (
        "cartoon, anime, illustration, painting, "
        "3d render, CGI, game graphics, "
        "unrealistic plumbing, impossible geometry, "
        "warped pipes, twisted pipes, floating pipes, "
        "duplicate objects, duplicate plumbing fixtures, "
        "deformed toilet, malformed faucet, "
        "incorrect water flow, "
        "deformed hands, extra fingers, extra limbs, "
        "bad anatomy, distorted face, "
        "text, letters, numbers, labels, signs, "
        "logo, watermark, advertisement, poster, "
        "blurry, pixelated, low quality"
    )

    # --------------------------------------------------------
    # GENERATION SETTINGS
    #
    # DreamShaper 8 LCM model card uses:
    # 15 inference steps
    # guidance scale 2
    #
    # Both dimensions are divisible by 8.
    # 864 x 1536 is exactly 9:16.
    # --------------------------------------------------------

    width = 864
    height = 1536

    num_steps = 15
    guidance = 2.0

    payload = {
        "prompt": image_prompt,
        "negative_prompt": negative_prompt,
        "height": height,
        "width": width,
        "num_steps": num_steps,
        "guidance": guidance
    }

    print()
    print("==========================================")
    print("CLOUDFLARE IMAGE GENERATION - TEST 4")
    print("==========================================")
    print(f"Model: {model}")
    print(f"Generation size: {width} x {height}")
    print("Aspect ratio: 9:16")
    print(f"Diffusion steps: {num_steps}")
    print(f"Guidance: {guidance}")
    print()
    print("Requesting image from Cloudflare AI...")
    print()

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=180
    )

    if not response.ok:

        print()
        print(
            "Cloudflare image generation failed:"
        )

        print(
            response.text
        )

        response.raise_for_status()

    if not response.content:

        raise RuntimeError(
            "Cloudflare returned an empty image response."
        )

    # --------------------------------------------------------
    # SAVE GENERATED IMAGE
    # --------------------------------------------------------

    with open(
        output_file,
        "wb"
    ) as image_file:

        image_file.write(
            response.content
        )

    # --------------------------------------------------------
    # VERIFY THAT CLOUDFLARE RETURNED AN IMAGE
    # --------------------------------------------------------

    try:

        with Image.open(
            output_file
        ) as image:

            image.verify()

    except Exception as error:

        raise RuntimeError(
            "Cloudflare returned data that is not a valid image."
        ) from error

    print()
    print(
        "Cloudflare image generated successfully."
    )

    # --------------------------------------------------------
    # BASIC BLANK/WHITE IMAGE PROTECTION
    #
    # This prevents an obviously broken image from continuing
    # through the Instagram publishing pipeline.
    # --------------------------------------------------------

    check_generated_image(
        output_file
    )

    return output_file


# ============================================================
# IMAGE QUALITY SAFETY CHECK
# ============================================================

def check_generated_image(
    image_file
):

    print()
    print(
        "Checking generated image quality..."
    )

    image = Image.open(
        image_file
    ).convert("RGB")

    # Resize for a fast statistical check.
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

    # Count pixels that are extremely close to white.
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
    # REJECT OBVIOUSLY BLANK IMAGE
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
        "Image passed basic blank-image check."
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
    # ADJUST RATIO IF NECESSARY
    # --------------------------------------------------------

    if abs(
        image_ratio - target_ratio
    ) > 0.01:

        print(
            "Adjusting image to exact 9:16 ratio..."
        )

        if image_ratio > target_ratio:

            # Image is too wide.
            # Crop left and right.

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

            # Image is too tall.
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
