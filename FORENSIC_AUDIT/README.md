# FORENSIC_AUDIT

This directory contains automatically-generated audit reports for the XPS
Intelligence Platform repository and all source repositories being consolidated
into it.

**Do not edit any report files manually.** Re-run the corresponding workflow to
regenerate them.

---

## Platform Self-Audit (this repo)

Produced by `_OPS/scripts/repo_self_audit.py` via
`.github/workflows/repo-self-audit.yml`.

| File | Description |
|------|-------------|
| `repo_settings_report.json` | Machine-readable JSON report |
| `repo_settings_report.md` | Human-readable Markdown report |

---

## Source-Repository Forensic Audit (Phase 1–2 consolidation)

Produced by `_OPS/scripts/source_repo_forensic_audit.py` via
`.github/workflows/source-forensic-audit.yml`.

Source repos are defined in `_OPS/scripts/source_repos_manifest.json`.  Each
repo is cloned at a pinned (or latest HEAD) SHA and analysed for file
inventory, tech stack, dependency manifests, and GitHub Actions workflows.

| File | Description |
|------|-------------|
| `sources_index.json` | Machine-readable index across all source repos |
| `sources_index.md` | Human-readable index table |
| `sources/<slug>/forensic_report.json` | Per-repo machine-readable report |
| `sources/<slug>/forensic_report.md` | Per-repo human-readable report |

See [`sources/README.md`](sources/README.md) for the full layout and field
descriptions.
