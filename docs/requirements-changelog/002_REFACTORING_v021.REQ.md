# 002 — Workflows Refactoring & Fixes v0.2.1

> **Status:** DRAFT  
> **Scope:** unified-ui-platform-service, unified-ui-agent-service, unified-ui-frontend-service  
> **Ziel:** Vollständiges Refactoring von "autonomous_agents" zu "workflows" in allen Services, Recent Visits Überarbeitung, State-Management Review, und Icon-Farben konsistent machen.

---

## Arbeitsweise & Prozess

> **Dieses Dokument ist das zentrale Tracking- und Anforderungsdokument.**  
> Es gibt keine separate Implementierungsplan-Datei. Alles wird hier gesteuert.

### Ablauf pro Paket (0, 1, 2, …)

1. **Implementierungsübersicht**: Copilot liest den relevanten Code ein und erstellt eine kompakte Übersicht: welche Dateien betroffen sind, welcher Ansatz gewählt wird.
2. **Review**: Nutzer prüft die Übersicht, gibt OK oder Korrekturen.
3. **Implementierung**: Copilot implementiert das **gesamte Paket** (alle Teilpakete zusammen, nicht einzeln).
4. **Testhinweise**: Copilot zeigt nach Implementierung kurz auf, was der Nutzer manuell testen soll (Stichpunkte).
5. **Test & Feedback**: Nutzer testet die Implementierung und gibt Anpassungswünsche.
6. **Abschluss**: Paket wird als `✅ Done` im Titel markiert → weiter zum nächsten Paket.

### Status-Tracking

- *(kein Marker)* → Noch nicht begonnen
- `⏳ In Progress` → Gerade in Bearbeitung
- `✅ Done` → Fertig implementiert und abgenommen

### Regeln

- Immer ein **komplettes Paket** als Einheit bearbeiten.
- Nach **jedem Paket**: `pre-commit run --all-files` ausführen und alle Fehler fixen.
- Tests nach jeder Code-Änderung ausführen.

---

## Pakete

### Paket 0: Database & Enums Migration (Foundation)

> Alle `autonomous_agent*` DB-Strukturen zu `workflow*` umbenennen. Enums anpassen. Migration erstellen und ausführen. Dies ist die Grundlage für alle folgenden Pakete.

#### 0.1 Database Tabellen Umbenennung

| ID | Anforderung |
|----|-------------|
| 0.1.1 | Tabelle `autonomous_agents` → `workflows` umbenennen |
| 0.1.2 | Tabelle `autonomous_agent_members` → `workflow_members` umbenennen |
| 0.1.3 | Tabelle `autonomous_agent_tags` → `workflow_tags` umbenennen |
| 0.1.4 | Alle Foreign Key Constraints entsprechend anpassen |
| 0.1.5 | Alle Indizes entsprechend umbenennen |

#### 0.2 SQLAlchemy Models Umbenennung

| ID | Anforderung |
|----|-------------|
| 0.2.1 | Model `AutonomousAgent` → `Workflow` in `models.py` |
| 0.2.2 | Model `AutonomousAgentMember` → `WorkflowMember` in `models.py` |
| 0.2.3 | Model `AutonomousAgentTag` → `WorkflowTag` in `models.py` |
| 0.2.4 | Model `AutonomousAgentUserFavorite` → `WorkflowUserFavorite` in `models.py` |
| 0.2.5 | Alle Relationships und Back-References aktualisieren |

#### 0.3 Enums Umbenennung

| ID | Anforderung |
|----|-------------|
| 0.3.1 | Enum `AutonomousAgentTypeEnum` → `WorkflowTypeEnum` (Wert `N8N` bleibt) |
| 0.3.2 | Enum-Wert `TenantRolesEnum.AUTONOMOUS_AGENTS_ADMIN` → `WORKFLOWS_ADMIN` |
| 0.3.3 | Enum-Wert `TenantRolesEnum.AUTONOMOUS_AGENTS_CREATOR` → `WORKFLOWS_CREATOR` |
| 0.3.4 | Alembic Migration für Enum-Wert-Updates in bestehenden DB-Einträgen |

#### 0.4 Recent Visits Migration

| ID | Anforderung |
|----|-------------|
| 0.4.1 | `resource_type="autonomous_agent"` → `"workflow"` in `recent_visits` Tabelle migrieren |
| 0.4.2 | Alle `resource_type="conversation"` Einträge aus `recent_visits` löschen |

#### 0.5 Alembic Migration

| ID | Anforderung |
|----|-------------|
| 0.5.1 | Alembic Migration erstellen mit allen Tabellen-, Index-, FK-Umbenennungen |
| 0.5.2 | Migration muss Rollback-fähig sein (downgrade function) |
| 0.5.3 | Migration ausführen (`alembic upgrade head`) |

---

### Paket 1: Platform-Service Refactoring

> Alle API-Routes, Handlers, Schemas, Exceptions in platform-service von `autonomous_agent` zu `workflow` umbenennen. Keine Backward Compatibility - direktes Entfernen der alten Pfade.

#### 1.1 API Routes

| ID | Anforderung |
|----|-------------|
| 1.1.1 | Datei `apis/v1/autonomous_agents.py` → `apis/v1/workflows.py` umbenennen |
| 1.1.2 | Alle Endpoints von `/autonomous-agents/*` → `/workflows/*` umbenennen |
| 1.1.3 | Router-Registrierung in `app.py` aktualisieren |
| 1.1.4 | Alle Funktionsnamen von `*autonomous_agent*` → `*workflow*` |

#### 1.2 Handlers

| ID | Anforderung |
|----|-------------|
| 1.2.1 | Datei `handlers/autonomous_agents.py` → `handlers/workflows.py` umbenennen |
| 1.2.2 | Klasse `AutonomousAgentHandler` → `WorkflowHandler` umbenennen |
| 1.2.3 | Alle Methoden von `*autonomous_agent*` → `*workflow*` |
| 1.2.4 | Dependency-Datei `handlers/dependencies/autonomous_agents.py` → `workflows.py` umbenennen |
| 1.2.5 | Validator-Datei `handlers/validators/autonomous_agent_config.py` → `workflow_config.py` umbenennen |

#### 1.3 Schemas

| ID | Anforderung |
|----|-------------|
| 1.3.1 | Datei `schema/requests/autonomous_agents.py` → `workflows.py` umbenennen |
| 1.3.2 | Datei `schema/responses/autonomous_agents.py` → `workflows.py` umbenennen |
| 1.3.3 | Alle Schema-Klassen von `*AutonomousAgent*` → `*Workflow*` umbenennen |
| 1.3.4 | Schema-Imports in allen anderen Dateien aktualisieren |

#### 1.4 Exceptions

| ID | Anforderung |
|----|-------------|
| 1.4.1 | Datei `exc/autonomous_agents.py` → `exc/workflows.py` umbenennen |
| 1.4.2 | Alle Exception-Klassen von `*AutonomousAgent*` → `*Workflow*` umbenennen |

#### 1.5 Tests

| ID | Anforderung |
|----|-------------|
| 1.5.1 | Test-Dateien für autonomous_agents → workflows umbenennen |
| 1.5.2 | Alle Test-Klassen und Funktionen aktualisieren |
| 1.5.3 | Fixtures für Workflows aktualisieren |
| 1.5.4 | Tests ausführen und sicherstellen dass alle bestehen |

#### 1.6 Sonstige Referenzen

| ID | Anforderung |
|----|-------------|
| 1.6.1 | `agent_service_client.py` - Referenzen aktualisieren |
| 1.6.2 | `user_favorites.py` Handler - Referenzen aktualisieren |
| 1.6.3 | Alle imports in `__init__.py` Dateien aktualisieren |
| 1.6.4 | Caching-Keys aktualisieren falls `autonomous_agent` enthalten |

---

### Paket 2: Agent-Service (Go) Refactoring

> Alle Referenzen in agent-service (Go) von `autonomous_agent` zu `workflow` umbenennen. Platform-Client, Handlers, DTOs, Trace-Logik.

#### 2.1 Platform Client

| ID | Anforderung |
|----|-------------|
| 2.1.1 | Funktion `ValidateAutonomousAgent` → `ValidateWorkflow` |
| 2.1.2 | Funktion `GetAutonomousAgentConfig` → `GetWorkflowConfig` |
| 2.1.3 | Funktion `ValidateAutonomousAgentAPIKey` → `ValidateWorkflowAPIKey` |
| 2.1.4 | Alle zugehörigen Structs umbenennen |

#### 2.2 Handlers

| ID | Anforderung |
|----|-------------|
| 2.2.1 | Handler `GetAutonomousAgentTraces` → `GetWorkflowTraces` |
| 2.2.2 | Handler `RefreshAutonomousAgentTrace` → `RefreshWorkflowTrace` |
| 2.2.3 | Handler `ListAutonomousAgentTraces` → `ListWorkflowTraces` |
| 2.2.4 | API-Routen von `/autonomous-agents/*` → `/workflows/*` |

#### 2.3 DTOs & Types

| ID | Anforderung |
|----|-------------|
| 2.3.1 | Struct `AutonomousAgentConfigResponse` → `WorkflowConfigResponse` |
| 2.3.2 | Alle anderen `AutonomousAgent*` Structs umbenennen |
| 2.3.3 | JSON-Tags prüfen und ggf. anpassen |

#### 2.4 Tests

| ID | Anforderung |
|----|-------------|
| 2.4.1 | Go-Tests aktualisieren und ausführen |
| 2.4.2 | Alle Mocks und Fixtures anpassen |

---

### Paket 3: Frontend Refactoring

> Alle TypeScript-Typen, API-Calls, und verbliebene Referenzen in frontend-service aktualisieren. API-Pfade auf `/workflows/*` umstellen.

#### 3.1 API Types

| ID | Anforderung |
|----|-------------|
| 3.1.1 | Type `AutonomousAgentResponse` → `WorkflowResponse` |
| 3.1.2 | Type `CreateAutonomousAgentRequest` → `CreateWorkflowRequest` |
| 3.1.3 | Type `UpdateAutonomousAgentRequest` → `UpdateWorkflowRequest` |
| 3.1.4 | Type `AutonomousAgentKeyResponse` → `WorkflowKeyResponse` |
| 3.1.5 | Type `N8NAutonomousAgentConfig` → `N8NWorkflowConfig` |
| 3.1.6 | Enum `AutonomousAgentTypeEnum` → `WorkflowTypeEnum` |
| 3.1.7 | Alle zugehörigen Permission-Types aktualisieren |
| 3.1.8 | TenantRoles-Werte: `AUTONOMOUS_AGENTS_ADMIN` → `WORKFLOWS_ADMIN`, `AUTONOMOUS_AGENTS_CREATOR` → `WORKFLOWS_CREATOR` |

#### 3.2 API Client

| ID | Anforderung |
|----|-------------|
| 3.2.1 | Funktion `listAutonomousAgents` → `listWorkflows` |
| 3.2.2 | Funktion `getAutonomousAgent` → `getWorkflow` |
| 3.2.3 | Funktion `createAutonomousAgent` → `createWorkflow` |
| 3.2.4 | Funktion `updateAutonomousAgent` → `updateWorkflow` |
| 3.2.5 | Funktion `deleteAutonomousAgent` → `deleteWorkflow` |
| 3.2.6 | Funktion `duplicateAutonomousAgent` → `duplicateWorkflow` |
| 3.2.7 | Alle Permission- und Key-Funktionen entsprechend umbenennen |
| 3.2.8 | API-Pfade von `/autonomous-agents/` → `/workflows/` |

#### 3.3 Components & Hooks

| ID | Anforderung |
|----|-------------|
| 3.3.1 | Alle Variablen/Props mit `autonomousAgent` → `workflow` umbenennen |
| 3.3.2 | `usePermissions.ts` aktualisieren (CREATOR_ROLES, ADMIN_ROLES maps) |
| 3.3.3 | `SidebarDataContext.tsx` - Entity-Type-Definitionen aktualisieren |
| 3.3.4 | Route-Redirect für `/autonomous-agents` entfernen (nicht mehr nötig) |

#### 3.4 i18n

| ID | Anforderung |
|----|-------------|
| 3.4.1 | Übersetzungs-Keys mit `autonomousAgent` prüfen und ggf. aktualisieren |

#### 3.5 Tests

| ID | Anforderung |
|----|-------------|
| 3.5.1 | Frontend-Tests aktualisieren |
| 3.5.2 | MSW-Mocks für neue API-Pfade anpassen |
| 3.5.3 | Tests ausführen und sicherstellen dass alle bestehen |

---

### Paket 4: State-Management Review

> Verifizieren dass alle Edit-Dialoge bei Deep-Links korrekt funktionieren (Single-Item-Fetch Fallback). Falls Issues gefunden werden → fixen.

#### 4.1 Verifizierung

| ID | Anforderung |
|----|-------------|
| 4.1.1 | ChatAgentsPage: Prüfen dass Edit-Dialog bei Deep-Link korrekten Fallback hat |
| 4.1.2 | WorkflowsPage: Prüfen dass Edit-Dialog bei Deep-Link korrekten Fallback hat |
| 4.1.3 | ChatWidgetsPage: Prüfen dass Edit-Dialog bei Deep-Link korrekten Fallback hat |
| 4.1.4 | TenantSettingsPage (Credentials, Tools, AI Models): Prüfen |
| 4.1.5 | IntegrationsPage: Prüfen |
| 4.1.6 | AppsPage: Prüfen |

#### 4.2 Dokumentation

| ID | Anforderung |
|----|-------------|
| 4.2.1 | Ergebnis der Review dokumentieren (in diesem Dokument) |
| 4.2.2 | Falls Fixes notwendig → in diesem Paket implementieren |

---

### Paket 5: Recent Visits Refactoring

> Recent Visits komplett überarbeiten: Conversations nicht mehr tracken, stattdessen Chat Agents bei jeder gesendeten Nachricht tracken. Filter auf Dashboard hinzufügen.

#### 5.1 Backend - API Änderungen

| ID | Anforderung |
|----|-------------|
| 5.1.1 | `GET /recent-visits` um Query-Param `resource_type` erweitern (optional, für Filter) |
| 5.1.2 | Filter soll mehrere Typen akzeptieren können (z.B. `?resource_type=chat_agent,workflow`) |
| 5.1.3 | Response-Schema bleibt gleich |

#### 5.2 Backend - Tracking-Logik

| ID | Anforderung |
|----|-------------|
| 5.2.1 | `conversation` als valid `resource_type` entfernen (nicht mehr erlauben) |
| 5.2.2 | API-Validierung aktualisieren |

#### 5.3 Frontend - Chat Agent Tracking

| ID | Anforderung |
|----|-------------|
| 5.3.1 | Bei jeder gesendeten Nachricht: `chat_agent` als Recent Visit tracken |
| 5.3.2 | RecentVisitsContext entsprechend anpassen |
| 5.3.3 | Altes Conversation-Tracking entfernen |

#### 5.4 Frontend - Dashboard Filter

| ID | Anforderung |
|----|-------------|
| 5.4.1 | Toggle-Buttons rechts neben "Recent Visits" Titel hinzufügen |
| 5.4.2 | Filter-Optionen: "All" (default), "Chat Agents", "Workflows", "Apps" |
| 5.4.3 | Filter-State NICHT persistieren (bei Page-Load immer "All") |
| 5.4.4 | Bei leerem Ergebnis: leerer State anzeigen (kein Error, einfach leer) |
| 5.4.5 | Filter serverseitig anwenden via `resource_type` Query-Param |

#### 5.5 Frontend - Navigation

| ID | Anforderung |
|----|-------------|
| 5.5.1 | Click auf Chat Agent → navigiert zu `/conversations?agent={agentId}&selected={agentId}` |
| 5.5.2 | Click auf Workflow → navigiert zu `/workflows/{id}` (Details-Page) |
| 5.5.3 | Click auf App → navigiert zu `/apps/{id}` (Details-Page) |

#### 5.6 Filter-Mapping

| UI-Filter | resource_type Query-Werte |
|-----------|---------------------------|
| All | (kein Filter, alle Typen) |
| Chat Agents | `chat_agent` |
| Workflows | `workflow` |
| Apps | `external_app` |

> **Hinweis:** `chat_widget` wird weiterhin getrackt, erscheint aber unter "All" und hat keinen eigenen Filter-Button.

---

### Paket 6: Icon-Farben auf List-Pages

> Die farbigen Icons vom Dashboard (Recent Visits, Quick Actions) auch auf den List-Pages in der DataTable verwenden.

#### 6.1 Farben-Konsistenz

| ID | Anforderung |
|----|-------------|
| 6.1.1 | `/chat-agents` Page: Icon in DataTable mit Dashboard-Farbe |
| 6.1.2 | `/workflows` Page: Icon in DataTable mit Dashboard-Farbe |
| 6.1.3 | `/chat-widgets` Page: Icon in DataTable mit Dashboard-Farbe |

#### 6.2 Implementierung

| ID | Anforderung |
|----|-------------|
| 6.2.1 | Zentrale Farb-Konstanten identifizieren (wo sind sie definiert?) |
| 6.2.2 | Icon-Komponente/Styling in DataTable anpassen |
| 6.2.3 | Sicherstellen dass Farben in Light- und Dark-Mode funktionieren |

---

## Anhang

### Package-Reihenfolge & Abhängigkeiten

```
Package 0 (DB Migration)
    ↓
Package 1 (Platform-Service)
    ↓
Package 2 (Agent-Service Go)
    ↓
Package 3 (Frontend)
    ↓
Package 4 (State-Management Review) ← unabhängig
    ↓
Package 5 (Recent Visits) ← abhängig von Package 0-3 wegen "workflow" statt "autonomous_agent"
    ↓
Package 6 (Icon-Farben) ← unabhängig
```

### Betroffene Services

| Service | Packages |
|---------|----------|
| unified-ui-platform-service | 0, 1, 5 |
| unified-ui-agent-service | 2 |
| unified-ui-frontend-service | 3, 4, 5, 6 |

### Referenzen

- Vorherige Research: autonomous_agents ist in ~20+ BE-Dateien, ~15+ FE-Dateien, ~8+ Go-Dateien
- State-Management-Pattern: `useEntityList` mit `rawDataRef` + Fallback zu Single-Item GET
