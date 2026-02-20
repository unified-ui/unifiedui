# Customizable Login Page Concept

## 1. Übersicht

Die Login-Seite (`/login`) soll von der aktuellen "Landing-Page" mit Feature-Cards zu einer **schlichten, zweispaltigen Login-Seite** umgebaut werden, die **pro Kunde individuell gebrandet** werden kann.

Das Branding wird **ausschließlich im Frontend** gelöst — eine einzige Config-Datei definiert das Default-Branding und optionale Kunden-Overrides. **Kein Backend, keine Datenbank, keine API** nötig.

### Ziel-Layout (Split-Screen)

```
┌─────────────────────────────┬──────────────────────────────┐
│                             │                              │
│  [Logo + Kundenname]        │                              │
│                             │                              │
│                             │      ┌──────────────┐       │
│                             │      │              │       │
│   Melde dich an, um auf     │      │  Kunden-Icon │       │
│   die App zuzugreifen       │      │   (groß)     │       │
│                             │      │              │       │
│   ┌──────────────────────┐  │      └──────────────┘       │
│   │ 🪟 Fortfahren mit    │  │                              │
│   │    Microsoft         │  │                              │
│   └──────────────────────┘  │                              │
│                             │                              │
│   ┌──────────────────────┐  │     Hintergrund:             │
│   │ 🔵 Fortfahren mit    │  │     Kundenfarbe (dunkel)     │
│   │    Google (später)   │  │     + Gradient/Pattern        │
│   └──────────────────────┘  │                              │
│                             │                              │
│  Hintergrund:               │                              │
│  Kundenfarbe (schlicht)     │                              │
│                             │                              │
└─────────────────────────────┴──────────────────────────────┘
```

### Linke Hälfte
- Oben links: **Logo des Kunden** (klein) + **Kundenname** als Text
- Mitte: Überschrift "Melde dich an, um auf die App zuzugreifen" (i18n)
- Darunter: Auth-Provider-Buttons (Microsoft, später Google, etc.)
- Hintergrund: Schlichte Kundenfarbe (z.B. dunkles Teal für Asklepios)

### Rechte Hälfte
- Großes **Kunden-Icon/Emblem** (z.B. Äskulapstab bei Asklepios), zentriert
- Hintergrund: Dunklerer Ton der Kundenfarbe oder Akzentfarbe mit optionalem Gradient/Overlay

---

## 2. Branding-Konfiguration (rein Frontend)

Das gesamte Branding wird **ausschließlich im Frontend** als TypeScript-Config verwaltet.
Kein Backend, keine Datenbank, keine API. Eine einzige Datei — fertig.

Die Config deckt **3 Bereiche** ab:
1. **Login-Page** (Farben, Hintergründe, Buttons)
2. **App-wide** (Header, Sidebar — für zukünftige Nutzung)
3. **Typografie** (Font-Family, Font-Size — für zukünftige Nutzung)

### 2.1 TypeScript Interfaces

```typescript
// src/config/branding.types.ts

export interface LoginBranding {
  bgLeft: string;              // CSS background für linke Hälfte
  bgRight: string;             // CSS background für rechte Hälfte
  textColor: string;           // Textfarbe links
  heading: string | null;      // Custom-Heading (null = i18n Default)
  buttonBorderColor: string;   // Auth-Button Border
  buttonHoverBg: string;       // Auth-Button Hover
}

export interface AppBranding {
  headerBg: string;            // Header-Hintergrund
  headerTextColor: string;     // Header-Textfarbe
  sidebarBg: string;           // Sidebar-Hintergrund
  sidebarTextColor: string;    // Sidebar-Textfarbe
  sidebarActiveBg: string;     // Sidebar aktives Item BG
  sidebarActiveTextColor: string;
}

export interface BrandingTypography {
  fontFamily: string;          // Primäre Schriftart
  headingFontFamily: string | null;  // Heading-Schriftart (Fallback: fontFamily)
  baseFontSize: number;        // Basis-Schriftgröße in px
}

export interface BrandingConfig {
  slug: string;
  displayName: string;
  logoUrl: string | null;      // Kleines Logo oben links
  iconUrl: string | null;      // Großes Icon rechte Seite
  faviconUrl: string | null;   // Browser-Favicon
  login: LoginBranding;
  app: AppBranding;
  typography: BrandingTypography;
}
```

### 2.2 Die Config-Datei

```typescript
// src/config/branding.config.ts

const DEFAULT_BRANDING: BrandingConfig = {
  slug: "default",
  displayName: "unified-ui",
  logoUrl: null,                 // → zeigt IconBrain Fallback
  iconUrl: null,                 // → zeigt default/icon.svg
  faviconUrl: null,

  login: {
    bgLeft: "linear-gradient(160deg, #0a1628, #0f2035, #0a1628)",
    bgRight: "linear-gradient(160deg, #0f2035, #162a4a, #0f2035)",
    textColor: "#FFFFFF",
    heading: null,               // → i18n Default
    buttonBorderColor: "rgba(255, 255, 255, 0.25)",
    buttonHoverBg: "rgba(255, 255, 255, 0.08)",
  },

  app: {
    headerBg: "var(--mantine-color-body)",
    headerTextColor: "var(--mantine-color-text)",
    sidebarBg: "var(--mantine-color-body)",
    sidebarTextColor: "var(--mantine-color-text)",
    sidebarActiveBg: "var(--mantine-primary-color-light)",
    sidebarActiveTextColor: "var(--mantine-primary-color-filled)",
  },

  typography: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    headingFontFamily: null,
    baseFontSize: 16,
  },
};

const TENANT_BRANDINGS: Record<string, DeepPartial<BrandingConfig>> = {
  asklepios: {
    displayName: "Asklepios",
    logoUrl: "/branding/asklepios/logo.svg",
    iconUrl: "/branding/asklepios/icon.svg",
    login: {
      bgLeft: "#0c2e2e",
      bgRight: "#091f1f",
    },
  },
};

// getBranding(slug) → deep-merged Config
```

Kunden-Overrides sind **Partial** — nur angeben, was abweicht. Alles andere kommt vom Default.

### 2.3 Bilder ablegen

```
public/
  branding/
    default/
      logo.svg            ← unified-ui Logo (Brain-Icon mit Gradient)
      icon.svg            ← großes Brain/Neural-Network Icon
    asklepios/
      logo.svg            ← Asklepios Logo + Text
      icon.svg            ← Äskulapstab (Rod of Asclepius)
```

Erreichbar unter `/branding/asklepios/logo.svg` — statisch, kein CDN nötig.

---

## 3. Branding-Auflösung

### URL Query-Parameter

```
/login                     → Default Unified-UI Branding
/login?tenant=asklepios    → Asklepios Branding
/login?tenant=unbekannt    → Default (Fallback)
```

- Synchron aus Config — kein API-Call, kein Loading
- Bookmark-fähig für Kunden-SSO-Entry-Points

---

## 4. Neuen Kunden hinzufügen — Workflow

### Schritt 1: Bilder ablegen

```bash
public/branding/<slug>/logo.svg   # oder .png
public/branding/<slug>/icon.svg   # oder .png
```

### Schritt 2: Config ergänzen

```typescript
// src/config/branding.config.ts — TENANT_BRANDINGS

neuerKunde: {
  displayName: "Neuer Kunde",
  logoUrl: "/branding/neuerkunde/logo.svg",
  iconUrl: "/branding/neuerkunde/icon.svg",
  login: {
    bgLeft: "#1A2B3C",
    bgRight: "#0F1E2D",
  },
  // Optional: app, typography Overrides
},
```

### Schritt 3: Deployen

Login-Link: `https://app.unified-ui.com/login?tenant=neuerkunde`

**Das war's.** Keine Migration, kein Backend, kein Admin-UI.

---

## 5. Dateistruktur

```
unified-ui-frontend-service/
  public/
    branding/
      default/
        logo.svg                      ← unified-ui Default Logo
        icon.svg                      ← unified-ui Default Icon
      asklepios/
        logo.svg                      ← Asklepios Logo + Text
        icon.svg                      ← Äskulapstab
  src/
    config/
      index.ts                        ← Re-Exports
      branding.types.ts               ← BrandingConfig, LoginBranding, AppBranding, etc.
      branding.config.ts              ← DEFAULT + TENANT_BRANDINGS + getBranding()
    hooks/
      useBranding.ts                  ← Hook: reads ?tenant= param → returns BrandingConfig
    pages/
      LoginPage/
        LoginPage.tsx                 ← Split-Screen Layout
        LoginPage.module.css          ← Neues CSS
```

---

## 6. Implementierungs-Phasen

### Phase 1: Core Login-Page Redesign ✅

1. ✅ `BrandingConfig` + Sub-Interfaces erstellen (`branding.types.ts`)
2. ✅ Config mit Default + Asklepios anlegen (`branding.config.ts`)
3. ✅ `useBranding()` Hook erstellen
4. ✅ `LoginPage` komplett umbauen (Split-Screen)
5. ✅ `LoginPage.module.css` neu schreiben
6. ✅ Mobile Responsive (rechte Hälfte ausblenden)
7. ✅ SVG-Assets für Default und Asklepios erstellen

### Phase 2: Erweiterungen

8. Weitere Auth-Provider-Buttons (Google, SAML/SSO)
9. Favicon dynamisch setzen basierend auf Branding
10. Subtile Animationen / Transitions

### Phase 3: App-weites Theming

11. `app`-Branding in Header/Sidebar nutzen (Farben, Logo)
12. `typography`-Branding anwenden (fontFamily, fontSize)
13. Mantine Theme dynamisch aus Branding ableiten

---

## 7. Technische Entscheidungen

| Entscheidung | Gewählt | Begründung |
|---|---|---|
| Branding-Speicherung | Frontend Config-Datei | Kein Backend, sofort verfügbar, einfach zu pflegen |
| Bilder | `public/branding/<slug>/` | Statisch ausgeliefert, kein Upload/CDN nötig |
| Tenant-Erkennung | URL `?tenant=<slug>` | Einfach, kein DNS nötig, Bookmark-fähig |
| Overrides | `DeepPartial<BrandingConfig>` | Nur abweichendes angeben, Rest = Default |
| Merge-Strategie | Deep-Merge | Nested Objekte (login, app, typography) korrekt gemerged |
| Login-Layout | 50/50 Split-Screen | Clean, modern, wie Asklepios-Beispiel |
| Mobile | Rechte Hälfte ausblenden | Login-Funktion hat Priorität |
| Hook | Synchron (`useBranding()`) | Kein Loading, kein API-Call |
| Zukunft: App-Theming | `app` + `typography` Felder | Bereits im Interface, aber noch nicht aktiv genutzt |
