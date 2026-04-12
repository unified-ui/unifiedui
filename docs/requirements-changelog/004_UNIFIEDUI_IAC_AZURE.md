# 004 — unified-ui IaC Azure v1.0.0

> **Status:** DRAFT  
> **Scope:** unifiedui-iac (neues Repository), alle Service-Repositories (CI/CD)  
> **Goal:** Terraform-basiertes IaC für serverlose Azure-Deployment mit config.yaml-gesteuerter Konfiguration

---

## Übersicht

Aufbau des `unifiedui-iac` Repositories für Infrastructure-as-Code Deployment von unified-ui auf Azure. Fokus auf:
- **100% Serverless** für Dev-Environment
- **Config-driven** durch YAML mit JSON Schema Validation
- **Lokale Skripte** für Deployment (CI/CD-unabhängig)
- **GitHub Container Registry (GHCR)** für Docker Images
- **System-assigned Managed Identities** für alle Services

---

## Architektur (Phase 1 — Dev/Serverless)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Resource Group: rg-unifiedui-dev-weu-001             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────┐     ┌──────────────────────────────────────┐   │
│  │ Static Web App     │     │  Container Apps Environment          │   │
│  │ stapp-unifiedui-   │     │  cae-unifiedui-dev-weu-001           │   │
│  │ dev-weu-001        │     │                                       │   │
│  │                    │     │  ┌────────────┐  ┌────────────────┐  │   │
│  │  React SPA         │────▶│  │ ca-platform│  │   ca-agent     │  │   │
│  │  (Frontend)        │     │  │   :8000    │  │     :8085      │  │   │
│  │                    │     │  └────────────┘  └────────────────┘  │   │
│  └────────────────────┘     │                                       │   │
│                              │  ┌────────────┐  ┌────────────────┐  │   │
│                              │  │  ca-redis  │  │   ca-n8n       │  │   │
│                              │  │   :6379    │  │   :5678 (opt)  │  │   │
│                              │  │ (container)│  │                │  │   │
│                              │  └────────────┘  └────────────────┘  │   │
│                              └──────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────┐  ┌─────────────────────┐                       │
│  │ sql-unifiedui-dev-  │  │ sql-n8n-dev-weu-001 │  ← Separate Server   │
│  │ weu-001 (Serverless)│  │ (Serverless)        │                       │
│  │ └─ db: unifiedui    │  │ └─ db: n8n          │                       │
│  └─────────────────────┘  └─────────────────────┘                       │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ cdb-unifiedui-dev-weu-001 (Serverless, NoSQL API)               │   │
│  │ └─ database: unifiedui │ containers: traces, sessions, messages │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐                     │
│  │ st-unifiedui-dev-    │  │ st-unifiedui-tfstate │  ← TF Backend      │
│  │ weu-001 (Files)      │  │ dev-weu-001          │                     │
│  │ └─ container: uploads│  │ └─ container: tfstate│                     │
│  └──────────────────────┘  └──────────────────────┘                     │
│                                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐                     │
│  │ kv-unifiedui-app-    │  │ kv-unifiedui-infra-  │                     │
│  │ dev-weu-001          │  │ dev-weu-001          │                     │
│  │ (App-managed secrets)│  │ (Env refs, TF vars)  │                     │
│  └──────────────────────┘  └──────────────────────┘                     │
│                                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐                     │
│  │ sb-unifiedui-dev-    │  │ log-unifiedui-dev-   │                     │
│  │ weu-001 (optional)   │  │ weu-001              │                     │
│  │ (Service Bus)        │  │ (Log Analytics)      │                     │
│  └──────────────────────┘  └──────────────────────┘                     │
│                                                                          │
│  Note: Alle Container Apps nutzen System-assigned Managed Identities    │
│  für Zugriff auf Key Vault, SQL, CosmosDB, Storage                      │
└─────────────────────────────────────────────────────────────────────────┘
```

**Entra ID App Registration** (erstellt via Bootstrap):
```
┌─────────────────────────────────────────────────────────────────────────┐
│  App Registration: app-unifiedui-{env}                                   │
│                                                                          │
│  ├─ Application (Client) ID                                             │
│  ├─ API Permissions:                                                    │
│  │   └─ Microsoft Graph: User.Read (delegated)                          │
│  ├─ Expose an API:                                                      │
│  │   └─ Scope: api://{client-id}/access_as_user                         │
│  ├─ Authentication:                                                     │
│  │   ├─ SPA Redirect URIs: https://{frontend-url}                       │
│  │   └─ Implicit grant: ID tokens, Access tokens                        │
│  └─ Client Secret (stored in Key Vault)                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Naming Convention (Azure CAF)

| Resource Type | Prefix | Example |
|---------------|--------|---------|
| Resource Group | `rg-` | `rg-unifiedui-dev-weu-001` |
| Storage Account | `st` | `stunifieduidevweu001` (no hyphens) |
| Key Vault | `kv-` | `kv-unifiedui-app-dev-weu-001` |
| SQL Server | `sql-` | `sql-unifiedui-dev-weu-001` |
| SQL Database | `sqldb-` | `sqldb-unifiedui-dev-weu-001` |
| Cosmos DB | `cdb-` | `cdb-unifiedui-dev-weu-001` |
| Container Apps Env | `cae-` | `cae-unifiedui-dev-weu-001` |
| Container App | `ca-` | `ca-platform-dev-weu-001` |
| Static Web App | `stapp-` | `stapp-unifiedui-dev-weu-001` |
| Service Bus | `sb-` | `sb-unifiedui-dev-weu-001` |
| Log Analytics | `log-` | `log-unifiedui-dev-weu-001` |
| App Registration | `app-` | `app-unifiedui-dev` |

**Region Abbreviations:** `weu` (West Europe), `neu` (North Europe), `eus` (East US), etc.

**Managed Identities:** System-assigned (automatisch bei Resource-Erstellung, keine separate Namensgebung)

---

## Packages

### Package 0: Repository Foundation

> Repository-Struktur, Copilot Instructions, JSON Schemas, Pre-commit Setup

#### 0.1 Repository Structure

| ID | Requirement |
|----|-------------|
| 0.1.1 | Erstelle `.github/copilot-instructions.md` mit IaC-spezifischen Regeln |
| 0.1.2 | Erstelle `instructions/terraform-conventions.md` für TF Best Practices |
| 0.1.3 | Erstelle `instructions/azure-architecture.md` für Azure-Patterns |
| 0.1.4 | Erstelle `instructions/config-schema.md` für YAML Konfiguration |
| 0.1.5 | Erstelle `instructions/security.md` für Secrets, RBAC, Networking |

#### 0.2 JSON Schema for Config Validation

| ID | Requirement |
|----|-------------|
| 0.2.1 | Erstelle `schema/azure-config.schema.json` mit vollständiger Konfiguration |
| 0.2.2 | Schema unterstützt `defaults` und Environment-spezifische Overrides |
| 0.2.3 | Schema validiert Tier-Optionen (Serverless, GeneralPurpose, etc.) |
| 0.2.4 | Schema unterstützt optionale Komponenten (n8n, Service Bus) |

#### 0.3 Pre-commit & Quality

| ID | Requirement |
|----|-------------|
| 0.3.1 | Erstelle `.pre-commit-config.yaml` mit terraform fmt, validate, tflint |
| 0.3.2 | Erstelle `README.md` mit Projekt-Dokumentation |
| 0.3.3 | Erstelle `CONTRIBUTING.md` mit Beitragsrichtlinien |

---

### Package 1: GitHub Container Registry Setup

> Anleitung und Skripte für GHCR Einrichtung (Voraussetzung für Deployment)

#### 1.1 GHCR Dokumentation

| ID | Requirement |
|----|-------------|
| 1.1.1 | Erstelle `docs/ghcr-setup.md` mit vollständiger Einrichtungsanleitung |
| 1.1.2 | Anleitung: GitHub Organization erstellen (falls nicht vorhanden) |
| 1.1.3 | Anleitung: Personal Access Token (PAT) mit `write:packages`, `read:packages`, `delete:packages` |
| 1.1.4 | Anleitung: Repository Secrets konfigurieren (`GHCR_TOKEN`, `GHCR_USERNAME`) |
| 1.1.5 | Anleitung: Package Visibility (public/private) konfigurieren |
| 1.1.6 | Anleitung: Docker Login zu GHCR (`docker login ghcr.io -u USERNAME -p TOKEN`) |
| 1.1.7 | Anleitung: Lokales Testing mit `scripts/build-and-push.sh` |

**GHCR Setup Inhalt (docs/ghcr-setup.md):**
```markdown
# GitHub Container Registry (GHCR) Setup

## 1. Personal Access Token (PAT) erstellen

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)"
3. Scopes auswählen:
   - `write:packages` — Push images
   - `read:packages` — Pull images  
   - `delete:packages` — Delete images (optional)
4. Token sicher speichern!

## 2. Docker Login (lokal)

\`\`\`bash
# Option A: Interaktiv
docker login ghcr.io -u YOUR_GITHUB_USERNAME
# Passwort = PAT

# Option B: Non-interaktiv
echo $GHCR_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
\`\`\`

## 3. Repository Secrets konfigurieren

Für jeden Service-Repo (unified-ui-*):
1. Settings → Secrets and variables → Actions
2. Secrets hinzufügen:
   - `GHCR_TOKEN` = dein PAT
   - `GHCR_USERNAME` = dein GitHub Username

## 4. Image Naming Convention

\`\`\`
ghcr.io/{org}/{repo}:{tag}

Beispiele:
- ghcr.io/enricogoerlitz/unified-ui-platform-service:v1.0.0
- ghcr.io/enricogoerlitz/unified-ui-platform-service:latest
- ghcr.io/enricogoerlitz/unified-ui-agent-service:v1.0.0
- ghcr.io/enricogoerlitz/unified-ui-frontend-service:v1.0.0
\`\`\`

## 5. Package Visibility

Nach erstem Push:
1. GitHub → Packages → {package name}
2. "Package settings"
3. "Change visibility" → Public oder Private

## 6. Erstes Image bauen und pushen

\`\`\`bash
# Im Service-Repo
cd unified-ui-platform-service

# Mit Script
../unifiedui-iac/scripts/build-and-push.sh \
  --service platform \
  --tag v1.0.0 \
  --registry ghcr.io/enricogoerlitz \
  --push

# Oder manuell
docker build -t ghcr.io/enricogoerlitz/unified-ui-platform-service:v1.0.0 .
docker push ghcr.io/enricogoerlitz/unified-ui-platform-service:v1.0.0
\`\`\`
```

#### 1.2 Workflow Templates

| ID | Requirement |
|----|-------------|
| 1.2.1 | Erstelle `docs/workflows/docker-publish.yml` als Template für Service-Repos |
| 1.2.2 | Trigger: Tag Push (`v*`) → pushed Image mit Tag |
| 1.2.3 | Trigger: PR auf `main` merged → pushed Image mit `:latest` |
| 1.2.4 | Multi-Arch Build (linux/amd64, linux/arm64) |
| 1.2.5 | GitHub Actions nutzt `scripts/build-and-push.sh` |

**Workflow Template (docs/workflows/docker-publish.yml):**
```yaml
name: Build and Push Docker Image

on:
  push:
    tags:
      - 'v*'
    branches:
      - main
  pull_request:
    branches:
      - main

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

### Package 2: Terraform Bootstrap (State Backend + App Registration)

> Separate Terraform-Konfiguration für initiales Setup (einmalig manuell)

**Context & Research:**
- State muss vor dem Hauptdeployment existieren
- App Registration benötigt für Frontend Auth + Backend OBO Flow
- Bootstrap ist ein einmaliger manueller Schritt pro Environment

#### 2.1 State Backend

| ID | Requirement |
|----|-------------|
| 2.1.1 | Erstelle `azure/bootstrap/main.tf` für TF State Storage Account |
| 2.1.2 | Storage Account mit Blob Versioning und Soft Delete |
| 2.1.3 | Container `tfstate` für State Files |
| 2.1.4 | Resource Group für Bootstrap-Ressourcen |

#### 2.2 Entra ID App Registration

| ID | Requirement |
|----|-------------|
| 2.2.1 | Erstelle App Registration `app-unifiedui-{env}` via AzureAD Provider |
| 2.2.2 | **API Permissions (Delegated) — Standard OIDC:** |
|      | — `Microsoft Graph → User.Read` (Sign in and read user profile) |
|      | — `Microsoft Graph → openid` (Sign users in) |
|      | — `Microsoft Graph → profile` (View users' basic profile) |
|      | — `Microsoft Graph → email` (View users' email address) |
|      | — `Microsoft Graph → offline_access` (Maintain access to data) |
| 2.2.3 | **API Permissions (Delegated) — OBO Flow für Platform Service:** |
|      | — `Microsoft Graph → User.Read.All` (Read all users' full profiles) — **Admin Consent Required** |
|      | — `Microsoft Graph → Group.Read.All` (Read all groups) — **Admin Consent Required** |
|      | — `Microsoft Graph → GroupMember.Read.All` (Read group memberships) — **Admin Consent Required** |
|      | — `Microsoft Graph → Directory.Read.All` (Read directory data) — **Admin Consent Required** |
| 2.2.4 | **API Permissions (Delegated) — Azure AI Foundry (Frontend):** |
|      | — `Azure AI Services → user_impersonation` (Access Azure AI services) |
|      | — Resource App ID: `https://cognitiveservices.azure.com` |
| 2.2.5 | **Expose an API:** |
|      | — Application ID URI: `api://{client-id}` |
|      | — Scope: `access_as_user` (Admin consent: No, User consent: Yes) |
|      | — Who can consent: Admins and users |
| 2.2.6 | **Authentication → Platform: SPA** |
|      | — Redirect URIs: `http://localhost:5173`, `https://{frontend-url}` |
|      | — Implicit grant: ✅ Access tokens, ✅ ID tokens |
| 2.2.7 | **Certificates & secrets:** |
|      | — Client Secret mit 12 Monate Expiry |
|      | — Description: `unifiedui-{env}-secret` |
| 2.2.8 | Grant Admin Consent für alle Admin-Required Permissions |
| 2.2.9 | Output: Client ID, Tenant ID, Client Secret (sensitive) |
| 2.2.10 | Client Secret wird in Infra Key Vault gespeichert |

**Warum diese Permissions?**

| Permission | Verwendet von | Zweck |
|------------|---------------|-------|
| `User.Read` | Frontend | Login, User Profile anzeigen |
| `openid`, `profile`, `email` | Frontend | Standard OIDC Claims |
| `offline_access` | Frontend | Refresh Tokens für Silent Auth |
| `User.Read.All` | Platform Service (OBO) | `/users` API, User Lookup by ID |
| `Group.Read.All` | Platform Service (OBO) | `/groups` API, Security Groups auflisten |
| `GroupMember.Read.All` | Platform Service (OBO) | `/me/memberOf` API, User's Gruppenmitgliedschaften |
| `Directory.Read.All` | Platform Service (OBO) | `/servicePrincipals/{oid}/memberOf`, umfassender Directory-Zugriff |
| `user_impersonation` (AIS) | Frontend | Azure AI Foundry Token für Foundry Agent Integration |

**App Registration Terraform (azure/bootstrap/app-registration.tf):**
```hcl
# App Registration for unified-ui
resource "azuread_application" "unifiedui" {
  display_name = "app-unifiedui-${var.environment}"
  
  sign_in_audience = "AzureADMyOrg"  # Single tenant
  
  # SPA Authentication
  single_page_application {
    redirect_uris = var.spa_redirect_uris
  }
  
  # API Permissions (Microsoft Graph - Delegated)
  required_resource_access {
    resource_app_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph
    
    # Standard OIDC Permissions
    resource_access {
      id   = "e1fe6dd8-ba31-4d61-89e7-88639da4683d" # User.Read
      type = "Scope"
    }
    resource_access {
      id   = "37f7f235-527c-4136-accd-4a02d197296e" # openid
      type = "Scope"
    }
    resource_access {
      id   = "14dad69e-099b-42c9-810b-d002981feec1" # profile
      type = "Scope"
    }
    resource_access {
      id   = "64a6cdd6-aab1-4aaf-94b8-3cc8405e90d0" # email
      type = "Scope"
    }
    resource_access {
      id   = "7427e0e9-2fba-42fe-b0c0-848c9e6a8182" # offline_access
      type = "Scope"
    }
    
    # OBO Flow Permissions (Admin Consent Required)
    resource_access {
      id   = "a154be20-db9c-4678-8ab7-66f6cc099a59" # User.Read.All
      type = "Scope"
    }
    resource_access {
      id   = "5f8c59db-677d-491f-a6b8-5f174b11ec1d" # Group.Read.All
      type = "Scope"
    }
    resource_access {
      id   = "bc024368-1153-4739-b217-4326f2e966d0" # GroupMember.Read.All
      type = "Scope"
    }
    resource_access {
      id   = "06da0dbc-49e2-44d2-8312-53f166ab848a" # Directory.Read.All
      type = "Scope"
    }
  }
  
  # API Permissions (Azure AI Services - Delegated for Foundry)
  required_resource_access {
    resource_app_id = "https://cognitiveservices.azure.com"
    
    resource_access {
      id   = "user_impersonation"  # Access Azure AI services
      type = "Scope"
    }
  }
  
  # Expose an API
  api {
    mapped_claims_enabled          = true
    requested_access_token_version = 2
    
    oauth2_permission_scope {
      admin_consent_description  = "Allow the application to access unified-ui on behalf of the signed-in user."
      admin_consent_display_name = "Access unified-ui"
      enabled                    = true
      id                         = random_uuid.scope_id.result
      type                       = "User"
      user_consent_description   = "Allow the application to access unified-ui on your behalf."
      user_consent_display_name  = "Access unified-ui"
      value                      = "access_as_user"
    }
  }
  
  # Enable implicit grant for SPA
  implicit_grant {
    access_token_issuance_enabled = true
    id_token_issuance_enabled     = true
  }
}

# Service Principal
resource "azuread_service_principal" "unifiedui" {
  client_id = azuread_application.unifiedui.client_id
}

# Client Secret
resource "azuread_application_password" "unifiedui" {
  application_id = azuread_application.unifiedui.id
  display_name   = "unifiedui-${var.environment}-secret"
  end_date       = timeadd(timestamp(), "8760h") # 1 year
}

resource "random_uuid" "scope_id" {}

# Admin Consent for permissions requiring admin approval
resource "azuread_service_principal_delegated_permission_grant" "graph_admin_consent" {
  service_principal_object_id          = azuread_service_principal.unifiedui.object_id
  resource_service_principal_object_id = data.azuread_service_principal.msgraph.object_id
  claim_values = [
    "User.Read",
    "User.Read.All",
    "Group.Read.All",
    "GroupMember.Read.All",
    "Directory.Read.All",
  ]
}

data "azuread_service_principal" "msgraph" {
  client_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph
}

output "client_id" {
  value = azuread_application.unifiedui.client_id
}

output "tenant_id" {
  value = data.azuread_client_config.current.tenant_id
}

output "client_secret" {
  value     = azuread_application_password.unifiedui.value
  sensitive = true
}

output "api_scope" {
  value = "api://${azuread_application.unifiedui.client_id}/access_as_user"
}
```

#### 2.3 Bootstrap Script

| ID | Requirement |
|----|-------------|
| 2.3.1 | Erstelle `scripts/bootstrap-azure.sh` für initiales Setup |
| 2.3.2 | Parameter: `--environment`, `--subscription-id`, `--location` |
| 2.3.3 | Script prüft Azure CLI Login |
| 2.3.4 | Script führt Bootstrap-TF aus |
| 2.3.5 | Script gibt Backend-Config für Hauptdeployment aus |

---

### Package 3: Terraform Core Modules

> Wiederverwendbare Module für Azure-Ressourcen

#### 3.1 Resource Group Module

| ID | Requirement |
|----|-------------|
| 3.1.1 | Erstelle `azure/modules/resource-group/` mit RG + Tags |
| 3.1.2 | Standard-Tags: project, environment, managed-by, created-at |

#### 3.2 Networking Module

| ID | Requirement |
|----|-------------|
| 3.2.1 | Erstelle `azure/modules/networking/` (für spätere Phase 2 vorbereitet) |
| 3.2.2 | Phase 1: Keine VNet (public endpoints) |
| 3.2.3 | Outputs für spätere Private Endpoint Integration |

#### 3.3 Storage Module

| ID | Requirement |
|----|-------------|
| 3.3.1 | Erstelle `azure/modules/storage/` für Storage Account |
| 3.3.2 | Container für File Uploads (Blob) |
| 3.3.3 | System-assigned MI Access (Storage Blob Data Contributor) |
| 3.3.4 | Lifecycle Policies für Cost Optimization |

#### 3.4 Key Vault Module

| ID | Requirement |
|----|-------------|
| 3.4.1 | Erstelle `azure/modules/keyvault/` für Key Vault |
| 3.4.2 | RBAC-basierter Zugriff (kein Access Policies) |
| 3.4.3 | Soft Delete und Purge Protection |
| 3.4.4 | Initial Secrets aus Terraform Variables |

#### 3.5 SQL Database Module

| ID | Requirement |
|----|-------------|
| 3.5.1 | Erstelle `azure/modules/database/sql/` für Azure SQL |
| 3.5.2 | Serverless Tier mit Auto-Pause (1 Stunde) |
| 3.5.3 | Entra ID Admin (System-assigned MI der Container App) |
| 3.5.4 | Firewall Rule für Azure Services (Phase 1) |
| 3.5.5 | Separater Server für n8n (wenn enabled) |

#### 3.6 CosmosDB Module

| ID | Requirement |
|----|-------------|
| 3.6.1 | Erstelle `azure/modules/database/cosmosdb/` für CosmosDB |
| 3.6.2 | **NoSQL API** (Core API) mit Serverless Capacity |
| 3.6.3 | Database: `unifiedui` mit Containers: `traces`, `sessions`, `messages` |
| 3.6.4 | System-assigned MI Access (Cosmos DB Data Contributor) |
| 3.6.5 | Partition Keys: `/tenantId` für alle Container |

#### 3.7 Container Apps Module

| ID | Requirement |
|----|-------------|
| 3.7.1 | Erstelle `azure/modules/container-apps/environment/` für CAE |
| 3.7.2 | Log Analytics Workspace Integration |
| 3.7.3 | Erstelle `azure/modules/container-apps/app/` für einzelne Apps |
| 3.7.4 | Min replicas: 0 (Serverless), Max replicas: konfigurierbar |
| 3.7.5 | Secrets aus Key Vault References |
| 3.7.6 | System-assigned Managed Identity per App |
| 3.7.7 | Health Probes (liveness, readiness) |

#### 3.8 Static Web App Module

| ID | Requirement |
|----|-------------|
| 3.8.1 | Erstelle `azure/modules/static-webapp/` für SWA |
| 3.8.2 | Free Tier für Dev |
| 3.8.3 | API Integration mit Container Apps Backend |

#### 3.9 Service Bus Module (Optional)

| ID | Requirement |
|----|-------------|
| 3.9.1 | Erstelle `azure/modules/messaging/servicebus/` für Service Bus |
| 3.9.2 | Basic Tier für Dev |
| 3.9.3 | Queue für async Messages |
| 3.9.4 | Nur erstellt wenn `servicebus.enabled: true` |

#### 3.10 Monitoring Module

| ID | Requirement |
|----|-------------|
| 3.10.1 | Erstelle `azure/modules/monitoring/` für Log Analytics |
| 3.10.2 | Application Insights (optional) |
| 3.10.3 | Retention: 30 Tage (Dev), konfigurierbar |

---

### Package 4: Main Terraform Configuration

> Hauptkonfiguration die Module orchestriert

#### 4.1 Configuration Parser

| ID | Requirement |
|----|-------------|
| 4.1.1 | Erstelle `azure/config.yaml` mit Defaults + Dev Environment |
| 4.1.2 | Erstelle `azure/locals.tf` für YAML Parsing und Merging |
| 4.1.3 | Defaults werden mit Environment-Config gemerged |
| 4.1.4 | Variablen: `environment` (dev/tst/prd), `config_file` |

#### 4.2 Provider & Backend

| ID | Requirement |
|----|-------------|
| 4.2.1 | Erstelle `azure/providers.tf` mit AzureRM + AzureAD Provider |
| 4.2.2 | Erstelle `azure/backend.tf.example` als Template |
| 4.2.3 | Backend-Konfiguration wird bei Init übergeben |

#### 4.3 Main Orchestration

| ID | Requirement |
|----|-------------|
| 4.3.1 | Erstelle `azure/main.tf` mit Module-Aufrufen |
| 4.3.2 | Erstelle `azure/outputs.tf` mit wichtigen Endpoints |
| 4.3.3 | Output: Frontend URL, API URLs, Connection Strings (sensitive) |

---

### Package 5: Deployment Scripts

> Lokale Skripte für Deployment (CI/CD-unabhängig)

#### 5.1 Core Scripts

| ID | Requirement |
|----|-------------|
| 5.1.1 | Erstelle `scripts/validate-config.py` für YAML Schema Validation |
| 5.1.2 | Erstelle `scripts/deploy.sh` als Haupt-Deployment-Script |
| 5.1.3 | Parameter: `--environment`, `--action` (plan/apply/destroy) |
| 5.1.4 | Script validiert Config, initialisiert Backend, führt TF aus |
| 5.1.5 | Erstelle `scripts/init-backend.sh` für Backend-Konfiguration |

#### 5.2 Container Image Scripts

| ID | Requirement |
|----|-------------|
| 5.2.1 | Erstelle `scripts/build-and-push.sh` für Docker Build & Push |
| 5.2.2 | Parameter: `--service`, `--tag`, `--registry` |
| 5.2.3 | Unterstützt GHCR (ghcr.io/enricogoerlitz/unified-ui-*) |
| 5.2.4 | Erstelle `scripts/update-container-app.sh` für Image-Update in ACA |

#### 5.3 Utility Scripts

| ID | Requirement |
|----|-------------|
| 5.3.1 | Erstelle `scripts/get-outputs.sh` für Terraform Output Abfrage |
| 5.3.2 | Erstelle `scripts/rotate-secrets.sh` für Secret Rotation |

---

### Package 6: Database Migration Konzept

> Strategie für Datenbank-Migrationen von lokal nach Cloud-Umgebungen

**Context:**
- Lokal: PostgreSQL (Docker)
- Cloud: Azure SQL (Serverless)
- Alembic für Migrations (Platform Service)
- Unterschiedliche Connection Strings je Environment

#### 6.1 Migration Scripts

| ID | Requirement |
|----|-------------|
| 6.1.1 | Erstelle `scripts/db-migrate.sh` für Remote-Migrationen |
| 6.1.2 | Parameter: `--environment` (dev/tst/prd), `--action` (upgrade/downgrade/current) |
| 6.1.3 | Script holt Connection String aus Terraform Output (oder Key Vault) |
| 6.1.4 | Script führt Alembic Migration remote aus |
| 6.1.5 | Unterstützt Dry-Run (`--dry-run`) für Vorschau |

#### 6.2 Migration Workflow

| ID | Requirement |
|----|-------------|
| 6.2.1 | Erstelle `docs/database-migration.md` mit Workflow-Dokumentation |
| 6.2.2 | Dokumentiere PostgreSQL ↔ Azure SQL Kompatibilität |
| 6.2.3 | Dokumentiere Migration-Strategie: Lokal entwickeln → Cloud deployen |
| 6.2.4 | Dokumentiere Rollback-Strategie |

#### 6.3 Connection String Management

| ID | Requirement |
|----|-------------|
| 6.3.1 | Erstelle `scripts/get-connection-string.sh` für sichere CS-Abfrage |
| 6.3.2 | Connection String wird **nicht** in Env-Vars gecached |
| 6.3.3 | Unterstützt sowohl TF Output als auch Key Vault als Quelle |
| 6.3.4 | Azure SQL Connection String Format mit Managed Identity |

---

### Package 7: Config.yaml Vollständige Konfiguration

> Detaillierte YAML-Konfiguration für alle Environments

#### 7.1 Dev Environment Config

| ID | Requirement |
|----|-------------|
| 7.1.1 | Vollständige `azure/config.yaml` mit Dev-Konfiguration |
| 7.1.2 | Alle Services: 0.25-0.5 vCPU, 0.5-1Gi Memory |
| 7.1.3 | SQL: Serverless, 0.5-2 vCores, Auto-Pause 60min |
| 7.1.4 | CosmosDB: Serverless (max 1000 RU/s burst), NoSQL API |
| 7.1.5 | Redis: Container in ACA (nicht managed) |
| 7.1.6 | n8n: Optional (default: disabled) |
| 7.1.7 | Service Bus: Optional (default: disabled) |

---

### Package 8: Agent Service — CosmosDB NoSQL API Migration

> Umstellung des Agent Service von MongoDB auf Azure CosmosDB NoSQL API

**Scope:** `unified-ui-agent-service`

**Context:**
- Aktuell: MongoDB Driver (`go.mongodb.org/mongo-driver`) mit `DOCDB_TYPE=cosmosdb` 
- Problem: CosmosDB MongoDB API ist ein Kompatibilitäts-Layer, nicht native NoSQL
- Ziel: Native CosmosDB NoSQL SDK für Performance, Kosten, Azure-Integration

#### 8.1 CosmosDB Client Implementation

| ID | Requirement |
|----|-------------|
| 8.1.1 | Erstelle `internal/infrastructure/docdb/cosmosdb/client.go` mit Azure Cosmos SDK |
| 8.1.2 | Implementiere `docdb.Client` Interface mit `azcosmos` SDK |
| 8.1.3 | Support für Managed Identity Authentication (DefaultAzureCredential) |
| 8.1.4 | Support für Connection String Authentication (Fallback) |
| 8.1.5 | Partition Key Strategy: `/tenantId` für alle Container |

#### 8.2 Collection Implementations

| ID | Requirement |
|----|-------------|
| 8.2.1 | Erstelle `internal/infrastructure/docdb/cosmosdb/traces.go` |
| 8.2.2 | Erstelle `internal/infrastructure/docdb/cosmosdb/sessions.go` |
| 8.2.3 | Erstelle `internal/infrastructure/docdb/cosmosdb/messages.go` |
| 8.2.4 | Erstelle `internal/infrastructure/docdb/cosmosdb/reactions.go` |
| 8.2.5 | Alle Collections implementieren bestehende Interfaces aus `internal/core/docdb/` |

#### 8.3 Factory Pattern Update

| ID | Requirement |
|----|-------------|
| 8.3.1 | Update `cmd/server/main.go` → `createDocDBClient()` |
| 8.3.2 | `DOCDB_TYPE=cosmosdb` → Native CosmosDB NoSQL Client |
| 8.3.3 | `DOCDB_TYPE=mongodb` → MongoDB Client (bleibt für lokale Entwicklung) |
| 8.3.4 | Neue Env-Vars: `COSMOSDB_ENDPOINT`, `COSMOSDB_DATABASE` |

#### 8.4 Configuration

| ID | Requirement |
|----|-------------|
| 8.4.1 | Update `internal/config/config.go` für CosmosDB-spezifische Config |
| 8.4.2 | `COSMOSDB_ENDPOINT` (z.B. `https://cdb-unifiedui-dev-weu-001.documents.azure.com:443/`) |
| 8.4.3 | `COSMOSDB_DATABASE` (default: `unifiedui`) |
| 8.4.4 | `COSMOSDB_USE_MANAGED_IDENTITY` (default: `true` in Cloud) |

#### 8.5 Tests

| ID | Requirement |
|----|-------------|
| 8.5.1 | Unit Tests für CosmosDB Client mit Mocks |
| 8.5.2 | Integration Tests (optional, mit CosmosDB Emulator) |
| 8.5.3 | Update bestehende Tests für neues Factory Pattern |

#### 8.6 Documentation

| ID | Requirement |
|----|-------------|
| 8.6.1 | Update `unified-ui-agent-service/.github/copilot-instructions.md` |
| 8.6.2 | Update `instructions/infrastructure.instructions.md` mit CosmosDB NoSQL |
| 8.6.3 | Update `README.md` mit neuen Env-Vars |

---

## Config.yaml Struktur

```yaml
# azure/config.yaml
project:
  name: unifiedui
  owner: "your-email@example.com"

# GitHub Container Registry (ghcr.io)
registry:
  type: ghcr
  organization: enricogoerlitz
  # Images: ghcr.io/enricogoerlitz/unified-ui-{service}:{tag}

# Entra ID App Registration (created in bootstrap)
auth:
  spa_redirect_uris:
    - "http://localhost:5173"  # Local dev
    - "https://{frontend-url}" # Will be replaced with actual URL

defaults:
  location: westeurope
  location_short: weu
  tags:
    project: unifiedui
    managed-by: terraform
  
  # Default resource configurations
  sql:
    tier: Serverless
    min_vcores: 0.5
    max_vcores: 2
    auto_pause_delay: 60  # minutes
  
  cosmosdb:
    api: NoSQL  # Core/NoSQL API (NOT MongoDB!)
    tier: Serverless
    max_throughput: 1000  # RU/s burst
  
  storage:
    tier: Standard_LRS
    kind: StorageV2
  
  container_apps:
    platform:
      image_tag: latest
      cpu: 0.5
      memory: 1Gi
      min_replicas: 0
      max_replicas: 2
      port: 8000
    agent:
      image_tag: latest
      cpu: 0.5
      memory: 1Gi
      min_replicas: 0
      max_replicas: 2
      port: 8085
    redis:
      enabled: true
      managed: false  # Container, not Azure Cache
      cpu: 0.25
      memory: 0.5Gi
    n8n:
      enabled: false
      cpu: 0.5
      memory: 1Gi
      port: 5678
  
  servicebus:
    enabled: false
    tier: Basic
  
  monitoring:
    retention_days: 30
  
  keyvault:
    sku: standard

environments:
  dev:
    # Inherits all defaults, override as needed
    suffix: "001"
    
    container_apps:
      platform:
        min_replicas: 0
        max_replicas: 1
      agent:
        min_replicas: 0
        max_replicas: 1
    
    # n8n disabled by default
    # servicebus disabled by default

  tst:
    suffix: "001"
    
    container_apps:
      platform:
        min_replicas: 1
        max_replicas: 3
      agent:
        min_replicas: 1
        max_replicas: 3
      n8n:
        enabled: true

  prd:
    suffix: "001"
    
    sql:
      tier: GeneralPurpose
      vcores: 2
      auto_pause_delay: -1  # No auto-pause
    
    cosmosdb:
      tier: Provisioned
      throughput: 1000
    
    container_apps:
      platform:
        cpu: 2
        memory: 4Gi
        min_replicas: 2
        max_replicas: 10
      agent:
        cpu: 2
        memory: 4Gi
        min_replicas: 2
        max_replicas: 10
      redis:
        managed: true  # Azure Cache for Redis
      n8n:
        enabled: true
        cpu: 1
        memory: 2Gi
    
    servicebus:
      enabled: true
      tier: Standard
    
    monitoring:
      retention_days: 90
```

---

## Repository Struktur (Final)

```
unifiedui-iac/
├── .github/
│   ├── copilot-instructions.md
│   └── CODEOWNERS
├── instructions/
│   ├── terraform-conventions.md
│   ├── azure-architecture.md
│   ├── config-schema.md
│   └── security.md
├── schema/
│   └── azure-config.schema.json
├── azure/
│   ├── config.yaml
│   ├── main.tf
│   ├── locals.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── backend.tf.example
│   ├── bootstrap/
│   │   ├── main.tf              # TF State + App Registration
│   │   ├── app-registration.tf  # Entra ID App Reg
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── modules/
│       ├── resource-group/
│       │   └── ...
│       ├── networking/
│       │   └── ...
│       ├── storage/
│       │   └── ...
│       ├── keyvault/
│       │   └── ...
│       ├── database/
│       │   ├── sql/
│       │   │   └── ...
│       │   └── cosmosdb/        # NoSQL API
│       │       └── ...
│       ├── container-apps/
│       │   ├── environment/
│       │   │   └── ...
│       │   └── app/
│       │       └── ...
│       ├── static-webapp/
│       │   └── ...
│       ├── messaging/
│       │   └── servicebus/
│       │       └── ...
│       └── monitoring/
│           └── ...
├── scripts/
│   ├── bootstrap-azure.sh       # Initial setup
│   ├── deploy.sh                # Main deployment
│   ├── init-backend.sh          # TF backend init
│   ├── validate-config.py       # YAML schema validation
│   ├── build-and-push.sh        # Docker build & GHCR push
│   ├── update-container-app.sh  # Update ACA image
│   ├── get-outputs.sh           # Get TF outputs
│   ├── rotate-secrets.sh        # Secret rotation
│   ├── db-migrate.sh            # Remote DB migrations
│   └── get-connection-string.sh # Secure CS retrieval
├── docs/
│   ├── ghcr-setup.md            # GHCR einrichten
│   ├── database-migration.md    # Migration workflow
│   └── workflows/
│       └── docker-publish.yml   # GH Actions template
├── aws/
│   └── config.yaml              # Future
├── gcp/
│   └── config.yaml              # Future
├── .pre-commit-config.yaml
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

---

## Offene Punkte / Entscheidungen

- [x] Naming Convention → Azure CAF Best Practice (`cdb-` für CosmosDB)
- [x] n8n SQL → Separater Server
- [x] Managed Identity → System-assigned überall
- [x] Container Registry → GHCR (ghcr.io)
- [x] CI/CD → Lokale Skripte, optional GH Actions
- [x] CosmosDB API → NoSQL (Core API)
- [x] App Registration → In Bootstrap inkludiert
- [x] DB Migration → Konzept für PostgreSQL → Azure SQL
- [x] Agent Service CosmosDB NoSQL Migration → Package 8
- [ ] Private Deployment (Phase 2) → Später

---

## Implementierungsreihenfolge

**Phase A: IaC Repository Setup (unifiedui-iac)**
1. **Package 0**: Repository Foundation (Instructions, Schema, Pre-commit)
2. **Package 1**: GHCR Setup (Dokumentation + Workflow Templates)
3. **Package 2**: Bootstrap (State Backend + App Registration)
4. **Package 3**: Terraform Core Modules
5. **Package 4**: Main Terraform Configuration
6. **Package 5**: Deployment Scripts
7. **Package 6**: Database Migration Konzept
8. **Package 7**: Config.yaml finalisieren

**Phase B: Agent Service Migration (unified-ui-agent-service)**
9. **Package 8**: Agent Service — CosmosDB NoSQL API Migration

**Hinweis:** Package 8 kann parallel zu Phase A entwickelt werden. Vor dem ersten Cloud-Deployment muss Package 8 abgeschlossen sein.

---

## Abhängigkeiten / Voraussetzungen

Bevor IaC genutzt werden kann:

1. **Azure Subscription** mit ausreichenden Berechtigungen (Owner oder Contributor + User Access Admin)
2. **GHCR Setup** (Package 1) — Docker Images müssen vorhanden sein
3. **Package 8 abgeschlossen** — Agent Service muss CosmosDB NoSQL unterstützen
4. **Azure CLI** installiert und eingeloggt
5. **Terraform** >= 1.5 installiert

---

## Geschätzte Kosten (Dev Environment, ~Serverless)

| Resource | Monthly Cost (Est.) |
|----------|---------------------|
| Azure SQL Serverless | ~$5-15 (auto-pause) |
| CosmosDB Serverless | ~$0-10 (pay per request) |
| Container Apps | ~$0-20 (scale to zero) |
| Storage Account | ~$1-2 |
| Key Vault | ~$0.03/10k operations |
| Log Analytics | ~$2-5 (30d retention) |
| Static Web App | Free |
| **Total (Dev, idle)** | **~$10-20/month** |
| **Total (Dev, active)** | **~$30-50/month** |

