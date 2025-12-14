# src/pdf_ingester.py

import pdfplumber
from typing import List, Dict, Optional
import re

# Simple heuristic to detect headings: short lines, bold (if detectable), all caps, or larger font
def _is_likely_heading(text: str, font_size: float, avg_font_size: float) -> bool:
    stripped = text.strip()
    if len(stripped) == 0:
        return False
    if len(stripped.split()) > 15:  # Too long for a heading
        return False
    if font_size > avg_font_size * 1.1:  # Larger font
        return True
    if stripped.isupper():  # ALL CAPS
        return True
    # Common heading patterns (e.g., "1. Introduction", "Chapter 2")
    if re.match(r"^\d+\.?\s*\d*\s*", stripped):
        return True
    return False


def extract_sections(pdf_path: str, max_sections: int = 20) -> List[Dict]:
    """
    Extract structured sections from a PDF.
    """
    sections: List[Dict] = []
    current_heading: Optional[str] = None
    current_content: List[str] = []
    current_page: int = 1

    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        print(f"   PDF loaded: {page_count} pages")

        # First pass: estimate average font size per page for heading detection
        font_sizes = []
        for page in pdf.pages:
            if page.objects.get("char"):
                for char in page.chars:
                    font_sizes.append(char["size"])
        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 11.0

        # Second pass: extract text with layout awareness
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text_blocks = []
            chars = page.chars

            # Group characters into lines based on y-coordinate (top)
            lines = {}
            for char in chars:
                top = round(char["top"], 1)  # Tolerance for alignment
                if top not in lines:
                    lines[top] = []
                lines[top].append(char)

            # Sort lines from top to bottom
            sorted_tops = sorted(lines.keys())
            for top in sorted_tops:
                line_chars = sorted(lines[top], key=lambda c: c["x0"])
                line_text = "".join(c["text"] for c in line_chars).strip()
                if line_text:
                    # Average font size for this line
                    line_font_size = sum(c["size"] for c in line_chars) / len(line_chars)
                    page_text_blocks.append({
                        "text": line_text,
                        "font_size": line_font_size,
                        "page": page_num
                    })

            # Process blocks on this page
            for block in page_text_blocks:
                text = block["text"]
                font_size = block["font_size"]

                if _is_likely_heading(text, font_size, avg_font_size):
                    # Save previous section if exists
                    if current_heading is not None and (current_content or len(sections) == 0):
                        sections.append({
                            "heading": current_heading.strip(),
                            "content": "\n".join(current_content).strip(),
                            "page_start": current_page
                        })

                    # Start new section
                    current_heading = text
                    current_content = []
                    current_page = page_num

                else:
                    # Add to current content
                    if text:
                        current_content.append(text)

        # Don't forget the last section
        if current_heading is not None:
            sections.append({
                "heading": current_heading.strip(),
                "content": "\n".join(current_content).strip(),
                "page_start": current_page
            })

    # Fallback: if no headings detected, split by page or paragraph
    if not sections:
        print("   Warning: No headings detected. Falling back to page-based sections.")
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    full_text += f"\n\n--- Page {page_num} ---\n\n" + text

            # Split into rough paragraphs
            paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
            chunk_size = max(3, len(paragraphs) // 10)
            for i in range(0, len(paragraphs), chunk_size):
                chunk = "\n\n".join(paragraphs[i:i + chunk_size])
                sections.append({
                    "heading": f"Section {len(sections) + 1}",
                    "content": chunk,
                    "page_start": 1
                })

    # Limit to max_sections and clean up empty ones
    sections = [s for s in sections if s["content"].strip()]
    sections = sections[:max_sections]

    # Final cleanup: ensure headings are reasonable
    for s in sections:
        if not s["heading"] or s["heading"].lower().startswith("page"):
            s["heading"] = " ".join(s["content"].split()[:8]) + "..." if s["content"] else "Untitled Section"

    print(f"   Extracted {len(sections)} clean sections")
    return sections