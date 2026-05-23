# TODOs unified-ui

## TODOs

- Design UI und weiterefixes:
    - allgemein:
        - sidebar
            - es gibt eine data sidebar, die eingeblendet wird, wenn man in einem unteritem ist; wenn cih in chat-agents/{id} bin, wird beim hovern über agents die datasidebar eingeblendet; hier sind die links zu den agents auf die chats ; aber ich will den link auf den chat-agents/{id}
            - settings kann raus; haben wir um user dropdpwn; also einfach item unten enfernen; dann ist admin button ganz unten und settings weg
        - alles was mit ReACT Agents zu tun hat und auch tools, soll aus dem code entfernt werden; sowohl backend (platform service), als auch frontend. auch aus den dokumentationen soll das raus!
    - /chat-agents/
        - 3-dots-menu:
            - Open Chat menüpunkt unter Open hinzufügen -> chat öffnen (wie auch auf der /{id} seite der link!)
            - embed agent auf ?embed page navigieren etc
    - /chat-agents/{id}
        - unter Tab embed: ALLES aus `/chat-agents/29be8df5-a39f-440f-8f1d-94924fe11f81/embed-chat` rein! (Config, iframe definition, url, allow origins, open chat button für preview...)
            - dann kann die embed-chat seite auch weg!
        - Manage access button weg
        - im tab overview -> info header icon hat kein icon nur das  quadrat mit den darben; muss noch icon rein!
    - /workflows/{id}
        - tab details: Endpoint & Keys > {YOUR-AGENT-SERVICE-HOST} => haben wir schon in den env
            - ebenso im &dialog=integrate-workflow
    - /conversations
        - search -> noch immer alle conversations?
    - /admin
        - /
            - hier soll nicht ganze page skollbar sein, sondern alles unter "m_4081bf90 mantine-Group-root"; also "Analytics" header und die filter sachen sollten immer oben stehen und dann sollte es entsprechend nen div geben, das unten skrollbar ist mit allen analytics cards, tables etc
        - /settings (alle tabs)
            - auch hier das problem: es sollte eigentlich jeweil NUR DIE TABELLE Skrollbar sein! nicht die gesamte Seite!

    - chat-widgets
        - params müssen für iFrame konfiguriert werden können (siehe YT-Embedding -> braucht params)
            - vielleicht sollte man auch alternativ selbst die iFrame Definition eingeben können, damit!
        - iFrame -> url muss pflichtfeld sein

    - alles weitere
        - DropDown with search Component
            - hier ist search box bissl zu weit links oder so (foto)
        - alles soll default active sein (workflow, chat-widgets, ....)

    - is_active überall raus und nur bei Agents und Credentials machen UND jetzt auch bei beiden im BE checken, ob active und sonst 4xx zurückgeben (wenn man zB nen Agent aufruft, der credentials braucht aber credentials ist inactive, dann soll 4xx zurückgegeben und gute beschreibung)
        - wenn nicht active (agent) -> nicht chatten können; credentials -> nicht freitext holen und 4XX zurückgeben


- global search
    - 

- n8n Integration verbessern:
    - /workflows/{id}
        - traces testen (verschiedene elemente im RUN mit gutem Icon textanzeigen?)

- api aufrufe optimieren
    - mehr mit select=id,name etc arbeiten (manuell schauen; zB tags abfrage!)


--- 


- [TESTE] Rollen im FE respektieren (und nur Items etc anzeigen, wenn man rolle hat)
    - einen unified-ui tenant bauen
        - neue app-registration
        - user anlegen mit verschiedenen rollen
        - gruppen anlegen
    - Rollen testen mit mehreren Usern


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
