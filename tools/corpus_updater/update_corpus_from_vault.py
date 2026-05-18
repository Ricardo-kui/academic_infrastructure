#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_corpus_from_vault.py
从 Vault 的 narrative_analysis 文件提取表达骨架，半自动更新 write-introduction 语料库。

使用方式:
  python update_corpus_from_vault.py [--dry-run] [--source-dir PATH] [--target-dir PATH]
"""

import os
import re
import sys
import io
import difflib
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DEFAULT_VAULT_NARRATIVE_DIR = r"D:\OneDrive\Obsidian Vault\00 工作台\叙述模板训练集\narrative_analysis\mvp30"
DEFAULT_SKILL_DIR = r"C:\Users\admin\.claude\skills\write-introduction"
DEFAULT_CORPUS_DIR = os.path.join(DEFAULT_SKILL_DIR, "academic-writing-corpus")
DEFAULT_REPORT_DIR = os.path.join(DEFAULT_SKILL_DIR, "corpus-update-reports")

CLASS_KEYWORDS = [
    ("Hook",        ["hook", "开场", "引子", "开头", "冷启动", "数据冲击", "共识挑战",
                     "范式挑战", "引语", "quotation", "丑闻", "案例", "轶事", "epigraph"]),
    ("Contribution",["贡献", "contribution", "声明", "我们贡献", "理论推进", "we contribute",
                     "this study makes", "our study is important because"]),
    ("Stakes",      ["stakes", "重要性", "经济显著性", "so what", "损失", "危机", "后果",
                     "经济损失", "价值", "cost", "quantified"]),
    ("Transition",  ["过渡", "转折", "transition", "信号词", "从...到...", "hook-to",
                     "literature-to", "gap-to"]),
    ("Tension",     ["矛盾", "缺口", "张力", "问题化", "blindspot", "assumption-wrong",
                     "contradicts", "inconsisten", "竞争逻辑", "解释不足", "尚未解释"]),
    ("Preview",     ["预览", "preview", "发现", "结果暗示", "假设预告", "findings preview",
                     "hypothesis preview"]),
    ("Mechanism",   ["机制", "mechanism", "中介", "mediat", "opposing-forces", "context-reversal"]),
    ("Theory_Lens", ["理论", "theory", "视角", "lens", "drawing on", "theorize", "argue that"]),
    ("Literature_Turn", ["文献", "literature", "对话", "conversation", "coherence",
                         "progressive", "synthesized", "non-coherence"]),
]

GAP_LANGUAGE_PATTERNS = {
    "Incompleteness": ["remains unclear", "remains poorly understood", "largely unaddressed",
                       "few studies have examined", "little is known", "underexplored",
                       "尚未解释", "留下空白", "遗漏了"],
    "Inadequacy":     ["overlooks", "treats as", "conflated", "misplaced", "decontextualized",
                       "implicit assumption", "structural blindspot", "解释不足", "误置了",
                       "忽视了", "片面"],
    "Incommensurability": ["consensus", "contradicts", "incompatible", "competing",
                           "paradox", "counter-evidence", "竞争逻辑", "不兼容", "矛盾"],
}


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm = text[3:end].strip()
    data = {}
    for line in fm.splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def extract_templates(filepath: Path) -> list:
    text = filepath.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    paper_key = fm.get("paper_key", filepath.stem)
    journal = fm.get("journal", "")
    year = fm.get("year", "")

    templates = []

    # Format A: **模板**: "content"  (zhou2017, han2020 style)
    pattern_a = re.compile(
        r'###\s+\d+\.\d+\s+(.+?)\n+'
        r'\*\*模板\*\*:\s*"?(.+?)"?\s*\n+',
        re.DOTALL
    )
    for m in pattern_a.finditer(text):
        title = m.group(1).strip()
        body = m.group(2).strip().strip('"').strip("'")
        templates.append({
            "title": title,
            "body": body,
            "source_paper": f"{paper_key}_{year}_{journal}".replace(" ", "_"),
            "paper_key": paper_key,
            "journal": journal,
            "year": year,
        })

    # Format B: **模板 X：desc（本文使用）**\n> "content"  (desjardine2023 style)
    section_pattern = re.compile(
        r'###\s+\d+\.\d+\s+(.+?)(?=\n#{1,3}\s|\Z)',
        re.DOTALL
    )
    for sec in section_pattern.finditer(text):
        sec_title = sec.group(1).strip().split('\n')[0].strip()
        sec_body = sec.group(0)
        tpl_pattern = re.compile(
            r'\*\*模板(?:\s+[A-Z])?[：:]\s*(.+?)\*\*\s*\n+'
            r'(?:\s*\n)*'
            r'(?:\*\*原文\*\*:\s*\n+)?'
            r'(?:\s*\n)*'
            r'(?:>\s*"(.+?)"\s*\n+|'
            r'```text\s*\n(.+?)\n```|'
            r'"{3}\s*\n(.+?)\n"{3})',
            re.DOTALL
        )
        for tm in tpl_pattern.finditer(sec_body):
            tpl_label = tm.group(1).strip()
            body = tm.group(2) or tm.group(3) or tm.group(4)
            if not body:
                continue
            body = body.strip().strip('"').strip("'")
            if any(t["body"] == body for t in templates):
                continue
            full_title = f"{sec_title} — {tpl_label}"
            templates.append({
                "title": full_title,
                "body": body,
                "source_paper": f"{paper_key}_{year}_{journal}".replace(" ", "_"),
                "paper_key": paper_key,
                "journal": journal,
                "year": year,
            })

    return templates


def classify_template(title: str, body: str) -> str:
    t_lower = title.lower()
    combined = (title + " " + body).lower()
    # Hard-coded priority fixes based on title signals
    if any(w in t_lower for w in ['hook', '开场', '引子', '开头', '冷启动', '数据冲击', '共识挑战',
                                    '范式挑战', '引语', 'quotation', '丑闻', '案例', '轶事', 'epigraph',
                                    '背景建立', '趋势现象', '行业关注', '社会案例']):
        return 'Hook'
    if any(w in t_lower for w in ['缺口', '问题化', 'tension', '矛盾', 'blindspot', 'assumption-wrong',
                                    'contradicts', '竞争逻辑', '解释不足', '尚未解释', '去情境化']):
        return 'Tension'
    if any(w in t_lower for w in ['贡献', 'contribution', '声明', '我们贡献', 'we contribute']):
        return 'Contribution'
    if any(w in t_lower for w in ['stakes', '重要性', '经济显著性', 'so what', '经济损失', '价值',
                                    'quantified', '成本量化']):
        return 'Stakes'
    if any(w in t_lower for w in ['预览', 'preview', '发现预览', '结果暗示', '假设预告', 'findings preview']):
        return 'Preview'
    for cls, keywords in CLASS_KEYWORDS:
        for kw in keywords:
            if kw.lower() in combined:
                return cls
    return 'Uncategorized'


def infer_gap_types(body: str) -> list:
    body_lower = body.lower()
    matched = []
    for gap, patterns in GAP_LANGUAGE_PATTERNS.items():
        if any(p.lower() in body_lower for p in patterns):
            matched.append(gap)
    return matched if matched else ["General"]


def skeleton_similarity(a: str, b: str) -> float:
    def normalize(s):
        s = re.sub(r'\[[^\]]+\]', '[PLACEHOLDER]', s)
        s = re.sub(r'\([^)]+\)', '(REF)', s)
        s = re.sub(r'[A-Za-z]+', 'WORD', s)
        return s.lower().strip()
    return difflib.SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def cluster_templates(templates: list, threshold: float = 0.55) -> list:
    clusters = []
    for t in templates:
        best_cluster = None
        best_sim = 0.0
        for c in clusters:
            if c["type"] != t["type"]:
                continue
            rep = c["skeletons"][0]["body"]
            sim = skeleton_similarity(rep, t["body"])
            if sim > best_sim:
                best_sim = sim
                best_cluster = c

        if best_cluster and best_sim >= threshold:
            best_cluster["skeletons"].append(t)
            best_cluster["papers"].add(t["source_paper"])
            best_cluster["gap_types"].update(infer_gap_types(t["body"]))
        else:
            clusters.append({
                "id": f"{t['type'].lower()}_auto_{len(clusters)+1:03d}",
                "type": t["type"],
                "skeletons": [t],
                "papers": {t["source_paper"]},
                "gap_types": set(infer_gap_types(t["body"])),
            })
    return clusters


def compute_validation_status(cluster: dict) -> tuple:
    n = len(cluster["papers"])
    if n >= 3:
        return ("PREMIUM", "ROBUST")
    elif n >= 2:
        return ("STANDARD", "VERIFIED")
    else:
        return ("EXPERIMENTAL", "SINGLE-INSTANCE")


def infer_exclusivity(cluster: dict) -> str:
    gaps = cluster["gap_types"]
    if len(gaps) == 1 and "General" not in gaps:
        return "HIGH"
    elif len(gaps) <= 2:
        return "MEDIUM"
    return "LOW"


def generate_corpus_file(cluster: dict, out_dir: Path) -> Path:
    status, validation = compute_validation_status(cluster)
    module_type_dir = out_dir / (cluster["type"].lower().replace("_", "-") + "s")
    module_type_dir.mkdir(parents=True, exist_ok=True)

    rep_title = cluster["skeletons"][0]["title"]
    safe_title = re.sub(r'[^\w一-鿿-]', '-', rep_title).strip('-')
    safe_title = re.sub(r'-+', '-', safe_title).lower()[:60]
    filepath = module_type_dir / f"{cluster['id']}_{safe_title}.md"

    main = max(cluster["skeletons"], key=lambda x: len(x["body"]))
    variants = [s for s in cluster["skeletons"] if s["body"] != main["body"]]

    star = "⭐" if status == "PREMIUM" else "✓" if status == "STANDARD" else "🔬"
    lines = [
        f"# {rep_title}",
        "",
        "## 功能描述",
        f"**类型**: {cluster['type']}",
        f"**适用 Gap**: {', '.join(sorted(cluster['gap_types']))}",
        f"**收录状态**: {star} {status}",
        f"**验证等级**: {validation}",
        f"**来源论文数**: {len(cluster['papers'])}",
        "",
        "## 验证状态",
        f"- 跨论文复现: {len(cluster['papers'])} 篇",
    ]
    for p in sorted(cluster["papers"]):
        lines.append(f"  - {p}")
    lines.extend([
        f"- 生成力测试: 待执行（使用 `--generativity-test` 触发）",
        f"- 排他性评估: {infer_exclusivity(cluster)} — {'与特定 Gap 类型强绑定' if infer_exclusivity(cluster)=='HIGH' else '跨少量 Gap 类型可用' if infer_exclusivity(cluster)=='MEDIUM' else '通用性强'}",
        "",
        "## 表达骨架",
        "",
        "```text",
        f"{main['body']}",
        "```",
        "",
    ])

    if variants:
        lines.extend(["## 骨架变体", ""])
        for i, v in enumerate(variants, 1):
            lines.extend([
                f"### 变体 {i}（来自 {v['paper_key']}）",
                "```text",
                f"{v['body']}",
                "```",
                "",
            ])

    lines.extend([
        "## 使用指南",
        "",
        "### 适用场景",
        "[由 distill skill 在使用时补充]",
        "",
        "### 常见误用",
        "[由 distill skill 的 Skeleton Critic 在验证时补充]",
        "",
        "### 必须配对",
        "[由 assembly-guide.md 维护]",
        "",
        "### 互斥警告",
        "[由 assembly-guide.md 维护]",
        "",
        "---",
        f"*自动生成于 {datetime.now().strftime('%Y-%m-%d')} by update_corpus_from_vault.py*",
    ])

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return filepath


def generate_module_index_updates(clusters: list) -> str:
    lines = [
        "<!-- 以下为 update_corpus_from_vault.py 生成的增量更新块 -->",
        "<!-- 建议：将此块内容合并到 module-index.md 的对应分类表格中 -->",
        "",
        f"## 自动发现模块（{datetime.now().strftime('%Y-%m-%d')}）",
        "",
        "| # | 文件名 | 功能描述 | 类型 | 适用 Gap | 来源论文数 | 状态 |",
        "|---|--------|---------|------|---------|-----------|------|",
    ]
    for c in clusters:
        status, _ = compute_validation_status(c)
        rep_title = c["skeletons"][0]["title"]
        gaps = ", ".join(sorted(c["gap_types"]))
        star = "⭐" if status == "PREMIUM" else "✓" if status == "STANDARD" else "🔬"
        lines.append(
            f"| {c['id'].split('_')[-1]} | `{c['id']}` | {rep_title[:40]}{'...' if len(rep_title) > 40 else ''} | {c['type']} | {gaps} | {len(c['papers'])} | {star} {status} |"
        )
    lines.append("")
    return "\n".join(lines)


def generate_report(clusters: list, output_path: Path, dry_run: bool = False):
    by_type = defaultdict(list)
    for c in clusters:
        by_type[c["type"]].append(c)

    lines = [
        f"# Corpus Update Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"**运行模式**: {'DRY-RUN（未写入文件）' if dry_run else 'LIVE（已写入文件）'}",
        f"**总 Cluster 数**: {len(clusters)}",
        f"**总来源论文数**: {len(set(p for c in clusters for p in c['papers']))}",
        "",
        "## 统计概览",
        "",
        "| 类型 | Cluster 数 | PREMIUM | STANDARD | EXPERIMENTAL |",
        "|------|-----------|---------|----------|--------------|",
    ]
    total_stats = {"PREMIUM": 0, "STANDARD": 0, "EXPERIMENTAL": 0}
    for t in sorted(by_type.keys()):
        cs = by_type[t]
        stats = {"PREMIUM": 0, "STANDARD": 0, "EXPERIMENTAL": 0}
        for c in cs:
            s, _ = compute_validation_status(c)
            stats[s] += 1
            total_stats[s] += 1
        lines.append(f"| {t} | {len(cs)} | {stats['PREMIUM']} | {stats['STANDARD']} | {stats['EXPERIMENTAL']} |")
    lines.append(f"| **总计** | **{len(clusters)}** | **{total_stats['PREMIUM']}** | **{total_stats['STANDARD']}** | **{total_stats['EXPERIMENTAL']}** |")
    lines.append("")

    experimental = [c for c in clusters if compute_validation_status(c)[0] == "EXPERIMENTAL"]
    if experimental:
        lines.extend([
            "## 需要人工审阅的 EXPERIMENTAL 模块",
            "",
            "以下模块仅来源于 1 篇论文，建议在使用前执行 distill skill 的 Skeleton Critic 验证。",
            "",
            "| ID | 类型 | 标题 | 来源论文 |",
            "|----|------|------|---------|",
        ])
        for c in experimental:
            lines.append(f"| {c['id']} | {c['type']} | {c['skeletons'][0]['title'][:50]} | {list(c['papers'])[0]} |")
        lines.append("")

    standard = [c for c in clusters if compute_validation_status(c)[0] == "STANDARD"]
    if standard:
        lines.extend([
            "## STANDARD 模块（可升级为 PREMIUM 的候选）",
            "",
            "以下模块已跨 2 篇论文复现，再找到 1 个独立案例即可升级为 PREMIUM。",
            "",
            "| ID | 类型 | 标题 | 来源论文 |",
            "|----|------|------|---------|",
        ])
        for c in standard:
            lines.append(f"| {c['id']} | {c['type']} | {c['skeletons'][0]['title'][:50]} | {', '.join(sorted(c['papers']))} |")
        lines.append("")

    lines.extend(["## 新发现的模式", "", "| 观察 | 证据 | 建议动作 |", "|------|------|---------|"])
    gap_type_counts = defaultdict(lambda: defaultdict(int))
    for c in clusters:
        for g in c["gap_types"]:
            gap_type_counts[c["type"]][g] += 1
    for t, gaps in gap_type_counts.items():
        total = sum(gaps.values())
        for g, cnt in gaps.items():
            if g != "General" and cnt / total >= 0.7:
                lines.append(f"| {t} 模块中 {g} 占比 {cnt}/{total} | 自动聚类结果 | 在 module-index.md 中强化 {t}→{g} 推荐映射 |")
    lines.append("")

    lines.extend([
        "## module-index.md 增量更新块",
        "",
        "将以下内容合并到 `references/module-index.md` 的对应分类表格末尾：",
        "",
        "```markdown",
        generate_module_index_updates(clusters),
        "```",
        "",
        "---",
        "*本报告由 update_corpus_from_vault.py 自动生成。*",
    ])

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="从 Vault narrative 更新 write-introduction 语料库")
    parser.add_argument("--source-dir", default=DEFAULT_VAULT_NARRATIVE_DIR,
                        help="Vault narrative_analysis 目录")
    parser.add_argument("--target-dir", default=DEFAULT_CORPUS_DIR,
                        help="write-introduction academic-writing-corpus 目录")
    parser.add_argument("--report-dir", default=DEFAULT_REPORT_DIR,
                        help="审阅报告输出目录")
    parser.add_argument("--dry-run", action="store_true",
                        help="只生成报告，不实际写入 corpus 文件")
    parser.add_argument("--similarity-threshold", type=float, default=0.55,
                        help="骨架聚类相似度阈值 (0-1)")
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    target_dir = Path(args.target_dir)
    report_dir = Path(args.report_dir)

    if not source_dir.exists():
        print(f"[ERROR] Source directory not found: {source_dir}")
        sys.exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    narrative_files = list(source_dir.glob("*_narrative.md"))
    print(f"[INFO] Found {len(narrative_files)} narrative files in {source_dir}")

    all_templates = []
    for nf in narrative_files:
        try:
            tpls = extract_templates(nf)
            for t in tpls:
                t["type"] = classify_template(t["title"], t["body"])
            all_templates.extend(tpls)
        except Exception as e:
            print(f"[WARN] Failed to parse {nf.name}: {e}")

    print(f"[INFO] Extracted {len(all_templates)} templates")

    by_type = defaultdict(list)
    for t in all_templates:
        by_type[t["type"]].append(t)

    all_clusters = []
    for t, tpls in by_type.items():
        clusters = cluster_templates(tpls, threshold=args.similarity_threshold)
        all_clusters.extend(clusters)
        print(f"[INFO] {t}: {len(tpls)} templates -> {len(clusters)} clusters")

    written_files = []
    if not args.dry_run:
        for c in all_clusters:
            fp = generate_corpus_file(c, target_dir)
            written_files.append(fp)
        print(f"[INFO] Written {len(written_files)} corpus files to {target_dir}")

    report_path = report_dir / f"corpus-update-report-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
    generate_report(all_clusters, report_path, dry_run=args.dry_run)
    print(f"[INFO] Report saved to {report_path}")

    print("\n" + "="*60)
    print("MODULE-INDEX INCREMENTAL UPDATE BLOCK")
    print("="*60)
    print(generate_module_index_updates(all_clusters))


if __name__ == "__main__":
    main()
