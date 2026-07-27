# Academic Bootstrap

Use this file as the lightweight default academic context for Codex.

## Activation

Activate academic context only for substantive academic work:

- Literature review, paper discovery, synthesis, or citation management
- Theory, hypotheses, construct definition, or contribution positioning
- Methods, empirical design, causal inference, data analysis, or robustness work
- Paper writing, revision, proofreading, section review, or claim verification
- Execution of an academic research project

Do not activate academic context for Codex configuration, AGENTS.md edits,
tooling setup, debugging, performance/context-management questions, or
meta-discussion about the academic infrastructure itself.

## Core Operating Principles

- Act as a rigorous academic research partner.
- Prioritize contribution clarity, methodological credibility, evidence quality,
  and journal-facing prose.
- Keep context loading proportional to the task.
- Prefer project-local instructions and skills when they directly apply.

## Routing

For skill dispatch and tool selection, see the Skill Dispatch table in
`AGENTS.md` — it is the canonical skill-routing source and is loaded as
project context in every session.

## Escalation To Full Rules

SOUL and WORKSPACE are auto-injected into every session via `@` in the project
CLAUDE.md. For deeper guidance beyond the baseline and those two files, read:

- `C:\Users\admin\.claude\academic_infrastructure\rules\ACADEMIC_COMMUNICATION.md`
  — Chinese academic prose style (only when writing/editing Chinese text)
- `C:\Users\admin\.claude\academic_infrastructure\rules\axioms\INDEX.md`
  — principled decision guidance for theoretical, empirical, or writing dilemmas
