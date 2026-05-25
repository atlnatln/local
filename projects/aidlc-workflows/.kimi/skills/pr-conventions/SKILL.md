---
name: pr-conventions
description: Pull request conventions and contributor statement requirements for aidlc-workflows
---

# pr-conventions

## Pull Request Conventions

When creating pull requests in this repository, always include the following in
the PR body:

1. Use the structure from `.github/pull_request_template.md`
2. The PR description MUST end with this contributor statement (required by CI):

```text
By submitting this pull request, I confirm that you can use, modify, copy, and redistribute this contribution, under the terms of the [project license](https://github.com/awslabs/aidlc-workflows/blob/main/LICENSE).
```

Without this statement, the `Require Contributor Statement` CI check will fail.

## PR Title Format

PR titles must follow [Conventional Commits](https://www.conventionalcommits.org/)
(e.g., `feat:`, `fix:`, `docs:`, `chore:`). This is enforced by the
`pull-request-lint.yml` workflow.
