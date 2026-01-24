# Tracing Sidebar Data Panels - Anforderungsspezifikation

> **Version**: 2.0 (IMPLEMENTIERT)
> **Datum**: 24. Januar 2026
> **Status**: ✅ Fertig implementiert
> **Bezug**: VS Code Sidebar Panel Verhalten (OUTLINE, TIMELINE, etc.)

---

## 0. Implementierungs-Zusammenfassung

### ✅ Finale Implementierung

**Dateien:**
- `src/components/tracing/TracingHierarchyView.tsx` - Komponenten-Logik
- `src/components/tracing/TracingHierarchyView.module.css` - Styles

**Komponenten:**
- `ResizablePanel` - Einzelnes Panel mit Header, Resize-Handle, ScrollArea
- `DataPanelsContainer` - Container für alle Panels mit State-Management

**Verhalten:**
| Feature | Implementierung |
|---------|-----------------|
| **Akkordeon** | Nur ein Panel kann gleichzeitig offen sein |
| **Shared Height** | Alle Panels teilen sich eine gemeinsame Höhe (`activeHeight`) |
| **Panel-Reihenfolge** | INPUT → OUTPUT → LOGS → METADATA |
| **Resize** | Direkte Höhenänderung ohne Animation (smooth) |
| **Höhen-Übernahme** | Beim Panel-Wechsel wird die aktuelle Höhe übernommen |

---

## 1. Problemstellung (IST-Zustand)

### 1.1 Aktuelles Verhalten

```
┌────────────────────────────────────┐
│ Tree Hierarchy                     │
│ ...                                │
├════════════════════════════════════┤ ← Einziger Resize-Handle
│                                    │
│ DATA PANELS SECTION (feste Höhe)   │
│                                    │
│ ▸ LOGS                       [3]   │ ← Collapsible, NICHT resizable
│ ▾ INPUT / OUTPUT                   │ ← Collapsible, NICHT resizable
│   │ INPUT                          │
│   │ Text: "Hello"                  │ ← KEIN individueller Scroll
│   │ OUTPUT                         │
│   │ Text: "Hi!"                    │
│ ▸ METADATA                         │ ← Collapsible, NICHT resizable
│                                    │
└────────────────────────────────────┘
```

### 1.2 Probleme

1. **Ein gemeinsamer Resize-Handle** für alle Panels zusammen
2. **Kein individueller Scroll** pro Section
3. **Keine individuelle Höhenverstellung** pro Section
4. **Panels sind nicht unten angeheftet** im collapsed Zustand
5. **Expandierte Sections nehmen nicht definierte Höhe ein**

---

## 2. Anforderungen (SOLL-Zustand)

### 2.1 VS Code Referenz-Verhalten

VS Code Sidebar Panels (z.B. Explorer → OUTLINE, TIMELINE):

```
┌────────────────────────────────────┐
│                                    │
│ MAIN CONTENT (z.B. File Explorer)  │
│                                    │
│                                    │
│                                    │
│                                    │
├────────────────────────────────────┤
│ ▸ OUTLINE                          │ ← Collapsed, am unteren Rand
├────────────────────────────────────┤
│ ▸ TIMELINE                         │ ← Collapsed, am unteren Rand
└────────────────────────────────────┘
```

Nach Expand von TIMELINE:

```
┌────────────────────────────────────┐
│                                    │
│ MAIN CONTENT (schrumpft)           │
│                                    │
├────────────────────────────────────┤
│ ▸ OUTLINE                          │ ← Collapsed
├════════════════════════════════════┤ ← Resize-Handle für TIMELINE
│ ▾ TIMELINE                         │
│   │ commit 1                       │ ← Scrollbar innerhalb
│   │ commit 2                       │
│   │ commit 3                       │
│   │ ...                            │
└────────────────────────────────────┘
```

### 2.2 Funktionale Anforderungen

#### FR-01: Collapsed State (Default) ✅
- **ALLE** Panels sind initial collapsed
- Collapsed Panels sind **am unteren Rand angeheftet** (stacked)
- Collapsed Panels zeigen nur den Header (Titel + Badge + Chevron)
- Collapsed Panels haben eine **feste Höhe** (28px)

#### FR-02: Expand/Collapse Toggle ✅
- Klick auf Panel-Header togglet den Expand-State
- Beim **Expand**: Panel öffnet sich mit der **gemeinsamen activeHeight** (Default: 150px)
- Beim **Collapse**: Panel schließt sich auf Header-Höhe
- Chevron-Icon zeigt State an: `▸` (collapsed) / `▾` (expanded)
- **AKKORDEON**: Nur ein Panel kann gleichzeitig offen sein

#### FR-03: Individuelle Höhenverstellung ✅
- Jedes **expandierte** Panel hat einen **eigenen Resize-Handle** (oben am Panel)
- Resize-Handle erlaubt Drag nach oben/unten
- **Minimum-Höhe**: 80px (damit Content sichtbar bleibt)
- **Gemeinsame Höhe**: Alle Panels teilen sich `activeHeight`
- **Höhen-Übernahme**: Beim Panel-Wechsel wird die aktuelle Höhe übernommen

#### FR-04: Individueller Scroll ✅
- Jedes expandierte Panel hat **eigene ScrollArea**
- Scroll ist **nur vertikal**
- Scrollbar erscheint nur bei Bedarf (auto)
- Content scrollt unabhängig von anderen Panels

#### FR-05: Layout-Verhalten ✅
- Collapsed Panels: Feste Höhe (28px), am unteren Rand gestapelt
- Expandierte Panels: Variable Höhe (`activeHeight`), nehmen Platz nach oben
- Tree Hierarchy (oben) schrumpft wenn Panels expandiert werden
- **Tree Hierarchy hat Minimum-Höhe** (100px)

#### FR-06: Akkordeon-Verhalten ✅ (GEÄNDERT)
- **Nur ein Panel** kann gleichzeitig expandiert sein
- Öffnen eines Panels schließt automatisch das vorher offene Panel
- Die eingestellte Höhe wird beim Panel-Wechsel übernommen

### 2.3 Panel-Spezifikationen

| Panel | Datenquelle (Root) | Datenquelle (Node) | Badge |
|-------|-------------------|-------------------|-------|
| **LOGS** | `trace.logs` | `node.logs` | Anzahl Logs |
| **INPUT** | - (nicht angezeigt) | `node.data.input` | - |
| **OUTPUT** | - (nicht angezeigt) | `node.data.output` | - |
| **METADATA** | `trace.referenceMetadata` | `node.metadata` | - |

**Hinweis:** INPUT und OUTPUT sind jetzt **separate Panels** (nicht mehr kombiniert).

### 2.4 Reihenfolge der Panels (von oben nach unten) ✅

1. **INPUT** - Zeigt Input-Daten (nur bei Node-Auswahl)
2. **OUTPUT** - Zeigt Output-Daten (nur bei Node-Auswahl)
3. **LOGS** - Zeigt Log-Einträge
4. **METADATA** - Zeigt Metadata

---

## 3. Visuelles Design

### 3.1 Collapsed State (alle Panels)

```
┌────────────────────────────────────┐
│                                    │
│         TREE HIERARCHY             │
│         (flex: 1, min-height)      │
│                                    │
│                                    │
│                                    │
├────────────────────────────────────┤
│ ▸ LOGS                       [5]   │ ← 28px
├────────────────────────────────────┤
│ ▸ INPUT                            │ ← 28px (nur bei Node)
├────────────────────────────────────┤
│ ▸ OUTPUT                           │ ← 28px (nur bei Node)
├────────────────────────────────────┤
│ ▸ METADATA                         │ ← 28px
└────────────────────────────────────┘
```

### 3.2 Ein Panel expandiert (z.B. LOGS)

```
┌────────────────────────────────────┐
│                                    │
│         TREE HIERARCHY             │
│         (schrumpft)                │
│                                    │
├════════════════════════════════════┤ ← Resize-Handle für LOGS
│ ▾ LOGS                       [5]   │
│ ┌────────────────────────────────┐ │
│ │ - Log entry 1                  │ │ ← ScrollArea
│ │ - Log entry 2                  │ │
│ │ - Log entry 3                  │ │
│ │ - Log entry 4                  │ │
│ │ - Log entry 5                  │ │
│ └────────────────────────────────┘ │
├────────────────────────────────────┤
│ ▸ INPUT                            │ ← Collapsed
├────────────────────────────────────┤
│ ▸ OUTPUT                           │ ← Collapsed
├────────────────────────────────────┤
│ ▸ METADATA                         │ ← Collapsed
└────────────────────────────────────┘
```

### 3.3 Mehrere Panels expandiert

```
┌────────────────────────────────────┐
│         TREE HIERARCHY             │
│         (minimal)                  │
├════════════════════════════════════┤ ← Resize für LOGS
│ ▾ LOGS                       [5]   │
│ │ - Log 1                        │ │
│ │ - Log 2                        │ │
├════════════════════════════════════┤ ← Resize für OUTPUT
│ ▾ OUTPUT                           │
│ │ Text: "Response..."            │ │
│ │ ▸ Arguments                    │ │
├────────────────────────────────────┤
│ ▸ INPUT                            │ ← Collapsed
├────────────────────────────────────┤
│ ▸ METADATA                         │ ← Collapsed
└────────────────────────────────────┘
```

### 3.4 Panel Header Design

```
┌────────────────────────────────────┐
│ [▾] [Icon] TITLE            [Badge]│
└────────────────────────────────────┘
  │     │      │                 │
  │     │      │                 └── Optional: Anzahl Items
  │     │      └── Panel-Titel (uppercase, letter-spacing)
  │     └── Panel-Icon (IconNote, IconFileText, etc.)
  └── Chevron (▸ collapsed, ▾ expanded)
```

**CSS:**
```css
.panelHeader {
  height: 28px;
  padding: 0 var(--spacing-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  background: var(--bg-paper);
  border-bottom: 1px solid var(--border-default);
  cursor: pointer;
  user-select: none;
}

.panelHeader:hover {
  background: var(--bg-hover);
}

.panelTitle {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex: 1;
}
```

### 3.5 Resize Handle Design

```
════════════════════════════════════  ← 4px Höhe, volle Breite
```

**CSS:**
```css
.resizeHandle {
  height: 4px;
  cursor: row-resize;
  background: transparent;
  transition: background-color var(--transition-fast);
}

.resizeHandle:hover,
.resizeHandle:active {
  background: var(--color-primary-300);
}
```

---

## 4. Technische Implementierung

### 4.1 State-Struktur (FINALE IMPLEMENTIERUNG)

```typescript
// Konstanten
const PANEL_HEADER_HEIGHT = 28;
const PANEL_MIN_HEIGHT = 80;
const PANEL_DEFAULT_HEIGHT = 150;
const TREE_MIN_HEIGHT = 100;

// Panel-Typen
type PanelId = 'logs' | 'input' | 'output' | 'metadata';

// State im DataPanelsContainer
const [activeHeight, setActiveHeight] = useState(PANEL_DEFAULT_HEIGHT);  // Gemeinsame Höhe
const [expandedPanel, setExpandedPanel] = useState<PanelId | null>(null); // Welches Panel offen ist
```

### 4.2 Komponenten-Struktur (FINALE IMPLEMENTIERUNG)

```
TracingHierarchyView
├── Header (optional)
├── ScrollArea (Tree, flex: 1, min-height: 100px)
└── DataPanelsContainer
    ├── ResizablePanel (INPUT) - nur bei Node
    ├── ResizablePanel (OUTPUT) - nur bei Node
    ├── ResizablePanel (LOGS)
    └── ResizablePanel (METADATA)
```

### 4.3 ResizablePanel Komponente (FINALE IMPLEMENTIERUNG)

```typescript
interface ResizablePanelProps {
  title: string;
  icon: React.ReactNode;
  badge?: number;
  isExpanded: boolean;
  height: number;
  onToggle: () => void;
  onHeightChange: (newHeight: number) => void;
  children: React.ReactNode;
  hasContent?: boolean;  // Zeigt "–" wenn keine Daten
}
```

### 4.4 Resize-Logik (FINALE IMPLEMENTIERUNG)

```typescript
const handleResizeStart = useCallback((e: React.MouseEvent) => {
  e.preventDefault();
  e.stopPropagation();
  isResizing.current = true;
  
  const startY = e.clientY;
  const startHeight = height;

  const handleMouseMove = (moveEvent: MouseEvent) => {
    if (!isResizing.current) return;
    
    // Bewegung nach oben = Panel wird größer (deltaY negativ)
    const deltaY = startY - moveEvent.clientY;
    const newHeight = Math.max(PANEL_MIN_HEIGHT, startHeight + deltaY);
    
    // Direkte Höhenänderung ohne requestAnimationFrame für responsive resize
    onHeightChange(newHeight);
  };

  const handleMouseUp = () => {
    isResizing.current = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  };

  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp);
  document.body.style.cursor = 'row-resize';
  document.body.style.userSelect = 'none';
}, [height, onHeightChange]);
```

### 4.5 Akkordeon-Toggle (FINALE IMPLEMENTIERUNG)

```typescript
// Toggle Panel - Accordion behavior: nur ein Panel gleichzeitig offen
const togglePanel = useCallback((panelId: PanelId) => {
  setExpandedPanel(prev => prev === panelId ? null : panelId);
}, []);

// Change Panel Height - ändert die gemeinsame activeHeight
const changePanelHeight = useCallback((newHeight: number) => {
  setActiveHeight(newHeight);
}, []);
```

### 4.6 Panel-Rendering (FINALE IMPLEMENTIERUNG)

```tsx
<ResizablePanel
  title="INPUT"
  icon={<IconArrowDown size={14} />}
  isExpanded={expandedPanel === 'input'}
  height={activeHeight}
  onToggle={() => togglePanel('input')}
  onHeightChange={changePanelHeight}
  hasContent={hasInput}
>
  {renderDataContent(inputData, 'Input')}
</ResizablePanel>
```

---

## 5. Edge Cases

### 5.1 Akkordeon-Verhalten
- **Nur ein Panel gleichzeitig offen**: Beim Öffnen eines Panels wird das vorherige automatisch geschlossen
- **Gemeinsame Höhe**: Alle Panels teilen sich eine `activeHeight`, die beim Resize geändert wird
- **Höhe bleibt erhalten**: Wenn Panel A auf 200px resized wird und dann Panel B geöffnet wird, hat B ebenfalls 200px

### 5.2 Root vs. Node Auswahl
- **Root ausgewählt**: INPUT und OUTPUT Panels werden **nicht angezeigt**
- **Node ausgewählt**: Alle 4 Panels werden angezeigt
- Beim Wechsel von Node → Root: INPUT/OUTPUT Panels verschwinden, Panel-State bleibt erhalten

### 5.3 Leere Daten
- Wenn ein Panel keine Daten hat (z.B. `logs = []`):
  - Panel wird trotzdem angezeigt
  - Content zeigt "–" Text (via `hasContent` prop)
  - Badge wird nur angezeigt wenn Content vorhanden ist

### 5.4 Resize-Verhalten
- **Smooth Resize**: Keine CSS-Transition auf height, keine requestAnimationFrame
- **Minimale Höhe**: 80px (PANEL_MIN_HEIGHT)
- **Default-Höhe**: 150px beim ersten Öffnen
- **Cursor-Feedback**: `row-resize` Cursor während Drag

---

## 6. Implementierungs-Checkliste

- [x] `ResizablePanel` Komponente erstellen
- [x] State-Management: `activeHeight` (gemeinsam) + `expandedPanel` (welches offen)
- [x] Resize-Handle mit Drag-Logik (direkt, ohne Animation)
- [x] Individuelle ScrollArea pro Panel
- [x] Akkordeon-Toggle (nur ein Panel offen)
- [x] Panel-Reihenfolge: INPUT → OUTPUT → LOGS → METADATA
- [x] Anpassung für Root vs. Node (INPUT/OUTPUT visibility)
- [x] CSS-Styles für Panel-Header, Resize-Handle, Content
- [x] Hover-Effekte für Panel-Header und Resize-Handle

---

## 7. Abgrenzung

### Was NICHT in diesem Scope:
- Persistierung der Panel-Höhen (localStorage)
- Drag & Drop zum Umsortieren der Panels
- Horizontales Resize
- Panel-spezifische Actions (z.B. "Copy All" Button)
- Animationen für Expand/Collapse (bewusst entfernt für smoothes Resize)

### Später möglich:
- Höhen-Persistierung in localStorage
- Keyboard Shortcuts (z.B. `Ctrl+1` für LOGS toggle)
- Context Menu auf Panel-Header

---

## 8. Änderungshistorie

| Version | Datum | Änderungen |
|---------|-------|------------|
| 1.0 | - | Initiale Spezifikation mit Multi-Panel-Expand |
| 2.0 | 11.07.2025 | **Finale Implementierung**: Akkordeon-Verhalten, gemeinsame Höhe, smooth resize, Panel-Reihenfolge geändert |

---

**Ende der Spezifikation**
