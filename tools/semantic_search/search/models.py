from dataclasses import dataclass
from typing import Optional


@dataclass
class Chunk:
    """A chunk of text with metadata."""
    text: str
    source_file: str
    note_id: Optional[str] = None
    doc_type: Optional[str] = None
    header: Optional[str] = None
    line_start: int = 0
    line_end: int = 0


@dataclass
class SearchResult:
    """A search result with relevance score."""
    score: float
    chunk: Chunk
