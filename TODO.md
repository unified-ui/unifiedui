# TODOs unified-ui

## Plan

- checken:
    1. wurde /api/v1/agent-service/tenants/{id}/... genutzt
    2. PUT "/refresh" weg!

- Tracing implementieren
    - TODOS
        - Frontend:
            - Autonomous-Agent Config bauen (aktuell nur n8n)
        - Platform-Service
            - /autonomous-agents/{id}/config implementieren
        - Agent Service
            -  Endpoints und handler / dto implementieren:
                - POST /autonomous-agents/{id}/traces/import
                - PUT /autonomous-agents/{id}/traces/{id}/import/refresh
                - PUT /conversations/{id}/traces/{id}/import/refresh

- Frontend
    - tracing im Chat einbauen -> beim draufklicken Hierarchische Struktur
        - klick auf message -> Rechte Sidebar für tracing einbauen und anzeigen
        - oben am Chat: Icon, bei dem man sich alle traces zu der conversation anschauen kann.
            - auch rechts als Sidebar
                - wenn man auf message in sidebar klickt, soll man zu dieser geführt werden
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
    - Credentials raus aus Sidebar und in Tenant-Settings rein
        - extra Tab; ähnlich wie Cutsom Groups
    - ConversationPage schöner designen
    - bugs beheben
        - systematisch jede Seite durchgehen und checken
            - wenn was hinzugefügt wird, wird jeder State aktualisiert?
        - beim wechseln des tenants
            - context leeren
                - zB sidebardatalist sind noch die bereits gefetcheten sachen dabei
        - beim fetchen der Credentials im Create- und EditApplicationDialog wird noch credentials?limit=999 gefetcht -> hier eher paginierung, aber man kann ruhig 100 fetchen (nur name und id -> + orderBy=name order_direction=asc)
        - siehe Video vom 02.01.
    - ConversationPage
        - Search implementieren
    - weitere features
        - PIN (favorietes)
    - Dashboard
    - ...

- platform-service
    - GET secret endpoint hinzufügen
        - GET /api/v1/platform-service/tenants/{id}/credentials/{id}/secret

- Agent-Service
    - autonomous agents
        - hier API Key generieren lassen, inkl. rotate
            - beim erstellen: werden in VAULT gespeichert und referenz uri in db auf autonomous-agent
            - PUT /api/v1/platform-service/tenants/{id}/autonomous-agents/{id}/keys/1|2/rotate
                - werden 

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

- Frontend-Tests entwickeln

- Tracings Refactoren
    - Foundry Tracings -> mehr Daten sammeln mit tool calls, etc etc
        - mehr daten analyiseren und algorithmus anpassen!
        - aktuell ist foundry algo noch eher fehlerhaft

- Refactoring:
    - bei POST /messages
        - geben wir applicationId und extConversationId mit -> beides bekommen wir über die Conversation!
            - applicationId vielleicht okay
            - aber extConversationId brauchen wir nicht!

- Foundry Agent -> MCP Call Confirmation
    - wenn man MCP Server aufruft (siehe Word), muss noch im chat confirmt werden -> wie machen wir das dann?

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
