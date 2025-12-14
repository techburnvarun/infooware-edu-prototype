# run_pipeline.py

import argparse
import os
import shutil
from datetime import datetime

# Import modules from src/
from src.pdf_ingester import extract_sections
from src.summarizer import generate_slide_content
from src.visual_selector import select_visual_for_slide
from src.slide_builder import build_pptx
from src.video_renderer import render_video


def ensure_directories(outdir: str):
    """Create output directory structure if it doesn't exist."""
    os.makedirs(outdir, exist_ok=True)
    temp_frames = os.path.join(outdir, "frames")
    os.makedirs(temp_frames, exist_ok=True)
    return temp_frames


def main():
    parser = argparse.ArgumentParser(description="Convert a PDF chapter/article into slides and a short explainer video.")
    parser.add_argument("--input", required=True, help="Path to input PDF file")
    parser.add_argument("--outdir", default="output/", help="Directory to save slides.pptx and video.mp4")
    parser.add_argument("--num_slides", type=int, default=8, help="Target number of slides (6–12 recommended)")
    parser.add_argument("--video_duration", type=int, default=None, 
                        help="Total video duration in seconds (auto-calculated if not set)")
    
    args = parser.parse_args()

    pdf_path = args.input
    outdir = args.outdir
    target_slides = max(6, min(12, args.num_slides))  # Clamp between 6 and 12

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Input PDF not found: {pdf_path}")

    print(f"Starting pipeline for: {pdf_path}")
    print(f"Target slides: {target_slides}")
    print(f"Output directory: {outdir}")

    # Create output directories
    frames_dir = ensure_directories(outdir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slides_path = os.path.join(outdir, "slides.pptx")
    video_path = os.path.join(outdir, "video.mp4")

    print("\nStep 1: Extracting text and sections from PDF...")
    sections = extract_sections(pdf_path, max_sections=target_slides * 2)  # Extract more to select best
    print(f"   → Extracted {len(sections)} sections")

    print("\nStep 2: Selecting key points and generating slide content...")
    slide_data = generate_slide_content(sections, target_count=target_slides)
    print(f"   → Generated content for {len(slide_data)} slides")

    print("\nStep 3: Selecting visuals for each slide...")
    for i, slide in enumerate(slide_data):
        visual_path = select_visual_for_slide(slide["title"], slide["bullets"])
        slide["visual_path"] = visual_path
        print(f"   Slide {i+1}: {slide['title'][:50]:50} → {os.path.basename(visual_path)}")

    print("\nStep 4: Building PowerPoint presentation...")
    build_pptx(slide_data, slides_path, temp_frames_dir=frames_dir)
    print(f"   → Slides saved: {slides_path}")

    print("\nStep 5: Rendering explainer video...")
    render_video(
        pptx_path=slides_path,
        slide_data=slide_data,
        output_path=video_path,
        frames_dir=frames_dir,
        total_duration=args.video_duration
    )
    print(f"   → Video saved: {video_path}")

    # Optional: Clean up temporary frames (comment out if debugging)
    # shutil.rmtree(frames_dir)

    print("\nPipeline completed successfully!")
    print(f"Outputs:")
    print(f"   • Slides: {slides_path}")
    print(f"   • Video : {video_path}")


if __name__ == "__main__":
    main()