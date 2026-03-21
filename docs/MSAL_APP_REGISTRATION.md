# Anleitung — Entra ID App Registration (MSAL SPA + OBO)

> **Project**: unified-ui

---

## 1. Überblick

Diese Anleitung beschreibt die Einrichtung einer
**Entra ID App Registration** für die unified-ui Plattform.
Pro Umgebung (z. B. DEV, TST, PRD) wird eine eigene
App Registration benötigt.

**Architektur:**

- **Frontend** — React SPA, authentifiziert sich via
    `@azure/msal-browser` / `@azure/msal-react` (PKCE Redirect-Flow).
- **Backend** — FastAPI (Platform Service), validiert das Access-Token und nutzt
    den **OBO-Flow** (On-Behalf-Of), um im Namen des Benutzers
    auf Microsoft Graph zuzugreifen (Gruppenmitgliedschaften, User-Profile).
- Die Plattform wird als **Single Page Application** konfiguriert.
- Das Backend benötigt ein **Client Secret** für den OBO-Flow.

---

## 2. App Registration erstellen

> **Portal-Pfad:** Microsoft Entra Admin Center →
> App registrations → New registration

### 2.1 Registrierung anlegen

| Feld                     | Wert                                                          |
| ------------------------ | ------------------------------------------------------------- |
| Name                     | `unified-ui-<env>` (z. B. `unified-ui-dev`)                   |
| Supported account types  | Siehe Abschnitt 2.2                                           |
| Redirect URI (Plattform) | Single Page Application (SPA)                                 |
| Redirect URI (Wert)      | `http://localhost:5173` (Local Dev)                            |

### 2.2 Single Tenant vs. Multitenant

| Szenario                                     | Kontotyp                                                       |
| -------------------------------------------- | -------------------------------------------------------------- |
| Alle User sind im **selben Tenant**          | Accounts in this organizational directory only (Single tenant) |
| User melden sich aus **mehreren Tenants** an | Accounts in any organizational directory (Multitenant)         |

> **Faustregel:** Single Tenant, wenn App und User im selben
> Tenant leben. Multitenant nur, wenn User aus fremden Tenants
> sich anmelden müssen.

---

## 3. Redirect URIs konfigurieren

> **Portal-Pfad:** App registration → Authentication →
> Platform configurations → Single-page application

Pro Umgebung die passenden URIs eintragen:

| Umgebung | Redirect URIs                                        |
| -------- | ---------------------------------------------------- |
| DEV      | `https://<frontend-dev>.azurewebsites.net`           |
|          | `http://localhost:5173`                              |
| TST      | `https://<frontend-tst>.azurewebsites.net`           |
|          | `http://localhost:5173`                              |
| PRD      | `https://<frontend-prd>.azurewebsites.net`           |

> Falls eine Custom Domain konfiguriert wird, deren URI
> zusätzlich eintragen (z. B. `https://app.unified-ui.com`).
> Das Frontend nutzt `window.location.origin` als Redirect URI.

---

## 4. Client Secret erstellen

> **Portal-Pfad:** App registration →
> Certificates & secrets → Client secrets → New client secret

1. **Description** vergeben (z. B. `backend-obo`).
2. **Expires** wählen (empfohlen: 12 oder 24 Monate).
3. **Value** sofort kopieren — wird nur einmal angezeigt.

Das Secret wird vom Backend für den OBO-Token-Exchange
benötigt (Env-Variable `IDENTITY_CLIENT_SECRET` / Docker: `MSAL_CLIENT_SECRET`).

---

## 5. Expose an API

> **Portal-Pfad:** App registration → Expose an API

Das Frontend fordert den Scope `api://<CLIENT_ID>/access_as_user`
an. Darüber identifiziert das Backend den Benutzer im OBO-Flow.

**Schritt 1 — Application ID URI setzen:**

- Auf **Set** klicken → Vorschlag `api://<CLIENT_ID>` übernehmen.

**Schritt 2 — Scope hinzufügen** (Add a scope):

| Feld                       | Wert                                            |
| -------------------------- | ----------------------------------------------- |
| Scope name                 | `access_as_user`                                |
| Who can consent            | Admins and users                                |
| Admin consent display name | Access the application as the signed-in user    |
| Admin consent description  | Allows the backend to act on behalf of the user |

---

## 6. API Permissions

> **Portal-Pfad:** App registration → API permissions →
> Add a permission

### 6.1 Microsoft Graph — Delegated (7 Scopes)

> Add a permission → Microsoft Graph → Delegated permissions

| Scope                  | Admin Consent | Begründung                                   |
| ---------------------- | ------------- | -------------------------------------------- |
| `openid`               | No            | OpenID-Connect-Login (ID-Token)              |
| `profile`              | No            | Basisprofil (Name, Vorname)                  |
| `email`                | No            | E-Mail-Adresse im Token                      |
| `offline_access`       | No            | Refresh-Token für langlebige Sessions        |
| `User.Read`            | No            | Eigenes Benutzerprofil lesen (Graph)         |
| `GroupMember.Read.All` | Yes           | Gruppen des Users abfragen (+ Overage)       |
| `User.ReadBasic.All`   | No            | Basisprofile aller User (People-Picker)      |

### 6.2 Admin Consent erteilen

Direkt nach dem Hinzufügen aller Permissions:

1. Auf **Grant admin consent for \<Tenant\>** klicken.
2. Prüfen, dass alle Permissions den Status
    **Granted for \<Tenant\>** zeigen.

> Bei **Multitenant**-Setups muss Admin Consent zusätzlich
> in **jedem beteiligten Tenant** erteilt werden — dort über
> die Enterprise Application (Service Principal), die beim
> ersten Login automatisch entsteht.

---

## 7. Token Configuration

> **Portal-Pfad:** App registration → Token configuration

Damit Gruppenmitgliedschaften direkt im Token verfügbar sind:

1. **Add groups claim** klicken.
2. Gruppentypen: **Security groups** auswählen.
3. Token-Typ **ID** und **Access**: jeweils **Group ID** wählen.
4. **Add** klicken.

> **Overage-Hinweis:** Ab **200+ Gruppen** liefert Entra ID
> statt Gruppen-IDs einen Overage-Indicator (`_claim_sources`).
> Die App ruft die Gruppen dann per Graph API ab
> (`GET /me/memberOf`). Die Permission `GroupMember.Read.All`
> aus Abschnitt 6.1 deckt diesen Fallback ab.

---

## 8. Ergebnis — benötigte Werte pro Umgebung

Nach Abschluss der Einrichtung werden folgende Werte benötigt:

| Wert                      | Wo zu finden                          | Env-Variable (Docker)  |
| ------------------------- | ------------------------------------- | ---------------------- |
| `Application (client) ID` | App registration → Overview           | `MSAL_CLIENT_ID`       |
| `Directory (tenant) ID`   | App registration → Overview           | `MSAL_TENANT_ID`       |
| `Client Secret` (Value)   | Certificates & secrets (nur einmalig) | `MSAL_CLIENT_SECRET`   |
| API Scope                 | Expose an API → Scopes                | `MSAL_API_SCOPE`       |
| Authority URL              | `https://login.microsoftonline.com/common` (Multitenant) oder `https://login.microsoftonline.com/<TENANT_ID>` (Single Tenant) | `MSAL_AUTHORITY` |
| Client Secret Ablaufdatum | Certificates & secrets → Expires      | —                      |

Diese Werte werden in der `docker/local/.env` eingetragen.
Siehe [Docker Local Setup](../docker/local/README.md) für Details.
