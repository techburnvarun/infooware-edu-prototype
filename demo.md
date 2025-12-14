# demo.md
# Infooware Edu Prototype Demo  
**PDF to Slides & Short Video Pipeline**

## Project Overview
This prototype automatically converts a single-chapter PDF (e.g., an article, lecture notes, or book chapter) into:

- A concise PowerPoint presentation (6–12 slides)
- A short animated explainer video (30–90 seconds) with narration, background music, and smooth transitions

All processing is done locally and offline — no internet or API keys required after setup.

## How the Pipeline Works (Step-by-Step)

1. **PDF Ingestion**  
   `pdf_ingester.py` uses pdfplumber to extract text while detecting headings (by font size, capitalization, and numbering). Content is grouped into logical sections (heading + paragraphs).

2. **Content Summarization**  
   `summarizer.py` ranks sections by importance, selects the top 6–12, and generates for each slide:  
   - A short title/headline (6–20 words)  
   - 1–2 supporting bullets  
   - A single speaker note sentence for narration  
   Uses lightweight NLTK-based extractive summarization — no hallucinations.

3. **Visual Selection**  
   `visual_selector.py` keyword-matches slide content against a local bundle of royalty-free icons (in `assets/icons/`). Falls back to a neutral placeholder if no match.

4. **Slide Assembly**  
   `slide_builder.py` creates a clean, consistent PowerPoint using python-pptx:  
   - White background, large title, readable bullets on the left  
   - Prominent illustrative icon/image on the right  
   - Exports individual slide images for video creation

5. **Video Generation**  
   `video_renderer.py` assembles the final MP4 with moviepy:  
   - Subtle Ken Burns zoom + pan on each slide  
   - Fade transitions  
   - Offline TTS narration (pyttsx3) from speaker notes  
   - Low-volume royalty-free background music (looped)

6. **CLI Execution**  
   `run_pipeline.py` orchestrates the full process with a simple command.

## How to Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run on the sample PDF
python run_pipeline.py --input examples/input/sample.pdf --outdir examples/output/ --num_slides 8