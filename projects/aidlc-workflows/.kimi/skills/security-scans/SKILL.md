---
name: security-scans
description: Running and interpreting the 6 security scanners for aidlc-workflows
---

# security-scans

## Security Scanners

Six scanners run on every push to `main`, every PR, and daily. All HIGH and
CRITICAL findings must be remediated or have documented risk acceptance before
merge.

| Scanner  | Detects                | Fails on                    | Config                                      |
| -------- | ---------------------- | --------------------------- | ------------------------------------------- |
| Bandit   | Python SAST issues     | High confidence findings    | `.bandit`                                   |
| Semgrep  | Multi-language SAST    | Any finding (PRs: new only) | `.semgrepignore`                            |
| Grype    | Dependency CVEs        | High/critical CVEs          | `.grype.yaml`                               |
| Gitleaks | Secrets in git history | Any non-baselined secret    | `.gitleaks.toml`, `.gitleaks-baseline.json` |
| Checkov  | IaC misconfigurations  | Any check failure           | `.checkov.yaml`                             |
| ClamAV   | Malware                | Any detection               | None                                        |

## Local Execution

### Quick (Docker recommended)

```bash
# Grype
docker run --rm -v "$PWD:/workspace" anchore/grype:latest grype dir:/workspace -o sarif=grype.sarif

# Gitleaks
docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest detect --source /repo --report-format sarif --report-path gitleaks.sarif

# Semgrep
docker run --rm -v "$PWD:/src" returntocorp/semgrep semgrep --config=r/all --sarif /src > semgrep.sarif

# Checkov
docker run --rm -v "$PWD:/src" bridgecrew/checkov --directory /src --output-file-path checkov.sarif --output sarif

# Bandit
docker run --rm -v "$PWD:/src" python:3.12-slim bash -c "pip install -q bandit && bandit -r /src -f sarif -o /src/bandit.sarif"

# ClamAV
docker run --rm -v "$PWD:/data" mkodockx/docker-clamav clamscan -r /data --log=/data/clamdscan.txt
```

### Inline Suppression Patterns

- Bandit: `# nosec BXXX — justification`
- Semgrep: `# nosemgrep: rule-id — justification`
- Checkov: `# checkov:skip=CKV_ID:justification`

For full remediation details, see
[docs/DEVELOPERS_GUIDE.md](docs/DEVELOPERS_GUIDE.md#security-scanners).
