import os
import requests
from PIL import Image, ImageFilter

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

def make_vertical_image(input_file="daily_image.png",
                        output_file="instagram_image.png"):

    image = Image.open(input_file).convert("RGB")

    target_width = 1080
    target_height = 1920

    # Create a blurred background from the original image
    background = image.resize((target_width, target_height))
    background = background.filter(ImageFilter.GaussianBlur(25))

    # Resize the original image while keeping its proportions
    foreground = image.copy()
    foreground.thumbnail((target_width, target_width))

    # Center the original image vertically
    x = (target_width - foreground.width) // 2
    y = (target_height - foreground.height) // 2

    background.paste(foreground, (x, y))

    background.save(
        output_file,
        "JPEG",
        quality=95,
        optimize=True
    )

    return output_file
