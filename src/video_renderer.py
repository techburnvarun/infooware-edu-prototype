# src/video_renderer.py

import os
from pathlib import Path
from typing import List, Dict
import pyttsx3
import numpy as np
from PIL import Image

from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_videoclips,
)
from moviepy.audio.AudioClip import concatenate_audioclips, AudioClip
from moviepy.video.fx.all import fadein, fadeout

# Constants
DEFAULT_SLIDE_DURATION = 8  # seconds per slide if no total duration specified
MIN_TOTAL_DURATION = 30
MAX_TOTAL_DURATION = 90
BACKGROUND_MUSIC_VOLUME = 0.15  # 15% volume
TTS_RATE = 150  # words per minute (adjust for natural pace)
TARGET_RESOLUTION = (1920, 1080)  # HD output


def _generate_narration_audio(slide_data: List[Dict], audio_dir: str) -> List[str]:
    """Generate individual TTS audio files for each slide's speaker note."""
    os.makedirs(audio_dir, exist_ok=True)
    audio_paths = []

    engine = pyttsx3.init()
    engine.setProperty("rate", TTS_RATE)
    voices = engine.getProperty("voices")
    if voices:
        engine.setProperty("voice", voices[0].id)

    print("   Generating TTS narration...")
    for i, slide in enumerate(slide_data):
        text = slide["speaker_note"].strip() or slide["title"]
        audio_path = os.path.join(audio_dir, f"narration_{i+1:03d}.wav")
        engine.save_to_file(text, audio_path)
        audio_paths.append(audio_path)

    engine.runAndWait()
    print(f"   Saved {len(audio_paths)} narration clips")
    return audio_paths


def _apply_ken_burns_optimized(img_path: str, duration: float, target_size=TARGET_RESOLUTION) -> ImageClip:
    """
    Optimized Ken Burns: precompute image at target resolution and apply slow zoom.
    """
    # Load and resize image to target resolution preserving aspect ratio
    img = Image.open(img_path)
    img.thumbnail(target_size, Image.Resampling.LANCZOS)
    img_clip = ImageClip(np.array(img)).set_duration(duration)

    # Apply subtle zoom using MoviePy resize
    #zoom_factor = 1.15  # 15% zoom over duration
    zoom_factor = 1.08
    return img_clip.resize(lambda t: 1 + (zoom_factor - 1) * (t / duration))


def render_video(
    pptx_path: str,
    slide_data: List[Dict],
    output_path: str,
    frames_dir: str,
    total_duration: int = None,
):
    """
    Render the final explainer video.
    """
    if not slide_data:
        raise ValueError("No slide data for video rendering.")

    num_slides = len(slide_data)
    frame_files = sorted(
        [f for f in os.listdir(frames_dir) if f.startswith("slide_") and f.endswith(".png")]
    )

    if len(frame_files) != num_slides:
        raise FileNotFoundError(
            f"Expected {num_slides} frame images in {frames_dir}, found {len(frame_files)}"
        )

    frame_paths = [os.path.join(frames_dir, f) for f in frame_files]

    # Determine per-slide duration
    if total_duration is not None:
        total_duration = max(MIN_TOTAL_DURATION, min(MAX_TOTAL_DURATION, total_duration))
        per_slide_duration = total_duration / num_slides
    else:
        per_slide_duration = DEFAULT_SLIDE_DURATION
        total_duration = int(per_slide_duration * num_slides)

    print(f"   Rendering video: {num_slides} slides → ~{total_duration}s total")
    print(f"   Per-slide duration: {per_slide_duration:.1f}s")

    # Generate TTS narration
    temp_audio_dir = os.path.join(frames_dir, "narration")
    narration_paths = _generate_narration_audio(slide_data, temp_audio_dir)

    # Load background music
    music_path = Path(__file__).parent.parent / "assets" / "music" / "background_loop1.mp3"
    background_music = None
    if music_path.exists():
        background_music = AudioFileClip(str(music_path)).volumex(BACKGROUND_MUSIC_VOLUME)
        # Loop to match total duration
        if background_music.duration < total_duration:
            loops_needed = int(np.ceil(total_duration / background_music.duration))
            background_music = concatenate_audioclips([background_music] * loops_needed)
        background_music = background_music.subclip(0, total_duration)
        print(f"   Added background music ({music_path.name})")
    else:
        print("   Warning: No background music found. Add to assets/music/")

    # Create video clips
    clips = []
    for img_path, narr_path in zip(frame_paths, narration_paths):
        img_clip = _apply_ken_burns_optimized(img_path, per_slide_duration)

        # Attach narration
        if os.path.exists(narr_path):
            narr_clip = AudioFileClip(narr_path)
            if narr_clip.duration > per_slide_duration:
                narr_clip = narr_clip.subclip(0, per_slide_duration).audio_fadeout(0.5)
            else:
                silence = AudioClip(lambda t: 0, duration=per_slide_duration - narr_clip.duration, fps=44100)
                narr_clip = concatenate_audioclips([narr_clip, silence])
            img_clip = img_clip.set_audio(narr_clip)

        # Fade in/out transitions
        img_clip = fadein(img_clip, 0.4)
        img_clip = fadeout(img_clip, 0.4)

        clips.append(img_clip)

    # Concatenate all slides
    final_video = concatenate_videoclips(clips, method="compose")

    # Add background music
    if background_music:
        final_audio = CompositeAudioClip([final_video.audio, background_music])
        final_video = final_video.set_audio(final_audio)

    # Write output (WITH progress bar & faster encoding)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_video.write_videofile(
        output_path,
        fps=15,                 # ↓ lower FPS = much faster
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",     # ↓ fastest FFmpeg preset
        verbose=True,
        logger="bar",           # ✅ THIS enables the progress bar
    )
