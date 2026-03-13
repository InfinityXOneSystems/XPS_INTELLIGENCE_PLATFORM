## Description

<!-- Clearly describe WHAT this PR does and WHY. Link to the GitHub Issue it resolves. -->

Resolves #<!-- issue number -->

### Changes Made
<!-- List the specific changes made in this PR -->
- 

### Type of Change
<!-- Mark the applicable option with [x] -->
- [ ] `feat` — New feature
- [ ] `fix` — Bug fix
- [ ] `docs` — Documentation only
- [ ] `refactor` — Code refactor (no functional change)
- [ ] `test` — Tests only
- [ ] `ci` — CI/CD workflow change
- [ ] `security` — Security fix or hardening
- [ ] `chore` — Maintenance (deps, config, etc.)

### Phase
- [ ] Foundation
- [ ] Phase 1 (Backend/Frontend consolidation)
- [ ] Phase 2 (Build/Infra)
- [ ] Phase 3 (Admin control plane)
- [ ] Phase 4 (Agents/ConstructIQ)
- [ ] Phase 5 (Full autonomous operation)

---

## Checklist

### Code Quality
- [ ] Code follows the conventions in `.github/copilot-instructions.md`
- [ ] All new functions/classes have docstrings
- [ ] No hardcoded secrets, URLs, or environment-specific values
- [ ] No `print()` statements in production code (use structured logger)
- [ ] Error handling is explicit and complete

### Testing
- [ ] Tests added/updated for all changed code paths
- [ ] All existing tests pass locally
- [ ] Playwright E2E tests pass (if UI changes)
- [ ] Visual snapshots updated (if UI changes)

### Security
- [ ] No new secrets introduced
- [ ] Input validation added for any new external input
- [ ] SQL injection protection maintained (ORM / parameterized queries)
- [ ] No new security vulnerabilities introduced

### Documentation
- [ ] `CHANGELOG.md` updated
- [ ] Architecture docs updated (if architectural change)
- [ ] `TODO.md` updated (if resolving or adding tasks)
- [ ] API docs updated (if new/changed endpoints)

### Frontend (if applicable)
- [ ] Frontend changes are **additive only** — no breaking changes to existing UI
- [ ] New components have Playwright snapshot tests

### Deployment
- [ ] Railway environment variables updated (if new config required)
- [ ] Database migrations included (if schema changed)
- [ ] No breaking changes to the Railway deployment

---

## Screenshots / Playwright Snapshots

<!-- If UI changes, paste Playwright snapshot diffs or screenshots here -->

---

## Notes for Reviewer

<!-- Any additional context, concerns, or instructions for the reviewer -->
