# FORENSIC_AUDIT/sources

This directory contains the automatically-generated forensic audit reports for
each **source repository** that will be consolidated into the XPS Intelligence
Platform.

Reports are produced by `_OPS/scripts/source_repo_forensic_audit.py` and
committed by the `.github/workflows/source-forensic-audit.yml` workflow.

---

## Index

The top-level index files summarise all audited repos:

| File | Description |
|------|-------------|
| [`../sources_index.json`](../sources_index.json) | Machine-readable index (JSON) |
| [`../sources_index.md`](../sources_index.md) | Human-readable index (Markdown) |

---

## Per-Repository Reports

Each source repository has its own sub-directory:

```
sources/
├── xps-intelligence-system/
│   ├── forensic_report.json   ← machine-readable
│   └── forensic_report.md     ← human-readable
├── xps-intelligence-frontend/
│   ├── forensic_report.json
│   └── forensic_report.md
├── quantum-x-build/
│   ├── forensic_report.json
│   └── forensic_report.md
├── vizual-x-admin-control-plane/
│   ├── forensic_report.json
│   └── forensic_report.md
└── construct-iq-360/
    ├── forensic_report.json
    └── forensic_report.md
```

Each report contains:

| Section | Description |
|---------|-------------|
| SHA Resolution | The exact commit SHA analysed (pinned or latest HEAD) |
| GitHub Metadata | Repository metadata (language, size, topics, etc.) |
| Clone Status | Whether the shallow clone at the pinned SHA succeeded |
| File Inventory | Total file count + size breakdown by extension |
| Tech Stack | Heuristic detection of frameworks and tools |
| GitHub Actions Workflows | List of workflow files in the source repo |
| Key Project Files | Contents of README, package.json, pyproject.toml, etc. |

---

## SHA Pinning

Source repos are defined in `_OPS/scripts/source_repos_manifest.json`.  
Set a `"pin_sha"` to lock analysis to a specific commit for reproducibility.  
Leave `"pin_sha": null` to always analyse the latest default-branch HEAD.

---

**Do not edit the report files manually.** Re-run the
`.github/workflows/source-forensic-audit.yml` workflow to regenerate them.
