# src/visual_selector.py

import os
from typing import List, Dict
import re
from pathlib import Path

# Define keyword-to-image mapping (case-insensitive)
# Format: {keyword: (category_folder, filename)}
KEYWORD_MAP = {
    # Technology
    "ai": ("technology", "ai.png"),
    "artificial intelligence": ("technology", "ai.png"),
    "machine learning": ("technology", "ai.png"),
    "computer": ("technology", "computer.png"),
    "network": ("technology", "network.png"),
    "cloud": ("technology", "cloud.png"),
    "data": ("technology", "network.png"),
    "algorithm": ("technology", "gears.png"),
    "code": ("technology", "computer.png"),
    "programming": ("technology", "computer.png"),

    # Science
    "science": ("science", "microscope.png"),
    "atom": ("science", "atom.png"),
    "physics": ("science", "atom.png"),
    "chemistry": ("science", "atom.png"),
    "biology": ("science", "dna.png"),
    "dna": ("science", "dna.png"),
    "cell": ("science", "dna.png"),
    "experiment": ("science", "microscope.png"),

    # General concepts
    "idea": ("general", "lightbulb.png"),
    "innovation": ("general", "lightbulb.png"),
    "concept": ("general", "lightbulb.png"),
    "introduction": ("general", "lightbulb.png"),
    "overview": ("general", "lightbulb.png"),
    "summary": ("general", "lightbulb.png"),
    "conclusion": ("general", "lightbulb.png"),
    "process": ("general", "gears.png"),
    "system": ("general", "gears.png"),
    "method": ("general", "gears.png"),
    "application": ("general", "gears.png"),
    "benefit": ("general", "lightbulb.png"),
    "challenge": ("general", "question_mark.png"),
    "future": ("general", "lightbulb.png"),
}

# Base directory for assets
ASSETS_ROOT = Path(__file__).parent.parent / "assets" / "icons"
PLACEHOLDER_IMAGE = ASSETS_ROOT / "general" / "placeholder.png"


def _extract_keywords(text: str) -> List[str]:
    """Extract lowercase keywords from title + bullets."""
    text = text.lower()
    # Remove common punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    words = text.split()
    # Return unique words longer than 3 chars
    return list(set(w for w in words if len(w) > 3))


def _find_best_match(keywords: List[str]) -> tuple:
    """
    Find the best matching image from KEYWORD_MAP.
    Returns (category, filename) or None.
    """
    # Direct full-phrase match first
    full_text = " ".join(keywords)
    for phrase, (cat, file) in KEYWORD_MAP.items():
        if phrase in full_text:
            return cat, file

    # Single keyword match
    for kw in keywords:
        if kw in KEYWORD_MAP:
            return KEYWORD_MAP[kw]

    return None


def select_visual_for_slide(title: str, bullets: List[str]) -> str:
    
    # Combine all text for keyword extraction
    all_text = title + " " + " ".join(bullets)

    keywords = _extract_keywords(all_text)

    match = _find_best_match(keywords)

    if match:
        category, filename = match
        image_path = ASSETS_ROOT / category / filename
        if image_path.exists():
            return str(image_path)

    # Fallback to generic placeholder
    if PLACEHOLDER_IMAGE.exists():
        return str(PLACEHOLDER_IMAGE)
    else:
        # Ultimate fallback: return empty string (slide builder will skip image)
        return ""


# Optional: Helper to list all available images (for debugging or extending)
def list_available_images() -> List[str]:
    """Return list of all bundled image paths."""
    if not ASSETS_ROOT.exists():
        return []
    return [str(p) for p in ASSETS_ROOT.rglob("*.png")] + [str(p) for p in ASSETS_ROOT.rglob("*.jpg")] + [str(p) for p in ASSETS_ROOT.rglob("*.svg")]