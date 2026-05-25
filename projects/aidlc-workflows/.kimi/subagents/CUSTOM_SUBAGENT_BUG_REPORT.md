# Bug Report: Custom Subagent Types Cannot Be Launched via Agent Tool

## Environment

- **Kimi CLI version:** 1.44.0
- **OS:** Linux (Ubuntu)
- **Project:** aidlc-workflows (awslabs/aidlc-workflows fork)

## Problem Summary

Custom subagents defined in `agent.yaml` cannot be launched via the `Agent` tool because `AgentTool.__call__` uses `require_builtin_type()`, which only accepts the three hardcoded built-in types (`coder`, `explore`, `plan`).

## Steps to Reproduce

### 1. Define a custom subagent in `.kimi/agent.yaml`

```yaml
version: 1
agent:
  extend: default
  subagents:
    coder:
      path: ./subagents/coder.yaml
      description: "Handle coding tasks"
    reviewer:
      path: ./subagents/reviewer.yaml
      description: "Code review expert"
```

### 2. Create the custom subagent file `.kimi/subagents/reviewer.yaml`

```yaml
version: 1
agent:
  extend: ./agent.yaml
  system_prompt_args:
    ROLE_ADDITIONAL: |
      You are a code review expert. Do not write or edit files.
```

### 3. Attempt to launch the custom subagent

```python
Agent(
    description="Run security review",
    prompt="Review the code for security issues",
    subagent_type="reviewer",
)
```

## Expected Behavior

The `Agent` tool should resolve `reviewer` from the `subagents` definitions in `agent.yaml` and launch it.

## Actual Behavior

```
Failed to run agent: 'Builtin subagent type not found: reviewer'
```

## Root Cause Analysis

In `kimi_cli/tools/agent/__init__.py`, line ~95 (inside `__call__`):

```python
type_def = self._runtime.labor_market.require_builtin_type(actual_type)
```

The `require_builtin_type` method only looks up types in `runtime.labor_market.builtin_types`, which contains only:

- `coder`
- `explore`
- `plan`

Custom subagents defined in `agent.yaml` under the `subagents:` block are **not merged** into `builtin_types`, so the lookup fails with a `KeyError`.

The exception is caught here:

```python
except KeyError as exc:
    return ToolError(message=str(exc), brief="Invalid subagent type")
```

## Evidence from Source Code

### `AgentTool.__call__` (excerpt)

```python
async def __call__(self, params: Params) -> ToolReturnValue:
    # ... validation ...
    runner = ForegroundSubagentRunner(self._runtime)
    req = ForegroundRunRequest(
        description=params.description,
        prompt=params.prompt,
        requested_type=params.subagent_type or "coder",  # <-- "reviewer" passed here
        model=params.model,
        resume=params.resume,
    )
    # ...
    return await runner.run(req)
```

### `ForegroundSubagentRunner.run` (inferred)

The `runner.run(req)` internally calls `require_builtin_type(req.requested_type)`, which raises `KeyError` for any type not in the built-in list.

## Documentation Contradiction

The official Kimi CLI documentation at `docs/en/customization/agents.md` explicitly shows custom subagent definitions:

```yaml
subagents:
  coder:
    path: ./coder-sub.yaml
    description: "Handle coding tasks"
  reviewer:
    path: ./reviewer-sub.yaml
    description: "Code review expert"
```

And states: *"After defining subagents in an agent file, the main agent can launch them via the `Agent` tool."*

However, the `Agent` tool's `subagent_type` parameter is documented as:

> `subagent_type`: **Built-in subagent type**, default `coder`.

This creates a contradiction: documentation says custom subagents can be launched, but the implementation only accepts built-in types.

## Impact

- Users cannot create more than 3 distinct subagent roles.
- The `subagents:` configuration block in `agent.yaml` is effectively limited to overriding the built-in types (`coder`, `explore`, `plan`) rather than adding new ones.
- Workflows requiring 4+ specialized agents (e.g., AIDLC's `analyst`, `architect`, `developer`, `reviewer`) cannot be mapped 1:1 to Kimi CLI subagents.

## Workaround

Map all custom roles onto the 3 built-in types by overriding their `system_prompt_args`:

```yaml
subagents:
  explore:  # Maps to AIDLC Analyst
    path: ./subagents/explore.yaml
    description: "AIDLC analyst: read-only exploration and planning"
  plan:     # Maps to AIDLC Architect
    path: ./subagents/plan.yaml
    description: "AIDLC architect: architecture and infrastructure design"
  coder:    # Maps to AIDLC Developer
    path: ./subagents/coder.yaml
    description: "AIDLC developer: code generation and test execution"
```

The `reviewer` role must be simulated by calling `coder` with a prompt that instructs it to act as a reviewer and not write files.

## Suggested Fix

Modify `AgentTool.__call__` (and the background runner path) to fall back to custom subagent definitions from `agent.yaml` when `require_builtin_type` raises `KeyError`:

```python
# Pseudocode
try:
    type_def = self._runtime.labor_market.require_builtin_type(actual_type)
except KeyError:
    type_def = self._runtime.config.subagents.get(actual_type)
    if type_def is None:
        raise ToolError(message=f"Unknown subagent type: {actual_type}", brief="Invalid subagent type")
```

Or, pre-register custom subagents into `labor_market.builtin_types` during agent initialization so they are indistinguishable from built-ins at runtime.

## Related

- AIDLC RFC #144 (Claude Code Native Implementation) defines a 4-agent model: `analyst`, `architect`, `developer`, `reviewer`.
- Kimi CLI's current 3-agent limitation prevents full AIDLC compliance.
