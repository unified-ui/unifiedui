# unified-ui Frontend — Refactoring Requirements v1.0

> **Status**: Approved  
> **Erstellt**: 08. Februar 2026  
> **Quellen**: UI_REFACTORING_CONCEPT.md, REFACTORING_QA.md (User-bestätigt)  
> **Workflow**: Test-Driven · API-First (Backend → Frontend)  
> **Sprache**: Englisch (i18n via react-i18next, default `en-US`)

---

## Inhaltsverzeichnis

1. [Grundregeln & Workflow](#1-grundregeln--workflow)
2. [Phase 1 — Foundation (Aufräumen)](#2-phase-1--foundation)
3. [Phase 2 — Layout Refactoring](#3-phase-2--layout-refactoring)
4. [Phase 3 — Core Features](#4-phase-3--core-features)
5. [Phase 4 — Conversations Overhaul](#5-phase-4--conversations-overhaul)
6. [Phase 5 — Polish](#6-phase-5--polish)
7. [Datenmodell-Änderungen (Backend)](#7-datenmodell-änderungen-backend)
8. [Neue API-Endpoints](#8-neue-api-endpoints)
9. [Widget Designer & ReACT Agent Developer](#9-widget-designer--react-agent-developer)
10. [Cross-Cutting Concerns](#10-cross-cutting-concerns)

---

## 1. Grundregeln & Workflow

### 1.1 Development Workflow

```
Für jedes Feature:
  1. Backend: Datenmodell + Migration + API-Endpoint + Tests
  2. Frontend: TypeScript Types + API-Client-Methoden
  3. Frontend: Hook/Context + Unit-Tests (Vitest + RTL + MSW)
  4. Frontend: Component + Tests
  5. Integration-Test
```

**Implementation Cycle** (pro Section/Feature):

```
1. Implementieren
2. Tests schreiben + ausführen
3. Failing Tests fixen
4. Bei grünen Tests: Code-Review der eigenen Implementierung
5. Unschlüssigkeiten / Inkonsistenzen → Refactoring
6. Zurück zu Schritt 2 (bis stabil)
```

**Nach Abschluss jedes Service** (platform-service, agent-service, frontend-service):
- `copilot-instructions.md` und alle zugehörigen Instruction-Dateien aktualisieren
- Neue Patterns, Entities, Conventions dokumentieren
- Veraltete Informationen entfernen

### 1.2 Test-Stack

| Layer | Tool | Coverage-Ziel |
|-------|------|---------------|
| Frontend Hooks/Handlers | Vitest + React Testing Library | 80%+ |
| Frontend Components | Vitest + RTL | 65%+ |
| API Mocking | MSW (Mock Service Worker) | — |
| Backend (Platform) | pytest -n auto | 80%+ (existing) |
| Backend (Agent) | go test | 80%+ (existing) |
| E2E | Nicht geplant | — |

### 1.3 i18n

- Framework: `react-i18next`
- Default Locale: `en-US`
- Struktur: `src/i18n/locales/{locale}/` mit JSON-Dateien pro Namespace
- URL-Pfad: Locale im Pfad (`/en-us/dashboard`, `/de-de/dashboard`) mit Fallback `en-US`
- Alle deutschen Strings werden zu englischen Keys migriert
- Namespaces: `common`, `dashboard`, `conversations`, `settings`, `notifications`, etc.

### 1.4 Accessibility

- Standard: WCAG 2.1 AA Compliance
- Alle interaktiven Elemente: `aria-label`, `role`, `tabIndex`
- Focus-Management: Focus-Trap in Modals, Roving Tabindex in Listen
- Keyboard-Navigation: alle Features per Keyboard erreichbar
- Color Contrast: AA-konform für Text und UI-Elemente

### 1.5 Responsive Strategy

- **Desktop-Focus**: Optimiert für ≥1024px
- **Tablet** (≥768px): Sidebar collapsed (nur Icons), Content full-width
- **Mobile** (<768px): Sidebar als Hamburger-Menu, Content full-width, kein Hard-Break

---

## 2. Phase 1 — Foundation

### 2.1 Fake-UI entfernen

| Element | Aktuell | Aktion |
|---------|---------|--------|
| Header Search Bar | Non-functional (kein onChange) | Funktional machen (→ Phase 3 Search) oder disabled + Tooltip "Coming soon" |
| Notification Badge | Hardcoded "2" | Badge entfernen bis echte Notifications existieren (→ Phase 3) |
| User Menu: "Manage Account" | Kein onClick | Entfernen |
| User Menu: "Manage Tenant" | Kein onClick | Entfernen |
| User Menu: "Manage Licence" | Kein onClick | Entfernen |

### 2.2 Sprache vereinheitlichen → Englisch

Alle deutschen Strings ersetzen. Betroffene Dateien:

| Datei | Deutsche Strings |
|-------|-----------------|
| DashboardPage | "Willkommen zurück", "Lade Dashboard...", "Benutzer", "Aktueller Tenant", "Verfügbare Tenants" |
| LoginPage | "Willkommen", "Melde dich an...", "Mit Microsoft anmelden", Feature-Texte |
| Header | "Kein Tenant", "Keine Tenants verfügbar", "Tenant auswählen" |
| EditCredentialDialog | "Neuer API Key", "Leer lassen um den aktuellen Wert beizubehalten" |
| SidebarDataList | "Suchen..." |
| IdentityContext | "Fehler", "Erfolg" |
| SidebarDataContext | "Fehler beim Laden der Chat Agents" |

**Gleichzeitig**: react-i18next Setup einführen, alle neuen Strings sofort als i18n-Keys anlegen.

### 2.3 Error-Handling verbessern

**Regel**: Jeder fehlgeschlagene API-Call muss dem User visuelles Feedback geben.

| Muster | Aktion |
|--------|--------|
| Leere `catch {}` Blöcke | Mantine `notifications.show({ color: 'red', ... })` |
| `console.error()` only | Zusätzlich User-Toast |
| Delete-Fehler | Dialog schließen + Error-Toast: "Failed to delete. Please try again." |
| Create-Fehler | Error inline im Dialog (Alert über Submit-Button) |
| Netzwerk-Fehler | Global Error-Boundary / Toast "Network error. Check your connection." |

### 2.4 TODO-Stubs aufräumen

Klickbare Menu-Items die `console.log()` ausführen — entweder implementieren oder entfernen:

| Page | Menu-Item | Aktion |
|------|-----------|--------|
| ChatAgentsPage | Duplicate | Implementieren oder entfernen |
| AutonomousAgentsPage | Share | Entfernen (kein Share-Konzept) |
| AutonomousAgentsPage | Duplicate | Implementieren oder entfernen |
| AutonomousAgentsPage | Pin | Implementieren (→ Favorites, Phase 3) |
| ChatWidgetsPage | Share | Entfernen |
| ChatWidgetsPage | Duplicate | Implementieren oder entfernen |

**Regel für DataTableRow Menu-Items**: Nur rendern wenn ein funktionierender Handler übergeben wird:
```tsx
{onDuplicate && <Menu.Item onClick={() => onDuplicate(item.id)}>Duplicate</Menu.Item>}
```

---

## 3. Phase 2 — Layout Refactoring

### 3.1 Full-Width Layout

| Änderung | Vorher | Nachher |
|----------|--------|---------|
| Header-Höhe | 70px | 56px |
| Sidebar-Breite | 100px | 80px |
| Content-Layout | `PageContainer` (max-width 1200px, centered) | Full-width, `padding: 24px 32px` |
| Content-Area Berechnung | `margin-top: 70px; margin-left: 100px` | `margin-top: 56px; margin-left: 80px` |

**`PageContainer` Komponente entfernen.** Alle Pages erhalten stattdessen ein einfaches `pageContent` CSS-Klassen-Pattern:

```css
.pageContent {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
```

**Betroffene Pages**: ChatAgentsPage, AutonomousAgentsPage, AutonomousAgentDetailsPage, TenantSettingsPage, ChatWidgetsPage, TracesPage (wird entfernt → 3.6).

### 3.2 Header Redesign

```
┌─────────────────────────────────────────────────────────────────┐
│ 🔷 unified-ui       🔍 [Search...]              🔔  🌙  👤    │
└─────────────────────────────────────────────────────────────────┘
                        56px Höhe
```

- Höhe: 56px
- Search-Bar: funktional (Quick-Search über Entities, → Phase 3)
- Notification-Bell: Badge nur bei echten ungelesenen Notifications
- User-Menu: Nur funktionierende Items (Tenant Switch, Theme Toggle, Logout)
- Tenant-Switching: Ohne `window.location.reload()` — Context-Update + Data-Invalidation

### 3.3 Sidebar Redesign

- Breite: 80px
- Kürzere Labels (1 Zeile): Home, Chats, Agents, Auto, ReACT, Widg., Set.
- Icons: Outline default, Filled bei aktiv
- Sidebar-DataList Hover: bestehende expand-on-hover Logik beibehalten
- Responsive: 56px (nur Icons) ≥768px, Hamburger <768px

### 3.4 Settings Page → Sidebar-Navigation

**TenantSettingsPage 2001 Zeilen aufbrechen in:**

```
TenantSettingsPage/
├── TenantSettingsPage.tsx           (~80 Zeilen — Shell mit SettingsSidebar)
├── GeneralSettingsTab.tsx           (~200 Zeilen)
├── IAMSettingsTab.tsx               (~300 Zeilen)
├── CustomGroupsTab.tsx              (~250 Zeilen)
├── CredentialsTab.tsx               (~250 Zeilen)
├── AIModelsTab.tsx                  (~250 Zeilen)
├── ToolsTab.tsx                     (~250 Zeilen)
├── BillingTab.tsx                   (~100 Zeilen)
├── TenantSettingsPage.module.css
└── hooks/
    └── useCrudTable.ts              (~120 Zeilen — shared IntersectionObserver + CRUD)
```

Layout:

```
┌──────────────┬───────────────────────────────────────────┐
│ ⚙️ General    │  [Active Section Content]                  │
│ ► IAM        │                                           │
│   Groups     │  Identity & Access Management             │
│   Credentials│  Manage who has access...                 │
│   AI Models  │                                           │
│   Tools      │  [+ Add Member]                           │
│   Billing    │  [Members Table]                          │
│              │                                           │
└──────────────┴───────────────────────────────────────────┘
  220px sidebar
```

- Sidebar: 220px, vertikale Navigation
- URL: `?tab=xxx` (bestehend beibehalten)
- Active Item: `bg-selected + left border 3px primary`
- `useCrudTable` Hook: Eliminiert 5x kopierten IntersectionObserver- + Fetch-Code

### 3.5 List-Page Deduplication

**`useEntityList` Custom Hook** extrahieren — eliminiert ~90% Code-Duplikation über ChatAgentsPage, AutonomousAgentsPage, ChatWidgetsPage.

```typescript
interface UseEntityListOptions<T> {
  entityType: string;
  fetchFn: (params: PaginationParams & SearchParams & OrderParams & FilterParams) => Promise<PaginatedResponse<T>>;
  fetchTagsFn?: (search: string) => Promise<TagListResponse>;
  storageKey: string;
}

const { items, isLoading, isLoadingMore, hasMore, tags, searchValue, sortBy, filters,
  handleSearch, handleSort, handleFilter, handleLoadMore, handleDelete, handleStatusChange, refetch
} = useEntityList(options);
```

Jede List-Page schrumpft auf ~80-100 Zeilen (nur Entity-spezifisches JSX + Handler).

### 3.6 Pages entfernen

| Page | Aktion |
|------|--------|
| TracesPage | Entfernen (Traces nur über Conversation/Agent-Detail erreichbar) |

### 3.7 Breadcrumb Navigation

Auf Detail-Pages einführen:

```
Autonomous Agents > Invoice Agent
Chat Agents > Support Bot > Traces
```

- Component: `<Breadcrumbs>` basierend auf Mantine Breadcrumbs
- Automatisch generiert aus Route-Hierarchy + Entity-Name

### 3.8 Entity Avatare

Hash-basierte farbige Initialen für alle Entities:

```
🟦SB  Support Bot       statt      ✨ Support Bot
🟩SA  Sales Agent        statt      ✨ Sales Agent
🟪FH  FAQ Helper         statt      ✨ FAQ Helper
```

- Farbe: `hsl(hash(name) % 360, 70%, 50%)`
- Component: `<EntityAvatar name={name} size="sm" />`
- Verwendet in: DataTable-Rows, Dashboard-Cards, Sidebar-Items, Detail-Header

---

## 4. Phase 3 — Core Features

### 4.1 Global Search

#### Backend

- Neuer Endpoint: `GET /v1/tenants/{id}/search?q=query&types=chat_agent,autonomous_agent&limit=10`
- Durchsucht: Chat Agents (name, description, tags), Autonomous Agents (name, description, tags), Conversations (title, messages), Credentials (name, type), Settings-Entities (Groups, AI Models, Tools)
- Response: `{ results: [{ type, id, name, description, match_field, match_highlight }] }`

#### Frontend

- **Header Search-Bar**: Quick-Search, Ergebnisse als Dropdown unter der Suchleiste
- `⌘K` / `Ctrl+K`: Öffnet Command Palette (selbes Such-Backend + Commands + Navigation)
- `/`: Focus auf Header-Search
- Library für Command Palette: `cmdk` oder `kbar`
- Debounce: 300ms auf Input
- Recent Searches: In localStorage, max 5

#### Command Palette Commands

```
RECENT
  🤖 Invoice Agent                    Autonomous Agent
  ✨ Support Bot                      Chat Agent

COMMANDS
  ➕ Create Chat Agent
  ➕ Create Autonomous Agent
  ⚙️  Open Settings
  🌙 Toggle Dark Mode

NAVIGATION
  📄 Chat Agents
  📄 Conversations
  📄 Settings
```

### 4.2 Notifications System

#### Backend (Platform Service)

- Neues DB-Modell: `notifications` Tabelle (→ Details in §7)
- Events die Notifications erzeugen:
  - **Agent-Fehler**: Autonomous Agent Trace mit Status `failed`
  - **Credential abgelaufen**: Credential mit abgelaufenem Secret (wenn erkannt)
  - **Trace importiert**: Autonomous Agent Trace erfolgreich importiert
- Polling-basiert: Frontend pollt alle 60 Sekunden
- Kein E-Mail, nur In-App

#### Frontend

- **Notification Panel**: Sidebar/Panel (wie GitHub) — öffnet sich bei Klick auf 🔔
- Header-Badge: Roter Dot (kein Zahl) wenn ungelesene Notifications existieren
- Panel-Features:
  - Liste aller Notifications (newest first)
  - Einzeln als gelesen markieren (Klick)
  - "Mark all as read" Button oben
  - Klick auf Notification → navigiert zur betroffenen Resource
- `NotificationsContext`: Pollt alle 60s, cached im State, unread-Count für Badge

```
┌────────────────────────────────────────────────┐
│ Notifications                    [Mark all ✓]  │
├────────────────────────────────────────────────┤
│ 🔴 Invoice Agent — trace failed               │
│    "Connection timeout to n8n endpoint"        │
│    2 minutes ago                          [✓]  │
├────────────────────────────────────────────────┤
│ 🟢 Email Parser — trace imported               │
│    Execution #14 imported successfully         │
│    15 minutes ago                         [✓]  │
├────────────────────────────────────────────────┤
│ 🟡 API Key "n8n-prod" — credential expiring   │
│    Expires in 7 days                           │
│    1 hour ago                             [✓]  │
└────────────────────────────────────────────────┘
```

### 4.3 Favorites/Pins anbinden

**Backend existiert bereits** (3 Favorites-Tabellen für chat_agent, autonomous_agent, conversation).

Frontend-Arbeiten:
- `FavoritesContext`: Lädt alle Favorites beim Mount, cached als `Map<type, Set<id>>`
- `isFavorite(type, id)` / `toggleFavorite(type, id)` — optimistic update
- **DataTableRow**: Star-Icon (☆/★) links neben Entity-Namen, klickbar
- **ChatAgentsPage**: Favorites anbinden
- **AutonomousAgentsPage**: Favorites anbinden
- **DataTable**: Pinned Items immer oben sortieren (visueller Separator)
- **SidebarDataList**: Favorites mit Star-Icon markieren

### 4.4 Last Visited

- **localStorage + Backend-Sync**
- `RecentVisitsContext`: Tracked letzte 50 Visits, dedupliziert
- Storage-Key: `unified-ui-recent-visits-{tenantId}`
- Tracked bei: Navigation zu Detail-Pages, Conversation-Öffnung, Sidebar-Item-Klick
- NICHT tracked: List-Page-Navigation, Settings
- Backend-Sync: `POST /v1/tenants/{id}/users/{uid}/recent-visits` periodisch
- Backend-Read: `GET /v1/tenants/{id}/users/{uid}/recent-visits?limit=20`

### 4.5 Dashboard Redesign

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Welcome back, {userName} 👋                                            │
│ Here's what's happening in "{tenantName}"                              │
│                                                                         │
│ ── Quick Stats ────────────────────────────────────────────────────── │
│ [12 Chat Agents] [8 Auto Agents] [156 Active Convos] [1.2k Traces]   │
│    +2 this week     3 active        +24 today          ↗ 15%          │
│                                                                         │
│ ── ★ Favorites ────────────────────────────────── [View All →] ────── │
│ [Card: Support Bot] [Card: Invoice Agent] [Card: Sales Agent]          │
│                                                                         │
│ ── 🕐 Recently Visited ──────────────────────── [View All →] ────── │
│ [Card: Email Parser] [Card: FAQ Bot] [Card: Conv #3842]                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**KEIN Activity Feed** (User-Entscheidung).

Sections:
1. **Quick Stats**: 4 Cards (Chat Agents, Autonomous Agents, Active Convos, Traces 7d) — klickbar, navigiert zu List-Page
2. **Favorites**: Max 6 Cards, aus FavoritesContext + Entity-Detail-Nachladen
3. **Recently Visited**: Max 6 Cards, aus RecentVisitsContext

Datenquelle Stats:
- Neuer Endpoint: `GET /v1/tenants/{id}/dashboard/stats` (→ §8)
- Oder: Einzelne List-APIs mit `limit=0` und `X-Total-Count` Header

---

## 5. Phase 4 — Conversations Overhaul

### 5.1 Architektur-Refactoring

ConversationsPage (934 Zeilen) aufbrechen:

```
ConversationsPage/
├── ConversationsPage.tsx               (~200 Zeilen — Layout + Wiring)
├── ConversationsPage.module.css
├── hooks/
│   ├── useChat.ts                      (~250 Zeilen — SSE, Streaming, Messages)
│   ├── useConversationList.ts          (~150 Zeilen — CRUD, Filter, Sort)
│   ├── useConversationTracing.ts       (~80 Zeilen — Trace laden, Node-Mapping)
│   └── useFileUpload.ts               (~80 Zeilen — File handling + forwarding)
├── components/
│   ├── ChatSidebar/                    (Conversation list + search)
│   ├── ChatHeader/                     (Conversation info + actions)
│   ├── ChatContent/                    (Message list + scroll behavior)
│   ├── ChatInput/                      (Input + attachments + submit)
│   └── MessageBubble/                  (Individual message rendering)
```

### 5.2 Chat-Features — ALLE implementieren

#### Scroll-Verhalten

- Wenn Streaming aktiv: Auto-Scroll nach unten (an den Stream geheftet)
- Wenn User aktiv hochscrollt/festhält: Scroll-Position beibehalten, NICHT nach unten forcen
- "↓ New messages" Button erscheint wenn User nicht am Ende ist
- Klick auf Button → smooth scroll to bottom

#### Error Handling

- Streaming-Fehler: User-Nachricht BEIBEHALTEN, nur AI-Antwort als Error markieren
- Error-Message als rote Bubble anzeigen mit Fehlerbeschreibung
- **Auto-Retry**: Bei erstem Fehler automatisch einmal neu versuchen
- Bei erneutem Fehler: Error-Bubble anzeigen mit "Retry" Button

#### Message Edit (Letzte User-Nachricht)

- Nur die letzte User-Nachricht ist editierbar
- Edit-Icon erscheint bei Hover über die letzte User-Message
- Klick → Nachricht wird zum editierbaren Textarea
- Submit → neuer Agent-Run (quasi Retry mit geändertem Text)
- Backend: Bestehende Nachricht updaten + neuen Agent-Run triggern

#### Message Delete

- User kann eigene Nachrichten löschen
- Bestätigungs-Dialog: "Delete this message?"
- Backend: `DELETE /messages/{id}`

#### Message Copy

- Copy-Button bei Hover über jede Nachricht (User + Assistant)
- Kopiert den Markdown-Rohtext in den Clipboard
- Toast: "Message copied"

#### Code-Block Copy

- In gerenderten Markdown Code-Blocks: Copy-Button rechts oben im Block
- Kopiert nur den Code-Inhalt
- Syntax-Highlighting beibehalten (bestehend)

#### Message Reaction (👍👎 + Text-Feedback)

- Unter jeder Assistant-Nachricht: 👍 und 👎 Buttons
- Klick → Reaction wird gespeichert
- Optional: Text-Feedback-Input (kleines Textarea das aufklappt)
- **Neues Backend-Modell**: `message_reactions` Collection (→ §7)
- Daten: `message_id`, `conversation_id`, `tenant_id`, `user_id`, `reaction` (thumbs_up/thumbs_down), `feedback_text`, `created_at`

#### File Upload

- Dateitypen: Bilder, PDFs, TXT, Markdown, Word, Excel
- Speicherung: **KEINE** — Dateien werden direkt an Agent-Tools weitergeleitet
- Frontend: Drag & Drop + Clip-Button im ChatInput
- Metadaten: Bei der Nachricht speichern welche Dateien (Typ, Anzahl, Name) mitgesendet wurden
- Anzeige in Chat: Dateien als kleine Badges/Chips an der User-Nachricht (Icon pro Typ + Dateiname)
- **Integration recherchieren**: N8N File-Handling + Microsoft Foundry (NEUE Version, nicht classic Azure AI Foundry)

#### Conversation Export

- Export-Menü im ChatHeader (3 Formate):
  - **Markdown**: Conversation als .md Datei
  - **PDF**: Conversation als formatiertes PDF (via Browser Print oder Library)
  - **JSON**: Raw Messages als .json Datei

#### Conversation-Sidebar Verbesserungen

- Infinite Scroll statt Hard-Limit 100
- Server-side Search (aktuell nur Client-Filter)
- Rechtsklick-Kontext-Menü: Copy ID, Edit, Delete, Pin, Export

#### Mobile-Fix

- Sidebar als Overlay/Drawer auf <768px
- Chat-Area full-width wenn Sidebar geschlossen
- Tracing-Sidebar als Bottom-Sheet oder Dialog auf Mobile

### 5.3 Chat-Component Parametrisierbar machen

Das Chat-Component muss parametrisierbar sein für Wiederverwendung im ReACT Agent Playground (→ §9):

```typescript
interface ChatPanelProps {
  mode: 'conversation' | 'playground';
  conversationId?: string;           // nur bei 'conversation'
  chatAgentId?: string;            // nur bei 'conversation'
  agentConfig?: PlaygroundConfig;    // nur bei 'playground'
  persistMessages?: boolean;         // true bei conversation, false bei playground
  showTracing?: boolean;             // true bei conversation, optional bei playground
  showSidebar?: boolean;             // true bei conversation, false bei playground
  showExport?: boolean;
  showReactions?: boolean;
}
```

---

## 6. Phase 5 — Polish

### 6.1 Command Palette

- Tastenkürzel: `⌘K` / `Ctrl+K`
- Such-Input + Ergebnisliste (Entities, Commands, Navigation)
- Library: `cmdk` oder `kbar`
- Commands:
  - Create Entity (Chat Agent, Agent, etc.)
  - Navigation (Dashboard, Settings, etc.)
  - Toggle Dark Mode
  - Focus Search
  - Open Settings
- Recent Searches integriert

### 6.2 Skeleton Loading

Skeleton statt Spinner bei allen Daten-Loading-States:

- DataTable: Row-Skeletons (5 Zeilen mit animierten Blöcken)
- Dashboard Cards: Card-shaped Skeletons
- Detail Pages: Content-shaped Skeletons
- Settings: Table-Skeletons

Component: Mantine `<Skeleton>` Komponente nutzen.

### 6.3 Empty States

Illustrierte Empty States mit Call-to-Action auf allen List-Pages:

```
┌──────────────────────────────────────┐
│                                      │
│        [Illustration/Icon]           │
│                                      │
│    No chat agents yet               │
│    Create your first AI agent to     │
│    get started.                      │
│                                      │
│       [+ Create Chat Agent]         │
│                                      │
└──────────────────────────────────────┘
```

Pro Entity-Typ ein passender Empty-State-Text + CTA.

### 6.4 Optimistic Updates

| Aktion | Strategie |
|--------|-----------|
| Delete | Sofort aus UI entfernen + Fade-Out Animation, Rollback bei Fehler |
| Status Toggle | Switch sofort togglen, Rollback bei Fehler |
| Favorite Toggle | Star sofort togglen, Rollback bei Fehler |
| Update Entity | Im lokalen State sofort updaten, Rollback bei Fehler |
| Create Entity | Temporäres Item mit Loading-State einfügen, durch echte Daten ersetzen |

Delete-Animation:
```css
.dataTableRow.deleting {
  opacity: 0;
  transform: translateX(-20px);
  max-height: 0;
  transition: all 200ms ease-out;
}
```

React.memo für DataTableRow, useCallback für Event-Handler.

### 6.5 Keyboard Shortcuts

| Shortcut | Aktion |
|----------|--------|
| `⌘K` / `Ctrl+K` | Command Palette öffnen |
| `N` | New Entity (kontextabhängig — auf ChatAgentsPage → Create Chat Agent) |
| `/` | Focus Header-Search |
| `Esc` | Close Dialog / Deselect / Close Panel |
| `⌘,` / `Ctrl+,` | Open Settings |

Implementierung: Custom `useKeyboardShortcuts` Hook mit Context-Awareness.

### 6.6 Multi-Select / Bulk Actions

- Checkbox-Column links in DataTable (unsichtbar by default, erscheint bei ersten Checkbox-Klick oder Shift-Select)
- Bulk-Action-Bar erscheint über der Tabelle bei Selection:

```
┌──────────────────────────────────────────────────────────────┐
│ 3 selected    [Delete] [Set Tags] [Toggle Status]  [Cancel] │
└──────────────────────────────────────────────────────────────┘
```

Aktionen: Bulk Delete, Bulk Tag, Bulk Status Toggle.

### 6.7 Tenant-Switching ohne Reload

Aktuell: `window.location.reload()` bei Tenant-Switch.

Neu:
1. Context-Update: `selectedTenant` im IdentityContext setzen
2. Alle Data-Contexts invalidieren: SidebarDataContext, FavoritesContext, RecentVisitsContext, NotificationsContext
3. Navigation zu Dashboard
4. Loading-Skeletons während Daten neu laden
5. Kein Page-Reload

### 6.8 Context-Architektur Splitting

Aktuellen `IdentityContext` aufteilen:

```
VORHER:
  IdentityContext (user + tenants + apiClient + alles)

NACHHER:
  AuthContext          (user, tokens, login/logout)
  TenantContext        (selectedTenant, tenants, switchTenant)
  ApiClientContext     (apiClient — stable, memo'd, kein Re-Render)
  FavoritesContext     (favorites state + toggle)
  RecentVisitsContext  (last visited tracking)
  NotificationsContext (notification state + polling)
```

Trennung verhindert unnötige Re-Renders.

---

## 7. Datenmodell-Änderungen (Backend)

### 7.1 Neue Tabelle: `notifications` (Platform Service — PostgreSQL)

```
┌──────────────────────────────────────────────────────────────────────┐
│ notifications                                                        │
├──────────────────┬───────────────────┬───────────────────────────────┤
│ Column           │ Type              │ Constraints                   │
├──────────────────┼───────────────────┼───────────────────────────────┤
│ id               │ UUID              │ PK, default uuid4             │
│ tenant_id        │ UUID              │ FK → tenants.id, NOT NULL     │
│ user_id          │ VARCHAR(255)      │ NULL = broadcast to all       │
│ type             │ NotificationTypeEnum │ NOT NULL                   │
│ title            │ VARCHAR(255)      │ NOT NULL                      │
│ message          │ TEXT              │ NULL                          │
│ resource_type    │ VARCHAR(50)       │ NULL (e.g. "autonomous_agent")│
│ resource_id      │ UUID              │ NULL                          │
│ is_read          │ BOOLEAN           │ NOT NULL, default FALSE       │
│ created_at       │ TIMESTAMP         │ NOT NULL, default now()       │
│ updated_at       │ TIMESTAMP         │ NOT NULL, default now()       │
└──────────────────┴───────────────────┴───────────────────────────────┘

Indices:
  - (tenant_id, user_id, is_read, created_at DESC)  — für Polling
  - (tenant_id, created_at DESC)                      — für Sortierung

NotificationTypeEnum:
  - AGENT_RUN_FAILED
  - CREDENTIAL_EXPIRING
  - TRACE_IMPORTED
```

**Wann werden Notifications erstellt?**:

| Event | Wo erzeugt | NotificationType | user_id |
|-------|-----------|-----------------|---------|
| Autonomous Agent Trace mit Status `failed` | Agent Service → Platform Service Callback ODER Platform Service prüft Traces periodisch | `AGENT_RUN_FAILED` | NULL (alle mit Zugriff) |
| Credential Secret nähert sich Ablauf | Platform Service cron/scheduled task | `CREDENTIAL_EXPIRING` | NULL (alle mit Zugriff) |
| Trace erfolgreich importiert (Autonomous Agent) | Agent Service Import-Handler → Platform Service Callback | `TRACE_IMPORTED` | NULL (alle mit Zugriff) |

**Offene Frage**: Wie erfährt der Platform Service von Agent-Service-Events? Optionen:
- **A) Webhook/Callback**: Agent Service ruft Platform Service API beim Trace-Import auf
- **B) Polling**: Platform Service pollt Agent Service Traces periodisch
- **C) Shared Event Bus**: Redis Pub/Sub oder ähnliches

→ **Empfehlung: Option A (Webhook)** — Agent Service ruft `POST /v1/internal/notifications` auf dem Platform Service auf wenn ein Trace importiert wird oder fehlschlägt. Leichtgewichtig, kein neues Infra-Tool nötig.

---

### 7.2 Neue Tabelle: `recent_visits` (Platform Service — PostgreSQL)

```
┌──────────────────────────────────────────────────────────────────────┐
│ recent_visits                                                        │
├──────────────────┬───────────────────┬───────────────────────────────┤
│ Column           │ Type              │ Constraints                   │
├──────────────────┼───────────────────┼───────────────────────────────┤
│ id               │ UUID              │ PK, default uuid4             │
│ tenant_id        │ UUID              │ FK → tenants.id, NOT NULL     │
│ user_id          │ VARCHAR(255)      │ NOT NULL                      │
│ resource_type    │ VARCHAR(50)       │ NOT NULL                      │
│ resource_id      │ UUID              │ NOT NULL                      │
│ resource_name    │ VARCHAR(255)      │ NOT NULL                      │
│ visited_at       │ TIMESTAMP         │ NOT NULL, default now()       │
└──────────────────┴───────────────────┴───────────────────────────────┘

Indices:
  - UNIQUE (tenant_id, user_id, resource_type, resource_id) — Upsert-Logik
  - (tenant_id, user_id, visited_at DESC)                    — für Sortierung

TTL/Cleanup:
  - Max 50 Einträge pro User pro Tenant
  - Älteste Einträge werden bei INSERT gelöscht wenn > 50
```

**Sync-Logik**: Frontend tracked in localStorage → Batch-Sync alle 5 Minuten oder bei Page-Unload per `POST /v1/tenants/{id}/users/{uid}/recent-visits/sync`.

---

### 7.3 Neue Collection: `message_reactions` (Agent Service — MongoDB)

```
┌──────────────────────────────────────────────────────────────────────┐
│ message_reactions (MongoDB Collection)                                │
├──────────────────┬───────────────────┬───────────────────────────────┤
│ Field            │ Type              │ Description                   │
├──────────────────┼───────────────────┼───────────────────────────────┤
│ _id              │ ObjectID          │ Auto-generated                │
│ tenant_id        │ string            │ Tenant-Scope                  │
│ conversation_id  │ string            │ Conversation-Scope            │
│ message_id       │ string            │ Referenz zur Nachricht        │
│ user_id          │ string            │ Wer hat reagiert              │
│ reaction         │ string            │ "thumbs_up" | "thumbs_down"  │
│ feedback_text    │ string            │ Optionaler Freitext           │
│ created_at       │ datetime          │ Zeitstempel                   │
│ updated_at       │ datetime          │ Bei Änderung der Reaction     │
└──────────────────┴───────────────────┴───────────────────────────────┘

Indices:
  - { tenant_id: 1, conversation_id: 1, message_id: 1 }
  - { tenant_id: 1, user_id: 1 }
  - UNIQUE: { tenant_id: 1, message_id: 1, user_id: 1 }  — 1 Reaction pro User pro Message
```

**Verhalten**: User kann Reaction ändern (thumbs_up ↔ thumbs_down) oder entfernen. Text-Feedback kann jederzeit ergänzt/geändert werden.

---

### 7.4 Erweiterung: `messages` Collection (Agent Service — MongoDB)

Bestehendes `Message` Modell erweitern um File-Attachment-Metadaten:

```
Neues Feld in Message (nur bei Type "user"):
  attachments_metadata: [
    {
      file_name: string,         // "invoice.pdf"
      file_type: string,         // "application/pdf"
      file_size: number,         // Bytes
      file_category: string      // "pdf" | "image" | "document" | "spreadsheet" | "text"
    }
  ]
```

**Hinweis**: Die Datei selbst wird NICHT gespeichert. Nur Metadaten werden in der Nachricht persistiert, damit im Chat-Verlauf angezeigt werden kann, welche Dateien mitgesendet wurden.

---

### 7.5 Erweiterung: `AIModelPurposeGroupEnum` (Platform Service)

Neuer Enum-Wert hinzufügen:

```python
class AIModelPurposeGroupEnum(str, Enum):
    CONVERSATION_TITLE_GENERATION = "CONVERSATION_TITLE_GENERATION"
    CONVERSATION_SUMMARIZATION = "CONVERSATION_SUMMARIZATION"
    DESCRIPTION_GENERATION = "DESCRIPTION_GENERATION"
    TRACE_ANALYSIS = "TRACE_ANALYSIS"
    GENERAL = "GENERAL"
    REACT_AGENT = "REACT_AGENT"        # ← NEU: für ReACT Agent Developer Page
```

---

### 7.6 Neues Modell: `re_act_agents` (Platform Service — PostgreSQL)

Für den ReACT Agent Developer (→ §9). Config-Daten (Tools, Models, Prompts, Greetings) werden als JSON gespeichert.

```
┌──────────────────────────────────────────────────────────────────────┐
│ re_act_agents                                                        │
├──────────────────┬───────────────────┬───────────────────────────────┤
│ Column           │ Type              │ Description                   │
├──────────────────┼───────────────────┼───────────────────────────────┤
│ id               │ UUID              │ PK                            │
│ tenant_id        │ UUID              │ FK → tenants, NOT NULL        │
│ name             │ VARCHAR(255)      │ NOT NULL                      │
│ description      │ TEXT              │ NULL                          │
│ ai_model_ids     │ JSON (UUID[])     │ References to tenant_ai_models│
│ system_prompt    │ TEXT (max 8000)   │ System Instructions           │
│ tool_ids         │ JSON (UUID[])     │ References to tools table     │
│ security_prompt  │ TEXT              │ Security Instructions (vorab) │
│ tool_use_prompt  │ TEXT              │ Tool Use Instructions (vorab) │
│ response_prompt  │ TEXT              │ Response Formatting (vorab)   │
│ greeting_messages│ JSON (string[])   │ Optional greeting messages    │
│ config           │ JSON              │ Extra config (temperature etc)│
│ is_active        │ BOOLEAN           │ default TRUE                  │
│ created_by       │ VARCHAR(255)      │ User ID                       │
│ created_at       │ TIMESTAMP         │ Audit                         │
│ updated_at       │ TIMESTAMP         │ Audit                         │
└──────────────────┴───────────────────┴───────────────────────────────┘

+ re_act_agent_members (standard RBAC members table)
+ re_act_agent_tags    (standard tags association)
```

**Spaltenreihenfolge spiegelt die UI-Reihenfolge wider** (AI Models → Instructions → Tools → Prompts → Greetings).

**Prompt Templates**: `security_prompt`, `tool_use_prompt` und `response_prompt` werden mit sinnvollen Defaults vorausgefüllt (nicht leer).

---

### 7.7 Widget Designer — Config-Erweiterung

Das bestehende `chat_widgets.config` JSON-Feld erweitern um Widget-Form-Felder:

```json
{
  "existing_config_fields": "...",
  "form_fields": [
    {
      "id": "uuid",
      "type": "text | textarea | select | multi_select | toggle | label | file | description_textarea",
      "label": "Field Label",
      "placeholder": "Optional placeholder",
      "required": true,
      "options": ["Option A", "Option B"],
      "default_value": "...",
      "order": 1,
      "validation": {
        "min_length": 0,
        "max_length": 500,
        "pattern": "regex (optional)"
      }
    }
  ],
  "form_layout": {
    "fields_order": ["field-id-1", "field-id-2"],
    "title": "Widget Form Title",
    "description": "Widget Form Description",
    "submit_label": "Submit"
  }
}
```

**Kein neues DB-Modell nötig** — nutzt das bestehende `config` JSON-Feld der `chat_widgets` Tabelle.

---

### 7.8 Zusammenfassung Datenmodell-Änderungen

| Änderung | Service | Typ | Prio |
|----------|---------|-----|------|
| `notifications` Tabelle | Platform (PostgreSQL) | NEUE TABELLE | P2 |
| `NotificationTypeEnum` | Platform | NEUER ENUM | P2 |
| `recent_visits` Tabelle | Platform (PostgreSQL) | NEUE TABELLE | P3 |
| `message_reactions` Collection | Agent (MongoDB) | NEUE COLLECTION | P3 |
| `messages.attachments_metadata` | Agent (MongoDB) | FELD-ERWEITERUNG | P3 |
| `AIModelPurposeGroupEnum.REACT_AGENT` | Platform | ENUM-ERWEITERUNG | P4 |
| `re_act_agents` + Members + Tags | Platform (PostgreSQL) | NEUE TABELLE(N) | P4 |
| `chat_widgets.config.form_fields` | Platform (JSON-Schema) | SCHEMA-ERWEITERUNG | P4 |

---

## 8. Neue API-Endpoints

### 8.1 Platform Service — Neue Endpoints

| Methode | Pfad | Beschreibung | Prio |
|---------|------|-------------|------|
| **GET** | `/v1/tenants/{id}/dashboard/stats` | Quick Stats (Counts pro Entity-Typ) | P1 |
| **GET** | `/v1/tenants/{id}/search?q=...&types=...&limit=10` | Global Search über alle Entities | P2 |
| **GET** | `/v1/tenants/{id}/notifications?is_read=false&limit=20` | Notifications Liste (für Polling) | P2 |
| **GET** | `/v1/tenants/{id}/notifications/unread-count` | Nur Unread-Count (leichtgewichtig für 60s-Polling) | P2 |
| **PUT** | `/v1/tenants/{id}/notifications/{nid}/read` | Einzelne Notification als gelesen markieren | P2 |
| **PUT** | `/v1/tenants/{id}/notifications/read-all` | Alle als gelesen markieren | P2 |
| **DELETE** | `/v1/tenants/{id}/notifications/{nid}` | Notification löschen | P2 |
| **GET** | `/v1/tenants/{id}/users/{uid}/recent-visits?limit=20` | Letzte Visits | P3 |
| **POST** | `/v1/tenants/{id}/users/{uid}/recent-visits/sync` | Batch-Sync von localStorage | P3 |
| **POST** | `/v1/internal/notifications` | Interner Webhook für Agent Service → Notification erstellen | P2 |

### 8.2 Agent Service — Neue Endpoints

| Methode | Pfad | Beschreibung | Prio |
|---------|------|-------------|------|
| **POST** | `/v1/tenants/{tid}/conversations/{cid}/messages/{mid}/reactions` | Reaction erstellen/updaten | P3 |
| **DELETE** | `/v1/tenants/{tid}/conversations/{cid}/messages/{mid}/reactions` | Reaction entfernen | P3 |
| **GET** | `/v1/tenants/{tid}/conversations/{cid}/messages/{mid}/reactions` | Reactions für eine Nachricht | P3 |
| **DELETE** | `/v1/tenants/{tid}/conversations/{cid}/messages/{mid}` | Nachricht löschen | P3 |
| **PUT** | `/v1/tenants/{tid}/conversations/{cid}/messages/{mid}` | Nachricht editieren (Retry) | P3 |

### 8.3 Dashboard Stats Response-Format

```json
{
  "chat_agents": {
    "total": 12,
    "active": 10,
    "inactive": 2
  },
  "autonomous_agents": {
    "total": 8,
    "active": 5,
    "inactive": 3
  },
  "conversations": {
    "total": 567,
    "active_7d": 156
  },
  "traces": {
    "total_7d": 1247,
    "failed_7d": 29,
    "error_rate_7d": 2.3
  }
}
```

### 8.4 Global Search Response-Format

```json
{
  "results": [
    {
      "type": "chat_agent",
      "id": "uuid",
      "name": "Support Bot",
      "description": "Handles customer support...",
      "match_field": "name",
      "is_active": true,
      "tags": ["support", "faq"]
    }
  ],
  "total": 5,
  "query": "support"
}
```

### 8.5 Notification Response-Format

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "type": "AGENT_RUN_FAILED",
  "title": "Invoice Agent — trace failed",
  "message": "Connection timeout to n8n endpoint",
  "resource_type": "autonomous_agent",
  "resource_id": "uuid",
  "is_read": false,
  "created_at": "2026-02-08T10:30:00Z"
}
```

---

## 9. Widget Designer & ReACT Agent Developer

### 9.1 Widget Designer Page

**Zweck**: Visual Editor für Chat-Widget Form-Konfiguration + Live-Preview.

#### Verfügbare Feld-Typen

| Typ | Beschreibung | Config |
|-----|-------------|--------|
| `text` | Einzeiliges Textfeld | label, placeholder, required, max_length |
| `textarea` | Mehrzeiliges Textfeld | label, placeholder, required, max_length, rows |
| `description_textarea` | Beschreibungs-Textarea (read-heavy) | label, content |
| `select` | Single-Select Dropdown | label, options[], required, default_value |
| `multi_select` | Multi-Select Tags/Chips | label, options[], required |
| `toggle` | Boolean Toggle/Switch | label, default_value (true/false) |
| `label` | Nur Anzeige-Text (kein Input) | text, style (heading/info) |
| `file` | Datei-Upload-Feld | label, accepted_types[], max_size |

#### Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ Widget Designer                                                       │
├──────────────────────────────┬───────────────────────────────────────┤
│                              │                                       │
│  FIELD PALETTE               │  CANVAS (Drop Zone)                   │
│  ┌────────────────────────┐  │  ┌───────────────────────────────┐   │
│  │ 📝 Text Field          │  │  │                               │   │
│  │ 📄 Text Area           │  │  │  [Drag fields here]           │   │
│  │ ▾  Select              │  │  │                               │   │
│  │ ☑  Multi Select        │  │  │  Field 1: Text "Name"   [✕]  │   │
│  │ 🔀 Toggle              │  │  │  Field 2: Select "Type"  [✕]  │   │
│  │ 🏷 Label               │  │  │  Field 3: Toggle "Active"[✕]  │   │
│  │ 📁 File Upload         │  │  │                               │   │
│  │ 📝 Description         │  │  │  [+ Add Field]                │   │
│  └────────────────────────┘  │  └───────────────────────────────┘   │
│                              │                                       │
│  FIELD PROPERTIES            │  LIVE PREVIEW                         │
│  (when field selected)       │  ┌───────────────────────────────┐   │
│  ┌────────────────────────┐  │  │ Widget Form Preview           │   │
│  │ Label: [Name        ]  │  │  │                               │   │
│  │ Placeholder: [...]     │  │  │ Name: [_______________]       │   │
│  │ Required: [✓]          │  │  │ Type: [Select...     ▾]       │   │
│  │ Max Length: [255]      │  │  │ Active: [●○]                  │   │
│  └────────────────────────┘  │  │                               │   │
│                              │  │ [Submit]                       │   │
│                              │  └───────────────────────────────┘   │
│                              │                                       │
├──────────────────────────────┴───────────────────────────────────────┤
│                                              [Cancel]  [Save Widget] │
└──────────────────────────────────────────────────────────────────────┘
```

- Felder per Drag & Drop vertikal stapelbar (kein Grid/Spalten-Layout)
- Felder auswählbar → Properties-Panel links zeigt Konfiguration
- Live-Preview aktualisiert sich in Echtzeit
- Speichert in `chat_widgets.config.form_fields` (bestehendes JSON-Feld)

### 9.2 ReACT Agent Developer Page

**Zweck**: LLM-basierter Agent-Builder mit Playground-Chat, inspiriert vom neuen Copilot Studio.

#### Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ ReACT Agent Developer                                                │
├──────────────────────────────┬───────────────────────────────────────┤
│                              │                                       │
│  CONFIGURATION               │  PLAYGROUND CHAT                      │
│  (Scrollbar, full height)    │  (parameterized ChatPanel)            │
│  Sections: collapsible ▼▶    │                                       │
│                              │                                       │
│  ▼ AI Models ─────────────   │  ┌───────────────────────────────┐   │
│  [🧠 GPT-4o] [✕]            │  │ AI: Hello! How can I help?    │   │
│  [+ Add Model]               │  │                               │   │
│  [+ Create New Model]        │  │ You: Check weather in Berlin  │   │
│  (Only REACT_AGENT purpose)  │  │                               │   │
│                              │  │ AI: [Calling Weather Tool...] │   │
│  ▼ Instructions ───────────  │  │ The weather in Berlin is 5°C  │   │
│  System Instructions         │  │ with light rain.              │   │
│  ┌──────────────────────┐    │  │                               │   │
│  │ You are a helpful    │    │  │                               │   │
│  │ assistant that...    │    │  │                               │   │
│  │ (max 8000 chars)     │    │  │                               │   │
│  └──────────────────────┘    │  │ [Message input...]       [→]  │   │
│                              │  └───────────────────────────────┘   │
│  ▼ Tools ─────────────────   │                                       │
│  [🔧 MCP Weather] [✕]       │  Playground messages are NOT          │
│  [🔧 OpenAPI CRM ] [✕]      │  persisted.                           │
│  [+ Add Tool]                │                                       │
│  [+ Create New Tool]         │                                       │
│                              │                                       │
│  ▼ Prompt Templates ───────  │                                       │
│  Security Instructions       │                                       │
│  ┌──────────────────────┐    │                                       │
│  │ [pre-filled default] │    │                                       │
│  └──────────────────────┘    │                                       │
│  Tool Use Instructions       │                                       │
│  ┌──────────────────────┐    │                                       │
│  │ [pre-filled default] │    │                                       │
│  └──────────────────────┘    │                                       │
│  Response Format Instr.      │                                       │
│  ┌──────────────────────┐    │                                       │
│  │ [pre-filled default] │    │                                       │
│  └──────────────────────┘    │                                       │
│                              │                                       │
│  ▶ Greeting Messages (opt) ─ │                                       │
│  (collapsed by default)      │                                       │
│                              │                                       │
├──────────────────────────────┴───────────────────────────────────────┤
│                                         [Save Config]  [Test Agent]  │
└──────────────────────────────────────────────────────────────────────┘
```

#### Konfigurationsfelder (Reihenfolge = UI-Reihenfolge)

Jede Sektion ist **ein- und ausklappbar** (Mantine `<Accordion>` oder `<Collapse>` mit Section-Header). Default: alle ausgeklappt, Greeting Messages eingeklappt.

| # | Sektion | Felder | Verhalten |
|---|---------|--------|-----------|
| 1 | **AI Models** | Liste ausgewählter Models | Nur Models mit `purpose_group = REACT_AGENT`, auswählen oder inline erstellen |
| 2 | **Instructions** | Textarea, max 8000 Zeichen | Freitext System-Prompt |
| 3 | **Tools** | Liste ausgewählter Tools | Aus bestehenden tenant-tools auswählen ODER neuen Tool inline erstellen (ohne Settings-Page-Navigation) |
| 4 | **Prompt Templates** | 3 Textareas | Security Instructions, Tool Use Instructions, Response Formatting — jeweils mit sinnvollem Default vorausgefüllt |
| 5 | **Greeting Messages** *(optional)* | String-Array | Liste von Begrüßungsnachrichten, die der Agent zu Beginn senden kann. Einfache Liste mit Add/Remove. |

#### Playground-Chat

- Nutzt das parametrisierbare `ChatPanel` Component (→ §5.3)
- `mode: 'playground'`
- `persistMessages: false` — Nachrichten werden NICHT in MongoDB gespeichert
- Kein Tracing, kein Export, keine Reactions
- Config wird live aus dem linken Panel gelesen
- "Clear Chat" Button zum Zurücksetzen

#### Iframe-Einbindung

Das Chat-Component soll auch als Iframe einbindbar sein:
- Dedizierte Route: `/embed/chat/{agentId}?token=xxx`
- Standalone-Seite ohne Sidebar/Header
- Auth via Token-Parameter
- **Konzept für spätere Phase** — jetzt nur die Route vorbereiten

---

## 10. Cross-Cutting Concerns

### 10.1 3-Dot-Menu (bestätigt)

User-Entscheidung: **3-Dot-Menu bevorzugt** über Inline-Action-Buttons. Aktionen bleiben im Kontext-Menü, keine Action-Bar bei Hover.

DataTableRow Menu-Items nur rendern wenn Handler übergeben:
```tsx
{onEdit && <Menu.Item>Edit</Menu.Item>}
{onDuplicate && <Menu.Item>Duplicate</Menu.Item>}
{onDelete && <Menu.Item color="red">Delete</Menu.Item>}
```

### 10.2 Icon-Vereinheitlichung

Einheitliches Icon-Mapping (Tabler Icons):

| Konzept | Icon |
|---------|------|
| Home | `IconHome` / `IconHomeFilled` |
| Conversations | `IconMessages` / `IconMessagesFilled` |
| Chat Agents | `IconSparkles` / `IconSparklesFilled` |
| Autonomous Agents | `IconRobot` / `IconRobotFilled` |
| Traces | `IconTimeline` |
| Chat Widgets | `IconMessageChatbot` |
| Settings | `IconSettings` / `IconSettingsFilled` |
| Tools / ReACT | `IconTool` |
| Credentials | `IconKey` |
| AI Models | `IconBrain` |
| IAM | `IconUsers` |
| Groups | `IconUsersGroup` |
| Billing | `IconCreditCard` |
| Favorites | `IconStar` / `IconStarFilled` |
| Notifications | `IconBell` / `IconBellFilled` |
| Search | `IconSearch` |

Sidebar: Outline default, Filled bei aktiv.

### 10.3 Style Consistency

Einheitliche Design-Tokens verwenden (→ variables.css):

| Element | Spezifikation |
|---------|--------------|
| Page Title | 24px, weight 600 |
| Section Title | 20px, weight 600 |
| Body Text | 14px, weight 400 |
| Small Text | 13px, weight 400 |
| Caption | 12px, weight 500 |
| DataTable Row Height | 60px |
| DataTable Row Padding | 12px 16px |
| Section Card | bg-paper, border default, radius 8px, padding 20px |
| Dialog Size | lg default, xl für Tabs |
| Button Order | Cancel (subtle) links, Primary rechts |
| Row Hover | bg-hover |
| Tags | max 3 visible, rest in Popover |

### 10.4 Files keinen `ChatSidebarContext` nutzen

`ChatSidebarContext` ist möglicherweise dead code. Sidebar implementiert eigene Hover-Logik. Prüfen und ggf. entfernen.

### 10.5 Neue CSS Custom Properties

```css
:root {
  --header-height: 56px;
  --sidebar-width: 80px;
  --sidebar-width-mobile: 56px;
  --settings-sidebar-width: 220px;
  --page-padding-x: 32px;
  --page-padding-y: 24px;
  --data-table-row-height: 60px;
  --section-card-padding: 20px;
  --tab-height: 44px;
  --dashboard-card-min-width: 280px;
}
```

### 10.6 Component-Hierarchie (Ziel)

```
App
├── I18nProvider (react-i18next)
├── AuthContext
├── TenantContext
├── ApiClientContext
├── FavoritesContext
├── RecentVisitsContext
├── NotificationsContext
├── SidebarDataContext
│
├── MainLayout
│   ├── Header (56px)
│   │   ├── Logo
│   │   ├── SearchBar (funktional)
│   │   ├── NotificationPanel
│   │   ├── ThemeToggle
│   │   └── UserMenu
│   │
│   ├── Sidebar (80px)
│   │   ├── NavItems
│   │   └── SidebarDataList
│   │
│   └── <main> (full-width)
│       ├── DashboardPage (Stats + Favorites + Recents)
│       ├── ChatAgentsPage (useEntityList)
│       ├── AutonomousAgentsPage (useEntityList)
│       ├── AutonomousAgentDetailsPage (Breadcrumbs)
│       ├── ChatWidgetsPage (useEntityList)
│       ├── ConversationsPage (ChatPanel, refactored hooks)
│       ├── TenantSettingsPage (SettingsSidebar + Tab-Components)
│       ├── WidgetDesignerPage (DnD Form Builder + Preview)
│       ├── ReactAgentDevPage (Config + Playground ChatPanel)
│       └── LoginPage
│
├── CommandPalette (⌘K)
└── KeyboardShortcuts (global)
```

---

## Appendix: Implementation Checklist

### Phase 1 — Foundation
- [ ] Setup react-i18next + en-US locale files
- [ ] Setup Vitest + RTL + MSW
- [ ] Entferne Fake-UI (Search placeholder, Notification "2", User Menu dead links)
- [ ] Ersetze alle deutschen Strings → i18n Keys
- [ ] Verbessere Error-Handling (Toast bei allen failed API-Calls)
- [ ] Entferne/implementiere TODO-Stubs in Menu-Items
- [ ] Entferne ChatSidebarContext (wenn dead code bestätigt)

### Phase 2 — Layout
- [ ] Header 70→56px
- [ ] Sidebar 100→80px
- [ ] PageContainer entfernen, full-width
- [ ] PageHeader redesign
- [ ] Settings Sidebar-Navigation (TenantSettingsPage aufbrechen)
- [ ] useCrudTable Hook (shared IntersectionObserver + CRUD)
- [ ] useEntityList Hook (shared List-Page logic)
- [ ] Entity Avatare Component
- [ ] Breadcrumbs auf Detail-Pages
- [ ] TracesPage entfernen

### Phase 3 — Core Features
- [ ] **Backend**: `notifications` Tabelle + Migration + API
- [ ] **Backend**: `GET /search` Endpoint
- [ ] **Backend**: `GET /dashboard/stats` Endpoint
- [ ] **Backend**: `recent_visits` Tabelle + Migration + API
- [ ] **Backend**: Internal webhook endpoint für Agent Service
- [ ] **Frontend**: NotificationsContext + Panel
- [ ] **Frontend**: SearchBar funktional + Command Palette (⌘K)
- [ ] **Frontend**: FavoritesContext + DataTable integration
- [ ] **Frontend**: RecentVisitsContext + localStorage + Backend-Sync
- [ ] **Frontend**: Dashboard redesign (Stats + Favorites + Recents)
- [ ] **Frontend**: Tenant-Switching ohne Reload
- [ ] **Frontend**: Context-Architektur Splitting

### Phase 4 — Conversations
- [ ] **Backend**: `message_reactions` Collection + API
- [ ] **Backend**: Message Delete + Edit Endpoints
- [ ] **Backend**: File forwarding (N8N + Microsoft Foundry Integration)
- [ ] **Backend**: `messages.attachments_metadata` Feld
- [ ] **Frontend**: ConversationsPage refactoring (hooks extraction)
- [ ] **Frontend**: ChatPanel parametrisierbar
- [ ] **Frontend**: Scroll-Verhalten (stream-pinned + manual scroll)
- [ ] **Frontend**: Error-Handling (retry once, show error)
- [ ] **Frontend**: Message Edit (letzte User-Nachricht)
- [ ] **Frontend**: Message Delete
- [ ] **Frontend**: Message Copy + Code-Block Copy
- [ ] **Frontend**: Message Reactions (👍👎 + Text-Feedback)
- [ ] **Frontend**: File Upload + Metadaten-Anzeige
- [ ] **Frontend**: Conversation Export (MD, PDF, JSON)
- [ ] **Frontend**: Sidebar Infinite Scroll + Server-Search
- [ ] **Frontend**: Mobile-Fix (Sidebar als Drawer)

### Phase 5 — Polish
- [ ] Command Palette vollständig
- [ ] Skeleton Loading überall
- [ ] Empty States mit CTAs
- [ ] Optimistic Updates (Delete, Toggle, Favorite)
- [ ] Delete Animation
- [ ] Keyboard Shortcuts
- [ ] Multi-Select / Bulk Actions
- [ ] React.memo + useCallback Optimierungen

### Phase 6 — New Pages
- [ ] **Backend**: `re_act_agents` Tabelle + Migration + API (inkl. Members + Tags)
- [ ] **Backend**: `AIModelPurposeGroupEnum.REACT_AGENT`
- [ ] **Frontend**: Widget Designer Page (DnD Form Builder)
- [ ] **Frontend**: ReACT Agent Developer Page (Config + Playground)
- [ ] **Frontend**: Embed Route vorbereiten (`/embed/chat/{id}`)
