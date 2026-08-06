import re
from dataclasses import dataclass


@dataclass
class Clause:
    """One retrievable unit: a single contract clause."""

    id: str
    clause_number: str
    title: str
    text: str
    section_title: str = ""  # the parent header this clause falls under, e.g. "Definitions"


# Patterns that commonly mark the start of a new clause/section in
# contracts. Ordered roughly from most to least specific. Each pattern
# must capture the clause "number" in group 1 and the "title" in group 2.
CLAUSE_HEADER_PATTERNS = [
    re.compile(r"^\s*(ARTICLE\s+[IVXLC]+)[\.\:\-\s]+(.*)$", re.IGNORECASE),
    re.compile(r"^\s*(SECTION\s+\d+(?:\.\d+)*)[\.\:\-\s]+(.*)$", re.IGNORECASE),
    re.compile(r"^\s*(CLAUSE\s+\d+(?:\.\d+)*)[\.\:\-\s]+(.*)$", re.IGNORECASE),
    re.compile(r"^\s*(\d+(?:\.\d+){0,3})[\.\)]?\s+([A-Z][A-Za-z ,&/\-]{2,80})\s*$"),
]

# A line is only treated as a header if it's reasonably short — long
# numbered sentences ("4.2 million dollars were paid...") are body text,
# not headers, even though they start with a number.
MAX_HEADER_LINE_LENGTH = 100


def _match_header(line: str):
    """Return (clause_number, title) if the line looks like a clause header, else None."""
    stripped = line.strip()
    if not stripped or len(stripped) > MAX_HEADER_LINE_LENGTH:
        return None

    for pattern in CLAUSE_HEADER_PATTERNS:
        match = pattern.match(stripped)
        if match:
            number = match.group(1).strip()
            title = match.group(2).strip() if match.lastindex and match.lastindex >= 2 else ""
            return number, title

    return None


def chunk_contract(text: str) -> list[Clause]:
    """
    Split raw contract text into clause-level chunks.

    Falls back gracefully: if no clause headers are detected at all,
    the whole document becomes a single chunk rather than silently
    losing content.
    """
    lines = text.split("\n")

    header_positions = []  # list of (line_idx, number, title)
    for idx, line in enumerate(lines):
        matched = _match_header(line)
        if matched:
            number, title = matched
            header_positions.append((idx, number, title))

    if not header_positions:
        return [
            Clause(
                id="clause_0001",
                clause_number="N/A",
                title="Full Document",
                text=text.strip(),
            )
        ]

    clauses = []
    current_section_title = ""
    clause_counter = 0

    for i, (line_idx, number, title) in enumerate(header_positions):
        next_line_idx = (
            header_positions[i + 1][0] if i + 1 < len(header_positions) else len(lines)
        )
        body_lines = lines[line_idx + 1 : next_line_idx]
        body_text = "\n".join(body_lines).strip()

        # A header with no body of its own (e.g. "1 Definitions" directly
        # followed by "1.1 Term") is a section marker, not a clause.
        # Track it as context for the clauses under it.
        if not body_text:
            current_section_title = title or number
            continue

        clause_counter += 1
        full_text = f"{number} {title}\n{body_text}".strip()
        clauses.append(
            Clause(
                id=f"clause_{clause_counter:04d}",
                clause_number=number,
                title=title or "(untitled)",
                text=full_text,
                section_title=current_section_title,
            )
        )

    return clauses


if __name__ == "__main__":
    import sys
    from parser import extract_text

    if len(sys.argv) != 2:
        print("Usage: python chunker.py <path_to_contract>")
        sys.exit(1)

    raw_text = extract_text(sys.argv[1])
    clauses = chunk_contract(raw_text)

    print(f"Found {len(clauses)} clauses.\n")
    for c in clauses:
        preview = c.text.replace("\n", " ")[:100]
        print(f"[{c.id}] {c.clause_number} — {c.title}  (section: {c.section_title})")
        print(f"    {preview}...\n")