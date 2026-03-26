#!/usr/bin/env python3
"""
Parse questions from the actual PDD PDF and regenerate questions.json.
Also rebuilds questionImageMap.json with correct mappings.

Usage: python3 scripts/parse-pdf-questions.py [path-to-pdf]
"""

import subprocess
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
PDF_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path.home() / "Downloads/bileti-pdd-abm-pddmaster.ru-10.0.pdf"
QUESTIONS_JSON = PROJECT_DIR / "data/questions.json"
IMAGE_MAP_OUT = PROJECT_DIR / "data/questionImageMap.json"

TICKET_COUNT = 40
QUESTIONS_PER_TICKET = 20
FIRST_TICKET_PAGE = 4
PAGES_PER_TICKET = 10
FIRST_QUESTION_IMG_IDX = 6

# Answer table from PDF page 404 (1-indexed, convert to 0-indexed)
# fmt: off
ANSWER_TABLE = {
    1:  [2,1,1,4,2,2,4,3,1,3,1,3,3,1,3,4,3,4,3,2],
    2:  [2,1,1,3,3,1,3,3,1,3,3,2,3,3,1,3,2,1,3,3],
    3:  [1,3,3,2,2,3,2,1,3,1,3,2,2,1,3,3,4,2,3,3],
    4:  [2,2,1,1,2,1,1,2,2,1,1,2,3,3,2,4,1,4,1,2],
    5:  [1,2,1,1,3,1,3,3,2,3,1,2,2,1,1,3,2,1,2,1],
    6:  [3,2,3,3,2,1,1,2,3,3,1,3,3,2,2,3,3,4,1,2],
    7:  [1,2,1,2,2,2,1,3,2,2,1,3,2,2,3,3,3,3,2,2],
    8:  [2,3,3,1,1,3,1,2,3,3,2,1,1,2,2,3,2,1,1,2],
    9:  [2,2,1,3,1,2,2,1,3,2,3,3,2,2,3,3,4,3,2,2],
    10: [2,1,3,3,2,1,1,2,1,3,2,2,3,3,3,3,2,4,3,1],
    11: [2,1,3,2,3,3,1,1,2,3,3,1,1,2,1,2,3,2,3,2],
    12: [2,3,2,1,2,3,2,1,3,2,2,3,2,3,3,3,2,2,1,3],
    13: [3,2,3,2,3,1,1,3,2,3,3,3,1,3,2,2,1,2,3,2],
    14: [1,2,2,3,2,1,1,3,1,2,1,1,3,3,2,2,1,3,1,3],
    15: [4,2,3,3,4,1,1,3,1,2,3,1,3,2,1,2,4,3,2,2],
    16: [4,2,2,2,3,2,3,2,3,2,1,1,2,1,3,2,3,2,1,2],
    17: [1,1,2,2,3,1,2,3,2,2,3,2,1,1,2,4,3,2,3,1],
    18: [1,3,1,2,2,2,3,2,2,3,3,2,3,3,2,3,2,2,3,3],
    19: [2,3,1,3,2,2,3,1,1,3,3,3,2,1,3,1,2,3,1,3],
    20: [4,1,3,2,2,3,1,3,2,2,3,1,3,2,3,1,2,1,2,2],
    21: [2,3,1,3,3,3,1,3,2,3,2,3,3,3,2,4,3,2,1,2],
    22: [1,2,2,3,2,3,1,2,3,4,2,1,1,3,2,3,2,2,3,1],
    23: [2,1,2,2,3,2,1,1,3,3,3,3,2,2,2,1,3,2,3,3],
    24: [3,2,1,2,2,2,2,3,2,3,3,2,1,3,3,2,1,2,2,3],
    25: [1,3,1,2,4,2,1,2,3,3,3,3,1,3,2,3,2,4,3,1],
    26: [3,2,2,1,2,2,1,2,3,2,3,2,2,3,2,2,1,3,2,2],
    27: [2,1,1,3,3,3,2,1,1,2,2,3,3,2,2,2,2,3,1,3],
    28: [1,1,3,3,1,3,3,2,1,2,1,3,3,1,1,1,2,2,4,4],
    29: [3,2,1,3,1,2,1,1,2,3,3,4,3,1,3,2,4,3,2,3],
    30: [1,2,2,2,3,2,3,1,3,2,3,3,3,2,4,3,1,3,1,2],
    31: [4,1,1,2,4,2,1,1,3,2,1,1,1,2,4,3,2,3,3,2],
    32: [2,2,1,4,3,3,1,3,4,4,3,1,3,2,3,3,2,3,1,1],
    33: [2,1,3,2,3,1,3,1,4,4,3,3,4,2,3,1,2,3,2,3],
    34: [3,2,2,2,1,3,1,2,3,2,3,3,1,2,1,2,3,3,2,3],
    35: [3,3,2,3,1,2,3,2,3,1,2,3,3,2,2,1,1,3,3,2],
    36: [1,2,1,3,3,2,1,3,1,3,2,2,3,3,2,3,3,2,3,1],
    37: [2,3,2,3,1,1,3,1,3,3,1,3,2,3,2,3,3,2,3,2],
    38: [2,2,2,3,1,3,2,4,2,1,2,2,3,3,2,1,3,3,2,2],
    39: [3,2,2,4,3,3,3,1,2,3,1,3,3,1,2,2,2,3,2,1],
    40: [1,1,3,1,2,3,1,3,1,3,1,1,4,2,3,3,1,4,1,3],
}
# fmt: on


def get_page_text(pdf_path: Path, page: int) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf_path), "-"],
        capture_output=True, text=True
    )
    return result.stdout


def has_image_before_question(text_before_answer_start: str) -> bool:
    """Check if there are 2+ blank lines before the question text (indicating image)."""
    lines = text_before_answer_start.split('\n')
    blank_count = 0
    for line in lines:
        if line.strip() == '':
            blank_count += 1
        else:
            break
    return blank_count >= 2


def clean_text(text: str) -> str:
    """Clean extracted text: collapse whitespace, remove artifacts."""
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove page footer patterns
    text = re.sub(r'\s+\d+\s*$', '', text, flags=re.MULTILINE)
    # Collapse multiple spaces
    text = re.sub(r'  +', ' ', text)
    # Strip lines
    lines = [l.strip() for l in text.split('\n')]
    # Remove empty trailing lines but keep structure
    return '\n'.join(lines)


def parse_ticket_page_range(pdf_path: Path, ticket_num: int) -> dict:
    """Parse all questions from a ticket's page range."""
    start_page = FIRST_TICKET_PAGE + (ticket_num - 1) * PAGES_PER_TICKET
    end_page = start_page + PAGES_PER_TICKET - 1

    # Extract all pages for this ticket as one text block
    full_text = ""
    for p in range(start_page, end_page + 1):
        page_text = get_page_text(pdf_path, p)
        full_text += page_text + "\n"

    full_text = clean_text(full_text)

    # Split into question blocks
    question_blocks = re.split(r'Вопрос №(\d+)', full_text)
    # question_blocks[0] = text before Q1 (ticket header)
    # question_blocks[1], question_blocks[2] = "1", text-of-Q1
    # etc.

    questions = {}
    i = 1
    while i < len(question_blocks) - 1:
        q_num = int(question_blocks[i])
        q_body = question_blocks[i + 1]
        questions[q_num] = q_body
        i += 2

    return questions


def parse_question_body(q_body: str, ticket_num: int, q_num: int, correct_answer_1based: int):
    """
    Parse a question body text into structured question data.
    Returns a question dict.
    """
    # Detect image: blank lines at the start
    lines = q_body.split('\n')
    blank_count = 0
    for line in lines:
        if line.strip() == '':
            blank_count += 1
        else:
            break
    has_image = blank_count >= 2

    # Remove leading blank lines
    stripped_lines = [l for l in lines]
    # Find where actual content starts
    content_start = 0
    for j, line in enumerate(stripped_lines):
        if line.strip():
            content_start = j
            break

    body_text = '\n'.join(stripped_lines[content_start:])

    # Split on "Варианты ответа:" to separate question text from options
    parts = re.split(r'Варианты ответа\s*:', body_text, maxsplit=1)
    if len(parts) < 2:
        # Try alternate patterns
        parts = re.split(r'Варианты\s+ответа\s*:', body_text, maxsplit=1)

    if len(parts) < 2:
        # Fallback: try to split on numbered options
        parts = re.split(r'\n\s*1\.', body_text, maxsplit=1)
        if len(parts) == 2:
            question_text = parts[0].strip()
            options_text = "1." + parts[1]
        else:
            question_text = body_text.strip()
            options_text = ""
    else:
        question_text = parts[0].strip()
        options_text = parts[1].strip()

    # Clean question text
    question_text = re.sub(r'\s+', ' ', question_text).strip()
    # Remove page number artifacts at end
    question_text = re.sub(r'\s+\d+\s*$', '', question_text).strip()

    # Parse answer options
    options = []
    if options_text:
        # Match numbered options: "1. text" "2. text" etc.
        # Options may be 1-4
        option_matches = re.findall(
            r'(?:^|\n)\s*(\d+)\.\s+(.*?)(?=\n\s*\d+\.|$)',
            options_text,
            re.DOTALL
        )
        for num_str, opt_text in option_matches:
            opt_clean = re.sub(r'\s+', ' ', opt_text).strip()
            opt_clean = re.sub(r'\s+\d+\s*$', '', opt_clean).strip()
            if opt_clean:
                options.append(opt_clean)

    # Correct answer (convert from 1-based to 0-based)
    correct_idx = correct_answer_1based - 1

    q_id = f"{ticket_num}-{q_num}"
    result = {
        "id": q_id,
        "question": question_text,
        "options": options,
        "correctAnswer": correct_idx,
    }
    if has_image:
        result["__hasImage"] = True  # temp marker, replaced with actual path later

    return result


def build_image_mapping(pdf_path: Path) -> dict[str, int]:
    """
    Build question_id → image_index mapping using full-ticket text analysis.
    Must use full ticket text (not per-page) to avoid page-margin false positives.
    """
    mapping = {}
    img_idx = FIRST_QUESTION_IMG_IDX

    for ticket_num in range(1, TICKET_COUNT + 1):
        question_bodies = parse_ticket_page_range(pdf_path, ticket_num)
        img_questions = []
        for q_num in range(1, QUESTIONS_PER_TICKET + 1):
            if q_num not in question_bodies:
                continue
            q_body = question_bodies[q_num]
            lines = q_body.split('\n')
            blank_count = 0
            for line in lines:
                if line.strip() == '':
                    blank_count += 1
                else:
                    break
            if blank_count >= 2:
                img_questions.append(q_num)

        for q_num in img_questions:
            mapping[f"{ticket_num}-{q_num}"] = img_idx
            img_idx += 1

    return mapping


def main():
    print(f"Parsing PDF: {PDF_PATH}")
    if not PDF_PATH.exists():
        print(f"❌ PDF not found: {PDF_PATH}")
        sys.exit(1)

    print("Building image mapping...")
    img_map = build_image_mapping(PDF_PATH)
    print(f"  Mapped {len(img_map)} question images")

    print("Parsing questions from all 40 tickets...")
    tickets = []
    total_questions = 0
    total_with_image = 0
    parse_errors = []

    for ticket_num in range(1, TICKET_COUNT + 1):
        answers_1based = ANSWER_TABLE[ticket_num]
        question_bodies = parse_ticket_page_range(PDF_PATH, ticket_num)

        questions = []
        for q_num in range(1, QUESTIONS_PER_TICKET + 1):
            if q_num not in question_bodies:
                parse_errors.append(f"{ticket_num}-{q_num}: body not found")
                continue

            correct = answers_1based[q_num - 1]
            q = parse_question_body(question_bodies[q_num], ticket_num, q_num, correct)

            # Assign image path
            q_id = f"{ticket_num}-{q_num}"
            if q.pop("__hasImage", False) and q_id in img_map:
                img_idx = img_map[q_id]
                q["image"] = f"/images/questions/{q_id}.jpg"
                total_with_image += 1

            questions.append(q)
            total_questions += 1

        tickets.append({
            "ticketNumber": ticket_num,
            "questions": questions
        })

        # Progress
        if ticket_num % 10 == 0:
            print(f"  Processed ticket {ticket_num}/40")

    print(f"\nTotal questions: {total_questions}")
    print(f"With images: {total_with_image}")
    if parse_errors:
        print(f"\n⚠️  {len(parse_errors)} parse errors:")
        for e in parse_errors[:10]:
            print(f"   {e}")

    # Sample QA: check option counts
    option_count_dist = {}
    empty_options = []
    for ticket in tickets:
        for q in ticket["questions"]:
            n = len(q["options"])
            option_count_dist[n] = option_count_dist.get(n, 0) + 1
            if n == 0:
                empty_options.append(q["id"])

    print(f"\nOption count distribution: {option_count_dist}")
    if empty_options:
        print(f"⚠️  Questions with 0 options: {empty_options[:10]}")

    # Save questions.json
    data = {"tickets": tickets}
    with open(QUESTIONS_JSON, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Saved {total_questions} questions → {QUESTIONS_JSON}")

    # Save image map
    img_map_out = {}
    for ticket in tickets:
        for q in ticket["questions"]:
            if q.get("image"):
                q_id = q["id"]
                idx = img_map.get(q_id, -1)
                img_map_out[q_id] = {
                    "imgIndex": idx,
                    "imgFile": f"imgs-{idx:03d}.jpg",
                    "publicPath": q["image"],
                    "status": "auto"
                }
    with open(IMAGE_MAP_OUT, "w") as f:
        json.dump(img_map_out, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved image map → {IMAGE_MAP_OUT}")


if __name__ == "__main__":
    main()
