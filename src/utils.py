# src/utils.py

import os
import sys
from pathlib import Path
from datetime import datetime

# Simple colored logging
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_info(message: str):
    """Print info message in blue."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.BLUE}[{timestamp}] INFO: {message}{Colors.END}")

def log_success(message: str):
    """Print success message in green."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.GREEN}[{timestamp}] SUCCESS: {message}{Colors.END}")

def log_warning(message: str):
    """Print warning in yellow."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.YELLOW}[{timestamp}] WARNING: {message}{Colors.END}")

def log_error(message: str):
    """Print error in red."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.RED}[{timestamp}] ERROR: {message}{Colors.END}")
    sys.exit(1)

def ensure_dir(path: str):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)

def clean_text(text: str) -> str:

    if not text:
        return ""
    # Replace multiple whitespace/newlines with single space
    text = " ".join(text.split())
    # Remove common PDF artifacts
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")  # ligatures
    return text.strip()

def truncate_text(text: str, max_words: int = 15) -> str:
    """Truncate text to max_words and add ellipsis if needed."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."

def get_project_root() -> Path:
    """Return the project root directory (parent of src/)."""
    return Path(__file__).parent.parent

def resource_path(relative_path: str) -> str:
    
    return str(get_project_root() / relative_path)