# src/summarizer.py
"""
Content Summarization Module
"""


import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from typing import List, Dict
import re
import heapq

# Download required NLTK data once (will be noted in README)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)


def _clean_text(text: str) -> str:
    """Basic cleaning: remove extra whitespace, newlines, and artifacts."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _score_sentences(sentences: List[str]) -> List[tuple]:
    if not sentences:
        return []

    # Build word frequency (ignore common stop words)
    stop_words = set([
        'the', 'a', 'an', 'and', 'or', 'but', 'if', 'while', 'at', 'by', 'for', 'with',
        'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
        'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
        'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
        'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
    ])

    word_freq = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word.isalnum() and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

    # Score sentences
    scored = []
    for sentence in sentences:
        score = 0
        words = word_tokenize(sentence.lower())
        for word in words:
            if word in word_freq:
                score += word_freq[word]
        if len(words) > 0:
            score /= len(words)  # Normalize by length
        scored.append((score, sentence))

    return scored


def _select_top_sentences(scored: List[tuple], max_sentences: int = 3) -> List[str]:
    """Select top sentences by score."""
    scored.sort(reverse=True)
    return [sent for _, sent in scored[:max_sentences]]


def generate_slide_content(sections: List[Dict], target_count: int = 8) -> List[Dict]:
    
    if not sections:
        raise ValueError("No sections provided for summarization.")

    target_count = max(6, min(12, target_count))
    print(f"   Targeting {target_count} slides")

    # Step 1: Rank sections by importance
    # Priority: longer content + meaningful heading
    ranked_sections = []
    for sec in sections:
        heading = sec["heading"]
        content = _clean_text(sec["content"])
        content_length = len(content.split())
        heading_length = len(heading.split())

        # Score: content length + bonus for good heading
        score = content_length
        if heading_length > 2 and heading_length < 20:
            score += 50
        if not heading.lower().startswith(("section", "untitled", "page")):
            score += 30

        ranked_sections.append((score, sec))

    #ranked_sections.sort(reverse=True)
    ranked_sections.sort(key=lambda x: x[0], reverse=True)


    # Step 2: Select top sections
    selected_sections = [sec for _, sec in ranked_sections[:target_count * 2]]  # Oversample
    selected_sections = selected_sections[:target_count]  # Final cut

    if len(selected_sections) < target_count:
        print(f"   Warning: Only {len(selected_sections)} suitable sections found. Using all.")

    slide_data = []

    for idx, sec in enumerate(selected_sections):
        heading = sec["heading"]
        raw_content = _clean_text(sec["content"])
        sentences = sent_tokenize(raw_content)

        # Generate title: prefer heading, fallback to first strong sentence
        if len(heading.split()) >= 6 and len(heading.split()) <= 20:
            title = heading
        else:
            # Use first 1–2 sentences or top scored
            if sentences:
                scored = _score_sentences(sentences)
                candidate = _select_top_sentences(scored, 1)[0]
                title_words = candidate.split()[:15]
                title = " ".join(title_words)
                if not title.endswith(('.', '!', '?')):
                    title += "."
            else:
                title = f"Key Concept {idx + 1}"

        # Capitalize title properly
        title = title.strip(". ").capitalize()
        if not title.endswith(('.', '?', '!')):
            title += "."

        # Generate bullets: 1–2 key sentences
        if len(sentences) >= 2:
            scored = _score_sentences(sentences)
            top_sents = _select_top_sentences(scored, 4)
            bullets = []
            for sent in top_sents:
                sent = sent.strip()
                if len(sent.split()) <= 20 and len(bullets) < 2:
                    if not sent.lower().startswith("figure") and not "table" in sent.lower():
                        bullets.append("• " + sent[0].capitalize() + sent[1:])
            if len(bullets) < 1 and sentences:
                first_sent = sentences[0].strip()
                if len(first_sent.split()) <= 25:
                    bullets = ["• " + first_sent[0].capitalize() + first_sent[1:]]
        else:
            bullets = ["• " + raw_content[:100] + "..." if len(raw_content) > 100 else "• " + raw_content]

        # Speaker note: simple rephrasing of title + first bullet
        speaker_note = title[:-1]  # Remove period
        if bullets:
            first_bullet = bullets[0][2:]  # Remove • 
            speaker_note += ", which means " + first_bullet.lower().rstrip(".") + "."

        slide_data.append({
            "title": title,
            "bullets": bullets,
            "speaker_note": speaker_note,
            "source_section": sec  # Keep for debugging/visual selection
        })

    print(f"   Generated {len(slide_data)} slides with titles, bullets, and narration")
    return slide_data