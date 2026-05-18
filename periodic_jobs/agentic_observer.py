#!/usr/bin/env python3
"""
agentic_observer.py — LLM-powered Agentic Observer for academic infrastructure.

Scans daily file changes, sends content to an LLM (DeepSeek/Kimi/OpenRouter)
for semantic analysis, receives structured 🔴🟡🟢 observations,
and writes to daily_raw/.

Usage:
    python agentic_observer.py [YYYY-MM-DD] [--dry-run] [--force]
    python agentic_observer.py --test  # Quick connectivity test

Fallback: If LLM API is unavailable, degrades to rule-based observer.
Configure provider in .env: LLM_PROVIDER=deepseek (default), kimi, openrouter
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from llm_client import LLMClient
from observer import (
    VAULT_ROOT,
    INFRA_DIR,
    RAW_DIR,
    SCAN_TARGETS,
    TRACKED_FILES,
    find_modified_files,
    get_file_mtime,
    extract_summary,
)

# ── Configuration ──────────────────────────────────────────────────────────

# Token budget per observation run
MAX_TOTAL_TOKENS = 200_000  # Kimi K2.5 supports 256K context
APPROX_CHARS_PER_TOKEN = 2  # Conservative estimate for Chinese + English
MAX_TOTAL_CHARS = MAX_TOTAL_TOKENS * APPROX_CHARS_PER_TOKEN

# Priority mapping from Kimi output
PRIORITY_MAP = {
    "high": "🔴",
    "medium": "🟡",
    "low": "🟢",
}

# ── Prompt Template ────────────────────────────────────────────────────────

OBSERVER_SYSTEM_PROMPT = """你是一个学术研究项目的"日常观察员"。你的任务是为教授研究团队扫描每日的文件变动，提取有价值的学术进展，并按照重要性分级记录。

## 你的判断标准

🔴 **高优先级 (high)** — 满足任一：
- 理论框架的重大修正或突破
- 识别策略（IV/DiD/RDD等）的确定或变更
- 项目里程碑（数据匹配完成、基准回归跑通、投稿决定等）
- 核心假设的验证或推翻

🟡 **中优先级 (medium)** — 满足任一：
- 变量测量方案的确定
- 稳健性检验的设计或结果
- 文献综述的实质性推进（新锚文、新gap定位）
- 写作段落的关键修改

🟢 **低优先级 (low)** — 常规进展：
- 日常文献阅读
- 笔记整理、格式调整
- 数据清洗的常规步骤
- 会议记录

## 输出格式

你必须以 JSON 格式输出，不要添加任何 markdown 代码块标记：

{
  "observations": [
    {
      "priority": "high|medium|low",
      "project_tag": "#标签名",
      "type": "theory|methods|writing|literature|milestone|routine",
      "summary": "一句话摘要（50字以内）",
      "files": ["相对路径1", "相对路径2"],
      "reasoning": "简要说明为什么这个变动值得此优先级"
    }
  ]
}

## 约束
- 仅对**确实有学术价值**的变动生成观察，无价值的返回空数组
- project_tag 从以下选择：#产品召回, #共同所有权, #竞业协议, #方法论, #写作, #理论, #审稿, #跨专题
- 每条 observation 的 reasoning 不超过 30 字
- 尽量合并同一项目下的多个文件变动为一条观察"""

# ── Helpers ────────────────────────────────────────────────────────────────


def gather_file_contents(target_date: datetime, max_chars: int = MAX_TOTAL_CHARS) -> list[dict]:
    """Collect file contents for Kimi analysis, respecting token budget."""
    files_data: list[dict] = []
    total_chars = 0

    # Priority order: tracked files first, then project files
    all_paths: list[tuple[Path, str]] = []

    for tracked_file, source_type in TRACKED_FILES:
        if tracked_file.exists():
            mtime = get_file_mtime(tracked_file)
            if mtime and mtime.date() == target_date.date():
                all_paths.append((tracked_file, source_type))

    for scan_dir, source_type in SCAN_TARGETS:
        modified = find_modified_files(scan_dir, target_date)
        for p in modified:
            all_paths.append((p, source_type))

    # Sort by project relevance: Context Packets and 项目概览优先
    def relevance_score(path_source: tuple[Path, str]) -> int:
        p, _ = path_source
        name = p.name.lower()
        if "context packet" in name:
            return 100
        if "项目概览" in name or "project_overview" in name:
            return 90
        if "作战室" in name:
            return 80
        if "00 active" in str(p).lower():
            return 70
        if p.suffix == ".md":
            return 50
        return 10

    all_paths.sort(key=relevance_score, reverse=True)

    for p, source_type in all_paths:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue

        # Skip huge files
        if len(text) > 50_000:
            text = text[:50_000] + "\n\n[文件过长，已截断]"

        rel_path = str(p.relative_to(VAULT_ROOT)) if VAULT_ROOT in p.parents else str(p)
        entry = {
            "path": rel_path,
            "source": source_type,
            "content": text,
        }

        added_chars = len(json.dumps(entry, ensure_ascii=False))
        if total_chars + added_chars > max_chars:
            break

        files_data.append(entry)
        total_chars += added_chars

    return files_data


def build_observer_prompt(files_data: list[dict], target_date: str) -> list[dict[str, str]]:
    """Construct the prompt messages for Kimi."""
    # Summarize files for the prompt
    file_sections = []
    for f in files_data:
        file_sections.append(f"""---
文件: {f['path']}
来源: {f['source']}
内容:
{f['content'][:3000]}
---""")

    files_text = "\n\n".join(file_sections)

    user_prompt = f"""以下是 {target_date} 发生变动的学术项目文件。请分析每个变动的学术价值，按标准分级，输出 JSON。

## 今日变动文件

{files_text}

## 任务
请根据上述文件变动，判断哪些具有学术记录价值，输出标准 JSON 格式的 observations 数组。
如果没有值得记录的变动，输出 {{"observations": []}}。"""

    return [
        {"role": "system", "content": OBSERVER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def parse_kimi_observations(response_text: str) -> list[dict]:
    """Parse Kimi's JSON response into observation dicts."""
    # Strip markdown code fences if present
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        data = json.loads(text)
        return data.get("observations", [])
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from the text
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            data = json.loads(text[start:end])
            return data.get("observations", [])
        except (ValueError, json.JSONDecodeError):
            print(f"[!] Failed to parse Kimi response as JSON:\n{text[:500]}")
            return []


def observations_to_yaml_struct(observations: list[dict], date_str: str) -> dict:
    """Convert Kimi observations to the standard YAML structure."""
    activities = []
    for obs in observations:
        priority = obs.get("priority", "low")
        marker = PRIORITY_MAP.get(priority, "🟢")
        act_type = obs.get("type", "routine")
        tag = obs.get("project_tag", "#general")
        summary = obs.get("summary", "[no summary]")
        files = obs.get("files", [])
        reasoning = obs.get("reasoning", "")

        # Enrich summary with reasoning if present
        if reasoning:
            summary = f"{summary} ({reasoning})"

        activity = {
            "source": "agentic_kimi",
            "path": files[0] if files else "",
            "type": act_type,
            "project_tag": tag,
            "summary": summary,
            "priority": priority,
            "marker": marker,
        }
        activities.append(activity)

    return {
        "date": date_str,
        "collected_at": datetime.now().isoformat(),
        "source": "agentic_observer",
        "activities": activities,
        "activity_counts": {
            key: sum(1 for a in activities if a["type"] == key)
            for key in ["theory", "methods", "writing", "literature", "milestone", "routine"]
        },
    }


# ── Core Logic ─────────────────────────────────────────────────────────────


def run_agentic_observations(target_date: datetime, dry_run: bool = False, force: bool = False) -> dict | None:
    """Run the full agentic observation pipeline."""
    date_str = target_date.strftime("%Y-%m-%d")
    raw_path = RAW_DIR / f"{date_str}.yaml"

    if raw_path.exists() and not force and not dry_run:
        print(f"[skip] Raw file already exists: {raw_path}")
        return None

    # 1. Gather files
    print(f"[*] Gathering file changes for {date_str}...")
    files_data = gather_file_contents(target_date)
    if not files_data:
        print("[*] No file changes found today.")
        return None

    print(f"[*] Found {len(files_data)} files to analyze ({sum(len(f['content']) for f in files_data):,} chars)")

    # 2. Build prompt
    messages = build_observer_prompt(files_data, date_str)
    prompt_chars = sum(len(m["content"]) for m in messages)
    print(f"[*] Prompt size: ~{prompt_chars:,} chars (est. {prompt_chars // 2:,} tokens)")

    if dry_run:
        print("\n--- Prompt Preview (first 2000 chars) ---")
        print(messages[1]["content"][:2000])
        print("... (truncated)")
        return None

    # 3. Call LLM
    print("[*] Sending to LLM for analysis...")
    try:
        client = LLMClient()
        response = client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=8000,
        )
    except Exception as e:
        print(f"[!] LLM API call failed: {e}")
        print("[!] Consider running rule-based observer as fallback.")
        return None

    if hasattr(response, "content"):
        response_text = response.content
        usage_prompt = response.usage_prompt
        usage_completion = response.usage_completion
    else:
        response_text = str(response)
        usage_prompt = 0
        usage_completion = 0

    print(f"[*] LLM response received (prompt={usage_prompt}, completion={usage_completion})")
    if hasattr(response, "usage_prompt"):
        cost, currency = client.estimate_cost(response)
        print(f"[*] Est. cost: {cost:.4f} {currency}")

    # 4. Parse
    observations = parse_kimi_observations(response_text)
    print(f"[*] Parsed {len(observations)} observations")

    for obs in observations:
        marker = PRIORITY_MAP.get(obs.get("priority", "low"), "🟢")
        print(f"  {marker} [{obs.get('project_tag', '#general')}] {obs.get('summary', '')}")

    # 5. Convert to standard struct
    result = observations_to_yaml_struct(observations, date_str)

    # 6. Write
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    import yaml
    temp_path = raw_path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        yaml.dump(result, f, allow_unicode=True, sort_keys=False)
    temp_path.replace(raw_path)
    print(f"[write] {raw_path}")

    return result


# ── CLI ────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Agentic Observer (Kimi-powered)")
    parser.add_argument("date", nargs="?", help="Target date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without calling API")
    parser.add_argument("--force", action="store_true", help="Overwrite existing raw file")
    parser.add_argument("--test", action="store_true", help="Quick API connectivity test")
    args = parser.parse_args()

    if args.test:
        return _run_test()

    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        target_date = datetime.now()

    print(f"[*] Agentic Observer for {target_date.strftime('%Y-%m-%d')}")
    provider = os.environ.get("LLM_PROVIDER", "deepseek")
    print(f"[*] Provider: {provider} (model: {os.environ.get('LLM_MODEL', 'default')})")

    result = run_agentic_observations(target_date, dry_run=args.dry_run, force=args.force)
    if result is None and not args.dry_run:
        print("[*] No observations generated.")
    return 0


def _run_test() -> int:
    """Quick connectivity and cost test."""
    print("[*] Testing LLM API connectivity...")
    try:
        client = LLMClient()
        resp = client.chat_completion(
            messages=[
                {"role": "system", "content": "你是一个学术研究助手。"},
                {"role": "user", "content": "请回复一句话确认API连接正常，并简述你能帮学术研究者做什么。"},
            ],
            temperature=0.0,
        )
        if hasattr(resp, "content"):
            print(f"[*] OK: {resp.content}")
            print(f"[*] Usage: prompt={resp.usage_prompt}, completion={resp.usage_completion}")
            cost, currency = client.estimate_cost(resp)
            print(f"[*] Est. cost: {cost:.6f} {currency}")
        else:
            print(f"[*] Response: {resp}")
    except Exception as e:
        print(f"[!] Test failed: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
