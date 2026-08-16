import os
import requests


def generate_image(image_prompt, output_file="daily_image.png"):
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN")

    if not account_id:
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID is not available.")

    if not api_token:
        raise RuntimeError("CLOUDFLARE_API_TOKEN is not available.")

    model = "@cf/bytedance/stable-diffusion-xl-lightning"

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/"
        f"{account_id}/ai/run/{model}"
    )

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": image_prompt,
        "negative_prompt": (
            "blurry, distorted plumbing equipment, "
            "unrealistic pipes, text, watermark, logo"
        ),
        "height": 1024,
        "width": 1024,
        "num_steps": 4
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    with open(output_file, "wb") as image_file:
        image_file.write(response.content)

    return output_file
