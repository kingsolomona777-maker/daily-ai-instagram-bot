"""
Orom Plan1 Teaching Reel Generator

Creates a short educational plumbing Reel from one vertical image.

The Reel has three teaching stages:

1. Hook
2. Teaching point
3. Takeaway

Safety:
    - No Gemini API calls
    - No Cloudflare API calls
    - No Instagram API calls
    - No publishing
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DEFAULT_INPUT = "instagram_image.jpg"
DEFAULT_OUTPUT = "orom_plan1_reel.mp4"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 8


DEFAULT_TEACHING_TEXT = {
    "hook": "Most plumbing problems start with a small warning.",
    "explanation": "Understanding the cause early can prevent bigger damage and expensive repairs.",
    "takeaway": "Learn the warning signs and fix the real problem, not just the symptom.",
}


def check_ffmpeg() -> None:
    """Confirm that FFmpeg is available."""

    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "FFmpeg was not found on this system."
        )


def check_input_image(input_file: str | Path) -> Path:
    """Confirm that the source image exists and is usable."""

    path = Path(input_file)

    if not path.exists():
        raise FileNotFoundError(
            f"Source image was not found: {path}"
        )

    if not path.is_file():
        raise RuntimeError(
            f"Source image is not a file: {path}"
        )

    try:
        with Image.open(path) as image:
            image.verify()
    except Exception as exc:
        raise RuntimeError(
            f"Source image could not be opened: {exc}"
        ) from exc

    return path


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a reliable Linux font."""

    if bold:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for font_path in font_paths:
        path = Path(font_path)

        if path.exists():
            return ImageFont.truetype(str(path), size)

    return ImageFont.load_default()


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    max_width: int,
) -> list[str]:
    """Wrap text to fit inside the Reel panel."""

    words = text.split()

    if not words:
        return []

    lines = []
    current = words[0]

    for word in words[1:]:
        candidate = f"{current} {word}"

        bbox = draw.textbbox(
            (0, 0),
            candidate,
            font=font,
        )

        width = bbox[2] - bbox[0]

        if width <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word

    lines.append(current)

    return lines


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    center_x: int,
    start_y: int,
    font,
    fill,
    max_width: int,
    spacing: int = 14,
) -> int:
    """Draw wrapped centered text and return the ending Y position."""

    lines = wrap_text(
        draw,
        text,
        font,
        max_width,
    )

    y = start_y

    for line in lines:
        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font,
        )

        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]

        x = center_x - (line_width / 2)

        draw.text(
            (x + 3, y + 3),
            line,
            font=font,
            fill=(0, 0, 0, 150),
        )

        draw.text(
            (x, y),
            line,
            font=font,
            fill=fill,
        )

        y += line_height + spacing

    return y


def create_scene(
    source_image: Path,
    output_file: Path,
    label: str,
    text: str,
) -> None:
    """Create one educational Reel scene."""

    with Image.open(source_image).convert("RGB") as source:

        source_ratio = source.width / source.height
        target_ratio = WIDTH / HEIGHT

        if source_ratio > target_ratio:
            new_height = HEIGHT
            new_width = int(new_height * source_ratio)
        else:
            new_width = WIDTH
            new_height = int(new_width / source_ratio)

        image = source.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS,
        )

        left = max(0, (new_width - WIDTH) // 2)
        top = max(0, (new_height - HEIGHT) // 2)

        image = image.crop(
            (
                left,
                top,
                left + WIDTH,
                top + HEIGHT,
            )
        )

        canvas = image.convert("RGBA")

        overlay = Image.new(
            "RGBA",
            (WIDTH, HEIGHT),
            (0, 0, 0, 0),
        )

        draw = ImageDraw.Draw(overlay)

        panel_top = int(HEIGHT * 0.60)
        panel_bottom = HEIGHT - 100

        draw.rounded_rectangle(
            (
                55,
                panel_top,
                WIDTH - 55,
                panel_bottom,
            ),
            radius=42,
            fill=(0, 0, 0, 190),
        )

        label_font = get_font(42, bold=True)
        text_font = get_font(50, bold=True)

        label_y = panel_top + 55

        draw.text(
            (
                WIDTH // 2,
                label_y,
            ),
            label.upper(),
            font=label_font,
            anchor="ma",
            fill=(255, 255, 255, 255),
        )

        draw_centered_text(
            draw=draw,
            text=text,
            center_x=WIDTH // 2,
            start_y=label_y + 85,
            font=text_font,
            fill=(255, 255, 255, 255),
            max_width=WIDTH - 190,
            spacing=18,
        )

        final_image = Image.alpha_composite(
            canvas,
            overlay,
        )

        final_image.convert("RGB").save(
            output_file,
            "JPEG",
            quality=95,
        )


def create_scene_video(
    image_file: Path,
    output_file: Path,
    duration: float,
) -> None:
    """Turn one scene image into a moving video segment."""

    frames = max(1, int(duration * FPS))

    zoom_filter = (
        f"scale={WIDTH}:{HEIGHT}:"
        f"force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"zoompan="
        f"z='min(zoom+0.0008,1.07)':"
        f"x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)':"
        f"d={frames}:"
        f"s={WIDTH}x{HEIGHT}:"
        f"fps={FPS},"
        f"format=yuv420p"
    )

    command = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_file),
        "-vf",
        zoom_filter,
        "-t",
        str(duration),
        "-r",
        str(FPS),
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_file),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg scene generation failed:\n"
            + result.stderr
        )


def combine_scenes(
    scene_videos: list[Path],
    output_file: Path,
) -> None:
    """Combine the three scene videos into one Reel."""

    concat_file = output_file.parent / "concat.txt"

    lines = []

    for scene in scene_videos:
        safe_path = str(scene.resolve()).replace("'", "'\\''")
        lines.append(f"file '{safe_path}'")

    concat_file.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        str(output_file),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg scene combination failed:\n"
            + result.stderr
        )


def generate_reel(
    input_file: str | Path = DEFAULT_INPUT,
    output_file: str | Path = DEFAULT_OUTPUT,
    duration: int = DURATION,
    teaching_text: dict | None = None,
) -> Path:
    """
    Create a three-part educational plumbing Reel.

    teaching_text may contain:

        hook
        explanation
        takeaway
    """

    if duration < 6:
        raise ValueError(
            "Teaching Reel duration must be at least 6 seconds."
        )

    if duration > 60:
        raise ValueError(
            "Reel duration must not exceed 60 seconds."
        )

    check_ffmpeg()

    source = check_input_image(input_file)

    output = Path(output_file)
    output.parent.mkdir(parents=True, exist_ok=True)

    text = dict(DEFAULT_TEACHING_TEXT)

    if teaching_text:
        for key in text:
            value = teaching_text.get(key)

            if isinstance(value, str) and value.strip():
                text[key] = value.strip()

    scene_duration = duration / 3

    print("==========================================")
    print("OROM PLAN1 TEACHING REEL GENERATOR")
    print("==========================================")
    print(f"Source image : {source}")
    print(f"Output Reel  : {output}")
    print(f"Resolution   : {WIDTH}x{HEIGHT}")
    print(f"FPS          : {FPS}")
    print(f"Duration     : {duration} seconds")
    print("Scenes       : Hook → Teaching → Takeaway")
    print("Audio        : None")
    print("Instagram    : Not connected")
    print("==========================================")

    with tempfile.TemporaryDirectory(
        prefix="orom_plan1_reel_"
    ) as temp_dir:

        temp = Path(temp_dir)

        scene_images = [
            temp / "scene_1_hook.jpg",
            temp / "scene_2_teaching.jpg",
            temp / "scene_3_takeaway.jpg",
        ]

        create_scene(
            source,
            scene_images[0],
            "Hook",
            text["hook"],
        )

        create_scene(
            source,
            scene_images[1],
            "Teaching point",
            text["explanation"],
        )

        create_scene(
            source,
            scene_images[2],
            "Takeaway",
            text["takeaway"],
        )

        scene_videos = []

        for index, scene_image in enumerate(
            scene_images,
            start=1,
        ):
            scene_video = temp / f"scene_{index}.mp4"

            create_scene_video(
                scene_image,
                scene_video,
                scene_duration,
            )

            scene_videos.append(scene_video)

        combine_scenes(
            scene_videos,
            output,
        )

    if not output.exists():
        raise RuntimeError(
            "The Reel file was not created."
        )

    file_size = output.stat().st_size

    if file_size < 10_000:
        raise RuntimeError(
            "The generated Reel file is unexpectedly small."
        )

    print()
    print("==========================================")
    print("TEACHING REEL CREATED SUCCESSFULLY")
    print("==========================================")
    print(f"File: {output}")
    print(f"Size: {file_size:,} bytes")
    print("==========================================")

    return output


if __name__ == "__main__":
    generate_reel()
