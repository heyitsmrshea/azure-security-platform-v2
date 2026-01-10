# Azure App Registration Setup Guide

**Time Required:** ~15 minutes  
**Prerequisites:** Azure AD Global Administrator or Application Administrator role

---

## Step 1: Create the App Registration

1. Go to **[Azure Portal](https://portal.azure.com)**
2. Search for **"App registrations"** in the top search bar
3. Click **"+ New registration"**

Fill in:
| Field | Value |
|-------|-------|
| **Name** | `Security Assessment Platform` (or your preferred name) |
| **Supported account types** | Select **"Accounts in any organizational directory (Any Azure AD directory - Multitenant)"** |
| **Redirect URI** | Leave blank for now (or add `http://localhost:8000/callback` for testing) |

4. Click **Register**

---

## Step 2: Note Your App IDs

After registration, you'll see the **Overview** page. Copy these values:

```
Application (client) ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  ← This is your CLIENT_ID
Directory (tenant) ID:   xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  ← This is YOUR tenant (not customer's)
```

---

## Step 3: Create a Client Secret

1. In your app registration, click **"Certificates & secrets"** (left menu)
2. Click **"+ New client secret"**
3. Add a description: `Assessment Platform Secret`
4. Choose expiration: **24 months** (recommended)
5. Click **Add**

⚠️ **IMPORTANT:** Copy the secret **Value** immediately - you won't see it again!

```
Secret Value: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  ← This is your CLIENT_SECRET
```

---

## Step 4: Add API Permissions

1. Click **"API permissions"** (left menu)
2. Click **"+ Add a permission"**

### Microsoft Graph Permissions (Application type)

For each permission below:
- Click **"Microsoft Graph"**
- Click **"Application permissions"** (NOT Delegated)
- Search for the permission name
- Check the box
- Click **"Add permissions"**

| Permission | Why We Need It |
|------------|----------------|
| `SecurityEvents.Read.All` | Read security alerts |
| `IdentityRiskyUser.Read.All` | Read risky user data |
| `Policy.Read.All` | Read Conditional Access policies |
| `RoleManagement.Read.Directory` | Read admin role assignments |
| `DeviceManagementManagedDevices.Read.All` | Read Intune device compliance |
| `Reports.Read.All` | Read MFA registration status |
| `User.Read.All` | Read user profiles |
| `AuditLog.Read.All` | Read audit logs |
| `Directory.Read.All` | Read directory data |

---

## Step 5: Grant Admin Consent (for YOUR tenant)

After adding all permissions:

1. Click **"Grant admin consent for [Your Organization]"**
2. Click **Yes** to confirm

You should see green checkmarks ✅ next to all permissions.

---

## Step 6: Save Your Credentials

Create a secure note with:

```
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Never commit these to git!**

---

## How Customer Consent Works

When you want to assess a customer's tenant:

### 1. Generate a Consent URL

```bash
# The customer's Global Admin clicks this URL
https://login.microsoftonline.com/CUSTOMER_TENANT_ID/adminconsent?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8000/callback
```

Or use the built-in helper:

```python
from backend.assessment.consent import generate_consent_url

url = generate_consent_url(
    client_id="your-client-id",
    redirect_uri="http://localhost:8000/callback",
    tenant_id="customer-tenant-id"  # Optional - use 'common' for any tenant
)
print(url)
```

### 2. Customer Approves

- Customer's Global Admin clicks the link
- Microsoft shows permission dialog
- Admin clicks **Accept**
- Your app now has read-only access to their tenant

### 3. Run Assessment

```bash
python3 run_assessment.py \
  --tenant-id "customer-tenant-id" \
  --customer-name "Customer Corp" \
  --client-id "your-client-id" \
  --client-secret "your-secret" \
  --brand polaris
```

---

## Quick Reference: Azure Portal Navigation

```
Azure Portal
├── App registrations
│   ├── + New registration          ← Create app
│   └── [Your App]
│       ├── Overview                ← Get Client ID
│       ├── Certificates & secrets  ← Create secret
│       ├── API permissions         ← Add permissions
│       └── Authentication          ← Configure redirect URIs
```

---

## Troubleshooting

### "AADSTS65001: The user or administrator has not consented"
→ Customer hasn't clicked the consent URL yet

### "AADSTS700016: Application not found"
→ Wrong client ID or app not set to multi-tenant

### "Insufficient privileges"
→ Missing API permission - check Step 4

### "Invalid client secret"
→ Secret expired or copied incorrectly

---

## Security Best Practices

1. **Rotate secrets** every 12-24 months
2. **Use environment variables** - never hardcode secrets
3. **Limit who has access** to the app credentials
4. **Monitor consent** - track which tenants have authorized your app
5. **Revoke access** when customer engagement ends

---

## Test Your Setup

```bash
cd ~/Desktop/CURSOR/azure_security_platform_v2

# Set credentials
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-secret"

# Dry run (validates config without connecting)
python3 run_assessment.py \
  --tenant-id "your-own-tenant-id" \
  --customer-name "Test" \
  --brand operationmos \
  --dry-run
```
