# N8N ↔ unified-ui Integration Pipeline

Diese Integration ermöglicht es, N8N Workflows automatisch mit unified-ui zu synchronisieren, sodass Traces im unified-ui Frontend visualisiert werden können.

---

## Konzept

Die Integration basiert auf einer **N8N Data Table** als Job-Queue:

1. **Jeder N8N Workflow** schreibt nach Abschluss einen Row in die Tabelle mit Status `PENDING`
2. **Ein dedizierter Integration Workflow** läuft im Schedule (z.B. jede Minute) und:
   - Liest alle Rows mit Status `PENDING`
   - Setzt Status auf `RUNNING`
   - Ruft `PUT /traces/import` im unified-ui Agent Service auf
   - Setzt Status auf `SUCCESS` (bei Erfolg) oder `FAILED` (bei Fehler)

---

## Tabellen-Schema

**Tabellen-Name**: `unified-ui-integration`

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | Auto-Increment | Primärschlüssel |
| `tenant_id` | String | unified-ui Tenant ID |
| `autonomous_agent_id` | String | ID des Autonomous Agents in unified-ui |
| `workflow_id` | String | N8N Workflow ID |
| `workflow_name` | String | Name des N8N Workflows |
| `execution_id` | String | N8N Execution ID (für Trace-Import) |
| `status` | String | `PENDING` / `RUNNING` / `SUCCESS` / `FAILED` |
| `createdAt` | DateTime | Automatisch |
| `updatedAt` | DateTime | Automatisch |

---

## Setup

### 1. Data Table erstellen

In N8N:
1. Gehe zu **Projects** → Dein Projekt
2. Erstelle neue **Data Table** mit Name `unified-ui-integration`
3. Füge die Spalten gemäß Schema hinzu (ohne `id`, `createdAt`, `updatedAt` — die werden automatisch erstellt)

### 2. Credential für unified-ui API erstellen

1. In N8N: **Credentials** → **New Credential** → **Header Auth**
2. Name: `unified-ui-agent-api`
3. Header Name: `X-API-Key`
4. Value: Der API Key des Autonomous Agents aus unified-ui Settings

### 3. Integration Workflow importieren

Importiere `unified-ui-integration-workflow.json`:

```json
{
  "nodes": [
    "Schedule Trigger (1 min interval)",
    "Get row(s) WHERE status = PENDING",
    "Update row(s) SET status = RUNNING",
    "HTTP Request PUT /traces/import",
    "Update row(s) SET status = SUCCESS (on success)",
    "Update row(s) SET status = FAILED (on error)"
  ]
}
```

**Wichtig**: Passe im HTTP Request Node die URL an:
- Lokales Docker: `http://host.docker.internal:8085`
- Production: Deine unified-ui Agent Service URL

### 4. Eigene Workflows integrieren

Füge am **Ende jedes Workflows** einen **Data Table Insert Node** hinzu:

```javascript
// Node: Insert row
// Trigger: Execute once (wichtig!)
{
  "tenant_id": "01fadbf4-...",  // Deine Tenant ID
  "autonomous_agent_id": "c523c3ad-...",  // Deine Agent ID
  "workflow_id": "={{ $execution.id }}",
  "workflow_name": "={{ $workflow.name }}",
  "execution_id": "={{ $execution.id }}",
  "status": "PENDING"
}
```

**Wichtig**: 
- `executeOnce: true` setzen, damit nur 1 Row pro Execution erstellt wird
- Tenant ID und Autonomous Agent ID müssen aus unified-ui Settings übernommen werden

---

## Beispiel: API Scraper Workflow

Siehe `workflow.json`:

1. **Manual Trigger** (oder anderer Trigger)
2. **HTTP Request** → Deine Business Logic
3. **Insert row** → Schreibt Row mit Status `PENDING` in die Tabelle

Der Integration Workflow holt dann automatisch die Traces aus N8N und importiert sie in unified-ui.

---

## Status-Übergänge

```
[Workflow beendet] 
    → Insert Row: status = PENDING
    ↓
[Integration Workflow findet Row]
    → Update: status = RUNNING
    ↓
[PUT /traces/import aufrufen]
    ↓
    ├─ Success → status = SUCCESS
    └─ Error   → status = FAILED
```

---

## Troubleshooting

### HTTP Request schlägt fehl (500 Error)

1. **Credential Secret fehlt**: Gehe in unified-ui → Settings → Credentials → Bearbeite das N8N API Credential → Speichere das Secret nochmal
2. **Vault läuft im Dev-Modus**: Secrets gehen bei Restart verloren → Konfiguriere persistenten Storage
3. **Agent Service nicht erreichbar**: Prüfe URL (`host.docker.internal` für Docker)

### Rows bleiben auf RUNNING

- Integration Workflow crashed während Verarbeitung
- Manuell wieder auf `PENDING` setzen oder Status-Filter anpassen

### Keine Traces im Frontend sichtbar

- Prüfe, ob Autonomous Agent ID korrekt ist
- Prüfe, ob User Permissions auf den Agent hat
- Schaue in Agent Service Logs nach Fehlern

---

## Deployment

**Production Hinweise**:

1. **Schedule Interval**: 1 Minute ist für Dev OK, in Production ggf. auf 5-10 Minuten erhöhen
2. **Retry Logic**: Fehlerhafte Rows könnten automatisch wieder auf `PENDING` gesetzt werden (separate Workflow)
3. **Cleanup**: Alte SUCCESS/FAILED Rows regelmäßig archivieren/löschen
4. **Monitoring**: Zähler für PENDING/FAILED Rows als Alert