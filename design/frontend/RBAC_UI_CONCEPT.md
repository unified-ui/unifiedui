# Frontend RBAC UI Concept

## Übersicht

Dieses Konzept definiert, wie Role-Based Access Control (RBAC) im Frontend implementiert wird, um UI-Elemente basierend auf den Berechtigungen des Benutzers:
- **Auszublenden** (kein Zugriff)
- **Auszugrauen/Deaktivieren** (nur Lesen, kein Schreiben)

---

## 1. Berechtigungsstruktur

### 1.1 Tenant-weite Rollen (`TenantPermissionEnum`)

| Rolle | Beschreibung | Befugnisse |
|-------|--------------|------------|
| `READER` | Basis-Lesezugriff | Kann Tenant-Ressourcen sehen |
| `GLOBAL_ADMIN` | Super-Admin | Vollzugriff auf ALLE Ressourcen |
| `APPLICATIONS_ADMIN` | App-Admin | Admin auf alle Applications |
| `APPLICATIONS_CREATOR` | App-Ersteller | Kann Applications erstellen |
| `AUTONOMOUS_AGENTS_ADMIN` | Agent-Admin | Admin auf alle Autonomous Agents |
| `AUTONOMOUS_AGENTS_CREATOR` | Agent-Ersteller | Kann Autonomous Agents erstellen |
| `CONVERSATIONS_ADMIN` | Konv.-Admin | Admin auf alle Conversations |
| `CONVERSATIONS_CREATOR` | Konv.-Ersteller | Kann Conversations erstellen |
| `CREDENTIALS_ADMIN` | Cred.-Admin | Admin auf alle Credentials |
| `CREDENTIALS_CREATOR` | Cred.-Ersteller | Kann Credentials erstellen |
| `CHAT_WIDGETS_ADMIN` | Widget-Admin | Admin auf alle Chat Widgets |
| `CHAT_WIDGETS_CREATOR` | Widget-Ersteller | Kann Chat Widgets erstellen |
| `REACT_AGENT_ADMIN` | ReACT-Admin | Admin auf alle ReACT Agents + Tools |
| `REACT_AGENT_CREATOR` | ReACT-Ersteller | Kann ReACT Agents erstellen |
| `CUSTOM_GROUPS_ADMIN` | Gruppen-Admin | Admin auf alle Custom Groups |
| `CUSTOM_GROUP_CREATOR` | Gruppen-Ersteller | Kann Custom Groups erstellen |
| `TENANT_AI_MODELS_ADMIN` | AI-Models Admin | Admin auf Tenant AI Models |

### 1.2 Ressourcen-Berechtigungen (`PermissionActionEnum`)

| Berechtigung | Hierarchie | Befugnisse |
|--------------|------------|------------|
| `READ` | Niedrigste | Ressource ansehen |
| `WRITE` | Mittel | Ressource bearbeiten + READ |
| `ADMIN` | Höchste | Vollzugriff + Mitglieder verwalten + DELETE |

**Hierarchie-Regel**: `ADMIN` ≥ `WRITE` ≥ `READ`

---

## 2. Datenquellen für Berechtigungen

### 2.1 Tenant-Rollen (bereits verfügbar)

**Quelle**: `GET /api/v1/identity/me` → `MeResponse.tenants[].roles`

```typescript
interface TenantWithRoles {
  tenant: TenantResponse;
  roles: string[];  // z.B. ['GLOBAL_ADMIN', 'APPLICATIONS_CREATOR']
}
```

**Problem**: Aktuell werden die Rollen im `IdentityContext` **verworfen**:
```typescript
// AKTUELL (falsch):
const tenantList = meResponse.tenants?.map(t => t.tenant) || [];

// NEU (korrekt):
const tenantsWithRoles = meResponse.tenants || [];
```

### 2.2 Ressourcen-Berechtigungen (neu zu fetchen bei Bedarf)

Für ressourcenspezifische Berechtigungen (z.B. hat User WRITE auf Application X?) gibt es zwei Ansätze:

**Option A: Principals-Endpoint pro Ressource**
- `GET /applications/{id}/principals` → Prüfen ob eigene `principal_id` in Liste ist
- Nachteil: Viele API-Calls bei Listen

**Option B: Neuer Endpoint für eigene Berechtigungen** (empfohlen)
- `GET /applications/{id}/my-permission` → `{ action: 'WRITE' }`
- Oder: Backend liefert `my_permission` im Response jeder Ressource mit

**Option C: Inline im Response** (am effizientesten)
- Jede Ressourcenabfrage liefert `my_permission: 'WRITE' | 'READ' | 'ADMIN' | null`
- Backend berechnet bereits jetzt Berechtigungen → einfach mitsenden

---

## 3. Architektur-Konzept

### 3.1 Erweiterter IdentityContext

```typescript
interface TenantWithRoles {
  tenant: TenantResponse;
  roles: TenantPermissionEnum[];
}

interface IdentityContextType {
  user: IdentityUser | null;
  selectedTenant: TenantResponse | null;
  selectedTenantRoles: TenantPermissionEnum[];  // NEU
  // ...
}
```

### 3.2 Neuer `usePermissions` Hook

```typescript
interface UsePermissionsReturn {
  // Tenant-Level Checks
  hasRole: (role: TenantPermissionEnum) => boolean;
  hasAnyRole: (roles: TenantPermissionEnum[]) => boolean;
  isGlobalAdmin: boolean;
  
  // Resource-Type Level (basierend auf Tenant-Rollen)
  canCreate: (resourceType: ResourceType) => boolean;
  isResourceAdmin: (resourceType: ResourceType) => boolean;
  
  // Resource-Instance Level (benötigt spezifische Permission)
  canRead: (permission: PermissionActionEnum | null) => boolean;
  canWrite: (permission: PermissionActionEnum | null) => boolean;
  canAdmin: (permission: PermissionActionEnum | null) => boolean;
  canDelete: (permission: PermissionActionEnum | null) => boolean;
}

type ResourceType = 
  | 'applications' 
  | 'autonomous-agents' 
  | 'chat-widgets' 
  | 're-act-agents'
  | 'conversations'
  | 'credentials'
  | 'custom-groups'
  | 'tools'
  | 'tenant-ai-models';
```

### 3.3 Permission-Gate Komponenten

```tsx
// Versteckt Kinder wenn keine Berechtigung
<PermissionGate 
  requiredRole="APPLICATIONS_CREATOR"
  fallback={null}  // oder <Tooltip>Keine Berechtigung</Tooltip>
>
  <Button>Application erstellen</Button>
</PermissionGate>

// Deaktiviert Kinder wenn keine Berechtigung
<PermissionGate 
  permission={resource.my_permission}
  requiredAction="WRITE"
  mode="disable"
>
  <Button>Speichern</Button>
</PermissionGate>
```

---

## 4. UI-Elemente und Berechtigungslogik

### 4.1 Listen-Seiten (ApplicationsPage, AutonomousAgentsPage, etc.)

| Element | Verhalten | Prüfung |
|---------|-----------|---------|
| Create Button | Verstecken | `canCreate(resourceType)` |
| Empty State Create-Action | Verstecken | `canCreate(resourceType)` |
| Status Toggle (Switch) | Deaktivieren | `canWrite(row.my_permission)` |
| Open/View | Immer aktiv | Nur `READ` nötig (über Liste bereits impliziert) |
| Edit | Deaktivieren | `canWrite(row.my_permission)` |
| Manage Access | Verstecken | `canAdmin(row.my_permission)` |
| Duplicate | Verstecken | `canCreate(resourceType)` |
| Delete | Verstecken | `canAdmin(row.my_permission)` |
| Favorite Toggle | Immer aktiv | User-Präferenz, keine Permission |

### 4.2 Detail-Seiten (AutonomousAgentDetailsPage, etc.)

| Element | Verhalten | Prüfung |
|---------|-----------|---------|
| Edit Button | Verstecken | `canWrite(resource.my_permission)` |
| Save Button | Deaktivieren | `canWrite(resource.my_permission)` |
| Delete | Verstecken | `canAdmin(resource.my_permission)` |
| API Key Reveal | Verstecken | `canAdmin(resource.my_permission)` |
| Key Rotation | Verstecken | `canAdmin(resource.my_permission)` |
| Alle Formularfelder | Deaktivieren | `canWrite(resource.my_permission)` |

### 4.3 Edit-Dialoge

| Element | Verhalten | Prüfung |
|---------|-----------|---------|
| Details Tab | Immer sichtbar | `READ` (Dialog öffnen bereits geprüft) |
| IAM Tab | Verstecken | `canAdmin(resource.my_permission)` |
| Save Button | Deaktivieren | `canWrite(resource.my_permission)` |
| Status Toggle | Deaktivieren | `canWrite(resource.my_permission)` |
| Alle Formularfelder | Deaktivieren | `canWrite(resource.my_permission)` |

### 4.4 ManageAccessTable

| Element | Verhalten | Prüfung |
|---------|-----------|---------|
| Add Access Button | Verstecken | `canAdmin(resource.my_permission)` |
| Role Checkboxes | Deaktivieren | `canAdmin(resource.my_permission)` |
| Remove Principal | Verstecken | `canAdmin(resource.my_permission)` |

### 4.5 TenantSettingsPage

| Element | Verhalten | Prüfung |
|---------|-----------|---------|
| Access (IAM) Tab | Verstecken | `!hasRole('GLOBAL_ADMIN')` |
| Add Access Button | Verstecken | `!hasRole('GLOBAL_ADMIN')` |
| Role Checkboxes | Deaktivieren | `!hasRole('GLOBAL_ADMIN')` |
| Remove Access | Verstecken | `!hasRole('GLOBAL_ADMIN')` |
| Create Credential | Verstecken | `!canCreate('credentials')` |
| Create AI Model | Verstecken | `!hasRole('TENANT_AI_MODELS_ADMIN') && !isGlobalAdmin` |
| Create Tool | Verstecken | `!canCreate('tools')` |
| Create Custom Group | Verstecken | `!canCreate('custom-groups')` |

### 4.6 Sidebar

| Element | Verhalten | Prüfung |
|---------|-----------|---------|
| + Button (Application) | Verstecken | `!canCreate('applications')` |
| + Button (Autonomous Agent) | Verstecken | `!canCreate('autonomous-agents')` |
| + Button (Chat Widget) | Verstecken | `!canCreate('chat-widgets')` |
| + Button (ReACT Agent) | Verstecken | `!canCreate('re-act-agents')` |
| Settings Link | Immer sichtbar | Jeder kann Settings sehen |

### 4.7 ConversationsPage / Chat

| Element | Verhalten | Prüfung |
|---------|-----------|---------|
| New Chat | Sichtbar wenn Apps vorhanden | Implizit durch App-Access |
| Share Button | Verstecken | `canAdmin(conversation.my_permission)` |
| Delete Conversation | Verstecken | `canAdmin(conversation.my_permission)` |
| Edit Message | Deaktivieren | `canWrite(conversation.my_permission)` |
| Send Message | Deaktivieren | `canWrite(conversation.my_permission)` |

---

## 5. Performance-Optimierung

### 5.1 Tenant-Rollen (performant)

- **Fetch**: Einmal bei Login via `/identity/me`
- **Cache**: Im `IdentityContext` für gesamte Session
- **Invalidierung**: Bei Tenant-Wechsel + manuelles Refresh

```typescript
// Kosten: 0 API-Calls bei Nutzung
const { hasRole, canCreate, isGlobalAdmin } = usePermissions();
```

### 5.2 Ressourcen-Berechtigungen (optimiert)

**Empfehlung: Backend erweitert alle Ressourcen-Responses um `my_permission`**

```typescript
// Beispiel: Application Response
interface ApplicationResponse {
  id: string;
  name: string;
  // ... andere Felder
  my_permission: PermissionActionEnum | null;  // NEU
}
```

**Vorteile:**
- Keine zusätzlichen API-Calls
- Permission wird beim Laden der Ressource mitgeliefert
- Backend-Logik bereits vorhanden (check_permissions)

**Backend-Änderung (geschätzter Aufwand: ~2h)**:
1. `my_permission` Feld in alle *Response-Schemas hinzufügen
2. In Handlers: Nach Abfrage die Permission des Users ermitteln und mitsenden
3. Bei Listen: Für jedes Item die Permission berechnen (bereits in members-Join vorhanden)

### 5.3 Fallback ohne Backend-Änderung

Falls Backend-Änderung nicht sofort möglich:

```typescript
// Permission-Cache pro Session
const permissionCache = new Map<string, PermissionActionEnum>();

// Lazy-Fetch bei erstem Zugriff
const getResourcePermission = async (
  resourceType: ResourceType, 
  resourceId: string
): Promise<PermissionActionEnum | null> => {
  const cacheKey = `${resourceType}:${resourceId}`;
  
  if (permissionCache.has(cacheKey)) {
    return permissionCache.get(cacheKey)!;
  }
  
  const principals = await apiClient.getResourcePrincipals(resourceType, resourceId);
  const myPermission = findMyPermission(principals, user.id, user.groups);
  
  permissionCache.set(cacheKey, myPermission);
  return myPermission;
};
```

---

## 6. Implementierungsplan

### Phase 1: Grundlagen (1-2 Tage)

1. **IdentityContext erweitern**
   - `selectedTenantRoles` State hinzufügen
   - Rollen nicht mehr verwerfen bei `refreshIdentity()`

2. **`usePermissions` Hook erstellen**
   - Tenant-Level: `hasRole()`, `hasAnyRole()`, `isGlobalAdmin`
   - Resource-Type: `canCreate()`, `isResourceAdmin()`
   - Resource-Instance: `canRead()`, `canWrite()`, `canAdmin()`

3. **`PermissionGate` Komponente erstellen**
   - Mode: `hide` (default) vs `disable`
   - Props: `requiredRole`, `requiredAction`, `permission`

### Phase 2: Backend-Erweiterung (optional, 2-4h)

1. **`my_permission` in Responses hinzufügen**
   - Alle *Response-Schemas erweitern
   - Handler-Logic: Permission ermitteln und mitsenden

### Phase 3: UI-Anpassungen (2-3 Tage)

1. **Listen-Seiten**
   - Create-Button mit `PermissionGate`
   - DataTableRow Actions anpassen

2. **Detail-Seiten**
   - Edit/Save Buttons
   - Formular-Felder deaktivieren

3. **Dialoge**
   - IAM Tab Sichtbarkeit
   - Formular-Felder

4. **TenantSettings**
   - Tab-Sichtbarkeit
   - Create-Buttons
   - IAM-Tabelle

5. **Sidebar + Chat**
   - Create-Buttons
   - Aktionen

### Phase 4: Testing & Feinschliff (1 Tag)

1. Tests für `usePermissions` Hook
2. Tests für `PermissionGate` Komponente
3. E2E-Tests mit verschiedenen Rollen

---

## 7. API-Typen Erweiterung (optional)

```typescript
// types.ts - Erweiterte Response-Typen

export interface ApplicationResponse {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  type: ApplicationTypeEnum;
  config: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  my_permission?: PermissionActionEnum;  // NEU
}

// Analog für alle anderen Ressourcen...
```

---

## 8. Hook Implementation (Entwurf)

```typescript
// src/hooks/usePermissions.ts

import { useIdentity } from '../contexts';
import { TenantPermissionEnum, PermissionActionEnum } from '../api/types';

type ResourceType = 
  | 'applications' 
  | 'autonomous-agents' 
  | 'chat-widgets' 
  | 're-act-agents'
  | 'conversations'
  | 'credentials'
  | 'custom-groups'
  | 'tools';

const CREATOR_ROLES: Record<ResourceType, TenantPermissionEnum> = {
  'applications': 'APPLICATIONS_CREATOR',
  'autonomous-agents': 'AUTONOMOUS_AGENTS_CREATOR',
  'chat-widgets': 'CHAT_WIDGETS_CREATOR',
  're-act-agents': 'REACT_AGENT_CREATOR',
  'conversations': 'CONVERSATIONS_CREATOR',
  'credentials': 'CREDENTIALS_CREATOR',
  'custom-groups': 'CUSTOM_GROUP_CREATOR',
  'tools': 'REACT_AGENT_CREATOR',  // Tools require ReACT role
};

const ADMIN_ROLES: Record<ResourceType, TenantPermissionEnum> = {
  'applications': 'APPLICATIONS_ADMIN',
  'autonomous-agents': 'AUTONOMOUS_AGENTS_ADMIN',
  'chat-widgets': 'CHAT_WIDGETS_ADMIN',
  're-act-agents': 'REACT_AGENT_ADMIN',
  'conversations': 'CONVERSATIONS_ADMIN',
  'credentials': 'CREDENTIALS_ADMIN',
  'custom-groups': 'CUSTOM_GROUPS_ADMIN',
  'tools': 'REACT_AGENT_ADMIN',
};

export function usePermissions() {
  const { selectedTenantRoles } = useIdentity();
  
  const hasRole = (role: TenantPermissionEnum): boolean => {
    return selectedTenantRoles.includes(role);
  };
  
  const hasAnyRole = (roles: TenantPermissionEnum[]): boolean => {
    return roles.some(role => selectedTenantRoles.includes(role));
  };
  
  const isGlobalAdmin = hasRole('GLOBAL_ADMIN');
  
  const canCreate = (resourceType: ResourceType): boolean => {
    if (isGlobalAdmin) return true;
    const creatorRole = CREATOR_ROLES[resourceType];
    const adminRole = ADMIN_ROLES[resourceType];
    return hasRole(creatorRole) || hasRole(adminRole);
  };
  
  const isResourceAdmin = (resourceType: ResourceType): boolean => {
    if (isGlobalAdmin) return true;
    return hasRole(ADMIN_ROLES[resourceType]);
  };
  
  // Resource-Instance checks (based on my_permission from resource)
  const canRead = (permission: PermissionActionEnum | null | undefined): boolean => {
    if (isGlobalAdmin) return true;
    return permission != null;  // READ, WRITE, or ADMIN all allow reading
  };
  
  const canWrite = (permission: PermissionActionEnum | null | undefined): boolean => {
    if (isGlobalAdmin) return true;
    return permission === 'WRITE' || permission === 'ADMIN';
  };
  
  const canAdmin = (permission: PermissionActionEnum | null | undefined): boolean => {
    if (isGlobalAdmin) return true;
    return permission === 'ADMIN';
  };
  
  const canDelete = canAdmin;  // Delete requires ADMIN
  
  return {
    hasRole,
    hasAnyRole,
    isGlobalAdmin,
    canCreate,
    isResourceAdmin,
    canRead,
    canWrite,
    canAdmin,
    canDelete,
  };
}
```

---

## 9. PermissionGate Komponente (Entwurf)

```tsx
// src/components/common/PermissionGate/PermissionGate.tsx

import type { FC, ReactNode } from 'react';
import { Tooltip } from '@mantine/core';
import { usePermissions } from '../../../hooks';
import { TenantPermissionEnum, PermissionActionEnum } from '../../../api/types';

interface PermissionGateProps {
  children: ReactNode;
  
  // Tenant-Level Check (OR)
  requiredRole?: TenantPermissionEnum;
  requiredRoles?: TenantPermissionEnum[];
  
  // Resource-Instance Check
  permission?: PermissionActionEnum | null;
  requiredAction?: 'READ' | 'WRITE' | 'ADMIN';
  
  // Behavior
  mode?: 'hide' | 'disable';
  fallback?: ReactNode;
  tooltip?: string;
}

export const PermissionGate: FC<PermissionGateProps> = ({
  children,
  requiredRole,
  requiredRoles,
  permission,
  requiredAction = 'READ',
  mode = 'hide',
  fallback = null,
  tooltip = 'Keine Berechtigung',
}) => {
  const { hasRole, hasAnyRole, canRead, canWrite, canAdmin } = usePermissions();
  
  let allowed = true;
  
  // Check tenant-level role
  if (requiredRole) {
    allowed = hasRole(requiredRole);
  } else if (requiredRoles && requiredRoles.length > 0) {
    allowed = hasAnyRole(requiredRoles);
  }
  
  // Check resource-level permission
  if (allowed && permission !== undefined) {
    switch (requiredAction) {
      case 'READ':
        allowed = canRead(permission);
        break;
      case 'WRITE':
        allowed = canWrite(permission);
        break;
      case 'ADMIN':
        allowed = canAdmin(permission);
        break;
    }
  }
  
  if (!allowed) {
    if (mode === 'hide') {
      return <>{fallback}</>;
    }
    
    // Mode: disable - wrap with tooltip
    return (
      <Tooltip label={tooltip} disabled={!tooltip}>
        <span style={{ display: 'contents' }}>
          {/* Clone children with disabled prop */}
          {React.Children.map(children, child => {
            if (React.isValidElement(child)) {
              return React.cloneElement(child, { disabled: true } as any);
            }
            return child;
          })}
        </span>
      </Tooltip>
    );
  }
  
  return <>{children}</>;
};
```

---

## 10. Zusammenfassung

### Vorteile dieses Konzepts

1. **Performant**: Tenant-Rollen einmal laden, ressourcenspezifisch nur bei Nutzung
2. **Wartbar**: Zentrale Logik in Hook + Komponente
3. **Konsistent**: Einheitliche Patterns für alle UI-Elemente
4. **Erweiterbar**: Einfach neue Ressourcen hinzufügen
5. **Testbar**: Hook + Komponente gut isoliert testbar

### Geschätzter Aufwand

| Phase | Aufwand |
|-------|---------|
| Grundlagen (Context + Hook + Gate) | 1-2 Tage |
| Backend-Erweiterung (my_permission) | 2-4 Stunden |
| UI-Anpassungen | 2-3 Tage |
| Tests | 1 Tag |
| **Gesamt** | **4-6 Tage** |

### Geklärte Fragen

1. **Soll das Backend `my_permission` in Responses liefern?** → ✅ Ja, Option C (inline im Response) wird umgesetzt.
2. **Sollen deaktivierte Elemente einen Tooltip zeigen?** → ✅ Ja, Tooltip mit Hinweis "Keine Berechtigung" bei deaktivierten Elementen.
3. **~~Bulk-Aktionen bei gemischten Berechtigungen?~~** → Entfällt, es gibt keine Bulk-Aktionen im System.
4. **~~Reduced Mode UI für User mit wenigen Berechtigungen?~~** → Entfällt, Standard hide/disable Verhalten ist ausreichend. Kein separater "Reduced Mode" nötig.

---

*Erstellt: 10. Februar 2026*
*Status: Approved — Bereit zur Implementierung*
