# TODOs unified-ui

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
## Plan

- N8N Application: Workflow Endpoint soll auch noch angegeben werden
    - dann kann man die workflowId in der Fallback logik nutzen, im besser über /executions zu itterieren!
    - in config workflowId zurückgeben!

- Konzept für Tracing Visualisierung
    - Daten:
        - Root
            - ReferenceName
            - ContextType
            - ReferenceId
            - Logs
            - ReferenceMetadata -> einfach als JSON anzeigen
            - CreatedAt
        - Nodes
            - Name
            - Type
            - Status
            - RefrenceId
            - StartAt
            - Data
                - input
                    - Text
                    - ExtraData -> als Tab und JSON anzeigen
                    - Metadata -> als Tab und JSON anzeigen
                - output
                    - Text
                    - ExtraData -> als Tab und JSON anzeigen
                    - Metadata -> als Tab und JSON anzeigen
            - Logs
    - Einsatzgebiete
        1. im Chat
            - Anzeige der Hierarchischen Traces in einer Sidebar
                - Oben eine hierarchische View (primär Type im container und Name)
            - Für detaiierte View -> kann man Dialog mit Details öffnen
                - rechts auch die hierarchische view (horizontal größer kleiner ziehen)
                - links:
                    - oben Canvas workflow view mit items die connectet sind
                    - unten (kleiner, vertkakl größer kleiner ziehen)
        2. Autonomous Agent page -> detaiierte view im Dialog
    - Konzept:
        - wir bauen modular ein tracings-visualisierungs-interface
        - Es wird zwei Hauptkomponenten geben:
            - [Canvas-View] Ein Canvas, mit Visuellen Items, welche connected sind und einen Workflowartige Visualisierung darstellt
            - [Hierachie-View] Eine vertikale, hierarchischaufgebaute struktur, die primär text hierarchisch anzeigt und beim klicken informationen in einem unteren fenster anzeigt
        - Skizze der Gesamt Page:
            - Header:
                - Icon + "Tracing for referenceName" + contextType (drunter) schön anzeigen
                - und schließen icon, klar
            - Einen Subheader, der aber fixed ist und nur über dem convas liegt
                - hier gewissen daten anzeigen:
                    - trace_id
                    - SelectedItem name (oder root)
                    - SelectedItem startAt, endAt oder root startat etc (wenn nicht gegeben nicht anzeigen)
                    - status
            - Links (3/4 breit):
                - Canvas View (oben, initial 2/3 hoch):
                    - Items (nodes aus den daten)
                        - eher quadratisch mit runden ecken
                        - erstes item: ecken oben links und unten links mehr rundung
                        - letztes item: ecken oben rechts und unten rechts mehr rundung
                        - Im Center ein Icon
                            - du bekommst daten -> anhand der typen kannst du passende icons auswählen
                            - ein schönes default icon auswählen
                        - unter dem icon den name
                        - wenn success (oder synonym wie compleated etc (du bekommst noch daten dazu))
                            - border schönes grün
                            - ein hakchen unten rechts
                        - wenn selected -> shadow hinzufügen
                    - item connections
                        - mit pfeil verbunden (wie zB in N8N Workflows)
                        - können horizental oder vertikal angeordnet werden
                        - wenn man sub-nodes nutzt
                            - dann wird ein abgerundeter pfeil nach (horizontal:oben->rechts / vertikal: rechts->unten) auf das nächste item "ausgefahren"
                                - wenn der subnode wiederum subnodes verwenden -> selbe logik (sollte hier rekursiv ermittelt werden)
                            - wenn ein node oder subnode mehrere subitems hat, muss der ausfahr-abstand (der standardisiert ist) für das erste item "Mal Anzahl subitems" genommen werden
                                - der erste wird ausgefahren zu beginn des parent items -> viel abstand
                                - der zweite wird mit etwas abstand zum ersten pfeil (auf dem item) ausgefahren, dann aber mit Abstand = "Mal Anzahl subitems - 1" und so weiter
                                    - bzw musst du ermitteln, wenn innerhlab eines subitems auch noch ganz viele subitems bestehen, muss der erste richtig weiß nach außen und so weiter
                                    - du musst also beim erstellen die abstände jeweils berechnen, damit keine items überlappen -> vielleicht gibt es noch eine sauberere lösung?
                                - ah und wichtig: auf den pfeilen zu den subitems soll in der mitte ein IconButton zum collaps und expand sein
                                    - bei collaps soll der arm eingefahren werden und nicht mehr angezeigt werden 
                                        - dann muss sich entsprechend die view sauber anpassen
                                        - bei expand wird der arm ausgefahren und die view muss wieder sauber angepasst werden
                                        - default: ausgefahren!
                                        - auf allen subnode pfleiden muss das sein, sodass ich auch zum einen den ersten subnode collapsen kann und alles unter diesem ebenfalls ausgeblendet wird, aber ich kann auch den subnode im subnode im subnode ... collapsen und dann soll dieses subnode + die darunter collapst werden -> du verstehst schon
                - Data Section (unten, initial ca 1/3 hoch)
                    - höhenanpassbar
                    - Links: Logs anzeigen
                        - Headertitel: Logs (root)
                        - Wenn kein Item selektiert -> root-logs anzeigen
                        - Wenn Item selektiert -> node-logs anzeigen
                        - eher schmal (inital 1/4 breit)
                    - rechts:
                        - initial 3/4 breit
                        - Header
                            - Tab-Bar
                                - Input + Output (nicht bei root)
                                - Metadata (referenceMetadata bei root)
                        - Input + Output:
                            - 1/2 und 1/2, breitenanpassbar
                            - Input:
                                - Text oben
                                - metadata (als JSON view)
                                - extraData (als JSON view)
                                - alle drei sections ein und ausblendbar
                                    - initial nur Text eingeblendet und anderen zu
                            - Output: wie input
                    - links/rechts breitenanpassbar
            - rechts (1/4 breit; breite anpassbar)
                - Oben: Hierarchy-View
                    - Hierachie view der Items, wie bei foundry (siehe bild)
                    - diese dient ebenfalls für die navigation und selektierung von items
                        - wenn conversation mehrere traces hat -> hier default ist die erste ausgewählt (über context kann man auch id angeben)
                        - man kann aber auch dann eine untere auswählen, dann werden die items der conversation im canvas gerendert, aus der selected conversation (*bei autonom agent wird immer nur ein trace ausgewäht!)
                    - zur hierarchie:
                        - root item ist trace oder wenn mehrere traces gegeben (nur bei conversations kann dies der fall sein, aber auch nicht wichtig), werden diese untereinander gerendert
                        - man kann root und jedes sub item entsprechend collapsen und expanden (defautl alles expandedt)
                        - item:
                            - root:
                                - Im Badge: contextType, daneben referenceName, daneben kleines icon für status
                            - node (gilt ebenso für subnodes)
                                - Im Badge: Node.type, danmeben name, daneben kleines icon für status (wenn null oder unbekannt -> einfach weglassen)
                            - wenn der name zu lang ist, wird dieser einfach abgeschnitten mit "..."
                                - beim selektieren, wird im sub header ja der name eh angezeigt
                        - die hierarchie zwischen root, nodes und subnodes wird immer mit einem schönem bogen gekennzeichnet und entsprechend der hierarchie gibt es dann links beim bogen etwas padding (beim ersten nur das icon, dann padding etc; siehe foto foundry)
                    - wenn man ein item in der hierarchie anklickt, wird dieses selektiert und dies sieht man dann auch ind er canvas view (shadow)
                        - zudem soll die canvas view dann zu diesem item im canvas navigieren und diesen zentriert zeigen
                - Unten:
                    - erstmal nur ein leerer container mit 30px höhe (placeholer)
                    - ist aber höhenverstellbar
        - Canvas
            - Canvas soll
                - mit Maus navigierbar sein (also linke maustaste gedrück halten und dann mit maus verschieben)
                - vergrößer und verkleinerbar sein (mit STRG Scroll oder wie auf Mac mit trackpad einfach rein und rausscrollen)
                - mit zB Mac Trackpad auch verschiebar (also einfach auch mit wischen mit zwei fingern schön im canvas navigieren -> du weißt bescheid)
                - man kann einzelne items auch margieren mit der Maus -> dann sieht man daten dazu, hier ist aber nur wichtig, dass halt dann um das item die border und viduell hervorgehoben wird (nur shadow?)
                - so typische buttons:
                    - zum start navigeren und "zentrieren"
                    - vergrößern
                    - verkleinern
                    - view: horizental, vertikal -> wie die items angeordnet werden (default horizontal!)

Für die Entwicklung der traces-visualisierung, bauen mir bitte die page `TracingDialogDevelopment`, welche unter `/dev/tracing` aufrufbar ist.
Default soll der Dialog direkt aufgehen und über query params will ich steuern, welche traces du holst:
entweder:
    - ?conversationId={"CONVERSATION_ID"} => dann fetchst du `{{host_agent_service}}/api/v1/agent-service/tenants/{{tenant_id}}/conversations/{{conversation_id}}/traces`
        - returns : {"traces": [...]}
        - siehe api client; wenn noch nicht implementiert, schaue in die routes.go und response schema und implementiere den client.ts und types.ts für diese route
    - ?autonomousAgentId={"AUTO_AGENT_ID"} => dann fetchst du `{{host_agent_service}}/api/v1/agent-service/tenants/{{tenant_id}}/autonomous-agents/{{autonomous_agent_id}}/traces`
        - returns : {"traces": [...]}
        - siehe api client; wenn noch nicht implementiert, schaue in die routes.go und response schema und implementiere den client.ts und types.ts für diese route
        - => ja, hier bekommst du dann mehrere von auto agent traces, aber auch das sollte ja kein problem sien, da selbe response!

**Diene Aufgaben**
1. Analysiere meine Anforderungen und definiere für dich optimierte Anfordeurngen, mit denen du super arbeiten kannst
2. Analysiere die tracing struktur (siehe, wie N8N und foundry traces entsprechend importiert werden)
3. Analyisere die "unifiedui.traces.json" datei, um verschiedene Daten zu sehen, die du bekommen kannst
4. Analysiere die Projektstruktur des Frontend-services; insbesondere die design farben
5. Baue mir die Page `TracingDialogDevelopment` und erstelle im route die route `/dev/tracing`
6. Plane die Implementierung des `TracingVisualDialog` entsprechend modular (ich will im chat auch in einer quick view zB nur die hierarchie verwenden etc)
7. Implementiere die module für den `TracingVisualDialog` und letztendlich den dialog, der auch direkt aufgehen soll auf /dev/tracing?...

Sollten noch weitere UI Libraries nötig sein, gerne diskutiere mit dir, welche am besten passen würde.

**Aktuelisieren**
- Subnodes lieber in einer Baumstruktur aufgehen lassen
    - siehe [Image Video von xyflow](https://xyflow.com/)

- Frontend Refactoring 1
    - Credentials raus aus Sidebar und in Tenant-Settings rein
        - extra Tab; ähnlich wie Cutsom Groups
    - MCP Servers als Tab in Tenant Settings rein -> erstmal nur Dummy Page wie Custom Groups
    - Development Platforms raus
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

- agent-service
    - N8N Traces refactoren
    - Foundry Traces refactoren

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
    - weitere features
        - PIN (favorietes)
        - last visited
    - Dashboard
    - ...


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