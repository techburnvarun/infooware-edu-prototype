# README.md
# Infooware Edu Prototype — PDF to Slides & Short Video

A fully offline Python pipeline that converts a single-chapter PDF (article, lecture notes, book chapter) into:

- A clean 6–12 slide PowerPoint presentation (.pptx)
- A 30–90 second animated explainer video (.mp4) with narration (TTS), subtle Ken Burns effects, transitions, and background music

Perfect for rapid educational content creation from existing documents.

## Features

- 100% offline (no API keys, no internet required after setup)
- Accurate text extraction with heading detection
- Extractive summarization (no hallucinations)
- Royalty-free icon selection based on keywords
- Professional slide layout via `python-pptx`
- Animated video with narration, music, and effects via `moviepy` + `pyttsx3`

