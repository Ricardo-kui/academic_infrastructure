"""
ObsidianChunker — parse Obsidian markdown with YAML frontmatter,
split by headers, and respect note_id / type fields.
"""

import re
from pathlib import Path
from typing import Iterator, Optional

from .models import Chunk


class ObsidianChunker:
    """Chunk Obsidian markdown files, respecting frontmatter and headers."""

    def __init__(
        self,
        max_chunk_size: int = 1000,
        overlap: int = 100,
    ):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def parse_frontmatter(self, text: str) -> tuple[dict, str]:
        """Extract YAML frontmatter and return (metadata, body)."""
        if not text.startswith("---"):
            return {}, text
        parts = text.split("---", 2)
        if len(parts) < 3:
            return {}, text
        import yaml
        try:
            meta = yaml.safe_load(parts[1]) or {}
        except Exception:
            meta = {}
        return meta, parts[2]

    def split_by_headers(self, text: str) -> list[tuple[Optional[str], str, int, int]]:
        """Split text by markdown headers (# ## ###).
        Returns list of (header_title, section_text, start_line, end_line).
        """
        lines = text.splitlines()
        sections: list[tuple[Optional[str], list[str], int]] = []
        current_header: Optional[str] = None
        current_lines: list[str] = []
        current_start = 0

        for i, line in enumerate(lines):
            header_match = re.match(r"^(#{1,6})\s+(.+)", line)
            if header_match:
                # Save previous section
                if current_lines:
                    sections.append((current_header, current_lines, current_start))
                current_header = header_match.group(2).strip()
                current_lines = [line]
                current_start = i
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_header, current_lines, current_start))

        # Convert to (header, text, start, end)
        result = []
        for idx, (header, sec_lines, start) in enumerate(sections):
            end = start + len(sec_lines)
            result.append((header, "\n".join(sec_lines), start, end))
        return result

    def chunk_text(self, text: str, header: Optional[str], line_start: int) -> Iterator[Chunk]:
        """Split oversized text into overlapping chunks."""
        if len(text) <= self.max_chunk_size:
            yield Chunk(
                text=text,
                source_file="",
                header=header,
                line_start=line_start,
                line_end=line_start + text.count("\n"),
            )
            return

        start = 0
        while start < len(text):
            end = start + self.max_chunk_size
            chunk_text = text[start:end]
            chunk_line_start = line_start + text[:start].count("\n")
            chunk_line_end = line_start + text[:end].count("\n")
            yield Chunk(
                text=chunk_text,
                source_file="",
                header=header,
                line_start=chunk_line_start,
                line_end=chunk_line_end,
            )
            start = end - self.overlap

    def chunk_file(self, file_path: Path) -> Iterator[Chunk]:
        """Chunk a single markdown file."""
        text = file_path.read_text(encoding="utf-8")
        meta, body = self.parse_frontmatter(text)
        note_id = meta.get("note_id") if meta else None
        doc_type = meta.get("type") if meta else None

        sections = self.split_by_headers(body)
        if not sections:
            # No headers — treat entire body as one chunk
            sections = [(None, body, 0, body.count("\n"))]

        for header, section_text, line_start, line_end in sections:
            for chunk in self.chunk_text(section_text, header, line_start):
                chunk.source_file = str(file_path)
                chunk.note_id = note_id
                chunk.doc_type = doc_type
                yield chunk
