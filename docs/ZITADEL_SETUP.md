# Anleitung — Zitadel OIDC Setup (SPA + Platform Service)

> **Project**: unified-ui

---

## 1. Überblick

Diese Anleitung beschreibt die Einrichtung von **Zitadel** als
OIDC Identity Provider für die unified-ui Plattform.
Zitadel ersetzt Microsoft Entra ID und bietet vollständiges
User- und Group-Management über eine eigene Admin Console.

**Architektur:**

- **Zitadel** — OIDC-kompatibler Identity Provider mit
    Admin Console, User/Group Management und JWKS-Endpoint.
- **Frontend** — React SPA, authentifiziert sich via
    `oidc-client-ts` (Authorization Code + PKCE).
- **Backend** — FastAPI (Platform Service), validiert das
    Access-Token über JWKS und ruft User/Group-Infos über
    die Zitadel Management API ab.
- Kein OBO-Flow nötig — Zitadel liefert alle Claims
    (inkl. Gruppen) direkt im Token.

**Voraussetzung:** Zitadel läuft via Docker Compose
(siehe `docker/local/identity.yml`).

---

## 2. Zitadel starten

```bash
cd docker/local
docker compose up unifiedui-database unifiedui-identity
```

Beim ersten Start:
- PostgreSQL erstellt die `zitadel`-Datenbank
    (via `init-scripts/create-additional-dbs.sql`).
- Zitadel führt DB-Migrationen durch (~30 Sekunden).
- Ein Admin-User wird automatisch angelegt.

> **Hinweis:** Falls PostgreSQL bereits Daten enthält
> (Volume existiert), wird das Init-Script nicht erneut
> ausgeführt. In dem Fall manuell erstellen:
> `docker exec unifiedui-database psql -U unifiedui -c "CREATE DATABASE zitadel;"`

---

## 3. In der Admin Console anmelden

> **URL:** http://localhost:8088/ui/console

| Feld     | Wert                                    |
| -------- | --------------------------------------- |
| Login    | `zitadel-admin@zitadel.localhost`       |
| Passwort | `ZitadelAdmin1!`                        |

Beim ersten Login wird eine Passwortänderung verlangt.

---

## 4. Projekt erstellen

> **Console-Pfad:** Projects → Create New Project

| Feld              | Wert                    |
| ----------------- | ----------------------- |
| Name              | `unified-ui`            |

Nach dem Erstellen das Projekt öffnen.

---

## 5. OIDC Application erstellen (Frontend SPA)

> **Console-Pfad:** Projects → unified-ui → Applications →
> New → Web Application

### 5.1 Application anlegen

| Feld              | Wert                          |
| ----------------- | ----------------------------- |
| Name              | `unified-ui-frontend`         |
| Application Type  | **User Agent** (SPA)          |
| Authentication    | **PKCE**                      |

> **Wichtig:** Für SPAs immer **PKCE** wählen,
> niemals Client Secret im Browser verwenden.

### 5.2 Redirect URIs konfigurieren

| Feld               | Wert                                          |
| ------------------ | --------------------------------------------- |
| Redirect URI       | `http://localhost:5173/callback`               |
| Post Logout URI    | `http://localhost:5173`                        |

Für weitere Umgebungen zusätzliche URIs eintragen:

| Umgebung | Redirect URI                                         |
| -------- | ---------------------------------------------------- |
| DEV      | `https://<frontend-dev>.example.com/callback`        |
| PRD      | `https://<frontend-prd>.example.com/callback`        |

### 5.3 Notieren

Nach dem Erstellen der Application werden folgende Werte angezeigt:

| Wert            | Wo zu finden                  | Env-Variable (Docker)      |
| --------------- | ----------------------------- | -------------------------- |
| `Client ID`     | Application → URLs            | `VITE_OIDC_CLIENT_ID`     |
| `Issuer URL`    | Application → URLs            | `VITE_OIDC_AUTHORITY`     |

> Die **Issuer URL** hat das Format:
> `http://localhost:8088/oauth/v2` (Local Dev)

---

## 6. Platform Service Application erstellen (Backend API)

> **Console-Pfad:** Projects → unified-ui → Applications →
> New → API Application

### 6.1 Application anlegen

| Feld              | Wert                          |
| ----------------- | ----------------------------- |
| Name              | `unified-ui-platform`         |
| Authentication    | **Basic**                     |

### 6.2 Notieren

| Wert              | Wo zu finden                  | Env-Variable (Docker)                 |
| ----------------- | ----------------------------- | ------------------------------------- |
| `Client ID`       | Application → URLs            | `IDENTITY_CLIENT_ID`                  |
| `Client Secret`   | Application → URLs            | `IDENTITY_CLIENT_SECRET`              |

> Das Backend verwendet Client ID + Secret, um die
> Zitadel Management API aufzurufen (User/Group-Abfragen).

---

## 7. Rollen & Gruppen konfigurieren

### 7.1 Projekt-Rollen erstellen (optional)

> **Console-Pfad:** Projects → unified-ui → Roles → New

Zitadel kann Rollen auf Projektebene vergeben. Diese werden
als `urn:zitadel:iam:org:project:role:{rolename}` Claim im
Token geliefert.

Für unified-ui relevante Gruppen werden jedoch über
**Zitadel Groups** verwaltet (nicht Projekt-Rollen),
damit sie im `groups` Claim des Tokens erscheinen.

### 7.2 Groups erstellen

> **Console-Pfad:** Organization → Groups

Beispiel-Gruppen für unified-ui:

| Group Name    | Beschreibung                       |
| ------------- | ---------------------------------- |
| `developers`  | Entwickler mit Standard-Zugriff    |
| `admins`      | Administratoren mit Vollzugriff    |

### 7.3 User zu Groups zuweisen

> **Console-Pfad:** Organization → Users →
> User auswählen → Groups → Add

---

## 8. Benutzer erstellen

> **Console-Pfad:** Organization → Users → New → Human User

| Feld         | Wert                          |
| ------------ | ----------------------------- |
| Username     | `testuser1`                   |
| First Name   | `Test`                        |
| Last Name    | `User`                        |
| Display Name | `Test User 1`                 |
| Email        | `testuser1@example.com`       |
| Password     | (selbst vergeben)             |

> **Email-Verifizierung:** In der lokalen Entwicklung
> ist kein SMTP konfiguriert. Email-Verifizierung kann
> übersprungen werden — dazu in den User-Details auf
> **Set Email Verified** klicken.

---

## 9. Token Configuration

### 9.1 Claims im Token prüfen

Zitadel liefert standardmäßig folgende Claims im ID/Access Token:

| Claim                | Beschreibung                         |
| -------------------- | ------------------------------------ |
| `sub`                | User ID (eindeutige ID)              |
| `iss`                | Issuer URL                           |
| `aud`                | Client ID (Audience)                 |
| `name`               | Display Name                         |
| `given_name`         | Vorname                              |
| `family_name`        | Nachname                             |
| `email`              | E-Mail-Adresse                       |
| `preferred_username` | Username                             |
| `locale`             | Sprache                              |

### 9.2 Gruppen-Claims aktivieren

Damit Gruppenmitgliedschaften im Token stehen, müssen
**User Grants** im Projekt konfiguriert sein:

> **Console-Pfad:** Projects → unified-ui →
> Authorizations → New

1. User auswählen.
2. Projekt `unified-ui` auswählen.
3. Rollen zuweisen (falls Projekt-Rollen verwendet werden).

> Die Gruppen erscheinen als
> `urn:zitadel:iam:org:project:roles` Claim im Token.
> Der Platform Service extrahiert diese im
> `OIDCIdentityProvider`.

---

## 10. Service User erstellen (Management API)

Damit der Platform Service alle Benutzer der Organisation
durchsuchen kann (z.B. bei der Tenant-Zugriffsvergabe),
wird ein **Service User** mit Personal Access Token (PAT) benötigt.

### 10.1 Service User anlegen

> **Console-Pfad:** Organization → Users → Service Users Tab → New

| Feld              | Wert                          |
| ----------------- | ----------------------------- |
| Username           | `unified-ui-platform-svc`    |
| Name               | `unified-ui Platform Service`|
| Access Token Type  | **JWT**                      |

### 10.2 Personal Access Token (PAT) erstellen

1. Den neuen Service User öffnen.
2. Tab **Personal Access Tokens** → **New**.
3. Optional: Ablaufdatum setzen (oder leer lassen für kein Ablauf).
4. **Token kopieren** — wird als `OIDC_ZITADEL_SERVICE_TOKEN` verwendet.

### 10.3 Org-Level Manager-Rolle zuweisen

1. Links: **Organization** → Zahnrad-Icon oben rechts (Settings).
2. Tab **Managers** → **Add Manager**.
3. Service User `unified-ui-platform-svc` suchen und auswählen.
4. Rolle: **Org User Manager** (für User-Suche ausreichend).
5. **Add** klicken.

Der Service User kann jetzt via
`POST /management/v1/users/_search` alle User der Organisation
durchsuchen.

---

## 11. OIDC Discovery & JWKS

Nach der Einrichtung sind folgende Endpoints verfügbar:

| Endpoint                    | URL                                                                |
| --------------------------- | ------------------------------------------------------------------ |
| **OIDC Discovery**          | `http://localhost:8088/.well-known/openid-configuration`           |
| **JWKS (Public Keys)**      | `http://localhost:8088/oauth/v2/keys`                              |
| **Authorization Endpoint**  | `http://localhost:8088/oauth/v2/authorize`                         |
| **Token Endpoint**          | `http://localhost:8088/oauth/v2/token`                             |
| **Userinfo Endpoint**       | `http://localhost:8088/oidc/v1/userinfo`                           |
| **End Session**             | `http://localhost:8088/oidc/v1/end_session`                        |

### 11.1 Discovery prüfen

```bash
curl -s http://localhost:8088/.well-known/openid-configuration | python3 -m json.tool
```

Erwartete Felder: `issuer`, `authorization_endpoint`,
`token_endpoint`, `userinfo_endpoint`, `jwks_uri`.

---

## 12. Ergebnis — benötigte Werte pro Umgebung

### 12.1 Frontend (React SPA)

| Wert            | Wo zu finden                 | Env-Variable                |
| --------------- | ---------------------------- | --------------------------- |
| Client ID       | Application → URLs           | `VITE_OIDC_CLIENT_ID`      |
| Authority URL   | Application → URLs           | `VITE_OIDC_AUTHORITY`      |
| Redirect URI    | Authentication Settings      | `VITE_OIDC_REDIRECT_URI`   |
| Scopes          | (Standard OIDC)              | `VITE_OIDC_SCOPES`         |

Beispiel `.env` (Frontend):

```env
VITE_OIDC_AUTHORITY=http://localhost:8088
VITE_OIDC_CLIENT_ID=<client-id-from-step-5>
VITE_OIDC_REDIRECT_URI=http://localhost:5173/auth/callback/oidc
VITE_OIDC_SCOPE=openid profile email
```

### 12.2 Backend (Platform Service)

| Wert                 | Wo zu finden                 | Env-Variable                           |
| -------------------- | ---------------------------- | -------------------------------------- |
| JWKS URL             | OIDC Discovery               | `OIDC_JWKS_URL`                        |
| Userinfo URL         | OIDC Discovery               | `OIDC_USERINFO_URL`                    |
| Management API URL   | Zitadel Docs                 | `OIDC_ZITADEL_MANAGEMENT_API_URL`      |
| Service Token (PAT)  | Service User (Step 10)       | `OIDC_ZITADEL_SERVICE_TOKEN`           |
| System Admin User    | Zitadel Admin                | `OIDC_ZITADEL_SYSTEM_ADMIN_USERNAME`   |
| Client ID            | API Application (Step 6)     | `OIDC_CLIENT_ID`                       |
| Client Secret        | API Application (Step 6)     | `OIDC_CLIENT_SECRET`                   |

Beispiel `.env` (Platform Service):

```env
OIDC_ISSUER_URL=http://localhost:8088
OIDC_CLIENT_ID=<client-id>
OIDC_JWKS_URL=http://unifiedui-identity:8080/oauth/v2/keys
OIDC_USERINFO_URL=http://unifiedui-identity:8080/oidc/v1/userinfo
OIDC_ZITADEL_MANAGEMENT_API_URL=http://unifiedui-identity:8080/management/v1
OIDC_ZITADEL_SERVICE_TOKEN=<service-user-pat>
OIDC_ZITADEL_SYSTEM_ADMIN_USERNAME=zitadel-admin@zitadel.localhost
IDENTITY_VERIFY_SIGNATURE=true
```

> **Hinweis:** Innerhalb von Docker Compose wird der
> interne Hostname `unifiedui-identity:8080` verwendet
> (Port 8080 intern, 8088 extern gemappt).

---

## 13. Testen

### 13.1 Token manuell anfordern (PKCE)

Für einen schnellen Smoke-Test den Authorization Code Flow
im Browser durchspielen:

1. Im Browser öffnen:
    ```
    http://localhost:8088/oauth/v2/authorize?client_id=<CLIENT_ID>&redirect_uri=http://localhost:5173/callback&response_type=code&scope=openid%20profile%20email&code_challenge=<CHALLENGE>&code_challenge_method=S256
    ```
2. Mit einem Zitadel-User einloggen.
3. Den `code` aus der Redirect-URL extrahieren.
4. Token tauschen:
    ```bash
    curl -X POST http://localhost:8088/oauth/v2/token \
      -d "grant_type=authorization_code" \
      -d "code=<CODE>" \
      -d "redirect_uri=http://localhost:5173/callback" \
      -d "client_id=<CLIENT_ID>" \
      -d "code_verifier=<VERIFIER>"
    ```

### 13.2 Token inspizieren

Den erhaltenen `access_token` auf https://jwt.io einfügen
und prüfen, ob `sub`, `name`, `email` und Gruppen-Claims
vorhanden sind.

### 13.3 JWKS-Validierung prüfen

```bash
curl -s http://localhost:8088/oauth/v2/keys | python3 -m json.tool
```

Muss mindestens einen RSA-Key mit `use: "sig"` enthalten.
