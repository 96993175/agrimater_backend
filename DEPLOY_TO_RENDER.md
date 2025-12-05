# Backend Deployment to Render - Complete Guide

## Step-by-Step Process

### 1. Go to Render Dashboard
Visit: https://dashboard.render.com

### 2. Create New Web Service
- Click **"New +"** button (top right)
- Select **"Web Service"**

### 3. Connect Your Repository
- Click **"Connect GitHub"** (if first time)
- Search for: **`96993175/agrimater-website`**
- Click **"Connect"**

### 4. Configure Service Settings

Fill in these details:

**Basic Settings:**
- **Name:** `agrimater-backend` (or any name you prefer)
- **Root Directory:** `backend`
- **Environment:** `Python 3`
- **Region:** Choose closest to your users
- **Branch:** `main`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python tts_server.py`

**Plan:**
- Select **Free** (or paid for better performance)

### 5. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these **5 variables:**

```
GROQ_API_KEY=your_groq_api_key_here

GROQ_MODEL=llama-3.1-8b-instant

MONGODB_URI=your_mongodb_connection_string

SENDGRID_API_KEY=your_sendgrid_api_key_here

SENDGRID_FROM=no-reply@agrimater.com
```

**Note:** Don't add `PORT` - Render sets this automatically

### 6. Deploy

- Click **"Create Web Service"**
- Render will:
  1. Clone your repo
  2. Install dependencies (`flask`, `flask-cors`, `edge-tts`)
  3. Start the server
  4. Give you a URL like: `https://agrimater-backend.onrender.com`

### 7. Wait for Deployment

Watch the logs. You should see:
```
==> Installing dependencies from requirements.txt
==> Starting service with 'python tts_server.py'
==> TTS Server running on port 10000
```

### 8. Test Your Backend

Once **"Live"** appears, test it:

```bash
# Health check
curl https://your-render-url.onrender.com/health

# Should return:
{"status":"healthy","service":"TTS Server"}
```

### 9. Copy Your Backend URL

Example: `https://agrimater-backend.onrender.com`

You'll need this for Vercel frontend deployment!

---

## Important Notes

⚠️ **Free Tier Limitations:**
- Sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Use paid plan for production ($7/month)

✅ **What This Backend Provides:**
- TTS (Text-to-Speech) with Microsoft Neural voices
- Groq AI chat integration
- MongoDB database access
- SendGrid email service

✅ **CORS Enabled:**
- Backend accepts requests from any origin (configured in `tts_server.py`)

---

## Next Step: Deploy Frontend to Vercel

After backend is live, deploy frontend with:
- `NEXT_PUBLIC_TTS_SERVER_URL` = Your Render URL
- All other environment variables (Groq, MongoDB, SendGrid)
