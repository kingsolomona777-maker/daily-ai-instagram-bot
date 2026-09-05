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
    # TEST 3 MODEL
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
    # STRONG NEGATIVE PROMPT
    # --------------------------------------------------------

    negative_prompt = (
        "cartoon, illustration, anime, painting, drawing, "
        "3d render, CGI, computer graphics, game graphics, "
        "plastic looking, artificial looking, fake photograph, "
        "unrealistic plumbing, impossible plumbing, "
        "incorrect plumbing geometry, malformed plumbing, "
        "warped plumbing, twisted pipes, bent pipes, "
        "impossible pipe connections, disconnected pipes, "
        "floating pipes, duplicated pipes, extra pipes, "
        "duplicate toilet, duplicate faucet, duplicate sink, "
        "duplicate plumbing fixtures, "
        "deformed toilet, malformed toilet, "
        "warped toilet bowl, duplicated toilet seat, "
        "multiple toilet lids, multiple toilet bowls, "
        "impossible toilet structure, "
        "deformed faucet, malformed faucet, "
        "duplicate faucet handles, "
        "incorrect water outlet, "
        "water coming from wrong location, "
        "floating water, impossible water flow, "
        "duplicate water streams, "
        "deformed hands, malformed hands, "
        "extra fingers, missing fingers, fused fingers, "
        "extra arms, extra limbs, disconnected arms, "
        "unnatural human anatomy, distorted face, "
        "deformed body, unnatural pose, "
        "bad proportions, artificial skin, "
        "blurry, low detail, low quality, pixelated, "
        "overprocessed, oversharpened, "
        "text, words, letters, numbers, "
        "labels, signs, logo, watermark, "
        "brand name, caption, advertisement, poster, "
        "social media graphic, UI"
    )

    # --------------------------------------------------------
    # TRUE 9:16 GENERATION
    # --------------------------------------------------------

    width = 768
    height = 1365

    payload = {
        "prompt": image_prompt,
        "negative_prompt": negative_prompt,
        "height": height,
        "width": width,
        "num_steps": 12,
        "guidance": 7.0
    }

    print()
    print("==========================================")
    print("CLOUDFLARE IMAGE GENERATION - TEST 3")
    print("==========================================")
    print(f"Model: {model}")
    print(f"Generation size: {width} x {height}")
    print("Aspect ratio: 9:16")
    print("Diffusion steps: 12")
    print("Guidance: 7.0")
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
    # CROP ONLY IF NECESSARY
    # --------------------------------------------------------

    if abs(
        image_ratio - target_ratio
    ) > 0.01:

        print(
            "Adjusting image to exact 9:16 ratio..."
        )

        if image_ratio > target_ratio:

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
    # SAVE JPEG
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
