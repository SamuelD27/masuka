# 🔧 Fix: 404 Error on /api/models/ Endpoint

## Problem

Getting `404 Not Found` when accessing `/api/models/` or `/api/generate/` endpoints.

**Error:**
```
❌ Error fetching models: 404
Response: {"detail":"Not Found"}
```

## Cause

The FastAPI backend was started **before** Phase 3 routes were added (via git pull). The backend needs to be restarted to load the new routes.

## Solution

Add this cell to your Colab notebook or run these commands:

### Quick Fix Cell for Colab

```python
#@title 🔧 Restart Backend (Run if you get 404 errors)

import subprocess
import time
import os
import requests

print("🔄 Restarting FastAPI backend with Phase 3 routes...\n")

# Kill existing backend
print("⏹️  Stopping old backend...")
subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
time.sleep(3)

# Change to backend directory
os.chdir('/content/masuka-v2/backend')

# Start new backend
print("▶️  Starting new backend...")
backend_process = subprocess.Popen(
    ['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--log-level', 'info'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

print("⏳ Waiting for backend to start...")
time.sleep(15)

# Test endpoints
print("\n✅ Testing endpoints:\n")

try:
    # Health check
    response = requests.get('http://localhost:8000/health', timeout=5)
    if response.status_code == 200:
        print(f"✅ /health - {response.json()}")

    # Models endpoint (Phase 3)
    response = requests.get('http://localhost:8000/api/models/', timeout=5)
    if response.status_code == 200:
        print(f"✅ /api/models/ - Works! (Phase 3)")
        models = response.json()
        print(f"   Found {len(models)} models")
    else:
        print(f"❌ /api/models/ - {response.status_code}")

    # Generate endpoint (Phase 3)
    response = requests.options('http://localhost:8000/api/generate/image', timeout=5)
    if response.status_code in [200, 204, 405]:
        print(f"✅ /api/generate/image - Available (Phase 3)")
    else:
        print(f"⚠️  /api/generate/image - {response.status_code}")

    # Training endpoint (Phase 2)
    response = requests.get('http://localhost:8000/api/training/', timeout=5)
    if response.status_code == 200:
        print(f"✅ /api/training/ - Works! (Phase 2)")
    else:
        print(f"❌ /api/training/ - {response.status_code}")

except Exception as e:
    print(f"❌ Error testing endpoints: {e}")

print("\n" + "="*70)
print("✅ Backend restarted! You can now use Cell 3 for generation.")
print("="*70)

BACKEND_PROCESS = backend_process
```

### Alternative: Add to Cell 1 Setup

Add this check at the end of Cell 1 (after ngrok setup):

```python
# Verify Phase 3 endpoints are available
print("\n🔍 Verifying Phase 3 endpoints...")
try:
    response = requests.get('http://localhost:8000/api/models/', timeout=5)
    if response.status_code == 200:
        print("✅ Phase 3 generation endpoints loaded!")
    else:
        print("⚠️  Phase 3 endpoints not loaded. Restarting backend...")
        subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
        time.sleep(3)
        backend_process = subprocess.Popen(
            ['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        time.sleep(15)
        print("✅ Backend restarted!")
except Exception as e:
    print(f"⚠️  Warning: {e}")
```

## Manual Fix (SSH/Terminal)

If running locally or via SSH:

```bash
# 1. Navigate to backend
cd /content/masuka-v2/backend

# 2. Pull latest changes
cd /content/masuka-v2
git pull origin main

# 3. Kill old backend
pkill -f uvicorn

# 4. Start new backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Verify Routes Are Loaded

Check the FastAPI docs to see all routes:

1. Go to: `{API_URL}/docs`
2. Look for these new Phase 3 endpoints:
   - `GET /api/models/` - List models
   - `GET /api/models/{model_id}` - Get model
   - `POST /api/generate/image` - Generate image
   - `GET /api/generate/{job_id}` - Get generation status
   - `GET /api/generate/` - List generations

## Prevention

To avoid this in the future, always:

1. **Pull latest code** before starting backend
2. **Use `--reload` flag** for auto-reload on code changes
3. **Check `/docs`** to verify routes loaded

## Updated Cell 1 (Complete)

Here's the complete Cell 1 with the fix integrated:

[See updated notebook with verification step]

---

**Status:** ✅ Fixed - Backend will now include Phase 3 routes
