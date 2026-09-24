"""
Orom Plan1 Reel Generator

Purpose:
    Convert an educational vertical plumbing image into a short Instagram Reel.

Safety:
    - Does not call Gemini.
    - Does not call Cloudflare.
    - Does not call Instagram.
    - Does not publish anything.
    - Does not modify project memory.

The production workflow can use this module later after testing is complete.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


DEFAULT_INPUT = "instagram_image.jpg"
DEFAULT_OUTPUT = "orom_plan1_reel.mp4"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 8


def check_ffmpeg() -> None:
    """Make sure FFmpeg is available."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "FFmpeg was not found on this system. "
            "Please install FFmpeg before generating a Reel."
        )


def check_input_image(input_file: str | Path) -> Path:
    """Validate that the source image exists."""
    path = Path(input_file)

    if not path.exists():
        raise FileNotFoundError(
            f"Source image was not found: {path}"
        )

    if not path.is_file():
        raise RuntimeError(
            f"Source image path is not a file: {path}"
        )

    return path


def generate_reel(
    input_file: str | Path = DEFAULT_INPUT,
    output_file: str | Path = DEFAULT_OUTPUT,
    duration: int = DURATION,
) -> Path:
    """
    Create a vertical educational Reel from a single image.

    The image receives a subtle continuous zoom using FFmpeg's
    zoompan filter. The output is H.264 MP4 suitable for later
    Instagram Reel publishing.
    """

    if duration < 3:
        raise ValueError("Reel duration must be at least 3 seconds.")

    if duration > 60:
        raise ValueError("Reel duration must not exceed 60 seconds.")

    check_ffmpeg()
    source = check_input_image(input_file)
    output = Path(output_file)

    output.parent.mkdir(parents=True, exist_ok=True)

    total_frames = duration * FPS

    filter_complex = (
        f"scale={WIDTH}:{HEIGHT}:"
        f"force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"zoompan="
        f"z='min(zoom+0.0007,1.08)':"
        f"x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)':"
        f"d={total_frames}:"
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
        str(source),
        "-vf",
        filter_complex,
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
        str(output),
    ]

    print("==========================================")
    print("OROM PLAN1 REEL GENERATOR")
    print("==========================================")
    print(f"Source image : {source}")
    print(f"Output Reel  : {output}")
    print(f"Resolution   : {WIDTH}x{HEIGHT}")
    print(f"FPS          : {FPS}")
    print(f"Duration     : {duration} seconds")
    print("Audio        : None")
    print("Instagram    : Not connected")
    print("==========================================")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("FFmpeg output:")
        print(result.stdout)
        print(result.stderr)

        raise RuntimeError(
            f"FFmpeg failed with exit code {result.returncode}."
        )

    if not output.exists():
        raise RuntimeError(
            "FFmpeg reported success, but the Reel file was not created."
        )

    if output.stat().st_size < 10_000:
        raise RuntimeError(
            "The generated Reel file is unexpectedly small."
        )

    print()
    print("==========================================")
    print("REEL CREATED SUCCESSFULLY")
    print("==========================================")
    print(f"File: {output}")
    print(f"Size: {output.stat().st_size:,} bytes")
    print("==========================================")

    return output


if __name__ == "__main__":
    generate_reel()
