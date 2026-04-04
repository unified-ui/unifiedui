# 002 — Container-Card Redesign & UX-Verbesserungen v0.2.1

> **Status:** DRAFT  
> **Scope:** unified-ui-frontend-service  
> **Ziel:** Standardisiertes Container-Card Design für Detail-Pages + UX-Verbesserungen

---

## Arbeitsweise & Prozess

> Gleicher Ablauf wie in `001_REDESIGN_v020.REQ.md` — siehe dort für Details.

### Status-Tracking

- *(kein Marker)* → Noch nicht begonnen
- `⏳ In Progress` → Gerade in Bearbeitung
- `✅ Done` → Fertig implementiert und abgenommen

---

## Paket 0: Container-Card Design-System

> Wiederverwendbare Komponente und CSS-Variablen für konsistente Detail-Page-Container.

### 0.1 Analyse: Ist-Zustand

| ID | Anforderung |
|----|-------------|
| 0.1.1 | **Code-Review**: Aktuelle Container-Styles auf `/workflows/{id}?tab=details` und `/chat-agents/{id}/embed-chat` analysieren. Dokumentieren, welche CSS-Klassen/Komponenten verwendet werden. |
| 0.1.2 | **Problem-Identifikation**: Container haben keinen Background, keinen Shadow, nur Border. Wirkt flach und langweilig. |

### 0.2 Container-Card Komponente

| ID | Anforderung |
|----|-------------|
| 0.2.1 | **Neue Komponente `ContentCard`** erstellen (oder bestehende erweitern): Wiederverwendbare Card für Content-Sections auf Detail-Pages. |
| 0.2.2 | **Props**: `title` (string), `icon` (TablerIcon), `children`, `collapsible` (boolean, optional), `defaultExpanded` (boolean, optional), `headerAction` (ReactNode, optional für Buttons rechts im Header). |
| 0.2.3 | **Design-Elemente**: <br>• Background: `var(--color-bg-elevated)` <br>• Border: Subtil (`var(--color-border-subtle)`) <br>• Border-Radius: `var(--radius-md)` <br>• Shadow: Dezent im Light-Mode, keiner/minimal im Dark-Mode <br>• Header: Icon + Titel linksbündig, optional Action-Button rechtsbündig <br>• Padding: Konsistent (`var(--spacing-md)` oder `var(--spacing-lg)`) |
| 0.2.4 | **Header-Style**: Icon in farbigem Container (wie bei Dialog-Icons), Titel als `Text` mit `fw={600}`. Visuell abgesetzt vom Content-Bereich (z.B. durch Border-Bottom oder Background-Unterschied). |
| 0.2.5 | **Collapsible-Variante**: Wenn `collapsible={true}`, Chevron-Icon im Header. Klick auf Header klappt Content ein/aus. Smooth Animation. |

### 0.3 CSS-Variablen ergänzen

| ID | Anforderung |
|----|-------------|
| 0.3.1 | Falls nicht vorhanden: CSS-Variablen für Card-Backgrounds, Elevations und Borders in `variables.css` ergänzen. Light/Dark-Mode-Werte definieren. |
| 0.3.2 | Beispiel: `--color-bg-card`, `--color-bg-card-header`, `--shadow-card`, `--shadow-card-dark`. |

---

## Paket 1: Workflow Details Redesign

> `/workflows/{id}?tab=details` — Neues Container-Design anwenden.

### 1.1 Aktuelle Struktur analysieren

| ID | Anforderung |
|----|-------------|
| 1.1.1 | **Betroffene Datei(en)**: `WorkflowDetailsTab.tsx` oder äquivalent identifizieren. |
| 1.1.2 | **Sections identifizieren**: Welche logischen Sections gibt es? (z.B. General Info, Configuration, Integration Details, etc.) |

### 1.2 Redesign umsetzen

| ID | Anforderung |
|----|-------------|
| 1.2.1 | Alle Content-Sections auf `ContentCard`-Komponente migrieren. |
| 1.2.2 | Jede Section bekommt passendes Icon im Header (aus Icon-Mapping in 001_REDESIGN). |
| 1.2.3 | Spacing zwischen Cards: `var(--spacing-lg)` oder `var(--spacing-xl)`. |
| 1.2.4 | Kein verschachteltes Card-in-Card — flache Hierarchie. |

---

## Paket 2: Embed Chat Redesign

> `/chat-agents/{id}/embed-chat` — Gleiches Design-Pattern wie Workflow Details.

### 2.1 Aktuelle Struktur analysieren

| ID | Anforderung |
|----|-------------|
| 2.1.1 | **Betroffene Datei(en)**: `EmbedChatPage.tsx` oder äquivalent identifizieren. |
| 2.1.2 | **Sections identifizieren**: Welche logischen Sections gibt es? (z.B. Embed Code, Customization Options, Preview, etc.) |

### 2.2 Redesign umsetzen

| ID | Anforderung |
|----|-------------|
| 2.2.1 | Alle Content-Sections auf `ContentCard`-Komponente migrieren. |
| 2.2.2 | Konsistentes Design mit Workflow Details — gleiche Abstände, gleiche Header-Styles. |
| 2.2.3 | Jede Section bekommt passendes Icon im Header. |

---

## Paket 3: Home — Favoriten 2-Zeilen Responsive

> Favoriten-Sektion auf `/home` dynamisch responsive anpassen.

### 3.1 Anforderungen

| ID | Anforderung |
|----|-------------|
| 3.1.1 | **Immer 2 Zeilen**: Die Favoriten-Sektion zeigt immer exakt 2 Zeilen an (außer "Show All" ist aktiv). |
| 3.1.2 | **Responsive zur Laufzeit**: Bei Änderung der Bildschirmbreite (Resize) wird die Anzahl der Items pro Zeile dynamisch angepasst. Mehr Platz = mehr Items pro Zeile. Weniger Platz = weniger Items pro Zeile. |
| 3.1.3 | **Berechnung**: Anzahl sichtbarer Items = `itemsPerRow * 2`. `itemsPerRow` wird aus Container-Breite und Item-Breite berechnet (inkl. Gap). |
| 3.1.4 | **"Show All X"**: Button zeigt Anzahl der nicht sichtbaren Items. Wenn alle sichtbar → Button ausblenden. |
| 3.1.5 | **Show All aktiv**: Wenn User "Show All" klickt → alle Favoriten in beliebig vielen Zeilen anzeigen. Button wird zu "Show Less". |
| 3.1.6 | **Lokale Daten**: Alle Favoriten sind bereits lokal geladen. Kein API-Call bei Resize — nur lokales Slicing der angezeigten Items. |

### 3.2 Implementierung

| ID | Anforderung |
|----|-------------|
| 3.2.1 | **ResizeObserver oder `useElementSize`**: Container-Breite tracken. Bei Änderung `itemsPerRow` neu berechnen. |
| 3.2.2 | **Item-Breite**: Feste Mindestbreite pro Favoriten-Card (z.B. `180px`). Gap zwischen Items (z.B. `16px`). |
| 3.2.3 | **State**: `showAll: boolean` — Toggle zwischen 2-Zeilen-Ansicht und Alle-Ansicht. |
| 3.2.4 | **Performance**: `useMemo` für berechnete `visibleItems` basierend auf `itemsPerRow` und `showAll`. |

---

## Paket 4: API-Calls Review (Research)

> Audit der Frontend-API-Calls pro Seite — Optimierungspotential identifizieren.

### 4.1 Scope

| ID | Anforderung |
|----|-------------|
| 4.1.1 | **Pro Seite dokumentieren**: Welche API-Calls werden beim initialen Laden ausgelöst? |
| 4.1.2 | **Seiten**: Home, Conversations, Chat Agents, Workflows, External Apps, Chat Widgets, Settings (alle Tabs), Detail-Pages (je Typ). |

### 4.2 Analyse-Kriterien

| ID | Anforderung |
|----|-------------|
| 4.2.1 | **Redundante Calls**: Werden dieselben Daten mehrfach geladen? (z.B. User-Info, Tenant-Info, Favorites) |
| 4.2.2 | **Unnötige Calls**: Calls die für die Seite nicht benötigt werden oder deren Daten bereits im Context vorhanden sind. |
| 4.2.3 | **Zusammenlegung möglich**: Mehrere kleine Calls die zu einem gebündelt werden könnten. |
| 4.2.4 | **Permissions-bedingte Calls**: Calls die bei fehlender Berechtigung fehlschlagen — werden diese vorab geprüft? |

### 4.3 Output

| ID | Anforderung |
|----|-------------|
| 4.3.1 | **Tabelle erstellen**: Seite → API-Calls → Trigger (Mount/Action) → Bereits optimiert? → Optimierungspotential |
| 4.3.2 | **Empfehlungen**: Konkrete Vorschläge für Zusammenlegung oder Vermeidung von Calls. |
| 4.3.3 | **Keine Implementierung**: Dieses Paket ist nur Research/Audit. Implementierung erfolgt ggf. in separatem Ticket. |

---

## Zusammenfassung

| Paket | Beschreibung | Typ |
|-------|--------------|-----|
| 0 | Container-Card Design-System | Design-System |
| 1 | Workflow Details Redesign | UI-Redesign |
| 2 | Embed Chat Redesign | UI-Redesign |
| 3 | Home Favoriten 2-Zeilen Responsive | UX-Feature |
| 4 | API-Calls Review | Research/Audit |

---

## Implementierungsreihenfolge

1. **Paket 0** — Design-System (Basis für Paket 1 + 2)
2. **Paket 1** — Workflow Details (erstes Redesign)
3. **Paket 2** — Embed Chat (konsistentes Design)
4. **Paket 3** — Home Favoriten Responsive
5. **Paket 4** — API-Calls Review (kann parallel laufen)
