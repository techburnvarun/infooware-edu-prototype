# src/__init__.py

from .pdf_ingester import extract_sections
from .summarizer import generate_slide_content
from .visual_selector import select_visual_for_slide, list_available_images
from .slide_builder import build_pptx
from .video_renderer import render_video
from .utils import (
    log_info,
    log_success,
    log_warning,
    log_error,
    ensure_dir,
    clean_text,
    truncate_text,
    resource_path,
)

__all__ = [
    "extract_sections",
    "generate_slide_content",
    "select_visual_for_slide",
    "list_available_images",
    "build_pptx",
    "render_video",
    "log_info",
    "log_success",
    "log_warning",
    "log_error",
    "ensure_dir",
    "clean_text",
    "truncate_text",
    "resource_path",
]

__version__ = "0.1.0"