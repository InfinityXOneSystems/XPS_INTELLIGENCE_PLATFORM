# API Documentation

> Auto-generated from FastAPI OpenAPI spec. See the live API docs at `https://<backend-url>/docs`

## Endpoints (Phase 1 Target)

### Health
- `GET /health` — System health check

### Authentication
- `POST /auth/login` — Login and receive JWT
- `POST /auth/refresh` — Refresh JWT token
- `POST /auth/logout` — Invalidate JWT

### Intelligence
- `GET /intelligence/leads` — Get processed leads
- `POST /intelligence/scrape` — Trigger Shadow Scraper
- `GET /intelligence/agents` — List all agents and their status

### Memory
- `GET /memory/{agent_id}` — Get agent memory
- `POST /memory/{agent_id}` — Save agent memory
- `DELETE /memory/{agent_id}/{key}` — Delete specific memory key

### Admin
- `GET /admin/status` — Full system status
- `POST /admin/agents/{agent_id}/run` — Trigger agent run
- `GET /admin/logs` — Recent system logs

---

*This documentation is auto-updated from the FastAPI OpenAPI spec by the `docs-sync` workflow.*
