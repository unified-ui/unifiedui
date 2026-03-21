# TODOs unified-ui

## CMDs

### Development (Hot Reload)

```sh
# Platform Service (Python/FastAPI)
uv run uvicorn unifiedui.app:app --reload

# Agent Service (Go/Gin with Air)
# make run
make dev
# oder: ~/go/bin/air -c .air.toml

# Frontend Service (React/Vite)
npm run dev

# Re-ACT Agent Service (Python/FastAPI)
uv run uvicorn app.main:app --reload --port 8086
```

### REST API Agent Service (Python/FastAPI)

```sh
# Start
uv run uvicorn app.main:app --reload --port 8087
```

Base URL: http://localhost:8087

Conversations (create session):
POST http://localhost:8087/api/v1/anonymous/conversations
POST http://localhost:8087/api/v1/basic-auth/conversations
POST http://localhost:8087/api/v1/api-key/conversations
POST http://localhost:8087/api/v1/entra-id/conversations
POST http://localhost:8087/api/v1/entra-id-appreg/conversations

Agent Invoke (SSE stream) — LangChain:
POST http://localhost:8087/api/v1/anonymous/agent/langchain/invoke
POST http://localhost:8087/api/v1/basic-auth/agent/langchain/invoke
POST http://localhost:8087/api/v1/api-key/agent/langchain/invoke
POST http://localhost:8087/api/v1/entra-id/agent/langchain/invoke
POST http://localhost:8087/api/v1/entra-id-appreg/agent/langchain/invoke

Agent Invoke (SSE stream) — LangGraph:
POST http://localhost:8087/api/v1/anonymous/agent/langgraph/invoke
POST http://localhost:8087/api/v1/basic-auth/agent/langgraph/invoke
POST http://localhost:8087/api/v1/api-key/agent/langgraph/invoke
POST http://localhost:8087/api/v1/entra-id/agent/langgraph/invoke
POST http://localhost:8087/api/v1/entra-id-appreg/agent/langgraph/invoke

Auth:
- anonymous: no auth
- basic-auth: Authorization: Basic base64(admin:password)
- api-key: X-API-Key: test-key-123
- entra-id: Authorization: Bearer <entra-id-user-token> (UPN must be in ENTRA_ID_AUTHORIZED_UPNS)
- entra-id-appreg: Authorization: Bearer <client-credentials-token> (App ID must be in ENTRA_ID_AUTHORIZED_APP_IDS)

Swagger UI: http://localhost:8087/docs

### Tests

```sh
# Platform Service
pytest tests/ -n auto --no-header -q

# Agent Service
make test

# Frontend Service
npx vitest run
```

### Test Coverage

```sh
# Platform Service (80%+)
pytest tests/ -n auto --cov=unifiedui --cov-report=html

# Agent Service
make test-cover
# oder: go test -coverprofile=coverage.out ./... && go tool cover -html=coverage.out -o coverage.html

# Frontend Service
npx vitest run --coverage
```

### Linting

```sh
# Platform Service
ruff check . && ruff format --check .

# Agent Service
make lint
# oder: golangci-lint run

# Frontend Service
npm run lint && npx tsc --noEmit
```

## Checkout:

- [Foundry REST API](https://learn.microsoft.com/en-us/azure/ai-foundry/reference/foundry-project-rest-preview?view=foundry)

## Plan

Deine Aufgaben:
1. Analysiere die aktuelle struktur
2. Analysiere meine anfordeurngen
3. Implementiere meine anforderungen

Deine Aufgaben:
1. Analysiere die aktuelle struktur
2. Analysiere meine anfordeurngen
3. Plane die implementierung
4. Hinterfrage deine Planung zur implementierung
5. Implementiere meine anforderungen

Beachte dabei den folgenden Workflow:
1. Wähle einen Part aus, den du implementieren möchtest
2. Plane deine implementierung
3. Implementiere
4. Füge Tests hinzu, passe bestehende ggf an und Führe alle tests aus; bei error: fixe
5. Reviewe nochmal deine Implementierung und baue ggf. Optimierungen ein. danach nochmal Schritt 4

---
############################### v0.2.0 ###############################
---


- Sonntag

    - AI Label Disclamer in chat!
    - Chat Widgets (custom)
        - fix: bei 
    - Azure OpenAI LLM
        - hier auch nach auth fragen: EntraID User Token (forward) (recommended und defazlt) oder API Key oder EntraID App Reg

    - Zitadel Auth testen
    - LDAP Auth testen

- Branding
    - Foto in den Header mit aufnehmen
    - App-Titel anpassbar machen (mit klein: by unified-ui), wenn titel nicht unified-ui ist

--- 


- [TESTE] Rollen im FE respektieren (und nur Items etc anzeigen, wenn man rolle hat)
    - einen unified-ui tenant bauen
        - neue app-registration
        - user anlegen mit verschiedenen rollen
        - gruppen anlegen
    - Rollen testen mit mehreren Usern

- Orga:
    - Repos refactoren / aufräumen
    - GitHub Projekt sauber aufsetzen mit issues etc
    - Branching-Konzept
    - automatischen Change-log
    - Copilot reviews
    - ruff als linter + linter bei go und ts
    - CI um linter + coverage tests erweitern

## Future

- tools service + re-act-agent-service
    - outlook tools
        - hier kann man mit SVC oder auch mit delegated permissions arbeiten! token haben wir ja
    - sharepoint
        - site scrapen
        - get metadata und und und
    - OpenAPI defintiion & mcp server (haben wir ja schon) mit beschreibung

- emtec branging / customizations ermöglichen
    - Farbschema
    - Logo
    - etc

- Backend
    - Agent-Integration
        - file upload
        - reasoning / tool calls etc
            - in foundry mit tools etc arbeiten und entsprechend im UI anzeigen
    - Fehler im UI auch anzeigen -> wenn von Agent Service kommt

- [DONE] CORS im platform-service
    - hier CORS für header X-Service-Key explizit angeben, damit nur vom unified-ui agent-service darauf zugegriffen werden kann

- Landingpage + Documentation App designen
    - en-us und de-de Version
    - App mit
        - Landingpage
        - docs
        - about us
            - why unified-ui
        - contact
        - Leistungen


- Import Dialog für Auto Agents
    - über Tabelle Import IconButton -> Import Dialog
        - hier die ID eingeben und dann importieren lassen

- ReACT Agent Development Pages designen
    - Extra Sidebar:
        - Agents
        - Tools
        - Knowledge
    - Agents
        - Liste der ReACT Agents mit Descriptions, Tags etc
    - Tools
        - Liste an Tools mit Description, Type, Tags etc
    - Knoledge
        - Liste an Knowledgebases
            - AI Search anbinden (nur connection)
                - dann hier irgendwie container für files schaffen (Storage Account)
                - dann kann man hier indexes bauen und und auch ACL definieren -> mit $filter ACL durchsetzen
            - insb. FoundryIQ, WorkIQ
    - agents/{id}
        - hier an CopilotStudio oder Foundry orientieren
            - Overview Page mit allem + einzelne Pages
            - ODER wie in Foundry alles in einem kompakt ein und ausblendbar

- Frontend
    - /refresh von identity implementieren
        - FE button in IAM table -> da wo das icon ganz links ist -> beim hovern hier ein refresh icon rein!

- Copilot anbinden
    - Integration:
        - API via `DirectLine` ODER
        - python sdk -> FastAPI Copilot Chat service
            - trigger über agent-service
            - FastAPI nur für Copilot-Anbindung -> alles sonst in GO agent-service
    - Integration testen (postman)
    - Config im Frontend implementieren
    - Agent im Frontend testen
