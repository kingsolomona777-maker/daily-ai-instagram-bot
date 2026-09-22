import os
import base64
import requests
from PIL import Image, ImageStat, ImageDraw, ImageFont


# ============================================================
# CLOUDFLARE IMAGE GENERATION
# OROM PLAN1
# FLUX.1 SCHNELL
#
# VERSION:
# Premium Educational Image System
#
# PIPELINE:
# Gemini scene prompt
#        ↓
# FLUX clean photograph
#        ↓
# Python educational text overlay
#        ↓
# 1080 x 1920 Instagram image
#
# IMPORTANT:
# FLUX DOES NOT generate the educational text.
# Python adds the exact text separately.
# ============================================================


# ============================================================
# FONT HELPERS
# ============================================================

def get_font(
    size,
    bold=False
):
    """
    Find a commonly available font.

    The system is designed to work on GitHub Actions/Linux,
    while also falling back safely if a particular font is
    unavailable.
    """

    possible_fonts = []

    if bold:

        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/"
            "DejaVuSans-Bold.ttf",

            "/usr/share/fonts/truetype/liberation2/"
            "LiberationSans-Bold.ttf"
        ]

    else:

        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/"
            "DejaVuSans.ttf",

            "/usr/share/fonts/truetype/liberation2/"
            "LiberationSans-Regular.ttf"
        ]

    for font_path in possible_fonts:

        if os.path.exists(font_path):

            return ImageFont.truetype(
                font_path,
                size
            )

    return ImageFont.load_default()


# ============================================================
# TEXT WRAPPING
# ============================================================

def wrap_text(
    draw,
    text,
    font,
    max_width
):

    words = str(
        text
    ).split()

    if not words:

        return ""

    lines = []

    current_line = words[0]

    for word in words[1:]:

        test_line = (
            current_line
            + " "
            + word
        )

        bbox = draw.textbbox(
            (0, 0),
            test_line,
            font=font
        )

        width = (
            bbox[2]
            - bbox[0]
        )

        if width <= max_width:

            current_line = test_line

        else:

            lines.append(
                current_line
            )

            current_line = word

    lines.append(
        current_line
    )

    return "\n".join(
        lines
    )


# ============================================================
# DRAW TEXT WITH SHADOW
# ============================================================

def draw_text_with_shadow(
    draw,
    position,
    text,
    font,
    fill,
    shadow_fill,
    shadow_offset=3
):

    x, y = position

    draw.text(
        (
            x + shadow_offset,
            y + shadow_offset
        ),
        text,
        font=font,
        fill=shadow_fill
    )

    draw.text(
        (
            x,
            y
        ),
        text,
        font=font,
        fill=fill
    )


# ============================================================
# DRAW ROUNDED TEXT PANEL
# ============================================================

def draw_panel(
    draw,
    box,
    radius=28
):

    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=(0, 0, 0, 185)
    )


# ============================================================
# CREATE EDUCATIONAL OVERLAY
# ============================================================

def add_educational_text(
    image_file,
    on_image_text,
    output_file
):

    print()
    print(
        "Adding educational text overlay..."
    )

    # --------------------------------------------------------
    # VALIDATE TEXT OBJECT
    # --------------------------------------------------------

    if not isinstance(
        on_image_text,
        dict
    ):

        raise RuntimeError(
            "on_image_text must be a dictionary."
        )

    hook = str(
        on_image_text.get(
            "hook",
            ""
        )
    ).strip()

    explanation = str(
        on_image_text.get(
            "explanation",
            ""
        )
    ).strip()

    callout = str(
        on_image_text.get(
            "callout",
            ""
        )
    ).strip()

    takeaway = str(
        on_image_text.get(
            "takeaway",
            ""
        )
    ).strip()

    if not hook:

        raise RuntimeError(
            "Educational image hook is empty."
        )

    if not explanation:

        raise RuntimeError(
            "Educational image explanation is empty."
        )

    if not takeaway:

        raise RuntimeError(
            "Educational image takeaway is empty."
        )

    # --------------------------------------------------------
    # OPEN IMAGE
    # --------------------------------------------------------

    image = Image.open(
        image_file
    ).convert(
        "RGBA"
    )

    # --------------------------------------------------------
    # ENSURE EXACT INSTAGRAM SIZE
    # --------------------------------------------------------

    target_width = 1080
    target_height = 1920

    if (
        image.width != target_width
        or image.height != target_height
    ):

        image = image.resize(
            (
                target_width,
                target_height
            ),
            Image.Resampling.LANCZOS
        )

    # --------------------------------------------------------
    # CREATE DRAWING LAYER
    # --------------------------------------------------------

    overlay = Image.new(
        "RGBA",
        image.size,
        (
            0,
            0,
            0,
            0
        )
    )

    draw = ImageDraw.Draw(
        overlay
    )

    # --------------------------------------------------------
    # FONTS
    # --------------------------------------------------------

    hook_font = get_font(
        76,
        bold=True
    )

    explanation_font = get_font(
        38,
        bold=False
    )

    callout_font = get_font(
        32,
        bold=True
    )

    takeaway_font = get_font(
        40,
        bold=True
    )

    # --------------------------------------------------------
    # COMMON SETTINGS
    # --------------------------------------------------------

    margin = 70

    maximum_text_width = (
        target_width
        - (margin * 2)
    )

    # --------------------------------------------------------
    # HOOK
    # --------------------------------------------------------

    hook_text = wrap_text(
        draw,
        hook,
        hook_font,
        maximum_text_width
    )

    hook_bbox = draw.multiline_textbbox(
        (
            0,
            0
        ),
        hook_text,
        font=hook_font,
        spacing=8
    )

    hook_width = (
        hook_bbox[2]
        - hook_bbox[0]
    )

    hook_height = (
        hook_bbox[3]
        - hook_bbox[1]
    )

    hook_x = (
        target_width
        - hook_width
    ) // 2

    hook_y = 85

    # --------------------------------------------------------
    # HOOK PANEL
    # --------------------------------------------------------

    hook_panel_left = 45

    hook_panel_top = (
        hook_y
        - 25
    )

    hook_panel_right = (
        target_width
        - 45
    )

    hook_panel_bottom = (
        hook_y
        + hook_height
        + 35
    )

    draw_panel(
        draw,
        (
            hook_panel_left,
            hook_panel_top,
            hook_panel_right,
            hook_panel_bottom
        ),
        radius=32
    )

    draw_text_with_shadow(
        draw,
        (
            hook_x,
            hook_y
        ),
        hook_text,
        hook_font,
        fill=(255, 255, 255, 255),
        shadow_fill=(0, 0, 0, 180),
        shadow_offset=4
    )

    # --------------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------------

    explanation_text = wrap_text(
        draw,
        explanation,
        explanation_font,
        maximum_text_width - 40
    )

    explanation_bbox = draw.multiline_textbbox(
        (
            0,
            0
        ),
        explanation_text,
        font=explanation_font,
        spacing=7
    )

    explanation_width = (
        explanation_bbox[2]
        - explanation_bbox[0]
    )

    explanation_height = (
        explanation_bbox[3]
        - explanation_bbox[1]
    )

    explanation_x = (
        target_width
        - explanation_width
    ) // 2

    explanation_y = (
        hook_panel_bottom
        + 28
    )

    # --------------------------------------------------------
    # EXPLANATION PANEL
    # --------------------------------------------------------

    explanation_panel_left = 65

    explanation_panel_top = (
        explanation_y
        - 18
    )

    explanation_panel_right = (
        target_width
        - 65
    )

    explanation_panel_bottom = (
        explanation_y
        + explanation_height
        + 25
    )

    draw_panel(
        draw,
        (
            explanation_panel_left,
            explanation_panel_top,
            explanation_panel_right,
            explanation_panel_bottom
        ),
        radius=25
    )

    draw_text_with_shadow(
        draw,
        (
            explanation_x,
            explanation_y
        ),
        explanation_text,
        explanation_font,
        fill=(255, 255, 255, 255),
        shadow_fill=(0, 0, 0, 160),
        shadow_offset=2
    )

    # --------------------------------------------------------
    # CALLOUT
    # --------------------------------------------------------

    if callout:

        callout_text = wrap_text(
            draw,
            callout,
            callout_font,
            360
        )

        callout_bbox = draw.multiline_textbbox(
            (
                0,
                0
            ),
            callout_text,
            font=callout_font,
            spacing=5
        )

        callout_width = (
            callout_bbox[2]
            - callout_bbox[0]
        )

        callout_height = (
            callout_bbox[3]
            - callout_bbox[1]
        )

        callout_x = (
            target_width
            - callout_width
            - 70
        )

        # Place the callout below the upper
        # text area while leaving the main
        # plumbing scene visible.

        callout_y = (
            explanation_panel_bottom
            + 45
        )

        callout_panel_left = (
            callout_x
            - 22
        )

        callout_panel_top = (
            callout_y
            - 15
        )

        callout_panel_right = (
            target_width
            - 45
        )

        callout_panel_bottom = (
            callout_y
            + callout_height
            + 18
        )

        draw_panel(
            draw,
            (
                callout_panel_left,
                callout_panel_top,
                callout_panel_right,
                callout_panel_bottom
            ),
            radius=20
        )

        draw_text_with_shadow(
            draw,
            (
                callout_x,
                callout_y
            ),
            callout_text,
            callout_font,
            fill=(255, 255, 255, 255),
            shadow_fill=(0, 0, 0, 150),
            shadow_offset=2
        )

    # --------------------------------------------------------
    # TAKEAWAY
    # --------------------------------------------------------

    takeaway_text = wrap_text(
        draw,
        takeaway,
        takeaway_font,
        maximum_text_width - 50
    )

    takeaway_bbox = draw.multiline_textbbox(
        (
            0,
            0
        ),
        takeaway_text,
        font=takeaway_font,
        spacing=7
    )

    takeaway_width = (
        takeaway_bbox[2]
        - takeaway_bbox[0]
    )

    takeaway_height = (
        takeaway_bbox[3]
        - takeaway_bbox[1]
    )

    takeaway_x = (
        target_width
        - takeaway_width
    ) // 2

    takeaway_y = (
        target_height
        - takeaway_height
        - 110
    )

    # --------------------------------------------------------
    # TAKEAWAY PANEL
    # --------------------------------------------------------

    takeaway_panel_left = 45

    takeaway_panel_top = (
        takeaway_y
        - 25
    )

    takeaway_panel_right = (
        target_width
        - 45
    )

    takeaway_panel_bottom = (
        takeaway_y
        + takeaway_height
        + 35
    )

    draw_panel(
        draw,
        (
            takeaway_panel_left,
            takeaway_panel_top,
            takeaway_panel_right,
            takeaway_panel_bottom
        ),
        radius=30
    )

    draw_text_with_shadow(
        draw,
        (
            takeaway_x,
            takeaway_y
        ),
        takeaway_text,
        takeaway_font,
        fill=(255, 255, 255, 255),
        shadow_fill=(0, 0, 0, 180),
        shadow_offset=3
    )

    # --------------------------------------------------------
    # COMBINE
    # --------------------------------------------------------

    final_image = Image.alpha_composite(
        image,
        overlay
    )

    # --------------------------------------------------------
    # SAVE JPEG
    # --------------------------------------------------------

    final_image = final_image.convert(
        "RGB"
    )

    final_image.save(
        output_file,
        "JPEG",
        quality=95,
        optimize=True
    )

    print(
        "Educational text overlay added successfully."
    )

    print(
        f"Final image: "
        f"{target_width} x {target_height}"
    )

    return output_file


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
    # BUILD COMPACT FLUX PROMPT
    # --------------------------------------------------------

    prompt_prefix = """
Photorealistic professional residential plumbing photograph.

Physical accuracy is critical:
one coherent plumbing system, realistic pipe geometry,
correct fittings and joints, realistic materials and
proportions, physically possible connections.

Natural real-world photography, not CGI, illustration,
cartoon or 3D render.

Keep the main plumbing subject clear and centered.
Avoid unnecessary people, hands or complicated anatomy.

No text, words, letters, numbers, labels, logos, watermarks,
advertisements, duplicated objects, warped plumbing,
impossible geometry, floating objects or deformed equipment.

Clean image composition suitable for educational text overlay.

Scene:
""".strip()

    scene_prompt = str(
        image_prompt
    ).strip()

    # --------------------------------------------------------
    # REMOVE LONG DASHES FROM PROMPT
    # --------------------------------------------------------

    scene_prompt = (
        scene_prompt
        .replace("—", ", ")
        .replace("–", ", ")
        .replace("−", ", ")
    )

    # --------------------------------------------------------
    # 2048 CHARACTER PROTECTION
    # --------------------------------------------------------

    maximum_scene_length = (
        2048
        - len(prompt_prefix)
    )

    if maximum_scene_length <= 0:

        raise RuntimeError(
            "FLUX prompt configuration is longer than "
            "the allowed 2048 characters."
        )

    if len(scene_prompt) > maximum_scene_length:

        scene_prompt = (
            scene_prompt[
                :maximum_scene_length
            ]
            .rsplit(" ", 1)[0]
            .rstrip()
        )

        print(
            "Gemini image prompt was shortened "
            "to fit FLUX.1 Schnell's 2048-character limit."
        )

    flux_prompt = (
        prompt_prefix
        + "\n"
        + scene_prompt
    ).strip()

    # --------------------------------------------------------
    # FINAL SAFETY CHECK
    # --------------------------------------------------------

    if len(flux_prompt) > 2048:

        flux_prompt = (
            flux_prompt[
                :2048
            ]
            .rsplit(" ", 1)[0]
            .rstrip()
        )

    print(
        f"FLUX prompt length: "
        f"{len(flux_prompt)} / 2048"
    )

    # --------------------------------------------------------
    # FLUX SETTINGS
    # --------------------------------------------------------

    steps = 8

    payload = {
        "prompt": flux_prompt,
        "steps": steps
    }

    print()
    print(
        "=========================================="
    )

    print(
        "CLOUDFLARE IMAGE GENERATION"
    )

    print(
        "=========================================="
    )

    print(
        f"Model: {model}"
    )

    print(
        "Generation model: FLUX.1 Schnell"
    )

    print(
        f"Steps: {steps}"
    )

    print(
        "Output will be prepared as 9:16"
    )

    print()

    print(
        "Requesting image from Cloudflare AI..."
    )

    print()

    # --------------------------------------------------------
    # SEND REQUEST
    # --------------------------------------------------------

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
    # READ RESPONSE
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

    if data.get(
        "success"
    ) is False:

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
    # FLUX IMAGE
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
    # SAVE GENERATED IMAGE
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
    ).convert(
        "RGB"
    )

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
    output_file="instagram_image.jpg",
    on_image_text=None
):

    print()

    print(
        "Preparing Instagram image..."
    )

    image = Image.open(
        input_file
    ).convert(
        "RGB"
    )

    print(
        f"Generated image size: "
        f"{image.width} x {image.height}"
    )

    target_width = 1080
    target_height = 1920

    target_ratio = (
        target_width
        / target_height
    )

    image_ratio = (
        image.width
        / image.height
    )

    # --------------------------------------------------------
    # CROP TO 9:16 IF REQUIRED
    # --------------------------------------------------------

    if abs(
        image_ratio
        - target_ratio
    ) > 0.01:

        print(
            "Adjusting image to exact 9:16 ratio..."
        )

        if image_ratio > target_ratio:

            # Image is wider than 9:16.
            # Crop the sides.

            new_width = int(
                image.height
                * target_ratio
            )

            left = (
                image.width
                - new_width
            ) // 2

            right = (
                left
                + new_width
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
                image.width
                / target_ratio
            )

            top = (
                image.height
                - new_height
            ) // 2

            bottom = (
                top
                + new_height
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
    # TEMPORARY CLEAN IMAGE
    # --------------------------------------------------------

    clean_output = (
        output_file
        + ".clean.jpg"
    )

    image.save(
        clean_output,
        "JPEG",
        quality=95,
        optimize=True
    )

    # --------------------------------------------------------
    # ADD EDUCATIONAL TEXT
    # --------------------------------------------------------

    if on_image_text is not None:

        add_educational_text(
            clean_output,
            on_image_text,
            output_file
        )

        try:

            os.remove(
                clean_output
            )

        except OSError:

            pass

    else:

        # Preserve old behaviour when
        # no text object is supplied.

        image.save(
            output_file,
            "JPEG",
            quality=95,
            optimize=True
        )

        try:

            os.remove(
                clean_output
            )

        except OSError:

            pass

    print()

    print(
        f"Instagram image saved: "
        f"{target_width} x {target_height}"
    )

    print(
        "Final aspect ratio: 9:16"
    )

    if on_image_text is not None:

        print(
            "Educational text overlay: ENABLED"
        )

    else:

        print(
            "Educational text overlay: NOT ENABLED"
        )

    print(
        "=========================================="
    )

    return output_file
