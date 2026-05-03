# 007 — Debug Backdoor (E2E Testing & Self-Debugging) v0.24.0

> **Status:** DRAFT
> **Scope:** unified-ui-platform-service, unified-ui-agent-service, unified-ui-frontend-service (re-act-agent-service vorerst ausgeklammert)
> **Ziel:** Copilot/Playwright in die Lage versetzen, die App (FE + BE) **fast vollständig selbst zu testen, debuggen und Bugs zu fixen**, ohne echte MSAL-/Google-OAuth-Flows. Eine kontrollierte Backdoor-Auth wird per Env-Variable aktivierbar gemacht und ist standardmäßig **strikt deaktiviert**. Zusätzlich: dokumentierter direkter Datenbank-Zugriff (Postgres, Mongo, Redis) für Kontext-Recherche.

---

## Arbeitsweise & Prozess

> **Dieses Dokument ist das zentrale Tracking- und Anforderungsdokument.**

### Ablauf pro Paket

1. **Implementierungsübersicht** im Chat (Dateien, Ansatz)
2. **Review** durch Nutzer
3. **Implementierung** des kompletten Pakets
4. **Testhinweise** (Stichpunkte)
5. **Test & Feedback**
6. **Abschluss** → `✅ Done` Marker

### Status-Tracking

- *(kein Marker)* → Noch nicht begonnen
- `⏳ In Progress` → Gerade in Bearbeitung
- `✅ Done` → Fertig

### Regeln

- Backdoor **niemals** in Production deployen → harte Checks (siehe Paket 0)
- Jeder Backdoor-Use → `WARNING`-Log mit User/Endpoint/IP
- Beim Service-Start mit `ENABLE_DEBUG_BACK_DOOR=true` → permanenter Banner-Log alle 30 s
- Nach jedem Paket: `pre-commit run --all-files`

---

## Kontext & Architekturentscheidungen

### Problem

Die App nutzt MSAL / Google OAuth. Copilot kann diese Flows nicht durchlaufen → kann keine echten E2E-Tests gegen laufende Services machen. Bisher: jeder Test braucht entweder Mocks oder einen menschlich beschafften Token. Das macht autonomes Debugging unmöglich.

### Lösung

**Eine** Env-Variable `ENABLE_DEBUG_BACK_DOOR=true` (default `false`) öffnet pro Service einen **klar isolierten Backdoor-Pfad**:

#### Backend (Platform-Service, Agent-Service, ReAct-Agent-Service)

- Im `@authenticate`-Decorator/Middleware: Wenn Backdoor aktiv UND Header `X-Debug-Backdoor: <SHARED_SECRET>` UND `X-Debug-User-Id: <id>` UND `X-Debug-User-UPN: <upn>` gesetzt → Token-Validierung wird **übersprungen** und ein synthetischer User-Context wird erzeugt.
- Optional: `X-Debug-Tenant-Id`, `X-Debug-Roles` (CSV: `TENANT_GLOBAL_ADMIN,...`), `X-Debug-Groups` (CSV).
- Defaults wenn nicht gesetzt: User wird als `SUPERADMIN` im Test-Tenant geführt.
- Service-API-Key-Auth (`@authenticate_service_key`, Autonomous-Agent-Key) bleibt unverändert — die kann Copilot bereits aufrufen.

#### Frontend

- Wenn `VITE_ENABLE_DEBUG_BACK_DOOR=true` → auf Login-Page erscheint zusätzlicher Button **„Debug Backdoor Login"** (nur sichtbar bei aktivierter Flag, **nie** in Prod-Build).
- Klick → ruft `/api/v1/platform-service/auth/debug-backdoor` auf, holt JWT (Backend stellt diesen aus, wenn Backdoor aktiv) und setzt ihn ins ApiClient + LocalStorage.
- Danach läuft die App identisch zur normalen Session → Playwright kann frei navigieren.

### Sicherheit (Hartes Set von Guardrails)

| Guardrail | Implementierung |
|-----------|----------------|
| Default-OFF | Env-Var muss explizit `true` gesetzt sein |
| Production-Block | Wenn `APP_ENVIRONMENT=production` (oder `prod`) → Service crasht beim Start mit Fatal-Error, falls Backdoor aktiv |
| Shared-Secret | Backdoor-Header benötigt zusätzlich `X-Debug-Backdoor: <secret>` (aus Env `DEBUG_BACK_DOOR_SECRET`, mind. 32 Zeichen) — verhindert versehentliche Aktivierung in Staging |
| Visible-Banner | Beim Start `WARNING`-Log: `=== DEBUG BACKDOOR ENABLED — DO NOT USE IN PRODUCTION ===` (alle 30 s wiederholt) |
| Audit-Log | Jeder Request via Backdoor → `WARNING`-Log mit `user_id`, `endpoint`, `client_ip`, `user_agent` |
| Health-Endpoint | `/health` zeigt Feld `debug_backdoor_enabled: true` an → einfach extern monitorbar |
| FE-Build-Time | Wenn Vite-Build mit `MODE=production` → Backdoor-Code wird statisch eliminiert (`if (import.meta.env.PROD) return null`) |
| CI/CD | GitHub-Actions-Step prüft, dass `ENABLE_DEBUG_BACK_DOOR` nicht in Prod-Manifests/Helm-Charts gesetzt ist |

### Self-Service Workflow für Copilot (wird in Instructions dokumentiert)

```
1. docker compose -f docker/local/docker-compose.yml up -d
2. pip install requests  # oder Playwright für FE
3. response = requests.post(
     "http://localhost:8000/api/v1/platform-service/tenants/<id>/chat-agents",
     headers={
       "X-Debug-Backdoor": os.environ["DEBUG_BACK_DOOR_SECRET"],
       "X-Debug-User-Id": "test-user-1",
       "X-Debug-User-UPN": "copilot@test.local",
       "X-Debug-Roles": "TENANT_GLOBAL_ADMIN",
     },
     json={...}
   )
4. → echte Response aus echtem Service mit echter DB
5. Bug erkannt → Code fixen → Service reload (uvicorn --reload) → erneut testen
```

---

## Pakete

### Paket 0: Backend Backdoor — Platform-Service

> Foundation. Implementiert den Backdoor-Mechanismus im Platform-Service als Referenz für die anderen Services.

#### 0.1 Configuration

| ID | Anforderung |
|----|-------------|
| 0.1.1 | `Settings` (`unifiedui/core/config.py`) erhält `enable_debug_back_door: bool = False` und `debug_back_door_secret: str \| None = None` |
| 0.1.2 | Production-Check: Wenn `app_environment in {"production", "prod"}` und `enable_debug_back_door=True` → `RuntimeError` beim App-Start (verhindert Deployment) |
| 0.1.3 | Wenn `enable_debug_back_door=True` aber `debug_back_door_secret` leer oder < 32 Zeichen → `RuntimeError` beim Start |
| 0.1.4 | Beim Start: prominenter `WARNING`-Log; periodischer Reminder-Log alle 30 s im Hintergrund-Task |

#### 0.2 Auth-Decorator-Erweiterung

| ID | Anforderung |
|----|-------------|
| 0.2.1 | `@authenticate` (`unifiedui/core/middleware/apis/v1/auth.py`) prüft als ersten Schritt: wenn Backdoor aktiv + Header `X-Debug-Backdoor` matched secret + `X-Debug-User-Id`/`X-Debug-User-UPN` gesetzt → erzeuge `ContextIdentityUser` synthetisch und überspringe Token-Validierung |
| 0.2.2 | Synthetische User-Felder: `id` aus Header, `upn`/`email` aus Header, `roles` aus `X-Debug-Roles` CSV (default `TENANT_GLOBAL_ADMIN`), `groups` aus `X-Debug-Groups` CSV (default `[]`), `tenants`-Liste enthält Standard-Test-Tenant mit allen Rollen |
| 0.2.3 | Backdoor-Use → `WARNING`-Log mit `endpoint`, `method`, `user_id`, `upn`, `client_ip`, `user_agent` |
| 0.2.4 | `@authenticate_service_key` und `@authenticate_autonomous_agent_api_key` bleiben unverändert |
| 0.2.5 | `check_permissions` prüft synthetische Rollen identisch zu echten — kein Bypass der Permission-Logik |

#### 0.3 Debug-Login-Endpoint (für Frontend)

| ID | Anforderung |
|----|-------------|
| 0.3.1 | Neuer Endpoint `POST /api/v1/platform-service/auth/debug-backdoor` — nur registriert wenn Backdoor aktiv |
| 0.3.2 | Request-Body: `{ user_id, upn, tenant_id?, roles?, groups? }` |
| 0.3.3 | Response: gültiger JWT (selbe Sign-Key wie regulärer JWT, kurze TTL = 1 h, Claim `debug=true`) + User-Info |
| 0.3.4 | Endpoint-Aufrufe → `WARNING`-Log |
| 0.3.5 | OpenAPI-Schema-Dokumentation mit roter Warnung im Description-Feld |

#### 0.4 Health-Endpoint Erweiterung

| ID | Anforderung |
|----|-------------|
| 0.4.1 | `GET /health` Response enthält `"debug_backdoor_enabled": true/false` |

#### 0.5 Tests

| ID | Anforderung |
|----|-------------|
| 0.5.1 | Tests: Backdoor disabled → Header werden ignoriert |
| 0.5.2 | Tests: Backdoor enabled, fehlendes Secret → 401 |
| 0.5.3 | Tests: Backdoor enabled, falsches Secret → 401 |
| 0.5.4 | Tests: Backdoor enabled, korrekt → User wird synthetisch erstellt, Endpoint funktioniert |
| 0.5.5 | Tests: `app_environment=production` + Backdoor=on → App startet nicht |
| 0.5.6 | Tests: `/auth/debug-backdoor` gibt JWT aus, der von `@authenticate` akzeptiert wird |

---

### Paket 1: Backend Backdoor — Agent-Service (Go)

> Gleiche Mechanik wie Paket 0, übersetzt in Go/Gin.

#### 1.1

| ID | Anforderung |
|----|-------------|
| 1.1.1 | `Config` (`internal/config/config.go`) erhält `EnableDebugBackDoor bool` und `DebugBackDoorSecret string`, beides aus Env |
| 1.1.2 | Production-Check beim Start (gleich wie 0.1.2) |
| 1.1.3 | Auth-Middleware (`internal/api/middleware/auth.go` o.ä.) prüft Backdoor-Header zuerst, erzeugt synthetischen User-Context |
| 1.1.4 | Backdoor-Use → `slog.Warn` mit allen Feldern |
| 1.1.5 | `/health`-Handler enthält `debug_backdoor_enabled` |
| 1.1.6 | Periodischer Banner-Log alle 30 s wenn aktiv (goroutine im `main.go`) |
| 1.1.7 | Tests analog zu 0.5 |

---

### Paket 2: Direct Database Inspection (Documentation only)

> Kein Code — nur dokumentierter Workflow, damit Copilot direkt in Postgres / Mongo / Redis schauen kann, um Kontextdaten zu ziehen (z.B. einen vorhandenen Tenant auswählen, eine Chat-Agent-ID nachschlagen, einen Session-Cache zu inspizieren).

#### 2.1 Connection-Cheatsheet

| ID | Anforderung |
|----|-------------|
| 2.1.1 | Datei `unifiedui/scripts/debug/db_inspect.md` mit Connection-Strings für alle lokalen DBs aus `docker/local/docker-compose.yml` (Postgres URL, Mongo URI, Redis URL) und Default-Credentials |
| 2.1.2 | Beispiel-Queries für häufige Lookups: `SELECT id, name FROM tenants;`, `SELECT id, name, type FROM chat_agents WHERE tenant_id = '...';`, Mongo `db.messages.find({conversationId: '...'}).limit(5)`, Redis `KEYS dashboard:stats:*` |
| 2.1.3 | Python-Helper `unifiedui/scripts/debug/db_inspect.py` mit Funktionen `pg_query(sql)`, `mongo_find(collection, filter)`, `redis_get(key)` — lest Credentials aus Env oder `docker compose` Defaults |
| 2.1.4 | Notebook `unifiedui/scripts/debug/db_inspect.ipynb` mit vorbereiteten Cells für typische Recherchen (Tenant auswählen, User-Roles inspizieren, Conversation-Stats) |

#### 2.2 Repo-Instructions

| ID | Anforderung |
|----|-------------|
| 2.2.1 | Top-Repo `unifiedui/.github/copilot-instructions.md` ergibt eine neue Sektion **"Direct DB Inspection"** mit Verweis auf die Cheatsheet-Datei |
| 2.2.2 | Klare Regel: **NUR für lokale Entwicklung** — niemals gegen produktive DBs |
| 2.2.3 | Klare Regel: **Read-only by default** — Mutationen nur mit explizitem User-OK |

---

### Paket 3: Frontend Backdoor Login

> Sichtbar in Dev-/Test-Environment, build-time entfernt in Prod.

#### 3.1 Konfiguration

| ID | Anforderung |
|----|-------------|
| 3.1.1 | `VITE_ENABLE_DEBUG_BACK_DOOR` (boolean) und `VITE_DEBUG_BACK_DOOR_SECRET` in `.env.example` und `vite-env.d.ts` |
| 3.1.2 | Build-Time-Guard: gesamter Backdoor-Code in `if (import.meta.env.PROD) {...return null}` gewrapped — wird tree-shaked in Prod-Build |

#### 3.2 Login-UI

| ID | Anforderung |
|----|-------------|
| 3.2.1 | `LoginPage` zeigt sekundären Outline-Button **„Debug Backdoor Login"** unterhalb der MSAL-/Google-Buttons, nur wenn Flag aktiv. Roter Warning-Banner darüber: `⚠ DEBUG MODE — DO NOT USE IN PRODUCTION` |
| 3.2.2 | Klick öffnet kleines Modal: Felder `User ID` (default `copilot-debug`), `UPN` (default `copilot@debug.local`), `Tenant` (Auto-Detect via API-Call falls möglich), `Roles` (Multi-Select, default `TENANT_GLOBAL_ADMIN`) |
| 3.2.3 | Submit → `POST /auth/debug-backdoor` mit Secret-Header → JWT speichern → identisch zur normalen Session weiter (Redirect `/home`) |
| 3.2.4 | LocalStorage-Key für Backdoor-JWT klar markiert: `auth_token_debug` (separater Key, damit normale Sessions nicht überschrieben werden) |

#### 3.3 Visual Indicator nach Login

| ID | Anforderung |
|----|-------------|
| 3.3.1 | Wenn aktive Session via Backdoor → permanenter roter Banner ganz oben in `MainLayout`: `🐛 DEBUG SESSION — User: <upn>` mit Logout-Button |

#### 3.4 Playwright-friendly Hooks

| ID | Anforderung |
|----|-------------|
| 3.4.1 | Backdoor-Login-Button erhält stabile Test-IDs: `data-testid="backdoor-login-trigger"`, `data-testid="backdoor-login-submit"` |
| 3.4.2 | Banner: `data-testid="debug-session-banner"` |

---

### Paket 4: Dokumentation & Instructions

> Damit Copilot weiß, wie es self-service debuggt.

#### 4.1 Repo-Instructions Updates

| ID | Anforderung |
|----|-------------|
| 4.1.1 | `unified-ui-platform-service/.github/instructions/debug-backdoor.instructions.md` neu — komplette Anleitung mit Beispiel-Curl + Python-Snippet |
| 4.1.2 | Gleiche Datei in agent-service, react-agent-service, frontend-service |
| 4.1.3 | Jeweiliges `copilot-instructions.md` indiziert die neue Datei mit „Read when... debugging endpoints / running E2E tests" |
| 4.1.4 | Top-Repo `unifiedui/docs/DEBUG_BACKDOOR.md` mit Übersicht über alle Services, Default-Ports, Secret-Setup |

#### 4.2 Beispiel-Skripte

| ID | Anforderung |
|----|-------------|
| 4.2.1 | `unifiedui/scripts/debug/test_endpoint.py` — Python-Helper, der Backdoor-Headers automatisch baut, Endpoint aufruft, Response printet |
| 4.2.2 | `unifiedui/scripts/debug/playwright_login.py` — Playwright-Snippet das automatisch Backdoor-Login durchläuft und einen Cookie/Token zurückgibt |
| 4.2.3 | `docker/local/.env.debug.example` — fertiges Env-File mit Backdoor + Secret für lokale Entwicklung |

#### 4.3 Docker-Compose

| ID | Anforderung |
|----|-------------|
| 4.3.1 | `docker/local/docker-compose.yml` erhält Kommentar-Block, wie Backdoor pro Service zu aktivieren ist (auskommentierte env-Block-Vorlage) |
| 4.3.2 | Optional: Neues File `docker-compose.debug.yml` (Override), das Backdoor automatisch in allen Services aktiviert (`docker compose -f docker-compose.yml -f docker-compose.debug.yml up`) |

---

## Anhang

### Header-Schema (Backend)

| Header | Pflicht | Default | Beschreibung |
|--------|---------|---------|--------------|
| `X-Debug-Backdoor` | ja | — | Shared-Secret aus `DEBUG_BACK_DOOR_SECRET` |
| `X-Debug-User-Id` | ja | — | Synthetische User-ID (UUID-Format empfohlen) |
| `X-Debug-User-UPN` | ja | — | E-Mail/UPN |
| `X-Debug-Tenant-Id` | nein | erster Test-Tenant | Tenant-Scope |
| `X-Debug-Roles` | nein | `TENANT_GLOBAL_ADMIN` | CSV der Tenant-Roles |
| `X-Debug-Groups` | nein | `[]` | CSV der Custom-Group-IDs |

### Env-Variablen pro Service

| Service | Variable | Default |
|---------|----------|---------|
| Platform | `ENABLE_DEBUG_BACK_DOOR` | `false` |
| Platform | `DEBUG_BACK_DOOR_SECRET` | leer |
| Agent | `ENABLE_DEBUG_BACK_DOOR` | `false` |
| Agent | `DEBUG_BACK_DOOR_SECRET` | leer |
| Frontend | `VITE_ENABLE_DEBUG_BACK_DOOR` | `false` |
| Frontend | `VITE_DEBUG_BACK_DOOR_SECRET` | leer |

*ReAct-Agent-Service ist vorerst nicht im Scope und behält seine bisherige Auth.*

### Issue-Referenz

Dieses Feature ist eine **Querschnitts-Anforderung**, nicht direkt einem Issue zugeordnet. Es ist Voraussetzung für autonomes Debugging aller weiteren REQs (008, 009, 010).
