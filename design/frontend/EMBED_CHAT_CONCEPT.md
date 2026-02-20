# Embed Chat Concept

## Overview

Applications can be embedded as chat widgets in external websites via iframe. The embed system uses the existing MSAL authentication — no separate embed-token system is needed.

## URL Format

```
https://{host}/embed/chat/{applicationId}?tenantId={tenantId}&theme=light|dark&lang=en-US&ctx_key=value
```

### Parameters

| Parameter | Source | Required | Description |
|-----------|--------|----------|-------------|
| `applicationId` | URL path | Yes | Application ID to chat with |
| `tenantId` | Query | Yes | Tenant ID the application belongs to |
| `theme` | Query | No | Force `light` or `dark` mode (default: auto) |
| `lang` | Query | No | UI language override |
| `ctx_*` | Query | No | Context data passed to the agent (prefix `ctx_` is stripped) |

## Authentication

The embed page is **not** behind `ProtectedRoute`. Authentication is handled inside the page:

1. **MSAL session exists** — If the user is already logged in (sessionStorage has tokens), the embed page works immediately.
2. **MSAL popup login** — If not authenticated, a login button is shown. Clicking it triggers `acquireTokenPopup()`, which opens a popup window for Azure AD login.

### Same-origin vs Cross-origin

- **Same-origin iframe** (e.g., `app.example.com` embedding `app.example.com/embed/chat/...`): MSAL sessionStorage tokens are shared. Auth is seamless.
- **Cross-origin iframe** (e.g., `customer.com` embedding `app.example.com/embed/chat/...`): Third-party cookie restrictions may block silent token acquisition. The popup fallback handles this case.

## Allowed Origins

Each application has an `embed_allowed_origins` field — a semicolon-separated string of allowed origins (e.g., `https://example.com;https://app.example.com`).

- Stored as a single `VARCHAR(2000)` column on the `applications` table.
- Managed via the Create/Edit Application dialogs (tag-like input using Mantine `TagsInput`).
- Used by the host page to configure CSP `frame-ancestors` headers.
- In the frontend, origins are displayed as chips and stored as a `;`-separated string in the API.

## Architecture

```
Host Page (customer.com)
  └── <iframe src="https://app.example.com/embed/chat/{appId}?tenantId=...">
        └── EmbedChatPage
              ├── MSAL Auth (popup if needed)
              ├── IdentityContext (apiClient, tenant selection)
              ├── useChat (with onNavigate override to suppress routing)
              └── ChatView (full-viewport, no MainLayout/sidebar)
```

### Key Design Decisions

1. **No embed token system** — Only MSAL-authenticated users can use the embed chat. This avoids complexity of managing separate token lifecycles.
2. **No MainLayout** — The embed page renders only `ChatView` in a full-viewport container.
3. **No conversation sidebar** — Each embed instance creates its own conversation. No conversation switching.
4. **`onNavigate` override on `useChat`** — The hook normally navigates to `/conversations/:id` after creating a conversation. In embed mode, this is replaced with a local state update.
5. **No tracing** — Trace sidebar is not shown in embed mode.

## Files Modified

### Backend (platform-service)
- `models.py` — Added `embed_allowed_origins` column to `Application`
- `schema/requests/applications.py` — Added `embed_allowed_origins` to Create/Update schemas
- `schema/responses/applications.py` — Added `embed_allowed_origins` to response schema
- `handlers/applications.py` — Handle `embed_allowed_origins` in create, update, and `_model_to_response`
- `alembic/versions/h2b3c4d5e6f7_...py` — Migration to add the column

### Frontend (frontend-service)
- `api/types.ts` — Added `embed_allowed_origins` to Application interfaces
- `components/dialogs/CreateApplicationDialog.tsx` — Added origins `TagsInput` field
- `components/dialogs/EditApplicationDialog/EditApplicationDialog.tsx` — Added origins `TagsInput` field with `;`-split/join
- `pages/EmbedChatPage/EmbedChatPage.tsx` — Full rewrite with ChatView + MSAL auth
- `pages/EmbedChatPage/EmbedChatPage.module.css` — Embed page styles
- `hooks/chat/useChat.ts` — Added optional `onNavigate` param
- `i18n/locales/en-US/common.json` — Added embed-related i18n keys

## Embedding Example

```html
<iframe
  src="https://app.example.com/embed/chat/abc-123?tenantId=tenant-456&theme=dark&ctx_userId=user-789"
  style="width: 100%; height: 600px; border: none;"
  allow="clipboard-write"
></iframe>
```
