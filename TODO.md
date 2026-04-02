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


- Redesign:
    - Main-Search
        - search-results
            - -> hier bitte batches mit farben für die einzelnen kategorien (conversations, messages, external apps, chat-widgets, agents, settings items etc) anzeigen
            - es soll mit load more (wenn mehr geladen werden könnte) paginiert werden in search results
        - hier geht dialog auf -> dialog überarbeiten:
            - sucht nicht nach/in:
                - messages (bitte gleiche suche wie bei conversation page nutzen und anzeigen)
                    - es wird nmur nach conversations gesucht, aber nicht nach messages -> das ist aber wichtig
                - external apps (keine external apps werden gesucht)
                - chat-widgets (werden nicht gesucht; nur standard widgets werden angezeigt, diese sollten aber NICHt angezeigt werden, da die keinen link haben, auf den man navigieren kann!)
                - ReACT Agents werden gesucht, aber falscher link -> wird auch chat-agents/{id} geleitet
                - die settings-items werden auch nicht gesucht:
                    - principals (in db)
                    - custom groups
                    - ai models
                    - tools
                    - credentials
                    - ==> bei all diesen items fehlt noch der support von query param mit id -> aktuell nur /tenant-settings?tab=iam; aber wenn man item auswählt und dialog erscheint -> wird nicht ?tab={tab}&selectedId={id} gemacht -> das muss rein, damit wir ne saubere struktur haben und auch beim suchen auf das item navigieren können!
                - bei chat-agents, chat-widgets und workflows (autonomous agents) haben wir ja zwei wege
                    - 1. auf die page navigieren
                    - 2. Edit dialog
                    - => hier will ich zwei buttons neben einander -> Open / Edit
                        - open -> navigiert auf page
                        - edit -> öffnet dialog
            - Struktur:
                - Commands -> finde ich gut, aber:
                    - 1. die links sind komplett quatsch
                        - zB new agent -> navigiert auf /new -> wir brauchen aber auf /chat-agents?dialog=new (das muss hinzugefügrt werden) und dann den link auf diese route
                    - 2. dann fehlt da nich: create workflow, create chat-widget, create credential, create tool, create ai model, create custom group, Add principal (natürlich nur, wenn rolle gegeben ist!)
                - navigation: ganz raus. ist quatsch!
        - wenn man über die items hovert, wird das nicht gehighlightet. sollte leicht gehighlight werden
        - im dark mode sieht man den shadow nicht. entweder dunkler oder ich denke her heller machen; und im light mode sieht man zB die border-line nicht (vermutlich wegen der farbe). das finde ich viel schöner. im dark mode sieht man sone helle line. fände es besser, wenn das im darkmode angepasst wird
    - Sidebar
        - blende react-agents erstmal aus (nicht löschen, nur ausblenden!)
        - data sidebar
            - hier haben ja eine data sidebar für die einzelnen items entwickelt. ich fand die idee super, aber die nutzung war noch nicht gut
                - zuvor war es so, dass immer wenn wir über ein sidebar item gehovert haben, wurde eine quicklist (data sidebar) angezeigt. nur nicht, wenn man schon auf der List-Page war.
                - das führte dazu, dass ständig diese data sidebar aufgeflackert ist, wenn man nur auf das sidebar item klicken wollte. da brauchte man die quicklist einfach nicht
                - die neue idee ist es, die data sidebar für ein item nur anzuzeigen, wenn man auf einer detail-page des items ist. sinn: ich bin auf detail page, möchte mit einem klick easy in ein anderes item des selben types welcheln
                    - konkret:
                        - /autonomous-agents/7baa5880-e4c4-488d-8521-0bd560de6300 => jetzt zeige ich, wenn ich über workflows in sidebar hovere, die data sidebar mit den anderen workflows an
                        - /external-apps/d74a270b-e15c-4b13-8337-c5ba7aceacb5 => wenn ich über external apps in sidebar hovere, zeige ich die data sidebar mit den anderen external apps an
                        - /widget-designer/66493869-a2b3-4e07-ac4a-c68d402646c8 => wenn ich über chat-widgets in sidebar hovere, zeige ich die data sidebar mit den anderen chat-widgets an
                        - /widget-widget/66493869-a2b3-4e07-ac4a-c68d402646c8 => wenn ich über chat-widgets in sidebar hovere, zeige ich die data sidebar mit den anderen chat-widgets an
                        - /chat-agents/1c41d5e8-15a8-494c-8c5d-2751484f24c0/develop => wenn ich über ReACT Agents in sidebar hovere, zeige ich die data sidebar mit den anderen ReACT Agents an
                        - *Nur bei diesen items -> bei chats und bei chat-agents brauchen wir das nicht!
        - wenn ich auf /chat-widgets auf "form" item gehe, werde ich auf /widget-designer/{id} geleitet. ist dein für mich, aber dann muss auch das sidebar item bei chat-widget/{id} UND bei /widget-designer/{id} aktiv sein. aktuell ist es so, dass nur bei /widget-designer/{id} das chat-widget item aktiv ist, aber nicht bei /chat-widgets/{id}.
        - beim klick auf settings icon, soll auf /settings?tab=iam nabigiert werden.
        - 
    - Styling
        - colors
            - im dark mode fällt es sehr auf, dass man shadow praktisch nur sehr selten sieht!
                - man sieht immer nur ne border die sehr hell ist. finde ich nicht so schön. bitte vielleicht einmal ein alternatives design für cards und container im darkmode ausarbeiten
        - Allgemein:
            - Icons und Icons konsistent für ein Item
        - Cards: Schatten im Dark-Mode nicht sichtbar -> ?hellerer/dunklerer? schatten!
        - auf manchen seiten -> läd gesamte content-page (nicht sidebar, header, aber site-header) solange auch die daten laden... das sollte nicht so sein. der cntent header sollte direkt da sein
    - Dashboard
        - mehr variation
        - Funktionale fixen:
            - 
        - Funktionalität erweitern
            - 
    - Chats
        - Create-
    - List Pages (Agents, Workflows)
        - Anpassung Filter / Suche:
            - die Sortier-Optionen
    - Detail Pages
    - ...
    - Settings
        - Organisation:
            - Tabelle mit Tenants unten (page unten skrollbar )
    - Dialoge
    - UX
        - Error Notifications:
            - ja, es ist wichtig dem nutzer die richtigen error notifications anzuzeigen, allerdings wird es aktuell übertieben.
                - zB wenn ich mit mit reader anmelde, bekomme ich erstmal beim starten der app oder bei settings zig error messages, dass ich auf die orga nicht zugreifen kann, irgendwas bei tenants nicht abfrgane kann und so weiter.
                - bitte checke einmal das UX verhalten bei error messages.
                    - ja, wenn nutzer auf einen button klickt um zB daten abzufragen, dann soll error message kommen, oder wenn er auf seite navigiert und es gibt nen 500er bzw. zB der serrvr nicht erreichbar ist
                    - vielleicht müssen wir auch einfach nur die aufrufe optimieren -> bei klick auf button -> immer ausführen, aber wenn auf seite navigiert und nutzer reader oder so ist und wir wissen ja, auf welche endpoints er zugriff hat, dann brauchen wir beim navigieren zB auf settings nicht irgendwelche protectet routes aufrufen. ist auch gleichzeitig performance optimierung!
                - hier das issue dazu: https://github.com/orgs/unified-ui/projects/1/views/2?pane=issue&itemId=165464674&issue=unified-ui%7Cunifiedui%7C11
        
    



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
