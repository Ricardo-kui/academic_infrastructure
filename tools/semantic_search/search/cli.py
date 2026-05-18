"""
CLI for academic semantic search across Obsidian Vault.
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tqdm import tqdm

from .chunker import ObsidianChunker
from .embedding import EmbeddingClient
from .index import ForwardIndex
from .models import Chunk


# ── Profile definitions ───────────────────────────────────────────────────

PROFILES = {
    "literature-index": {
        "description": "Tier 1 canonical notes: literature, concepts, claim cards",
        "paths": [
            "literature/*.md",
            "概念库/*.md",
            "论证卡库/**/*.md",
        ],
    },
    "atomic-index": {
        "description": "Tier 2 deep evidence: atomic notes",
        "paths": [
            "文献笔记库/02 原子化/**/*.md",
        ],
    },
    "project-index": {
        "description": "Active projects only",
        "paths": [
            "00 工作台/项目/**/*.md",
        ],
    },
    "full-index": {
        "description": "Comprehensive: Tier 1 + Tier 2 + projects",
        "paths": [
            "literature/*.md",
            "概念库/*.md",
            "论证卡库/**/*.md",
            "文献笔记库/02 原子化/**/*.md",
            "00 工作台/项目/**/*.md",
        ],
    },
}


# ── Helpers ────────────────────────────────────────────────────────────────


def expand_globs(vault_root: Path, patterns: list[str]) -> list[Path]:
    """Expand glob patterns under vault_root, excluding trash/dirs."""
    files = set()
    for pat in patterns:
        for p in vault_root.rglob(pat.lstrip("/")):
            if p.is_file() and p.suffix == ".md":
                files.add(p)
    return sorted(files)


def load_env() -> None:
    """Load .env from infra dir if present."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path)


# ── Commands ───────────────────────────────────────────────────────────────


def cmd_index(args: argparse.Namespace) -> int:
    vault = Path(args.vault_root)
    if not vault.exists():
        print(f"[error] Vault not found: {vault}", file=sys.stderr)
        return 1

    profile = PROFILES.get(args.profile)
    if not profile:
        print(f"[error] Unknown profile: {args.profile}", file=sys.stderr)
        print(f"Available: {', '.join(PROFILES.keys())}")
        return 1

    files = expand_globs(vault, profile["paths"])
    if not files:
        print(f"[warn] No files matched for profile '{args.profile}'")
        return 0

    print(f"[*] Profile: {args.profile} — {profile['description']}")
    print(f"[*] Found {len(files)} markdown files")

    index_dir = Path(args.index_dir) / args.profile
    index = ForwardIndex(index_dir)
    chunker = ObsidianChunker(max_chunk_size=1000, overlap=100)
    embed = EmbeddingClient()

    manifest = index.get_manifest()

    # Determine which files need indexing
    to_index = []
    for f in files:
        mtime = os.path.getmtime(f)
        rel = str(f)
        if rel not in manifest or manifest[rel].get("mtime", 0) < mtime:
            to_index.append(f)

    if not to_index:
        print("[*] All files up to date. Nothing to index.")
        return 0

    print(f"[*] Indexing {len(to_index)} changed files...")

    for fpath in tqdm(to_index, desc="Indexing"):
        chunks = list(chunker.chunk_file(fpath))
        if not chunks:
            continue
        texts = [c.text for c in chunks]
        embeddings = embed.embed_batch(texts)
        index.update_file(str(fpath), chunks, embeddings)

    print(f"[*] Done. Index stored at: {index_dir}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    index_dir = Path(args.index_dir) / args.profile
    if not index_dir.exists():
        print(f"[error] Index not found: {index_dir}", file=sys.stderr)
        print("Run: python -m search.cli index --profile {profile}")
        return 1

    index = ForwardIndex(index_dir)
    embed = EmbeddingClient()

    print(f"[*] Searching: '{args.query}'")
    q_emb = embed.embed(args.query)
    results = index.search(q_emb, top_k=args.top_k)

    if args.json:
        out = []
        for score, chunk in results:
            out.append(
                {
                    "score": round(score, 4),
                    "source": chunk.source_file,
                    "note_id": chunk.note_id,
                    "doc_type": chunk.doc_type,
                    "header": chunk.header,
                    "line_start": chunk.line_start,
                    "line_end": chunk.line_end,
                    "text": chunk.text[:500],
                }
            )
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for rank, (score, chunk) in enumerate(results, 1):
            rel_path = chunk.source_file
            print(f"\n--- Result {rank} (score: {score:.4f}) ---")
            print(f"File: {rel_path}")
            if chunk.note_id:
                print(f"Note ID: {chunk.note_id}")
            if chunk.header:
                print(f"Header: {chunk.header}")
            print(f"Lines: {chunk.line_start}-{chunk.line_end}")
            print(f"Text:\n{chunk.text[:400]}...")

    return 0


def cmd_list_profiles(_args: argparse.Namespace) -> int:
    print("Available indexing profiles:\n")
    for name, info in PROFILES.items():
        print(f"  {name:20s} — {info['description']}")
        for p in info["paths"]:
            print(f"{'':22s} {p}")
    return 0


# ── Main ───────────────────────────────────────────────────────────────────


def main():
    load_env()

    default_vault = "D:/Onedrive/Obsidian Vault"
    default_index = os.path.expanduser("~/.claude/academic_infrastructure/tools/semantic_search/indexes")

    parser = argparse.ArgumentParser(
        prog="academic_search",
        description="Semantic search over Obsidian Vault literature notes.",
    )
    parser.add_argument(
        "--vault-root",
        default=default_vault,
        help="Path to Obsidian Vault root",
    )
    parser.add_argument(
        "--index-dir",
        default=default_index,
        help="Directory to store index files",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # index
    idx = sub.add_parser("index", help="Build or update the embedding index")
    idx.add_argument(
        "--profile",
        default="literature-index",
        choices=list(PROFILES.keys()),
        help="Which document set to index",
    )

    # search
    srch = sub.add_parser("search", help="Search the index")
    srch.add_argument("query", help="Search query")
    srch.add_argument(
        "--profile",
        default="literature-index",
        choices=list(PROFILES.keys()),
    )
    srch.add_argument("--top-k", type=int, default=10)
    srch.add_argument("--json", action="store_true", help="Output JSON")

    # profiles
    sub.add_parser("profiles", help="List available profiles")

    args = parser.parse_args()

    if args.command == "index":
        return cmd_index(args)
    elif args.command == "search":
        return cmd_search(args)
    elif args.command == "profiles":
        return cmd_list_profiles(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
