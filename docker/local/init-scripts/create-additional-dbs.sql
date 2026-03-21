-- ============================================================
-- Additional databases for unified-ui local development
-- Executed automatically on first PostgreSQL start
-- ============================================================

-- Zitadel OIDC Identity Provider
CREATE DATABASE zitadel;

-- N8N Workflow Engine
SELECT 'CREATE DATABASE n8n'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'n8n')\gexec
