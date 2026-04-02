# 001 — Redesign & Funktionale Erweiterungen v0.2.0

> **Status:** DRAFT  
> **Scope:** unified-ui-frontend-service, unified-ui-platform-service  
> **Ziel:** Moderneres, ansprechenderes Design + funktionale Verbesserungen + bessere UX

---

## Arbeitsweise & Prozess

> **Dieses Dokument ist das zentrale Tracking- und Anforderungsdokument.**  
> Es gibt keine separate Implementierungsplan-Datei. Alles wird hier gesteuert.

### Ablauf pro Paket (0, 1, 2, …)

1. **Implementierungsübersicht**: Copilot liest den relevanten Code ein und erstellt eine kompakte Übersicht: welche Dateien betroffen sind, welcher Ansatz gewählt wird, bei Design-Paketen konkrete Varianten mit Empfehlung.
2. **Review**: Nutzer prüft die Übersicht, gibt OK oder Korrekturen.
3. **Implementierung**: Copilot implementiert das **gesamte Paket** (alle Teilpakete zusammen, nicht einzeln).
4. **Test & Feedback**: Nutzer testet die Implementierung und gibt Anpassungswünsche.
5. **Abschluss**: Paket wird als `✅ Done` im Titel markiert → weiter zum nächsten Paket.

### Status-Tracking

Jedes Paket bekommt einen Status-Marker im Titel:
- *(kein Marker)* → Noch nicht begonnen
- `⏳ In Progress` → Gerade in Bearbeitung
- `✅ Done` → Fertig implementiert und abgenommen

### Regeln

- Immer ein **komplettes Paket** als Einheit bearbeiten (nicht Teilpakete einzeln).
- Bei Design-Entscheidungen (Dark-Mode-Variante, Container-Redesign) werden konkrete Optionen mit CSS-Beispielen gezeigt → Nutzer wählt vor der Implementierung.
- Dieses Dokument kann in jeder neuen Session als Kontext geladen werden, um den aktuellen Stand und nächsten Schritt zu kennen.
- Backend-Änderungen (platform-service) werden im selben Paket miterledigt, wenn das Paket Backend-Anforderungen enthält.

---

## Paket 0: Voraussetzungen & Übergreifende Grundlagen ✅ Done

> Grundlegende Änderungen, die als Basis für alle nachfolgenden Pakete dienen.

### 0.1 Umbenennung "Autonomous Agents" → "Workflows"

| ID | Anforderung |
|----|-------------|
| 0.1.1 | **Frontend — Route-Umbenennung**: `/autonomous-agents` → `/workflows`, `/autonomous-agents/{id}` → `/workflows/{id}`. Alte Routen per Redirect auf neue weiterleiten. |
| 0.1.2 | **Frontend — UI-Strings**: Alle Vorkommen von "Autonomous Agent(s)" in i18n-Dateien, Komponenten, Dialogen, Buttons, Breadcrumbs und Tooltips durch "Workflow(s)" ersetzen. |
| 0.1.3 | **Frontend — Code-Referenzen**: Interne Variablen-, Typ- und Komponentennamen, die `autonomousAgent` enthalten, auf `workflow` umstellen (z.B. `AutonomousAgentsPage` → `WorkflowsPage`, Route-Mappings, Sidebar-Konfiguration etc.). |
| 0.1.4 | **Backend — Keine Änderung an API-Pfaden** (bleiben `/autonomous-agents`). Nur Frontend-seitige Umbenennung in Routing, UI-Strings und internem Code. |

### 0.2 Route-Umbenennung "/dashboard" → "/home"

| ID | Anforderung |
|----|-------------|
| 0.2.1 | Route `/dashboard` in `/home` umbenennen. Default-Redirect von `/` auf `/home`. |
| 0.2.2 | Alle internen Navigationslinks, Sidebar-Referenzen und i18n-Keys aktualisieren. |

### 0.3 Einheitliche Dialog-Struktur (CreateDialog / EditDialog / ConfirmDialog)

| ID | Anforderung |
|----|-------------|
| 0.3.1 | **CreateDialogHeader**: Standard-Header für Create-Dialoge mit Icon (in farbigem Container, wie bei `UnifiedDialog.titleIcon`), Titel und Schließen-Button. Wiederverwendbar für alle Create-Dialoge. |
| 0.3.2 | **EditDialogHeader**: Standard-Header für Edit-Dialoge. Abweichendes Design vom Create-Header (bestehendes Pattern aus z.B. "Integrate Autonomous Agent"-Dialog mit Icon + farbigem Hintergrund als Vorlage). Wiederverwendbar für alle Edit-Dialoge. |
| 0.3.3 | **ConfirmDialog**: Einheitlicher Dialog für Bestätigungen (Delete, Warn, Info). Konfigurierbar mit Typ (`danger` / `warning` / `info`), Icon, Titel, Beschreibung und Confirm/Cancel-Buttons. |
| 0.3.4 | Alle bestehenden Create- und Edit-Dialoge auf die neuen einheitlichen Header migrieren, damit konsistentes Erscheinungsbild über gesamte App gegeben ist. |
| 0.3.5 | Jeder Dialog muss ein zum Ressourcentyp passendes, konsistentes Icon verwenden (z.B. Agent → `IconSparkles`, Workflow → `IconRobot`, Credential → `IconKey` etc.). |

### 0.4 Query-Parameter-Konvention für Dialoge

| ID | Anforderung |
|----|-------------|
| 0.4.1 | **Konvention definieren**: Alle Seiten mit Dialogen müssen Query-Parameter nutzen, um Dialogzustand in der URL abzubilden: `?dialog=new` (Create), `?dialog=edit&selectedId={id}` (Edit), `?dialog=delete&selectedId={id}` (Delete). |
| 0.4.2 | Beim Öffnen eines Dialogs werden Query-Params gesetzt, beim Schließen entfernt. Bei Navigation auf URL mit Query-Params öffnet sich der entsprechende Dialog automatisch. |
| 0.4.3 | Gilt für: Chat Agents, Workflows, Chat Widgets, External Apps und Settings-Tabs (Principals, Custom Groups, AI Models, Tools, Credentials). |
| 0.4.4 | **Settings-Seite erweitern**: `?tab={tab}&selectedId={id}` bzw. `?tab={tab}&dialog=new` — damit beim Öffnen einer Settings-URL mit ID der passende Dialog mit dem selektierten Item geöffnet wird. |

### 0.5 ListPages: Deaktivierungsbestätigung

| ID | Anforderung |
|----|-------------|
| 0.5.1 | Überall, wo ein Toggle-Button für "active"/"inactive" existiert (Listen, Tabellen, Detail-Seiten): Beim Wechsel von `active` → `inactive` muss ein **Warning-ConfirmDialog** erscheinen (Typ: `warning`). |
| 0.5.2 | Dialog-Text erklärt, dass das Item deaktiviert wird und nicht mehr verfügbar ist. Erst nach Bestätigung wird die Änderung durchgeführt. |
| 0.5.3 | Wechsel von `inactive` → `active` benötigt keine Bestätigung. |

### 0.6 Error-Notification UX

| ID | Anforderung |
|----|-------------|
| 0.6.1 | **Fehler-Anzeige nur bei User-initiierter Aktion**: Error-Notifications nur zeigen, wenn der Nutzer eine Aktion ausgelöst hat (Button-Klick, Form-Submit, explizite Navigation). |
| 0.6.2 | **Keine Error-Notifications bei Seiten-Load für fehlende Berechtigungen**: Wenn beim Laden einer Seite API-Calls fehlschlagen, weil der Nutzer (z.B. Reader-Rolle) keine Berechtigung hat, sollen KEINE Error-Toasts angezeigt werden. Stattdessen: Daten einfach nicht laden / leere States zeigen. |
| 0.6.3 | **API-Call-Optimierung**: Auf Seiten wie Settings bei Reader-Rolle keine geschützten Endpoints aufrufen, die der Nutzer nicht erreichen kann. Vor dem Aufruf die Benutzerrolle prüfen (`usePermissions`). |
| 0.6.4 | **Server-Fehler (5xx) und Netzwerkfehler**: Weiterhin als Error-Notification anzeigen — diese sind immer relevant. |
| 0.6.5 | Referenz: [GitHub Issue #11](https://github.com/orgs/unified-ui/projects/1/views/2?pane=issue&itemId=165464674&issue=unified-ui%7Cunifiedui%7C11) |

### 0.7 Konsistente Icons pro Ressourcentyp

| ID | Anforderung |
|----|-------------|
| 0.7.1 | Für jeden Ressourcentyp ein festes Icon definieren und diese global konsistent nutzen (Sidebar, Dialoge, Cards, Badges, Search-Results, Dashboard). |
| 0.7.2 | Mapping: Chat Agent → `IconSparkles`, Workflow → `IconRobot`, Conversation → `IconMessages`, Chat Widget → `IconMessageChatbot`, External App → `IconWorld`/`IconApps`, Credential → `IconKey`, Tool → `IconTool`, AI Model → `IconCpu`, Custom Group → `IconUsersGroup`, Principal → `IconUser`. |
| 0.7.3 | Alle bestehenden Stellen prüfen und inkonsistente Icons vereinheitlichen. |

---

## Paket 1: Dark-Mode & Styling-Überarbeitung

> Globale visuelle Verbesserungen für beide Color-Schemes.

### 1.1 Dark-Mode: Schatten & Border-Überarbeitung

| ID | Anforderung |
|----|-------------|
| 1.1.1 | **Cards und Container im Dark Mode**: Border-Farbe angleichen an Item-Background-Farbe oder sehr ähnliche Farbe → Border soll subtil bis unsichtbar sein, NICHT kontrastreich hell auf dunklem Hintergrund. |
| 1.1.2 | **Shadow im Dark Mode**: Alternativen zu Box-Shadow erarbeiten — entweder dunklere/dezentere Shadows oder dezente `border` + leichter Glow-Effekt durch hellere Border bei Hover. |
| 1.1.3 | **Designvorschläge im Implementierungsplan erarbeiten** — mindestens 3 Varianten mit Empfehlung. Mögliche Richtungen: <br>**A)** Subtle Elevation — fast unsichtbare Border (`1px solid rgba(255,255,255,0.04)`), kein Shadow, Hover zeigt leichte Border-Aufhellung <br>**B)** Soft Glow — keine Border, dezenter farbiger Glow (`box-shadow: 0 0 12px rgba(primary, 0.08)`), Hover verstärkt Glow <br>**C)** Layered Surfaces — unterschiedliche Background-Helligkeiten für Tiefe (bg-app < bg-surface < bg-elevated), keine Shadows/Borders nötig |

### 1.2 Dark-Mode: Mehr Farbakzente

| ID | Anforderung |
|----|-------------|
| 1.2.1 | Der Dark Mode ist aktuell sehr schwarz-weiß mit wenig Farbe. Mehr Farbakzente einbringen (z.B. Gradient-Akzente, subtile farbige Hintergründe für aktive States, leichte Farbe in Section-Headern). |
| 1.2.2 | **Designvorschläge im Implementierungsplan erarbeiten** — mindestens 3 Varianten mit Empfehlung. Mögliche Richtungen: <br>**A)** Accent Tint — Aktive Sidebar-Items bekommen subtilen Primary-Hintergrund (`rgba(primary, 0.08)`), Cards bei Hover leichten farbigen Rand, Section-Header mit feinem Gradient-Underline <br>**B)** Colored Surfaces — Icon-Container in Dialogen/Cards behalten farbige Hintergründe (wie aktuell `titleIcon`), Stat-Cards und Badges benutzen satte Farben auf dunklem Grund, Rest bleibt neutral <br>**C)** Gradient Touches — Dezente Gradient-Akzente an strategischen Stellen (Sidebar-Active, Page-Header-Underline, Card-Top-Border als 2px Gradient-Linie), ergibt modernen Look ohne zu bunt zu sein |
| 1.2.3 | Soll clean & modern bleiben — kein Regenbogen, sondern gezielte Farbakzente an wenigen Stellen. |

### 1.3 Light-Mode: Border-Konsistenz

| ID | Anforderung |
|----|-------------|
| 1.3.1 | Im Light Mode: Border-Line bei CommandPalette-Dialog und anderen Containern ist zu unauffällig/unsichtbar. Sicherstellen, dass Borders in beiden Modi konsistent sichtbar (aber subtil) sind. |

### 1.4 Content-Loading-Pattern vereinheitlichen

| ID | Anforderung |
|----|-------------|
| 1.4.1 | Auf allen Seiten: Page-Header (Titel, Breadcrumb, Action-Buttons) sofort rendern. NUR der Datenbereich (Liste, Cards, Details) zeigt Loading-Skeleton/Spinner. |
| 1.4.2 | Beispiel Ist-Zustand: External Apps Page zeigt zentrierten Spinner ohne Header → Soll: Header sofort sichtbar, Liste lädt mit Skeleton. |
| 1.4.3 | Alle Seiten prüfen und Pattern konsistent umsetzen (Vorlage: ChatAgentsPage, WorkflowsPage/AutonomousAgentsPage). |

---

## Paket 2: Sidebar-Überarbeitung

### 2.1 ReACT Agents ausblenden

| ID | Anforderung |
|----|-------------|
| 2.1.1 | Sidebar-Item "ReACT Agents" temporär ausblenden (nicht löschen). Code beibehalten, nur `visible: false` oder Äquivalent. |

### 2.2 Data-Sidebar: Neues Hover-Verhalten

| ID | Anforderung |
|----|-------------|
| 2.2.1 | **Alte Logik entfernen**: Bisheriges Verhalten (Hover auf Sidebar-Item → Data-Sidebar aufklappen, außer wenn auf List-Page) wird komplett ersetzt. |
| 2.2.2 | **Neue Logik**: Data-Sidebar nur anzeigen, wenn der Nutzer sich auf einer **Detail-Page** des jeweiligen Ressourcentyps befindet UND über das zugehörige Sidebar-Item hovert. |
| 2.2.3 | **Konkrete Zuordnung**: <br>• `/workflows/{id}` → Hover auf "Workflows" sidebar item → Data-Sidebar mit Workflow-Liste <br>• `/external-apps/{id}` → Hover auf "External Apps" → Data-Sidebar mit External-Apps-Liste <br>• `/widget-designer/{id}` ODER `/chat-widgets/{id}` → Hover auf "Chat Widgets" → Data-Sidebar mit Chat-Widget-Liste <br>• `/chat-agents/{id}/develop` → Hover auf "ReACT Agents" (wenn sichtbar) → Data-Sidebar mit ReACT-Agent-Liste |
| 2.2.4 | **Nicht** bei: Conversations (`/conversations`), Chat Agents (`/chat-agents`) — dort keine Data-Sidebar. |
| 2.2.5 | Data-Sidebar ermöglicht schnelles Wechseln zwischen Items desselben Typs ohne Umweg über die Liste. |

### 2.3 Sidebar Active-State für Chat-Widgets

| ID | Anforderung |
|----|-------------|
| 2.3.1 | Sidebar-Item "Chat Widgets" muss in beiden Fällen als aktiv markiert sein: auf `/chat-widgets/{id}` (iFrame-Detail) UND auf `/widget-designer/{id}` (Form-Detail). |
| 2.3.2 | Aktuell ist nur `/widget-designer/{id}` als aktiv markiert → auch `/chat-widgets/{id}` hinzufügen. |

### 2.4 Settings-Icon: Navigation

| ID | Anforderung |
|----|-------------|
| 2.4.1 | Klick auf Settings-Icon in Sidebar navigiert zu `/tenant-settings?tab=iam` (statt nur `/tenant-settings`). |

---

## Paket 3: Main-Search (CommandPalette) Redesign

### 3.1 Erweiterte Suche: Fehlende Entitäten

| ID | Anforderung |
|----|-------------|
| 3.1.1 | **Messages durchsuchen**: Suche soll auch Messages (Nachrichteninhalte) innerhalb von Conversations finden. Gleiches Such-Pattern wie auf der Conversation-Page verwenden. Suchergebnisse zeigen Message-Vorschau + zugehörige Conversation. |
| 3.1.2 | **External Apps durchsuchen**: External Apps in die globale Suche aufnehmen. |
| 3.1.3 | **Chat Widgets durchsuchen**: Nur benutzerdefinierte Chat Widgets suchen (NICHT Standard-Widgets ohne navigierbaren Link). |
| 3.1.4 | **ReACT Agents korrekter Link**: ReACT Agents werden gefunden, aber der Link leitet falsch zu `/chat-agents/{id}` → korrekter Link muss zu `/chat-agents/{id}/develop` führen. |
| 3.1.5 | **Settings-Items durchsuchen**: Folgende Settings-Ressourcen müssen in der globalen Suche auffindbar sein: Principals, Custom Groups, AI Models, Tools, Credentials. Suchergebnis-Klick navigiert zu `/tenant-settings?tab={tab}&selectedId={id}`. **Permissions beachten**: Ergebnisse nur zurückgeben, wenn der anfragende Nutzer die nötige Berechtigung für den jeweiligen Ressourcentyp hat (z.B. Principals nur für User mit IAM-Admin-Rolle). |
| 3.1.6 | **Backend erweitern**: Globale Such-API (`GET /search`) um neue Entitäten erweitern: `messages`, `external_apps`, `chat_widgets`, `principals`, `custom_groups`, `ai_models`, `tools`, `credentials`. **Permissions-Filterung serverseitig**: Jeder Typ wird nur durchsucht/zurückgegeben, wenn der Nutzer die entsprechende Leseberechtigung hat. |

### 3.2 Suchergebnisse: Visuelles Redesign

| ID | Anforderung |
|----|-------------|
| 3.2.1 | **Farbige Kategorie-Badges**: Jede Ergebnis-Kategorie bekommt eine eigene Badge-Farbe. Mapping definieren: Conversations → Blau-Grün, Messages → Blau, Chat Agents → Violett, Workflows → Orange, External Apps → Grün, Chat Widgets → Pink, Settings-Items → Grau. (Finaler Farbvorschlag im Implementierungsplan). |
| 3.2.2 | **Pagination "Mehr laden"**: Wenn mehr Ergebnisse vorhanden als angezeigt → "Mehr laden"-Button am Ende der Ergebnisliste. Nächste Seite nachladen und an bestehende liste anhängen. |
| 3.2.3 | **Hover-Highlighting**: Suchergebnis-Items müssen beim Hover visuell hervorgehoben werden (leichter Background-Change). |

### 3.3 Suchergebnisse: Dual-Action für navigierbare Ressourcen

| ID | Anforderung |
|----|-------------|
| 3.3.1 | Für Ressourcentypen, die sowohl eine **Detail-Page** als auch einen **Edit-Dialog** haben (Chat Agents, Chat Widgets, Workflows): Zwei Buttons nebeneinander im Suchergebnis-Item anzeigen: **"Öffnen"** (navigiert auf Detail-Page) und **"Bearbeiten"** (öffnet Edit-Dialog über Query-Param-Navigation). |
| 3.3.2 | Für alle anderen Ressourcentypen: Standard-Klick navigiert zum Item. |

### 3.4 Commands-Sektion überarbeiten

| ID | Anforderung |
|----|-------------|
| 3.4.1 | **Links korrigieren**: "New Agent" navigiert zu `/chat-agents?dialog=new` (nicht `/chat-agents/new`). Alle Command-Links auf korrekte Routen mit Dialog-Query-Params anpassen. |
| 3.4.2 | **Fehlende Commands ergänzen**: Create Workflow, Create Chat Widget, Create Credential, Create Tool, Create AI Model, Create Custom Group, Add Principal. Jeweils navigiert zu `/{seite}?dialog=new` bzw. `/tenant-settings?tab={tab}&dialog=new`. |
| 3.4.3 | **Permissions beachten**: Commands nur anzeigen, wenn der Nutzer die nötige Rolle/Permission hat (z.B. "Create Agent" nur für Creator/Admin). |
| 3.4.4 | **Navigation-Gruppe entfernen**: Die gesamte "Navigation"-Sektion aus der CommandPalette entfernen. |

### 3.5 Dialog: Styling-Fixes

| ID | Anforderung |
|----|-------------|
| 3.5.1 | **Dark Mode Shadow**: Shadow im Dark Mode entweder dunkler/dezenter oder leichten hellen Glow verwenden, damit Dialog sichtbar abgegrenzt ist. |
| 3.5.2 | **Light Mode Border**: Border im Light Mode besser sichtbar machen (aktuell unsichtbar). |

---

## Paket 4: Dashboard/Home Redesign

### 4.1 Layout & Design

| ID | Anforderung |
|----|-------------|
| 4.1.1 | **Titel fixiert**: Begrüßungstitel oben bleibt sticky. Content-Bereich darunter ist scrollbar. |
| 4.1.2 | **"Erstellen"-Dropdown-Button**: Rechts neben dem Titel ein Button "Erstellen" mit Dropdown-Pfeil. Klick öffnet Dropdown-Menü mit: Chat Agent, Workflow, Chat Widget, External App, Credential, Tool, AI Model, Custom Group, Principal. Auswahl öffnet den jeweiligen Create-Dialog auf der Seite (oder navigiert zu `?dialog=new` Route). |
| 4.1.3 | **Stat-Cards beibehalten**: Bestehende Kacheln (Chat Agents, Workflows, Conversations) bleiben. Route-Mappings aktualisieren auf neue `/workflows`-Route. |
| 4.1.4 | **Recently Visited Gallery**: Unter den Stat-Cards eine horizontal scrollbare Card-Gallery. Navigationsbuttons (links/rechts) zum Scrollen um jeweils ein Item. Backend liefert paginiert mit `limit=25` im ersten Request. Paginierung einbauen (Query-Params `limit` + `offset`/`cursor`), damit bei Bedarf weitere Items nachgeladen werden können. |
| 4.1.5 | **Recently-Visited Card-Design**: Quadratisch bis leicht rechteckig (breiter als hoch). Inhalt: Oben Icon des Ressourcentyps → darunter Name (groß, fett) → darunter Typ-Badge → darunter klein/dezent "vor X Minuten/Stunden/Tagen". Wenn Favorit: Stern-Icon oben rechts (nicht klickbar, nur Anzeige; kein Stern wenn kein Favorit). |
| 4.1.6 | **Links korrigieren**: Alle Links in Dashboard auf korrekte Routen mappen (Workflows auf `/workflows/{id}`, External Apps auf `/external-apps/{id}`, Chat Widgets auf korrekten Pfad etc.). |

### 4.2 Favoriten-Sektion

| ID | Anforderung |
|----|-------------|
| 4.2.1 | Unter der Recently-Visited-Gallery: Favoriten als Wrapped-Card-Liste (wie aktuell). |
| 4.2.2 | "Mehr laden"-Button wenn mehr Favoriten vorhanden als initial angezeigt. |

### 4.3 Scrollbarkeit

| ID | Anforderung |
|----|-------------|
| 4.3.1 | Die gesamte Dashboard-Seite (Content-Bereich) muss scrollbar sein. Aktuell ist die Seite nicht scrollbar → fixen. |

---

## Paket 5: Conversations-Page Überarbeitung

### 5.1 Chat-Vorschläge (Empty State)

| ID | Anforderung |
|----|-------------|
| 5.1.1 | Die Chat-Vorschläge/Suggestions (die man pro Agent definieren kann) sollen **über** dem Input-Wrapper positioniert werden (nicht im separaten Empty-State-Container). |
| 5.1.2 | Suggestion-Badges brauchen angemessenes Padding. |

### 5.2 Conversation-Sidebar: Button-Reihenfolge

| ID | Anforderung |
|----|-------------|
| 5.2.1 | In der Conversation-Sidebar: "New Chat"-Button nach rechts verschieben, "Search"-Button nach links. |

### 5.3 Tracing-Container

| ID | Anforderung |
|----|-------------|
| 5.3.1 | Der Container für Logs/Metadata etc. (Tracing-Hierarchie unten) soll initial doppelt so hoch sein wie aktuell. |
| 5.3.2 | Background-Farbe des unteren Containers angleichen an die Background-Farbe der Tracing-Hierarchie oben (ScrollArea), damit einheitliches Erscheinungsbild. |

---

## Paket 6: Embed-Chat-Page Redesign

### 6.1 Layout/Design

| ID | Anforderung |
|----|-------------|
| 6.1.1 | **Komplettes Redesign der Container/Cards**: Aktuelle Container-Struktur (eintönige abgerundete gleichfarbige Container) ist visuell langweilig. Neues Layout/Design vorschlagen und umsetzen. |
| 6.1.2 | Inhaltlich bleibt alles gleich — nur die visuelle Präsentation der Container und Sections soll moderner und ansprechender werden. |
| 6.1.3 | **Designvorschläge im Implementierungsplan** — mindestens 3 Varianten mit Empfehlung. Mögliche Richtungen: <br>**A)** Flat Sections — Keine Container/Cards, stattdessen flache Sections mit dezenten Divider-Linien und Section-Titeln in Muted-Color. Inputs gruppiert ohne umschließenden Container. Clean, minimalistisch. <br>**B)** Grouped Cards mit Akzent-Header — Jede Section bekommt eine Card mit farbigem Left-Border (2–3px, Primary-Color) oder Top-Accent-Line. Section-Titel prominent mit Icon. Visuell gegliedert, aber nicht überladen. <br>**C)** Sidebar-Detail-Layout — Linke Spalte als schmale Inhaltsübersicht/Navigation, rechts der jeweilige Detail-Content. Gibt komplexen Seiten mehr Struktur. <br>**D)** Accordion-Sections — Aufklappbare Sections, initial geöffnet, können eingeklappt werden. Spart Platz und gibt Nutzer Kontrolle. |

### 6.2 Breadcrumb-Navigation

| ID | Anforderung |
|----|-------------|
| 6.2.1 | In der Breadcrumb "Chat Agents > {Agent Name} > Embed Chat": `{Agent Name}` muss klickbar sein und in den Chat für diesen Agent navigieren (`/conversations?agentId={id}` oder äquivalent). |

### 6.3 Sidebar-Integration

| ID | Anforderung |
|----|-------------|
| 6.3.1 | Auf `/chat-agents/{id}/embed-chat` soll das Sidebar-Item "Chat Agents" als aktiv markiert sein. |
| 6.3.2 | Data-Sidebar: Beim Hover auf "Chat Agents" Sidebar-Item (wenn auf Embed-Chat-Page) soll die Data-Sidebar mit Chat-Agent-Liste angezeigt werden. |

---

## Paket 7: Chat-Agents-Page Überarbeitung

### 7.1 Create-Dialog Anpassungen

| ID | Anforderung |
|----|-------------|
| 7.1.1 | **Type-Reihenfolge ändern**: Neue Reihenfolge im Type-Dropdown: Microsoft Foundry, n8n, REST API, ReACT Agent. |
| 7.1.2 | **"Is Active" Default**: Default-Wert für "Is Active" Toggle auf `true` setzen. |

### 7.2 3-Dot-Menü: "Pin" entfernen

| ID | Anforderung |
|----|-------------|
| 7.2.1 | "Pin"-Option aus dem 3-Dot-Menü der Chat-Agents-Liste entfernen (hat keine Funktion, Favorit ist bereits vorne in der Liste). |

### 7.3 Dialog-Öffnung via Query-Param

| ID | Anforderung |
|----|-------------|
| 7.3.1 | `?dialog=new` öffnet den Create-Chat-Agent-Dialog. |

### 7.4 Duplikat-Funktion

| ID | Anforderung |
|----|-------------|
| 7.4.1 | **Backend**: Neuen Endpoint `POST /chat-agents/{id}/duplicate` erstellen. Erstellt 1:1-Kopie des Agents mit Name + " Copy" (bzw. " Copy(n)" wenn schon existiert). |
| 7.4.2 | **Frontend**: "Duplizieren"-Option im 3-Dot-Menü der Agent-Liste und auf der Detail-Seite. Nach Duplikation: Liste aktualisieren (NICHT auf neuen Agent navigieren). |

---

## Paket 8: Workflows-Page Überarbeitung

### 8.1 3-Dot-Menü: "Pin" entfernen

| ID | Anforderung |
|----|-------------|
| 8.1.1 | "Pin"-Option aus dem 3-Dot-Menü der Workflows-Liste entfernen. |

### 8.2 Dialog-Öffnung via Query-Param

| ID | Anforderung |
|----|-------------|
| 8.2.1 | `?dialog=new` öffnet den Create-Workflow-Dialog. |

### 8.3 Duplikat-Funktion

| ID | Anforderung |
|----|-------------|
| 8.3.1 | **Backend**: Neuen Endpoint `POST /autonomous-agents/{id}/duplicate` erstellen. Logik analog zu Chat-Agent-Duplikation. |
| 8.3.2 | **Frontend**: "Duplizieren"-Option im 3-Dot-Menü und auf Detail-Seite. Nach Duplikation: Liste aktualisieren (NICHT auf neuen Workflow navigieren). |

---

## Paket 9: Workflow-Details-Page Redesign

### 9.1 Details-Tab Redesign

| ID | Anforderung |
|----|-------------|
| 9.1.1 | **Tab `?tab=details`**: Aktuelle Container-Struktur ist visuell langweilig (gleiche eintönige Container wie Embed-Chat). Neues Design/Layout vorschlagen und umsetzen. |
| 9.1.2 | **Designvorschläge im Implementierungsplan** — gleiche Varianten wie Paket 6.1.3 (Flat Sections / Grouped Cards / Sidebar-Detail / Accordion). Konsistentes Design über alle Detail-Pages hinweg — gewählte Variante soll für Embed-Chat, Workflow-Details und Widget-Detail gleichermaßen gelten. |

### 9.2 Dialog-Header: Pattern aus "Integrate Autonomous Agent"

| ID | Anforderung |
|----|-------------|
| 9.2.1 | Das Icon-mit-Hintergrundfarbe-Pattern aus dem "Integrate Autonomous Agent"-Dialog soll als Standard für alle Create- und Edit-Dialoge genutzt werden (→ ist übergreifend in Paket 0.3 abgebildet). |

---

## Paket 10: External-Apps-Page Überarbeitung

### 10.1 Dialog-Öffnung via Query-Param

| ID | Anforderung |
|----|-------------|
| 10.1.1 | `?dialog=new` öffnet den Create-External-App-Dialog. |
| 10.1.2 | `?dialog=edit&selectedId={id}` öffnet den Edit-Dialog für die gewählte External App. |

### 10.2 Tooltips für abgeschnittenen Text

| ID | Anforderung |
|----|-------------|
| 10.2.1 | Cards auf der External-Apps-Seite: Bei Titel und Description, die abgeschnitten werden, Tooltip mit vollem Text anzeigen (wie auf anderen Seiten). |

---

## Paket 11: Chat-Widgets-Page Überarbeitung

### 11.1 3-Dot-Menü: "Pin" entfernen

| ID | Anforderung |
|----|-------------|
| 11.1.1 | "Pin"-Option aus dem 3-Dot-Menü der Chat-Widgets-Liste entfernen. |

### 11.2 Dialog-Öffnung via Query-Param

| ID | Anforderung |
|----|-------------|
| 11.2.1 | `?dialog=new` öffnet den Create-Chat-Widget-Dialog. |
| 11.2.2 | `?dialog=edit&selectedId={id}`, `?dialog=prompt-integration&selectedId={id}` etc. für alle Widget-Dialoge. |

### 11.3 Duplikat-Funktion

| ID | Anforderung |
|----|-------------|
| 11.3.1 | **Backend**: Neuen Endpoint `POST /chat-widgets/{id}/duplicate` erstellen. |
| 11.3.2 | **Frontend**: "Duplizieren"-Option im 3-Dot-Menü. Nach Duplikation: Liste aktualisieren (NICHT auf neues Widget navigieren). |

---

## Paket 12: Chat-Widget-Detail-Page (iFrame-Typ) Redesign

### 12.1 Layout/Design

| ID | Anforderung |
|----|-------------|
| 12.1.1 | Komplettes Redesign der Container-Struktur (gleiche Problematik wie Embed-Chat und Workflow-Details). Gleiche Design-Variante wie bei Paket 6 und 9 anwenden — konsistent über alle Detail-Pages. |

### 12.2 Konfig-Felder bereinigen

| ID | Anforderung |
|----|-------------|
| 12.2.1 | **Frontend**: Felder `width`, `height`, `allowFullScreen` aus der Detail-Page und Formularen entfernen (werden nicht genutzt, da Chat-Window immer dynamisch rendert). |
| 12.2.2 | **Backend**: Entsprechende Felder aus Schema/Modell entfernen oder als deprecated markieren (im Implementierungsplan klären). |

### 12.3 Inline-Name-Edit

| ID | Anforderung |
|----|-------------|
| 12.3.1 | Klick auf den Widget-Namen oben links wandelt den Text in ein editierbares Textfeld um. Bei Enter: Name speichern. Bei Escape/Klick außerhalb: Abbrechen. |

### 12.4 Data-Sidebar Integration

| ID | Anforderung |
|----|-------------|
| 12.4.1 | Auf `/chat-widgets/{id}` Hover auf "Chat Widgets" Sidebar-Item zeigt Data-Sidebar (analog zu `/widget-designer/{id}`). |

---

## Paket 13: Widget-Designer-Page — Minimale Erweiterung

> Widget-Designer-Redesign wird in einem eigenem Zyklus bearbeitet. Hier nur eine kleine funktionale Erweiterung.

### 13.1 3-Dot-Menü: Edit-Details hinzufügen

| ID | Anforderung |
|----|-------------|
| 13.1.1 | Im 3-Dot-Menü des Widget-Designers: Option "Details bearbeiten" hinzufügen → öffnet den Edit-Dialog für das Chat Widget. |

---

## Paket 14: Settings-Page Überarbeitung

### 14.1 Organisation-Tab: Tenant-Tabelle

| ID | Anforderung |
|----|-------------|
| 14.1.1 | Tabelle mit Tenants im Organisation-Tab muss scrollbar sein (Page unten scrollbar). |

### 14.2 Query-Parameter Konsistenz

| ID | Anforderung |
|----|-------------|
| 14.2.1 | **Alle Tabs**: Konsequent Query-Parameter verwenden bei Dialog-Öffnungen: `?tab={tab}&dialog=new`, `?tab={tab}&selectedId={id}`, `?tab={tab}&dialog=edit&selectedId={id}`. |
| 14.2.2 | Bei Navigation auf URL mit Query-Params: automatisch korrekten Tab öffnen und ggf. Dialog mit selektiertem Item anzeigen. |

### 14.3 Dialog-Header Konsistenz

| ID | Anforderung |
|----|-------------|
| 14.3.1 | Alle Create/Edit-Dialoge innerhalb der Settings (z.B. Custom Groups, Credentials, Tools) auf die einheitliche Dialog-Struktur (Paket 0.3) migrieren. Beispiel: "Create Custom Group"-Dialog hat aktuell kein Icon im Header → mit einheitlichem Header versehen. |

---

## Zusammenfassung: Backend-Anforderungen (plattform-service)

> Gesammelte Backend-Änderungen über alle Pakete hinweg.

| ID | Paket-Ref | Backend-Anforderung |
|----|-----------|---------------------|
| BE-1 | 3.1.6 | Globale Such-API erweitern: Messages, External Apps, Chat Widgets (nur custom), Settings-Items (Principals, Custom Groups, AI Models, Tools, Credentials) als durchsuchbare Typen hinzufügen. **Permissions-Filterung serverseitig** pro Typ. |
| BE-6 | 4.1.4 | Recent-Visits-Endpoint: Paginierung einbauen (`limit` + `offset`/`cursor` Query-Params). Default `limit=25`. |
| BE-2 | 7.4.1 | `POST /chat-agents/{id}/duplicate` — Agent 1:1 kopieren, Name + " Copy" / " Copy(n)". |
| BE-3 | 8.3.1 | `POST /autonomous-agents/{id}/duplicate` — Workflow 1:1 kopieren. |
| BE-4 | 11.3.1 | `POST /chat-widgets/{id}/duplicate` — Widget 1:1 kopieren. |
| BE-5 | 12.2.2 | iFrame-Widget: `width`, `height`, `allowFullScreen` Felder klären (entfernen oder deprecated). |

---

## Implementierungsreihenfolge (empfohlen)

1. **Paket 0** — Voraussetzungen (Basis für alles)
2. **Paket 1** — Styling/Dark Mode (globale visuelle Basis)
3. **Paket 2** — Sidebar (Navigation-Grundlage)
4. **Paket 3** — Main Search (nutzt Query-Param-Konvention + Styling)
5. **Paket 4** — Dashboard/Home (nutzt neue Routen + Dialoge)
6. **Paket 5** — Conversations Page
7. **Paket 6** — Embed Chat Page
8. **Paket 7** — Chat Agents Page (nutzt Duplikat-Backend)
9. **Paket 8** — Workflows Page
10. **Paket 9** — Workflow Details
11. **Paket 10** — External Apps Page
12. **Paket 11** — Chat Widgets Page
13. **Paket 12** — Chat Widget Detail (iFrame)
14. **Paket 13** — Widget Designer (nur 3-Dot-Menü-Erweiterung)
15. **Paket 14** — Settings Page