#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量为 write-methods 和 write-results SKILL.md 中的模板变体添加验证状态标注。
"""

import re
import sys
from pathlib import Path

METHODS_STATUS = {
    # M1
    "**通用填空段落**：": " ⭐ PREMIUM（28/28 篇范文使用，跨所有模型类型复现）",
    "**自然实验/DiD 变体**（替换首句）：": " ✓ STANDARD（5-8 篇 DiD/自然实验范文复现）",
    "**实验变体**：": " ✓ STANDARD（5-6 篇实验范文复现）",
    "**多研究变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：使用通用填空段落，将 study sequence 嵌入 M1 末尾",
    "**同时方程/SEM 变体**（替换整个 M1）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用填空段落 + M7 同时方程变体",
    # M2
    "**稀有结果变体**（在通用段落前插入）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M2 段落 + 脚注说明抽样策略",
    "**实证对象构建变体**（替换或前置）：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：通用 M2 段落",
    "**自然实验/DiD 变体**：": " ✓ STANDARD（5-8 篇 DiD 范文复现）",
    "**多研究变体**（逐研究）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M2 段落 + M9 多研究过渡段",
    "**PSM匹配面板变体**（在通用段落中加入匹配步骤）：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：通用 M2 + M8 匹配检验",
    "**层级回退匹配变体**（如 Pfarrer et al. AMJ，1:3 SIC 匹配 + 层级回退）：": " 🔬 EXPERIMENTAL（2 篇范文：Pfarrer et al., Mayo et al.）⚠️ 保守替代：通用 M2 + PSM 变体",
    "**多行为者设计变体**（替换通用段落）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M2 段落 + 说明多数据源匹配",
    "**多源嵌套调查变体**（如 Mannor et al. SMJ，多方法数据 + 聚类标准误）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M2 + M7 多层模型/聚类标准误",
    "**事件历史变体**（在通用段落中加入过程说明）：": " 🔬 EXPERIMENTAL（2-3 篇范文：Zhou 2017, Pontikes 2012 等）⚠️ 保守替代：通用 M2 + M3 生存分析变体",
    # M3
    "**稀有结果/序数变体**（替换末句）：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：通用 M3 段落",
    "**事件研究变体**：": " ✓ STANDARD（3-4 篇事件研究范文复现）",
    "**指数/净指数变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M3 段落",
    "**行为编码变体（实验）**：": " 🔬 EXPERIMENTAL（3-4 篇实验范文）⚠️ 保守替代：通用 M3 段落 + 说明编码者间信度",
    "**文本构念测量变体**（M3 或 M4 均可使用，三段式效度链）：": " 🔬 EXPERIMENTAL（3-4 篇范文：Zhao 2022, Gamache 2020 等）⚠️ 保守替代：通用 M3 + 增加效度检验句",
    "**LIWC 心理语言学构念测量变体**（如 Mannor et al. SMJ，Pfarrer et al. AMJ）：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：通用 M3 段落 + 增加字典说明",
    "**人工内容分析 + 编码者间信度变体**（如 Desai AMJ，Pfarrer et al. AMJ）：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：通用 M3 段落 + 编码者间信度说明",
    "**推断二元结果变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M3 段落",
    "**多行为者因变量变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M3 段落",
    # M4
    "**自然实验/处理变量变体**：": " ✓ STANDARD（5-8 篇 DiD/自然实验范文复现）",
    "**处理分配稳定性补充**（DiD 可选）：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：省略此段",
    "**竞争机制预测变量变体**（机制测试中分解核心构念时）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M4 段落",
    "**实验操纵变体**：": " ✓ STANDARD（5-6 篇实验范文复现）",
    "**网络/组合/配对构念变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M4 段落",
    "**同伴效应/网络效应变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M4 段落",
    "**构造暴露/指数变体**（用于堆叠扩散或媒体暴露）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M4 段落",
    "**文本构念预测变量变体**（当预测变量来自文本分析，如 earnings calls、10-K、媒体、访谈时）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M4 段落",
    "**同时方程变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M4 段落",
    # M5
    "**子样本分割变体**（用样本分割而非交互项检验调节时）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M5 段落",
    "**行为者类型分解变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M5 段落",
    "**边界条件验证变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M5 段落",
    "**间接调节（ mediated moderation ）变体**：": " 🔬 EXPERIMENTAL（1 篇范文）⚠️ 保守替代：通用 M5 段落",
    # M6
    "**自然实验/Bad Control 变体**：": " ✓ STANDARD（5-8 篇自然实验/DiD 范文复现）",
    "**同时方程/方程特定控制变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M6 段落",
    # M7
    "**模型选择理由补充段**（按需添加）：": " ✓ STANDARD（15+/28 篇范文使用）",
    "**诊断检验补充段**：": " ✓ STANDARD（15+/28 篇范文使用）",
    "**非线性模型变体**：": " ✓ STANDARD（8-10 篇非线性模型范文复现）",
    "**DiD 变体**：": " ✓ STANDARD（5-8 篇 DiD 范文复现）",
    "**DiD 方程编号与 SE 聚类引用补充**：": " ✓ STANDARD（5-8 篇 DiD 范文复现）",
    "**生存分析变体**：": " 🔬 EXPERIMENTAL（2-3 篇范文：Zhou 2017, Pontikes 2012 等）⚠️ 保守替代：通用 M7 段落 + 说明分布选择",
    "**复发事件 AFT 变体**（当同一主体经历多次事件时）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M7 + 生存分析变体",
    "**复发事件风险模型变体**（Recurrent-Event Hazard，如 Mayo et al. POMS）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M7 + 生存分析变体",
    "**复发事件时间测量策略补充段**（当需要论证 continuous vs. reset time 时）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：省略",
    "**同时方程变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M7 段落",
    "**IV/2SLS 变体**：": " ✓ STANDARD（3-4 篇 IV 范文复现）",
    "**线性概率模型（LPM）+ 2SLS 变体**（二元 DV 且需固定效应时）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：IV/2SLS 变体",
    "**事件研究 GLM 变体**（CAR 为 DV 时）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M7 段落",
    "**动态面板/GMM 变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M7 段落 + M8 Nickell bias 提示",
    "**匹配DiD/广义DiD 变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：DiD 变体 + M2 PSM 变体",
    "**堆叠扩散Logit 变体**：": " 🔬 EXPERIMENTAL（1 篇范文）⚠️ 保守替代：通用 M7 段落",
    "**PSM匹配面板 + 随机效应Tobit 变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：M7 Tobit + M2 PSM",
    "**混合效应（within-between 分解）变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M7 段落",
    "**HLM/多层模型变体**（当数据为嵌套结构，如员工-团队-公司，或重复测量-个体时）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 M7 段落 + 说明聚类标准误",
    "**实验变体**：": " ✓ STANDARD（5-6 篇实验范文复现）",
    # M8
    "**自然实验/DiD 变体**：": " ✓ STANDARD（5-8 篇 DiD 范文复现）",
    "**DiD 置换检验预览补充**（可选，置于自然实验/DiD 变体后）：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：省略",
    "**内生性/控制函数变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：M8 通用段落",
    "**实验效度变体**：": " ✓ STANDARD（5-6 篇实验范文复现）",
    "**多研究变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：省略",
    "**IV 排他性约束/过度识别检验变体**：": " ✓ STANDARD（3-4 篇 IV 范文复现）",
    "**同伴效应/网络效应 falsification 变体**：": " 🔬 EXPERIMENTAL（1 篇范文）⚠️ 保守替代：M8 通用段落",
    "**匹配DiD 平行趋势与重叠支撑变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：M8 自然实验/DiD 变体",
    "**粗化精确匹配（CEM）/ 匹配解决内生性变体**（非 DiD，仅用匹配加权解决内生性）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：M8 通用段落",
    "**制度/政策体制安慰剂检验变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：M8 通用段落",
    "**部分重叠同伴群体 + 形式化识别证明变体**（网络效应核心识别故事）：": " 🔬 EXPERIMENTAL（1 篇范文）⚠️ 保守替代：M8 通用段落",
    "**SEM 模型识别变体**（当使用结构方程模型或联立方程时）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：M8 通用段落",
    # M9
    "**多研究总览段**（M9 前置）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：省略",
    "**逐研究过渡段**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：省略",
    "**研究间衔接段**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：省略",
}

RESULTS_STATUS = {
    # R1
    "**通用填空段落**：": " ⭐ PREMIUM（28/28 篇范文使用）",
    "**多研究变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 R1 段落",
    # R2
    "**通用填空段落**：": " ⭐ PREMIUM（28/28 篇范文使用）",
    "**DiD 变体**：": " ✓ STANDARD（5-8 篇 DiD 范文复现）",
    "**多研究变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 R2 段落",
    "**双重估计量表格导航变体**（当 Results 包含两种不同估计量时，如 AFT + GLM）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 R2 段落 + 分别说明两个表格",
    "**同时方程变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 R2 段落",
    "**IV/2SLS 变体**：": " ✓ STANDARD（3-4 篇 IV 范文复现）",
    "**IV/2SLS 脚注精简变体**（当 first-stage 仅作为诊断、不单独展示时，如 ASQ 常见做法）：": " ✓ STANDARD（3-4 篇 IV 范文复现）",
    "**匹配DiD 变体**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 R2 段落 + 说明匹配后样本",
    # R3
    "**通用填空段落（每假设一段，内置四拍）**：": " ⭐ PREMIUM（28/28 篇范文使用）",
    "**含经济显著性（R5 嵌入）的扩展版**：": " ⭐ PREMIUM（20+/28 篇范文使用）",
    "**OLS/FE 专用**：": " ✓ STANDARD（15+/28 篇面板数据范文复现）",
    "**Logit/Probit/Ordered Probit 专用**：": " ✓ STANDARD（8-10 篇非线性模型范文复现）",
    "**有序 Probit 专用**：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：Logit/Probit 专用 + 增加序数解释句",
    "**生存分析专用**：": " 🔬 EXPERIMENTAL（2-3 篇范文：Zhou 2017, Pontikes 2012 等）⚠️ 保守替代：通用 R3 段落 + 说明 shape parameter",
    "**DiD 专用**：": " ✓ STANDARD（5-8 篇 DiD 范文复现）",
    "**计数模型专用**：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：通用 R3 段落 + IRR 解释",
    "**计数模型 AME + 区域显著性变体**（Han 2024 模式，紧跟 IRR 后）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 R3 + 增加 AME 解释句",
    "**U-shaped / 倒U型专用**（Zhou 2017 模式，内置四拍 + 转折点计算）：": " 🔬 EXPERIMENTAL（1-2 篇范文：Zhou 2017 等）⚠️ 保守替代：通用 R3 段落 + 增加 squared term 解释",
    "**U-shaped + 交互调节变体**（当 U-shaped 被三向交互调节时）：": " 🔬 EXPERIMENTAL（1 篇范文）⚠️ 保守替代：U-shaped 专用 + 增加交互解释",
    # R4
    "**通用填空段落**：": " ✓ STANDARD（12+/28 篇含交互效应范文复现）",
    "**含经济显著性（R5 嵌入）的扩展版**：": " ✓ STANDARD（12+/28 篇含交互效应范文复现）",
    "**简单斜率 / 条件效应专用**：": " ✓ STANDARD（10+/28 篇含交互效应范文复现）",
    "**三向交互专用**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：简单斜率专用 + 增加三维解释",
    "**简单斜率 + 图示专用**：": " ✓ STANDARD（10+/28 篇含交互效应范文复现）",
    "**Johnson-Neyman 专用**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：简单斜率专用",
    "**调节中介（间接调节）专用**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 R4 段落 + 增加中介解释",
    "**非显著间接调节变体**（mediated moderation 中部分路径不显著时）：": " 🔬 EXPERIMENTAL（1 篇范文）⚠️ 保守替代：省略或 inline 报告",
    "**主效应不显著但交互显著变体**（Mannor 2016 模式；禁止跳过主效应）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：R3 通用段落 + 增加交互警告句",
    # R5
    "**通用填空段落**：": " ⭐ PREMIUM（20+/28 篇显著假设报告经济显著性）",
    "**交互效应经济显著性专用**：": " ✓ STANDARD（10+/28 篇含交互效应范文）",
    "**稀有结果/概率变化专用**：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：通用 R5 段落",
    "**U-shaped 经济显著性专用**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 R5 段落 + 转折点解释",
    # R6
    "**通用填空段落**：": " ✓ STANDARD（8-10 篇范文报告非显著/混合发现）",
    "**方向一致但不显著**：": " ✓ STANDARD（5-8 篇范文）",
    "**与预测方向相反**：": " ✓ STANDARD（3-4 篇范文）",
    "**部分支持（混合证据）**：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：方向一致但不显著 + 增加情境解释",
    # R7
    "**测量威胁**：": " ✓ STANDARD（20+/28 篇范文使用）",
    "**模型威胁**：": " ✓ STANDARD（20+/28 篇范文使用）",
    "**样本威胁**：": " ✓ STANDARD（15+/28 篇范文使用）",
    "**时点威胁**：": " ✓ STANDARD（10+/28 篇范文使用）",
    "**内生性威胁**：": " ✓ STANDARD（10+/28 篇范文使用）",
    "**机制/边界威胁**：": " ✓ STANDARD（8-10 篇范文使用）",
    "**DiD 平行趋势专用**：": " ✓ STANDARD（5-8 篇 DiD 范文复现）",
    "**DiD 置换检验专用**：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：省略",
    "**实验排除标准专用**：": " ✓ STANDARD（5-6 篇实验范文复现）",
    "**IV 有效性专用**：": " ✓ STANDARD（3-4 篇 IV 范文复现）",
    "**匹配DiD 重叠支撑专用**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：R7 内生性威胁 + 增加重叠支撑说明",
    "**空间安慰剂检验专用**（DiD / 自然实验）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：R7 内生性威胁 + 增加安慰剂说明",
    "**事件研究稳健性专用**（替代事件日期）：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：R7 时点威胁 + 增加替代日期说明",
    "**市场地位/主导企业固定效应专用**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：R7 样本威胁",
    "**同伴效应/网络效应 falsification 专用**：": " 🔬 EXPERIMENTAL（1 篇范文）⚠️ 保守替代：R7 内生性威胁",
    "**推断二元结果阈值敏感性专用**：": " 🔬 EXPERIMENTAL（1 篇范文）⚠️ 保守替代：R7 测量威胁 + 增加阈值说明",
    # R8
    "**通用填空段落**：": " ✓ STANDARD（8-10 篇范文使用）",
    "**机制检验专用**：": " ✓ STANDARD（8-10 篇含机制检验范文复现）",
    "**替代机制排除专用**（多机制竞争检验）：": " 🔬 EXPERIMENTAL（2-3 篇范文）⚠️ 保守替代：通用 R8 段落 + 增加竞争机制说明",
    "**假设验证 / Corroborating Evidence 专用**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 R8 段落",
    "**MCMC / 模拟中介专用**（当使用贝叶斯模拟检验中介时）：": " 🔬 EXPERIMENTAL（1 篇范文）⚠️ 保守替代：通用 R8 段落 + 增加模拟说明",
    "**辅助方程闭合专用（同时方程）**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 R8 段落",
    # R9
    "**通用填空段落**：": " ✓ STANDARD（15+/28 篇范文使用）",
    "**多研究专用**：": " 🔬 EXPERIMENTAL（1-2 篇范文）⚠️ 保守替代：通用 R9 段落",
}


def add_status_to_file(filepath, status_map, section_name):
    text = filepath.read_text(encoding='utf-8')
    original = text

    for pattern, status in status_map.items():
        # Replace only if the pattern exists and hasn't been modified yet
        if pattern in text and status not in text:
            text = text.replace(pattern, pattern + status, 1)

    if text != original:
        filepath.write_text(text, encoding='utf-8')
        print(f"[{section_name}] Updated {filepath.name}")
    else:
        print(f"[{section_name}] No changes needed or already updated")


if __name__ == "__main__":
    methods_path = Path(r"C:\Users\admin\.claude\skills\write-methods\SKILL.md")
    results_path = Path(r"C:\Users\admin\.claude\skills\write-results\SKILL.md")

    if methods_path.exists():
        add_status_to_file(methods_path, METHODS_STATUS, "write-methods")
    else:
        print(f"[ERROR] {methods_path} not found")

    if results_path.exists():
        add_status_to_file(results_path, RESULTS_STATUS, "write-results")
    else:
        print(f"[ERROR] {results_path} not found")
