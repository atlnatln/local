---
name: scripts-guide
description: Working with the evaluator, design reviewer, and traceability tools in scripts/
---

# scripts-guide

## scripts/ Overview

The `scripts/` directory contains three supporting tools:

| Tool                  | Location                      | Purpose                                                            |
| --------------------- | ----------------------------- | ------------------------------------------------------------------ |
| AIDLC Evaluator       | `scripts/aidlc-evaluator/`    | Automated testing and reporting for AI-DLC workflow changes        |
| AIDLC Design Reviewer | `scripts/aidlc-designreview/` | AI-powered design review of AIDLC artifacts (experimental)         |
| AIDLC Traceability    | `scripts/aidlc-traceability/` | Traceability matrix generation                                     |

## Evaluator

```bash
cd scripts/aidlc-evaluator
uv sync
uv run python run.py test
```

- Multi-package Python workspace (`uv` managed)
- 10 workspace members under `packages/`
- Test cases in `test_cases/`

## Design Reviewer

```bash
cd scripts/aidlc-designreview
uv sync --extra test
source .venv/bin/activate
design-reviewer --aidlc-docs /path/to/aidlc-docs
```

- Multi-agent review (Critique, Alternatives, Gap Analysis)
- Can also be installed as a Claude Code hook via `tool-install/`

## Traceability

```bash
cd scripts/aidlc-traceability
# See local README for setup
```

## When to Use

- **Making rule changes** → run Evaluator to validate
- **Reviewing design artifacts** → run Design Reviewer
- **Need cross-reference mapping** → run Traceability
