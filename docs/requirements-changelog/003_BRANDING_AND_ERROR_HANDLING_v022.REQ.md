# 003 — Branding, Error Handling & List Polish v0.22

> **Status:** DRAFT  
> **Scope:** unified-ui-frontend-service  
> **Goal:** Fix FE crashes from legacy widget data, implement OSS-friendly branding system with theme presets, polish list layouts

---

## Arbeitsweise & Prozess

> **Dieses Dokument ist das zentrale Tracking- und Anforderungsdokument.**  
> Es gibt keine separate Implementierungsplan-Datei. Alles wird hier gesteuert.

### Ablauf pro Paket (0, 1, 2, …)

1. **Implementierungsübersicht**: Copilot liest den relevanten Code ein und erstellt eine kompakte Übersicht: welche Dateien betroffen sind, welcher Ansatz gewählt wird, bei Design-Paketen konkrete Varianten mit Empfehlung.
2. **Review**: Nutzer prüft die Übersicht, gibt OK oder Korrekturen.
3. **Implementierung**: Copilot implementiert das **gesamte Paket** (alle Teilpakete zusammen, nicht einzeln).
4. **Testhinweise**: Copilot zeigt nach Implementierung kurz auf, was der Nutzer manuell testen soll (Stichpunkte).
5. **Test & Feedback**: Nutzer testet die Implementierung und gibt Anpassungswünsche.
6. **Abschluss**: Paket wird als `✅ Done` im Titel markiert → weiter zum nächsten Paket.

### Status-Tracking

Jedes Paket bekommt einen Status-Marker im Titel:
- *(kein Marker)* → Noch nicht begonnen
- `⏳ In Progress` → Gerade in Bearbeitung
- `✅ Done` → Fertig implementiert und abgenommen

### Regeln

- Immer ein **komplettes Paket** als Einheit bearbeiten (nicht Teilpakete einzeln).
- Bei Design-Entscheidungen werden konkrete Optionen mit CSS-Beispielen gezeigt → Nutzer wählt vor der Implementierung.
- Dieses Dokument kann in jeder neuen Session als Kontext geladen werden, um den aktuellen Stand und nächsten Schritt zu kennen.
- Nach **jedem Paket**: `pre-commit run --all-files` ausführen und alle Fehler fixen.

---

## Pakete

### Paket 0: ✅ Done — FE Error Handling — Graceful Degradation

> Aktuell crasht die gesamte Conversation Page wenn alte Widget-Daten (z.B. RangeSlider mit ungültigen Werten) gerendert werden. Wir brauchen eine ErrorBoundary + defensive Validierung im FormWidget.

**Root Cause:**
- `RangeSlider` in `FormWidget.tsx` erhält `value` das kein `[number, number]` Array ist
- Error: `Uncaught TypeError: value.toFixed is not a function`
- Alte Chat-Widget-Versionen haben andere Datenstrukturen

**Context & Research:**
- Affected: `src/components/chat/widgets/FormWidget/FormWidget.tsx` (Zeilen 535-543)
- Aktuell keine `ErrorBoundary` im Projekt vorhanden
- Pattern: Defensive value parsing + Catch-all ErrorBoundary für Widget-Rendering

#### 0.1 ErrorBoundary Komponente

| ID | Anforderung |
|----|-------------|
| 0.1.1 | Neue `WidgetErrorBoundary` Komponente in `src/components/common/` erstellen |
| 0.1.2 | Bei Render-Error: "Widget could not be rendered" als UI anzeigen (nicht crash) |
| 0.1.3 | Original Error als `console.warn()` loggen für Debugging |
| 0.1.4 | ErrorBoundary um alle Widget-Renderungen in Chat wrappen |

#### 0.2 Defensive Value Parsing

| ID | Anforderung |
|----|-------------|
| 0.2.1 | In `FormWidget.tsx`: RangeSlider value validieren bevor Rendering |
| 0.2.2 | Wenn value ungültig (nicht `[number, number]`): Default `[min, max]` verwenden |
| 0.2.3 | Analog für andere anfällige Felder: Slider, Rating (value muss Nummer sein) |

---

### Paket 1: Branding Konzept — OSS-Friendly Architecture

> OpenSource-Nutzer sollen das Repo clonen und ihr eigenes Branding verwenden können, ohne den Source Code zu ändern. Wir definieren hier das Konzept.

**Ziele:**
- Logo/Icon/Favicon als Custom Files (`.gitignore`-freundlich)
- App Title per Environment Variable
- Theme Presets (Farbschemata) per Environment Variable auswählbar
- "powered by unified-ui" Subtitle bei custom titles

#### 1.1 Environment Variables

| ID | Anforderung |
|----|-------------|
| 1.1.1 | `VITE_APP_TITLE` — App Title (default: "unified-ui") |
| 1.1.2 | `VITE_THEME_PRESET` — Theme Auswahl (default: "default") |
| 1.1.3 | `VITE_BRANDING_SLUG` — Branding Ordner Slug (default: "default") |
| 1.1.4 | Alle Env Vars optional mit sinnvollen Defaults |

#### 1.2 Custom Asset Files & Lookup-Reihenfolge

| ID | Anforderung |
|----|-------------|
| 1.2.1 | **Asset-Lookup Reihenfolge (3-stufig):** |
|       | 1. Konfigurierter Branding-Ordner (z.B. `emtec`) wenn `VITE_BRANDING_SLUG` gesetzt |
|       | 2. Custom files in `/public/branding/default/` (`{name}.custom.{ext}`) |
|       | 3. Default files in `/public/branding/default/` (`{name}.{ext}`) — Fallback |
| 1.2.2 | Unterstützte Formate: `.svg`, `.png`, `.jpg`, `.webp` |
| 1.2.3 | Assets: `icon`, `logo`, `favicon` |
| 1.2.4 | `.gitignore` Eintrag: `public/branding/default/*.custom.*` |
| 1.2.5 | `README.md` in `/public/branding/` mit Anleitung für OSS-Nutzer |
| 1.2.6 | `asklepios` Branding-Ordner löschen, `emtec` bleibt als Beispiel |

#### 1.3 Theme Presets

| ID | Anforderung |
|----|-------------|
| 1.3.1 | Theme Preset Definitionen in `src/theme/presets/` |
| 1.3.2 | Presets: `default` (blue), `ocean` (teal), `forest` (green), `sunset` (orange), `purple` |
| 1.3.3 | Jedes Preset definiert: primary color palette, optional secondary |
| 1.3.4 | **Alle Presets müssen Dark Mode und Light Mode unterstützen** |
| 1.3.5 | Theme wird zur Build-Zeit basierend auf `VITE_THEME_PRESET` gewählt |
| 1.3.6 | **Theme Presets beeinflussen auch Login Page** (bgLeft, bgRight als passende Gradient-Varianten) |
| 1.3.7 | Login-spezifische Overrides weiterhin möglich in `branding.config.ts` |

#### 1.4 App Header Branding

| ID | Anforderung |
|----|-------------|
| 1.4.1 | Header Icon: Aus Branding Assets laden statt hardcoded `IconBrain` |
| 1.4.2 | Header Title: Aus `VITE_APP_TITLE` laden |
| 1.4.3 | Wenn Title ≠ "unified-ui": Subtitle "powered by unified-ui" rechtsbündig darunter |
| 1.4.4 | Subtitle erscheint sowohl im **App Header** als auch im **Login Header** |
| 1.4.5 | Favicon (`index.html`): Dynamisch aus Branding Assets |

#### 1.5 Branding Config Refactoring

| ID | Anforderung |
|----|-------------|
| 1.5.1 | `ACTIVE_BRANDING` durch `VITE_BRANDING_SLUG` ersetzen |
| 1.5.2 | `asklepios` Branding komplett entfernen |
| 1.5.3 | `emtec` als Beispiel-Branding behalten (konfigurierbar via `VITE_BRANDING_SLUG=emtec`) |
| 1.5.4 | Resolver-Funktion für Asset-URLs (3-stufige Lookup-Reihenfolge) |
| 1.5.5 | TypeScript Types für alle neuen Configs |

---

### Paket 2: Branding Implementierung

> Umsetzung des Konzepts aus Paket 1.

#### 2.1 Theme Presets erstellen

| ID | Anforderung |
|----|-------------|
| 2.1.1 | `src/theme/presets/index.ts` — Preset Registry |
| 2.1.2 | `src/theme/presets/default.ts` — Aktuelles Blue Theme (unverändert) |
| 2.1.3 | `src/theme/presets/ocean.ts` — Teal/Cyan Theme |
| 2.1.4 | `src/theme/presets/forest.ts` — Green Theme |
| 2.1.5 | `src/theme/presets/sunset.ts` — Orange/Warm Theme |
| 2.1.6 | `src/theme/presets/purple.ts` — Purple Theme |
| 2.1.7 | `mantineTheme.ts` refactoren um Preset zu laden |

#### 2.2 Asset Resolver

| ID | Anforderung |
|----|-------------|
| 2.2.1 | `src/config/assetResolver.ts` — Funktion für 3-stufige Asset-Auflösung |
| 2.2.2 | `getIconUrl()`, `getLogoUrl()`, `getFaviconUrl()` Funktionen |
| 2.2.3 | **Lookup-Reihenfolge:** 1. Branding-Ordner → 2. `*.custom.*` in default → 3. default |
| 2.2.4 | Format-Reihenfolge: `.svg` → `.png` → `.jpg` → `.webp` |

#### 2.3 Cleanup & Migration

| ID | Anforderung |
|----|-------------|
| 2.3.1 | `/public/branding/asklepios/` Ordner komplett löschen |
| 2.3.2 | `branding.config.ts`: asklepios Eintrag aus `TENANT_BRANDINGS` entfernen |

#### 2.4 Header Update

| ID | Anforderung |
|----|-------------|
| 2.4.1 | Header Logo durch dynamisches Asset ersetzen |
| 2.4.2 | Header Title dynamisch aus Branding Config |
| 2.4.3 | Subtitle "powered by unified-ui" bei custom title |
| 2.4.4 | CSS für Subtitle (kleiner, rechtsbündig, muted color) |

#### 2.5 Favicon & HTML

| ID | Anforderung |
|----|-------------|
| 2.5.1 | `index.html` Favicon auf dynamischen Pfad setzen |
| 2.5.2 | `<title>` Tag dynamisch aus Config |
| 2.5.3 | Vite Plugin oder Build-Script für Favicon Injection |

#### 2.6 Documentation

| ID | Anforderung |
|----|-------------|
| 2.6.1 | `public/branding/README.md` mit Custom Branding Anleitung |
| 2.6.2 | `.gitignore` Einträge für custom files |
| 2.6.3 | Env Vars in `.env.example` dokumentieren |

---

### Paket 3: Listen Layout-Polish

> Feinschliff für DataTable: Spaltenbreiten mit min/max, horizontales Scrollen, responsive Verhalten.

**Aktueller Stand (DataTable):**
- Spalten: Favorite → Icon → Name/Desc → Type → Tags → Status → Menu
- Einige Spalten haben feste Breiten, andere flex
- Kein horizontales Scrollen bei min-width

**Betroffene Dateien:**
- `src/components/common/DataTable/DataTable.module.css`
- `src/components/common/DataTable/DataTableRow.tsx`

#### 3.1 Spaltenbreiten mit min/max

| ID | Anforderung |
|----|-------------|
| 3.1.1 | **Name/Description Spalte:** `min-width: 200px`, `max-width: 500px`, `flex: 1` |
| 3.1.2 | **Type Spalte:** `min-width: 100px`, `max-width: 180px` |
| 3.1.3 | **Tags Spalte:** `min-width: 120px`, `max-width: 250px` |
| 3.1.4 | **Status/Actions Spalte:** `flex-grow: 1` (nimmt restlichen Platz, damit Liste volle Breite nutzt) |
| 3.1.5 | Icon, Favorite, Menu behalten feste Breiten (keine Änderung) |

#### 3.2 Type als farbiges Badge

| ID | Anforderung |
|----|-------------|
| 3.2.1 | Type wird als `Badge` Komponente dargestellt statt als `Text` |
| 3.2.2 | Jeder Type bekommt eine eigene Farbe (z.B. Chat Agent → blue, Workflow → green, Widget → purple) |
| 3.2.3 | Farb-Mapping in einer zentralen Konstante definieren |
| 3.2.4 | Badge Styling: `variant="light"`, `size="sm"`, `radius="sm"` |

#### 3.3 Horizontales Scrollen

| ID | Anforderung |
|----|-------------|
| 3.3.1 | Wenn alle Spalten min-width erreichen → Container wird horizontal scrollbar |
| 3.3.2 | `overflow-x: auto` auf Row-Container |
| 3.3.3 | Rechts `margin-right` / `padding-right` bei Scroll, damit letzte Spalte nicht am Rand klebt |
| 3.3.4 | Toolbar (Search/Filter) bleibt außerhalb des Scroll-Bereichs (scrollt nicht mit) |

#### 3.4 Responsive Breakpoints

| ID | Anforderung |
|----|-------------|
| 3.4.1 | **< 992px:** Type-Spalte verstecken (aktuell schon so) |
| 3.4.2 | **< 768px:** Tags-Spalte verstecken |
| 3.4.3 | **< 576px:** Nur Icon, Name, Status, Menu anzeigen |

---

## Anhang

### Asset Lookup Beispiel

```
VITE_BRANDING_SLUG=emtec → /public/branding/emtec/icon.svg ✓
VITE_BRANDING_SLUG=default → /public/branding/default/icon.custom.svg (falls vorhanden) ✓
                          → /public/branding/default/icon.svg (Fallback) ✓
```

### Referenzen

- Error Stack Trace: `FormWidget` → `RangeSlider` → `getFloatingValue` → `value.toFixed is not a function`
- Affected Pages: ConversationsPage (alte Chats mit legacy Widget-Daten)
- DataTable CSS: `src/components/common/DataTable/DataTable.module.css`

### Theme Preset Beispiel (forest)

```typescript
// src/theme/presets/forest.ts
export const forestPreset = {
  primary: [
    '#e8f5e9', '#c8e6c9', '#a5d6a7', '#81c784', '#66bb6a',
    '#4caf50', '#43a047', '#388e3c', '#2e7d32', '#1b5e20',
  ],
  secondary: [
    '#e0f2f1', '#b2dfdb', '#80cbc4', '#4db6ac', '#26a69a',
    '#009688', '#00897b', '#00796b', '#00695c', '#004d40',
  ],
};
```

### Header Subtitle Design

```
┌─────────────────────────────────────────┐
│  [Icon]  Customer Portal                │
│              powered by unified-ui     │  ← 12px, muted, right-aligned
└─────────────────────────────────────────┘
```
