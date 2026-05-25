# Kimi CLI — specs.md AI-DLC Adaptasyonu

This file extends the root `AGENTS.md` with Kimi Code CLI specific guidance for the **specs.md 4-Agent AI-DLC model**.
Kimi CLI automatically merges all `AGENTS.md` files from project root to working directory into `${KIMI_AGENTS_MD}`.

## AI-DLC Framework Overview

This project uses the **AI-Driven Development Life Cycle (AI-DLC)** methodology adapted from the **specs.md 4-Agent Command-Driven model**.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Intent** | High-level statement of purpose (business goal, feature, technical outcome) |
| **Unit** | Cohesive, self-contained work element derived from an Intent |
| **Bolt** | Time-boxed execution session for rapid implementation (hours, not weeks) |
| **Memory Bank** | File-based persistent storage for all project artifacts (`aidlc-docs/`) |
| **Gate** | Human checkpoint where AI pauses for approval before proceeding |

### Three Phases

1. **🔵 Inception** — Capture intents, elaborate requirements, decompose into units and bolts
2. **🟢 Construction** — Execute bolts through validated stages to produce tested code
3. **🟡 Operations** — Deploy, verify, and monitor systems in production

## Agent Architecture

This project implements the specs.md 4-Agent model via Kimi CLI subagents:

```
Master Agent (Orchestrator)
    ├── Inception Agent
    ├── Construction Agent
    └── Operations Agent
```

The **Master Agent** routes requests and maintains project awareness. Specialized agents handle their respective phases.

## Agent Reference

### `master` — Master Agent

**Role:** Orchestrates the overall flow, routes requests, maintains project awareness.

**Commands:**
| Command | Purpose |
|---------|---------|
| `project-init` | Initialize project with standards (tech stack, coding standards, architecture) |
| `analyze-context` | View current project state (active intents, units, bolt stages) |
| `route-request` | Get directed to the right agent based on request |
| `explain-flow` | Learn about AI-DLC methodology |

**When to use:** Always start here. The Master Agent reads `aidlc-docs/aidlc-state.md` to determine current project state and routes to the appropriate specialized agent.

### `inception` — Inception Agent

**Role:** Captures intents, elaborates requirements, decomposes into units and bolts.

**Commands:**
| Command | Purpose |
|---------|---------|
| `intent-create` | Create a new intent from high-level goal |
| `requirements` | Elaborate functional and non-functional requirements |
| `units` | Decompose intent into loosely coupled units |
| `story-create` | Create user stories for a unit |
| `bolt-plan` | Plan bolts (DDD/TDD/BDD/Simple) for stories |
| `review` | Review all inception artifacts |

**4 Gates:** Gate 1 (questions) → Gate 2 (requirements) → Gate 3 (all artifacts) → Gate 4 (ready for construction)

**When to use:** New features, requirements gathering, architecture planning.

### `construction` — Construction Agent

**Role:** Executes bolts through validated stages to produce tested code.

**Commands:**
| Command | Purpose |
|---------|---------|
| `bolt-start` | Start or continue executing a bolt |
| `bolt-status` | Check bolt progress |
| `bolt-list` | List all bolts |
| `bolt-replan` | Replan bolts if scope changes |

**Bolt Types:**
- **DDD Construction** (5 stages): Domain Model → Technical Design → ADR → Implement → Test
- **TDD Construction** (3 stages): Test → Implement → Refactor
- **BDD Construction** (3 stages): Scenario → Implement → Verify
- **Simple Construction** (3 stages): Spec → Implement → Test

**When to use:** Code generation, implementation, testing.

### `operations` — Operations Agent

**Role:** Deploys, verifies, and monitors systems in production.

**Commands:**
| Command | Purpose |
|---------|---------|
| `build` | Build deployment units (containers, serverless, artifacts) |
| `deploy` | Deploy to environment (staging → production) |
| `verify` | Verify deployment (smoke tests, health checks, security scan) |
| `monitor` | Set up observability stack and analyze telemetry |

**When to use:** Deployment, infrastructure setup, monitoring.

## Tool Usage Preferences

- **Agent tool**: Use `master` to start. The Master Agent routes to `inception`, `construction`, or `operations` as needed.
  > **Note:** These are custom subagents defined in `.kimi/agent.yaml`. Built-in `coder`, `explore`, `plan` are overridden.
- **SetTodoList**: Use this tool to track multi-step tasks and milestones.
- **EnterPlanMode / ExitPlanMode**: Use for significant architectural changes, new features, or when there is meaningful ambiguity.

## Memory Bank Structure

All artifacts are persisted in `aidlc-docs/` (Memory Bank):

```
aidlc-docs/
├── aidlc-state.md          # Project state tracking
├── audit.md                # Audit trail (timestamped interactions)
├── standards.md            # Tech stack, coding standards, architecture
├── inception/              # 🔵 INCEPTION PHASE
│   ├── intents/
│   ├── requirements/
│   ├── context/
│   ├── units/
│   ├── stories/
│   └── bolt-plans/
├── construction/           # 🟢 CONSTRUCTION PHASE
│   ├── {unit-name}/
│   │   └── bolts/
│   │       ├── {bolt-name}/
│   │       │   ├── domain-model.md
│   │       │   ├── technical-design.md
│   │       │   ├── adr-001.md
│   │       │   ├── implementation/
│   │       │   └── tests/
│   └── build-and-test/
└── operations/             # 🟡 OPERATIONS PHASE
    ├── deployment-guide.md
    ├── verification-report.md
    ├── monitoring-setup.md
    └── runbooks/
```

## Subagent Invocation Examples

**Start a new project:**
```text
Agent(description="Initialize project", subagent_type="master", prompt="project-init")
```

**Create a new intent:**
```text
Agent(description="Create intent", subagent_type="inception", prompt="intent-create: I want to build a user authentication system")
```

**Start a bolt:**
```text
Agent(description="Start bolt", subagent_type="construction", prompt="bolt-start")
```

**Deploy to production:**
```text
Agent(description="Deploy system", subagent_type="operations", prompt="deploy production")
```

## Project Skills

The following project-level skills are available under `.kimi/skills/`:

| Skill | Purpose |
|-------|---------|
| `pr-conventions` | Pull request contributor statement and template rules |
| `aidlc-rules` | How to write and update AI-DLC workflow rules |
| `security-scans` | Running and interpreting the ${DEFAULT_SCANNER_SET} locally |
| `markdown-style` | Project markdown style and lint rules |
| `scripts-guide` | Working with evaluator, design-reviewer, and traceability tools |

Invoke a skill manually with `/skill:<name>` or let the Agent decide based on context.

## PR Attribution

When creating pull requests, the PR body MUST end with:

> By submitting this pull request, I confirm that you can use, modify, copy,
> and redistribute this contribution, under the terms of the
> [project license](https://github.com/awslabs/aidlc-workflows/blob/main/LICENSE).

This is enforced by CI; without it the `Require Contributor Statement` check will fail.
