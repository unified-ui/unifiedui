# unified-ui Frontend — UI Refactoring Concept v1.0

> **Status**: Draft — zur Abnahme  
> **Erstellt**: 08. Februar 2026  
> **Scope**: Layout-System, Dashboard, Favorites/Pins, Last Visited, Notifications, Settings Navigation, Rendering-Optimierungen, Style Consistency

---

## Inhaltsverzeichnis

1. [Analyse des Ist-Zustands](#1-analyse-des-ist-zustands)
2. [Design-Prinzipien & Inspiration](#2-design-prinzipien--inspiration)
3. [Neues Layout-System (Full-Width)](#3-neues-layout-system-full-width)
4. [Dashboard-Design](#4-dashboard-design)
5. [Favorites / Pins System](#5-favorites--pins-system)
6. [Last Visited Tracking](#6-last-visited-tracking)
7. [Notifications System](#7-notifications-system)
8. [Settings Page — Sidebar Navigation](#8-settings-page--sidebar-navigation)
9. [Rendering-Optimierungen (Flicker-Free)](#9-rendering-optimierungen-flicker-free)
10. [Icon-Vereinheitlichung](#10-icon-vereinheitlichung)
11. [Style Consistency Guide](#11-style-consistency-guide)
12. [Daten-Requirements (Backend)](#12-daten-requirements-backend)
13. [Implementierungs-Roadmap](#13-implementierungs-roadmap)

---

## 1. Analyse des Ist-Zustands

### Aktuelles Layout-System

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER (70px, fixed top)                                        │
├──────┬──────────────────────────────────────────────────────────┤
│      │  padding: 32px                                           │
│ SIDE │  ┌─────────────────────────────────┐                     │
│ BAR  │  │  PageContainer (max 1200px)     │                     │
│      │  │  ┌───────────────────────────┐  │                     │
│ 100  │  │  │  PageHeader               │  │     ← zentriert    │
│  px  │  │  ├───────────────────────────┤  │                     │
│      │  │  │  DataTable / Content      │  │                     │
│      │  │  │                           │  │                     │
│      │  │  └───────────────────────────┘  │                     │
│      │  └─────────────────────────────────┘                     │
│      │                                            ← viel        │
│      │                                               ungenutzter│
│      │                                               Platz      │
└──────┴──────────────────────────────────────────────────────────┘
```

### Probleme

| Problem | Beschreibung |
|---------|-------------|
| **Zentriertes Container-Layout** | `PageContainer` nutzt Mantine `<Container>` mit max-width 1200px → auf breiten Screens wird >40% des Platzes verschwendet |
| **Dashboard ist Platzhalter** | Nur statische Cards (Willkommen, Tenant-Info), keine dynamischen Daten |
| **Pins nicht verbunden** | Backend-API existiert, DataTableRow hat Pin-Menu-Item, aber bis auf Conversations-Favorites ist nichts angebunden |
| **Kein Last-Visited-Tracking** | Existiert weder im Frontend noch im Backend |
| **Notifications hardcoded** | Badge im Header zeigt immer "2", kein Backend |
| **Settings mit horizontalen Tabs** | 7 Tabs horizontal → wird bei vielen Einträgen unübersichtlich, scrollt horizontal auf kleineren Screens |
| **Re-Render-Flackern** | Bei Delete/Update wird komplette Liste neu geladen → UI flackert |
| **Inkonsistente Icons** | Verschiedene Icon-Varianten für gleiche Konzepte (Traces, Agents etc.) |
| **TenantSettingsPage 2000+ Zeilen** | Viel zu große Komponente, schwer wartbar |

---

## 2. Design-Prinzipien & Inspiration

### Design-Referenzen

| App | Was wir übernehmen |
|-----|-------------------|
| **Linear** | Full-width Layout, schnelle Navigation, Clean Sidebar, Keyboard-first UX |
| **Vercel Dashboard** | Card-basiertes Dashboard, Activity Feed, klare Hierarchie |
| **Azure Portal** | Settings als Left-Sidebar, Resource-Overview Pages |
| **GitHub** | Pin/Favorite System, Activity Feed, Notification Center |
| **Power BI** | Dashboard mit Favorites + Recents, Entity-Gruppen |
| **Retool / Supabase Studio** | Admin-Panel full-width, klare Data-Tables, moderne Spacing |

### Design-Prinzipien

1. **Full-Width First** — Content nutzt die gesamte verfügbare Breite mit intelligentem Padding
2. **Information Density** — Mehr Informationen pro Screen, weniger leerer Raum
3. **Progressive Disclosure** — Details on Demand, nicht alles auf einmal
4. **Optimistic Updates** — UI reagiert sofort, rollback bei Fehler
5. **Consistent Patterns** — Gleiche Konzepte sehen überall gleich aus
6. **Keyboard-First** — Power User können alles über Tastatur erreichen

---

## 3. Neues Layout-System (Full-Width)

### 3.1 Neues Layout (Ziel)

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER (56px, fixed top)                                            │
├──────┬──────────────────────────────────────────────────────────────┤
│      │ padding: 24px 32px                                           │
│ SIDE │                                                              │
│ BAR  │ Page Title                               [+ Create Button]  │
│      │ Short description of this page                               │
│  80  │ ────────────────────────────────────────────────────────────  │
│  px  │                                                              │
│      │ ┌──────────────────────────────────────────────────────────┐ │
│      │ │ Search          │ Sort ▾ │ Filter ▾ │        │ ⊞ ≡     │ │
│      │ ├──────────────────────────────────────────────────────────┤ │
│      │ │ Item Row ──────────────────────────── Tags  Status  ⋯  │ │
│      │ │ Item Row ──────────────────────────── Tags  Status  ⋯  │ │
│      │ │ Item Row ──────────────────────────── Tags  Status  ⋯  │ │
│      │ │ Item Row ──────────────────────────── Tags  Status  ⋯  │ │
│      │ │ ...                                                     │ │
│      │ └──────────────────────────────────────────────────────────┘ │
│      │                                                              │
└──────┴──────────────────────────────────────────────────────────────┘
```

### 3.2 Änderungen im Detail

#### Header: 70px → 56px

```
Vorher:  70px → zu viel vertikaler Platz für eine schmale Leiste
Nachher: 56px → Kompakter, mehr Platz für Content

┌─────────────────────────────────────────────────────────────────┐
│ 🔷 unified-ui       🔍 ........................    🔔 🌙 👤    │
│                      Suche                                      │
└─────────────────────────────────────────────────────────────────┘
                        56px Höhe
```

#### Sidebar: 100px → 80px (optional 64px)

```
Vorher:             Nachher:
┌──────────┐        ┌────────┐
│          │        │        │
│  🏠      │        │  🏠   │
│  Home    │        │ Home   │
│          │        │        │
│  💬      │        │  💬   │
│  Conver- │        │ Chats  │
│  sations │        │        │
│          │        │  ✨   │
│  ✨      │        │ Agents │
│  Chat    │        │        │
│  Agents  │        │  🤖   │
│          │        │ Auto   │
│  🤖      │        │        │
│  Autono- │        │  ──── │
│  mous    │        │  🔧   │
│  Agents  │        │ ReACT │
│          │        │        │
│ ──────── │        │  💬   │
│          │        │ Widg.  │
│  🔧      │        │        │
│  ReACT-  │        │        │
│  Agent   │        │        │
│  Dev.    │        │  ⚙️   │
│          │        │ Set.   │
│  💬      │        └────────┘
│  Chat    │           80px
│  Widgets │
│          │
│          │
│  ⚙️      │
│  Settings│
└──────────┘
   100px
```

Vorteile:
- 20px mehr Content-Breite
- Kürzere Labels (1 Zeile statt mehrzeilig)
- Modernerer Look (vgl. Linear, VS Code)

#### PageContainer → Entfernen / Full-Width ersetzen

**Kern-Änderung**: `PageContainer` wird durch ein einfaches CSS-Klassen-System ersetzt:

```css
/* NEU: Page-Level Styles */
.pageContent {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  /* KEIN max-width, KEIN centering */
}
```

Die `MainLayout` `.content`-Klasse wird angepasst:

```css
/* VORHER */
.content {
  margin-top: 70px;
  margin-left: 100px;
  height: calc(100vh - 70px);
  padding: var(--spacing-xl);  /* 32px rundherum */
}

/* NACHHER */
.content {
  margin-top: 56px;                 /* Neue Header-Höhe */
  margin-left: 80px;                /* Neue Sidebar-Breite */
  height: calc(100vh - 56px);
  padding: var(--spacing-lg) var(--spacing-xl);  /* 24px top/bottom, 32px sides */
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
```

#### Neue Spacing-Variablen

```css
:root {
  /* Page Layout */
  --header-height: 56px;
  --sidebar-width: 80px;
  --sidebar-width-mobile: 56px;
  
  /* Page Content */
  --page-padding-x: 32px;          /* Horizontales Padding */
  --page-padding-y: 24px;          /* Vertikales Padding */
  --page-max-width: none;          /* Full-width! */
  
  /* Content Sections */
  --section-gap: 24px;             /* Abstand zwischen Sektionen */
  --section-padding: 20px;         /* Padding innerhalb einer Section Card */
}
```

### 3.3 Page-Header Redesign

```
VORHER:
┌────────────────────────────────────────────────────┐
│  Chat Agents                 [+ Create Application]│
│  Manage your AI chat agents                        │
│  ──────────────────────────────────────────────────│
└────────────────────────────────────────────────────┘
      (zentriert in 1200px Container)

NACHHER:
Chat Agents                                              [+ Create Agent]
Manage and configure your AI-powered chat agents across applications.
─────────────────────────────────────────────────────────────────────────
      (full-width, links-bündig, Linie geht über gesamte Breite)
```

Änderungen:
- **Kein Container-Wrapper** — Header geht über volle Breite
- **Beschreibung max-width: 720px** — Lesbarkeit bei breiten Screens
- **Schlankere Divider-Line** — 1px, `var(--border-light)` statt `var(--border-default)`
- **Title** — `font-size: 24px` (war 24px, bleibt), `font-weight: 600` (war 700 → etwas leichter)
- **Weniger vertikales Padding** — `padding: 16px 0` statt `padding: 24px 0`
- **Kein margin-bottom** — Gap wird durch parent flex-gap gesteuert

### 3.4 Detail-Pages (z.B. AutonomousAgentDetailsPage)

```
VORHER:
┌──────────────────────────────────────────┐
│  (max 1400px, zentriert)                 │
│  ← Agent Name         [Edit] [Delete]   │
│  Description text...                     │
│  ┌──────────────────────────────────┐    │
│  │ Traces │ Details │               │    │
│  ├──────────────────────────────────┤    │
│  │  Content...                      │    │
│  └──────────────────────────────────┘    │
└──────────────────────────────────────────┘

NACHHER:
← Agent Name                                      [Status Badge]  [Edit] [⋮]
  Description text, badges for type and tags
─────────────────────────────────────────────────────────────────────────────
┌─────────┬──────────┐
│ Traces  │ Details  │
├─────────┴──────────┴────────────────────────────────────────────────────┐
│                                                                         │
│  Content uses full width                                                │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Trace Table goes edge to edge (with padding)                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.5 Responsive Breakpoints

```
≥ 1920px (UltraWide):   Sidebar 80px, Content full width
                         Bei Tables: mehr Spalten sichtbar
                         Dashboard: 4 Spalten Grid

≥ 1440px (Desktop):     Sidebar 80px, Content full width
                         Dashboard: 3 Spalten Grid

≥ 1024px (Laptop):      Sidebar 80px, Content full width
                         Dashboard: 2 Spalten Grid

≥ 768px (Tablet):       Sidebar 56px (nur Icons)
                         Content full width
                         Dashboard: 2 Spalten Grid

< 768px (Mobile):        Sidebar collapsed (Hamburger Menu)
                         Content full width
                         Dashboard: 1 Spalte
```

---

## 4. Dashboard-Design

### 4.1 Konzept

Das Dashboard ist die erste Seite nach dem Login. Es soll dem User seine **persönliche Arbeitsumgebung** zeigen — Was ist relevant? Was hat er zuletzt bearbeitet? Was sind seine Favourites?

**Inspiriert von**: Power BI Home, GitHub Dashboard, Vercel Dashboard, Linear Home

### 4.2 Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🏠 Welcome back, Enrico                                     🔔  🌙  👤│
├──────┬──────────────────────────────────────────────────────────────────┤
│      │                                                                  │
│ SIDE │  Welcome back, Enrico 👋                                        │
│ BAR  │  Here's what's happening in "My Tenant"                         │
│      │                                                                  │
│      │  ── Quick Stats ─────────────────────────────────────────────── │
│      │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│      │  │ ✨ 12     │ │ 🤖 8      │ │ 💬 156    │ │ 📊 1.2k   │       │
│      │  │ Chat      │ │ Auto      │ │ Active    │ │ Traces    │       │
│      │  │ Agents    │ │ Agents    │ │ Convos    │ │ (7 days)  │       │
│      │  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
│      │                                                                  │
│      │  ── Favorites ──────────────────────────────── [View All →]  ── │
│      │  ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐  │
│      │  │ ✨ Support Bot   │ │ 🤖 Invoice Agent │ │ ✨ Sales Agent │  │
│      │  │ Last active: 2h  │ │ 42 traces today  │ │ Online • 3 tag │  │
│      │  │ ★ Pinned         │ │ ★ Pinned         │ │ ★ Pinned       │  │
│      │  └──────────────────┘ └──────────────────┘ └────────────────┘  │
│      │                                                                  │
│      │  ── Recently Visited ───────────────────────── [View All →]  ── │
│      │  ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐  │
│      │  │ 🤖 Email Parser  │ │ ✨ FAQ Bot       │ │ 💬 Conv #3842  │  │
│      │  │ Visited 15m ago  │ │ Visited 1h ago   │ │ Visited 3h ago │  │
│      │  └──────────────────┘ └──────────────────┘ └────────────────┘  │
│      │                                                                  │
│      │  ── Recent Activity ─────────────────────────────────────────── │
│      │  │ 🔵 Invoice Agent completed 3 runs         2 minutes ago    │ │
│      │  │ 🟢 Support Bot conversation started        15 minutes ago  │ │
│      │  │ 🟡 Email Parser trace failed               1 hour ago      │ │
│      │  │ 🔵 FAQ Bot updated by admin@company.com    3 hours ago     │ │
│      │  │ 🟢 New API key generated for Sales Agent   5 hours ago     │ │
│      │                                                                  │
└──────┴──────────────────────────────────────────────────────────────────┘
```

### 4.3 Dashboard Sections im Detail

#### Section 1: Quick Stats Bar

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   ✨  12    │  │   🤖   8    │  │   💬  156   │  │   📊 1.2k   │
│             │  │             │  │             │  │             │
│ Chat Agents │  │ Autonomous  │  │  Active     │  │  Traces     │
│             │  │ Agents      │  │  Convos     │  │  (7 days)   │
│ +2 this wk  │  │ 3 active    │  │  +24 today  │  │  ↗ 15%      │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
   klickbar →       klickbar →       klickbar →       klickbar →
 /applications    /auto-agents    /conversations     /traces
```

- **Datenquelle**: Neue Backend-API `GET /tenants/{id}/dashboard/stats`
- Liefert Counts + Trends (Vergleich letzte 7 Tage)
- Klick navigiert zur entsprechenden List-Page
- **Variante**: Optional können die Stats auch direkt aus den bestehenden List-APIs (mit limit=0) abgeleitet werden:
  - `GET /applications?limit=0` → Header `X-Total-Count`
  - Oder: dedizierter lightweight Dashboard-Stats-Endpoint

#### Section 2: Favorites / Pinned Items

```
── ★ Favorites ────────────────────────────────── [View All →] ──

┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ ✨ Support Bot      │  │ 🤖 Invoice Agent    │  │ ✨ Sales Agent      │
│                     │  │                     │  │                     │
│ Application         │  │ Autonomous Agent    │  │ Application         │
│ Last msg: 2h ago    │  │ 42 traces (today)   │  │ Online              │
│ ── ── ── ── ──      │  │ ── ── ── ── ──      │  │ ── ── ── ── ──      │
│ support, faq        │  │ finance, invoice    │  │ sales, crm          │
│                ★    │  │                ★    │  │                ★    │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

- **Datenquelle**: `GET /tenants/{id}/users/{id}/favorites?limit=6` (existierende API!)
- Dann für jedes Favorite-Item die Entity-Details nachladen (oder ein neuer Batch-Endpoint)
- Empfehlung: **Neuer Endpoint** `GET /tenants/{id}/dashboard/favorites` der direkt die Entity-Details + Metadata mitliefert
- Max 6 Items in der Übersicht, "View All" öffnet eine Full-List oder filtert die entsprechende Seite

#### Section 3: Recently Visited

```
── 🕐 Recently Visited ───────────────────────── [View All →] ──

┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ 🤖 Email Parser     │  │ ✨ FAQ Bot          │  │ 💬 Conversation     │
│                     │  │                     │  │    #3842            │
│ Autonomous Agent    │  │ Application         │  │ Conversation        │
│ 15 minutes ago      │  │ 1 hour ago          │  │ 3 hours ago         │
│ ── ── ── ── ──      │  │                     │  │                     │
│ email, automation   │  │ support, chatbot    │  │ Support Bot         │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

- **Datenquelle**: Neuer Endpoint `GET /tenants/{id}/users/{id}/recent-visits?limit=6`
- **Client-side Alternative**: `localStorage`-basiertes Tracking (einfacher, aber nicht cross-device)
- **Empfehlung**: Kombination — Client-tracked + periodisch ans Backend gesynced:
  - Frontend schreibt bei Navigation in ein `localStorage`-Array
  - Beim Dashboard-Load wird aus dem lokalen Array gelesen
  - Optional: `POST /tenants/{id}/users/{id}/recent-visits` zum Sync

#### Section 4: Recent Activity / Activity Feed

```
── 📋 Recent Activity ──────────────────────────────────────────

  🔵  Invoice Agent completed 3 runs               2 min ago
  🟢  Support Bot — new conversation started       15 min ago
  🟡  Email Parser — trace failed (timeout)         1 hour ago
  🔵  FAQ Bot updated by admin@company.com          3 hours ago
  🟢  New API key generated for Sales Agent         5 hours ago
  ─── Show more ───
```

- **Datenquelle**: Neuer Endpoint `GET /tenants/{id}/activity-feed?limit=10`
- Events: Agent Runs, Conversation starts, Config changes, Error/Failures, Access changes
- **Prio**: Niedrigere Prio als Favorites und Recents — kann in v0.2.0 kommen
- Im Minimum: letzte Traces/Runs der Autonomous Agents anzeigen (existierende Daten)

### 4.4 Dashboard Card-Component

Einheitliche Card für Dashboard-Items:

```css
/* DashboardCard Styles */
.dashboardCard {
  background: var(--bg-paper);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);             /* 8px */
  padding: var(--spacing-md);                  /* 16px */
  cursor: pointer;
  transition: all var(--transition-fast) var(--easing-ease-out);
  min-width: 200px;
}

.dashboardCard:hover {
  border-color: var(--color-primary-300);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}
```

### 4.5 Dashboard — Responsive Grid

```
Desktop (≥1440px):    [Card] [Card] [Card] [Card]     ← 4 columns
Laptop  (≥1024px):    [Card] [Card] [Card]             ← 3 columns
Tablet  (≥768px):     [Card] [Card]                    ← 2 columns
Mobile  (<768px):     [Card]                           ← 1 column
                      [Card]
```

CSS:

```css
.dashboardGrid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-md);
}
```

---

## 5. Favorites / Pins System

### 5.1 Ist-Zustand

| Aspekt | Status |
|--------|--------|
| Backend API (CRUD) | ✅ Vollständig implementiert |
| `FavoriteResourceTypeEnum` | ✅ `APPLICATION`, `AUTONOMOUS_AGENT`, `CONVERSATION` |
| ConversationsPage | ✅ Nutzt Favorites |
| ApplicationsPage | ❌ Kein Handler |
| AutonomousAgentsPage | ❌ Nur TODO-Stub |
| DataTableRow | ⚠️ Hat Pin-Menu-Item, aber nicht verbunden |
| Dashboard | ❌ Zeigt keine Favorites |

### 5.2 Konzept

#### Wo Favorites angezeigt werden

1. **Dashboard** — Dedicated "Favorites" Section (Cards, max 6)
2. **List-Pages** — Favourite-Items werden **oben** in der Liste angezeigt, visuell abgesetzt
3. **Sidebar Data-Lists** — Favourites mit Star-Icon markiert, optional separater "Pinned"-Bereich oben
4. **DataTable Rows** — Star-Icon links neben dem Namen

#### DataTable mit Favorites-Sortierung

```
── Search ──────────────── │ Sort ▾ │ Filter ▾ │

  ★ ✨ Support Bot         support, faq        Active    ⋯
  ★ ✨ Sales Agent         sales, crm          Active    ⋯
  ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
  ✨ FAQ Bot                faq, support        Active    ⋯
  ✨ Onboarding Bot         hr, onboarding      Inactive  ⋯
  ✨ Internal Helper        internal, tools     Active    ⋯
```

- Pinned Items kommen immer zuerst (visueller Separator)
- Star-Icon (★) ist klickbar in der Zeile (inline, nicht nur im Menu)
- Im Menu bleibt Pin/Unpin auch erhalten (Redundanz für Discoverability)

#### Quick-Pin via Star-Icon

```
Nicht gepinnt:         Gepinnt:
☆ Agent Name           ★ Agent Name
(outline star)         (filled star, primary color)
```

- Star-Icon links neben dem Entity-Namen in der DataTableRow
- Klick toggled den Pin-Status (optimistic update)
- Kein Dialog, kein Confirmation — instant toggle

### 5.3 Implementierung

```
┌──────────────────────────────────┐
│ FavoritesProvider (Context)      │
│  - favorites: Map<string, Set>   │
│  - isFavorite(type, id): bool    │
│  - toggleFavorite(type, id)      │
│  - loadFavorites(type)           │
│  - favoritesLoaded: boolean      │
└──────────────────────────────────┘
         ↓ used by
┌───────────────┐  ┌───────────────┐  ┌────────────────┐
│ DashboardPage │  │ DataTableRow  │  │ SidebarDataList│
└───────────────┘  └───────────────┘  └────────────────┘
```

- **Neuer Context**: `FavoritesContext` — lädt Favorites einmal beim Mount, cached im State
- **Optimistic Toggle**: UI updated sofort, API-Call im Hintergrund, Rollback bei Fehler
- DataTable bei Favorites-Change: kein Re-Fetch, nur Re-Sort (pinned nach oben)

### 5.4 Favoriten-Fetching-Strategie

```
Option A: Separate Fetch (empfohlen für v1)
  1. Dashboard Mount → GET /favorites?type=all → alle Favorites laden
  2. Favorites in Context speichern (Map<ResourceType, Set<string>>)
  3. DataTable erhält isPinned über Context-Lookup

Option B: Favorites als Teil der List-Response (v2)
  1. Backend gibt bei List-Requests ein `is_pinned` Feld mit
  2. Reduziert API-Calls, aber ändert Backend-Response-Schema
```

---

## 6. Last Visited Tracking

### 6.1 Konzept

Tracking der letzten N besuchten Entities für:
- Dashboard "Recently Visited" Section
- Evtl. Suchvorschläge
- User-Activity-Analyse

### 6.2 Tracking-Strategie

**Empfehlung: Client-Side-First mit optionaler Backend-Persistenz**

```
┌──────────────────────────────────────────────────────┐
│ RecentVisitsProvider (Context)                       │
│                                                      │
│ State:                                               │
│   recentVisits: RecentVisit[]  (max 50 items)       │
│                                                      │
│ Methods:                                             │
│   trackVisit(type, id, name, metadata)              │
│   getRecent(limit): RecentVisit[]                   │
│   getRecentByType(type, limit): RecentVisit[]       │
│   clearHistory()                                     │
│                                                      │
│ Storage:                                             │
│   localStorage: `unified-ui-recent-visits-{tenant}`  │
│   → JSON Array, sorted by timestamp desc            │
│   → Deduplication: gleiche Resource updated timestamp│
│                                                      │
└──────────────────────────────────────────────────────┘
```

#### RecentVisit Interface

```typescript
interface RecentVisit {
  resourceType: 'application' | 'autonomous-agent' | 'conversation' | 'trace' | 'settings';
  resourceId: string;
  resourceName: string;
  visitedAt: string;  // ISO timestamp
  metadata?: {
    tags?: string[];
    status?: string;
    type?: string;
  };
}
```

#### Wann wird ein Visit getrackt?

| Navigation | Tracking |
|-----------|---------|
| `/applications` (Liste) | ❌ Nicht tracken (zu generisch) |
| `/conversations?chat-agent=xxx` (Chat öffnen) | ✅ Conversation tracken |
| `/autonomous-agents/{id}` (Detail-Seite) | ✅ Agent tracken |
| Klick auf Entity in Sidebar-DataList | ✅ Entity tracken |
| `/tenant-settings` | ❌ Nicht tracken |
| `/traces` (Browse) | ❌ Nicht tracken |

#### Deduplication-Logik

```
Benutzer besucht "Support Bot" um 10:00    → [Support Bot 10:00]
Benutzer besucht "Sales Agent" um 10:05    → [Sales Agent 10:05, Support Bot 10:00]
Benutzer besucht "Support Bot" um 10:10    → [Support Bot 10:10, Sales Agent 10:05]
                                              ↑ verschoben nach oben, neuer Timestamp
```

### 6.3 Backend-Persistenz (Optional, v0.2.0+)

Für Cross-Device-Support:

```
POST /tenants/{id}/users/{id}/recent-visits
Body: { resource_type, resource_id, resource_name }

GET /tenants/{id}/users/{id}/recent-visits?limit=20
Response: { visits: [...], total: N }
```

Für v0.1.0 reicht localStorage vollkommen.

---

## 7. Notifications System

### 7.1 Konzept

Notifications informieren den User über asynchrone Events:
- Autonomous Agent Run abgeschlossen (Erfolg / Fehler)
- Neuer User zum Tenant hinzugefügt
- API Key läuft bald ab
- Trace-Error erkannt

### 7.2 Notification Center (Header)

```
Klick auf 🔔 öffnet Dropdown:

┌────────────────────────────────────────────┐
│ Notifications                   [Mark all] │
├────────────────────────────────────────────┤
│ 🔵 Invoice Agent completed 3 runs         │
│    2 minutes ago                           │
├────────────────────────────────────────────┤
│ 🔴 Email Parser trace failed              │
│    "Connection timeout to n8n endpoint"    │
│    1 hour ago                              │
├────────────────────────────────────────────┤
│ 🟢 Max Mustermann joined the tenant       │
│    3 hours ago                             │
├────────────────────────────────────────────┤
│ ── View all notifications ──              │
└────────────────────────────────────────────┘
```

### 7.3 Implementierungs-Stufen

**Stufe 1 (v0.1.0) — Minimal Viable Notifications**:
- Badge im Header entfernen (aktuell hardcoded "2")
- Badge nur anzeigen wenn es echte ungelesene Notifications gibt
- Erstmal: Notification Center mit letzten Autonomous Agent Runs (Traces)
- Datenquelle: `GET /tenants/{id}/traces?sort=created_desc&limit=5` — Traces als "Notifications" darstellen

**Stufe 2 (v0.2.0) — Echtes Notification-System**:
- Backend: Neue `notifications`-Tabelle
- SSE/WebSocket-Push für Real-time Updates
- Notification Types: `AGENT_RUN_COMPLETED`, `AGENT_RUN_FAILED`, `MEMBER_ADDED`, `KEY_EXPIRING`
- Mark as read / Mark all as read
- Notification Settings (pro User konfigurierbar)

### 7.4 Notification Badge Logic

```
unreadCount = 0  → Kein Badge
unreadCount > 0  → Roter Dot (kein Zahl, nur Indikator)
unreadCount > 0  → Optional: Zahl im Badge (max "9+")
```

Empfehlung: **Roter Dot ohne Zahl** für v0.1.0 — simpler und cleaner (wie Linear, Slack).

---

## 8. Settings Page — Sidebar Navigation

### 8.1 Analyse

Aktuell: 7 horizontale Tabs:
```
[ Settings | IAM | Custom Groups | Credentials | AI Models | Tools | Billing ]
```

Probleme:
- Auf schmalen Screens scrollen die Tabs horizontal
- Bei weiteren Tabs wird die Leiste zu lang
- Horizontale Tabs skalieren nicht gut bei 10+ Einträgen

### 8.2 Design-Entscheidung: Vertikale Page-Sidebar

**Referenz**: Azure Portal Settings, GitHub Settings, AWS Console, Vercel Project Settings

```
┌──────────────────────────────────────────────────────────────────────┐
│ HEADER                                                               │
├──────┬───────────────────────────────────────────────────────────────┤
│      │                                                               │
│ NAV  │  Tenant Settings                                              │
│ SIDE │  Manage your tenant configuration and access control          │
│ BAR  │  ─────────────────────────────────────────────────────────── │
│      │                                                               │
│      │  ┌──────────────┬───────────────────────────────────────────┐ │
│      │  │              │                                           │ │
│      │  │  General     │  Identity & Access Management             │ │
│      │  │ ►IAM         │                                           │ │
│      │  │  Groups      │  Manage who has access to this tenant.    │ │
│      │  │  Credentials │  Add members and assign roles.            │ │
│      │  │  AI Models   │                                           │ │
│      │  │  Tools       │  ┌────────────────────────────────────┐   │ │
│      │  │  Billing     │  │ 🔍 Search members                 │   │ │
│      │  │              │  ├────────────────────────────────────┤   │ │
│      │  │              │  │ Name    │ Role    │ Added    │  ⋯  │   │ │
│      │  │              │  │ admin@  │ Admin   │ Jan 2026 │  ⋯  │   │ │
│      │  │              │  │ user@   │ Read    │ Feb 2026 │  ⋯  │   │ │
│      │  │              │  └────────────────────────────────────┘   │ │
│      │  │              │                                           │ │
│      │  └──────────────┴───────────────────────────────────────────┘ │
│      │                                                               │
└──────┴───────────────────────────────────────────────────────────────┘
```

### 8.3 Settings-Sidebar Spezifikation

```
┌──────────────┐
│              │
│  ⚙️ General  │  ← Tenant Name, Description, Danger Zone
│  👥 IAM      │  ← Identity & Access Management (Members-Tabelle)
│  👤 Groups   │  ← Custom Groups
│  🔑 Creds    │  ← Credentials (API Keys, Secrets)
│  🧠 AI Mod.  │  ← AI Model Configurations
│  🔧 Tools    │  ← Tool Definitions
│  💳 Billing  │  ← Billing & Licence
│              │
└──────────────┘
  Breite: 220px
  Padding: 12px
  Items: 40px Höhe
  Active: bg-selected + left border 3px primary
  Font: 14px, weight 500
  Icon: 18px, text-secondary
```

### 8.4 Settings Content Area

Jede Settings-Section hat:
1. **Section Title** (h2, 20px, semibold)
2. **Section Description** (14px, text-secondary, max 600px)
3. **Content** (Formulare, Tabellen, Cards)

```
Identity & Access Management
Manage who has access to this tenant and their permission levels.
─────────────────────────────────────────────────────────────────

[+ Add Member]

┌────────────────────────────────────────────────────────────┐
│ 🔍 Search members...                                       │
├───────────────────┬──────────┬────────────┬───────┬────────┤
│ Member            │ Type     │ Role       │ Added │ Actions│
├───────────────────┼──────────┼────────────┼───────┼────────┤
│ admin@company.com │ User     │ Admin      │ Jan 1 │  ⋯     │
│ dev@company.com   │ User     │ Write      │ Feb 1 │  ⋯     │
│ DevOps Team       │ Group    │ Read       │ Jan 15│  ⋯     │
└───────────────────┴──────────┴────────────┴───────┴────────┘
```

### 8.5 Vorteile des Sidebar-Ansatzes

| Aspekt | Horizontal Tabs (Ist) | Vertical Sidebar (Soll) |
|--------|----------------------|------------------------|
| Skalierbarkeit | Schlecht (≥7 Tabs problematisch) | Gut (20+ Items möglich) |
| Platz für Labels | Begrenzt | Viel (220px Breite) |
| Mobile-friendly | Horizontal Scroll | Collapsible/Accordion |
| Kontext-Klarheit | Tab-Label oft abgeschnitten | Voller Text + Icon sichtbar |
| Übersichtlichkeit | Flach | Gruppierbar (Sections) |
| Pattern-Verbreitung | Wenig bei Settings-Pages | Standard (Azure, GitHub, AWS) |

### 8.6 URL-Routing

Bleibt wie bisher: `/tenant-settings?tab=iam` etc.  
Aber zusätzlich als "echte" Sub-Routes möglich (v0.2.0):
```
/tenant-settings              → General
/tenant-settings/iam          → IAM
/tenant-settings/credentials  → Credentials
...
```

Für v0.1.0: Query-Param-Ansatz beibehalten (`?tab=xxx`), da routing-Änderung aufwändiger.

---

## 9. Rendering-Optimierungen (Flicker-Free)

### 9.1 Problem-Analyse

```
AKTUELL:
  User löscht Item → API Delete Call → On Success: refetch entire list
                                                        ↓
                                       UI: Loading State → Flicker → New List
  
  User updated Item → API Patch Call → On Success: refetch entire list
                                                        ↓
                                       UI: Loading State → Flicker → New List
```

### 9.2 Lösung: Optimistic Updates + Local State Mutations

```
NEU:
  User löscht Item → Sofort: Item aus lokalem State entfernen (Animation)
                   → Im Hintergrund: API Delete Call
                   → Bei Fehler: Item wieder einfügen + Error Toast

  User updated Item → Sofort: Item im lokalen State updaten
                    → Im Hintergrund: API Patch Call
                    → Bei Fehler: Alten State wiederherstellen + Error Toast
```

### 9.3 Implementierungs-Pattern

```typescript
// Optimistic Delete Pattern
const handleDelete = async (id: string) => {
  const previousItems = [...items];
  
  // Optimistic: sofort aus UI entfernen
  setItems(prev => prev.filter(item => item.id !== id));
  
  try {
    await apiClient.deleteApplication(tenantId, id);
    // Sidebar refreshen (lightweight)
    sidebarData.refreshApplications();
  } catch (error) {
    // Rollback bei Fehler
    setItems(previousItems);
    showError('Failed to delete application');
  }
};

// Optimistic Update Pattern
const handleUpdate = async (id: string, data: UpdateRequest) => {
  const previousItems = [...items];
  
  // Optimistic: sofort im UI updaten
  setItems(prev => prev.map(item => 
    item.id === id ? { ...item, ...data } : item
  ));
  
  try {
    await apiClient.updateApplication(tenantId, id, data);
  } catch (error) {
    setItems(previousItems);
    showError('Failed to update application');
  }
};
```

### 9.4 Wo Optimistic Updates anwenden

| Aktion | Optimistic Update | Begründung |
|--------|------------------|------------|
| Delete Item | ✅ Ja | Item sofort ausblenden mit Fade-Out |
| Toggle Status | ✅ Ja | Switch sofort togglen |
| Toggle Pin/Favorite | ✅ Ja | Star sofort togglen |
| Update Name/Description | ✅ Ja | In der Liste sofort reflektieren |
| Create Item | ⚠️ Teilweise | Item temporär mit Loading-State einfügen, nach API-Response mit echten Daten ersetzen |
| Reorder/Sort | ❌ Nein | Server-side Sort → Refetch nötig |
| Pagination/Load More | ❌ Nein | Neue Daten müssen vom Server kommen |

### 9.5 Delete-Animation

```css
.dataTableRow {
  transition: 
    opacity var(--transition-normal) var(--easing-ease-out),
    transform var(--transition-normal) var(--easing-ease-out),
    max-height var(--transition-normal) var(--easing-ease-out);
}

.dataTableRow.deleting {
  opacity: 0;
  transform: translateX(-20px);
  max-height: 0;
  overflow: hidden;
  margin: 0;
  padding: 0;
}
```

### 9.6 React-Rendering-Optimierungen

1. **`React.memo`** für DataTableRow — Re-Render nur wenn Props sich ändern
2. **`useCallback`** für Event-Handler in Listen — stabile Referenzen
3. **`key` Props korrekt** — `key={item.id}` statt Index → React erkennt Adds/Removes korrekt
4. **Virtualisierung** (v0.2.0) — `react-window` oder `@tanstack/virtual` für Listen >100 Items
5. **Skeleton Loading** statt Spinner — Layout bleibt stabil während Daten laden:

```
Spinner (aktuell):              Skeleton (neu):
┌─────────────────┐           ┌─────────────────┐
│                 │           │ ████████████    │
│     ⏳          │           │ ████████        │
│   Loading...    │           │ ────────────────│
│                 │           │ ██████████████  │
└─────────────────┘           │ █████████       │
                              │ ────────────────│
                              │ ████████████    │
                              │ ██████████      │
                              └─────────────────┘
```

---

## 10. Icon-Vereinheitlichung

### 10.1 Icon-Mapping (Vereinheitlicht)

| Konzept | Icon (Outline) | Icon (Filled) | Wozu |
|---------|---------------|---------------|------|
| Home / Dashboard | `IconHome` | `IconHomeFilled` | Sidebar, Breadcrumbs |
| Chat / Conversations | `IconMessages` | `IconMessagesFilled` | Sidebar, Nav |
| Chat Agents / Applications | `IconSparkles` | `IconSparklesFilled` | Sidebar, Cards, DataTable |
| Autonomous Agents | `IconRobot` | `IconRobotFilled` | Sidebar, Cards, DataTable |
| Traces / Tracing | `IconTimeline` | — | Sidebar, Tabs, Pages |
| Chat Widgets | `IconMessageChatbot` | — | Sidebar, Cards |
| Settings | `IconSettings` | `IconSettingsFilled` | Sidebar |
| Tools / ReACT Dev | `IconTool` | — | Sidebar, Settings |
| Credentials | `IconKey` | — | Settings |
| AI Models | `IconBrain` | — | Settings |
| IAM / Members | `IconUsers` | — | Settings |
| Groups | `IconUsersGroup` | — | Settings |
| Billing | `IconCreditCard` | — | Settings |
| Favorites / Pin | `IconStar` | `IconStarFilled` | DataTable, Dashboard |
| Notifications | `IconBell` | `IconBellFilled` | Header |
| Search | `IconSearch` | — | Header, Toolbar |
| Add / Create | `IconPlus` | — | Buttons |
| Delete | `IconTrash` | — | Menus |
| Edit | `IconPencil` | — | Menus, Buttons |
| External Link | `IconExternalLink` | — | Links |

### 10.2 Icon-Verwendungs-Regeln

1. **Sidebar** — Outline per default, Filled wenn aktiv
2. **DataTable Rows** — Outline, 20px, `color: var(--text-secondary)`
3. **Dashboard Cards** — Outline, 24px, `color: var(--color-primary-500)`
4. **Buttons** — Outline, 18px
5. **Menu Items** — Outline, 16px
6. **Consistent sizing** — Nie Mix aus verschiedenen Größen im gleichen Kontext

### 10.3 Tracing-Icons (Aktuell inkonsistent)

Bisher werden für Tracing verschiedene Icons genutzt. Vereinheitlichung:

| Tracing-Konzept | Icon |
|----------------|------|
| Trace (Container) | `IconTimeline` |
| Span / Node | `IconPointFilled` (farbig nach Status) |
| LLM Call | `IconBrain` |
| Tool Call | `IconTool` |
| Error | `IconAlertTriangle` |
| Success | `IconCheck` |
| Duration / Time | `IconClock` |

---

## 11. Style Consistency Guide

### 11.1 Tabellen / Listen

Alle Listen im System sollen konsistent aussehen:

```
╔══════════════════════════════════════════════════════════════╗
║ Standard DataTable Layout                                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ┌────────────────────────── │ Sort │ Filter │ ⊞  ≡  ║
║  │ 🔍 Search...             │                              ║
║  └──────────────────────────────────────────────────────────║
║                                                              ║
║  ★ ✨ Support Bot        support, faq     Active   ⋯       ║
║  ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──     ║
║  ☆ ✨ FAQ Bot            faq, help        Active   ⋯       ║
║  ☆ ✨ Sales Agent        sales, crm       Inactive ⋯       ║
║  ☆ ✨ Onboarding         hr, onboard      Active   ⋯       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**Regeln**:
- **Row Height**: 60px (consistent überall)
- **Row Padding**: `12px 16px`
- **Row Gap**: 0px (Rows direkt aneinander, getrennt durch 1px Border)
- **Row Hover**: `background: var(--bg-hover)`
- **Row Border**: `border-bottom: 1px solid var(--border-light)`
- **Name Font**: 14px, weight 500, `var(--text-primary)`
- **Description Font**: 13px, weight 400, `var(--text-secondary)`, truncated
- **Tags**: max 3 sichtbar, Rest in Popover; `font-size: 12px`, `radius: full`
- **Status Switch**: Mantine Switch, keine custom Styles
- **Actions Menu**: `IconDotsVertical`, 3-Dot-Menu rechts

### 11.2 Detail-Pages

```
╔══════════════════════════════════════════════════════════════╗
║ Standard Detail Page Layout                                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ← Entity Name                            [Status] [Edit]   ║
║    Description text                                          ║
║    🏷 tag1  🏷 tag2  🏷 tag3                                ║
║  ────────────────────────────────────────────────────────── ║
║  ┌─────────┬──────────┐                                     ║
║  │ Tab 1   │ Tab 2    │                                     ║
║  ├─────────┴──────────┴─────────────────────────────────────║
║  │                                                           ║
║  │  Section Card                                             ║
║  │  ┌──────────────────────────────────────────────────┐    ║
║  │  │ Section Title                                    │    ║
║  │  │ ────────────────────────────────────────────────  │    ║
║  │  │ Field Label          Field Value                 │    ║
║  │  │ Field Label          Field Value                 │    ║
║  │  └──────────────────────────────────────────────────┘    ║
║  │                                                           ║
║  │  Section Card                                             ║
║  │  ┌──────────────────────────────────────────────────┐    ║
║  │  │ Section Title                                    │    ║
║  │  │ ...                                              │    ║
║  │  └──────────────────────────────────────────────────┘    ║
║  │                                                           ║
╚══════════════════════════════════════════════════════════════╝
```

**Regeln**:
- **Back Button**: `IconArrowLeft`, 20px, klick → navigiert zurück
- **Entity Name**: `font-size: 24px`, `weight: 600`
- **Description**: `font-size: 14px`, `color: var(--text-secondary)`, max-width 720px
- **Tags**: Mantine Badge, `variant: light`, `size: sm`
- **Tab Height**: 44px, `font-size: 14px`, `weight: 500`
- **Section Card**: `background: var(--bg-paper)`, `border: 1px solid var(--border-default)`, `radius: 8px`, `padding: 20px`
- **Section Title**: `font-size: 16px`, `weight: 600`, `margin-bottom: 16px`
- **Field Label**: `font-size: 13px`, `weight: 500`, `color: var(--text-secondary)`
- **Field Value**: `font-size: 14px`, `weight: 400`, `color: var(--text-primary)`

### 11.3 Dialoge / Modals

```
╔══════════════════════════════════════════════════════════════╗
║ Standard Dialog Layout                                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Dialog Title                                          ✕     ║
║  ────────────────────────────────────────────────────────── ║
║                                                              ║
║  Form Field Label                                            ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ Input Value                                          │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  Form Field Label                                            ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ Textarea Value                                       │   ║
║  │                                                      │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  ────────────────────────────────────────────────────────── ║
║                                    [Cancel]  [Save]          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**Regeln**:
- **Size**: `lg` (default), `xl` für komplexe Dialoge mit Tabs
- **Radius**: `var(--radius-lg)` (12px)
- **Title**: `font-size: 18px`, `weight: 600`
- **Label**: `font-size: 14px`, `weight: 500`
- **Button-Reihenfolge**: Cancel (subtle/outline) links, Primary Action rechts
- **Gap zwischen Feldern**: `16px` (spacing-md)
- **Footer**: Getrennt durch `border-top: 1px solid var(--border-light)`, `padding-top: 16px`, `margin-top: 24px`

### 11.4 Einheitliche Typography Scale

```
Page Title (h1):      24px, weight 600, line-height 1.2
Section Title (h2):   20px, weight 600, line-height 1.3
Sub-Section (h3):     16px, weight 600, line-height 1.4
Body Text:            14px, weight 400, line-height 1.5
Small Text:           13px, weight 400, line-height 1.5
Caption/Label:        12px, weight 500, line-height 1.4, uppercase optional
Mono/Code:            13px, Fira Code, weight 400
```

### 11.5 Unified Button Styles

```
Primary:    bg primary-600, text white, hover primary-700
Secondary:  bg transparent, border default, text primary, hover bg-hover
Danger:     bg error-600, text white, hover error-700
Ghost:      bg transparent, text secondary, hover bg-hover
Icon:       bg transparent, border none, text secondary, hover bg-hover
            → radius-sm (4px), padding 6px
```

### 11.6 Konsistente Card Styles

```css
/* Standard Card (Section Cards, Dashboard Cards) */
.card {
  background: var(--bg-paper);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);       /* 8px */
  padding: var(--spacing-md);            /* 16px */
}

/* Elevated Card (z.B. hovered, selected) */
.cardElevated {
  background: var(--bg-elevated);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  box-shadow: var(--shadow-sm);
}

/* Interactive Card (klickbar) */
.cardInteractive {
  /* extends .card */
  cursor: pointer;
  transition: all var(--transition-fast) var(--easing-ease-out);
}

.cardInteractive:hover {
  border-color: var(--color-primary-300);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}
```

---

## 12. Daten-Requirements (Backend)

### 12.1 Neue Endpoints (Platform Service)

| Endpoint | Method | Beschreibung | Prio |
|----------|--------|-------------|------|
| `/tenants/{id}/dashboard/stats` | GET | Quick Stats (Counts + Trends) | P1 |
| `/tenants/{id}/users/{uid}/favorites` | GET | **Existiert** — alle Favorites | ✅ |
| `/tenants/{id}/users/{uid}/favorites` | POST/DELETE | **Existiert** — toggle | ✅ |
| `/tenants/{id}/users/{uid}/recent-visits` | GET | Letzte N Visits | P3 (optional) |
| `/tenants/{id}/users/{uid}/recent-visits` | POST | Visit tracken | P3 (optional) |
| `/tenants/{id}/activity-feed` | GET | Activity Events | P3 |
| `/tenants/{id}/notifications` | GET | Notifications Liste | P2 |
| `/tenants/{id}/notifications/{nid}/read` | POST | Als gelesen markieren | P2 |

### 12.2 Dashboard Stats Response

```json
{
  "applications": {
    "total": 12,
    "active": 10,
    "trend": "+2",
    "trend_period": "7d"
  },
  "autonomous_agents": {
    "total": 8,
    "active": 5,
    "trend": "+1",
    "trend_period": "7d"
  },
  "conversations": {
    "total": 156,
    "active_today": 24,
    "trend": "+15%",
    "trend_period": "7d"
  },
  "traces": {
    "total_7d": 1247,
    "error_rate": "2.3%",
    "trend": "+15%",
    "trend_period": "7d"
  }
}
```

### 12.3 Vorhandene Daten die wir nutzen können

| Daten | Quelle | Dashboard-Nutzung |
|-------|--------|-------------------|
| Favorites | `user_favorites` Tabelle | ✅ Favorites Section |
| Application Count | `/applications?limit=0` (Header) | ✅ Quick Stats |
| Agent Count | `/autonomous-agents?limit=0` | ✅ Quick Stats |
| Recent Traces | `/traces?sort=created_desc&limit=5` | ✅ Activity Feed (minimal) |
| User Info | IdentityContext | ✅ Welcome Message |
| Tenant Info | IdentityContext | ✅ Tenant Badge |

---

## 13. Implementierungs-Roadmap

### Phase 1: Layout-System (1-2 Wochen)

```
1.1  Header Height: 70px → 56px
1.2  Sidebar Width: 100px → 80px
1.3  PageContainer entfernen, Full-Width Layout
1.4  MainLayout CSS anpassen (neue Dimensions)
1.5  PageHeader redesign (slim, full-width)
1.6  Alle Pages an neues Layout anpassen
1.7  Responsive Breakpoints implementieren
1.8  CSS Variables für Layout-Dimensions
```

### Phase 2: Style Consistency (1 Woche)

```
2.1  Typography Scale unifizieren
2.2  DataTableRow Styles konsistent machen
2.3  Detail-Page Section Cards vereinheitlichen  
2.4  Dialog Styles standardisieren
2.5  Button Styles vereinheitlichen
2.6  Icon-Mapping vereinheitlichen (siehe §10)
```

### Phase 3: Favorites/Pins (3-5 Tage)

```
3.1  FavoritesContext erstellen
3.2  DataTableRow: Star-Icon inline + optimistic toggle
3.3  ApplicationsPage: Favorites anbinden
3.4  AutonomousAgentsPage: Favorites anbinden
3.5  DataTable: Pinned Items oben sortieren
3.6  SidebarDataList: Favorites markieren
```

### Phase 4: Rendering-Optimierungen (3-5 Tage)

```
4.1  Optimistic Delete Pattern implementieren
4.2  Optimistic Update Pattern implementieren
4.3  React.memo für DataTableRow
4.4  useCallback für Event-Handler
4.5  Delete Animation (Fade-Out)
4.6  Skeleton Loading statt Spinner
```

### Phase 5: Settings-Page Refactor (3-5 Tage)

```
5.1  SettingsSidebar Component erstellen
5.2  TenantSettingsPage auf Sidebar-Layout umbauen
5.3  Tab-Content in separate Sub-Components extrahieren (2000 Zeilen aufbrechen!)
5.4  URL-Routing beibehalten (?tab=xxx)
5.5  Mobile: Sidebar collapsible
```

### Phase 6: Dashboard (1 Woche)

```
6.1  DashboardCard Component
6.2  Quick Stats Section (mit vorhandenen APIs oder neuem Endpoint)
6.3  Favorites Section (aus FavoritesContext)
6.4  Recently Visited Section (localStorage-basiert)
6.5  RecentVisitsContext erstellen
6.6  Visit-Tracking bei Navigation einbauen
6.7  Dashboard Responsive Grid
```

### Phase 7: Last Visited + Notifications (3-5 Tage)

```
7.1  RecentVisitsProvider implementieren
7.2  Visit-Tracking an relevanten Navigation-Points
7.3  Header Notification Badge: hardcoded "2" entfernen
7.4  Minimal Notification Dropdown (letzte Traces als Events)
7.5  (Optional) Backend Endpoints für Notifications
```

---

## Anhang A: Vergleich Vorher/Nachher

### Applications Page

```
VORHER:                                  NACHHER:
┌──────────────────────────────────┐    ┌──────────────────────────────────────────┐
│ HEADER (70px)                    │    │ HEADER (56px)                            │
├──────┬───────────────────────────┤    ├────┬─────────────────────────────────────┤
│      │  ┌────────────────────┐   │    │    │Chat Agents              [+ Create]  │
│ 100  │  │ Chat Agents    [+] │   │    │ 80 │Manage your AI agents                │
│  px  │  │ Description        │   │    │ px │─────────────────────────────────────│
│      │  │ ────────────────── │   │    │    │🔍 Search     │Sort│Filter│          │
│      │  │  ┌──────────────┐  │   │    │    │★ ✨ Support    tags   Active   ⋯   │
│      │  │  │ ✨ Agent 1   │  │   │    │    │☆ ✨ FAQ Bot    tags   Active   ⋯   │
│      │  │  │ ✨ Agent 2   │  │   │    │    │☆ ✨ Sales      tags   Inactive ⋯   │
│      │  │  │ ✨ Agent 3   │  │   │    │    │☆ ✨ Onboard    tags   Active   ⋯   │
│      │  │  └──────────────┘  │   │    │    │                                     │
│      │  │    max 1200px      │   │    │    │   FULL WIDTH — kein Container       │
│      │  └────────────────────┘   │    │    │                                     │
│      │     viel leerer Raum      │    │    │                                     │
└──────┴───────────────────────────┘    └────┴─────────────────────────────────────┘
```

### Dashboard

```
VORHER:                                  NACHHER:
┌──────────────────────────────────┐    ┌──────────────────────────────────────────┐
│ HEADER                           │    │ HEADER                                   │
├──────┬───────────────────────────┤    ├────┬─────────────────────────────────────┤
│      │                           │    │    │Welcome back, Enrico 👋              │
│      │  Welcome Card             │    │    │Here's what's happening in "Tenant"  │
│      │  ┌─────────────────────┐  │    │    │                                     │
│      │  │ Willkommen zurück   │  │    │    │ [12 Agents] [8 Auto] [156] [1.2k]  │
│      │  └─────────────────────┘  │    │    │                                     │
│      │  Tenant Card              │    │    │★ Favorites                          │
│      │  ┌─────────────────────┐  │    │    │ [Card] [Card] [Card] [Card]         │
│      │  │ Current Tenant Info │  │    │    │                                     │
│      │  └─────────────────────┘  │    │    │🕐 Recently Visited                 │
│      │  Available Tenants        │    │    │ [Card] [Card] [Card] [Card]         │
│      │  ┌─────────────────────┐  │    │    │                                     │
│      │  │ Tenant List         │  │    │    │📋 Recent Activity                  │
│      │  └─────────────────────┘  │    │    │ • Invoice Agent completed 3 runs    │
│      │                           │    │    │ • Support Bot conversation started   │
│      │  Next Steps (Static)      │    │    │ • Email Parser trace failed          │
│      │                           │    │    │                                     │
└──────┴───────────────────────────┘    └────┴─────────────────────────────────────┘
```

### Settings Page

```
VORHER:                                  NACHHER:
┌──────────────────────────────────┐    ┌──────────────────────────────────────────┐
│ HEADER                           │    │ HEADER                                   │
├──────┬───────────────────────────┤    ├────┬─────────────────────────────────────┤
│      │                           │    │    │ Tenant Settings                      │
│      │ [Set|IAM|Grp|Cred|AI|..]│    │    │ Manage your tenant configuration     │
│      │ ──────────────────────── │    │    │ ─────────────────────────────────── │
│      │                           │    │    │┌─────────┬──────────────────────────┤
│      │  Content of               │    │    ││ General │ Identity & Access Mgmt.  │
│      │  selected tab             │    │    ││►IAM     │                          │
│      │  (all in 1 component      │    │    ││ Groups  │ Manage who has access    │
│      │   2000+ Zeilen!)          │    │    ││ Creds   │ to this tenant.          │
│      │                           │    │    ││ AI Mod. │                          │
│      │                           │    │    ││ Tools   │ [+ Add Member]           │
│      │  horizontal scroll        │    │    ││ Billing │ ┌──────────────────┐     │
│      │  bei vielen tabs          │    │    ││         │ │ Members Table    │     │
│      │                           │    │    ││         │ └──────────────────┘     │
└──────┴───────────────────────────┘    └────┴─────────┴──────────────────────────┘
```

---

## Anhang B: Neue CSS Custom Properties

```css
:root {
  /* === LAYOUT === */
  --header-height: 56px;
  --sidebar-width: 80px;
  --sidebar-width-mobile: 56px;
  --settings-sidebar-width: 220px;
  
  /* === PAGE === */
  --page-padding-x: 32px;
  --page-padding-y: 24px;
  
  /* === COMPONENTS === */
  --data-table-row-height: 60px;
  --data-table-row-padding: 12px 16px;
  --section-card-padding: 20px;
  --section-card-radius: var(--radius-md);
  --tab-height: 44px;
  
  /* === DASHBOARD === */
  --dashboard-card-min-width: 280px;
  --dashboard-grid-gap: 16px;
  --stats-card-height: 100px;
}
```

---

## Anhang C: Component-Hierarchie (Neu)

```
App
├── AuthProvider
├── FavoritesProvider          ← NEU
├── RecentVisitsProvider       ← NEU
├── IdentityContext
├── SidebarDataContext
│
├── MainLayout
│   ├── Header (56px)
│   │   ├── Logo
│   │   ├── GlobalSearch       ← v0.2.0
│   │   ├── NotificationCenter ← NEU
│   │   ├── ThemeToggle
│   │   └── UserMenu
│   │
│   ├── Sidebar (80px)
│   │   ├── NavItems
│   │   └── SidebarDataList
│   │
│   ├── GlobalChatSidebar
│   │
│   └── <main> (full-width)
│       ├── DashboardPage
│       │   ├── WelcomeSection
│       │   ├── QuickStats         ← NEU
│       │   ├── FavoritesSection   ← NEU
│       │   ├── RecentVisits       ← NEU
│       │   └── ActivityFeed       ← NEU
│       │
│       ├── ApplicationsPage (full-width, no PageContainer)
│       │   ├── PageHeader
│       │   └── DataTable (optimistic updates)
│       │
│       ├── AutonomousAgentsPage (full-width)
│       │   ├── PageHeader
│       │   └── DataTable (optimistic updates)
│       │
│       ├── AutonomousAgentDetailsPage (full-width)
│       │   ├── DetailHeader
│       │   └── Tabs (Traces | Details)
│       │
│       ├── TenantSettingsPage (full-width)
│       │   ├── SettingsHeader         ← NEU
│       │   ├── SettingsSidebar (220px) ← NEU
│       │   └── SettingsContent
│       │       ├── GeneralSettings
│       │       ├── IAMSettings
│       │       ├── GroupsSettings
│       │       ├── CredentialsSettings
│       │       ├── AIModelsSettings
│       │       ├── ToolsSettings
│       │       └── BillingSettings
│       │
│       └── ConversationsPage (custom 3-panel, unchanged)
```

---

## Anhang D: Migration Guide — PageContainer Removal

### Schritt-für-Schritt für jede Page:

```
1. Import entfernen:
   - import { PageContainer } from ...
   
2. JSX ändern:
   VORHER:  <MainLayout><PageContainer>...</PageContainer></MainLayout>
   NACHHER: <MainLayout>...</MainLayout>
   
3. Content-Wrapper hinzufügen (falls nötig für Scrolling):
   <div className={classes.pageContent}>
     <PageHeader ... />
     <DataTable ... />
   </div>

4. CSS Module anpassen:
   .pageContent {
     width: 100%;
     height: 100%;
     display: flex;
     flex-direction: column;
     overflow: hidden;
   }
```

### Betroffene Pages:

| Page | Aktuell | Aktion |
|------|---------|--------|
| ApplicationsPage | `PageContainer` (lg=1200px) | Entfernen |
| AutonomousAgentsPage | `PageContainer` (lg=1200px) | Entfernen |
| AutonomousAgentDetailsPage | `PageContainer` (xl=1400px) | Entfernen |
| TenantSettingsPage | `PageContainer` (lg=1200px) | Entfernen, SettingsSidebar statt |
| ChatWidgetsPage | `PageContainer` (lg=1200px) | Entfernen |
| TracesPage | `PageContainer` | Entfernen |
| DashboardPage | Kein PageContainer | Kein Change nötig |
| ConversationsPage | Kein PageContainer | Kein Change nötig |
---
---

## 14. Comprehensive UI & UX Review

> **Erstellt**: 08. Februar 2026  
> **Methodik**: Vollständige Code-Analyse aller Pages (13), Dialoge (17), Common Components (16), Tracing Components (10), Layout Components (4), Contexts (4). Gesamtumfang: ~20.000 Lines of Code analysiert.

---

### 14.1 Executive Summary

Die Anwendung funktioniert grundsätzlich und löst ihren Kernzweck: Multi-Tenant-Management von AI-Agent-Systemen. Die Architektur ist solide angelegt — Contexts, API-Client, Component-Hierarchie sind da. **ABER**: Es gibt erhebliche technische Schulden, UX-Inkonsistenzen, Fake-UI-Elemente und Code-Duplikation, die die Qualität und Professionalität der Anwendung stark beeinträchtigen.

**Gesamtbewertung: 5.5 / 10**

| Kategorie | Note | Begründung |
|-----------|------|-----------|
| Funktionalität | 7/10 | Kern-Features funktionieren, aber viele TODO-Stubs |
| Code-Qualität | 4/10 | Massive Duplikation, God-Components, 60+ useState in einer Datei |
| UX-Konsistenz | 4/10 | Mixed Languages, Fake-UI, inkonsistente Patterns |
| Visual Design | 6/10 | Login-Page schön, Rest funktional aber "uninspired" |
| Performance | 5/10 | Kein Memoization, Full-Refetch statt Optimistic Updates |
| Accessibility | 3/10 | Minimal — keine aria-labels, keine Keyboard-Navigation |
| Mobile/Responsive | 4/10 | Grundlegende Breakpoints, aber ConversationsPage bricht |
| Error Handling | 3/10 | Silent catches, kein User-Feedback bei vielen Operationen |

---

### 14.2 Kritische Probleme (Must Fix)

#### 14.2.1 Fake UI-Elemente — Vertrauensverlust

Das ist das schwerwiegendste UX-Problem. Drei UI-Elemente im Header täuschen Funktionalität vor, die nicht existiert:

```
┌──────────────────────────────────────────────────────────────────┐
│ 🔷 unified-ui    [🔍 Search...          ]    🔔②  🌙  👤      │
│                       ↑                       ↑                  │
│                  FAKE: Kein onChange,       FAKE: Hardcoded "2", │
│                  kein Handler,             keine Notifications   │
│                  macht nichts               existieren            │
│                                                                  │
│  User Menu:                                                      │
│  ┌────────────────┐                                              │
│  │ Manage Account │ ← FAKE: Kein onClick                        │
│  │ Manage Tenant  │ ← FAKE: Kein onClick                        │
│  │ Manage Licence │ ← FAKE: Kein onClick                        │
│  └────────────────┘                                              │
└──────────────────────────────────────────────────────────────────┘
```

**Impact**: Jeder neue User klickt auf die Suche und denkt sie ist kaputt. Die "2" Notifications erzeugen die Erwartung, dass es was zu sehen gibt — es gibt aber nichts. Die Management-Links sehen klickbar aus, tun aber nichts.

**Empfehlung**: 
- Search-Bar entfernen oder als "Coming Soon" markieren (disabled + tooltip)
- Notification-Bell Badge komplett entfernen bis echte Notifications existieren 
- Management-Links entfernen oder als disabled darstellen mit Tooltip "Coming soon"
- **Grundregel: Nie UI-Elemente anzeigen, die nichts tun**

#### 14.2.2 TODO-Stubs als klickbare Menu-Items

Über mindestens 3 Pages hinweg gibt es Menu-Items im DataTable-Kontext-Menü, hinter denen `console.log()` steht:

| Page | Menu-Item | Implementierung |
|------|-----------|----------------|
| ApplicationsPage | Duplicate | `console.log('Duplicate:', id)` |
| AutonomousAgentsPage | Share | `console.log('Share:', id)` |
| AutonomousAgentsPage | Duplicate | `console.log('Duplicate:', id)` |
| AutonomousAgentsPage | Pin | `console.log('Pin:', id, isPinned)` |
| ChatWidgetsPage | Share | `console.log('Share:', id)` |
| ChatWidgetsPage | Duplicate | `console.log('Duplicate:', id)` |

**Empfehlung**: Menu-Items in `DataTableRow` nur rendern, wenn ein Handler übergeben wird:

```tsx
// VORHER: Immer sichtbar, tut nichts
<Menu.Item onClick={() => onDuplicate?.(item.id)}>Duplicate</Menu.Item>

// NACHHER: Nur wenn Handler existiert
{onDuplicate && (
  <Menu.Item onClick={() => onDuplicate(item.id)}>Duplicate</Menu.Item>
)}
```

#### 14.2.3 Silent Error Handling

An zahlreichen Stellen werden Fehler verschluckt, ohne dem User Feedback zu geben:

```typescript
// AutonomousAgentDetailsPage.tsx L174
catch {} // "Silently handle — could show notification"

// ApplicationsPage L230 — Delete-Fehler
catch (error) { console.error('Error deleting:', error); }
// → Dialog bleibt offen, User bemerkt nichts

// Alle Create-Dialoge:
catch { /* Error handling is done by the API client */ }
// → Wenn der API-Client crash't, sieht der User nichts
```

**Impact**: User klickt "Delete", wartet, nichts passiert. Oder schlimmer: User denkt es hat funktioniert, aber es hat nicht.

**Empfehlung**: 
- Mantine `notifications.show()` bei JEDEM fehlerhaften API-Call
- Bei Delete: Dialog schließen + Error-Toast: "Failed to delete. Please try again."
- Bei Create: Error inline im Dialog anzeigen (Alert-Component über dem Submit-Button)

#### 14.2.4 Sprach-Chaos (i18n)

Die App ist ein Mix aus Deutsch und Englisch. Kein i18n-Framework vorhanden.

| Datei | Deutsche Strings |
|-------|-----------------|
| DashboardPage | "Willkommen zurück", "Lade Dashboard...", "Benutzer", "Aktueller Tenant", "Verfügbare Tenants" |
| LoginPage | "Willkommen", "Melde dich an...", "Mit Microsoft anmelden", "Integration verschiedener AI-Agent-Systeme" |
| Header | "Kein Tenant", "Keine Tenants verfügbar", "Tenant auswählen" |
| EditCredentialDialog | "Neuer API Key", "Leer lassen um den aktuellen Wert beizubehalten" |
| SidebarDataList | "Suchen..." |
| IdentityContext | "Fehler", "Erfolg" |
| SidebarDataContext | "Fehler beim Laden der Chat Agents" |
| AutonomousAgentDetailsPage | Diverse Notification-Messages |

**Empfehlung für v0.1.0**: Alles auf Englisch vereinheitlichen (kein i18n-Framework nötig, einfach die Strings ersetzen). i18n-Framework (z.B. `react-i18next`) erst für v0.3.0+ wenn Multi-Language wirklich gebraucht wird.

---

### 14.3 Architektur-Probleme (Refactoring nötig)

#### 14.3.1 God-Component: TenantSettingsPage (2001 Zeilen)

Dies ist der größte einzelne Code-Smell in der gesamten Anwendung.

```
TenantSettingsPage.tsx — 2001 Zeilen
├── ~60 useState hooks
├── ~15 useEffect hooks
├── ~25 Callback-Handler
├── ~12 Dialog open/close-Paare
├── 4x kopierter IntersectionObserver-Code
├── 5x kopiertes CRUD-Table-Pattern
├── 7 Tab-Panels (je ~200-300 Zeilen inline JSX)
└── 1 CSS-Klasse (.customGroupRow) für 4 verschiedene Entity-Typen
```

**Empfehlung — Aufbrechen in 7 Dateien + 1 Shared Hook**:

```
TenantSettingsPage/
├── TenantSettingsPage.tsx       (~80 Zeilen — Shell mit Sidebar)
├── GeneralSettingsTab.tsx       (~200 Zeilen)
├── IAMSettingsTab.tsx           (~300 Zeilen)
├── CustomGroupsTab.tsx          (~250 Zeilen)
├── CredentialsTab.tsx           (~250 Zeilen)
├── AIModelsTab.tsx              (~250 Zeilen)
├── ToolsTab.tsx                 (~250 Zeilen)
├── BillingTab.tsx               (~100 Zeilen)
└── hooks/
    └── useCrudTable.ts          (~120 Zeilen — search, sort, fetch, IntersectionObserver)
```

**Geschätztes Ergebnis**: 7 Dateien à 100-300 Zeilen statt 1 Datei à 2001 Zeilen. `useCrudTable` Hook eliminiert 4x kopierten IntersectionObserver-Code und 5x kopiertes Fetch-Pattern.

#### 14.3.2 List-Page Triple-Duplication

`ApplicationsPage`, `AutonomousAgentsPage`, `ChatWidgetsPage` sind ~90% identisch:

```
Identischer Code (in allen 3 Dateien):
├── getStoredSort() — localStorage-basiertes Sort-Persistence
├── getSortParams() — Sort-String zu API-Params Mapping
├── fetchTags() — Tag-Autocomplete laden
├── fetchEntities() — Paginated Fetch mit debounced Search
├── handleLoadMore() — Infinite-Scroll Callback
├── handleSearchChange() — Debounced Search Handler
├── handleSortChange() — Sort mit localStorage-Persistence
├── handleFilterChange() — Filter State Management
├── handleStatusChange() — Toggle Active/Inactive
├── handleDeleteConfirm() — Delete mit Refetch
├── 5x useEffect für Search/Sort/Filter/Tags
└── JSX: MainLayout > PageContainer > PageHeader + DataTable
```

**Empfehlung — Custom Hook `useEntityList`**:

```typescript
const {
  items, isLoading, isLoadingMore, hasMore, error,
  tags, searchValue, sortBy, filters,
  handleSearch, handleSort, handleFilter, handleLoadMore,
  handleDelete, handleStatusChange, refetch
} = useEntityList({
  entityType: 'applications',
  fetchFn: (params) => apiClient.listApplications(tenantId, params),
  fetchTagsFn: (search) => apiClient.listTags(tenantId, 'application', search),
  storageKey: 'applications-sort',
});
```

Dadurch schrumpfen alle 3 Pages auf ~80-100 Zeilen (nur noch JSX + Entity-spezifische Handler wie `handleOpen`).

#### 14.3.3 ConversationsPage — 933 Zeilen Orchestrator

Die ConversationsPage enthält SSE-Streaming-Logik, Conversation-CRUD, Message-State, Tracing-Verknüpfung und Drag-and-Drop in einer Datei.

**Empfehlung — Zerlegung in Custom Hooks**:

```
ConversationsPage/
├── ConversationsPage.tsx           (~200 Zeilen — Layout + Wiring)
├── hooks/
│   ├── useChat.ts                  (~250 Zeilen — SSE, Streaming, Messages)
│   ├── useConversationList.ts      (~150 Zeilen — Conversations laden, filtern, CRUD)
│   ├── useConversationTracing.ts   (~80 Zeilen — Trace laden, Node-Mapping)
│   └── useConversationDragDrop.ts  (~50 Zeilen — File Drag & Drop State)
├── components/
│   ├── ChatSidebar/
│   ├── ChatHeader/
│   ├── ChatContent/
│   └── ChatInput/
```

#### 14.3.4 Dialog-Duplikation — IAM-Boilerplate

Die Edit-Dialoge haben einen `details | iam`-Tab-Pattern. Die IAM-Tab-Logik ist:
- In `EditApplicationDialog` **manuell** implementiert (~200 Zeilen Inline-Code für Permission-Loading/Updating)
- In allen anderen Edit-Dialogen über den `useEntityPermissions` Hook gelöst

**Problem**: `EditApplicationDialog` ist mit 936 Zeilen der größte Dialog — hauptsächlich weil es die IAM-Logik dupliziert, die in einem fertigen Hook existiert.

---

### 14.4 UX-Probleme im Detail

#### 14.4.1 Conversations-Page

| Problem | Impact | Lösung |
|---------|--------|--------|
| File-Upload UI existiert, aber `handleUploadFiles` ist TODO | User zieht Dateien rein → nichts passiert | Upload entweder implementieren oder UI entfernen |
| `setTimeout(1500ms)` für Trace-Refresh nach Message | Fragiler Workaround | Backend-seitig lösen oder Polling mit Retry |
| Sidebar Conversations Limit: 100 (hardcoded) | User mit >100 Conversations sehen nicht alle | Infinite Scroll für Sidebar oder expliziter Hinweis |
| Streaming-Fehler entfernt auch die User-Nachricht | User verliert seinen getippten Text | User-Nachricht beibehalten, nur AI-Antwort als Error markieren |
| Kein Mobile-Layout | Sidebar und Chat überlappen auf <768px | Sidebar als Overlay/Drawer auf Mobile |
| Kein Scroll-to-Bottom-Button | User muss manuell nach unten scrollen bei langen Chats | Floating "↓ New messages" Button |

#### 14.4.2 DataTable

| Problem | Impact | Lösung |
|---------|--------|--------|
| Filter erfordern "Apply Filters" Button | Ungewöhnlich, User erwartet Live-Filter | Live-Filter bei Änderung (mit Debounce für Server-side) |
| `onShare` Prop wird akzeptiert aber nie gerendert | Verwirrend für Entwickler, Dead Code | Share-Menu-Item rendern oder Prop entfernen |
| Alle Menu-Items immer sichtbar | Klickbare Items die nichts tun | Conditional Rendering basierend auf Handler-Prop |
| Kein Multi-Select | Bulk-Aktionen (Delete, Tag, Status) nicht möglich | Checkbox-Column + Bulk-Action-Bar |
| Kein Column-Resize | Feste Spaltenbreiten | Nice-to-have für v0.2.0+ |
| Kein Export (CSV/JSON) | Daten können nicht exportiert werden | Nice-to-have |

#### 14.4.3 Tracing-System

Das Tracing-System ist mit ~4.500 Zeilen die komplexeste Feature-Area. Hauptprobleme:

| Problem | Impact |
|---------|--------|
| `TracingCanvasView` ist 974 Zeilen | Unmöglich zu warten, enthält Rendering + Interaction + Layout |
| `TracingHierarchyView` ist 779 Zeilen | Gleiches Problem |
| `centerOnNode` ist ein No-Op | State wird gesetzt, aber nie gelesen |
| Traces-Page ist ein "Coming Soon" Platzhalter | Navigation zu Traces führt zu leerer Seite |
| N8N-Tracing-Algorithmus "eher fehlerhaft" (eigene Einschätzung im TODO) | Falsche Darstellung von Traces |

#### 14.4.4 Tenant-Switching

```
Aktuell:
  User wählt neuen Tenant → localStorage.setItem('selectedTenant', newId)
                           → window.location.reload()  ← BRUTE FORCE
                           → Alle States weg
                           → Alle SSE-Connections weg
                           → Full Page Reload + Re-Auth
                           → Flash of Content
```

**Moderner Ansatz**:
```
Besser:
  User wählt neuen Tenant → Context-Update (selectedTenant)
                           → Alle Data-Contexts invalidieren (clear + refetch)
                           → Keine Page Navigation
                           → Kein Reload
                           → Smooth Transition mit Loading-Skeleton
```

---

### 14.5 visual Design Critique

#### 14.5.1 Was gut ist

- **Login-Page**: Visuell die stärkste Page — Glassmorphism, animierte Gradients, floating Icons, responsive. Zeigt was möglich ist.
- **Design-Tokens**: Durchdachtes CSS-Variable-System mit Dark Mode Support. Semantic Variables (`--bg-paper`, `--text-primary`) auto-switchen.
- **DataTable-Rows**: Cleanes Card-Design mit Hover-States, konsistente Tag-Badges.
- **Tracing-Visualisierung**: Impressive Canvas-basierte Node-Darstellung mit Zoom/Pan.
- **Dark Mode**: Funktioniert überall, keine gebrochenen Styles.

#### 14.5.2 Was fehlt / besser sein könnte

| Aspekt | Ist-Zustand | Sollte |
|--------|-------------|--------|
| **Micro-Interactions** | Keine Animationen bei State-Changes | Subtle Fade/Slide für List-Item-Erscheinen/Verschwinden |
| **Empty States** | Generisches "No items found" | Illustrierte Empty States mit CTA ("Create your first agent →") |
| **Skeleton Loading** | Nur Spinner (Mantine `Loader`) | Content-shaped Skeletons (Layout bleibt stabil) |
| **Success Feedback** | Kein Feedback nach Create | Success-Toast: "Agent created successfully" + Link zum neuen Item |
| **Breadcrumbs** | Nicht einheitlich | Breadcrumb-Trail auf Detail-Pages: `Agents > Invoice Agent > Traces` |
| **Page Transitions** | Hard-Cut bei Navigation | Subtle Fade-Transition (Framer Motion oder CSS) |
| **Data Visualization** | Keine Charts/Graphs | Dashboard: Mini-Sparklines in Stats-Cards, Trace-Count-Trend-Chart |
| **Color-Coding** | Status nur als Switch | Status-Dots (🟢🔴🟡) neben Entity-Namen + farbige Row-Left-Border |
| **Avatars/Icons** | Alle Entities haben gleiche Icons | Entity-spezifische farbige Avatare (Initiale + Farbe basierend auf Name-Hash) |

#### 14.5.3 Entity-Avatare (Vorschlag)

Statt generischer Icons für alle Agents, könnte jede Entity einen generierten Avatar bekommen:

```
AKTUELL:                           VORSCHLAG:
┌──────────────────────┐           ┌──────────────────────┐
│ ✨ Support Bot       │           │ 🟦SB  Support Bot    │
│ ✨ Sales Agent       │           │ 🟩SA  Sales Agent    │
│ ✨ FAQ Helper        │           │ 🟪FH  FAQ Helper     │
└──────────────────────┘           └──────────────────────┘
   Alle gleich!                       Visuell unterscheidbar
```

Farbe wird aus dem Entity-Namen per Hash generiert → konsistent, keine Konfiguration nötig. Schema: `hsl(hash(name) % 360, 70%, 50%)`.

---

### 14.6 Feature-Bewertung & Priorisierung

#### Essentielle Features (v0.1.0 — vor Release)

| # | Feature | Begründung | Aufwand |
|---|---------|-----------|---------|
| 1 | **Fake-UI entfernen** | Vertrauensverlust, unprofessionell | 1h |
| 2 | **Sprache vereinheitlichen (→ Englisch)** | Inkonsistenz verwirrt User | 2-3h |
| 3 | **Error-Handling verbessern** | User braucht Feedback bei Fehlern | 1 Tag |
| 4 | **TODO-Stubs entfernen oder implementieren** | Klickbare No-Ops sind Bugs | 2-4h |
| 5 | **Full-Width Layout** (Konzept §3) | Layout verschwendet 40% Platz | 1-2 Tage |
| 6 | **TenantSettingsPage aufbrechen** | 2001 Zeilen sind unwartbar | 2-3 Tage |
| 7 | **List-Page-Deduplication** | 90% Code-Kopie über 3 Files | 1-2 Tage |
| 8 | **Favorites/Pins anbinden** | Backend existiert, nur Frontend fehlt | 1-2 Tage |
| 9 | **Settings Sidebar** (Konzept §8) | Horizontale Tabs skalieren nicht | 1-2 Tage |
| 10 | **Optimistic Updates** (Konzept §9) | Flicker-Free Delete/Update | 2-3 Tage |

#### Wichtige Features (v0.1.0 — sollte rein)

| # | Feature | Begründung | Aufwand |
|---|---------|-----------|---------|
| 11 | **Dashboard redesign** (Konzept §4) | Home-Page hat null Mehrwert | 3-5 Tage |
| 12 | **Skeleton Loading** | Professioneller als Spinner | 1-2 Tage |
| 13 | **Last Visited** (Konzept §6) | Personalisierte Navigation | 1-2 Tage |
| 14 | **Empty States mit CTAs** | Bessere Onboarding-UX | 1 Tag |
| 15 | **Conversations Mobile-Fix** | Chat-Page bricht auf Mobile | 1-2 Tage |
| 16 | **Notification Badge Fix** (mindestens entfernen) | Fake-Badge | 30 min |
| 17 | **Tenant-Switching ohne Reload** | Bessere UX | 1-2 Tage |

#### Nice-to-Have (v0.2.0+)

| # | Feature | Begründung | Aufwand |
|---|---------|-----------|---------|
| 18 | **Command Palette (⌘K)** | Power-User Navigation (wie Linear, VS Code) | 2-3 Tage |
| 19 | **Keyboard Shortcuts** | Schnellere Bedienung (`N` = New, `E` = Edit, `/` = Search) | 2-3 Tage |
| 20 | **Bulk Actions (Multi-Select)** | Mehrere Agents auf einmal löschen/taggen | 2-3 Tage |
| 21 | **i18n Framework** | Multi-Language Support | 3-5 Tage |
| 22 | **Trace-Page implementieren** | Standalone Trace-Browser | 3-5 Tage |
| 23 | **Entity Avatare** (farbige Initialen) | Visuelle Unterscheidbarkeit | 1 Tag |
| 24 | **Data Export (CSV/JSON)** | Admin-Feature | 1-2 Tage |
| 25 | **Activity Feed** | Dashboard-Section + eigene Page | 3-5 Tage |
| 26 | **Page Transitions** | Smooth Navigation | 1 Tag |
| 27 | **Virtualisierte Listen** (react-window) | Performance bei 100+ Items | 1-2 Tage |
| 28 | **Breadcrumb Navigation** | Orientierung in der App | 1 Tag |
| 29 | **onboarding Flow** (Tour, Tooltips) | Neuen Usern helfen | 2-3 Tage |
| 30 | **Fullscreen Chat Widget Preview** | Designer-Page lebendig machen | 3-5 Tage |

---

### 14.7 Ideen & Feature-Vorschläge

#### 14.7.1 Command Palette (⌘K / Ctrl+K)

Wie in Linear, VS Code, Vercel — eine globale Suchleiste die ALLES kann:

```
┌──────────────────────────────────────────────────────┐
│ 🔍 Search entities, commands, settings...            │
├──────────────────────────────────────────────────────┤
│ RECENT                                               │
│   🤖 Invoice Agent                    Auto Agent     │
│   ✨ Support Bot                      Application    │
│                                                      │
│ COMMANDS                                             │
│   ➕ Create Application                              │
│   ➕ Create Autonomous Agent                         │
│   ⚙️  Open Settings                                  │
│   🌙 Toggle Dark Mode                               │
│                                                      │
│ NAVIGATION                                           │
│   📄 Applications                                    │
│   📄 Conversations                                   │
│   📄 Traces                                          │
└──────────────────────────────────────────────────────┘
```

- Ersetzt den aktuellen (fake) Suchbalken im Header
- Sucht über alle Entities (Applications, Agents, Conversations, Credentials)
- Quick-Commands: Create, Navigation, Settings, Theme Toggle
- Recent Searches + Recent Visits integriert
- **Aufwand**: ~2-3 Tage (Library: `cmdk` oder `kbar`)
- **Impact**: Enorme Produktivitätssteigerung für Power User

#### 14.7.2 Status Dashboard mit Mini-Sparklines

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   ✨ 12          │  │   🤖 8           │  │   💬 156         │
│   Chat Agents    │  │   Auto Agents    │  │   Convos (7d)    │
│                  │  │                  │  │                  │
│   ▁▂▃▄▅▆▇  +2   │  │   ▇▆▅▄▃▂▁  -1   │  │   ▁▂▂▃▅▇▇  +24  │
│                  │  │                  │  │                  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

Mini-Sparklines (7-Tage-Trend) direkt in den Stats-Cards. Keine Chart-Library nötig — kann mit SVG-Polylines oder CSS-Gradients gebaut werden.

#### 14.7.3 Contextual Action Bar

Statt Actions nur im 3-Dot-Menu zu verstecken, eine kontextuelle Action-Bar bei Hover über eine Tabellenzeile:

```
  ✨ Support Bot      support, faq      Active     [ ✏️  📋  🗑  ★ ]
                                                        ↑
                                               Erscheint nur bei Hover
                                               (wie in Gmail, Linear)
```

#### 14.7.4 Inline-Editing bei Entity-Details

Statt immer einen Dialog zu öffnen, könnten einfache Felder (Name, Description) direkt inline editierbar sein:

```
AKTUELL:
  Name: Support Bot  [✏️ Edit] → öffnet 10-Feld Dialog

VORSCHLAG:
  Name: Support Bot  [✏️] → Feld wird inline editierbar
  Description: This bot handles... [✏️] → Inline Textarea
  
  Für komplexe Felder (Type, Tags, Credentials): weiterhin Dialog
```

#### 14.7.5 Agent Health / Status Overview

Für die DetailPage eines Autonomous Agent: eine Health-Übersicht mit den letzten N Runs:

```
── Health ─────────────────────────────────────────────
  Last 24h:  🟢🟢🟢🔴🟢🟢🟡🟢🟢🟢🟢🟢  92% success
  Avg Duration: 4.2s
  Error Rate: 8% (↓ from 12% last week)
```

#### 14.7.6 Conversation Insights

Auf der Conversations-Page: eine Mini-Statistik über dem Chat:

```
── This Conversation ──────────────────────────
  Messages: 24 │ Duration: 12 min │ Tokens: ~3.2k
```

#### 14.7.7 Quick-Actions in Sidebar

Rechtsklick auf Sidebar-Items für Quick-Actions:

```
  ✨ Chat Agents
     ┌────────────────────┐
     │ 📋 Copy ID         │
     │ ✏️  Edit            │
     │ 🔗 Copy Link       │
     │ ★  Pin to Dashboard│
     │ 🗑  Delete          │
     └────────────────────┘
```

#### 14.7.8 Drag & Drop Reordering für Dashboard

Pinned Items auf dem Dashboard per Drag & Drop umsortierbar. Position wird in localStorage persisted.

---

### 14.8 Conversations-Page Deep Review

Die Conversations-Page ist die Kern-Interaktionsfläche der Anwendung — hier verbringt der User die meiste Zeit. Sie verdient besondere Aufmerksamkeit.

#### Positives

- SSE-Streaming funktioniert mit schönem Typewriter-Effekt
- Conversation-Sidebar mit intelligenter Gruppierung (time-based + app-based)
- Tracing-Integration: direkt vom Chat zur Trace-Visualisierung
- Favorites/Pin für Conversations funktioniert
- Auto-generated Conversation Titles (AI)

#### Probleme & Verbesserungsvorschläge

```
AKTUELLES LAYOUT:
┌──────────────┬──────────────────────────────┬──────────────┐
│              │                              │              │
│  Chat List   │  Chat Area                   │  Tracing     │
│  (280px)     │  (flex: 1)                   │  Sidebar     │
│              │                              │  (320px)     │
│  - Nur       │  - Kein "Scroll to Bottom"   │              │
│    Client-   │  - Fehler löscht User-Msg    │  - Nur bei   │
│    Side      │  - File Upload ist Fake      │    Trace     │
│    Filter    │  - Kein Typing-Indicator     │    aktiv     │
│  - Max 100   │  - Kein Message-Edit         │              │
│    Convos    │  - Kein Message-Delete       │              │
│  - Kein      │  - Kein Code-Copy-Button     │              │
│    Infinite  │    in Code-Blocks             │              │
│    Scroll    │                              │              │
│              │                              │              │
└──────────────┴──────────────────────────────┴──────────────┘
```

**Fehlende Standard-Chat-Features**:

| Feature | Status | Prio |
|---------|--------|------|
| Scroll-to-Bottom Button | ❌ | P1 |
| Code-Block Copy Button | ❌ | P1 |
| Message Retry (bei Error) | ❌ | P1 |
| Typing Indicator (3 Dots während Streaming) | ⚠️ Teilweise (StreamingDots) | P2 |
| Message Edit | ❌ | P3 |
| Message Delete | ❌ | P3 |
| Conversation Export (Markdown/PDF) | ❌ | P3 |
| Image Preview in Chat | ❌ | P3 |
| Code Execution Preview | ❌ | Future |
| Voice Input | ❌ | Future |

---

### 14.9 Gesamtkonzept-Review — Architektonische Bedenken

#### 14.9.1 Context-Architektur

```
AKTUELL:
  App
  ├── IdentityContext (user, tenants, apiClient)
  ├── SidebarDataContext (entity lists for sidebar)
  ├── ChatSidebarContext (möglicherweise Dead Code)
  └── AICapabilitiesContext (feature flags)
```

**Probleme**:
- `IdentityContext` enthält den API-Client → **jede Änderung am Identity-State triggert Re-Renders in jeder Komponente die den apiClient nutzt**, obwohl sich der apiClient nie ändert
- `SidebarDataContext` lädt ALLE Entities mit limit: 999 → skaliert nicht
- `ChatSidebarContext` scheint nicht genutzt zu werden

**Empfehlung**:
```
BESSER:
  App
  ├── AuthContext (nur auth state: user, tokens)
  ├── TenantContext (selectedTenant, tenants, switchTenant)
  ├── ApiClientContext (apiClient — stabil, keine Re-Renders)
  ├── FavoritesContext (favorites state)
  ├── RecentVisitsContext (last visited tracking)
  ├── NotificationsContext (notification state)
  └── SidebarContext (sidebar entity caches)
```

Trennung von Auth, Tenant und ApiClient verhindert unnötige Re-Renders.

#### 14.9.2 Form-Validierung

Die App nutzt `@mantine/form` mit `useForm`, aber die Validierung ist inkonsistent:

| Dialog | Client-Side Validation | Server-Side Errors shown |
|--------|----------------------|-------------------------|
| CreateApplicationDialog | ✅ Name, URL Pattern, Ranges | ❌ |
| CreateAutonomousAgentDialog | ✅ Name, URL Pattern | ❌ |
| CreateChatWidgetDialog | ✅ Name | ❌ |
| CreateCredentialDialog | ✅ Name | ❌ |
| CreateCustomGroupDialog | ⚠️ Name (ohne Asterisk) | ❌ |
| CreateToolDialog | ✅ Name | ❌ |
| AIModelDialog | ⚠️ Nur HTML required | ❌ |

**Kein Dialog zeigt Server-Side-Validation-Errors an.** Wenn der Server einen 422 (Validation Error) zurückgibt, wird nur der globale Toast gezeigt — die Field-Level-Errors werden nicht auf die entsprechenden Formular-Felder gemappt.

#### 14.9.3 Performance-Risiken

1. **Kein React.memo**: DataTableRow wird bei jedem State-Change des Parents neu gerendert — bei 50+ Items in der Liste = 50 unnötige Re-Renders pro Keystroke in der Suche
2. **TenantSettingsPage rendert alle 7 Tabs**: Auch nicht-aktive Tabs werden gerendert (inkl. deren Effects und IntersectionObservers)
3. **SidebarDataContext limit: 999**: Bei Tenants mit vielen Entities wird initial eine sehr große Response geladen
4. **TracingContext `JSON.stringify` Vergleich**: O(n) String-Comparison auf potentiell großen Trace-Objekten bei jedem Render

---

### 14.10 Gesamt-Fazit & Empfehlung

Die Anwendung hat ein **solides Foundation** — die Core-Features funktionieren, das Design-Token-System ist durchdacht, Dark Mode funktioniert, die API-Abstraktion ist sauber. Das Trace-Visualization-System ist beeindruckend.

Aber sie braucht **Polishing und Konsolidierung** bevor sie als professionelles Produkt wahrgenommen wird:

1. **Sofort** (vor v0.1.0): Fake-UI entfernen, Sprache vereinheitlichen, Error-Handling fixen, TODO-Stubs aufräumen
2. **Layout-Refactoring** (v0.1.0): Full-Width, Settings-Sidebar, TenantSettings aufbrechen, List-Page-Deduplication
3. **UX-Features** (v0.1.0): Dashboard, Favorites, Optimistic Updates, Skeleton Loading
4. **Power-User-Features** (v0.2.0): Command Palette, Keyboard Shortcuts, Bulk Actions, Activity Feed
5. **Conversations-Polish** (v0.2.0): Scroll-to-Bottom, Code-Copy, Message-Retry, Mobile-Fix, File-Upload

Die vorgeschlagenen Refactorings aus §3-§13 dieses Dokuments sind **fundiert und notwendig**. Zusätzlich empfehle ich die in §14.2-14.4 identifizierten kritischen Probleme als **P0** vor allen Feature-Additions zu beheben — sie beeinträchtigen das Vertrauen der User in die Anwendung mehr als fehlende Features.