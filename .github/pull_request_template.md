## TAP Compliance

- [ ] Read `.infinity/ACTIVE_MEMORY.md` before making changes
- [ ] Validated `FORENSIC_AUDIT/` outputs are current
- [ ] No frontend aesthetic changes (additive only; existing styles are immutable)
- [ ] No secrets exposed to frontend bundle (no `VITE_` prefix on secrets)
- [ ] Sandbox execution boundary enforced for all code execution tasks
- [ ] All new environment variables documented in `_OPS/ARCHITECTURE/SYSTEM_TOPOLOGY.md`

## Change Summary

<!-- Describe what this PR changes and why. -->

## Proof of Correctness

- [ ] Unit tests added or updated and passing
- [ ] Integration tests added or updated and passing
- [ ] E2E Playwright tests pass; snapshots attached as CI artifacts
- [ ] Test evidence stored in `TEST_EVIDENCE/` or CI artifacts
- [ ] `FORENSIC_AUDIT/repo_settings_report.json` shows no new P0/P1 issues

## Type of Change

- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking, additive)
- [ ] Breaking change (requires migration or version bump)
- [ ] Documentation update
- [ ] CI/CD or tooling change
- [ ] Dependency update
- [ ] Security fix

## Checklist

- [ ] All required status checks pass
- [ ] Code follows the style and conventions in `CONTRIBUTING.md`
- [ ] Self-review of the diff is complete
- [ ] Documentation updated where applicable
- [ ] No hardcoded URLs, ports, or credentials
