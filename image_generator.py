import os
import requests
from PIL import Image


# ============================================================
# CLOUDFLARE IMAGE GENERATION
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
    # CURRENT MODEL
    # --------------------------------------------------------

    model = (
        "@cf/bytedance/"
        "stable-diffusion-xl-lightning"
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
    # --------------------------------------------------------
    #
    # These specifically target the types of problems visible
    # in the previous Instagram image.
    #

    negative_prompt = (
        "cartoon, illustration, anime, painting, drawing, "
        "3d render, CGI, computer generated, game graphics, "
        "plastic appearance, artificial appearance, "
        "fake looking photograph, oversaturated, "
        "unrealistic lighting, unrealistic reflections, "
        "distorted objects, warped objects, melted objects, "
        "floating objects, duplicate objects, "
        "extra objects, impossible geometry, "
        "deformed plumbing, twisted pipes, broken pipes, "
        "incorrect pipe connections, impossible plumbing layout, "
        "duplicate faucet, malformed faucet, "
        "deformed hands, malformed hands, extra fingers, "
        "missing fingers, fused fingers, extra arms, "
        "extra limbs, disconnected arms, "
        "unnatural human anatomy, distorted face, "
        "deformed body, unnatural pose, "
        "bad proportions, artificial skin, "
        "fake water, impossible water flow, "
        "water coming from wrong location, "
        "floating water, duplicated water streams, "
        "blurry, low detail, low quality, pixelated, "
        "text, words, letters, numbers, labels, "
        "logo, watermark, brand name, caption, "
        "social media graphic, advertisement, poster"
    )

    # --------------------------------------------------------
    # VERTICAL GENERATION
    # --------------------------------------------------------
    #
    # Generate 9:16 from the beginning instead of generating
    # square and cropping afterward.
    #

    width = 864
    height = 1536

    payload = {

        "prompt": image_prompt,

        "negative_prompt": negative_prompt,

        "height": height,

        "width": width,

        # More steps than the old 4-step generation.
        "num_steps": 8,

        # Helps the model follow the detailed prompt.
        "guidance": 6.5
    }

    print()
    print("==========================================")
    print("CLOUDFLARE IMAGE GENERATION")
    print("==========================================")
    print(f"Model: {model}")
    print(f"Generation size: {width} x {height}")
    print("Aspect ratio: 9:16")
    print("Diffusion steps: 8")
    print("Guidance: 6.5")
    print()
    print("Requesting image from Cloudflare AI...")

    # --------------------------------------------------------
    # SEND REQUEST
    # --------------------------------------------------------

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
    # SAVE ORIGINAL GENERATED IMAGE
    # --------------------------------------------------------

    with open(
        output_file,
        "wb"
    ) as image_file:

        image_file.write(
            response.content
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
            "Cloudflare returned data that is not a valid image."
        ) from error

    print()
    print(
        "Cloudflare image generated successfully."
    )

    return output_file


# ============================================================
# CREATE INSTAGRAM 9:16 IMAGE
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

    # --------------------------------------------------------
    # TARGET INSTAGRAM SIZE
    # --------------------------------------------------------

    target_width = 1080
    target_height = 1920

    target_ratio = (
        target_width / target_height
    )

    image_ratio = (
        image.width / image.height
    )

    # --------------------------------------------------------
    # ONLY CROP IF NECESSARY
    # --------------------------------------------------------
    #
    # The generator already creates 9:16.
    # This is simply a safety check.
    #

    if abs(
        image_ratio - target_ratio
    ) > 0.01:

        print(
            "Image ratio differs from 9:16."
        )

        if image_ratio > target_ratio:

            # Image is too wide.
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
    # RESIZE TO INSTAGRAM SIZE
    # --------------------------------------------------------

    image = image.resize(
        (
            target_width,
            target_height
        ),
        Image.Resampling.LANCZOS
    )

    # --------------------------------------------------------
    # SAVE HIGH-QUALITY JPEG
    # --------------------------------------------------------

    image.save(
        output_file,
        "JPEG",
        quality=95,
        optimize=True
    )

    print(
        f"Instagram image saved: "
        f"{target_width} x {target_height}"
    )

    print(
        "=========================================="
    )

    return output_file
