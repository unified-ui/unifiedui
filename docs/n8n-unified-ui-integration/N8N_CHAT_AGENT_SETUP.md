# N8N Chat Agent Setup für unified-ui

Diese Anleitung beschreibt, wie ein N8N Workflow für die Nutzung als **Chat Agent** in unified-ui konfiguriert wird — inklusive automatischem Trace-Import.

---

## Voraussetzungen

- N8N Instance (lokal oder gehostet)
- unified-ui Chat Agent mit Typ `N8N`
- N8N API Key (für Trace-Import)

---

## Workflow-Aufbau

### Basis-Struktur

```
┌─────────────────────────┐
│ When chat message       │
│ received                │
│ (Chat Trigger)          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ AI Agent                │
│ (oder andere Logik)     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Respond ExecutionID     │  ◀── Wichtig für Trace-Import!
│ (Respond to Webhook)    │
└─────────────────────────┘
```

---

## Schritt-für-Schritt Konfiguration

### 1. Chat Trigger Node

1. Node hinzufügen: **"When chat message received"**
2. Einstellungen:
   - **Make Chat Publicly Available**: `Yes`
   - **Add Field** → **Response Mode**: `Streaming`
3. **Chat URL kopieren** — diese wird in unified-ui als "Chat URL" eingetragen

### 2. AI Agent Node (oder andere Logik)

Füge deine Workflow-Logik hinzu, z.B.:
- **AI Agent** Node mit Azure OpenAI / OpenAI
- **HTTP Request** Nodes
- **Code** Nodes
- etc.

### 3. Respond to Webhook Node (WICHTIG für Traces!)

**Dieser Node ist erforderlich, damit unified-ui die Traces importieren kann.**

1. Node hinzufügen: **"Respond to Webhook"**
2. Einstellungen:
   - **Respond with**: `JSON`
   - **Response Body**: Klicke auf das Feld und wähle **"Expression"** (oder setze `=` als Prefix)
   - Inhalt:
     ```
     ={{ { "executionId": $execution.id } }}
     ```
   - **Add Option** → **Response Mode**: `Streaming`
3. Node umbenennen zu: `Respond ExecutionID`

> **Wichtig**: Das `=` am Anfang aktiviert den Expression-Modus! Ohne Expression wird `{{ $execution.id }}` als String zurückgegeben, nicht als echte ID.

---

## unified-ui Chat Agent Konfiguration

### Erforderliche Felder

| Feld | Wert | Beschreibung |
|------|------|--------------|
| **API Version** | `v1` | Aktuell nur v1 unterstützt |
| **Workflow Type** | `Chat Agent Workflow` | Standard für Chat Agents |
| **Chat URL** | `http://localhost:5678/webhook/.../chat` | Die kopierte Chat URL aus n8n |
| **Workflow Endpoint** | `http://localhost:5678/workflow/{ID}` | Workflow-URL aus n8n Browser |
| **API Key Credential** | N8N API Key | Für Trace-Import erforderlich |
| **Chat Auth Credential** | (Optional) | Basic Auth falls Workflow geschützt |

### N8N API Key erstellen

1. In n8n: **Settings** → **API** → **Create API Key**
2. In unified-ui: **Credentials** → **New** → **API Key**
3. Secret einfügen und speichern

---

## Trace-Import Flow

Nach korrekter Konfiguration werden Traces automatisch importiert:

```
1. User sendet Nachricht in unified-ui
   ↓
2. Agent Service ruft n8n Chat Webhook auf
   (mit sessionId = conversationId)
   ↓
3. n8n führt Workflow aus
   ↓
4. n8n gibt Response zurück:
   { "output": "AI Antwort", "executionId": "123" }
   ↓
5. Agent Service parsed executionId
   ↓
6. Agent Service ruft n8n API auf:
   GET /api/v1/executions/123?includeData=true
   ↓
7. Trace wird in unified-ui gespeichert
   ↓
8. Trace ist im Frontend sichtbar (Tracing Tab)
```

---

## Troubleshooting

### Traces werden nicht importiert

1. **API Key korrekt?**
   - Prüfe ob N8N API Key Credential in unified-ui gespeichert ist
   - Teste: `curl -H "X-N8N-API-KEY: {key}" http://localhost:5678/api/v1/executions`

2. **executionId in Response?**
   - Prüfe n8n Response im Browser DevTools (Network Tab)
   - Muss `{"executionId": "..."}` enthalten

3. **Workflow Endpoint korrekt?**
   - Format: `http://host:5678/workflow/{workflowId}`
   - workflowId aus n8n URL kopieren

4. **Docker Networking?**
   - Wenn Agent Service in Docker läuft: `localhost` → `host.docker.internal`

### Leere Antwort im Chat

- Prüfe ob `output` im Respond to Webhook Node korrekt referenziert wird
- Expression muss `{{ $json.output }}` sein (vom AI Agent Node)

### Connection refused

- n8n nicht erreichbar
- Bei Docker: `host.docker.internal:5678` statt `localhost:5678` verwenden

---

## Beispiel: Minimaler Chat Workflow

```json
{
  "nodes": [
    {
      "name": "When chat message received",
      "type": "@n8n/n8n-nodes-langchain.chatTrigger",
      "parameters": {
        "public": true,
        "options": {
          "responseMode": "streaming"
        }
      }
    },
    {
      "name": "AI Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "parameters": {
        "options": {
          "systemMessage": "Du bist ein hilfreicher Assistent."
        }
      }
    },
    {
      "name": "Respond ExecutionID",
      "type": "n8n-nodes-base.respondToWebhook",
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { \"output\": $json.output, \"executionId\": $execution.id } }}",
        "options": {
          "responseMode": "streaming"
        }
      }
    }
  ]
}
```

---

## Referenzen

- [N8N Chat Trigger Dokumentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.chattrigger/)
- [N8N API Dokumentation](https://docs.n8n.io/api/)
- [unified-ui Agent Service POC](../../unified-ui-agent-service/poc/n8n/001_workflow-stream/)
