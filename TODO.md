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

Beachte dabei den folgenden Workflow:
1. Wähle einen Part aus, den du implementieren möchtest
2. Plane deine implementierung
3. Implementiere
4. Füge Tests hinzu, passe bestehende ggf an und Führe alle tests aus; bei error: fixe
5. Reviewe nochmal deine Implementierung und baue ggf. Optimierungen ein. danach nochmal Schritt 4

---
############################### v0.1.0 ###############################
---


- ConversationPage
    - MessageSearchDialog

- Skeleton loading schön gestalten
    - farben

- Tool-Tips
    - bei allen beschreibungen, namen und überall wo abgeschnitten werden kann
        - hier soll der volle text in einem tooltip angezeigt werden
            - so wie auch bei den dateiuploads im chat

- Dashboard design mit mehr Farbe

- [TESTE] Rollen im FE respektieren (und nur Items etc anzeigen, wenn man rolle hat)
    - einen unified-ui tenant bauen
        - neue app-registration
        - user anlegen mit verschiedenen rollen
        - gruppen anlegen
    - Rollen testen mit mehreren Usern

- Frontend-Refactoring
    - checken, ob alles so funktioniert, wie es soll
    - Design ggf anpassen lassen

--- 

- Refactoring:
    - bei POST /messages
        - geben wir applicationId und extConversationId mit -> beides bekommen wir über die Conversation!
            - applicationId vielleicht okay
            - aber extConversationId brauchen wir nicht!

- Tracings Refactoren
    - Foundry Tracings -> mehr Daten sammeln mit tool calls, etc etc
        - mehr daten analyiseren und algorithmus anpassen!
        - aktuell ist foundry algo noch eher fehlerhaft
    - Tool calls in die hierarchie
    - Foundry Agent -> MCP Call Confirmation
        - wenn man MCP Server aufruft (siehe Word), muss noch im chat confirmt werden -> wie machen wir das dann?
    - N8N
        - calls

- Frontend Tracing Visualizer Design überarbeiten
    - Die Data Section ist noch chaos!
        - sowohl im chat interface, als auc im dialog

- AI-Based Refactring
    - für agent-service, platform-service und frontend-service eine analyse machen lassen und refactoring vorschlagen
    - dann die vorschläge durchgehen und umsetzen

- frontend code struktur refactoren
    - aktuell chat content und so unter conversation page => hier eher in components?/common odero so, damit wir in ReACT Agent Development page wiederverwenden können

- naming refactoring:
    - überhall "applications"/"application" in "chat-agents"/"chat-agent" umbenennen
        - auch in DB!!!

- Orga:
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

- Landingpage desinen

- Chat in ext. Webseite embedden lassen

- [DONE] PUT und POST auf autoagents /traces soll auch mit Service Principal funktionieren -> dann kann man SVC in Manage Access registrieren und dann mit diesem bearer token auth machen

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
