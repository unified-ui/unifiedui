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

Ich möchte ein Redesign der App machen, um es moderner, ansprechender und auch nutzerfreundlicher zu machen. Es soll aber nicht nur ein Redesign sein, sondern auch funktionale Verbesserungen und Erweiterungen geben, damit die App insgesamt besser wird.
Dafür entwickeln wir gemeinsam zwei Dateien, auf die immer wieder verwiesen werden kann.
Ich habe grobe Anforderungen definiert. diese möchte ich von dir in eine klare saubere anforerungsstruktur bringen, welche strukturiert und sequenzell Pakete mit Anforderungen definiert, damit ich diese dann Stück für Stück implementieren kann.
Diese Datei stellt die Anforderungen dar.
Die zweite Datei Soll dann zu jedem Anforderungspunkt die konkrete Implementierung beschreiben.
Die Requirements können in einem Batch definiert werden, ich schaue rüber und gebe anmerkungen.
Wenn die Reuqiremtns-datei passt, soll jedes arbeitspaket einzeln in einem Batch geplant, von mir reviewt und dann das nächste paket geplant, von mir reviert werden und  so weiter.
wenn der implementierungsplan dann steht, wirst du mir alle anpassungen nacheinander (jedes paket einzeln) implementieren. nach der implementierung eines pakets, teste ich die implementierung, werde anpassungen geben und dann irgendwann final sagen, dass das paket so passt. bei diesem prozess markiertst du dann den titel das paketes mit (startet, in progress, fertig oder so ähnlich), damit ich und du immer den überblick habe, was gerade implementiert wird und was schon fertig ist.

Hier einmal meine semistrukturierten Anforderungen:

```
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
                - vielleicht border gleiche farbe wie item-background, damit man nicht sieht oder sehr ähnlich, damit man die nicht so präsent sieht
            - der dark mode ist generell sehr schwarz-weiß; bisschen blau; farbe kommt fast nur über badges rein. vielleicht könnte man hier generell etwas mehr farbe reinbringen, damit es nicht so trist ist? es soll clean sein, aber auch modern und ansprechend
        - Allgemein:
            - Icons und Icons konsistent für ein Item
                - zB Create chat agent
            - auf manchen seiten -> läd gesamte content-page (nicht sidebar, header, aber site-header) solange auch die daten laden... das sollte nicht so sein. der cntent header sollte direkt da sein
                - nur als beispiel: auf external Apps seite -> aktuell wird einfach loading spinner in der mitte der seite angezeigt, bis alle daten da sind. das ist aber nicht so schön. man kann ja den header ganz normal anzeigen und liste laden -> wie zB in chat-agents list page oder auch workflows!
    - Page:Dashboard (/dashboard)
        - Layout/Design überarbeiten:
            - die kacheln "Chat Agents, "Wofklows" finde ich super. können bleiben
            - ich stelle mir oben den titel vor, wie er gerade ist; ganz rechts ein button "Create" mit sonem arrow-dropdown icon -> da drauf klick -> dropdown mit den items: Chat Agents, Workflows, Chat Widgets, External Apps, Credentials, Tools, AI Models, Custom Groups, Principals -> je nachdem was man auswählt, öffnet sich der entsprechende create dialog auf der seite
            - unter den aktuellen kacheln sollte sone horizontale kachel-gallery sein, die man per navigationsbuttons nach rechts und links scrollen (je ein item) kann. in den kacheln werden dann die items angezeigt, die man zuletzt besucht hat (recently visited/interagiert hat)
                - die Card (quadratisch, maximal leicht rechteckig (breiter als hoch)) (ähnlich wie die aktuellen Kacheln oben -> Anzahl Chat Agents etc):
                    - in card oben icon des items; darunte rin groß dick der namen; darunter der typ (wie aktuell schon in der card) und darunteer in recht klein und weniger deutlich: wann letztes mal besucht (vor <zeit> minuten, stunden, tage, wochen, monate)
                    - oben rechts mit einem sternchen anzeigen, obs favorit ist; aber hir nicht toggeln können und wenn kein favorit, auch stern nicht zeigen
                - max 25 abfragen und anzeigen!
            - darunter sollte man auch noch die favorieten als so wrapped card-list sehen; wie aktuell, aber mit load more button wenn möglich.
            - aktuell lässt sich die page nicht skrollen... Der titel sollte oben fixiert bleiben, aber die seite (content) sollte dann auch skollfähig sein
        - Funktionale fixen:
            - die links gehen alle auf /chat-agents/{id}. das muss dann in dem neuen dashboard natürlich korrekt sein
        - Funktionalität erweitern
            - schon im design beschreiben
    - Page:Chats (/conversations)
        - Layout/Design überarbeiten
            - aktuell sind die "vorschläge" die man für einen chat agent definieren kann im "_emptyState_1jccf_1" container bzw gerade nicht mal mehr zu sehen
                - die sollen über dem _inputOuterWrapper_1547w_11 liegen und die brauchen auch bisschen padding die badges
                - in der conversation sidebar ist der new chat button links neben dem search button im m_4081bf90 mantine-Group-root; bitte new chat button nach rechts und search nach links
            - Component: Tracing-Hierarchie für Conversation page überarbeiten:
                - der container (_container_3d3v3_1) für logs, metadata etc ist initial zu wenig hoch. bitte hier höher inital (doppelt so hoch). kann man ja erhöhen, aber ist mit zu niedrig initial!
                - dann sollte der container (_container_3d3v3_1) gleiche background color wie auch die tracinig hierachie oben (m_c0783ff9 mantine-ScrollArea-viewport) haben. sieht sonst komisch aus
                - 
        - Funktionale fixen:
            - keine
        - Funktionalität erweitern
            - keine
    - Page:EmbedChat (/chat-agents/{id}/embed-chat)
        - Layout/Design überarbeiten
            - puh. mir gefällt die page design-technisch gar nicht!
                - einfach nur container mit rundungen und gleiche farben...
                - die aufteilung ist okay, aber die container cards gefallen mir überhaupt nicht. bitte arbeite gerne ein neues design/layout für diese seite aus! gebe mir das als layout design und vorschläge
                - inhaltlich passt das, nur die container finde ich voll langweilig...
        - Funktionale fixen:
            - keine
        - Funktionalität erweitern
            - aktuell haben wir oben ne navigation "Chat Agents > {agent name} > Embed Chat". {angent name} ist aber nicht klickbar. ich fände es gut, wenn man dann in den chat springen würde. und die sidebar sollte hier auch auf Chat Agents aktiv sein und auch die data sidebar dann zeigen. liegt ja auf dem pfad
    - Page:Agents (/chat-agents)
        - Layout/Design überarbeiten
            - Create Dialog:
                - type: neue order: Microsoft Foundry / n8n / REST API / ReACT Agent
                - is active: default auf true!!!
            - 3-dot-menu: nimm "Pin" raus. hat keine funktion und wir haben fav schon vorne in der liste
        - Funktionale fixen:
            - keine
        - Funktionalität erweitern:
            - ?dialog=new -> öffnet den create dialog für chat agents
            - duplicate -> dupliziert agent 1:1 und schreibt hinter: "Copy" bzw "Copy{n}" wenn schon Copy existiert
                - dafür brauchen wir wahrschenlich backend endpoint! planen!
    - Page:Workflows (/autonomous-agents -> in /workflows umbenennen)
        - Layout/Design überarbeiten
            - 3-dot-menu: nimm "Pin" raus. hat keine funktion und wir haben fav schon vorne in der liste
        - Funktionale fixen:
            - keine
        - Funktionalität erweitern:
            - siehe Agents Page
    - Workflow-Details (/autonomous-agents/{id} -> in /workflows/{id} umbenennen)
        - Layout/Design überarbeiten
            - ?tab=details
                - auch hier ist wieder so eine langweilige "container-struktur" gegebene wie bei Embed Chat. bitte hier auch gerne neues design/layout vorschlagen und ausarbeiten lassen!
            - wenn ich in den dialog "Integrate Autonomous Agent" gehe, hat dieser zB ein icon mit hintergundfarbe. find eich richtig nice. ich finde, die create und edit dialoge für agenten, workflows etc etc könnten genau dieses pattern auch nutzen. daher gerne hier diesen header für den zentalen dialog nutzen...
        - Funktionale fixen:
            - keine
        - Funktionalität erweitern:
            - keine
    - Page:External Apps (/external-apps)
        - Layout/Design überarbeiten
        - Funktionale fixen:
            - keine
        - Funktionalität erweitern:
            - ?dialog=new -> öffnet den create dialog für external apps
            - hat keine query params für editSelectedId etc. sowas brauchen wir immer, wenn ein dialog geöffnet wird. 
            - cards haben bei titel und description keinen tooltip wie überall sonst auch, wenn was zu groß ist. bitte hinzufügen
    - Page:ChatWidgets (//chat-widgets)
        - Layout/Design überarbeiten
            - 3-dot-menu: nimm "Pin" raus. hat keine funktion und wir haben fav schon vorne in der liste
        - Funktionale fixen:
            - keine
        - Funktionalität erweitern:
            - ?dialog=new -> öffnet den create dialog für chat widgets
            - hat keine query params für editSelectedId, dialog=prompt-integration/new etc. sowas brauchen wir immer, wenn ein dialog geöffnet wird.
            - implement duplicate funktion wie bei agents und workflows
    - Page:ChatWidget-Details (/chat-widgets/{id}) (bei iFrame type)
        - Layout/Design überarbeiten
            - auch wieder sehr sehr langweilige container struktur. bitte hier auch gerne neues design/layout vorschlagen und ausarbeiten lassen!
        - Funktionale fixen:
            - so width und height / allow full screen eigentlich total irrelevant, weil wir das im chat-window sowieso so rendern wie es geht! also hier diese onfigmöglichkeiten im FE entfernen und im Backend genauso. wir brauchen im prinzip nur die url.
        - Funktionalität erweitern:
            - Wenn ich oben links auf den Namen, soll daraus text box werden und ich soll den Namen editieren können. bei enter dann speichern!
            - denk dran -> hier audch data sidebar beim hovern!
    - Page:ChatWidget-Designer (/widget-designer/{id}) (bei form type)
        - Layout/Design überarbeiten
            - hier werden wir gesondert dran arbeiten!
        - Funktionale fixen:
            - keine
        - Funktionalität erweitern:
            - bei den 3-dots menu; auch edit details hizufügen und den dialog verfügabr machen!
    - ListPages -> haben fast alle einen toggle button für "active"
        - überall (liste, tabelle etc) wo toggle ist -> wenn von true auf false gestellt werden soll -> immer fragen mit dialog (wie bei delete, nur halt als warning dialog), ob man wirklich deaktivieren möchte. das item ist dann nicht mehr aktiv und verfügbar...
    - Settings
        - Organisation:
            - Tabelle mit Tenants unten (page unten skrollbar)
        - alle:
            - einfach darauf achten, auch hier IMMER mit query params zu arbeiten, wenn dialoge geöffnet werden. also ?tab={tab}&selectedId={id} oder ?tab={tab}&dialog=new etc. damit wir eine saubere struktur haben und auch beim suchen auf das item navigieren können!
        - create custom group -> hier zB kein icon im dialog header -> also wirklich wichtig zentralen dialog mit standard header zu bauen und zu reusen (für create und edit; NICHT alle!)
    - UX
        - Error Notifications:
            - ja, es ist wichtig dem nutzer die richtigen error notifications anzuzeigen, allerdings wird es aktuell übertieben.
                - zB wenn ich mit mit reader anmelde, bekomme ich erstmal beim starten der app oder bei settings zig error messages, dass ich auf die orga nicht zugreifen kann, irgendwas bei tenants nicht abfrgane kann und so weiter.
                - bitte checke einmal das UX verhalten bei error messages.
                    - ja, wenn nutzer auf einen button klickt um zB daten abzufragen, dann soll error message kommen, oder wenn er auf seite navigiert und es gibt nen 500er bzw. zB der serrvr nicht erreichbar ist
                    - vielleicht müssen wir auch einfach nur die aufrufe optimieren -> bei klick auf button -> immer ausführen, aber wenn auf seite navigiert und nutzer reader oder so ist und wir wissen ja, auf welche endpoints er zugriff hat, dann brauchen wir beim navigieren zB auf settings nicht irgendwelche protectet routes aufrufen. ist auch gleichzeitig performance optimierung!
                - hier das issue dazu: https://github.com/orgs/unified-ui/projects/1/views/2?pane=issue&itemId=165464674&issue=unified-ui%7Cunifiedui%7C11
    - refactoring:
        - wir haben ja viele dialoge. man könnte für so edit/create dialoge ein zentrales dialog component bauen, welches header mit icon und titel + schlißen button hat und dann ne content area, die frei gestaltbar ist. dann sehen components immer einheitlich aus.
            - ich finde die dialoge sehr gut! aber wenn ich neue von copilot erstellen lasse, sind die immer etwas anders und der baut immer wieder nach -> hier könnte man eine einheitliche dialog struktur vorgeben, damit die dialoge immer gleich aussehen
            - überall wo noch "Autonomous Agent(s)" steht, bitte in "Workflows" ändern. in dialogen, in buttons, in url routes; überall!
    - weiteres:
        - /dashboard in /home ändern!!! beachte dabei auch das routing von / etc etc.
    - Anmerkung:
        - Wir brauchen glaube common CreateDialogCommon und EditDialogCommon; da sich die header hier auch unterscheiden. ich finde den edit dialog header sehr sehr schon. also sollten wir hier zwei haben. vielleicht noch einen weiteren für info, warn, und configrm deletion etc. du verstehst
```

Erstelle aus meinen groben Anforderungen ein detaillierten Anforderungskatalog, der logisch aufbauend ist und kategorien in pakete packt.
zB erstmal allgemeine Themen wie die umbenennung, oder sachen, die halt übergreifen sind; diese dann erstmal in kleine arbeitspakete bündeln und requirements beschreiben
bsp:
1. Allgemeine Themen (voraussetzungen für die anderen Pakete)
    1.1 Umbenennung Autonomous Agents in Workflows
    1.2 Einheitliche Dialogstruktur
    1.3 Error Notifications UX optimieren
    1.4 ListPages: Deaktivieren von Items mit Bestätigungsdialog
    ...
2. Redesign
    2.1 Main Search
    2.2 Sidebar
    2.3 Colors (Dark Mode)
    2.4 Page: Dashboard
    2.5 Page: Chats
    2.6 Page: EmbedChat
    2.7 Page: Agents
    2.8 Page: Workflows
    2.9 Page: Workflow Details
    2.10 Page: External Apps
    2.11 Page: Widgets
    ....


Hast du alle deine Aufgaben verstanden.
Hast du rückfragen zu irgendeiner Zeit, stelle diese bitte gern!


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
