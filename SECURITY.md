# Security Policy

## Supported Versions

The following versions of the XPS Intelligence Platform receive active security
updates:

| Version | Status |
|---|---|
| `main` branch | Actively maintained — security fixes applied immediately |
| `develop` branch | Staging — security fixes applied before release |
| All other branches | Not supported — upgrade to `main` |

## Reporting a Vulnerability

**Do not report security vulnerabilities through public GitHub issues.**

Please report vulnerabilities using one of these methods:

1. **GitHub Security Advisory (preferred):** Navigate to
   [Security → Advisories](../../security/advisories/new) and open a private
   advisory. This keeps the details confidential until a fix is ready.
2. **Email:** If you cannot use GitHub Advisories, contact the maintainers
   directly through the contact information in the repository profile.

### What to Include

When reporting a vulnerability, please include:

- A clear description of the vulnerability and its potential impact.
- The affected component (frontend, backend API, worker, CI/CD workflow).
- Steps to reproduce the vulnerability.
- Any proof-of-concept code (do not publish this publicly).
- Your assessment of severity (P0/P1/P2/P3 per `_OPS/POLICY/TAP.md`).

### Response Timeline

| Action | Target Time |
|---|---|
| Acknowledgment of report | Within 48 hours |
| Initial severity assessment | Within 72 hours |
| Fix for P0 Critical | Within 7 days |
| Fix for P1 High | Within 14 days |
| Fix for P2 Medium | Within 30 days |
| Disclosure after fix | Coordinated with reporter |

## Security Configuration

### Secrets Management

- All secrets are stored as GitHub Environment secrets or Railway variables.
- Secrets are **never** committed to the repository.
- Frontend environment variables (prefixed `VITE_`) are public by definition
  and must never contain credentials, tokens, or API keys.
- Rotate secrets immediately if accidental exposure is suspected.

### Dependency Security

- All production dependencies are audited by the `Security Scan` workflow on
  every PR.
- Dependabot alerts are reviewed weekly and P0/P1 CVEs are patched within
  the response timeline above.
- Dependencies with no active maintenance are evaluated for replacement.

### Branch Protection

The `main` branch has the following protections enforced (see
`_OPS/RUNBOOK/OPERATOR_RUNBOOK.md` for full configuration):

- Required pull request reviews (minimum 1 approver)
- Required status checks (CI must pass)
- No direct pushes to `main`
- Signed commits encouraged (configurable per team policy)

### Sandbox Execution

All user-initiated code execution and web scraping runs inside the
`sandbox-runner` service with:

- Container isolation
- Read-only mounts where possible
- Network access restricted to an allowlist
- Per-task workspace directories that are cleaned after completion

### Secret Scanning

- GitHub Secret Scanning is enabled on this repository.
- Push protection prevents secrets from being committed.
- The CI `Check No VITE_ Secrets` job scans for patterns that could expose
  secrets through the frontend bundle.
