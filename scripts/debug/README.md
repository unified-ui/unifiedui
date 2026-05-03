# DB Inspection Toolkit (REQ 007 — Paket 2)

Cheatsheet for inspecting **all unified-ui datastores** during local development
and self-debugging by Copilot.

> All commands assume the local docker-compose stack is running:
> `cd unifiedui/docker/local && docker compose up -d`

---

## Connection Cheatsheet

| Service        | Container               | Host             | Port  | User    | Password / DB |
|----------------|-------------------------|------------------|-------|---------|---------------|
| PostgreSQL     | `unifiedui-database`    | `localhost`      | 5432  | `unifiedui` | pw `unifiedui_password`, db `unifiedui` |
| MongoDB        | `unifiedui-docdatabase` | `localhost`      | 27017 | `admin` | pw `admin`, db `unifiedui` |
| Redis          | `unifiedui-cache`       | `localhost`      | 6379  | -       | pw `admin` |
| Vault (HCL)    | `unifiedui-vault`       | `localhost`      | 8200  | -       | dev token from `.env` |
| RabbitMQ Mgmt  | `unifiedui-message-broker` | `localhost`   | 15672 | `admin` | pw `admin` |

> Real values come from `unifiedui/docker/local/.env`. Defaults shown above match `.env.example`.

---

## CLI Quick Access

### PostgreSQL (relational data: tenants, agents, credentials, members)
```bash
docker exec -it unifiedui-database psql -U unifiedui -d unifiedui

# One-shot query
docker exec -i unifiedui-database psql -U unifiedui -d unifiedui -c "SELECT id, name FROM tenants LIMIT 10;"

# Dump schema for a table
docker exec -i unifiedui-database psql -U unifiedui -d unifiedui -c "\d+ chat_agents"

# List all tables
docker exec -i unifiedui-database psql -U unifiedui -d unifiedui -c "\dt"
```

### MongoDB (conversations, messages, traces, telemetry)
```bash
docker exec -it unifiedui-docdatabase mongosh -u admin -p admin --authenticationDatabase admin

# In shell
use unifiedui
show collections
db.messages.find({tenant_id: "t-1"}).sort({created_at: -1}).limit(5).pretty()
db.traces.countDocuments({status: "error"})
```

### Redis (caches: identity, tenants, group ids, etc.)
```bash
docker exec -it unifiedui-cache redis-cli -a admin

# In shell
KEYS identity:*
GET identity:idp_group_ids:user:test-user-123
TTL identity:idp_group_ids:user:test-user-123
FLUSHDB                          # nuke current db (idx 0) — destructive
```

---

## Python Helper (`db_inspect.py`)

A connection-bootstrap script. Import it in a REPL or notebook:

```bash
cd unifiedui/scripts/debug
uv run --with psycopg2-binary --with pymongo --with redis python -i db_inspect.py
```

```python
>>> pg.execute("SELECT id, name FROM tenants LIMIT 5").fetchall()
>>> mongo.messages.find_one({"tenant_id": "t-1"})
>>> redis.keys("identity:*")
```

See [`db_inspect.py`](db_inspect.py) for full source.

---

## Common Recipes

### See all members of a tenant
```sql
SELECT p.id, p.principal_type, tm.role
FROM tenant_members tm
JOIN principals p ON p.id = tm.principal_id
WHERE tm.tenant_id = '<TENANT_ID>';
```

### Last 20 messages in a conversation
```js
db.messages.find({conversation_id: "<CONV_ID>"})
  .sort({created_at: -1}).limit(20).pretty()
```

### Find all reactions for a message
```js
db.message_reactions.find({message_id: "<MSG_ID>"}).pretty()
```

### Inspect cached organization context for a user
```bash
docker exec -i unifiedui-cache redis-cli -a admin --scan --pattern 'identity:*'
docker exec -i unifiedui-cache redis-cli -a admin GET 'identity:idp_group_ids:user:<USER_ID>'
```

### Drop & recreate Postgres (nuclear reset — DESTRUCTIVE)
```bash
cd unifiedui/docker/local
docker compose -f infra.yml down -v
docker compose -f infra.yml up -d unifiedui-database
cd ../../../unified-ui-platform-service
uv run alembic upgrade head
```

---

## Microsoft Foundry Smoke Tests

`foundry_smoke.py` lets Copilot iterate on prompts against a real Foundry project using the API key (no `az login` required).

```bash
# Step 1: source the platform-service .env to get FOUNDRY_PROJECT_* vars
cd unified-ui-platform-service && set -a && source .env && set +a

# Step 2: open REPL
cd ../unifiedui/scripts/debug
uv run --with httpx python -i foundry_smoke.py

>>> ping("gpt-4.1")           # Expect: PONG
>>> ask("gpt-4.1", "Refactor this prompt for brevity: <text>")
>>> chat("gpt-4.1", [{"role":"system","content":"You are terse."},{"role":"user","content":"hi"}])
>>> list_models()              # Catalog (NOT actual deployments)
```

**API-key path**: only `/responses`, `/chat/completions`, `/models` work. Project agent CRUD requires AAD (`az login` + Azure AI Developer role) — out of scope unless the user grants it.

**Naming convention**: any Foundry resource Copilot creates MUST start with `co-debug-`. Never modify or delete resources without that prefix.

---

## Safety Rules for Copilot

1. **Never run `DROP`, `TRUNCATE`, `DELETE` without WHERE, `FLUSHALL`, `db.dropDatabase()`, or `docker compose down -v` without explicit user consent.**
2. **All SELECT/find queries are safe** — read freely.
3. **Backdoor (REQ 007) > raw DB writes**: prefer authenticated API calls via the backdoor over direct DB mutations whenever possible.
4. **Production**: this toolkit MUST NOT be pointed at production. Only local docker-compose.

---

## Related Files

- [db_inspect.py](db_inspect.py) — Python connection helper
- [`unifiedui/docker/local/.env.example`](../../docker/local/.env.example) — credential reference
- [`007_DEBUG_BACKDOOR_v024.REQ.md`](../../docs/requirements-changelog/007_DEBUG_BACKDOOR_v024.REQ.md) — full requirements
