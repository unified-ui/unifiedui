# {NNN} — {Kurztitel} v{X.Y.Z}

> **Status:** DRAFT | IN PROGRESS | DONE  
> **Scope:** {betroffene Repos/Services, z.B. unified-ui-frontend-service, unified-ui-platform-service}  
> **Ziel:** {1-2 Sätze: Was soll erreicht werden?}

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
- Backend-Änderungen werden im selben Paket miterledigt, wenn das Paket Backend-Anforderungen enthält.
- Nach **jedem Paket**: `pre-commit run --all-files` ausführen und alle Fehler fixen.

---

## Pakete

### Paket 0: {Voraussetzungen / Grundlagen}

> {Kurzbeschreibung: Was wird in diesem Paket gemacht?}

#### 0.1 {Unterabschnitt}

| ID | Anforderung |
|----|-------------|
| 0.1.1 | {Konkrete, implementierbare Anforderung} |
| 0.1.2 | {Konkrete, implementierbare Anforderung} |

---

### Paket 1: {Hauptfeature 1}

> {Kurzbeschreibung}

#### 1.1 {Unterabschnitt}

| ID | Anforderung |
|----|-------------|
| 1.1.1 | {Anforderung} |

---

## Anhang

### Referenzen

- {Link zu Issue, PR, Dokumentation}
