# Azure Security Platform V2 - Environment Configuration

This document describes the environment variables required for production deployment.

## Quick Setup

1. Copy the example below to `.env.production` in the project root
2. Fill in the values from your Azure resources
3. Never commit `.env.production` to version control

## Required Secrets for GitHub Actions

Set these in your GitHub repository **Settings → Secrets and variables → Actions**:

| Secret Name | Description |
|-------------|-------------|
| `AZURE_CREDENTIALS` | Service principal JSON (see below) |
| `ACR_LOGIN_SERVER` | e.g., `securityplatform.azurecr.io` |
| `ACR_USERNAME` | ACR admin username |
| `ACR_PASSWORD` | ACR admin password |
| `AZURE_CLIENT_ID` | Service principal client ID |
| `AZURE_CLIENT_SECRET` | Service principal secret |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `COSMOS_ENDPOINT` | CosmosDB endpoint URL |
| `COSMOS_KEY` | CosmosDB primary key |
| `REDIS_URL` | Redis connection string |
| `NEXT_PUBLIC_API_URL` | Backend API URL |
| `AZURE_AD_CLIENT_ID` | Frontend Azure AD client ID |
| `AZURE_AD_TENANT_ID` | Azure AD tenant ID for frontend |

## Environment Variables Reference

### Azure Service Principal (Required)

```bash
# Create a service principal with the following Graph API permissions:
# - SecurityEvents.Read.All
# - IdentityRiskyUser.Read.All
# - User.Read.All
# - Reports.Read.All
# - Policy.Read.All
# - DeviceManagementManagedDevices.Read.All

AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

### CosmosDB (Optional)

Falls back to local JSON storage if not configured.

```bash
COSMOS_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_KEY=your-primary-key
COSMOS_DATABASE=security_platform
```

### Redis Cache (Optional)

Falls back to in-memory cache if not configured.

```bash
REDIS_URL=rediss://your-redis.redis.cache.windows.net:6380?password=your-key
```

### Frontend Configuration

```bash
NEXT_PUBLIC_API_URL=https://your-backend.azurewebsites.net/api
NEXT_PUBLIC_USE_MOCK_DATA=false
NEXT_PUBLIC_AZURE_AD_CLIENT_ID=your-frontend-client-id
NEXT_PUBLIC_AZURE_AD_TENANT_ID=your-tenant-id
```

### Backend Configuration

```bash
CORS_ORIGINS=https://your-frontend.azurewebsites.net
LOG_LEVEL=info
JWT_SECRET=your-jwt-secret-min-32-chars
```

## AZURE_CREDENTIALS Format

The `AZURE_CREDENTIALS` GitHub secret should be a JSON object:

```json
{
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret",
  "subscriptionId": "your-subscription-id",
  "tenantId": "your-tenant-id"
}
```

Generate with Azure CLI:
```bash
az ad sp create-for-rbac \
  --name "github-actions-security-platform" \
  --role contributor \
  --scopes /subscriptions/{subscription-id} \
  --sdk-auth
```

## Local Development

For local development, create a `.env` file in both `backend/` and `frontend/` directories:

### backend/.env
```bash
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
# Leave COSMOS_* unset to use local JSON storage
LOG_LEVEL=debug
```

### frontend/.env.local
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_USE_MOCK_DATA=false
```

## Azure Resources Required

| Resource | SKU | Purpose |
|----------|-----|---------|
| App Service (Backend) | B1 or higher | Hosts FastAPI backend |
| App Service (Frontend) | B1 or higher | Hosts Next.js frontend |
| Container Registry | Basic | Docker image storage |
| CosmosDB | Serverless | Historical data storage |
| Redis Cache | Basic C0 | API caching (optional) |

## Permission Verification

After configuration, verify permissions by calling:
```bash
curl https://your-backend.azurewebsites.net/api/health
curl https://your-backend.azurewebsites.net/api/demo/executive/live
```

The `/live` endpoint should return `is_live: true` if Graph API permissions are correct.
