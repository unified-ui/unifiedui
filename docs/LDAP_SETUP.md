# Anleitung — OpenLDAP Setup (Lokale Entwicklung)

> **Project**: unified-ui

---

## 1. Überblick

Diese Anleitung beschreibt die Einrichtung von **OpenLDAP**
als LDAP-Backend für die unified-ui Plattform.
OpenLDAP dient als Directory Service für User- und
Group-Management und wird über den LDAP Identity Provider
im Platform Service angebunden.

**Architektur:**

- **OpenLDAP** — LDAP-Server mit vorkonfigurierten
    Testdaten (Users + Groups via Seed-LDIF).
- **phpLDAPadmin** — Web-UI zum Verwalten des
    LDAP-Verzeichnisses (Users, Groups, OUs).
- **Platform Service** — Bindet sich über den
    `LDAPIdentityProvider` an den LDAP-Server an
    (User/Group-Abfragen per LDAP-Bind).
- Authentifizierung läuft über einen OIDC-Provider
    (z. B. Zitadel), **nicht** direkt über LDAP.
    LDAP dient nur als Directory (User/Group-Lookup).

**Voraussetzung:** OpenLDAP läuft via Docker Compose
(siehe `docker/local/ldap.yml`).

---

## 2. OpenLDAP starten

```bash
cd docker/local
docker compose up unifiedui-ldap unifiedui-ldap-admin
```

Beim ersten Start:
- OpenLDAP initialisiert die Datenbank mit der
    konfigurierten Domain (`unifiedui.local`).
- Seed-Daten aus `ldap/seed.ldif` werden geladen
    (3 User + 2 Gruppen).
- phpLDAPadmin startet mit Verbindung zum LDAP-Server.

---

## 3. phpLDAPadmin aufrufen

> **URL:** https://localhost:6443

> **Wichtig:** phpLDAPadmin läuft auf **HTTPS** (selbst-signiertes
> Zertifikat). Der Browser zeigt eine Sicherheitswarnung —
> **Advanced → Proceed** klicken.
> Nicht `http://localhost:6443` verwenden — das gibt einen
> "Bad Request" Fehler.

| Feld     | Wert                                         |
| -------- | -------------------------------------------- |
| Login DN | `cn=admin,dc=unifiedui,dc=local`             |
| Passwort | `admin` (aus `LDAP_ADMIN_PASSWORD`)           |

---

## 4. Verzeichnisstruktur

Nach dem Start mit Seed-Daten sieht das LDAP-Verzeichnis
folgendermaßen aus:

```
dc=unifiedui,dc=local
├── cn=admin                          ← LDAP Admin (built-in)
├── ou=Users
│   ├── uid=testuser1                 ← Test User 1
│   ├── uid=testuser2                 ← Jane Developer
│   └── uid=admin                     ← System Admin
└── ou=Groups
    ├── cn=developers                 ← testuser1, testuser2
    └── cn=admins                     ← admin
```

---

## 5. Vorkonfigurierte Testdaten

### 5.1 Benutzer

| Username    | Name            | E-Mail                         | Passwort     |
| ----------- | --------------- | ------------------------------ | ------------ |
| `testuser1` | Test User 1     | `testuser1@unifiedui.local`    | `Test1234!`  |
| `testuser2` | Jane Developer  | `testuser2@unifiedui.local`    | `Test1234!`  |
| `admin`     | System Admin    | `admin@unifiedui.local`        | `Admin1234!` |

### 5.2 Gruppen

| Gruppenname   | Mitglieder                     | Beschreibung         |
| ------------- | ------------------------------ | -------------------- |
| `developers`  | `testuser1`, `testuser2`       | Development team     |
| `admins`      | `admin`                        | Administrators       |

> Die Seed-Daten werden über `docker/local/ldap/seed.ldif`
> definiert. Änderungen an der Datei erfordern ein Neustarten
> mit gelöschtem Volume:
> `docker compose down -v` und `docker compose up`.

---

## 6. LDAP-Verbindung testen

### 6.1 Per ldapsearch (CLI)

```bash
# Gesamtes Verzeichnis auflisten
ldapsearch -x -H ldap://localhost:389 \
  -D "cn=admin,dc=unifiedui,dc=local" \
  -w admin \
  -b "dc=unifiedui,dc=local"
```

### 6.2 Nur Benutzer auflisten

```bash
ldapsearch -x -H ldap://localhost:389 \
  -D "cn=admin,dc=unifiedui,dc=local" \
  -w admin \
  -b "ou=Users,dc=unifiedui,dc=local" \
  "(objectClass=inetOrgPerson)" \
  uid cn mail
```

### 6.3 Nur Gruppen auflisten

```bash
ldapsearch -x -H ldap://localhost:389 \
  -D "cn=admin,dc=unifiedui,dc=local" \
  -w admin \
  -b "ou=Groups,dc=unifiedui,dc=local" \
  "(objectClass=groupOfNames)" \
  cn member description
```

### 6.4 User-Bind testen (Authentifizierung)

```bash
ldapsearch -x -H ldap://localhost:389 \
  -D "uid=testuser1,ou=Users,dc=unifiedui,dc=local" \
  -w "Test1234!" \
  -b "dc=unifiedui,dc=local" \
  -s base
```

> Wenn der Befehl erfolgreich ist (Exit Code 0),
> ist die Authentifizierung gültig.

---

## 7. Benutzer & Gruppen verwalten

### 7.1 Neuen Benutzer per phpLDAPadmin anlegen

1. https://localhost:6443 öffnen und einloggen.
2. Links im Baum: `ou=Users` auswählen.
3. **Create a child entry** klicken.
4. Template: **Default** oder **inetOrgPerson** wählen.
5. Felder ausfüllen:

| Feld         | Beispielwert                      |
| ------------ | --------------------------------- |
| cn           | `Max Mustermann`                  |
| sn           | `Mustermann`                      |
| givenName    | `Max`                             |
| uid          | `mmustermann`                     |
| mail         | `mmustermann@unifiedui.local`     |
| userPassword | (Passwort setzen)                 |

6. **Create Object** klicken.

### 7.2 Neuen Benutzer per ldapadd (CLI)

```bash
ldapadd -x -H ldap://localhost:389 \
  -D "cn=admin,dc=unifiedui,dc=local" \
  -w admin << 'EOF'
dn: uid=mmustermann,ou=Users,dc=unifiedui,dc=local
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: mmustermann
sn: Mustermann
givenName: Max
cn: Max Mustermann
displayName: Max Mustermann
mail: mmustermann@unifiedui.local
uidNumber: 10004
gidNumber: 10000
homeDirectory: /home/mmustermann
userPassword: SecurePass123!
EOF
```

### 7.3 User zu Gruppe hinzufügen

```bash
ldapmodify -x -H ldap://localhost:389 \
  -D "cn=admin,dc=unifiedui,dc=local" \
  -w admin << 'EOF'
dn: cn=developers,ou=Groups,dc=unifiedui,dc=local
changetype: modify
add: member
member: uid=mmustermann,ou=Users,dc=unifiedui,dc=local
EOF
```

### 7.4 Neue Gruppe erstellen

```bash
ldapadd -x -H ldap://localhost:389 \
  -D "cn=admin,dc=unifiedui,dc=local" \
  -w admin << 'EOF'
dn: cn=viewers,ou=Groups,dc=unifiedui,dc=local
objectClass: groupOfNames
cn: viewers
description: Read-only users
member: uid=testuser1,ou=Users,dc=unifiedui,dc=local
EOF
```

---

## 8. Ergebnis — benötigte Werte für Platform Service

| Wert              | Wert (Local Dev)                        | Env-Variable                |
| ----------------- | --------------------------------------- | --------------------------- |
| LDAP Server URL   | `ldap://unifiedui-ldap:389`             | `LDAP_SERVER_URL`           |
| Bind DN           | `cn=admin,dc=unifiedui,dc=local`       | `LDAP_BIND_DN`              |
| Bind Password     | `admin`                                 | `LDAP_BIND_PASSWORD`        |
| User Base DN      | `ou=Users,dc=unifiedui,dc=local`       | `LDAP_USER_BASE_DN`         |
| Group Base DN     | `ou=Groups,dc=unifiedui,dc=local`      | `LDAP_GROUP_BASE_DN`        |
| User Object Class | `inetOrgPerson`                         | `LDAP_USER_OBJECT_CLASS`    |
| Group Object Class| `groupOfNames`                          | `LDAP_GROUP_OBJECT_CLASS`   |
| User ID Attr      | `uid`                                   | `LDAP_USER_ID_ATTRIBUTE`    |
| Group Member Attr | `member`                                | `LDAP_GROUP_MEMBER_ATTRIBUTE`|

> **Hinweis:** Innerhalb von Docker Compose wird der
> interne Hostname `unifiedui-ldap:389` verwendet.
> Von außen (Host): `ldap://localhost:389`.

Beispiel `.env` (Platform Service):

```env
IDENTITY_PROVIDER=ldap
LDAP_SERVER_URL=ldap://unifiedui-ldap:389
LDAP_BIND_DN=cn=admin,dc=unifiedui,dc=local
LDAP_BIND_PASSWORD=admin
LDAP_USER_BASE_DN=ou=Users,dc=unifiedui,dc=local
LDAP_GROUP_BASE_DN=ou=Groups,dc=unifiedui,dc=local
LDAP_USER_OBJECT_CLASS=inetOrgPerson
LDAP_GROUP_OBJECT_CLASS=groupOfNames
LDAP_USER_ID_ATTRIBUTE=uid
LDAP_GROUP_MEMBER_ATTRIBUTE=member
```

---

## 9. Troubleshooting

### Container startet nicht

```bash
docker compose logs unifiedui-ldap
```

Häufige Ursachen:
- Port 389 bereits belegt → `lsof -i :389`
- Volume-Konflikte → `docker compose down -v` und neu starten

### LDAP-Verbindung schlägt fehl

```bash
# Verbindung testen
ldapsearch -x -H ldap://localhost:389 -b "" -s base namingContexts
```

Muss `dc=unifiedui,dc=local` zurückgeben.

### phpLDAPadmin "Bad Request"

- **Ursache:** `http://` statt `https://` verwendet.
- **Lösung:** https://localhost:6443 verwenden.
- Der Browser zeigt eine Zertifikatswarnung — diese akzeptieren.

### Seed-Daten werden nicht geladen

Seed-Daten werden nur beim **ersten Start** geladen.
Wenn Änderungen an `seed.ldif` gemacht wurden:

```bash
docker compose down
docker volume rm unifiedui-local_ldap_data unifiedui-local_ldap_config
docker compose up unifiedui-ldap unifiedui-ldap-admin
```
