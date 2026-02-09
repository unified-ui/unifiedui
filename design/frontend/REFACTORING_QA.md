# UI Refactoring — Rückfragen & Klärungen

> **Zweck**: Ich beantworte die Fragen, Copilot nutzt die Antworten für das finale Anforderungsdokument.
> **Format**: Frage → Antwort (von mir auszufüllen)

---

## 1. Notifications System

### 1.1 Welche Events erzeugen Notifications?

Beispiele — bitte ankreuzen/ergänzen:

- [x] Agent-Fehler (Agent-Run failed / Error Rate hoch)
- [x] Credential abgelaufen / ungültig
- [ ] Neuer User wurde zum Tenant hinzugefügt (IAM)
- [ ] Permission-Änderungen (Rolle geändert)
- [ ] Conversation abgeschlossen (async Agent fertig)
- [ ] System-Announcements (Wartung, neue Features)
- [x] Autonomous Agent trace importiert
- [ ] Andere: ___

### 1.2 Notification-Delivery: Wie sollen Notifications ankommen?

- [x] **Polling** (Frontend pollt alle X Sekunden) — einfacher – alle 60s
- [ ] **SSE** (Server-Sent Events, real-time Push) — bereits für Chat genutzt
- [ ] **WebSocket** (Bidirektional) — Overkill für Notifications?
- [ ] Erstmal nur Polling, später SSE

### 1.3 Notification-Center: Wie umfangreich?

- [ ] **Minimal**: Dropdown im Header mit Liste + "Mark all as read"
- [x] **Mittel**: Eigene Sidebar/Panel (wie GitHub Notifications)
    - hier öffnen, einzeln bestätigen oder oben alle gemeinsam als gelesen markieren
- [ ] **Voll**: Eigene Page + Filter (Read/Unread, Type-Filter) + Settings (welche Notifications will ich?)

### 1.4 E-Mail-Notifications?

- [x] Nein, nur In-App
- [ ] Ja, für kritische Events (Agent-Fehler)
- [ ] Later (v0.3.0+)

---

## 2. Search / Command Palette

### 2.1 Was soll durchsuchbar sein?

- [x] Applications (Name, Description, Tags)
- [x] Autonomous Agents (Name, Description, Tags)
- [x] Conversations (Title, Messages)
- [x] Credentials (Name, type)
- [x] Settings-Entities (Groups, AI Models, Tools)
- [ ] Traces (Trace-Titel, Status)
- [ ] Andere: ___

### 2.2 Suchlogik: Wo wird gesucht?

- [ ] **Frontend-Filter** (nur aktuell geladene Daten filtern)
- [x] **Backend-API** (dedizierter `/search`-Endpoint, Full-Text over DB)
- [ ] **Hybrid** (Quick-Search lokal, Deep-Search via API)

### 2.3 Search Bar im Header — was passiert dort?

Mein Vorschlag: Search-Bar im Header funktioniert als Quick-Search über Entities. `⌘K` öffnet die Command Palette (Suche + Commands + Navigation). Beide teilen das gleiche Suchbackend.

- [x] Ja, genau so
- [ ] Nein, anders: ___

---

## 3. Dashboard

### 3.1 Welche Stats/KPIs sind wichtig?

- [x] Anzahl Applications (aktiv / inaktiv)
- [x] Anzahl Autonomous Agents (aktiv / inaktiv)
- [x] Anzahl Conversations (letzte 7/30 Tage)
- [x] Anzahl Traces / Error-Rate
- [ ] Token-Verbrauch (falls tracked)
- [x] Letzte Aktivitäten (Activity Feed)
- [ ] Andere: ___

### 3.2 Mini-Sparklines (7-Tage-Trend in Stats-Cards)?

- [ ] Ja, gute Idee — implementieren
- [x] Nein, zu aufwändig für v0.1.0
- [ ] Later (v0.2.0+)

### 3.3 Activity Feed — welche Events?

- [ ] Entity erstellt/gelöscht/geändert
- [ ] Conversations (neue Nachricht, Agent-Antwort)
- [ ] Agent-Runs (Erfolg/Fehler)
- [ ] IAM-Änderungen (User hinzugefügt/entfernt)
- [ ] Andere: ___
=> brauchen wir nicht

(Hinweis: Activity Feed braucht ein Backend-Event-Log. Existiert das bereits oder muss es gebaut werden?)

---

## 4. Conversations Page — Scope

### 4.1 File Upload

- [x] Welche Dateitypen? (Bilder, PDFs, txt, markdown, word, excel, etc)
- [x] Wo wird gespeichert? (Azure Blob Storage? S3? Lokal?) => gar nicht; wir leiten die Dateien direkt an die Agent-Tools weiter, ohne sie zu speichern -> das muss definitiv noch implementiert werden => schaue dir dazu die implementierung in N8N UND auch für die !NEUE! Micrsoft Foundry (new); nicht die classic Azure AI Foundry!!! Die neue **Microsoft Foundry**
- [x] Max Dateigröße? => sollen die agent tools entscheiden, wir geben einfach weiter, die sollen alles weitere handlen
- [ ] Sollen Dateien in der Chat-History angezeigt werden? (Preview für Bilder, Download-Link für andere)
    - nein. ich würde nur gerne die symbole als typen im ersten schritt anzeigen. also irgendwie bei metadaten spechern was und wie viele dateien wurden an der nachricht mitgesendet

### 4.2 Message-Features

- [x] **Message Edit**: User kann eigene Nachrichten bearbeiten → neuer API Call → Agent antwortet neu?
    - ja, aber nur für die letzte user nachricht, und ja, das soll einen neuen agent-run triggern, also quasi eine "retry" funktion sein
- [x] **Message Delete**: User kann eigene Nachrichten löschen?
    - ja gerne
- [x] **Message Retry**: Bei Fehler: Letzte User-Nachricht erneut senden?
    - einemal neu versuchen (aber auch anzeigen) und dann den error ausgeben (bei erneutem error);
- [x] **Message Copy**: Einzelne Nachricht in Clipboard kopieren?
    - ja, ist schon drin. soll für beide gehen
- [x] **Message Reaction** (👍👎): Feedback für AI-Antworten (für Finetuning)?
    - ja bitte führe das ein. man soll auch noch text-feadback geben; hierfür neue colllection und message id mit angeben
- [x] **Code-Block Copy**: Copy-Button in gerenderten Code-Blocks?

### 4.3 Conversation-Export

- [x] Markdown Export
- [x] PDF Export
- [x] JSON Export (Raw Messages)
- [ ] Kein Export nötig

### 4.4 Voice Input

- [ ] In-Scope für v0.1.0
- [ ] Later (v0.2.0+)
- [x] Nicht geplant

---

## 5. Pages — Scope Klärung

### 5.1 Traces Page (aktuell "Coming Soon")

- [ ] **Implementieren**: Standalone Trace-Browser mit Suche, Filter, Visualisierung
- [ ] **Placeholder lassen**: Traces nur über Conversation-Detail erreichbar
- [ ] **Minimal**: Liste aller Traces mit Link zur Visualisierung, kein eigenes Filtering

=> traces page kann erstmal entfernt werden!

### 5.2 Widget Designer Page (aktuell "Coming Soon")

- [x] **Implementieren**: Visual Editor für Chat-Widget Konfiguration + Live-Preview
    - hier standard felder für wichtigsten datentypen verfügbar machen (text, single-select, true/false toggle, multi-select, label, text-area, text-area für bescheibung, file)
    - Felder erstmal simpel per drag und drop übereinander stapelbar machen, ohne komplexe layout-optionen (spalten, grids, etc)
- [ ] **Placeholder lassen**: Für spätere Version
- [ ] **Minimal**: Nur Config-Formular, kein Visual Editor

### 5.3 ReACT Agent Developer Page

- [ ] Existiert diese Page? Was ist der Plan dafür?
- [ ] Placeholder lassen für v0.1.0?

Antwort:
- existiert nicht, will ich aber
- ich will ein ähnlcihes Design wie im neuen Copilot Studio:
    - Rechts Chat Fenster für playground (moderne chat featrue -> einfach wie im conversation page -> selbes component nur component muss parameterisierbar sein, damit man im playground bisschen anpassen kann; zudem soll chat fenster auch wie mit iframe einbindbar sein; dafür benötigen wir nen konzept)
        - playground chat wird nicht persistiert
    - Links konfig:
        - Tools:
            - wir haben bereits entsprechende tools in unified-ui, die wir auch in der ReACT Agent Developer Page verfügbar machen können. hier für den agent registrieren können bzw. auch neue über den dialog hinzufügbar machen können (ohne auf settings page zu navigieren)
            - sind openAPI oder mcp tools -> also beschreibung der tools haben wir automatisch
        - AI models
            - hier 1 oder mehrere models auswählbar machen und wie bei tools auch direkt hier hinzufügen können
                - hier muss man neue purpose group "ReACT Agent" erstellen und nur diese sind hier verwendbar
        - instrcutions -> system instructions -> max 8000 zeichen
        - prompt templates für security instructions, tool use instructions, response formatting instructions
        - erstmal nur im frontend den designer (also tools, ai models, etc)

---

## 6. Testing & Workflow

### 6.1 Frontend Test-Framework

Mein Vorschlag: **Vitest** + **React Testing Library** + **MSW** (Mock Service Worker für API-Mocking)

- [x] Ja, genau so
- [ ] Anderes Framework: ___

### 6.2 Test-Coverage-Ziel

- [x] 80%+ für Handler/Hooks
- [x] 65%+ für Components
- [ ] Nur kritische Paths testen
- [ ] Andere: ___

### 6.3 E2E-Tests?

- [ ] Ja, mit Playwright/Cypress
- [x] Nein, nur Unit + Integration Tests
- [ ] Later

---

## 7. Allgemeine Entscheidungen

### 7.1 i18n (Internationalisierung)

- [ ] **Nur Englisch**: Alle deutschen Strings durch englische ersetzen, kein i18n-Framework
- [x] **i18n-Framework jetzt**: react-i18next einführen, Strings in JSON-Dateien
- [ ] **i18n-ready**: Englisch + Codestruktur vorbereiten für späteres i18n, aber kein Framework jetzt

- ja bitte mehrsprachig designen; default englisch und mit in den pfad aufnehmen: en-us etc; wenn ncit da, einfach en-us als default

### 7.2 Mobile / Responsive

- [ ] **Must Work**: Alles muss responsive sein (Mobile-First)
- [x] **Desktop Focus**: Desktop optimiert, Mobile "bricht nicht" aber nicht optimiert
- [ ] **Desktop Only**: Kein Mobile-Support geplant

### 7.3 Keyboard Shortcuts — Scope

Mein Vorschlag für v0.1.0:
- `⌘K` / `Ctrl+K` → Command Palette
- `N` → New Entity (kontextabhängig)
- `/` → Focus Search
- `Esc` → Close Dialog / Deselect
- `⌘,` → Settings

- [x] Ja, diese Shortcuts
- [ ] Mehr: ___
- [ ] Weniger / Later

### 7.4 Accessibility (a11y)

- [ ] **Basis**: aria-labels, focus-management, keyboard-navigation
- [x] **Voll**: WCAG 2.1 AA Compliance
- [ ] **Minimal**: Erstmal nur Focus-States + Esc-to-Close
- [ ] Later

### 7.5 Entity Avatare (farbige Initialen)

- [x] Ja, implementieren (Hash-basierte Farbe aus Entity-Name)
- [ ] Nein, Icons reichen
- [ ] Later

### 7.6 Multi-Select / Bulk Actions in DataTable

- [x] Ja, für v0.1.0 (Delete, Tag, Status-Toggle)
- [ ] Later (v0.2.0+)
- [ ] Nicht geplant

### 7.7 Breadcrumb Navigation

- [x] Ja, auf Detail-Pages (`Agents > Invoice Agent > Traces`)
- [ ] Nein, nicht nötig
- [ ] Later

### 7.8 Onboarding / Tour

- [ ] Ja, für v0.1.0
- [ ] Later (v0.2.0+)
- [x] Nicht geplant

---

## 8. Backend-Fragen

### 8.1 Notifications — Backend-Tabelle

Hier muss ein neues DB-Modell + API her. Mein Vorschlag:

```
notifications Table:
  id, tenant_id, user_id (nullable = broadcast), 
  type (enum: agent_error, iam_change, system, ...),
  title, message, resource_type, resource_id,
  is_read (boolean), created_at

API:
  GET    /v1/tenants/{id}/notifications?is_read=false&limit=20
  PUT    /v1/tenants/{id}/notifications/{nid}/read
  PUT    /v1/tenants/{id}/notifications/read-all
  DELETE /v1/tenants/{id}/notifications/{nid}
```

- [x] Ja, dieses Modell passt
- [ ] Anpassungen: ___

### 8.2 Global Search — Backend-Endpoint

```
GET /v1/tenants/{id}/search?q=invoice&types=application,agent&limit=10
→ Returns: [{ type: "application", id: "...", name: "...", match_field: "name" }, ...]
```

- [x] Ja, so einen Endpoint brauchen wir
- [ ] Frontend-only Search reicht erstmal
- [ ] Anderer Ansatz: ___

### 8.3 Activity Feed / Event Log

Braucht ein Event-Log-System im Backend. Existiert das schon?

- [ ] Ja, existiert bereits als ___
- [ ] Nein, muss gebaut werden
- [x] Activity Feed ist nicht nötig

### 8.4 Last Visited — Wo speichern?

- [ ] **localStorage** (Frontend-only, geht bei Browser-Wechsel verloren)
- [ ] **Backend** (neuer Endpoint, survives across devices)
- [x] **localStorage + Backend-Sync** (best of both, mehr Aufwand)

---

## 9. Priorisierung & Reihenfolge

### 9.1 Deine Top-5 Prioritäten für die erste Session?

Mein Vorschlag für die Reihenfolge:

**Phase 1 — Foundation (Aufräumen)**
1. Fake-UI entfernen + Sprache vereinheitlichen
2. Error-Handling verbessern
3. TODO-Stubs aufräumen

**Phase 2 — Layout Refactoring**
4. Full-Width Layout
5. Header/Sidebar Redesign
6. Settings Sidebar-Navigation
7. TenantSettingsPage aufbrechen
8. List-Page Deduplication (useEntityList Hook)

**Phase 3 — Core Features**
9. Search Implementation (Backend + Frontend)
10. Notifications (Backend + Frontend)
11. Favorites/Pins anbinden
12. Last Visited
13. Dashboard Redesign

**Phase 4 — Conversations Overhaul**
14. ConversationsPage Refactoring + alle Chat-Features

**Phase 5 — Polish**
15. Command Palette
16. Skeleton Loading
17. Empty States
18. Optimistic Updates
19. Keyboard Shortcuts
20. Entity Avatare

- [x] Ja, diese Reihenfolge ist gut
- [ ] Andere Reihenfolge: ___

---

**Bitte fülle die Checkboxen aus und ergänze Freitext wo nötig. Ich erstelle dann das finale konsolidierte Anforderungsdokument.**
