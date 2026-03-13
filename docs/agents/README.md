# Agent Documentation

## Overview

All autonomous agents in the XPS Intelligence Platform implement the `BaseAgent` interface. See `packages/agents/README.md` for the base contract.

## Agent Lifecycle

```
1. Trigger (scheduled / event / manual)
2. Load memory (Postgres via MemoryAgent)
3. Execute task
4. Save memory (Postgres + Redis cache)
5. Report result (GitHub Issue / log / metrics)
```

## Communication Patterns

### Sync (direct call)
```python
result = await agent.run()
```

### Async (Redis pub/sub)
```python
await redis.publish("agent:channel", json.dumps(payload))
```

### Human-visible (GitHub Issues via Infinity Orchestrator)
```python
await orchestrator.create_issue(title="Agent result", body=result)
```

## Memory System

All agent memory is stored in Postgres (`agent_memory` table) with Redis caching.

```sql
-- Agent memory schema
SELECT * FROM agent_memory WHERE agent_id = 'shadow-scraper';
```

## Adding a New Agent

1. Create directory: `packages/agents/<agent-name>/`
2. Implement `BaseAgent` interface
3. Add health check endpoint
4. Add unit tests
5. Register in `packages/agents/README.md`
6. Add to `issue-manager.yml` monitoring
