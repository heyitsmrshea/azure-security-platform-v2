# Deployment Guide - Azure Security Platform V2

Deploy your dashboard with permanent URLs using **Vercel** (frontend) + **Render** (backend).

Both services have generous free tiers and require no credit card.

---

## Step 1: Push to GitHub

First, ensure your code is pushed to a GitHub repository:

```bash
cd /Users/andrewshea/Desktop/CURSOR/azure_security_platform_v2
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

---

## Step 2: Deploy Backend to Render

### 2.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended for easy repo access)

### 2.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `azure-security-api` |
| **Root Directory** | `backend` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT` |

### 2.3 Add Environment Variables
In Render dashboard, go to **Environment** tab and add:

| Key | Value | Notes |
|-----|-------|-------|
| `AZURE_CLIENT_ID` | `your-client-id` | From Azure App Registration |
| `AZURE_CLIENT_SECRET` | `your-client-secret` | From Azure App Registration |
| `AZURE_TENANT_ID` | `your-tenant-id` | Your Azure AD Tenant ID |
| `PYTHON_VERSION` | `3.11` | Required |

### 2.4 Deploy
Click **"Create Web Service"** and wait for deployment (~3-5 minutes).

You'll get a URL like: `https://azure-security-api-xxxx.onrender.com`

**Copy this URL** - you'll need it for the frontend.

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub

### 3.2 Import Project
1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repository
3. Configure the project:

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Next.js` |
| **Root Directory** | `frontend` |

### 3.3 Add Environment Variables
Before deploying, add these environment variables:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://azure-security-api-xxxx.onrender.com/api` |

⚠️ **Important**: Replace `xxxx` with your actual Render URL, and add `/api` at the end!

### 3.4 Deploy
Click **"Deploy"** and wait (~2-3 minutes).

You'll get a URL like: `https://azure-security-platform-xxxx.vercel.app`

---

## Step 4: Configure CORS (Important!)

After both are deployed, update the backend to allow requests from your Vercel domain.

### Option A: Update via Render Environment Variables
Add this environment variable in Render:

| Key | Value |
|-----|-------|
| `CORS_ORIGINS` | `https://azure-security-platform-xxxx.vercel.app` |

### Option B: Update Code
Edit `backend/api/main.py` and add your Vercel URL to `CORS_ORIGINS`:

```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://azure-security-platform-xxxx.vercel.app",  # Add your Vercel URL
]
```

Then push and Render will auto-redeploy.

---

## Your URLs

After deployment, you'll have:

| Service | URL |
|---------|-----|
| **Dashboard** | `https://azure-security-platform-xxxx.vercel.app` |
| **API** | `https://azure-security-api-xxxx.onrender.com` |
| **Health Check** | `https://azure-security-api-xxxx.onrender.com/health` |

---

## Sharing the Link

Your dashboard URL is "obscure" by default:
- `https://azure-security-platform-a1b2c3d4.vercel.app`

To make it even more private:
1. In Vercel, go to **Settings** → **Domains**
2. Disable the default `.vercel.app` domain
3. Add a custom domain if desired

---

## Troubleshooting

### "Failed to load dashboard data"
- Check that `NEXT_PUBLIC_API_URL` includes `/api` at the end
- Verify CORS is configured for your Vercel domain
- Check Render logs for backend errors

### Backend not connecting to Azure
- Verify all three Azure credentials are set in Render
- Check Render logs: `Logs` tab in your service

### Slow first load
- Render free tier "sleeps" after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Upgrade to paid tier ($7/month) to avoid this

---

## Cost Summary

| Service | Free Tier | Paid Option |
|---------|-----------|-------------|
| **Vercel** | Unlimited for hobby | $20/month for team features |
| **Render** | 750 hours/month (sleeps after inactivity) | $7/month for always-on |

**Total: $0/month** for basic usage, $7-27/month for better performance.
