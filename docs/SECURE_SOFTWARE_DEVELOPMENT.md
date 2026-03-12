# Secure Software Development

Leitfaden für sicheres Software Development mit Fokus auf Cloud Deployment (Azure) und Cloud-Native Architektur.

---

## 1. Threat Modeling & Security by Design

- **Threat Modeling vor Entwicklungsstart** — z.B. STRIDE-Methodik (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
- **Attack Surface Analysis** — Angriffsfläche minimieren: nur notwendige Ports, Endpunkte und Services exponieren
- **Security by Design** — Sicherheit von Anfang an in Architektur und Design einplanen, nicht nachträglich
- **Defense in Depth** — Mehrschichtige Sicherheit: jede Schicht (Netzwerk, Plattform, Anwendung, Daten) hat eigene Schutzmaßnahmen
- **Principle of Least Privilege** — Jeder User/Service bekommt nur die minimal notwendigen Rechte

---

## 2. Infrastruktur & Netzwerk

### 2.1 Netzwerk-Sicherheit
- **Private Networking** — VNets, Subnets, Network Security Groups (NSGs)
- **Private Endpoints** — Azure Services über Private Link anbinden (kein Public Internet)
- **Service Endpoints** — Als Alternative zu Private Endpoints für bestimmte Services
- **VPN / ExpressRoute** — Zugriff auf Cloud-Ressourcen nur über VPN oder ExpressRoute (kein öffentlicher Zugriff auf Management-Ebene)
- **DNS Security** — Private DNS Zones für interne Namensauflösung

### 2.2 Perimeter-Schutz
- **WAF (Web Application Firewall)** — Azure Front Door oder Application Gateway mit WAF Policy (OWASP Core Rule Set)
- **DDoS Protection** — Azure DDoS Protection Standard auf VNet-Ebene
- **Rate Limiting / Throttling** — API Management oder Application Gateway Policies
- **Azure Firewall** — Zentrales Netzwerk-Firewall für Outbound-Traffic-Kontrolle

### 2.3 Transport & Verschlüsselung
- **TLS/HTTPS überall** — Kein unverschlüsselter Traffic, TLS 1.2+ erzwingen
- **Encryption at Rest** — Alle Daten verschlüsselt speichern (Azure Storage, SQL, Cosmos DB — standardmäßig aktiv)
- **Encryption in Transit** — Alle Kommunikation zwischen Services verschlüsselt
- **Customer-Managed Keys (CMK)** — Für besonders sensible Daten eigene Schlüssel in Key Vault verwalten

### 2.4 Verfügbarkeit & Resilienz
- **Backup-Strategie** — Automatisierte Backups konfigurieren und regelmäßig Restore testen
- **High Availability** — Availability Zones, Multi-Region Deployment wo nötig
- **Disaster Recovery** — DR-Konzept mit definierten RPO/RTO-Werten
- **PaaS-Services nutzen** — Bringen HA/Backup/Geo-Redundanz mit, müssen aber konfiguriert und bezahlt werden

---

## 3. Identity & Access Management (IAM)

### 3.1 Authentifizierung
- **Microsoft Entra ID als Identity Provider** — Zentrales Identity Management
- **Multi-Factor Authentication (MFA)** — Pflicht für alle Benutzer, insbesondere Admins
- **Conditional Access Policies** — Zugriff nur von bestimmten Geräten, Standorten, Risiko-Leveln
- **Passwordless Authentication** — FIDO2, Windows Hello, Authenticator App bevorzugen
- **Single Sign-On (SSO)** — Über Entra ID für alle Anwendungen

### 3.2 Autorisierung
- **Managed Identity** — Keine API Keys, keine Passwörter für Service-zu-Service Kommunikation
- **Azure RBAC** — Role-Based Access Control auf Azure-Ressourcen-Ebene
- **Application-Level RBAC** — Eigene Rollen- und Berechtigungslogik in der Anwendung
- **Least Privilege Prinzip** — Nur notwendige Rechte vergeben, regelmäßig reviewen
- **Privileged Identity Management (PIM)** — Just-in-Time Access für Admin-Rollen, zeitlich begrenzt

### 3.3 Service-Identitäten
- **Managed Identity bevorzugen** — System-assigned oder User-assigned Managed Identity
- **Keine Secrets in Code oder Config** — Nur im absoluten Notfall Service Principals mit Secrets
- **Workload Identity Federation** — Für externe CI/CD (z.B. GitHub Actions → Azure ohne Secrets)

---

## 4. Secrets Management

- **Azure Key Vault** — Zentraler Speicher für Secrets, Keys und Zertifikate
- **Secrets Binding** — Services lesen Secrets direkt aus Key Vault (Key Vault References in App Service/Container Apps)
- **Secret Rotation** — Automatisierte regelmäßige Rotation von Secrets und Keys
- **Certificate Management** — TLS-Zertifikate in Key Vault verwalten, automatisierte Erneuerung
- **Zugriff über Managed Identity** — Key Vault Access nur über Managed Identity, nicht über Access Keys
- **Key Vault RBAC** — Feingranulare Zugriffssteuerung (wer darf welche Secrets lesen/schreiben)
- **Env Variables** — Nur für Umgebungssteuerung (z.B. `ENVIRONMENT=production`), niemals für Secrets
- **.env in .gitignore** — Lokale .env-Dateien niemals committen, .env.example als Vorlage bereitstellen

---

## 5. Repository & CI/CD Security

### 5.1 Repository-Organisation
- **Git Versionierung** — Gesamter Code unter Versionskontrolle
- **Branch Protection** — main/release Branches geschützt: kein direkter Push, nur über Pull Requests
- **Branching-Konzept** — Definiertes Branching-Modell (z.B. GitFlow, Trunk-Based Development)
- **Code Reviews (PRs)** — Mindestens 4-Augen-Prinzip, verpflichtende Approvals
- **CODEOWNERS** — Definierte Verantwortliche für kritische Code-Bereiche

### 5.2 CI Pipeline Security
- **Automatisierte Security Scans im CI** — Jeder PR wird automatisch geprüft
- **SAST (Static Application Security Testing)** — Code-Analyse auf Schwachstellen (z.B. CodeQL, SonarQube, Semgrep)
- **SCA (Software Composition Analysis)** — Dependency-Scanning (Dependabot, Snyk, Trivy)
- **Secret Scanning** — Automatische Erkennung von Secrets im Code (GitHub Secret Scanning, gitleaks)
- **Container Image Scanning** — Schwachstellen-Scan für Docker Images (Trivy, Defender for Containers)
- **License Compliance** — Prüfung auf problematische Open-Source-Lizenzen
- **Unit Tests / Integration Tests / E2E Tests** — Automatisierte Testsuites im CI
- **Lint & Type Checking** — Code-Qualität automatisiert prüfen

### 5.3 CD Pipeline Security
- **Standardisiertes Deployment** — Infrastructure as Code (Bicep, Terraform), reproduzierbare Deployments
- **Environment Separation** — Strikte Trennung von Dev/Staging/Production
- **Release-Strategie** — Tagging, Semantic Versioning, Conventional Commits für automatisierten Changelog
- **Deployment Approvals** — Manuelle Genehmigung für Production-Deployments
- **Rollback-Strategie** — Schnelles Zurückrollen bei Problemen
- **Workload Identity Federation** — CI/CD Zugriff auf Azure ohne langlebige Secrets

---

## 6. Supply Chain Security

- **Software Bill of Materials (SBOM)** — Automatisierte SBOM-Generierung für jedes Release
- **Dependency Pinning** — Exakte Versionen pinnen (Lock-Files: package-lock.json, uv.lock, go.sum)
- **Regelmäßige Dependency Updates** — Dependabot / Renovate für automatisierte Updates
- **Container Base Images** — Nur vertrauenswürdige, minimale Base Images (Distroless, Alpine)
- **Container Image Signing** — Images signieren (z.B. Cosign/Notation) und Signatur-Verification im Cluster
- **Registry Security** — Private Container Registry (ACR) mit Vulnerability Scanning
- **Trusted Publishers** — Nur Packages von verifizierten Quellen verwenden

---

## 7. Application Security (Security in Code)

### 7.1 Input Validation & Output Encoding
- **Input Validation** — Alle User-Inputs serverseitig validieren (Typ, Länge, Format, Whitelist)
- **Output Encoding** — Alle Ausgaben korrekt encoden (Context-abhängig: HTML, URL, JS, SQL)
- **Daten-Validierung in FE und BE** — Frontend-Validierung für UX, Backend-Validierung für Security
- **Datenbank-Constraints** — Check Constraints, NOT NULL, Foreign Keys als letzte Verteidigungslinie
- **Fail-Fast Prinzip** — Sofort Fehler werfen bei ungültigen Daten — lieber zu früh als zu spät

### 7.2 OWASP Top 10 Schutzmaßnahmen
- **SQL Injection Prevention** — ORM verwenden (SQLAlchemy, etc.), niemals Raw-SQL mit User-Input
- **XSS (Cross-Site Scripting) Prevention** — Output Encoding, Content Security Policy (CSP) Header
- **CSRF Protection** — Anti-CSRF Tokens oder SameSite Cookies
- **SSRF (Server-Side Request Forgery)** — URL-Validierung, Allowlists für externe Aufrufe
- **Broken Access Control** — RBAC auf jedem Endpoint, Autorisierung immer serverseitig prüfen
- **Security Misconfiguration** — Sichere Defaults, keine Debug-Modi in Production
- **Insecure Deserialization** — Nur vertrauenswürdige Datenformate, Pydantic/Schema-Validierung

### 7.3 API Security
- **Authentication auf jedem Endpoint** — Middleware prüft Auth vor Business-Logik
- **RBAC auf Endpunkt- und Daten-Ebene** — ACL, Backend-Endpoint Access Control
- **Rate Limiting pro User/API Key** — Schutz vor Abuse
- **CORS korrekt konfigurieren** — Nur erlaubte Origins, keine Wildcards in Production
- **API Versioning** — Breaking Changes nur in neuen API-Versionen
- **Request Size Limits** — Maximale Payload-Größe begrenzen
- **API Gateway** — Azure API Management als zentraler Einstiegspunkt

### 7.4 Frontend Security
- **Strikte Trennung Frontend / Backend** — Frontend enthält KEINE sensiblen Daten (im Browser sichtbar!)
- **Content Security Policy (CSP)** — Verhindert XSS und Data Injection
- **HTTP Security Headers** — Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options
- **Keine Secrets im Frontend** — API Keys, Tokens etc. gehören ins Backend
- **Secure Cookie Flags** — HttpOnly, Secure, SameSite

### 7.5 Logging & Sichere Datenverarbeitung
- **Keinen User-Content ungeschützt loggen** — PII/sensible Daten maskieren oder ausschließen
- **Keine Secrets in Logs** — Tokens, Passwörter, API Keys niemals loggen
- **Structured Logging** — JSON-basiertes Logging für maschinelle Auswertung
- **Audit Trail** — Sicherheitsrelevante Aktionen protokollieren (Login, Permission Changes, Data Access)

---

## 8. Container & Cloud-Native Security

- **Minimale Base Images** — Distroless oder Alpine, keine unnötigen Pakete
- **Non-Root Container** — Container als Non-Root User ausführen
- **Read-Only Filesystem** — Container Filesystem read-only mounten wo möglich
- **Image Scanning** — Automatisiertes Vulnerability Scanning in CI und Registry (Trivy, Defender)
- **Pod Security Standards** — Kubernetes Pod Security Admission (Restricted Profile)
- **Network Policies** — Kubernetes Network Policies für Pod-zu-Pod Kommunikation
- **Service Mesh** — mTLS zwischen Services (z.B. Dapr Sidecar, Istio — bei Container Apps built-in)
- **Resource Limits** — CPU/Memory Limits setzen gegen Resource Exhaustion

---

## 9. Monitoring, Logging & Incident Response

### 9.1 Monitoring & Observability
- **Application Insights** — APM, Distributed Tracing, Performance Monitoring
- **OpenTelemetry** — Standardisierte Metriken, Traces und Logs
- **Azure Monitor** — Infrastruktur-Metriken und Log Analytics
- **Alerting** — Automatische Alerts bei Anomalien, Fehlern, Security Events
- **Dashboards** — Zentrale Übersicht über System-Health und Security-Metriken

### 9.2 Security Monitoring (Azure)
- **Microsoft Defender for Cloud** — Cloud Security Posture Management (CSPM), Threat Protection
- **Microsoft Sentinel** — SIEM & SOAR für Security Event Management
- **Defender for Containers** — Runtime Threat Detection für Container-Workloads
- **Defender for Key Vault** — Erkennung anomaler Key Vault Zugriffe
- **Entra ID Sign-in Logs** — Überwachung verdächtiger Anmeldungen

### 9.3 Incident Response
- **Incident Response Plan** — Dokumentiertes Vorgehen bei Security Incidents
- **Runbooks** — Automatisierte oder dokumentierte Reaktionen auf bekannte Incident-Typen
- **Post-Mortem Prozess** — Nach jedem Incident: Root Cause Analysis und Verbesserungen
- **Communication Plan** — Klare Kommunikationswege bei Incidents (intern und extern)

---

## 10. Compliance & Governance

- **Azure Policy** — Automatisierte Durchsetzung von Unternehmensrichtlinien (z.B. keine Public Endpoints)
- **Azure Blueprints / Landing Zones** — Standardisierte, sichere Umgebungen provisionieren
- **DSGVO / GDPR** — Datenschutz-Anforderungen: Data Residency, Right to Erasure, Data Processing Agreements
- **Data Classification** — Daten klassifizieren (Public, Internal, Confidential, Restricted) und entsprechend schützen
- **Regulatory Compliance** — Branchenspezifische Anforderungen (ISO 27001, SOC 2, etc.)
- **Regelmäßige Security Audits** — Externe Penetration Tests, interne Security Reviews
- **Security Training** — Regelmäßige Schulungen für Entwickler (Secure Coding, OWASP Top 10)

---

## Checkliste (Quick Reference)

| Bereich | Maßnahme | Priorität |
|---------|----------|-----------|
| Identity | Managed Identity statt Secrets | 🔴 Kritisch |
| Identity | MFA für alle Benutzer | 🔴 Kritisch |
| Secrets | Key Vault für alle Secrets | 🔴 Kritisch |
| Secrets | Secret Rotation einrichten | 🟡 Hoch |
| Netzwerk | Private Endpoints für Azure Services | 🟡 Hoch |
| Netzwerk | WAF aktivieren | 🟡 Hoch |
| Code | Input Validation (FE + BE) | 🔴 Kritisch |
| Code | ORM statt Raw-SQL | 🔴 Kritisch |
| Code | CORS korrekt konfigurieren | 🟡 Hoch |
| CI/CD | SAST/SCA im CI | 🟡 Hoch |
| CI/CD | Secret Scanning | 🔴 Kritisch |
| CI/CD | Container Image Scanning | 🟡 Hoch |
| Container | Non-Root, Minimale Base Images | 🟡 Hoch |
| Monitoring | Defender for Cloud aktivieren | 🟡 Hoch |
| Monitoring | Application Insights einrichten | 🟢 Mittel |
| Compliance | Azure Policy konfigurieren | 🟢 Mittel |
| Prozess | Incident Response Plan erstellen | 🟡 Hoch |
| Prozess | Security Training für Devs | 🟢 Mittel |
