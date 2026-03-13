#!/usr/bin/env python3
"""
repo_self_audit.py — GitHub repository settings self-audit tool.

Collects repository governance data via the GitHub REST API and writes:
  - FORENSIC_AUDIT/repo_settings_report.json  (machine-readable)
  - FORENSIC_AUDIT/repo_settings_report.md    (human-readable)

Defensive: any endpoint that returns an error (403, 404, 5xx, network failure)
is recorded as "unavailable" — the script NEVER exits non-zero due to an
inaccessible API; it only exits non-zero for programming errors or missing
required env vars.

SECURITY: Secret *values* are never printed. Only metadata (names, counts) is
collected for secrets/variables.

Required environment variables:
  GITHUB_TOKEN       — Personal Access Token or Actions GITHUB_TOKEN
  GITHUB_REPOSITORY  — "owner/repo" (e.g. "InfinityXOneSystems/XPS_INTELLIGENCE_PLATFORM")

Optional:
  AUDIT_OUTPUT_DIR   — directory to write reports (default: FORENSIC_AUDIT)
"""

import json
import os
import sys
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
API_BASE = "https://api.github.com"


def die(msg: str) -> None:
    print(f"FATAL: {msg}", file=sys.stderr)
    sys.exit(1)


if not GITHUB_TOKEN:
    die("GITHUB_TOKEN environment variable is not set.")
if not GITHUB_REPOSITORY or "/" not in GITHUB_REPOSITORY:
    die("GITHUB_REPOSITORY must be set to 'owner/repo'.")

OWNER, REPO = GITHUB_REPOSITORY.split("/", 1)

OUTPUT_DIR = Path(AUDIT_OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

def gh_get(path: str, accept: str = "application/vnd.github+json") -> object:
    """
    Perform a GET request against the GitHub API.

    Returns parsed JSON on success.
    Returns the string "unavailable" on any HTTP or network error.
    NEVER raises — all errors are caught and recorded.
    """
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "xps-repo-self-audit/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        status = exc.code
        if status in (401, 403, 404, 422, 451):
            return "unavailable"
        # 5xx or unexpected — also unavailable, not a fatal error
        return "unavailable"
    except Exception:
        return "unavailable"


def gh_get_paginated(path: str) -> object:
    """
    Collect all pages of a paginated GitHub API list endpoint.

    Returns a list of items, or the string "unavailable" if the first
    request fails.
    """
    results = []
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        data = gh_get(f"{path}{sep}per_page=100&page={page}")
        if data == "unavailable":
            return "unavailable" if page == 1 else results
        if not isinstance(data, list):
            # Some endpoints wrap in a dict (e.g. secrets → {"secrets": [...]})
            return data
        if not data:
            break
        results.extend(data)
        if len(data) < 100:
            break
        page += 1
    return results


# ---------------------------------------------------------------------------
# Collection functions
# ---------------------------------------------------------------------------

def collect_repo_info() -> dict:
    data = gh_get(f"/repos/{OWNER}/{REPO}")
    if data == "unavailable":
        return {"status": "unavailable"}
    return {
        "default_branch": data.get("default_branch", "unavailable"),
        "visibility": data.get("visibility", "unavailable"),
        "archived": data.get("archived", False),
        "has_issues": data.get("has_issues"),
        "has_projects": data.get("has_projects"),
        "has_wiki": data.get("has_wiki"),
        "delete_branch_on_merge": data.get("delete_branch_on_merge"),
        "allow_squash_merge": data.get("allow_squash_merge"),
        "allow_merge_commit": data.get("allow_merge_commit"),
        "allow_rebase_merge": data.get("allow_rebase_merge"),
        "allow_auto_merge": data.get("allow_auto_merge"),
    }


def collect_branches() -> object:
    data = gh_get_paginated(f"/repos/{OWNER}/{REPO}/branches")
    if data == "unavailable":
        return "unavailable"
    return [b.get("name") for b in data if isinstance(b, dict)]


def collect_branch_protection(default_branch: str) -> dict:
    """
    Collect protection rules for the default branch (and all branches if admin).
    Returns a dict keyed by branch name, or "unavailable".
    """
    if not default_branch or default_branch == "unavailable":
        return {"status": "unavailable"}

    result = {}
    raw = gh_get(f"/repos/{OWNER}/{REPO}/branches/{default_branch}/protection")
    if raw == "unavailable":
        result[default_branch] = "unavailable"
    else:
        result[default_branch] = _parse_protection(raw)

    return result


def _parse_protection(raw: dict) -> dict:
    if not isinstance(raw, dict):
        return "unavailable"
    rsc = raw.get("required_status_checks") or {}
    prr = raw.get("required_pull_request_reviews") or {}
    return {
        "required_status_checks": {
            "strict": rsc.get("strict"),
            "contexts": rsc.get("contexts", []),
            "checks": [
                {"context": c.get("context"), "app_id": c.get("app_id")}
                for c in (rsc.get("checks") or [])
            ],
        },
        "enforce_admins": (raw.get("enforce_admins") or {}).get("enabled"),
        "required_pull_request_reviews": {
            "dismissal_restrictions": bool(prr.get("dismissal_restrictions")),
            "dismiss_stale_reviews": prr.get("dismiss_stale_reviews"),
            "require_code_owner_reviews": prr.get("require_code_owner_reviews"),
            "required_approving_review_count": prr.get("required_approving_review_count"),
        },
        "restrictions": "present" if raw.get("restrictions") else "none",
        "allow_force_pushes": (raw.get("allow_force_pushes") or {}).get("enabled"),
        "allow_deletions": (raw.get("allow_deletions") or {}).get("enabled"),
    }


def collect_environments() -> object:
    data = gh_get(f"/repos/{OWNER}/{REPO}/environments")
    if data == "unavailable":
        return "unavailable"
    envs = data.get("environments", []) if isinstance(data, dict) else []
    result = []
    for env in envs:
        if not isinstance(env, dict):
            continue
        entry = {
            "name": env.get("name"),
            "protection_rules": [],
        }
        for rule in env.get("protection_rules", []) or []:
            rule_entry = {"type": rule.get("type")}
            if rule.get("type") == "required_reviewers":
                reviewers = []
                for rv in rule.get("reviewers", []) or []:
                    reviewer = rv.get("reviewer", {}) or {}
                    reviewers.append({
                        "type": rv.get("type"),
                        "login": reviewer.get("login"),
                    })
                rule_entry["reviewers"] = reviewers
            entry["protection_rules"].append(rule_entry)
        result.append(entry)
    return result


def collect_secrets() -> object:
    """Collect only secret NAMES — values are never fetched or printed."""
    data = gh_get(f"/repos/{OWNER}/{REPO}/actions/secrets")
    if data == "unavailable":
        return "unavailable"
    secrets = data.get("secrets", []) if isinstance(data, dict) else []
    return [
        {
            "name": s.get("name"),
            "created_at": s.get("created_at"),
            "updated_at": s.get("updated_at"),
        }
        for s in secrets
        if isinstance(s, dict)
    ]


def collect_variables() -> object:
    """Collect only variable NAMES — values are never fetched or printed."""
    data = gh_get(f"/repos/{OWNER}/{REPO}/actions/variables")
    if data == "unavailable":
        return "unavailable"
    variables = data.get("variables", []) if isinstance(data, dict) else []
    return [
        {
            "name": v.get("name"),
            "created_at": v.get("created_at"),
            "updated_at": v.get("updated_at"),
        }
        for v in variables
        if isinstance(v, dict)
    ]


def collect_open_pull_requests() -> object:
    data = gh_get_paginated(f"/repos/{OWNER}/{REPO}/pulls?state=open")
    if data == "unavailable":
        return "unavailable"
    if not isinstance(data, list):
        return "unavailable"
    return [
        {
            "number": pr.get("number"),
            "title": pr.get("title"),
            "state": pr.get("state"),
            "draft": pr.get("draft"),
            "created_at": pr.get("created_at"),
            "updated_at": pr.get("updated_at"),
            "head_ref": (pr.get("head") or {}).get("ref"),
            "base_ref": (pr.get("base") or {}).get("ref"),
            "author": (pr.get("user") or {}).get("login"),
            "url": pr.get("html_url"),
        }
        for pr in data
        if isinstance(pr, dict)
    ]


def collect_required_status_checks(default_branch: str) -> object:
    """
    Extract required status check contexts from branch protection.
    Returns list of checks or "unavailable".
    """
    if not default_branch or default_branch == "unavailable":
        return "unavailable"
    raw = gh_get(
        f"/repos/{OWNER}/{REPO}/branches/{default_branch}/protection/required_status_checks"
    )
    if raw == "unavailable":
        return "unavailable"
    if not isinstance(raw, dict):
        return "unavailable"
    return {
        "strict": raw.get("strict"),
        "contexts": raw.get("contexts", []),
        "checks": [
            {"context": c.get("context"), "app_id": c.get("app_id")}
            for c in (raw.get("checks") or [])
        ],
    }


def collect_rulesets() -> object:
    """Collect repository rulesets (newer API, may not be available on all plans)."""
    data = gh_get_paginated(f"/repos/{OWNER}/{REPO}/rulesets")
    if data == "unavailable":
        return "unavailable"
    if not isinstance(data, list):
        return "unavailable"
    return [
        {
            "id": r.get("id"),
            "name": r.get("name"),
            "target": r.get("target"),
            "enforcement": r.get("enforcement"),
            "conditions": r.get("conditions"),
        }
        for r in data
        if isinstance(r, dict)
    ]


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def build_report() -> dict:
    print(f"[audit] Collecting data for {OWNER}/{REPO} ...")

    repo_info = collect_repo_info()
    default_branch = repo_info.get("default_branch", "unavailable")

    branches = collect_branches()
    protection = collect_branch_protection(default_branch)
    environments = collect_environments()
    secrets = collect_secrets()
    variables = collect_variables()
    open_prs = collect_open_pull_requests()
    required_checks = collect_required_status_checks(default_branch)
    rulesets = collect_rulesets()

    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": f"{OWNER}/{REPO}",
        "repo_info": repo_info,
        "default_branch": default_branch,
        "branches": branches,
        "branch_protection": protection,
        "required_status_checks": required_checks,
        "rulesets": rulesets,
        "environments": environments,
        "actions_secrets_names_only": secrets,
        "actions_variables_names_only": variables,
        "open_pull_requests": open_prs,
    }

    print("[audit] Collection complete.")
    return report


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------

UA = "unavailable"


def _md_val(val) -> str:
    if val is None:
        return "_not set_"
    if val == UA:
        return "⚠️ unavailable (permissions or plan)"
    if val is True:
        return "✅ yes"
    if val is False:
        return "❌ no"
    return str(val)


def render_markdown(report: dict) -> str:
    ts = report.get("generated_at", "unknown")
    repo = report.get("repository", "unknown")
    default_branch = report.get("default_branch", UA)
    repo_info = report.get("repo_info", {})

    lines = [
        f"# Repository Settings Audit Report",
        f"",
        f"**Repository:** `{repo}`  ",
        f"**Generated:** {ts}  ",
        f"**Default branch:** `{default_branch}`",
        f"",
        f"---",
        f"",
        f"## Repository Configuration",
        f"",
        f"| Setting | Value |",
        f"| ------- | ----- |",
    ]
    for key in [
        "visibility", "archived", "has_issues", "has_projects", "has_wiki",
        "delete_branch_on_merge", "allow_squash_merge", "allow_merge_commit",
        "allow_rebase_merge", "allow_auto_merge",
    ]:
        lines.append(f"| {key.replace('_', ' ').title()} | {_md_val(repo_info.get(key))} |")

    lines += ["", "---", "", "## Branches", ""]
    branches = report.get("branches", UA)
    if branches == UA:
        lines.append(f"> ⚠️ Branch list unavailable.")
    elif isinstance(branches, list):
        lines.append(f"**Total branches:** {len(branches)}")
        lines.append("")
        for b in branches:
            lines.append(f"- `{b}`")
    else:
        lines.append(f"> {branches}")

    lines += ["", "---", "", "## Branch Protection Rules", ""]
    protection = report.get("branch_protection", {})
    _protection_unavailable = (
        protection == UA
        or not protection
        or (isinstance(protection, dict) and protection.get("status") == UA)
    )
    if _protection_unavailable:
        lines.append("> ⚠️ Branch protection data unavailable.")
    else:
        for branch, rules in protection.items():
            lines.append(f"### Branch: `{branch}`")
            lines.append("")
            if rules == UA:
                lines.append("> ⚠️ Protection rules unavailable (not configured or insufficient permissions).")
            elif isinstance(rules, dict):
                rsc = rules.get("required_status_checks", {}) or {}
                lines.append(f"**Enforce admins:** {_md_val(rules.get('enforce_admins'))}")
                lines.append(f"**Force pushes allowed:** {_md_val(rules.get('allow_force_pushes'))}")
                lines.append(f"**Deletions allowed:** {_md_val(rules.get('allow_deletions'))}")
                lines.append(f"**Restrictions:** {_md_val(rules.get('restrictions'))}")
                lines.append("")
                lines.append("**Required status checks:**")
                if rsc == UA or not rsc:
                    lines.append("> ⚠️ Not configured or unavailable.")
                else:
                    lines.append(f"- Strict: {_md_val(rsc.get('strict'))}")
                    checks = rsc.get("checks") or rsc.get("contexts") or []
                    if checks:
                        for c in checks:
                            ctx = c.get("context", c) if isinstance(c, dict) else c
                            lines.append(f"  - `{ctx}`")
                    else:
                        lines.append("  - _none configured_")
                prr = rules.get("required_pull_request_reviews", {}) or {}
                lines.append("")
                lines.append("**Pull request reviews:**")
                lines.append(f"- Required approvals: {_md_val(prr.get('required_approving_review_count'))}")
                lines.append(f"- Dismiss stale reviews: {_md_val(prr.get('dismiss_stale_reviews'))}")
                lines.append(f"- Require code owner review: {_md_val(prr.get('require_code_owner_reviews'))}")
            lines.append("")

    lines += ["---", "", "## Required Status Checks", ""]
    rsc = report.get("required_status_checks", UA)
    if rsc == UA:
        lines.append("> ⚠️ Required status checks unavailable.")
    elif isinstance(rsc, dict):
        lines.append(f"**Strict:** {_md_val(rsc.get('strict'))}")
        checks = rsc.get("checks") or rsc.get("contexts") or []
        if checks:
            lines.append("**Checks:**")
            for c in checks:
                ctx = c.get("context", c) if isinstance(c, dict) else c
                lines.append(f"- `{ctx}`")
        else:
            lines.append("_No required checks configured._")
    else:
        lines.append(f"> {rsc}")

    lines += ["", "---", "", "## Rulesets", ""]
    rulesets = report.get("rulesets", UA)
    if rulesets == UA:
        lines.append("> ⚠️ Rulesets unavailable (feature may not be enabled on this plan).")
    elif isinstance(rulesets, list):
        if not rulesets:
            lines.append("_No rulesets configured._")
        else:
            for rs in rulesets:
                lines.append(f"- **{rs.get('name')}** — target: `{rs.get('target')}`, enforcement: `{rs.get('enforcement')}`")
    else:
        lines.append(f"> {rulesets}")

    lines += ["", "---", "", "## Environments", ""]
    environments = report.get("environments", UA)
    if environments == UA:
        lines.append("> ⚠️ Environments unavailable.")
    elif isinstance(environments, list):
        if not environments:
            lines.append("_No environments configured._")
        else:
            for env in environments:
                lines.append(f"### Environment: `{env.get('name')}`")
                rules = env.get("protection_rules", [])
                if not rules:
                    lines.append("- No protection rules.")
                else:
                    for rule in rules:
                        rtype = rule.get("type", "unknown")
                        if rtype == "required_reviewers":
                            reviewers = rule.get("reviewers", [])
                            rv_list = ", ".join(
                                f"{rv.get('type')}/{rv.get('login')}" for rv in reviewers
                            )
                            lines.append(f"- Required reviewers: {rv_list or '_none_'}")
                        else:
                            lines.append(f"- Rule type: `{rtype}`")
                lines.append("")
    else:
        lines.append(f"> {environments}")

    lines += ["---", "", "## GitHub Actions Secrets (Names Only)", ""]
    secrets = report.get("actions_secrets_names_only", UA)
    if secrets == UA:
        lines.append("> ⚠️ Secrets list unavailable (insufficient permissions or no secrets).")
    elif isinstance(secrets, list):
        if not secrets:
            lines.append("_No repository secrets configured._")
        else:
            lines.append(f"**Count:** {len(secrets)}")
            lines.append("")
            lines.append("| Name | Created | Updated |")
            lines.append("| ---- | ------- | ------- |")
            for s in secrets:
                lines.append(f"| `{s.get('name')}` | {s.get('created_at', '-')} | {s.get('updated_at', '-')} |")
    else:
        lines.append(f"> {secrets}")

    lines += ["", "---", "", "## GitHub Actions Variables (Names Only)", ""]
    variables = report.get("actions_variables_names_only", UA)
    if variables == UA:
        lines.append("> ⚠️ Variables list unavailable.")
    elif isinstance(variables, list):
        if not variables:
            lines.append("_No repository variables configured._")
        else:
            lines.append(f"**Count:** {len(variables)}")
            lines.append("")
            lines.append("| Name | Created | Updated |")
            lines.append("| ---- | ------- | ------- |")
            for v in variables:
                lines.append(f"| `{v.get('name')}` | {v.get('created_at', '-')} | {v.get('updated_at', '-')} |")
    else:
        lines.append(f"> {variables}")

    lines += ["", "---", "", "## Open Pull Requests", ""]
    prs = report.get("open_pull_requests", UA)
    if prs == UA:
        lines.append("> ⚠️ Open PRs unavailable.")
    elif isinstance(prs, list):
        if not prs:
            lines.append("_No open pull requests._")
        else:
            lines.append(f"**Count:** {len(prs)}")
            lines.append("")
            lines.append("| # | Title | Author | Draft | Head → Base | Created |")
            lines.append("| - | ----- | ------ | ----- | ----------- | ------- |")
            for pr in prs:
                draft = "✏️ draft" if pr.get("draft") else ""
                lines.append(
                    f"| [{pr.get('number')}]({pr.get('url')}) "
                    f"| {pr.get('title')} "
                    f"| {pr.get('author')} "
                    f"| {draft} "
                    f"| `{pr.get('head_ref')}` → `{pr.get('base_ref')}` "
                    f"| {(pr.get('created_at') or '')[:10]} |"
                )
    else:
        lines.append(f"> {prs}")

    lines += [
        "",
        "---",
        "",
        "## Notes",
        "",
        "- Fields marked ⚠️ **unavailable** indicate the API endpoint is either not accessible with",
        "  the current token permissions or the feature is not enabled on this plan.",
        "- **Secret values are never collected or stored** — only metadata (name, timestamps).",
        "- Re-run this audit after updating token scopes or branch protection settings.",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    report = build_report()

    json_path = OUTPUT_DIR / "repo_settings_report.json"
    md_path = OUTPUT_DIR / "repo_settings_report.md"

    json_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"[audit] JSON report written → {json_path}")

    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"[audit] Markdown report written → {md_path}")

    # Surface a summary to stdout for the Actions log
    n_branches = len(report["branches"]) if isinstance(report["branches"], list) else "?"
    n_secrets = len(report["actions_secrets_names_only"]) if isinstance(report["actions_secrets_names_only"], list) else "?"
    n_envs = len(report["environments"]) if isinstance(report["environments"], list) else "?"
    n_prs = len(report["open_pull_requests"]) if isinstance(report["open_pull_requests"], list) else "?"

    print(
        f"\n[audit] Summary: "
        f"default_branch={report['default_branch']}  "
        f"branches={n_branches}  "
        f"secrets(names)={n_secrets}  "
        f"environments={n_envs}  "
        f"open_prs={n_prs}"
    )


if __name__ == "__main__":
    main()
