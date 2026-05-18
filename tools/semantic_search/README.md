# Semantic Search for Obsidian Vault

Meaning-based search across the academic knowledge base.

## Setup

```bash
cd tools/semantic_search
python -m pip install -r requirements.txt

# Copy and edit API key
cp .env.example .env
# Edit .env with your OpenRouter API key
```

## Indexing Profiles

| Profile | Contents |
|---------|----------|
| `literature-index` | `literature/*.md` + `概念库/*.md` + `论证卡库/**/*.md` (Tier 1) |
| `atomic-index` | `文献笔记库/02 原子化/**/*.md` (Tier 2) |
| `project-index` | `00 工作台/项目/**/*.md` (Active projects) |
| `full-index` | All of the above |

## Usage

```bash
# List profiles
python -m search.cli profiles

# Build index for literature (Tier 1)
python -m search.cli index --profile literature-index

# Search
python -m search.cli search "competition softening measurement" --profile literature-index --top-k 10

# JSON output (for Claude integration)
python -m search.cli search "CEO narcissism mechanism" --profile literature-index --json

# Full index (slow on first run)
python -m search.cli index --profile full-index
```

## Integration with Claude Code

Claude Code can call this tool directly:

```bash
python tools/semantic_search/main.py search "query" --profile literature-index --json
```

The JSON output is consumed by Claude to build the `Knowledge Evidence Table`.
