# config.py

import os
from pathlib import Path

# Project root (for consistent path resolution)
PROJECT_ROOT = Path(__file__).parent.resolve()

# Output settings
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "examples" / "output"
DEFAULT_NUM_SLIDES = 8
MIN_SLIDES = 6
MAX_SLIDES = 12

# PDF ingestion
MAX_SECTIONS_TO_EXTRACT = 30  # Before selection in summarizer

# Summarization
TARGET_TITLE_WORDS = (6, 20)      # Min/max words for slide title
MAX_BULLETS_PER_SLIDE = 2
MAX_BULLET_WORDS = 20
DEFAULT_TTS_RATE = 150           # Words per minute for pyttsx3

# Slide layout (dimensions in inches)
SLIDE_WIDTH = 13.33              # 16:9 aspect ratio
SLIDE_HEIGHT = 7.5
TITLE_FONT_SIZE = 36
BULLET_FONT_SIZE = 24
IMAGE_MAX_WIDTH = 5.5
IMAGE_MAX_HEIGHT = 5.0

# Video rendering
DEFAULT_SLIDE_DURATION = 8       # Seconds per slide if no total duration set
MIN_TOTAL_VIDEO_DURATION = 30
MAX_TOTAL_VIDEO_DURATION = 90
VIDEO_FPS = 30
BACKGROUND_MUSIC_VOLUME = 0.15   # 0.0 to 1.0
KEN_BURNS_ZOOM_FACTOR = 0.2      # Additional zoom (e.g., 1.0 → 1.2)

# Asset paths (resolved via PROJECT_ROOT)
ASSETS_ROOT = PROJECT_ROOT / "assets"
ICONS_ROOT = ASSETS_ROOT / "icons"
MUSIC_ROOT = ASSETS_ROOT / "music"
DEFAULT_MUSIC_FILE = MUSIC_ROOT / "background_loop1.mp3"
PLACEHOLDER_ICON = ICONS_ROOT / "general" / "placeholder.png"

# Temporary directories (relative to output dir)
TEMP_FRAMES_SUBDIR = "frames"
TEMP_NARRATION_SUBDIR = "narration"

# Logging
LOG_TIMESTAMPS = True

# Environment variable overrides (optional advanced usage)
def get_env_int(var_name: str, default: int) -> int:
    """Helper to get integer from environment with fallback."""
    try:
        return int(os.getenv(var_name, str(default)))
    except (TypeError, ValueError):
        return default

def get_env_float(var_name: str, default: float) -> float:
    """Helper to get float from environment with fallback."""
    try:
        return float(os.getenv(var_name, str(default)))
    except (TypeError, ValueError):
        return default

# Allow overrides via environment variables
DEFAULT_NUM_SLIDES = get_env_int("EDU_NUM_SLIDES", DEFAULT_NUM_SLIDES)
DEFAULT_SLIDE_DURATION = get_env_int("EDU_SLIDE_DURATION", DEFAULT_SLIDE_DURATION)
BACKGROUND_MUSIC_VOLUME = get_env_float("EDU_MUSIC_VOLUME", BACKGROUND_MUSIC_VOLUME)
DEFAULT_TTS_RATE = get_env_int("EDU_TTS_RATE", DEFAULT_TTS_RATE)