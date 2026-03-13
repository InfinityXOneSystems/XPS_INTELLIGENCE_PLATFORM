#!/usr/bin/env bash
# =============================================================================
# validate_repo_settings.sh
# Read-only validation of repository settings via the GitHub API.
# Produces a JSON compliance report at FORENSIC_AUDIT/repo_settings_report.json
#
# Required environment variables:
#   GITHUB_TOKEN        — GitHub token with at minimum contents:read scope
#   GITHUB_REPOSITORY   — Repository in "owner/repo" format (set by Actions)
#
# Optional environment variables:
#   GITHUB_DEFAULT_BRANCH — Branch to check for protection (default: main)
#   FORENSIC_AUDIT_DIR    — Output directory (default: FORENSIC_AUDIT)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OWNER="${GITHUB_REPOSITORY_OWNER:-}"
REPO_FULL="${GITHUB_REPOSITORY:-}"

if [[ -z "${REPO_FULL}" ]]; then
  echo "ERROR: GITHUB_REPOSITORY is not set." >&2
  exit 1
fi

REPO="${REPO_FULL#*/}"
OWNER="${OWNER:-${REPO_FULL%%/*}}"
TOKEN="${GITHUB_TOKEN:?GITHUB_TOKEN must be set}"
BRANCH="${GITHUB_DEFAULT_BRANCH:-main}"
OUTPUT_DIR="${FORENSIC_AUDIT_DIR:-FORENSIC_AUDIT}"
REPORT_FILE="${OUTPUT_DIR}/repo_settings_report.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

TMP_DIR=$(mktemp -d)
# shellcheck disable=SC2064
trap "rm -rf '${TMP_DIR}'" EXIT

mkdir -p "${OUTPUT_DIR}"

# ---------------------------------------------------------------------------
# GitHub API helper
# Writes the response body to stdout.
# Writes the HTTP status code to the variable named by the second argument.
# On network error, writes '{"network_error":true}' to stdout and sets
# status to "000".
# ---------------------------------------------------------------------------
api_get() {
  local path="$1"
  local status_var="${2:-_status}"
  local response
  local http_code

  response=$(
    curl -s -w "\n__STATUS__%{http_code}" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "https://api.github.com${path}" 2>/dev/null
  ) || response='{"network_error":true}\n__STATUS__000'

  http_code="${response##*$'\n'__STATUS__}"
  local body="${response%$'\n'__STATUS__*}"

  # Assign http_code to caller's variable via a temp file (portable)
  echo "${http_code}" > "${TMP_DIR}/${status_var}.code"
  echo "${body}"
}

read_code() {
  local status_var="$1"
  cat "${TMP_DIR}/${status_var}.code" 2>/dev/null || echo "000"
}

# ---------------------------------------------------------------------------
# Fetch repository data
# ---------------------------------------------------------------------------
echo "INFO: Fetching repository info for ${OWNER}/${REPO} ..."
api_get "/repos/${OWNER}/${REPO}" "repo_status" > "${TMP_DIR}/repo_info.json"
REPO_STATUS=$(read_code "repo_status")
echo "INFO: Repository info HTTP ${REPO_STATUS}"

echo "INFO: Fetching branch protection for '${BRANCH}' ..."
api_get "/repos/${OWNER}/${REPO}/branches/${BRANCH}/protection" "bp_status" \
  > "${TMP_DIR}/branch_protection.json"
BP_STATUS=$(read_code "bp_status")
echo "INFO: Branch protection HTTP ${BP_STATUS}"

echo "INFO: Fetching repository rulesets ..."
api_get "/repos/${OWNER}/${REPO}/rulesets" "rs_status" \
  > "${TMP_DIR}/rulesets.json"
RS_STATUS=$(read_code "rs_status")
echo "INFO: Rulesets HTTP ${RS_STATUS}"

echo "INFO: Fetching security and analysis settings ..."
api_get "/repos/${OWNER}/${REPO}" "sec_status" \
  > "${TMP_DIR}/security.json"

# ---------------------------------------------------------------------------
# Generate compliance report with Python
# ---------------------------------------------------------------------------
echo "INFO: Generating compliance report ..."

python3 - \
  "${TMP_DIR}" \
  "${REPORT_FILE}" \
  "${OWNER}/${REPO}" \
  "${BRANCH}" \
  "${TIMESTAMP}" \
  "${REPO_STATUS}" \
  "${BP_STATUS}" \
  "${RS_STATUS}" \
<<'PYEOF'
import json
import sys
import os

(
    tmp_dir,
    report_file,
    repo_full,
    branch,
    timestamp,
    repo_status,
    bp_status,
    rs_status,
) = sys.argv[1:9]


def load_json(path, default):
    """Load JSON from a file, returning default if the file is missing or invalid."""
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:
        return default


repo_info = load_json(f"{tmp_dir}/repo_info.json", {})
branch_protection = load_json(f"{tmp_dir}/branch_protection.json", {})
rulesets = load_json(f"{tmp_dir}/rulesets.json", [])

# -----------------------------------------------------------------------
# Extract key settings
# -----------------------------------------------------------------------
sec_analysis = repo_info.get("security_and_analysis") or {}
secret_scanning = (sec_analysis.get("secret_scanning") or {}).get("status", "unknown")
secret_push_protection = (
    (sec_analysis.get("secret_scanning_push_protection") or {}).get("status", "unknown")
)
advanced_security = (sec_analysis.get("advanced_security") or {}).get("status", "unknown")

repo_settings = {
    "private": repo_info.get("private", False),
    "default_branch": repo_info.get("default_branch", "unknown"),
    "has_issues": repo_info.get("has_issues", False),
    "delete_branch_on_merge": repo_info.get("delete_branch_on_merge", False),
    "allow_auto_merge": repo_info.get("allow_auto_merge", False),
    "allow_merge_commit": repo_info.get("allow_merge_commit", True),
    "allow_squash_merge": repo_info.get("allow_squash_merge", True),
    "allow_rebase_merge": repo_info.get("allow_rebase_merge", True),
    "secret_scanning": secret_scanning,
    "secret_scanning_push_protection": secret_push_protection,
    "advanced_security": advanced_security,
}

# Branch protection is only readable with administration:read scope.
bp_accessible = bp_status == "200"
bp_not_configured = bp_status in ("404", "403", "000") or branch_protection.get("not_found")

if bp_accessible:
    pr_reviews = branch_protection.get("required_pull_request_reviews") or {}
    status_checks = branch_protection.get("required_status_checks") or {}
    enforce_admins = branch_protection.get("enforce_admins") or {}
    restrictions = branch_protection.get("restrictions")

    branch_protection_summary = {
        "configured": True,
        "require_pull_request_reviews": bool(pr_reviews),
        "required_approving_review_count": pr_reviews.get("required_approving_review_count", 0),
        "dismiss_stale_reviews": pr_reviews.get("dismiss_stale_reviews", False),
        "require_status_checks": bool(status_checks),
        "require_branches_up_to_date": status_checks.get("strict", False),
        "required_status_check_contexts": status_checks.get("contexts", []),
        "enforce_admins": enforce_admins.get("enabled", False) if isinstance(enforce_admins, dict) else False,
        "restrict_pushes": restrictions is not None,
    }
elif bp_status == "403":
    branch_protection_summary = {
        "configured": "unknown",
        "note": "Insufficient token permissions to read branch protection (need administration:read scope).",
    }
else:
    branch_protection_summary = {
        "configured": False,
        "note": f"Branch protection API returned HTTP {bp_status}.",
    }

# -----------------------------------------------------------------------
# Build compliance issues and recommendations
# -----------------------------------------------------------------------
issues = []
recommendations = []

if branch_protection_summary.get("configured") is False:
    issues.append("Branch protection is not configured on the default branch.")
    recommendations.append(
        "Enable branch protection on 'main' with required PR reviews and status checks. "
        "See _OPS/RUNBOOK/OPERATOR_RUNBOOK.md for exact settings."
    )
elif branch_protection_summary.get("configured") is True:
    if not branch_protection_summary.get("require_pull_request_reviews"):
        issues.append("Pull request reviews are not required before merging.")
        recommendations.append("Require at least 1 approving review before merging.")

    if not branch_protection_summary.get("require_status_checks"):
        issues.append("Required status checks are not enforced.")
        recommendations.append(
            "Add CI workflow jobs as required status checks: "
            "'CI / Lint Markdown', 'CI / Lint YAML', "
            "'CI / Check Repo Structure', 'CI / Check No VITE_ Secrets'."
        )

    if not branch_protection_summary.get("enforce_admins"):
        recommendations.append(
            "Enable 'Enforce for administrators' to prevent admin bypasses."
        )

if not repo_settings.get("delete_branch_on_merge"):
    recommendations.append(
        "Enable 'Automatically delete head branches' for cleaner branch management."
    )

if repo_settings.get("allow_merge_commit", True):
    recommendations.append(
        "Disable merge commits; use squash merges only for a clean linear history."
    )

if repo_settings.get("allow_rebase_merge", True):
    recommendations.append(
        "Disable rebase merges; use squash merges only for consistent attribution."
    )

if secret_scanning == "disabled":
    issues.append("Secret scanning is disabled.")
    recommendations.append("Enable GitHub Secret Scanning in repository security settings.")

if secret_push_protection == "disabled":
    recommendations.append(
        "Enable Secret Scanning Push Protection to block secret commits at push time."
    )

# -----------------------------------------------------------------------
# Compile final report
# -----------------------------------------------------------------------
status = "PASS" if len(issues) == 0 else "NEEDS_ATTENTION"

report = {
    "schema_version": "1.0",
    "generated_at": timestamp,
    "repository": repo_full,
    "branch_checked": branch,
    "api_status": {
        "repo_info": repo_status,
        "branch_protection": bp_status,
        "rulesets": rs_status,
    },
    "repo_settings": repo_settings,
    "branch_protection": branch_protection_summary,
    "rulesets_count": len(rulesets) if isinstance(rulesets, list) else 0,
    "compliance_summary": {
        "status": status,
        "total_issues": len(issues),
        "issues": issues,
        "recommendations": recommendations,
    },
}

os.makedirs(os.path.dirname(report_file), exist_ok=True)
with open(report_file, "w") as fh:
    json.dump(report, fh, indent=2)

print(f"Report written to: {report_file}")
print(f"Compliance status: {status}")

if issues:
    print(f"\nIssues found ({len(issues)}):")
    for issue in issues:
        print(f"  - {issue}")

if recommendations:
    print(f"\nRecommendations ({len(recommendations)}):")
    for rec in recommendations:
        print(f"  - {rec}")
PYEOF

echo "INFO: Validation complete. Report: ${REPORT_FILE}"
