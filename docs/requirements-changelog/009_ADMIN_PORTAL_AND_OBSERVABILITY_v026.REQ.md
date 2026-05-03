# 009 — Admin Portal & Observability v0.26.0

> **Status:** DRAFT
> **Scope:** unified-ui-platform-service, unified-ui-agent-service, unified-ui-frontend-service
> **Ziel:** Vollständiger **Admin-Portal**-Bereich (`/admin/*`), zentralisierte **Telemetrie-Erfassung** (Tokens, Latency, Feedback) als Foundation für Analytics-Dashboards, **Audit-Log**-System für Compliance, und **Detail-Seiten** für Chat-Agents/Workflows mit eingebetteten Analytics.
> **Issues:** [#22](https://github.com/unified-ui/unifiedui/issues/22), [#30](https://github.com/unified-ui/unifiedui/issues/30), [#31](https://github.com/unified-ui/unifiedui/issues/31), [#32](https://github.com/unified-ui/unifiedui/issues/32), [#33](https://github.com/unified-ui/unifiedui/issues/33), [#34](https://github.com/unified-ui/unifiedui/issues/34), [#35](https://github.com/unified-ui/unifiedui/issues/35)

---

## Arbeitsweise & Prozess

> Standard-Ablauf: Übersicht → Review → Implementation → Testhinweise → Review → Done. Nach jedem Paket `pre-commit run --all-files`.

### Status-Tracking

- *(kein Marker)* | `⏳ In Progress` | `✅ Done`

### Voraussetzung

REQ 007 (Debug Backdoor) sollte vorher fertig sein, damit Copilot die neuen Endpoints + Pages selbständig E2E-testen kann.

---

## Kontext & Architekturentscheidungen

### Aktueller Stand

| Bereich | Status | Datei |
|---------|--------|-------|
| `/admin`-Routen-Group | ❌ existiert nicht | — |
| Admin-Pages | ⚠️ alle als Tabs in `TenantSettingsPage` (`?tab=iam/credentials/tools/ai-models/custom-groups`) | `src/pages/TenantSettingsPage` |
| Token/Latency-Capture | ⚠️ in Mongo `messages.metadata` (TokensInput/Output/LatencyMs) | `agent-service/internal/domain/models/messages.go` |
| Feedback-Capture | ⚠️ in Mongo `message_reactions` (FeedbackText Freitext, **keine strukturierten Reasons**) | `agent-service/internal/domain/models/reaction.go` |
| Audit-Log | ❌ existiert nicht | — |
| Analytics-Endpoints | ❌ existieren nicht | — |
| `WorkflowDetailsPage` | ✅ existiert mit Tabs `traces/runs/details` | `src/pages/WorkflowDetailsPage` |
| `ChatAgentDetailsPage` | ❌ existiert nicht (nur ListPage) | — |

### Architektur-Entscheidungen

#### 1. Wo werden Telemetrie-Daten gespeichert?

**Entscheidung:** Hybrid.
- **Source-of-Truth bleibt agent-service Mongo** (`messages.metadata` → Tokens, Latency, Model, AgentType)
- **Materialisiert in platform-service SQL** (`message_metric` Tabelle, factory-pattern PostgreSQL/Azure-SQL/CosmosDB) für Aggregations-Queries
- Fluss: agent-service emittiert nach jedem `MESSAGE_COMPLETE`-Event einen async HTTP-Call `POST /platform-service/internal/metrics/messages` (mit Service-Key) → platform-service schreibt eine Zeile pro assistant-message
- **Warum:** Aggregationen über Wochen/Monate/Tausende Messages brauchen Indizes + Group-By, das Mongo-Aggregation-Pipeline langsam und teuer macht. Mongo bleibt für volle Message-Inhalte zuständig.

#### 2. Wo wird Feedback gespeichert?

**Entscheidung:** Migration nach platform-service SQL (factory pattern).
- Neue Tabelle `message_feedback` (multi-DB via factory pattern)
- FK: `tenant_id`, `conversation_id` (FK auf `conversations.id`), `message_id` (kein FK — bleibt in Mongo, logical reference), `user_id`, `rating` (`THUMBS_UP`/`THUMBS_DOWN`), `reasons` (JSON Array von Enum-Werten), `comment` (Freitext)
- agent-service-Endpoint `POST .../reactions` proxied weiterhin existierend, schreibt aber via API in platform-service statt Mongo
- One-Off-Migration-Script: alle existierenden Mongo-Reactions → SQL übertragen, danach Mongo-Collection deprecaten (read-only für Backward-Compat 30 Tage, dann löschen)

#### 3. Wo wird Audit-Log gespeichert?

**Entscheidung:** SQL via factory pattern (PostgreSQL/Azure-SQL/CosmosDB).
- **Capture-Mechanismus:** Decorator `@audit_event(resource_type=..., action=...)` auf Handler-Methoden
- Diff-Capture: Entity-State vor/nach Update via SQLAlchemy-Snapshot oder explizite Übergabe
- Async-Write: Audit-Log-Write läuft via `BackgroundTasks` (FastAPI), damit es Resource-Operationen nicht blockt
- **Bei Audit-Write-Error:** Loggen mit `ERROR`-Level, Resource-Operation NICHT zurückrollen (Audit darf User-Operationen nie blockieren)

#### 4. Multi-DB / Factory Pattern

Alle neuen Tabellen (`message_metric`, `message_feedback`, `audit_log`, optional `model_pricing`) müssen mit allen unterstützten Backends funktionieren:
- PostgreSQL (existing)
- Azure SQL Server (existing)
- CosmosDB (NoSQL — via existing factory)

Dafür:
- Models in `unifiedui/core/database/models.py` (SQLAlchemy für SQL)
- Parallel CosmosDB-Repository-Implementierung im selben Pattern wie existierende Resources
- Kein vendor-spezifisches SQL (`JSON_VALUE`, `MERGE`, etc.) — nur portable SQLAlchemy-API + JSON-Field-Validators

### Routen-Mapping (Frontend Refactor)

User hat bestätigt: voller Refactor erlaubt, **keine Backward-Compat**.

| Alt (raus) | Neu |
|------------|-----|
| `/tenant-settings?tab=iam` | `/admin/principals` |
| `/tenant-settings?tab=credentials` | `/admin/credentials` |
| `/tenant-settings?tab=tools` | `/admin/tools` |
| `/tenant-settings?tab=ai-models` | `/admin/ai-models` |
| `/tenant-settings?tab=custom-groups` | `/admin/custom-groups` |
| `/tenant-settings` (sonstige Settings) | `/admin/tenant-settings` |
| (neu) | `/admin/dashboard` |
| (neu) | `/admin/audit-log` |
| (neu) | `/admin/chat-agents/analytics` |
| (neu) | `/admin/workflows/analytics` |
| (neu) | `/chat-agents/:id` (Details, nicht /admin) |

---

## Pakete

### Paket 0: Telemetry-Foundation (Tokens, Latency, Cost) ⏳

> Backend-Infrastruktur für alle weiteren Analytics-Pakete. Muss zuerst stehen.

#### 0.1 Schema in Platform-Service

| ID | Anforderung |
|----|-------------|
| 0.1.1 | Neue Tabelle `message_metric` (`unifiedui/core/database/models.py`) mit Spalten: `id` (UUID PK), `tenant_id` (FK), `chat_agent_id` (FK nullable), `workflow_id` (FK nullable), `conversation_id` (FK nullable), `message_id` (str, indexed, kein FK — Mongo-Reference), `user_id` (FK), `provider` (str, z.B. `AZURE_OPENAI`), `model` (str), `tokens_input` (int), `tokens_output` (int), `latency_ms` (int), `agent_type` (str — Enum-String aus `ChatAgentTypeEnum`/`WorkflowTypeEnum`), `status` (str: `success`/`failed`/`canceled`), `error_code` (str nullable), `created_at` (timestamp, indexed) |
| 0.1.2 | Composite-Indizes: `(tenant_id, created_at)`, `(tenant_id, chat_agent_id, created_at)`, `(tenant_id, workflow_id, created_at)` für schnelle Aggregations-Queries |
| 0.1.3 | Alembic-Migration |
| 0.1.4 | CosmosDB-Implementierung (analog zu existierenden Resources) |
| 0.1.5 | Pydantic Request/Response: `MessageMetricCreateRequest`, `MessageMetricResponse` |

#### 0.2 Internal-Endpoint

| ID | Anforderung |
|----|-------------|
| 0.2.1 | Neuer Router `apis/v1/internal/metrics.py` mit `POST /api/v1/platform-service/internal/metrics/messages` (geschützt via `@authenticate_service_key`) |
| 0.2.2 | Bulk-Variante `POST /metrics/messages:batch` (max 100/Batch) für höhere Effizienz |
| 0.2.3 | Idempotenz: Wenn `message_id` bereits existiert → Update statt Insert |

#### 0.3 Agent-Service Emitter

| ID | Anforderung |
|----|-------------|
| 0.3.1 | Neue Komponente `internal/services/telemetry/emitter.go` |
| 0.3.2 | Hooks nach jedem Message-Save in `messages_send.go` (success), `messages_helpers.go` (canceled, failed) |
| 0.3.3 | Async via Goroutine + Buffered Channel (Buffer 1000); bei Buffer-Overflow → Drop + `WARN`-Log + Metric `telemetry_drops_total` |
| 0.3.4 | Bulk-Send alle 5 s oder bei 100 Items |
| 0.3.5 | Bei Platform-Service-Unreachability → Retry mit Exponential-Backoff, max 3 Retries, dann Drop + Log |

#### 0.4 Tests

| ID | Anforderung |
|----|-------------|
| 0.4.1 | Backend: Endpoint-Tests (Permission, Idempotenz, Batch) |
| 0.4.2 | CosmosDB-Variante: Smoke-Test mit Cosmos-Emulator |
| 0.4.3 | Agent-Service: Emitter-Tests (Buffer, Retry, Drop) |

---

### Paket 1: Feedback-Migration nach Platform-Service ⏳ depends on 0

> Migration der Reactions/Feedback aus Mongo nach SQL/CosmosDB + Erweiterung um strukturierte Reasons.

#### 1.1 Schema in Platform-Service

| ID | Anforderung |
|----|-------------|
| 1.1.1 | Neue Tabelle `message_feedback` mit: `id`, `tenant_id`, `conversation_id` (FK), `message_id` (string, indexed), `user_id` (FK), `rating` (`THUMBS_UP`/`THUMBS_DOWN`), `reasons` (JSONB/JSON: Array von Enum-Werten), `comment` (Text nullable), `created_at`, `updated_at` |
| 1.1.2 | Neuer Enum `MessageFeedbackReasonEnum`: `HALLUCINATION`, `TOO_SLOW`, `FORMATTING`, `INACCURATE`, `INAPPROPRIATE`, `INCOMPLETE`, `OTHER` |
| 1.1.3 | Pydantic-Validator für `reasons[]` (alle Werte aus Enum) |
| 1.1.4 | Unique-Constraint `(tenant_id, message_id, user_id)` (eine Reaction pro User pro Message) |
| 1.1.5 | Alembic-Migration + CosmosDB-Implementierung |

#### 1.2 Endpoints in Platform-Service

| ID | Anforderung |
|----|-------------|
| 1.2.1 | `POST /api/v1/platform-service/tenants/{tenant_id}/conversations/{conv_id}/messages/{msg_id}/feedback` (Upsert) |
| 1.2.2 | `GET .../messages/{msg_id}/feedback` (eigenes Feedback) |
| 1.2.3 | `DELETE .../messages/{msg_id}/feedback` |
| 1.2.4 | `GET .../conversations/{conv_id}/feedback` (alle Feedbacks der Conversation) |
| 1.2.5 | Permission: User darf nur eigenes Feedback ändern; Admins sehen alle |

#### 1.3 Agent-Service-Proxy

| ID | Anforderung |
|----|-------------|
| 1.3.1 | Existing `POST .../messages/{id}/reactions` (agent-service) wird umgeschrieben: forwarded an platform-service via Service-Key |
| 1.3.2 | Mongo-Reactions-Collection wird **read-only** (deprecated), Schreib-Operationen entfernt |
| 1.3.3 | Lese-Operationen agent-service: lesen weiterhin aus Mongo bis Migration durch ist, danach von platform-service über internen API-Call |

#### 1.4 Migration-Script

| ID | Anforderung |
|----|-------------|
| 1.4.1 | `unifiedui-platform-service/scripts/migrate_feedback_from_mongo.py` — liest aus Mongo, schreibt nach SQL/CosmosDB, Idempotent (Skip wenn bereits vorhanden) |
| 1.4.2 | Mapping: `FeedbackText` → `comment`, `Reaction` → `rating`, `reasons` initial leer (nur neue Feedbacks haben Reasons) |
| 1.4.3 | Dry-Run-Modus mit Stats-Output |

#### 1.5 Tests

| ID | Anforderung |
|----|-------------|
| 1.5.1 | Endpoint-Tests inkl. RBAC |
| 1.5.2 | Migration-Script-Test mit Mock-Mongo |

---

### Paket 2: Audit-Log Foundation ⏳

> Unabhängig von 0/1, kann parallel laufen.

#### 2.1 Schema

| ID | Anforderung |
|----|-------------|
| 2.1.1 | Neue Tabelle `audit_log`: `id`, `tenant_id`, `timestamp` (indexed), `actor_id`, `actor_email`, `action` (Enum), `resource_type` (Enum), `resource_id`, `resource_name`, `changes` (JSON nullable: `{before: {...}, after: {...}}`), `client_ip` (str nullable), `user_agent` (str nullable) |
| 2.1.2 | Neuer Enum `AuditActionEnum`: `CREATE`, `UPDATE`, `DELETE`, `MEMBER_ADD`, `MEMBER_REMOVE`, `ROLE_CHANGE`, `EXECUTE` |
| 2.1.3 | Neuer Enum `AuditResourceTypeEnum`: `CHAT_AGENT`, `WORKFLOW`, `CREDENTIAL`, `TOOL`, `TAG`, `PRINCIPAL`, `CUSTOM_GROUP`, `AI_MODEL`, `EXTERNAL_APP`, `TENANT_SETTING` |
| 2.1.4 | Indizes: `(tenant_id, timestamp)`, `(tenant_id, resource_type, timestamp)`, `(tenant_id, actor_id, timestamp)` |
| 2.1.5 | Alembic + CosmosDB-Implementation |

#### 2.2 Decorator

| ID | Anforderung |
|----|-------------|
| 2.2.1 | Neuer Decorator `@audit_event(resource_type, action)` in `unifiedui/core/middleware/audit.py` |
| 2.2.2 | Signatur erlaubt `resource_id_arg` und `resource_name_arg` als Keyword zur Auflösung aus Function-Args |
| 2.2.3 | Bei `UPDATE`: Decorator erwartet, dass Handler vorher und nachher den Entity-State zurückgibt (oder via Hook); Diff via `dictdiffer` |
| 2.2.4 | Audit-Write erfolgt async via `BackgroundTasks` |
| 2.2.5 | Bei Audit-Write-Error: `logger.error("Audit log write failed", extra={...}, exc_info=True)` — keine Exception nach außen |
| 2.2.6 | Decorator extrahiert `actor_id`, `actor_email` aus `ContextIdentityUser` (Dependency-Injection vorausgesetzt) |
| 2.2.7 | Wenn Aufruf via Debug-Backdoor (REQ 007) → Audit-Entry markiert `actor_email` mit Suffix ` (DEBUG)` |

#### 2.3 Endpoints

| ID | Anforderung |
|----|-------------|
| 2.3.1 | `GET /api/v1/platform-service/tenants/{tenant_id}/admin/audit-log` mit Query-Params: `actor_id`, `resource_type`, `resource_id`, `action`, `from`, `to`, `q` (search in `resource_name`), `cursor`, `limit` (max 100, default 50) |
| 2.3.2 | Cursor-Pagination (created_at + id) für stabile Infinite-Scroll |
| 2.3.3 | `GET .../audit-log/{id}` für Detail-View mit vollem Diff |
| 2.3.4 | `GET .../audit-log/export?format=csv|json` (Streaming für große Exports, Limit 100k Records) |
| 2.3.5 | RBAC: nur ADMIN/SUPERADMIN |

#### 2.4 Decorator-Anwendung

| ID | Anforderung |
|----|-------------|
| 2.4.1 | Anwendung auf alle Resource-Handler: chat_agents, workflows, credentials, tools, tags, principals, custom_groups, ai_models, external_apps, tenant_settings (CREATE/UPDATE/DELETE/MEMBER_ADD/MEMBER_REMOVE) |
| 2.4.2 | Sensible Felder werden im Diff redacted (z.B. `secret`, `password`, `client_secret`, `api_key`) — Redaction-Liste konfigurierbar |

#### 2.5 Retention-Job

| ID | Anforderung |
|----|-------------|
| 2.5.1 | Background-Task (cron-like, daily) löscht Audit-Entries älter als `audit_retention_days` (Setting, default 90) |
| 2.5.2 | Konfigurierbar pro Tenant (zukünftig, vorerst global) |

#### 2.6 Tests

| ID | Anforderung |
|----|-------------|
| 2.6.1 | Decorator-Tests: korrekte Capture, Diff-Generation, Redaction, Async-Behavior, Error-Logging |
| 2.6.2 | Endpoint-Tests: Filter-Kombinationen, Pagination, Export, RBAC |

---

### Paket 3: Aggregation-Endpoints ⏳ depends on 0, 1

> Analytics-Endpoints, die `message_metric` und `message_feedback` aggregieren.

#### 3.1 Chat-Agent-Analytics

| ID | Anforderung |
|----|-------------|
| 3.1.1 | `GET /admin/analytics/chat-agents` (tenant-scoped) — Query: `from`, `to`, `agent_ids[]`, `granularity` (day/week) |
| 3.1.2 | Response: `{ kpis: {total_messages, total_tokens_input, total_tokens_output, avg_latency_ms, feedback_score, error_rate}, token_series: [{date, tokens_in, tokens_out}], top_agents_by_tokens: [{agent_id, name, total_tokens}], feedback_breakdown: [{rating, reasons[], count}], performance: [{agent_id, avg_latency, error_rate}] }` |
| 3.1.3 | RBAC: ADMIN/SUPERADMIN |
| 3.1.4 | Caching: 60 s pro Filter-Kombination (Redis) |

#### 3.2 Workflow-Analytics

| ID | Anforderung |
|----|-------------|
| 3.2.1 | `GET /admin/analytics/workflows` — analoge Struktur, dazu: `total_executions`, `success_rate`, `avg_duration_s`, `executions_series`, `recent_executions[]` |

#### 3.3 Per-Resource-Analytics

| ID | Anforderung |
|----|-------------|
| 3.3.1 | `GET /chat-agents/{id}/analytics` — gleiche Struktur wie 3.1, aber pre-filtered |
| 3.3.2 | `GET /workflows/{id}/analytics` — gleiche Struktur wie 3.2, pre-filtered |
| 3.3.3 | Permission: ADMIN/SUPERADMIN ODER User mit Read-Permission auf die spezifische Resource |

#### 3.4 Tests

| ID | Anforderung |
|----|-------------|
| 3.4.1 | Mit Seed-Daten (Factories) verschiedene Aggregationen prüfen |
| 3.4.2 | Cache-Hit/Miss-Test |

---

### Paket 4: Admin Portal Shell (Frontend) ⏳

> Refactor: existierende Settings-Tabs werden eigenständige `/admin/*`-Pages. Voller Refactor — alte URLs werden entfernt (User OK).

#### 4.1 Layout & Routing

| ID | Anforderung |
|----|-------------|
| 4.1.1 | Neue Layout-Komponente `src/components/layout/AdminLayout/AdminLayout.tsx` mit `MainLayout` als Parent + linker Admin-Sidebar |
| 4.1.2 | `AdminSidebar` mit Sektionen: Overview (Dashboard), Analytics (Chat Agents, Workflows), Audit Log, Identity (Principals, Custom Groups), Resources (Credentials, Tools, AI Models, External Apps), Settings (Tenant Settings, Billing, API Docs) |
| 4.1.3 | Routes registriert in `src/routes/index.tsx` unter `/admin/*`, alle wrapped in `<AdminProtectedRoute>` |
| 4.1.4 | `AdminProtectedRoute`: prüft `usePermissions().isAdmin` — sonst Redirect auf `/home` mit Toast „Admin-Zugriff erforderlich" |
| 4.1.5 | Breadcrumb-Komponente in `AdminLayout` (z.B. `Admin > Audit Log`) |
| 4.1.6 | Mobile-Responsive: Sidebar wird Drawer auf < md |

#### 4.2 Page-Verschiebungen (kompletter Refactor)

| ID | Anforderung |
|----|-------------|
| 4.2.1 | `TenantSettingsPage` aufgesplittet: jede Tab-Sektion (iam, credentials, tools, ai-models, custom-groups) wird eine eigene Page-Komponente unter `src/pages/admin/`: `PrincipalsPage`, `CustomGroupsPage`, `CredentialsPage`, `ToolsPage`, `AIModelsPage` |
| 4.2.2 | Reine Tenant-Settings (LDAP, Branding, etc.) verbleiben als `TenantSettingsPage` unter `/admin/tenant-settings` |
| 4.2.3 | Sidebar-Hauptnavigation (`MainLayout`-Sidebar): Admin-Tabs entfernt; stattdessen ein „Admin"-Eintrag (nur sichtbar für Admins) der zu `/admin/dashboard` führt |
| 4.2.4 | Alle alten Links (`navigate('/tenant-settings?tab=...')`, Dashboard-Quick-Links, Command-Palette) auf neue Pfade aktualisiert |
| 4.2.5 | `RecentVisits` und `Favorites` Resource-Type-Mappings updaten |

#### 4.3 Dashboard-Stub

| ID | Anforderung |
|----|-------------|
| 4.3.1 | `src/pages/admin/AdminDashboardPage` als Placeholder mit Sektion-Cards (gefüllt in Paket 9) |

#### 4.4 Tests

| ID | Anforderung |
|----|-------------|
| 4.4.1 | Routing-Test: Redirect für non-Admin |
| 4.4.2 | Layout-Snapshot |

---

### Paket 5: Audit-Log UI ⏳ depends on 2, 4

| ID | Anforderung |
|----|-------------|
| 5.1.1 | `src/pages/admin/AuditLogPage` mit `DataTable`-Komponente |
| 5.1.2 | Columns: Timestamp, Actor, Action, Resource Type, Resource Name |
| 5.1.3 | Filter-Bar oben: Date-Range-Picker, Actor-MultiSelect (lädt Principals), Resource-Type-MultiSelect, Action-MultiSelect, Search-Input (Resource-Name) |
| 5.1.4 | Infinite-Scroll mit Cursor-Pagination |
| 5.1.5 | Klick auf Row → Drawer mit Detail-View: alle Felder + Diff-Visualization (`react-diff-viewer` o.ä.) für `changes` |
| 5.1.6 | Export-Button: Dropdown (CSV/JSON), respektiert aktuelle Filter |
| 5.1.7 | i18n |
| 5.1.8 | Tests |

---

### Paket 6: Chat-Agent Analytics-Page ⏳ depends on 3, 4

| ID | Anforderung |
|----|-------------|
| 6.1.1 | `src/pages/admin/ChatAgentAnalyticsPage` unter `/admin/chat-agents/analytics` |
| 6.1.2 | Filter-Bar: Date-Range, Agent-MultiSelect (lädt ChatAgents), Platform-Type-Filter (`MICROSOFT_FOUNDRY`, `LLM`, `N8N`, `REST_API`, `REACT_AGENT`) |
| 6.1.3 | KPI-Cards: Total Messages, Total Tokens (in/out split), Avg Latency, Feedback Score (mit Trend vs vorige Periode) |
| 6.1.4 | Charts (Recharts, Reuse-Komponenten in `src/components/analytics/`): Token-Series-LineChart, Top-Agents-BarChart, Feedback-Breakdown-PieChart, Performance-Table |
| 6.1.5 | Negative-Feedback-Drilldown-Tabelle: zeigt jüngste THUMBS_DOWN-Feedbacks mit Comment + Link auf Conversation |
| 6.1.6 | Loading-Skeletons, Empty-State, Error-State |
| 6.1.7 | i18n + Tests |

---

### Paket 7: Chat-Agent Details-Page ⏳ depends on 6

| ID | Anforderung |
|----|-------------|
| 7.1.1 | Neue Route `/chat-agents/:id` (NICHT unter `/admin`, da auch normale User Agent-Details sehen sollen) |
| 7.1.2 | `ChatAgentDetailsPage` mit Header (Avatar, Name, Status-Badge, Platform-Icon) + Action-Buttons (Start Chat, Edit, Delete) |
| 7.1.3 | Tabs: `Overview` (alle User), `Analytics` (nur Admins) |
| 7.1.4 | Overview-Tab: Basic-Info, Config-Summary (platform-spezifisch), Tags, Members, Recent Conversations (last 5) |
| 7.1.5 | Analytics-Tab: Reuse Komponenten aus Paket 6 mit fixiertem `agent_id` Filter |
| 7.1.6 | Breadcrumb: `Chat Agents > {Name}` |
| 7.1.7 | Backend: `GET /chat-agents/{id}/analytics` aus Paket 3.3.1 |
| 7.1.8 | i18n + Tests |

---

### Paket 8: Workflow Analytics-Tab ⏳ depends on 3

> Erweitert die existierende `WorkflowDetailsPage` um Analytics-Tab.

| ID | Anforderung |
|----|-------------|
| 8.1.1 | Neuer Tab `Analytics` in `WorkflowDetailsPage` (`src/pages/WorkflowDetailsPage`) — Position zwischen `traces` und `details` |
| 8.1.2 | Time-Range-Filter (7/30/90 Tage / Custom) |
| 8.1.3 | KPI-Cards: Total Executions, Success Rate, Avg Duration, Total Tokens (wenn AI-Workflow) |
| 8.1.4 | Charts: Executions-Over-Time, Success/Fail-PieChart, Duration-Trend-LineChart |
| 8.1.5 | Recent-Executions-Tabelle mit Status, Duration, Error, Link auf Trace-Detail |
| 8.1.6 | Empty-State, Loading-State |
| 8.1.7 | Visibility: nur Admins (Tab wird für non-Admin nicht gerendert) |
| 8.1.8 | i18n + Tests |

---

### Paket 9: Workflow Admin-Analytics-Page (Issue #32) ⏳ depends on 3

| ID | Anforderung |
|----|-------------|
| 9.1.1 | `src/pages/admin/WorkflowAnalyticsPage` unter `/admin/workflows/analytics` |
| 9.1.2 | Analoge Struktur zu Paket 6 (Chat-Agent-Analytics), aber Workflow-spezifisch (mehr Fokus auf Execution-Counts und Duration statt Tokens) |
| 9.1.3 | Filter-Bar: Date-Range, Workflow-MultiSelect, Type-Filter (`N8N`, …) |
| 9.1.4 | KPI-Cards, Charts, Recent-Failures-Drilldown |

---

### Paket 10: Admin-Dashboard Overview ⏳ depends on 5, 6, 8

> Landing-Page `/admin/dashboard` mit Aggregations aus allen Bereichen.

| ID | Anforderung |
|----|-------------|
| 10.1.1 | `AdminDashboardPage`: Quick-Stats-Cards (Total Agents, Workflows, Active-Users-Today, Conversations-Today, Avg-Feedback-Score) |
| 10.1.2 | Recent-Audit-Entries Preview (letzte 10) mit Link auf vollständigen Audit-Log |
| 10.1.3 | System-Alerts-Card (Cache-Health, Vault-Health — nutzt existierenden `/health/full` Endpoint) |
| 10.1.4 | Quick-Action-Cards: Create Agent, Create Workflow, Add Principal, Create Credential |
| 10.1.5 | i18n + Tests |

---

### Paket 11: Strukturiertes Feedback-UI im Chat ⏳ depends on 1

> Erweiterung der existierenden `FeedbackDialog`-Komponente.

| ID | Anforderung |
|----|-------------|
| 11.1.1 | Existierender `FeedbackDialog` (`src/components/chat/FeedbackDialog`) erweitert: zusätzlich zum Comment-Field eine Reasons-Multi-Checkbox-Group (alle Werte aus `MessageFeedbackReasonEnum`) |
| 11.1.2 | Schema/Types-Update in `src/api/types.ts` |
| 11.1.3 | API-Client umstellen auf neuen platform-service-Endpoint (Paket 1) |
| 11.1.4 | Reaction-Buttons (Thumbs up/down) bleiben prominent; Reasons-Dialog erscheint nur bei THUMBS_DOWN |
| 11.1.5 | Submit ist optional bei THUMBS_UP, Reasons leer (nur Comment) |
| 11.1.6 | i18n |
| 11.1.7 | Tests |

---

## Anhang

### Empfohlene Liefer-Reihenfolge

1. **Paket 0 + 2 parallel** (Telemetry-Foundation und Audit-Log unabhängig)
2. **Paket 1** (Feedback-Migration baut auf 0 nicht zwingend, kann früh laufen)
3. **Paket 3** (Aggregation braucht 0 + 1)
4. **Paket 4** (Frontend-Shell — kann parallel zu 0–3 laufen, da reiner Refactor)
5. **Paket 5** (Audit-UI — braucht 2 + 4)
6. **Paket 6 → 7 → 8/9 → 10** (Analytics-UI sequentiell wegen Komponenten-Reuse)
7. **Paket 11** (Feedback-UI — kann ab Paket 1 laufen)

### Issue-Zuordnung

| Issue | Pakete |
|-------|--------|
| #22 (Telemetry/Dashboard/Feedback) | 0, 1, 10, 11 |
| #30 (Chat-Agent-Analytics) | 3, 6 |
| #31 (Workflow-Analytics-Tab) | 8 |
| #32 (Workflow-Admin-Analytics) | 9 |
| #33 (Chat-Agent-Details-Page) | 7 |
| #34 (Audit-Log) | 2, 5 |
| #35 (Admin-Portal-Shell) | 4 |

### Sicherheit

- Alle neuen Endpoints `@authenticate` + `@check_permissions` (mind. ADMIN für `/admin/*`)
- Audit-Log-Diffs redacten alle Felder, die in `SENSITIVE_FIELDS` (Liste in `core/config.py`)
- Telemetrie-Endpoint nur via Service-Key — kein User-Auth → verhindert Manipulation
- Migration-Script läuft nur mit explizitem `--confirm` Flag
