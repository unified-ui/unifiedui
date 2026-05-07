# 011 — User Settings, File Uploads & Image Caching v0.2.8

> **Status:** DRAFT  
> **Scope:** unified-ui-frontend-service, unified-ui-platform-service  
> **Ziel:** Language-Selector funktional machen (de-DE Translations), Settings-Page Dark-Mode Design verbessern, File-Upload-Flow reviewen, Browser-Image-Caching einführen.

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

### Paket 0: Language Selector & Settings Dark Mode

> Language-Auswahl funktional machen (de-DE Translations anlegen) und Settings-Page-Design im Dark Mode auf das ContentCard-Pattern upgraden.

#### 0.1 Language Persistence & de-DE Translations

| ID | Anforderung |
|----|-------------|
| 0.1.1 | De-DE Locale-Dateien für alle 14 Namespaces anlegen (`src/i18n/locales/de-DE/*.json`) mit deutschen Übersetzungen. |
| 0.1.2 | De-DE Locale-Dateien in `src/i18n/index.ts` importieren und als `'de-DE'`-Ressource registrieren. |
| 0.1.3 | Language-Auswahl wird über `localStorage` persistiert (funktioniert bereits über `i18next-browser-languagedetector`). Default bleibt `en-US`. Sicherstellen, dass der gespeicherte Wert beim App-Start korrekt geladen wird. Wenn kein Wert in localStorage gesetzt ist, soll der Dropdown trotzdem `English (US)` als ausgewählt anzeigen. |
| 0.1.4 | Copilot Instructions (`unified-ui-frontend-service/.github/copilot-instructions.md`) updaten: bei neuen UI-Strings immer in **beiden** Sprachen (`en-US` + `de-DE`) übersetzen. |

#### 0.2 Settings Page Dark Mode Redesign

| ID | Anforderung |
|----|-------------|
| 0.2.1 | Die drei Paper-Sections (Profile, Tenant Context, Preferences) durch die **`ContentCard`-Komponente** direkt ersetzen (`src/components/common/ContentCard/`). Jede Section bekommt ein passendes Icon im Header (Profile → `IconUser`, Tenant Context → `IconBuildingCommunity`, Preferences → `IconSettings`). |
| 0.2.2 | Dark-Mode-Styling wird automatisch durch ContentCard mitgeliefert (blauer Glow-Shadow, Gradient-Header, `#292929` Background). Keine zusätzliche CSS nötig. |
| 0.2.3 | InfoRow-Styling aufwerten: subtilere Borders, bessere Kontraste im Dark Mode, konsistent mit dem restlichen Design-System. |

---

### Paket 1: Browser Image Caching

> Browser HTTP Cache + Blob-URL-Map nutzen, damit Bilder nicht bei jedem Mount/Seitennavigation neu gefetched werden. Kein Custom In-Memory-Cache — der Browser übernimmt das Caching über `Cache-Control` Header.

#### 1.1 Backend: Cache-Control Header

| ID | Anforderung |
|----|-------------|
| 1.1.1 | Download-Endpoint (`GET /tenants/{tenant_id}/files/{file_id}/download`) soll `Cache-Control: private, max-age=600` Header setzen. `private` erlaubt Browser-Cache trotz `Authorization` Header, aber kein CDN/Proxy-Caching. |

#### 1.2 Frontend: Blob-URL-Map

| ID | Anforderung |
|----|-------------|
| 1.2.1 | Module-Level `Map<fileId, blobUrl>` in `AuthImage` einführen. Zweck: vermeidet, dass bei jedem Mount erneut `response.blob()` + `URL.createObjectURL()` aufgerufen wird, selbst wenn der Browser-Cache den Netzwerk-Request spart. |
| 1.2.2 | `AuthImage`-Komponente: bei bekannter `fileId` zuerst die Blob-URL-Map prüfen → wenn vorhanden, sofort nutzen (kein fetch). Bei Map-Miss: fetch (Browser-Cache wird automatisch genutzt) → Blob-URL erstellen → in Map speichern. |
| 1.2.3 | `URL.revokeObjectURL()` NICHT mehr bei Component Unmount aufrufen — Blob-URLs bleiben in der Map erhalten über die SPA-Lebensdauer. |
| 1.2.4 | Invalidierung: `invalidateImageCache(fileId)` Funktion exportieren, die den Map-Eintrag löscht und die alte Blob-URL revoked. Aufrufen wenn ein Image aktualisiert wird (z.B. neues App-Icon). |

---

## Anhang

### Kontext-Recherche

#### Language Selector (Paket 0.1)
- **Aktueller Stand**: Language-Dropdown existiert in `UserSettingsPage.tsx` mit `en-US` und `de-DE` Optionen. `i18n.changeLanguage()` + `localStorage` Persistierung ist implementiert.
- **Problem**: Es gibt **keine `de-DE` Locale-Dateien** — nur `en-US` existiert in `src/i18n/locales/`. Die Auswahl "Deutsch" fällt auf `en-US` zurück.
- **Lösung**: 14 de-DE JSON-Dateien erstellen und in i18n-Config registrieren.

#### Settings Dark Mode (Paket 0.2)
- **Aktueller Stand**: Settings-Page nutzt plain `<Paper withBorder>` Mantine-Komponenten. Im Dark Mode hat das keinen visuellen Lift — flaches, langweiliges Design.
- **Referenz**: `ContentCard` Komponente (`src/components/common/ContentCard/`) hat explizites Dark-Mode-Styling mit blauem Glow-Shadow, Gradient-Header, und erhöhtem Background (`#292929`).
- **Lösung**: Paper-Sections durch ContentCard ersetzen oder analoges Styling in der Settings-Page CSS übernehmen.

#### File Upload (Kein Paket — bereits korrekt)
- **Aktueller Stand**: Mehrere Dateien werden **zusammen in EINER Message** gesendet, nicht getrennt. Flow: `ChatInput` sammelt bis zu 5 Files → `useChat.handleSendMessage()` konvertiert alle zu base64 → parallel Upload zu Platform-Storage → alle Files werden in einem einzigen SSE-Stream-Request an den Agent Service gesendet.
- **Ergebnis**: ✅ Funktioniert korrekt. Keine Änderung nötig.

#### Image Caching (Paket 1)
- **Aktueller Stand**: `AuthImage` Komponente fetcht bei jedem Mount/Re-Render das Bild neu via authentifiziertem `fetch()`. Kein Cache, kein `Cache-Control` Header vom Backend.
- **Lösung**: Module-Level `Map` als Cache, Backend optional `Cache-Control` Header.

### Referenzen

- Issue: https://github.com/unified-ui/unifiedui-agent-service/issues/9
- ContentCard Pattern: `src/components/common/ContentCard/`
- AuthImage: `src/components/common/AuthImage/AuthImage.tsx`
- i18n Config: `src/i18n/index.ts`
- Settings Page: `src/pages/UserSettingsPage/`
