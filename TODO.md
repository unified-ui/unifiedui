# TODOs unified-ui

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

## Done

- Agent-Service
    - autonomous agents
        - hier API Key generieren lassen, inkl. rotate
            - beim erstellen: werden in VAULT gespeichert und referenz uri in db auf autonomous-agent
            - PUT /api/v1/platform-service/tenants/{id}/autonomous-agents/{id}/keys/1|2/rotate
                - werden 

- Tracing implementieren
    - TODOS

- platform-service
    - models.py
        - auto-agent entitiy
            - type: enum[N8N] (aktuell nur N8N supportet!)
            - primary_key_vault_uri -> bei POST -> erstelle einen API key für diese resource; nur über spezielle route bearbeitbar, wird aber IMMER vom system generiert
            - secondary_key_vault_uri -> siehe primary_key_vault_uri
            - last_full_import (timestamp; default NULL; system column (nicht vom user setzbar))
            - config structure (validation needed!!!):
                ```json
                "workflow_endpoint": "http://localhost:5678/workflow/01V4K8pjRhOVncdg" (so bekommen wir sowohl den host, als auch die workflow id)
                "api_api_key_credential_id": "<CREDENTIAL_ID>"
                ```
    - Anpassen:
        - POST /autonomous-agents
            - primary + secondary key generation + speicherung
            - validierung der config (aktuell nur n8n)
                - orientiere dich bei der validierung an dieser route:
                    - POST /applications -> handler
                    - da wurde schon mal n8n validiert, mit etwas anderen parametern
                    - aber nutze auch hier ein entsprechendes pattern, da noch mehr typen mit unterschiedlichen configs kommen werden
        - PATCH /autonomous-agents/{id}
            - keys sind nicht bearbeitbar und dürfen nicht in body sein
    - PUT /api/v1/platform-service/tenants/{id}/autonomous-agents/{id}/keys/1|2/rotate
        - kein body -> alles systemseitig!
        - gibt den neuen key zurück
        - check_permissions:
            - nur [TENANT ROLES:] GLOBAL_ADMIN, AUTONOMOUS_AGENT_ADMIN, [RESOURCE ROLES] ADMIN, WRITE
    - GET /api/v1/platform-service/tenants/{id}/autonomous-agents/{id}/keys/1|2 erstellen
        - hier den secret zurückgeben -> nur wenn 
        - check_permissions:
            - nur [TENANT ROLES:] GLOBAL_ADMIN, AUTONOMOUS_AGENT_ADMIN, [RESOURCE ROLES] ADMIN, WRITE

            - GET /autonomous-agents/{id}/config implementieren
                - Agent-Service Key 
                

- platform-service
    - GET secret endpoint hinzufügen
        - da man über "GET /api/v1/platform-service/tenants/{id}/credentials/{id}" nur die beschreibenden daten bekommt und nicht den secret, soll es eine dedizierte route für das fetchen des secrets geben:
        - GET /api/v1/platform-service/tenants/{id}/credentials/{id}/secret
            - gibt nur secret_value zurück
            - check_permissions:
                - Tenant Roles: GLOBAL_ADMIN, CREDENTIALS_ADMIN
                - Resource Roles: WRITE, ADMIN

- Frontend:
    - client.ts und types.ts anpassen
    - Autonomous-Agent Config bauen (aktuell nur n8n)

- platform-service + Frontend: N8N API Version
    - passe N8N config validator für auto-agent > config an: muss api_version gegeben sein (aktuell nut zulässig: "v1")
    - füge in Create/EditAutonomousAgentDialog an: Feld "API Version" hinzu -> ganz so wie bei Create/EditApplicationDialog

- platform-service /autonomous-agents/{id}/config implementieren
    - analog zu /applications/{id}/config, nur mit anderer Config
    - config: siehe config_auto_agent.json
    - UND Auth ist anders! hier wird nicht mit einem bearer sondern der header `X-Unified-UI-Autonomous-Agent-API-Key` (und nur dieser key! nicht noch agent-service key) wenn nein 403
        - jeder auto-agent hat ja nun zwei keys (primary key, secondary key) und einer dieser keys muss mit dem header key übereinstimmen; sonst 403
    - und nutze kein Caching hier! Da keys rotieren können!

- Agent Service
    -  Endpoints und handler implementieren:
        - POST /autonomous-agents/{id}/traces/import
            - body: {"type": "N8N", "executionId": "..."}
        - PUT /autonomous-agents/{id}/traces/{id}/import/refresh -> refresh import of trace
            - hier bekommst du aus refrenceId die executionId für n8n; kein Body nötig
        - beide routes kann nur mit dem header `X-Unified-UI-Autonomous-Agent-API-Key` ansprechen; kein bearer authorizatin nötig!
        - du holst dir, wie auch bei POST /messages die config (von platform-service/autonomous-agent/{id}/config) endpoint
        - du cachst in diesem fall NICHT -> es wird immer der Platform-servce /config abgefragt (wegen API Keys, die können rotieren etc)
            - du holst dir die config aber nicht mit bearer token, sondern mit dem Header API Key
        -  mit der config kannst du dann enstprechend die traces importieren. siehe dafür POST /messages > N8N
            - aktuell wird für autonomous agents nur n8n unterstützt, jedoch beachte bei der implementierung, dass auch andere quellen zukünftig unterstützt werden! nutze das factory pattern bzw. orientiere dich sehr stark an POST /messages, da wurde schon einmal die logik für Microsoft Foundry und N8N traces umgesetzt, nur dass halt hier dann aus der jobQueue und nach dem stream die traces für chats importiert werden; etzt wollen wir autonome workflows (background workflows) importieren
        - importlogik für n8n besteht schon
- agent-service
    - POST /autonomous-agents/{id}/traces/import
        - ==> hier lieber ein PUT draus machen!
        - weil wir haben ja die executionId!!!

- N8N
    - unified-ui-integration Workflow bauen -> traces übertragen
        - PUT /autonomous-agents/{id}/traces/import
- N8N Application: Workflow Endpoint soll auch noch angegeben werden
    - dann kann man die workflowId in der Fallback logik nutzen, im besser über /executions zu itterieren!
    - in config workflowId zurückgeben!


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



- Frontend Refactoring 1
    - Development Platforms raus
    - Credentials raus aus Sidebar und in Tenant-Settings rein
        - extra Tab; ähnlich wie Cutsom Groups
    - Simple ReACT Agent entwickeln
        - + MCP Server Support für ReACT Agent
        - + OpenAPI Definition als Tool für ReACT Agent (wie in Foundry)
        - neue Entitäten:
            - MCP Servers
            - Open API Config
            - Credentials.Type: OPEN_API_CONNECTION > key mappen in header (wie in Foundry)
        - Tabs:
            - Tools
        - Sidebar
            - ReACT-Agent Development
    - bugs beheben
        - systematisch jede Seite durchgehen und checken
            - wenn was hinzugefügt wird, wird jeder State aktualisiert?
        - beim wechseln des tenants
            - context leeren
                - zB sidebardatalist sind noch die bereits gefetcheten sachen dabei
        - beim fetchen der Credentials im Create- und EditApplicationDialog wird noch credentials?limit=999 gefetcht -> hier eher paginierung, aber man kann ruhig 100 fetchen (nur name und id -> + orderBy=name order_direction=asc)
        - siehe Video vom 02.01.
    - ConversationPage
        - schöner designen
        - Search implementieren
        - tracing im Chat verschönern

- AutonomousAgentPage
    - TabBar
        - Runs
        - Autonomous Agent
    - Liste der Autonomous Agents:
        - wie jede andere auch
    - Liste der RUNS:
        - Filter
            - nach Tag, Monat, Jahr
            - status
                - Success
                - In Progress
                - Partial Error
                - Error
                - Import Error
        - Sort by
            - ...
- TracesPage
    - hier ALLE traces, Chat Agent und Autonoumus Agents mit coolen filtern etc
- TracingDetailPage
    - details zu den traces
        - Kopf: mit Metadaten (created, duration, status, name, description etc)
        - Tracings... Hierarchie

- Frontend Refactoring
    - weitere features
        - PIN (favorietes)
        - last visited
    - Dashboard
    - ...

- agent-service
    - N8N Traces refactoren
    - Foundry Traces refactoren

11. ZWEI Vaults fixen:
    - app_vault + secrets_vault
        - App Vault für application keys wie zB `X-Service-Key`
        - Secrets Vault -> ist vault für credentials aus der app etc...
    - *aktuell in auth.py > _validate_service_key soll app_vault nutzen
        - app_vault kann auch dotenv sein...

- models.py refactoren
    - überall wo uuid von uns -> char(36) nutzen
        - zb bei Conversation.application_id string(100) -> char(36)

- Bei delete conversation -> auch messages und traces löschen
- Bei delete auto agent -> auch traces löschen

- Frontend-Tests entwickeln

- Tracings Refactoren
    - Foundry Tracings -> mehr Daten sammeln mit tool calls, etc etc
        - mehr daten analyiseren und algorithmus anpassen!
        - aktuell ist foundry algo noch eher fehlerhaft
    - Tool calls in die hierarchie
    - Foundry Agent -> MCP Call Confirmation
        - wenn man MCP Server aufruft (siehe Word), muss noch im chat confirmt werden -> wie machen wir das dann?

- Refactoring:
    - bei POST /messages
        - geben wir applicationId und extConversationId mit -> beides bekommen wir über die Conversation!
            - applicationId vielleicht okay
            - aber extConversationId brauchen wir nicht!

- Foundry IMT Agent
    - Tool, welches AI-Search abfragt und auf device_id == {ID} filtert!
        - Wie tool entwickeln?
            - in foundry kann man irgendwie MCP server erstellen und als tool nutzen?
    - Prompt entsprechend anpassen -> auc <context>device_id={ID}</context> holen
    - in tool übergeben (soll agent machen)
    - sollte in unified-ui funktionieren

## Future

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
        - externen 