#!/usr/bin/env python3
"""
source_repo_forensic_audit.py — Source-repository forensic audit tool.

For each repository listed in ``source_repos_manifest.json`` this script:
  1. Resolves the commit SHA to use (from the manifest ``pin_sha`` field, or
     the current default-branch HEAD via the GitHub API).
  2. Clones the repository at exactly that SHA (shallow, single-commit clone).
  3. Walks the working tree to build a full file inventory.
  4. Reads key project files (README, dependency manifests, workflow YAML, etc.).
  5. Produces two reports per repository under ``FORENSIC_AUDIT/sources/<slug>/``:
       - ``forensic_report.json``  — machine-readable
       - ``forensic_report.md``   — human-readable

Defensive: any step that fails (network error, missing permission, private repo
without a valid token) is recorded as "unavailable" and never causes a non-zero
exit.  The script only exits non-zero for programming errors or missing required
environment variables.

SECURITY:
  - The GITHUB_TOKEN is only ever passed to ``git`` via the git credential
    helper mechanism (``GIT_ASKPASS``).  It is never written to disk, logged,
    or included in any report output.
  - File *contents* included in reports are limited to well-known plain-text
    configuration/documentation files (see KEY_FILES list).
  - Binary files and files larger than MAX_FILE_BYTES are skipped.

Required environment variables:
  GITHUB_TOKEN      — Personal Access Token or Actions GITHUB_TOKEN
  GITHUB_REPOSITORY — "owner/repo" of the *platform* repo (used only for
                      constructing absolute report paths in log messages)

Optional:
  AUDIT_OUTPUT_DIR  — root output directory (default: FORENSIC_AUDIT)
  MANIFEST_PATH     — path to manifest JSON
                      (default: _OPS/scripts/source_repos_manifest.json)
  CLONE_BASE_DIR    — temp directory for clones (default: /tmp/forensic_clones)
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")
AUDIT_OUTPUT_DIR = os.environ.get("AUDIT_OUTPUT_DIR", "FORENSIC_AUDIT")
MANIFEST_PATH = os.environ.get(
    "MANIFEST_PATH", "_OPS/scripts/source_repos_manifest.json"
)
CLONE_BASE_DIR = os.environ.get("CLONE_BASE_DIR", "")

API_BASE = "https://api.github.com"

# Maximum size (bytes) for a single file read into the report
MAX_FILE_BYTES = 64 * 1024  # 64 KB

# Well-known files whose *full text* is captured in the report
KEY_FILES = [
    "README.md",
    "README.rst",
    "README.txt",
    "CHANGELOG.md",
    "CHANGELOG.rst",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-test.txt",
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "composer.json",
    "Gemfile",
    "Gemfile.lock",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
    ".env.sample",
    "railway.json",
    "railway.toml",
    "Procfile",
]


def die(msg: str) -> None:
    print(f"FATAL: {msg}", file=sys.stderr)
    sys.exit(1)


if not GITHUB_TOKEN:
    die("GITHUB_TOKEN environment variable is not set.")

# ---------------------------------------------------------------------------
# HTTP helper (GitHub REST API — read-only)
# ---------------------------------------------------------------------------


def gh_get(path: str) -> object:
    """
    Perform a GET request against the GitHub REST API.

    Returns parsed JSON on success, or the string "unavailable" on any
    HTTP / network error.  Never raises.
    """
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "source-repo-forensic-audit/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError:
        return "unavailable"
    except Exception:
        return "unavailable"


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _git_env() -> dict:
    """
    Return an env dict for subprocess git calls that injects the GITHUB_TOKEN
    via GIT_ASKPASS so it never appears in command arguments or logs.
    """
    askpass_script = tempfile.NamedTemporaryFile(
        mode="w", suffix=".sh", delete=False, prefix="git_askpass_"
    )
    # The script prints the token when git asks for a password.
    # Username prompt is answered with "x-access-token".
    askpass_script.write(
        "#!/bin/sh\n"
        "case \"$1\" in\n"
        "  *Username*) echo 'x-access-token' ;;\n"
        f"  *Password*) echo '{GITHUB_TOKEN}' ;;\n"
        "esac\n"
    )
    askpass_script.flush()
    os.chmod(askpass_script.name, 0o700)
    askpass_script.close()

    env = os.environ.copy()
    env["GIT_ASKPASS"] = askpass_script.name
    env["GIT_TERMINAL_PROMPT"] = "0"
    # Remove any SSH_AUTH_SOCK to force HTTPS
    env.pop("SSH_AUTH_SOCK", None)
    return env, askpass_script.name


def clone_at_sha(owner: str, repo: str, sha: str, dest: Path) -> tuple[bool, str]:
    """
    Clone ``owner/repo`` into ``dest`` and check out ``sha``.

    Performs a shallow clone of the default branch, then fetches the exact
    commit if needed (handles cases where the SHA is not the branch tip).

    Returns ``(success: bool, message: str)``.
    """
    clone_url = f"https://github.com/{owner}/{repo}.git"
    env, askpass_path = _git_env()

    try:
        # Shallow clone — only fetch the branch tip first
        result = subprocess.run(
            ["git", "clone", "--depth=1", "--no-tags", clone_url, str(dest)],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if result.returncode != 0:
            return False, f"git clone failed: {result.stderr.strip()[:500]}"

        # Check whether the target SHA is already checked out
        head_result = subprocess.run(
            ["git", "-C", str(dest), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        current_sha = head_result.stdout.strip()

        if current_sha != sha:
            # Fetch the specific commit (not all commits — GitHub supports
            # fetching a single object by SHA)
            fetch_result = subprocess.run(
                ["git", "-C", str(dest), "fetch", "--depth=1", "origin", sha],
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
            )
            if fetch_result.returncode != 0:
                # If GitHub doesn't allow fetching by SHA directly, fall back
                # to a full unshallow fetch then checkout
                subprocess.run(
                    ["git", "-C", str(dest), "fetch", "--unshallow", "origin"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    env=env,
                )

            checkout_result = subprocess.run(
                ["git", "-C", str(dest), "checkout", sha, "--detach"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if checkout_result.returncode != 0:
                return (
                    False,
                    f"git checkout {sha[:12]} failed: "
                    f"{checkout_result.stderr.strip()[:500]}",
                )

        return True, f"Cloned at {sha[:12]}"
    except subprocess.TimeoutExpired:
        return False, "git operation timed out"
    except Exception as exc:
        return False, str(exc)
    finally:
        try:
            os.unlink(askpass_path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Repository analysis helpers
# ---------------------------------------------------------------------------


def resolve_sha(owner: str, repo: str, pin_sha: str | None) -> tuple[str | None, str]:
    """
    Resolve the commit SHA to analyse.

    If ``pin_sha`` is set, return it as-is.
    Otherwise, fetch the latest SHA from the default branch via the API.

    Returns ``(sha_or_None, resolution_note)``.
    """
    if pin_sha:
        return pin_sha, f"pinned in manifest ({pin_sha[:12]})"

    data = gh_get(f"/repos/{owner}/{repo}")
    if data == "unavailable":
        return None, "could not resolve — API returned unavailable"

    default_branch = data.get("default_branch", "main")
    branch_data = gh_get(
        f"/repos/{owner}/{repo}/branches/{default_branch}"
    )
    if branch_data == "unavailable":
        return None, f"could not resolve — branch {default_branch!r} unavailable"

    sha = (branch_data.get("commit") or {}).get("sha")
    if not sha:
        return None, "could not resolve — no commit SHA in branch data"

    return sha, f"latest HEAD of {default_branch!r} ({sha[:12]})"


def collect_repo_metadata(owner: str, repo: str) -> dict:
    """Fetch high-level repository metadata from the GitHub API."""
    data = gh_get(f"/repos/{owner}/{repo}")
    if data == "unavailable":
        return {"status": "unavailable"}
    return {
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "default_branch": data.get("default_branch"),
        "visibility": data.get("visibility"),
        "archived": data.get("archived"),
        "fork": data.get("fork"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "pushed_at": data.get("pushed_at"),
        "stargazers_count": data.get("stargazers_count"),
        "forks_count": data.get("forks_count"),
        "open_issues_count": data.get("open_issues_count"),
        "language": data.get("language"),
        "topics": data.get("topics", []),
        "homepage": data.get("homepage"),
        "license": (data.get("license") or {}).get("spdx_id"),
        "has_issues": data.get("has_issues"),
        "has_wiki": data.get("has_wiki"),
        "has_pages": data.get("has_pages"),
        "size_kb": data.get("size"),
    }


def build_file_inventory(clone_dir: Path) -> dict:
    """
    Walk the cloned directory tree and produce a file inventory.

    Returns:
      {
        "total_files": int,
        "total_size_bytes": int,
        "by_extension": {"py": count, ...},
        "directories": [list of non-empty dir paths],
        "files": [{"path": str, "size_bytes": int}, ...]  # top 500 by size
      }
    """
    files = []
    ext_counts: dict[str, int] = {}
    dirs: set[str] = set()
    total_size = 0

    git_dir = clone_dir / ".git"

    for item in clone_dir.rglob("*"):
        # Skip .git internals
        try:
            item.relative_to(git_dir)
            continue
        except ValueError:
            pass

        if item.is_dir():
            rel = str(item.relative_to(clone_dir))
            if rel != ".":
                dirs.add(rel)
            continue

        if not item.is_file():
            continue

        rel_path = str(item.relative_to(clone_dir))
        try:
            size = item.stat().st_size
        except OSError:
            continue

        total_size += size
        ext = item.suffix.lstrip(".").lower() or "_no_ext"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        files.append({"path": rel_path, "size_bytes": size})

    # Sort largest first, keep top 500 for the report
    files.sort(key=lambda f: f["size_bytes"], reverse=True)

    return {
        "total_files": len(files),
        "total_size_bytes": total_size,
        "by_extension": dict(sorted(ext_counts.items(), key=lambda x: -x[1])),
        "top_directories": sorted(dirs)[:200],
        "files": files[:500],
    }


def read_key_files(clone_dir: Path) -> dict:
    """
    Read the content of well-known project files from the cloned repo.

    Only reads files listed in KEY_FILES and only at the root or in common
    subdirectories.  Truncates files larger than MAX_FILE_BYTES.

    Returns a dict keyed by relative file path.
    """
    results = {}
    search_dirs = [
        clone_dir,
        clone_dir / "apps" / "backend",
        clone_dir / "apps" / "frontend",
        clone_dir / "backend",
        clone_dir / "frontend",
        clone_dir / "src",
    ]

    for d in search_dirs:
        if not d.is_dir():
            continue
        prefix = str(d.relative_to(clone_dir)) if d != clone_dir else ""
        for fname in KEY_FILES:
            fpath = d / fname
            if not fpath.is_file():
                continue
            rel = str(fpath.relative_to(clone_dir))
            if rel in results:
                continue
            try:
                size = fpath.stat().st_size
                if size > MAX_FILE_BYTES:
                    results[rel] = (
                        f"[truncated — file is {size:,} bytes; "
                        f"showing first {MAX_FILE_BYTES:,} bytes]\n"
                        + fpath.read_text(encoding="utf-8", errors="replace")[
                            :MAX_FILE_BYTES
                        ]
                    )
                else:
                    results[rel] = fpath.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                results[rel] = f"[read error: {exc}]"

    return results


def collect_workflow_list(clone_dir: Path) -> list[dict]:
    """List GitHub Actions workflow files found in the cloned repo."""
    workflows_dir = clone_dir / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return []
    result = []
    for f in sorted(workflows_dir.iterdir()):
        if f.is_file() and f.suffix in (".yml", ".yaml"):
            result.append({"name": f.name, "size_bytes": f.stat().st_size})
    return result


def detect_tech_stack(file_inventory: dict, key_files: dict) -> dict:
    """
    Heuristically detect the technology stack from the file inventory and key
    files.

    Returns a dict of detected technologies and their evidence.
    """
    detected = {}
    paths = {f["path"] for f in file_inventory.get("files", [])}
    ext_counts = file_inventory.get("by_extension", {})

    # Python
    py_files = ext_counts.get("py", 0)
    if py_files > 0 or any(
        k in key_files
        for k in ("pyproject.toml", "setup.py", "setup.cfg", "requirements.txt")
    ):
        detected["python"] = {"file_count": py_files}

    # Node / JavaScript / TypeScript
    js_files = ext_counts.get("js", 0) + ext_counts.get("jsx", 0)
    ts_files = ext_counts.get("ts", 0) + ext_counts.get("tsx", 0)
    if js_files + ts_files > 0 or "package.json" in key_files:
        detected["nodejs_or_js"] = {
            "js_files": js_files,
            "ts_files": ts_files,
            "has_package_json": "package.json" in key_files,
        }

    # Next.js
    if any("next.config" in p for p in paths):
        detected["nextjs"] = True

    # FastAPI / Flask / Django
    for framework in ("fastapi", "flask", "django"):
        if any(
            framework in (key_files.get(k) or "").lower()
            for k in ("requirements.txt", "pyproject.toml", "setup.py", "setup.cfg")
        ):
            detected[framework] = True

    # Docker
    if "Dockerfile" in key_files or any(
        "Dockerfile" in p for p in paths
    ):
        detected["docker"] = {
            "has_dockerfile": "Dockerfile" in key_files,
            "has_compose": any(
                p in key_files
                for p in ("docker-compose.yml", "docker-compose.yaml")
            ),
        }

    # Go
    if ext_counts.get("go", 0) > 0 or "go.mod" in key_files:
        detected["go"] = {"file_count": ext_counts.get("go", 0)}

    # GitHub Actions
    workflow_count = ext_counts.get("yml", 0) + ext_counts.get("yaml", 0)
    if any(".github/workflows" in p for p in paths):
        detected["github_actions"] = {"workflow_files_detected": True}

    return detected


# ---------------------------------------------------------------------------
# Per-repo audit orchestration
# ---------------------------------------------------------------------------


def audit_one_repo(entry: dict, clone_base: Path, output_dir: Path) -> dict:
    """
    Run the full forensic audit for one source repository entry.

    Returns a complete report dict.
    """
    owner = entry["owner"]
    repo = entry["repo"]
    pin_sha = entry.get("pin_sha")
    slug = repo.lower().replace("_", "-").replace(" ", "-")
    repo_output_dir = output_dir / slug
    repo_output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[forensic] ── Auditing {owner}/{repo} ──")

    report: dict = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "owner": owner,
            "repo": repo,
            "phase": entry.get("phase"),
            "role": entry.get("role"),
            "note": entry.get("note"),
        },
        "sha_resolution": {},
        "github_metadata": {},
        "clone_status": {},
        "file_inventory": {},
        "key_files": {},
        "workflow_list": [],
        "tech_stack": {},
    }

    # ── 1. Resolve SHA ──────────────────────────────────────────────────────
    sha, sha_note = resolve_sha(owner, repo, pin_sha)
    report["sha_resolution"] = {
        "sha": sha,
        "note": sha_note,
        "was_pinned": bool(pin_sha),
    }
    if sha:
        print(f"[forensic]   SHA: {sha_note}")
    else:
        print(f"[forensic]   SHA resolution failed: {sha_note}")

    # ── 2. GitHub API metadata ──────────────────────────────────────────────
    print(f"[forensic]   Fetching GitHub metadata …")
    report["github_metadata"] = collect_repo_metadata(owner, repo)

    if sha is None:
        report["clone_status"] = {
            "success": False,
            "message": f"SHA could not be resolved: {sha_note}",
        }
        _write_reports(report, repo_output_dir)
        return report

    # ── 3. Clone ─────────────────────────────────────────────────────────────
    clone_dir = clone_base / slug
    if clone_dir.exists():
        shutil.rmtree(clone_dir)

    print(f"[forensic]   Cloning at {sha[:12]} …")
    success, message = clone_at_sha(owner, repo, sha, clone_dir)
    report["clone_status"] = {"success": success, "message": message}

    if not success:
        print(f"[forensic]   Clone failed: {message}")
        _write_reports(report, repo_output_dir)
        return report

    print(f"[forensic]   Clone succeeded.")

    # ── 4. File inventory ────────────────────────────────────────────────────
    print(f"[forensic]   Building file inventory …")
    report["file_inventory"] = build_file_inventory(clone_dir)

    # ── 5. Key file contents ─────────────────────────────────────────────────
    print(f"[forensic]   Reading key files …")
    report["key_files"] = read_key_files(clone_dir)

    # ── 6. Workflow list ─────────────────────────────────────────────────────
    report["workflow_list"] = collect_workflow_list(clone_dir)

    # ── 7. Tech stack detection ──────────────────────────────────────────────
    report["tech_stack"] = detect_tech_stack(
        report["file_inventory"], report["key_files"]
    )

    # ── 8. Clean up clone ────────────────────────────────────────────────────
    try:
        shutil.rmtree(clone_dir)
    except OSError:
        pass

    _write_reports(report, repo_output_dir)

    n_files = report["file_inventory"].get("total_files", 0)
    size_kb = report["file_inventory"].get("total_size_bytes", 0) // 1024
    print(
        f"[forensic]   Done — {n_files} files, {size_kb} KB, "
        f"tech: {list(report['tech_stack'].keys())}"
    )
    return report


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------


def _write_reports(report: dict, out_dir: Path) -> None:
    """Write JSON and Markdown reports for a single repo audit."""
    # JSON
    json_path = out_dir / "forensic_report.json"
    json_path.write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )
    print(f"[forensic]   Written: {json_path}")

    # Markdown
    md_path = out_dir / "forensic_report.md"
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"[forensic]   Written: {md_path}")


_UA = "unavailable"


def _md_val(val) -> str:
    if val is None:
        return "_not set_"
    if val == _UA:
        return "⚠️ unavailable"
    if val is True:
        return "✅ yes"
    if val is False:
        return "❌ no"
    return str(val)


def render_markdown(report: dict) -> str:  # noqa: C901
    src = report.get("source", {})
    owner = src.get("owner", "unknown")
    repo_name = src.get("repo", "unknown")
    ts = report.get("generated_at", "unknown")
    sha_res = report.get("sha_resolution", {})
    meta = report.get("github_metadata", {})
    clone = report.get("clone_status", {})
    inv = report.get("file_inventory", {})
    key_files = report.get("key_files", {})
    workflows = report.get("workflow_list", [])
    tech = report.get("tech_stack", {})

    sha = sha_res.get("sha") or "unresolved"
    sha_display = sha[:12] if len(sha) >= 12 else sha

    lines = [
        f"# Forensic Audit Report — `{owner}/{repo_name}`",
        "",
        f"**Generated:** {ts}  ",
        f"**Phase:** {src.get('phase', '_unknown_')}  ",
        f"**Role:** {src.get('role', '_unknown_')}  ",
        f"**Note:** {src.get('note', '')}  ",
        "",
        "---",
        "",
        "## SHA Resolution",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Commit SHA | `{sha}` |",
        f"| Short SHA | `{sha_display}` |",
        f"| Was pinned | {_md_val(sha_res.get('was_pinned'))} |",
        f"| Note | {sha_res.get('note', '')} |",
        "",
        "---",
        "",
        "## GitHub Metadata",
        "",
    ]

    if meta.get("status") == _UA or not meta:
        lines.append("⚠️ Metadata unavailable.")
    else:
        lines += [
            f"| Field | Value |",
            f"|-------|-------|",
            f"| Full name | `{meta.get('full_name', '_unknown_')}` |",
            f"| Description | {meta.get('description') or '_none_'} |",
            f"| Default branch | `{meta.get('default_branch', '_unknown_')}` |",
            f"| Visibility | {meta.get('visibility', '_unknown_')} |",
            f"| Archived | {_md_val(meta.get('archived'))} |",
            f"| Fork | {_md_val(meta.get('fork'))} |",
            f"| Language | {meta.get('language') or '_none_'} |",
            f"| License | {meta.get('license') or '_none_'} |",
            f"| Size | {meta.get('size_kb', 0):,} KB |",
            f"| Stars | {meta.get('stargazers_count', 0)} |",
            f"| Forks | {meta.get('forks_count', 0)} |",
            f"| Open Issues | {meta.get('open_issues_count', 0)} |",
            f"| Created | {meta.get('created_at', '')} |",
            f"| Last push | {meta.get('pushed_at', '')} |",
        ]
        topics = meta.get("topics", [])
        if topics:
            lines.append(f"| Topics | {', '.join(topics)} |")

    lines += [
        "",
        "---",
        "",
        "## Clone Status",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Success | {_md_val(clone.get('success'))} |",
        f"| Message | {clone.get('message', '')} |",
        "",
        "---",
        "",
        "## File Inventory",
        "",
    ]

    if not inv:
        lines.append("_(clone did not succeed — no inventory)_")
    else:
        total_files = inv.get("total_files", 0)
        total_size = inv.get("total_size_bytes", 0)
        lines += [
            f"**Total files:** {total_files:,}  ",
            f"**Total size:** {total_size / 1024:.1f} KB",
            "",
            "### Files by Extension",
            "",
            "| Extension | Count |",
            "|-----------|-------|",
        ]
        by_ext = inv.get("by_extension", {})
        for ext, count in list(by_ext.items())[:30]:
            lines.append(f"| `.{ext}` | {count} |")

        dirs = inv.get("top_directories", [])
        if dirs:
            lines += [
                "",
                "### Top-Level Directory Structure",
                "",
                "```",
            ]
            # Show only depth-1 directories
            depth1 = sorted(
                {d.split("/")[0] for d in dirs if d and "/" not in d}
            )
            for d in depth1:
                lines.append(f"{d}/")
            lines.append("```")

    lines += [
        "",
        "---",
        "",
        "## Tech Stack",
        "",
    ]

    if not tech:
        lines.append("_(no stack detected or clone failed)_")
    else:
        lines += [
            "| Technology | Details |",
            "|------------|---------|",
        ]
        for name, detail in tech.items():
            if isinstance(detail, dict):
                detail_str = ", ".join(f"{k}={v}" for k, v in detail.items())
            else:
                detail_str = str(detail)
            lines.append(f"| {name} | {detail_str} |")

    lines += [
        "",
        "---",
        "",
        "## GitHub Actions Workflows",
        "",
    ]

    if not workflows:
        lines.append("_(none found or clone failed)_")
    else:
        lines += [
            "| Workflow File | Size |",
            "|---------------|------|",
        ]
        for wf in workflows:
            lines.append(f"| `{wf['name']}` | {wf['size_bytes']:,} B |")

    lines += [
        "",
        "---",
        "",
        "## Key Project Files",
        "",
    ]

    if not key_files:
        lines.append("_(none found or clone failed)_")
    else:
        for rel_path, content in key_files.items():
            ext = Path(rel_path).suffix.lstrip(".") or "text"
            lines += [
                f"### `{rel_path}`",
                "",
                f"```{ext}",
                content.rstrip("\n"),
                "```",
                "",
            ]

    lines += [
        "---",
        "",
        "_Report generated automatically by "
        "`_OPS/scripts/source_repo_forensic_audit.py`.  "
        "Do not edit manually — re-run the workflow to regenerate._",
    ]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Index report (across all repos)
# ---------------------------------------------------------------------------


def write_index(reports: list[dict], output_dir: Path) -> None:
    """Write a combined index JSON + Markdown summarising all repo audits."""
    ts = datetime.now(timezone.utc).isoformat()

    index = {
        "schema_version": "1.0",
        "generated_at": ts,
        "source_count": len(reports),
        "sources": [
            {
                "owner": r["source"]["owner"],
                "repo": r["source"]["repo"],
                "phase": r["source"].get("phase"),
                "role": r["source"].get("role"),
                "sha": r["sha_resolution"].get("sha"),
                "sha_pinned": r["sha_resolution"].get("was_pinned"),
                "clone_success": r["clone_status"].get("success"),
                "total_files": r["file_inventory"].get("total_files"),
                "total_size_kb": (
                    r["file_inventory"].get("total_size_bytes", 0) // 1024
                ),
                "tech_stack": list(r.get("tech_stack", {}).keys()),
                "report_path": (
                    f"sources/"
                    f"{r['source']['repo'].lower().replace('_', '-').replace(' ', '-')}"
                    f"/forensic_report.md"
                ),
            }
            for r in reports
        ],
    }

    (output_dir / "sources_index.json").write_text(
        json.dumps(index, indent=2, default=str), encoding="utf-8"
    )

    lines = [
        "# Source Repository Forensic Audit — Index",
        "",
        f"**Generated:** {ts}  ",
        f"**Total source repos audited:** {len(reports)}",
        "",
        "---",
        "",
        "| Phase | Repo | SHA (short) | Clone | Files | Size | Stack |",
        "|-------|------|-------------|-------|-------|------|-------|",
    ]

    for s in index["sources"]:
        sha = s.get("sha") or "unresolved"
        sha_display = sha[:12] if len(sha) >= 12 else sha
        clone_ok = "✅" if s.get("clone_success") else "❌"
        files = f"{s.get('total_files', 0):,}" if s.get("total_files") is not None else "—"
        size = f"{s.get('total_size_kb', 0):,} KB"
        stack = ", ".join(s.get("tech_stack", []))
        report_link = f"[report]({s['report_path']})"
        lines.append(
            f"| {s.get('phase','?')} "
            f"| `{s['repo']}` {report_link} "
            f"| `{sha_display}` "
            f"| {clone_ok} "
            f"| {files} "
            f"| {size} "
            f"| {stack} |"
        )

    lines += [
        "",
        "---",
        "",
        "_Index auto-generated by `_OPS/scripts/source_repo_forensic_audit.py`._",
    ]

    (output_dir / "sources_index.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    print(f"\n[forensic] Index written to {output_dir}/sources_index.{{json,md}}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    # Load manifest
    manifest_path = Path(MANIFEST_PATH)
    if not manifest_path.is_file():
        die(f"Manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    repos = manifest.get("repos", [])
    if not repos:
        die("Manifest contains no repos to audit.")

    # Set up output directory
    output_dir = Path(AUDIT_OUTPUT_DIR)
    sources_dir = output_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)

    # Set up clone base directory
    if CLONE_BASE_DIR:
        clone_base = Path(CLONE_BASE_DIR)
    else:
        clone_base = Path(tempfile.mkdtemp(prefix="forensic_clones_"))
    clone_base.mkdir(parents=True, exist_ok=True)

    print(
        f"[forensic] Starting source-repo forensic audit\n"
        f"[forensic]   Repos     : {len(repos)}\n"
        f"[forensic]   Output    : {output_dir.resolve()}\n"
        f"[forensic]   Clone tmp : {clone_base.resolve()}\n"
    )

    reports = []
    for entry in repos:
        try:
            report = audit_one_repo(entry, clone_base, sources_dir)
            reports.append(report)
        except Exception as exc:  # noqa: BLE001
            owner = entry.get("owner", "?")
            repo_name = entry.get("repo", "?")
            tb = traceback.format_exc()
            print(
                f"[forensic] ERROR auditing {owner}/{repo_name}: {exc}\n{tb}",
                file=sys.stderr,
            )
            reports.append(
                {
                    "schema_version": "1.0",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "source": {
                        "owner": owner,
                        "repo": repo_name,
                        "phase": entry.get("phase"),
                        "role": entry.get("role"),
                        "note": entry.get("note"),
                    },
                    "sha_resolution": {"sha": None, "note": f"audit error: {exc}"},
                    "github_metadata": {},
                    "clone_status": {"success": False, "message": str(exc)},
                    "file_inventory": {},
                    "key_files": {},
                    "workflow_list": [],
                    "tech_stack": {},
                }
            )

    # Write combined index
    write_index(reports, output_dir)

    # Clean up clone base if it was auto-created
    if not CLONE_BASE_DIR and clone_base.exists():
        try:
            shutil.rmtree(clone_base)
        except OSError:
            pass

    print("\n[forensic] All audits complete.")


if __name__ == "__main__":
    main()
