# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email: **rico.goerlitz@gmail.com**
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Affected service(s) (platform-service, agent-service, frontend-service, SDK)

We will respond within **48 hours** and work with you to resolve the issue before any public disclosure.

## Supported Versions

| Service | Version | Supported |
|---------|---------|-----------|
| Platform Service | 0.x.x | ✅ Latest only |
| Agent Service | 0.x.x | ✅ Latest only |
| Frontend Service | 0.x.x | ✅ Latest only |
| SDK | 0.x.x | ✅ Latest only |

## Security Best Practices

When deploying unified-ui:

- Use HTTPS in production
- Configure proper CORS origins
- Use Azure Key Vault or HashiCorp Vault for secrets (not environment variables in production)
- Enable authentication via Microsoft Entra ID or other supported providers
- Regularly update dependencies
