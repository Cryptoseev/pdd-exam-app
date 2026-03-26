#!/usr/bin/env python3
"""
PDF Image Extractor for PDD Exam App
Extracts images from the PDD PDF and maps them to questions.

Usage:
  python3 scripts/extract-images.py [path-to-pdf]

Default PDF path: ~/Downloads/bileti-pdd-abm-pddmaster.ru-10.0.pdf
"""

import subprocess
import json
import re
import os
import shutil
import sys
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
PDF_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads/bileti-pdd-abm-pddmaster.ru-10.0.pdf"
EXTRACTED_DIR = Path("/tmp/pdd_extraction")
PUBLIC_IMAGES_DIR = PROJECT_DIR / "public/images/questions"
QUESTIONS_JSON = PROJECT_DIR / "data/questions.json"
IMAGE_MAP_OUT = PROJECT_DIR / "data/questionImageMap.json"

# PDF structure: ticket N starts at PDF page (4 + (N-1)*10), spans 10 pages
TICKET_COUNT = 40
QUESTIONS_PER_TICKET = 20
FIRST_TICKET_PAGE = 4   # PDF page where ticket 1 starts
PAGES_PER_TICKET = 10

# pdfimages: question images (480×180 JPEGs) start at extracted index 6
FIRST_QUESTION_IMG_IDX = 6

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_for_page(pdf_path: Path, page: int) -> str:
    """Return layout text of a single PDF page (1-indexed)."""
    result = subprocess.run(
        ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf_path), "-"],
        capture_output=True, text=True
    )
    return result.stdout


def questions_with_images_on_page(page_text: str) -> list[int]:
    """
    Returns list of question numbers (1-20) that have an image on this page.
    Heuristic: a question has an image when there are ≥2 blank lines between
    'Вопрос №N' and the actual question text.
    """
    questions = []
    # Split into question blocks
    blocks = re.split(r'Вопрос №(\d+)', page_text)
    # blocks[0] = text before first question
    # blocks[1] = question number, blocks[2] = text after that number
    # blocks[3] = next question number, etc.
    i = 1
    while i < len(blocks) - 1:
        q_num = int(blocks[i])
        q_body = blocks[i + 1]
        # Count blank lines at start of body (before non-empty line)
        lines = q_body.split('\n')
        blank_count = 0
        for line in lines:
            if line.strip() == '':
                blank_count += 1
            else:
                break
        if blank_count >= 2:
            questions.append(q_num)
        i += 2
    return questions


def build_question_image_map(pdf_path: Path) -> dict[str, int]:
    """
    Returns mapping: question_id → extracted image index (0-based from pdfimages).
    Example: {"1-2": 6, "1-3": 7, ...}
    """
    mapping = {}
    img_idx = FIRST_QUESTION_IMG_IDX  # images 0-5 are non-question images

    for ticket_num in range(1, TICKET_COUNT + 1):
        ticket_start_page = FIRST_TICKET_PAGE + (ticket_num - 1) * PAGES_PER_TICKET
        ticket_end_page = ticket_start_page + PAGES_PER_TICKET - 1

        # collect all q-with-image for this ticket across its pages
        ticket_img_questions = []

        for pdf_page in range(ticket_start_page, ticket_end_page + 1):
            page_text = extract_text_for_page(pdf_path, pdf_page)
            qs = questions_with_images_on_page(page_text)
            for q in qs:
                if q not in ticket_img_questions:
                    ticket_img_questions.append(q)

        ticket_img_questions.sort()

        for q_num in ticket_img_questions:
            question_id = f"{ticket_num}-{q_num}"
            mapping[question_id] = img_idx
            img_idx += 1

        print(f"  Ticket {ticket_num:2d}: {len(ticket_img_questions)} images "
              f"(Q{ticket_img_questions[0] if ticket_img_questions else '-'}"
              f"–Q{ticket_img_questions[-1] if ticket_img_questions else '-'})"
              f"  img_idx now {img_idx}")

    return mapping


def copy_images_to_public(mapping: dict[str, int], extracted_dir: Path, out_dir: Path):
    """
    Copy extracted images to public/images/questions/<question_id>.jpg
    Returns set of question_ids that were successfully copied.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    copied = set()
    missing = []

    for question_id, img_idx in mapping.items():
        src = extracted_dir / f"imgs-{img_idx:03d}.jpg"
        dst = out_dir / f"{question_id}.jpg"
        if src.exists():
            shutil.copy2(src, dst)
            copied.add(question_id)
        else:
            missing.append((question_id, str(src)))

    if missing:
        print(f"\n⚠️  {len(missing)} images not found:")
        for qid, path in missing[:10]:
            print(f"   {qid} → {path}")
        if len(missing) > 10:
            print(f"   ... and {len(missing)-10} more")

    return copied


def update_questions_json(questions_json_path: Path, copied_ids: set[str], image_map: dict):
    """Add image field to questions that have images in questions.json."""
    with open(questions_json_path) as f:
        data = json.load(f)

    updated_count = 0
    for ticket in data["tickets"]:
        for question in ticket["questions"]:
            qid = question["id"]
            if qid in copied_ids:
                question["image"] = f"/images/questions/{qid}.jpg"
                updated_count += 1
            elif "image" in question:
                # Remove stale image ref if image no longer present
                del question["image"]

    with open(questions_json_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Updated {updated_count} questions with image paths in questions.json")
    return updated_count


def save_image_map(mapping: dict, out_path: Path, copied_ids: set):
    """
    Save questionImageMap.json with full mapping including confidence.
    Format: { "1-2": { "imgIndex": 6, "imgFile": "imgs-006.jpg", "status": "auto" } }
    """
    output = {}
    for qid, img_idx in mapping.items():
        output[qid] = {
            "imgIndex": img_idx,
            "imgFile": f"imgs-{img_idx:03d}.jpg",
            "publicPath": f"/images/questions/{qid}.jpg",
            "status": "auto" if qid in copied_ids else "missing"
        }
    with open(out_path, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved image map → {out_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"PDF: {PDF_PATH}")
    print(f"Extracted images dir: {EXTRACTED_DIR}")
    print(f"Output: {PUBLIC_IMAGES_DIR}")
    print()

    if not PDF_PATH.exists():
        print(f"❌ PDF not found: {PDF_PATH}")
        sys.exit(1)

    # Check tools
    for tool in ["pdftotext", "pdfimages"]:
        if not shutil.which(tool):
            print(f"❌ {tool} not found. Install poppler: brew install poppler")
            sys.exit(1)

    # Check that images were already extracted to EXTRACTED_DIR
    sample = EXTRACTED_DIR / "imgs-006.jpg"
    if not sample.exists():
        print(f"ℹ️  Extracting images from PDF (this may take a moment)...")
        EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["pdfimages", "-j", str(PDF_PATH), str(EXTRACTED_DIR / "imgs")],
            check=True
        )
        print(f"   Done.")
    else:
        print(f"ℹ️  Using already-extracted images in {EXTRACTED_DIR}")

    # Verify image count
    imgs = sorted(EXTRACTED_DIR.glob("imgs-*.jpg"))
    print(f"   Found {len(imgs)} JPEG images in extraction dir\n")

    # Build mapping
    print("Building question → image mapping...")
    mapping = build_question_image_map(PDF_PATH)
    print(f"\nTotal mapped: {len(mapping)} question images\n")

    # Copy to public
    print("Copying images to public/images/questions/...")
    copied = copy_images_to_public(mapping, EXTRACTED_DIR, PUBLIC_IMAGES_DIR)
    print(f"   Copied {len(copied)} images")

    # Update questions.json
    update_questions_json(QUESTIONS_JSON, copied, mapping)

    # Save image map
    save_image_map(mapping, IMAGE_MAP_OUT, copied)

    print("\n🎉 Done! Summary:")
    print(f"   Images copied: {len(copied)}")
    print(f"   questions.json updated with image paths")
    print(f"   Full mapping: {IMAGE_MAP_OUT}")
    print(f"\nImages missing or needing manual review:")
    missing = [qid for qid in mapping if qid not in copied]
    if missing:
        print(f"   {missing}")
        print(f"   → Edit data/questionImageMap.json to fix these manually")
    else:
        print("   None — all images mapped successfully!")


if __name__ == "__main__":
    main()
