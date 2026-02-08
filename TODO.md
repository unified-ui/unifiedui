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

---
############################### v0.1.0 ###############################
---


- Frontend Refactoring
    - alle pages sollen NICHT im container-layout, sondern über gesamte page gehen mit meinetwegen max-width
        - hier mit ist gemeint, aktuell ist ein "typeisches" container layout für die breite eingebaut. man hat zentral die page mit ner max width
        - will aber, dass jetzt die gesamte page width verwendet wird.
            - konkretes beispiel: applications page:
                - hier ist alles serh zentriert. ich will das der header der page oben links ist (mit bisschen page padding natürlich) etc. also insgesamt soll einfach mehr platz genutzt werden und es soll nicht so zentriert sein. das gleiche gilt für die details page etc. generell halt alle pages
        - entwerfe hierfür ein neues layout, inkl. fontsizes, paddings, etc etc
            - recherchiere gerne nach modernen layouts
    - weitere features
        - PIN (favorietes)
        - last visited
            - für ein nices dashboard, auf dem der benutzer je entities seine relevanten last visits, aber auch favorites sieht
        - notifications
            - auto-agent runs
        - plane all diese features. wir haben ja schon einiges datenseitig vorbereitet (zB pin etc), aber logik ist noch nicht implementiert und wir benötigen auch noch ein konzept, wie wir dann zB pins (favoroutes) im UI darstellen -> oben; aber vielleicht gesondert fetchen etc etc
    - Dashboard designen
        - ich will ein schönes dashboard (home) design haben. hier sollte der benutzer je entity irgendwie seine favoriztes vorne sehen und last visits etc. du verstehst schon. ähnlich wie bei powerbi. bielleicht gibts noch andere sachen, die geil sind. überlege mal, wke man da nen schönes und benutzer zentrietes design/layout hinbekommt
        - gerne kannst du weitere features vorschlagen
        - bedenke auch dabei, welche daten wir wie erheben müssen, um das zu ermöglichen (zB last visited etc) darzustellen. 
    - Sidebar & überall: die icons insb. für tracing vereinheitlichen
    - dann ist es bei vielen pages so, wenn man nen refresh macht, flackert die page komplett aus und wieder ein. das ist nicht so geil. hier sollte der refresh der liste eigentlich geil über react gelöst werden. ist das nicht so, dass eine liste nie komplett neu gerendert wird, sondern nur die items, die sich geändert haben? also zB wenn ich auf der applications page bin und ich lösche eine application, dann sollte eigentlich nur diese eine application rausfliegen und nicht die komplette liste neu laden und damit das komplette UI flackern. das gleiche gilt für die details page. hier sollte eigentlich auch nur das item aktualisiert werden, wenn ich zB den namen ändere oder so. generell sollten wir also schauen, dass wir das UI so bauen, dass es möglichst wenig komplett neu rendert, sondern wirklich nur die items, die sich geändert haben. das macht das UI viel smoother und angenehmer zu bedienen
        - überlege auch an anderen stellen, ob du solche optimierungen irgendwie finden kannst
    - die settingspage arbeitet aktuell mit einer horizontalen tabbar navigation. ich denke, da wir schon einige einträge haben, würde es sinn ergeben hier auf eine page sidebar umzusteigen und oben auf der page dann wieder nen titel und beschreibung zu geben
        - aber überlege mal, was aus design sicht hier best practice für den user wäre

deine aufgabe ist letztendlich, ein geiles ui konzept zu entwickeln und gewisse themen zu refactiren (erstmal konzeptionell.)
Scheibe das konzept in eine markdown datei für die abnahme meinerseits.
sei wirklich ausführlich in deiner recherche und deinen überlegungen. es soll wirklich ein geiles und modernes UI Konzept entstehen, was auch die user experience verbessert.
anschließend wollen wir vielleicht n och nen style guide als instructions entwerfen. dazu aber später
zudem sollten styles auch einheitlich sein. tabellen immer sehr ähnlich; listen immer sehr ähnlich etc

arbeit in deinem konzept auch viel mit layout beispielen (die du mehr oder weniger "zeichnest" mit ascii oder so) damit ich auch wirklich verstehe, wie du dir das vorstellst. gerne kannst du auch beispiele von anderen modernen ui's oder so einbauen, wenn du das für sinnvoll hältst

    - login routing etc besser gestalten

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
    - ruff als linter + linter bei go und ts
    - CI um linter + coverage tests erweitern

## Future

- Backend
    - Agent-Integration
        - file upload
        - reasoning / tool calls etc
            - in foundry mit tools etc arbeiten und entsprechend im UI anzeigen
    - Fehler im UI auch anzeigen -> wenn von Agent Service kommt

- [DONE?] CORS im platform-service
    - hier CORS für header X-Service-Key explizit angeben, damit nur vom unified-ui agent-service darauf zugegriffen werden kann

- Landingpage desinen

- Chat in ext. Webseite embedden lassen

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
