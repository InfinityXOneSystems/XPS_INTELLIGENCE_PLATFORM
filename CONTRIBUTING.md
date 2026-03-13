# Contributing to XPS Intelligence Platform

Thank you for contributing to the XPS Intelligence Platform. This document
describes the process, standards, and requirements for all contributions.

## Prerequisites

Before contributing, read these files in order:

1. `.github/copilot-instructions.md` — Governance rules and mission
2. `_OPS/POLICY/TAP.md` — TAP enforcement contract
3. `_OPS/ARCHITECTURE/SYSTEM_TOPOLOGY.md` — System topology
4. `_OPS/RUNBOOK/OPERATOR_RUNBOOK.md` — Operator runbook

## Getting Started

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/InfinityXOneSystems/XPS_INTELLIGENCE_PLATFORM.git
cd XPS_INTELLIGENCE_PLATFORM

# Start local infrastructure (redis + postgres)
docker compose up -d

# Install backend dependencies
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start backend API
uvicorn app.main:app --reload --port 8000

# Install frontend dependencies (separate terminal)
cd apps/frontend
npm install
npm run dev
```

## Branch Strategy

| Branch pattern | Purpose | Target PR base |
|---|---|---|
| `feature/<name>` | New features | `develop` |
| `fix/<name>` | Bug fixes | `develop` |
| `release/<version>` | Release preparation | `main` |
| `hotfix/<name>` | Emergency production fixes | `main` |

Always branch from `develop` for features and fixes. The `main` branch
receives only release and hotfix PRs.

## Pull Request Process

1. Create your branch from `develop` (or `main` for hotfixes).
2. Make your changes following the code standards below.
3. Run all relevant tests locally before pushing.
4. Open a PR against the correct base branch.
5. Complete every item in the PR template checklist.
6. Wait for CI to pass and address any failures.
7. Request a review from a CODEOWNER (automatic on PR creation).
8. Address all review comments.
9. Squash-merge after approval.

### PR Title Format

Use the conventional commits format:

```text
<type>(<scope>): <short description>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`

Examples:

```text
feat(scraper): add rate limit configuration to settings UI
fix(backend): correct lead normalization for missing phone field
docs(_OPS): update operator runbook with Railway service names
ci(workflows): add markdownlint step to CI workflow
```

## Code Standards

### General

- No hardcoded URLs, ports, or credentials.
- No `TODO` bodies in committed code. File an issue and reference it instead.
- All environment variables must be documented in
  `_OPS/ARCHITECTURE/SYSTEM_TOPOLOGY.md`.

### Backend (Python)

- Use Python 3.11+.
- Format with `ruff format` and lint with `ruff check`.
- Type hints are required on all public functions and class methods.
- Use Pydantic v2 for all request/response schemas.
- New endpoints require unit tests and integration tests.

### Frontend (TypeScript/React)

- Use TypeScript strict mode (`"strict": true` in tsconfig).
- Format with Prettier and lint with ESLint.
- Do NOT change existing component styles, tokens, or layout. Additions only.
- New components require unit tests (Vitest) and visual snapshots (Playwright).
- No `any` types without explicit `// eslint-disable` comment and justification.

### Tests

- Backend: pytest with minimum 80% coverage on new code.
- Frontend: Vitest for unit tests; Playwright for e2e and snapshot tests.
- All tests must pass before a PR can be merged.
- Test evidence (snapshots, coverage reports) is uploaded as CI artifacts.

## Commit Signing

Signed commits are encouraged. Configure GPG or SSH signing:

```bash
git config --global commit.gpgsign true
```

## Security

Report security vulnerabilities privately per `SECURITY.md`. Do not open
public issues for security vulnerabilities.

## License

By contributing to this repository, you agree that your contributions will be
licensed under the MIT License as specified in `LICENSE`.
