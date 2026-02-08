# TODOs unified-ui

## Setup vault secrets

### 1. Shared Service Key generieren

```sh
openssl rand -hex 32
```

Ergebnis kopieren (z.B. `a1b2c3d4...`). Das ist der gemeinsame Service Key.

### 2. Platform Service `.env` anpassen

In `unified-ui-platform-service/.env`:

```dotenv
# ALT — löschen oder leer lassen:
# X_AGENT_SERVICE_KEY=

# NEU — Vault-basierte Service Keys:
VAULT_TYPE=DOTENV
platform-to-agent-service-key=<GENERATED_KEY>
agent-to-platform-service-key=<GENERATED_KEY>

# Agent Service URL (wo der Agent Service läuft):
AGENT_SERVICE_URL=http://localhost:8085
AGENT_SERVICE_TIMEOUT=30
```

> **Hinweis:** `platform-to-agent-service-key` und `agent-to-platform-service-key` sind die Vault-Key-Namen. Der DotEnv-Vault liest sie als Env-Vars via `os.getenv()`. Beide Keys können denselben Wert haben oder unterschiedliche (je nach gewünschter Granularität).

### 3. Agent Service `.env` anpassen

In `unified-ui-agent-service/.env`:

```dotenv
# ALT — löschen:
# X_AGENT_SERVICE_KEY=

# NEU — Vault-basierte Service Keys:
VAULT_TYPE=dotenv
platform-to-agent-service-key=<GENERATED_KEY>
agent-to-platform-service-key=<GENERATED_KEY>
```

> Gleiche Werte wie im Platform Service verwenden!

### 4. Services starten

```sh
# Terminal 1: Platform Service
cd unified-ui-platform-service
uvicorn unifiedui.app:app --reload

# Terminal 2: Agent Service
cd unified-ui-agent-service
make run

# Terminal 3: Frontend
cd unified-ui-frontend-service
npm run dev
```

### 5. Testen

**a) Service-Key Auth testen (Agent → Platform):**
```sh
# Sollte 401 liefern (kein Key):
curl -X GET http://localhost:8081/api/v1/...eine-service-key-route...

# Sollte 403 liefern (falscher Key):
curl -X GET http://localhost:8081/api/v1/... -H "X-Service-Key: falsch"

# Sollte 200 liefern (richtiger Key):
curl -X GET http://localhost:8081/api/v1/... -H "X-Service-Key: <GENERATED_KEY>"
```

**b) Cascade Delete testen (Platform → Agent):**
1. Im Frontend eine Conversation mit Nachrichten/Traces anlegen
2. Conversation löschen → Platform Service ruft Agent Service auf und löscht Messages + Traces
3. In MongoDB prüfen: `db.messages.find({conversationId: "..."})` und `db.traces.find({conversationId: "..."})` sollten leer sein

**c) Autonomous Agent Cascade Delete testen:**
1. Autonomous Agent mit Traces anlegen
2. Agent löschen → Platform ruft Agent Service, löscht Traces + Vault-Secrets
3. In MongoDB prüfen: `db.traces.find({autonomousAgentId: "..."})` sollte leer sein

### 6. Fehler-Diagnose

- **Platform startet nicht?** → `VAULT_TYPE=DOTENV` prüfen
- **401/403 bei Service-Calls?** → Keys in beiden `.env` vergleichen, müssen identisch sein
- **Cascade Delete tut nichts?** → Agent Service Logs prüfen, `AGENT_SERVICE_URL` korrekt?
- **Fallback:** Alt-Modus funktioniert weiterhin über `X_AGENT_SERVICE_KEY` in Platform `.env`



## CMDs

```sh
uvicorn unifiedui.app:app --reload
make run
npm run dev
```

## Checkout:

- [Foundry REST API](https://learn.microsoft.com/en-us/azure/ai-foundry/reference/foundry-project-rest-preview?view=foundry)
    - see: "In this article" on the right side!
-  OSS Project for Chat Frontend [chainlit](https://github.com/Chainlit/chainlit)

## emtec Plan

1. v0.1.0 fertigstellen
    - definieren, welche Features in v1 vorhanden sein sollen
2. v0.2.0
    - Langchain + Langgraph integration
        - per REST API
        - python-unified-ui-sdk für Streaming und Tracing
            - track_langchain_traces(lc_agent=lc_agent)
            - ...
    - anhand des Typecode Research Chats Features ableiten
        - Real-Time Updates von
            - Reasoning
            - Tool Calls wie Web-Search etc
    - einfache Chat-Widgets im Chat einbinden
        - Standard Chat Widgets können Application hinzugefügt werden
            - spezielle Zwischen Response notwendig
        - Single-Select
        - Multi-Select
    - Connection-Tests einführen
        - wenn man mit N8N verbinden möchte per API -> test obs funktioniert
            - /tenants/{id}/api/v1/test-connection {""...}
    - DropDowns für externe Daten zur Verfügung stellen
        - zB n8n: man gibt credentials an, endpoint und kann sich dann die workflows auflisten lassen 
3. v0.3.0
    - Azure Cloud Deployment
        - Private-Public Deployment
            - Kommunikation und DBs etc private
            - Frontend Public
        - Private-Private Deployment
            - Frontend ebenfalls nur mit VPN erreichbar
    - LDAP Auth-Provider
    - Kerberos Auth-Provider
    - tenant-konzept überarbeiten
    - MS Copilot integration
    - Feedback Framework integration
    - Formulare als Chat Widgets supporten
    - Simple ReACT Agent entwickeln
        - + Chat-Playground
        - + MCP Server Support für ReACT Agent
        - + OpenAPI Definition als Tool für ReACT Agent (wie in Foundry)
        - neue Entitäten:
            - MCP Servers
            - Open API Config
            - Credentials.Type: LLM > Azure, Anthropic etc (via Langchain)
            - Credentials.Type: OPEN_API_CONNECTION > key mappen in header (wie in Foundry)
        - Agent-Features:
            - Reasoning
            - Tool Calls
            - Custom Agentic-Engine
                - Summarization of History (Sub Agent)
                - Split message in different tasks and create sub-agents for each task
                    - enable Multi-Agent Orchestration
                - ...


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

---
############################### v0.1.0 ###############################
---

<!-- - Bei delete conversation -> auch messages und traces löschen
    - hier müsste man auf agent-service gehen und platform-service anschließend aufrufen und mit X-Service-Key auth machen
- Bei delete auto agent -> auch traces löschen
    - hier müsste man auf agent-service gehen und platform-service anschließend aufrufen und mit X-Service-Key auth machen
- CORS im platform-service
    - hier CORS für header X-Service-Key explizit angeben, damit nur vom unified-ui agent-service darauf zugegriffen werden kann

- ZWEI Vaults fixen:
    - app_vault + secrets_vault
        - App Vault für application keys wie zB `X-Service-Key`
        - Secrets Vault -> ist vault für credentials aus der app etc...
    - *aktuell in auth.py > _validate_service_key soll app_vault nutzen
        - app_vault kann auch dotenv sein... -->

- Setup vault secrets (siehe Anleitung oben)

- N8N Workflow nach traces importieren
    - Workflow-Run per Tabelle und extra Workflow in traces importieren
    - dann einmal re-run dieses traces im UI anstoßen

- Tenant Sessting > AI Settings
    - entity: tenant_ai_models
        - name
        - type [LLM_MODEL | EMBEDDING_MODEL]
    - credentials.Type: TENANT_AI_MODEL
    - liste an Models hinterlegen -> es wird loadbalancing genutzt
    - Warum: AI Support, Embeddings für Search ()


- Frontend Refactoring
    - alle pages sollen NICHT im container, sondern über gesamte page gehen mit meinetwegen max-width
    - weitere features
        - PIN (favorietes)
        - last visited
        - notifications
            - auto-agent runs
    - Dashboard designen
        - auf GET /id -> in user_history collection schreiben
            - {"tenant_id": "", "user_id": "", "entity": "application": "id": "id"}
        - hier fragen, was best practice -> eigentlich event, aber zu aufwendig!
    - login routing etc besser gestalten
    - Sidebar & überall: die icons insb. für tracing vereinheitlichen

- ConversationPage
    - schöner designen
    - Search implementieren
    - tracing im Chat verschönern
    - ...

- Frontend-Tests entwickeln

- Tracings Refactoren
    - Foundry Tracings -> mehr Daten sammeln mit tool calls, etc etc
        - mehr daten analyiseren und algorithmus anpassen!
        - aktuell ist foundry algo noch eher fehlerhaft
    - Tool calls in die hierarchie
    - Foundry Agent -> MCP Call Confirmation
        - wenn man MCP Server aufruft (siehe Word), muss noch im chat confirmt werden -> wie machen wir das dann?
    - N8N

- Refactoring:
    - bei POST /messages
        - geben wir applicationId und extConversationId mit -> beides bekommen wir über die Conversation!
            - applicationId vielleicht okay
            - aber extConversationId brauchen wir nicht!

- Rollen im FE respektieren (und nur Items etc anzeigen, wenn man rolle hat)
    - Rollen testen mit mehreren Usern

- AI-Based Refactring
    - für agent-service, platform-service und frontend-service eine analyse machen lassen und refactoring vorschlagen
    - dann die vorschläge durchgehen und umsetzen

- Orga:
    - GitHub Projekt sauber aufsetzen mit issues etc
    - Branching-Konzept
    - automatischen Change-log
    - Copilot reviews#
    - ...

## Future

- CORS im platform-service
    - hier CORS für header X-Service-Key explizit angeben, damit nur vom unified-ui agent-service darauf zugegriffen werden kann

- Landingpage desinen

- PUT und POST auf autoagents /traces soll auch mit Service Principal funktionieren -> dann kann man SVC in Manage Access registrieren und dann mit diesem bearer token auth machen

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

- Backend
    - Agent-Integration
        - file upload
        - reasoning / tool calls etc
            - in foundry mit tools etc arbeiten und entsprechend im UI anzeigen

- Frontend
    - /refresh von identity implementieren
        - FE button in IAM table -> da wo das icon ganz links ist -> beim hovern hier ein refresh icon rein!

    - Rollen im FE beachten
        - GLOBAL_ADMIN, *CREATOR, *ADMIN
        - TENANT manages acces etc etc

    - language-support einbauen
        - erstmal alles in englisch
        - als zweites: über url /de-de /en-us übersetzen (default -> /en-us)

- Copilot anbinden
    - Integration:
        - API via `DirectLine` ODER
        - python sdk -> FastAPI Copilot Chat service
            - trigger über agent-service
            - FastAPI nur für Copilot-Anbindung -> alles sonst in GO agent-service
    - Integration testen (postman)
    - Config im Frontend implementieren
    - Agent im Frontend testen

- Langchain und Langgraph REST API Service
    - mit eigenem ReACT Chat Agent verknüpfen!
        - fürs streaming und tracing geben wir je zwei klassen vor mit to_dict()...
    - einen simplen Langchain Agent bauen -> per REST API exposen
    - state auch irgendwie senden
        - einfach als dict?
    - Integration in GO mit sdk bauen
    - Integration testen (postman)
    - Config im Frontend implementieren
    - Agent im Frontend testen

- Application -> Simple ReAct Chat Agent direkt in unified-ui
    - PoC [Here](/Users/enricogoerlitz/Developer/repos/unified-ui-agent-service/poc/unified_ui_agent/py/)
    - dafür müsste man verschiedene LLM-APIs anbinden können
        - NEIN -> wir nutzen einfach auch Langchain, müssen nur die config speichern und damit das llm bauen
    - UND! man kann MCP Server je Application anbinden und tools mitgeben!

    - TODOs:
        - PoC in GO schreiben und nochmal testen
            - langchain und alle Features müssen auch in GO nutzbar sein!
                - ansonsten FAST API Service für custom agents...
        - Update Entities
            - credentials
                - type: HTTP_HEADERS UND AZURE_OPENAI
                - wird als string in secret_value gesendet
        - Neue Entities:
            - mcp_servers
                - id
                - name
                - description
                - type: "SSE"
                - credential_id
        - ....
    - Frontend Config:
        - agent_version (aktuell nur ["v1"])
        - agent_type (aktuell nur ["ReACT_AGENT", "MULTI_AGENT_ORCHESTRATOR"])
        - instructions
        - Geeting message (Message, die zum start gesendet wird und als Gruß oder als Einleitung in die Konversation dient)
        - default chat history count
        - llm_credentials_id
            - neuen Credential Type: "AZURE_OPENAI"
                - type
                - api_version
                - endpoint
                - api_key
        - llm_deployment_name
        - tools[]:
            - type: mcp_server
            - mcp_server_id
            - allowed_tools: [liste aus strings]
        - sub_agents[]:
            - agent (Chat Agent)
            - 
        - tools > Log Tool-Output to Message
        - *zukünftig: Playground!


- Überlegen, full import eines auto-agents von unified-ui anstoßen? **eher nicht, kann automatisierungsplattform übernehmen!**
    - PATCH /autonomous-agents/{id}/last-full-import {"timestamp": "..."}
        - nur wenn user check_permissions: GLOBAL_ADMIN, AUTONOMOUS_ADMIN, oder auf Resource: WRITE oder ADMIN hat
        - UND wenn X-Agent-Service-API-Key korrekt ist!
        - hier wird NUR das feld last_full_import 

        - PUT /autonomous-agents/{id}/traces/import/refresh -> make full import of all traces of this workflow
            - n8n: itterate over /executions?workflowId={WORKFLOW_ID}
                - in config we get "last_full_import" (wenn null -> alle; wennn nicht null; nur executions nach last_full_inpott)
                - hier die id holen und dann über gefilterte ids -> /executions/{id}?includeData=true -> parallel ausführen und speichern
                - wenn fertig (successfuly), an platform-service PATCH
            - im ersten schritt mit JobQueue arbeiten und 202 zurückgeben (später vielleicht consumer/producer)

- Embedding-Service
    - Ziel:
        - Customer kann Dokumente an API schicken und diese werden entsprechend der config embeddet
        - Anschließend kann man dynamische querys absenden
    - muss man configureiren
        - Document-Collection anlegen und konfigurieren
            - embedding model (NICHT von unified-ui bezahlt)
            - destination (AI Search, )
            - chunking; text extraction type -> gibt ja sowas die Indexer :)
            - text extraction service oder default tika?
    - Upload Files via REST API
        - API Key
    - in Collections speichern + embedded search
    - Text-Extraction
        - Tika
        - externen dienst
    - per kafka / eventhub!
