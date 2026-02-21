# Konzept: Unified File-Uploads im POST /messages Endpoint

## 1. Übersicht

Dieses Konzept beschreibt, wie File-Uploads im Agent-Service für verschiedene AI-Agent-Systeme implementiert werden können. Ziel ist ein einheitliches API-Interface, das über das Factory Pattern agent-spezifische Konvertierungen abstrahiert.

### 1.1 Unterstützte Agent-Systeme

| Agent-System | File-Upload Support | Implementierungsstrategie |
|--------------|---------------------|---------------------------|
| **Microsoft Foundry** | ✅ Nativ | Multimodal Responses API |
| **N8N** | ⚠️ Workaround | Base64 Files via WebHook Body |
| **Copilot** (Zukunft) | TBD | Geplant |
| **Custom REST** (Zukunft) | TBD | Erweiterbar |

### 1.2 Design-Prinzipien

1. **Einheitliche API-Struktur**: Ein Request-Format für alle Agent-Typen
2. **Factory Pattern für Konvertierung**: Jeder Agent-Typ hat seinen eigenen Adapter
3. **Erweiterbarkeit**: Neue Agent-Systeme können einfach hinzugefügt werden
4. **Backward-Compatibility**: Bestehende Requests funktionieren weiterhin

---

## 2. Agent-Spezifische Analyse

### 2.1 Microsoft Foundry API

Die Microsoft Foundry Responses API (`POST /openai/responses`) unterstützt **native multimodale Inputs**. Das `input`-Feld kann entweder ein String oder ein Array von Content-Items sein.

#### Unterstützte Input-Content-Typen

| Type | Beschreibung | Felder |
|------|--------------|--------|
| `input_text` | Text-Eingabe | `text` (string) |
| `input_image` | Bild-Eingabe | `image_url` (URL oder Base64 Data-URL), `file_id`, `detail` (low/high/auto) |
| `input_file` | Datei-Eingabe | `file_data` (Base64), `file_id`, `filename` |
| `input_audio` | Audio-Eingabe | `data` (Base64), `format` (mp3/wav) |

#### Beispiel: Foundry Request mit Multimodal-Input

```json
{
  "agent": {
    "type": "agent_reference",
    "name": "my-agent"
  },
  "conversation": "conv_123",
  "input": [
    {
      "role": "user",
      "content": [
        { "type": "input_text", "text": "Was siehst du auf diesem Bild?" },
        { "type": "input_image", "image_url": "data:image/png;base64,iVBORw0KGgo..." }
      ]
    }
  ],
  "stream": true
}
```

### 2.2 N8N Chat Trigger

Der N8N "Chat Trigger" Node hat **keine native File-Upload-Unterstützung**. Der Standard-Request enthält nur `chatInput` und `sessionId`. 

#### Aktueller N8N Request (ohne Files)

```json
{
  "chatInput": "Hallo, wie geht es dir?",
  "sessionId": "session_123"
}
```

#### Workaround-Strategie für N8N

Da N8N Webhooks beliebige JSON-Daten akzeptieren können, implementieren wir einen **erweiterten Request-Body** mit einem `files`-Array. Der N8N-Workflow muss entsprechend angepasst werden, um diese Files zu verarbeiten:

**Option A: Files im Request-Body (Empfohlen)**
```json
{
  "chatInput": "Analysiere diese Datei",
  "sessionId": "session_123",
  "files": [
    {
      "type": "image",
      "data": "data:image/png;base64,iVBORw0KGgo...",
      "filename": "screenshot.png",
      "mimeType": "image/png"
    }
  ]
}
```

**Option B: Vision-Model mit Base64 im Text**
```json
{
  "chatInput": "Analysiere dieses Bild: [IMAGE:data:image/png;base64,iVBORw0KGgo...]",
  "sessionId": "session_123"
}
```

#### N8N Workflow-Anforderungen

Der N8N-Workflow muss folgende Schritte implementieren:
1. Files aus dem Request extrahieren
2. Base64 zu Binary konvertieren (bei Bedarf)
3. Files an das passende AI-Model weiterleiten (z.B. GPT-4 Vision, Claude Vision)

---

## 3. Aktuelle Implementierung im Agent-Service

### 3.1 Aktueller Request-Body (`POST /messages`)

```go
// SendMessageRequest - aktuell
type SendMessageRequest struct {
    ConversationID    string         `json:"conversationId,omitempty"`
    ChatAgentID     string         `json:"chatAgentId" binding:"required"`
    ExtConversationID string         `json:"extConversationId,omitempty"`
    Message           MessageContent `json:"message" binding:"required"`
    InvokeConfig      InvokeConfig   `json:"invokeConfig,omitempty"`
}

type MessageContent struct {
    Content     string   `json:"content" binding:"required,min=1,max=32000"`
    Attachments []string `json:"attachments,omitempty"` // URLs - Legacy
}
```

### 3.2 Aktuelle Agent-Spezifische Payloads

#### Foundry (aktuell)
```go
type FoundryRequestPayload struct {
    Agent        FoundryAgentPayload `json:"agent"`
    Conversation string              `json:"conversation,omitempty"`
    Input        string              `json:"input"`  // <-- Nur String!
    Stream       bool                `json:"stream"`
}
```

#### N8N (aktuell)
```go
type ChatRequest struct {
    ChatInput string `json:"chatInput"`
    SessionID string `json:"sessionId"`
}
```

**Problem**: Beide Implementierungen unterstützen nur Text-Inhalte, keine Files.

---

## 4. Unified Design mit Factory Pattern

### 4.1 Neue Unified API-Struktur

Das Frontend sendet einen **einheitlichen Request**, unabhängig vom Agent-Typ:

```go
// FileAttachment repräsentiert ein hochgeladenes File (einheitlich für alle Agents)
type FileAttachment struct {
    // Type: "image", "file", "audio"
    Type     string `json:"type" binding:"required,oneof=image file audio"`
    
    // Für Bilder: URL oder Base64 Data-URL
    ImageURL string `json:"imageUrl,omitempty"`
    
    // Für Dateien/Audio: Base64-encoded Inhalt
    FileData string `json:"fileData,omitempty"`
    
    // Dateiname (empfohlen)
    Filename string `json:"filename,omitempty"`
    
    // MIME-Type (empfohlen)
    MimeType string `json:"mimeType,omitempty"`
    
    // Für Bilder: Detail-Level (low, high, auto)
    Detail string `json:"detail,omitempty"`
}

// MessageContent - erweitert (unified)
type MessageContent struct {
    Content     string           `json:"content" binding:"required,min=1,max=32000"`
    Attachments []string         `json:"attachments,omitempty"` // Legacy: URLs
    Files       []FileAttachment `json:"files,omitempty"`       // NEU: Inline files
}
```

### 4.2 FileInput Interface (Core Abstraction)

```go
// internal/services/agents/types.go

// FileInput represents a file attachment in a unified format
type FileInput struct {
    Type     string // "image", "file", "audio"
    ImageURL string // For images: Data-URL or external URL
    FileData string // For files/audio: Base64 encoded data
    Filename string
    MimeType string
    Detail   string // For images: "low", "high", "auto"
}

// InvokeRequest - erweitert um Files
type InvokeRequest struct {
    ConversationID string
    Message        string
    SessionID      string
    ChatHistory    []models.ChatHistoryEntry
    ContextData    map[string]string
    Files          []FileInput  // NEU: Unified file attachments
}
```

### 4.3 Factory Pattern - FileConverter Interface

```go
// internal/services/agents/converter.go

// FileConverter converts unified FileInput to agent-specific format
type FileConverter interface {
    // SupportsFiles returns true if the agent type supports file attachments
    SupportsFiles() bool
    
    // ConvertFiles converts FileInput slice to agent-specific payload structure
    // Returns the modified payload that should be sent to the agent
    ConvertFiles(message string, files []FileInput) (interface{}, error)
}
```

### 4.4 Foundry FileConverter Implementation

```go
// internal/services/agents/foundry/converter.go

type FoundryFileConverter struct{}

func (c *FoundryFileConverter) SupportsFiles() bool {
    return true
}

func (c *FoundryFileConverter) ConvertFiles(message string, files []FileInput) (interface{}, error) {
    if len(files) == 0 {
        // Return simple string for backward compatibility
        return message, nil
    }
    
    // Build multimodal content array
    content := []FoundryInputContent{
        {Type: "input_text", Text: message},
    }
    
    for _, file := range files {
        switch file.Type {
        case "image":
            content = append(content, FoundryInputContent{
                Type:     "input_image",
                ImageURL: file.ImageURL,
                Detail:   file.Detail,
            })
        case "file":
            content = append(content, FoundryInputContent{
                Type:     "input_file",
                FileData: file.FileData,
                Filename: file.Filename,
            })
        case "audio":
            content = append(content, FoundryInputContent{
                Type:   "input_audio",
                Data:   file.FileData,
                Format: extractAudioFormat(file.MimeType),
            })
        }
    }
    
    return []FoundryInputMessage{
        {Role: "user", Content: content},
    }, nil
}
```

### 4.5 N8N FileConverter Implementation

```go
// internal/services/agents/n8n/converter.go

type N8NFileConverter struct{}

func (c *N8NFileConverter) SupportsFiles() bool {
    return true // Via custom webhook payload
}

func (c *N8NFileConverter) ConvertFiles(message string, files []FileInput) (interface{}, error) {
    if len(files) == 0 {
        // Standard N8N request without files
        return &ChatRequestWithFiles{
            ChatInput: message,
        }, nil
    }
    
    // Extended N8N request with files
    n8nFiles := make([]N8NFileAttachment, 0, len(files))
    for _, file := range files {
        n8nFiles = append(n8nFiles, N8NFileAttachment{
            Type:     file.Type,
            Data:     getFileData(file), // ImageURL or FileData
            Filename: file.Filename,
            MimeType: file.MimeType,
        })
    }
    
    return &ChatRequestWithFiles{
        ChatInput: message,
        Files:     n8nFiles,
    }, nil
}

// ChatRequestWithFiles extends the standard N8N chat request
type ChatRequestWithFiles struct {
    ChatInput string              `json:"chatInput"`
    SessionID string              `json:"sessionId,omitempty"`
    Files     []N8NFileAttachment `json:"files,omitempty"`
}

type N8NFileAttachment struct {
    Type     string `json:"type"`     // image, file, audio
    Data     string `json:"data"`     // Base64 data or Data-URL
    Filename string `json:"filename"`
    MimeType string `json:"mimeType"`
}
```

### 4.6 Factory Integration

```go
// internal/services/agents/factory.go - erweitert

// GetFileConverter returns the appropriate FileConverter for the agent type
func (f *Factory) GetFileConverter(agentType platform.AgentType) FileConverter {
    switch agentType {
    case platform.AgentTypeFoundry:
        return &foundry.FoundryFileConverter{}
    case platform.AgentTypeN8N:
        return &n8n.N8NFileConverter{}
    case platform.AgentTypeCopilot:
        // Future: return &copilot.CopilotFileConverter{}
        return &NoopFileConverter{}
    default:
        return &NoopFileConverter{}
    }
}

// NoopFileConverter for agents that don't support files
type NoopFileConverter struct{}

func (c *NoopFileConverter) SupportsFiles() bool { return false }

func (c *NoopFileConverter) ConvertFiles(message string, files []FileInput) (interface{}, error) {
    if len(files) > 0 {
        return nil, errors.New("this agent type does not support file attachments")
    }
    return message, nil
}
```

---

## 5. Implementierungsplan

### 5.1 Phase 1: Core Types und Interfaces

#### 5.1.1 Neue Types (internal/api/handlers/messages.go)

```go
// FileAttachment repräsentiert ein hochgeladenes File (API Layer)
type FileAttachment struct {
    Type     string `json:"type" binding:"required,oneof=image file audio"`
    ImageURL string `json:"imageUrl,omitempty"`
    FileData string `json:"fileData,omitempty"`
    Filename string `json:"filename,omitempty"`
    MimeType string `json:"mimeType,omitempty"`
    Detail   string `json:"detail,omitempty"`
}

// MessageContent - erweitert mit Files
type MessageContent struct {
    Content     string           `json:"content" binding:"required,min=1,max=32000"`
    Attachments []string         `json:"attachments,omitempty"` // Legacy URLs
    Files       []FileAttachment `json:"files,omitempty"`       // NEW: Inline files
}
```

#### 5.1.2 Core FileInput Type (internal/services/agents/types.go)

```go
// FileInput represents a unified file attachment
type FileInput struct {
    Type     string // "image", "file", "audio"
    ImageURL string // For images: Data-URL or external URL
    FileData string // For files/audio: Base64 encoded data
    Filename string
    MimeType string
    Detail   string // For images: "low", "high", "auto"
}

// InvokeRequest - erweitert um Files (bereits in types.go)
type InvokeRequest struct {
    ConversationID string
    Message        string
    SessionID      string
    ChatHistory    []models.ChatHistoryEntry
    ContextData    map[string]string
    Files          []FileInput  // NEU
}
```

### 5.2 Phase 2: Foundry-Spezifische Implementation

#### 5.2.1 Foundry Types (internal/services/agents/foundry/types.go)

```go
// FoundryInputContent für multimodale Inputs
type FoundryInputContent struct {
    Type     string `json:"type"`
    Text     string `json:"text,omitempty"`
    ImageURL string `json:"image_url,omitempty"`
    FileData string `json:"file_data,omitempty"`
    FileID   string `json:"file_id,omitempty"`
    Filename string `json:"filename,omitempty"`
    Detail   string `json:"detail,omitempty"`
    Data     string `json:"data,omitempty"`
    Format   string `json:"format,omitempty"`
}

// FoundryInputMessage für strukturierte Inputs
type FoundryInputMessage struct {
    Role    string                `json:"role"`
    Content []FoundryInputContent `json:"content"`
}

// FoundryRequestPayload - erweitert für multimodal input
type FoundryRequestPayload struct {
    Agent        FoundryAgentPayload   `json:"agent"`
    Conversation string                `json:"conversation,omitempty"`
    Input        interface{}           `json:"input"` // String ODER []FoundryInputMessage
    Stream       bool                  `json:"stream"`
}
```

#### 5.2.2 Foundry WorkflowClient Update

```go
func (c *WorkflowClient) InvokeStreamReader(ctx context.Context, req *InvokeRequest) (StreamReader, error) {
    url := fmt.Sprintf("%s/openai/responses?api-version=%s", c.projectEndpoint, c.apiVersion)

    var payload interface{}

    if len(req.Files) > 0 {
        // Multimodal Request mit Files
        content := []FoundryInputContent{
            {Type: "input_text", Text: req.Message},
        }
        
        for _, file := range req.Files {
            switch file.Type {
            case "image":
                content = append(content, FoundryInputContent{
                    Type:     "input_image",
                    ImageURL: file.ImageURL,
                    Detail:   file.Detail,
                })
            case "file":
                content = append(content, FoundryInputContent{
                    Type:     "input_file",
                    FileData: file.FileData,
                    Filename: file.Filename,
                })
            case "audio":
                content = append(content, FoundryInputContent{
                    Type:   "input_audio",
                    Data:   file.FileData,
                    Format: file.MimeType, // mp3 or wav
                })
            }
        }

        payload = &FoundryRequestPayloadMultimodal{
            Agent: FoundryAgentPayload{
                Type: "agent_reference",
                Name: c.agentName,
            },
            Conversation: req.ExtConversationID,
            Input: []FoundryInputMessage{
                {
                    Role:    "user",
                    Content: content,
                },
            },
            Stream: true,
        }
    } else {
        // Standard Text-only Request (backward compatible)
        payload = &FoundryRequestPayload{
            Agent: FoundryAgentPayload{
                Type: "agent_reference",
                Name: c.agentName,
            },
            Conversation: req.ExtConversationID,
            Input:        req.Message,
            Stream:       true,
        }
    }

    body, err := json.Marshal(payload)
    // ... rest of implementation
}
```

### 5.3 Phase 3: N8N-Spezifische Implementation

#### 5.3.1 N8N Types (internal/services/agents/n8n/types.go)

```go
// ChatRequestWithFiles extends the standard N8N chat request
type ChatRequestWithFiles struct {
    ChatInput string              `json:"chatInput"`
    SessionID string              `json:"sessionId,omitempty"`
    Files     []N8NFileAttachment `json:"files,omitempty"`
}

// N8NFileAttachment represents a file in N8N compatible format
type N8NFileAttachment struct {
    Type     string `json:"type"`     // image, file, audio
    Data     string `json:"data"`     // Base64 data or Data-URL
    Filename string `json:"filename"`
    MimeType string `json:"mimeType"`
}
```

#### 5.3.2 N8N ChatWorkflowClient Update

```go
// internal/services/agents/n8n/chat_workflow.go

func (c *ChatWorkflowClient) buildRequestPayload(req *InvokeRequest) interface{} {
    if len(req.Files) > 0 {
        // Extended request with files
        files := make([]N8NFileAttachment, 0, len(req.Files))
        for _, file := range req.Files {
            data := file.ImageURL
            if data == "" {
                data = file.FileData
            }
            files = append(files, N8NFileAttachment{
                Type:     file.Type,
                Data:     data,
                Filename: file.Filename,
                MimeType: file.MimeType,
            })
        }
        return &ChatRequestWithFiles{
            ChatInput: req.Message,
            SessionID: req.SessionID,
            Files:     files,
        }
    }
    
    // Standard request without files
    return &ChatRequest{
        ChatInput: req.Message,
        SessionID: req.SessionID,
    }
}
```

### 5.4 Phase 4: Handler Integration

#### 5.4.1 SendMessage Handler (internal/api/handlers/messages_send.go)

```go
func (h *MessagesHandler) SendMessage(c *gin.Context) {
    // ... existing code ...

    // Convert FileAttachment to FileInput (unified format)
    var files []agents.FileInput
    for _, f := range req.Message.Files {
        files = append(files, agents.FileInput{
            Type:     f.Type,
            ImageURL: f.ImageURL,
            FileData: f.FileData,
            Filename: f.Filename,
            MimeType: f.MimeType,
            Detail:   f.Detail,
        })
    }

    // Create invoke request with files
    invokeReq := &agents.InvokeRequest{
        ConversationID: conversationID,
        Message:        req.Message.Content,
        SessionID:      sessionID,
        Files:          files,  // Unified files passed to adapter
    }

    // The factory pattern handles agent-specific conversion
    // ...
}
```

### 5.5 Phase 5: Persistierung der File-Metadaten

```go
// Erweiterte AttachmentMetadata im Message-Model
type AttachmentMetadata struct {
    FileName     string `json:"fileName" bson:"fileName"`
    FileType     string `json:"fileType" bson:"fileType"`        // image, file, audio
    FileSize     int64  `json:"fileSize" bson:"fileSize"`
    FileCategory string `json:"fileCategory" bson:"fileCategory"`
    MimeType     string `json:"mimeType" bson:"mimeType"`
}
```

---

## 6. API-Dokumentation

### 6.1 Unified POST /messages Request

Der Request ist **identisch für alle Agent-Typen**. Die Konvertierung erfolgt intern.

```http
POST /api/v1/agent-service/tenants/{tenantId}/conversation/messages
Content-Type: application/json
Authorization: Bearer {token}
X-Microsoft-Foundry-API-Key: {foundry-api-key}  // Optional, nur für Foundry

{
  "chatAgentId": "app-123",
  "conversationId": "conv-456",
  "message": {
    "content": "Was siehst du auf diesem Bild?",
    "files": [
      {
        "type": "image",
        "imageUrl": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA...",
        "filename": "screenshot.png",
        "mimeType": "image/png",
        "detail": "high"
      }
    ]
  },
  "invokeConfig": {
    "chatHistoryMessageCount": 10
  }
}
```

### 6.2 Beispiele für verschiedene File-Typen

#### Bild mit Base64 Data-URL

```json
{
  "type": "image",
  "imageUrl": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "detail": "high"
}
```

#### Bild mit externer URL

```json
{
  "type": "image",
  "imageUrl": "https://example.com/images/photo.jpg",
  "detail": "auto"
}
```

#### PDF-Datei

```json
{
  "type": "file",
  "fileData": "JVBERi0xLjQKJeLjz9MKNCAwIG9iago8PC9...",
  "filename": "document.pdf",
  "mimeType": "application/pdf"
}
```

#### Audio-Datei

```json
{
  "type": "audio",
  "fileData": "//uQxAAAAAANIAAAAAExBTUUzLjk5Lr...",
  "filename": "recording.mp3",
  "mimeType": "audio/mp3"
}
```

---

## 7. Validierung & Limits

### 7.1 Unified Limits (Agent-übergreifend)

| Parameter | Foundry | N8N | Begründung |
|-----------|---------|-----|------------|
| Max. Dateigröße (Base64) | 10MB | 10MB | API-Payload-Grenzen |
| Max. Files pro Request | 5 | 5 | Performance |
| Bild-Formate | PNG, JPEG, GIF, WEBP | PNG, JPEG, GIF, WEBP | Model Support |
| Audio-Formate | MP3, WAV | MP3, WAV | Model Support |
| Dokument-Formate | PDF, TXT, DOCX, MD | Abhängig vom Workflow | Agent-spezifisch |

### 7.2 Validierungslogik

```go
func validateFileAttachment(file *FileAttachment, agentType string) error {
    // Universal validation
    switch file.Type {
    case "image":
        if file.ImageURL == "" {
            return errors.New("imageUrl is required for image type")
        }
        if err := validateBase64Size(file.ImageURL, 10*1024*1024); err != nil {
            return err
        }
    case "file":
        if file.FileData == "" {
            return errors.New("fileData is required for file type")
        }
        if err := validateBase64Size(file.FileData, 10*1024*1024); err != nil {
            return err
        }
    case "audio":
        if file.FileData == "" {
            return errors.New("fileData is required for audio type")
        }
    default:
        return errors.New("invalid file type: must be image, file, or audio")
    }
    return nil
}

func validateBase64Size(data string, maxBytes int) error {
    // Extract base64 data from Data-URL if present
    base64Data := data
    if idx := strings.Index(data, ","); idx != -1 {
        base64Data = data[idx+1:]
    }
    
    decoded, err := base64.StdEncoding.DecodeString(base64Data)
    if err != nil {
        return errors.New("invalid base64 encoding")
    }
    if len(decoded) > maxBytes {
        return fmt.Errorf("file size exceeds %dMB limit", maxBytes/(1024*1024))
    }
    return nil
}
```

---

## 8. Backward Compatibility

Die Änderungen sind **vollständig backward-compatible**:

1. Das neue `files` Feld ist optional (`omitempty`)
2. Bestehende Requests ohne `files` funktionieren weiterhin für alle Agent-Typen
3. Legacy `attachments` (URLs) bleiben erhalten
4. Agents, die keine Files unterstützen, geben einen klaren Fehler zurück
5. Die Factory-Pattern-Erweiterung ändert keine bestehenden Interfaces

---

## 9. Frontend-Integration

### 9.1 TypeScript Types (src/api/types.ts)

```typescript
export interface FileAttachment {
  type: 'image' | 'file' | 'audio';
  imageUrl?: string;  // Für Bilder: Data-URL oder externe URL
  fileData?: string;  // Für Files/Audio: Base64
  filename?: string;
  mimeType?: string;
  detail?: 'low' | 'high' | 'auto';
}

export interface MessageContent {
  content: string;
  attachments?: string[];  // Legacy URLs
  files?: FileAttachment[];
}

export interface SendMessageRequest {
  chatAgentId: string;
  conversationId?: string;
  message: MessageContent;
  invokeConfig?: InvokeConfig;
  extConversationId?: string;
}
```

### 9.2 File Conversion Utility (src/utils/fileUtils.ts)

```typescript
export async function fileToAttachment(file: File): Promise<FileAttachment> {
  const data = await fileToBase64(file);
  const type = getFileType(file.type);
  
  return {
    type,
    [type === 'image' ? 'imageUrl' : 'fileData']: data,
    filename: file.name,
    mimeType: file.type,
    detail: type === 'image' ? 'auto' : undefined,
  };
}

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function getFileType(mimeType: string): 'image' | 'file' | 'audio' {
  if (mimeType.startsWith('image/')) return 'image';
  if (mimeType.startsWith('audio/')) return 'audio';
  return 'file';
}
```

### 9.3 useChat Hook Update (src/pages/ConversationsPage/hooks/useChat.ts)

```typescript
const handleSendMessage = useCallback(async (content: string, attachments?: File[]) => {
  // ... existing validation ...

  // Convert File[] to FileAttachment[]
  let files: FileAttachment[] | undefined;
  if (attachments && attachments.length > 0) {
    files = await Promise.all(attachments.map(fileToAttachment));
  }

  // Build request with files
  const requestBody = {
    conversationId: activeConversationId,
    chatAgentId: selectedChatAgentId,
    message: {
      content,
      files,  // NEW: Include converted files
    },
    invokeConfig: { chatHistoryMessageCount: 10 },
    extConversationId: activeExtConversationId,
  };

  // ... rest of send logic ...
}, [/* dependencies */]);
```

---

## 10. Migrations- und Rollout-Plan

### Phase 1: Backend Core (1-2 Sprints)
1. ✅ FileAttachment und FileInput Types hinzufügen
2. ✅ FileConverter Interface definieren
3. ✅ Foundry FileConverter implementieren
4. ✅ N8N FileConverter implementieren
5. ✅ Factory um GetFileConverter erweitern
6. ⬜ Validierungslogik implementieren
7. ⬜ Unit-Tests schreiben

### Phase 2: Agent-Integration (1 Sprint)
1. ⬜ Foundry WorkflowClient für multimodal Input anpassen
2. ⬜ N8N ChatWorkflowClient für Files anpassen
3. ⬜ SendMessage Handler erweitern
4. ⬜ Integration-Tests

### Phase 3: API-Dokumentation (0.5 Sprint)
1. ⬜ Swagger/OpenAPI aktualisieren
2. ⬜ Inline-Dokumentation ergänzen
3. ⬜ N8N Workflow-Dokumentation für File-Handling

### Phase 4: Frontend-Integration (1 Sprint)
1. ⬜ TypeScript Types erweitern
2. ⬜ fileToAttachment Utility
3. ⬜ useChat Hook aktualisieren (Files nicht mehr ignorieren)
4. ⬜ ChatInput Vorschau für Attachments (bereits vorhanden)

### Phase 5: Testing & Rollout (1 Sprint)
1. ⬜ E2E-Tests mit Foundry und N8N
2. ⬜ Load-Testing für große Files
3. ⬜ Staged Rollout (Feature Flag)

---

## 11. N8N Workflow-Konfiguration

Damit N8N-Workflows File-Uploads verarbeiten können, müssen sie entsprechend konfiguriert werden:

### 11.1 Beispiel N8N Workflow mit File-Processing

```json
{
  "nodes": [
    {
      "name": "Chat Trigger",
      "type": "n8n-nodes-langchain.chatTrigger",
      "parameters": {
        "mode": "embedded"
      }
    },
    {
      "name": "Process Files",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// Extract files from request\nconst files = $input.item.json.files || [];\nconst chatInput = $input.item.json.chatInput;\n\n// Process each file (e.g., extract text from images)\nfor (const file of files) {\n  if (file.type === 'image') {\n    // Send to vision model\n  }\n}\n\nreturn [{ json: { chatInput, files } }];"
      }
    },
    {
      "name": "AI Agent",
      "type": "n8n-nodes-langchain.agent",
      "parameters": {
        "text": "={{ $json.chatInput }}"
      }
    }
  ]
}
```

### 11.2 Empfehlungen für N8N-Nutzer

1. **Vision-Models verwenden**: Für Bild-Attachments GPT-4 Vision oder Claude mit Vision
2. **File-Vorverarbeitung**: PDFs mit Extract-Text-Node verarbeiten
3. **Rate Limiting**: Bei vielen File-Uploads eigenes Rate-Limiting implementieren

---

## 12. Erweiterbarkeit für zukünftige Agent-Systeme

### 12.1 Neuen Agent hinzufügen

1. **FileConverter implementieren**:
```go
// internal/services/agents/newagent/converter.go
type NewAgentFileConverter struct{}

func (c *NewAgentFileConverter) SupportsFiles() bool {
    return true // oder false
}

func (c *NewAgentFileConverter) ConvertFiles(message string, files []FileInput) (interface{}, error) {
    // Agent-spezifische Konvertierung
}
```

2. **Factory erweitern**:
```go
case platform.AgentTypeNewAgent:
    return &newagent.NewAgentFileConverter{}
```

3. **WorkflowClient implementieren** (falls Files unterstützt werden)

### 12.2 Geplante Erweiterungen

| Agent-System | Status | Priorität |
|--------------|--------|-----------|
| Microsoft Copilot | 🔄 Geplant | Mittel |
| LangChain/Custom REST | 🔄 Geplant | Niedrig |
| Azure OpenAI Direct | 💡 Idee | Niedrig |

---

## 13. Offene Punkte / Diskussion

1. **Pre-Upload für große Dateien**: Soll ein separater `/files` Endpoint implementiert werden für Files > 10MB?

2. **File Storage**: Sollen die hochgeladenen Files persistiert werden (Azure Blob Storage) oder nur transient weitergeleitet werden?

3. **Rate Limiting**: Separates Rate Limiting für File-Uploads (z.B. max 10 Files/Minute)?

4. **N8N WebSocket**: Falls N8N WebSocket-Support bekommt, könnte File-Streaming möglich werden.

5. **Audio-Transcription**: Soll der Agent-Service Audio zu Text konvertieren bevor es an Agents gesendet wird?

---

## 14. Zusammenfassung

Dieses Konzept ermöglicht ein **unified File-Upload System** für den POST /messages Endpoint:

| Feature | Status |
|---------|--------|
| **Einheitliche API** | ✅ Ein Request-Format für alle Agents |
| **Microsoft Foundry Support** | ✅ Native multimodal API |
| **N8N Support** | ✅ Via erweitertem WebHook Body |
| **Factory Pattern** | ✅ Erweiterbar für neue Agent-Typen |
| **Backward Compatibility** | ✅ Bestehende Requests funktionieren |
| **Frontend Integration** | ✅ Files werden an API gesendet |
| **Validierung** | ✅ Unified + agent-spezifisch |

### Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend                               │
│  ChatInput → fileToAttachment() → SendMessageRequest        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Service API                         │
│  POST /messages → FileAttachment[] → Validation             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Factory Pattern                           │
│  GetFileConverter(agentType) → FileConverter.ConvertFiles() │
└─────────────────────────────────────────────────────────────┘
              │                              │
              ▼                              ▼
┌─────────────────────────┐    ┌─────────────────────────────┐
│   FoundryFileConverter  │    │      N8NFileConverter       │
│   → FoundryInputContent │    │   → ChatRequestWithFiles    │
│   → multimodal API      │    │   → extended webhook body   │
└─────────────────────────┘    └─────────────────────────────┘
```
