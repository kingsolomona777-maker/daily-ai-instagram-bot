import os
import requests
from PIL import Image


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


    payload = {

        "prompt": image_prompt,

        "negative_prompt": (
            "blurry, distorted plumbing equipment, "
            "unrealistic pipes, text, watermark, logo, "
            "bad anatomy, duplicate objects, "
            "low quality"
        ),

        "height": 1024,

        "width": 1024,

        "num_steps": 4
    }


    print("Requesting image from Cloudflare AI...")


    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120
    )


    if not response.ok:

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


    # Confirm that the file is actually an image
    try:

        with Image.open(
            output_file
        ) as image:

            image.verify()

    except Exception as error:

        raise RuntimeError(
            "Cloudflare returned data that is not a valid image."
        ) from error


    return output_file


def make_vertical_image(
    input_file="daily_image.png",
    output_file="instagram_image.jpg"
):

    image = Image.open(
        input_file
    ).convert("RGB")


    target_width = 1080
    target_height = 1920


    target_ratio = (
        target_width / target_height
    )

    image_ratio = (
        image.width / image.height
    )


    if image_ratio > target_ratio:

        # Wider than 9:16.
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

        # Taller/narrower than 9:16.
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


    image = image.resize(
        (
            target_width,
            target_height
        ),
        Image.Resampling.LANCZOS
    )


    image.save(
        output_file,
        "JPEG",
        quality=95,
        optimize=True
    )


    return output_file
