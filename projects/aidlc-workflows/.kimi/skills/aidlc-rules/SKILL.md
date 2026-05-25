---
name: aidlc-rules
description: Guidelines for writing and updating AI-DLC workflow rules in aidlc-rules/
---

# aidlc-rules

## Working with aidlc-rules/

The `aidlc-rules/` directory contains the distributable product of this
repository. It is zipped and published via GitHub Releases.

### Structure

```text
aidlc-rules/
├── aws-aidlc-rules/          # Core workflow entry point (DO NOT rename)
│   └── core-workflow.md
└── aws-aidlc-rule-details/   # Detailed rules (DO NOT rename)
    ├── common/
    ├── inception/
    ├── construction/
    ├── extensions/
    └── operations/
```

### Rules

- Do **not** rename, move, or reorganize `aws-aidlc-rules/` or
  `aws-aidlc-rule-details/` — they are part of the public contract.
- Do **not** duplicate content across rules. Place shared guidance in
  `common/` and reference it.
- Keep the core methodology IDE/agent/model agnostic.
- When adding or updating rules, test with at least one supported platform
  (Kiro, Amazon Q, Cursor, Cline, Claude Code, GitHub Copilot) before
  submitting.
- Run `npx markdownlint-cli2 "**/*.md"` before committing.

### Extensions

Extensions live under `aws-aidlc-rule-details/extensions/` and consist of:

- A **rules file** (e.g., `security-baseline.md`)
- An **opt-in file** (e.g., `security-baseline.opt-in.md`)

Rules are blocking by default — if verification criteria are not met, the
stage cannot proceed.
