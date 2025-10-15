# MASUKA V2 - Quick Reference Card

## 🚀 Current Status: ✅ OPERATIONAL

**Your API URL:** `https://magnitudinous-contrastively-katherin.ngrok-free.dev`

---

## 📝 Most Common Tasks

### Check if Everything is Working
```python
# Run this cell in Colab:
# CELL_TEST_API.py
```
**Expected:** All green checkmarks ✅

---

### Get Your Public URL
```python
from pyngrok import ngrok
tunnels = ngrok.get_tunnels()
print(tunnels[0].public_url)
```

---

### Test Backend Locally
```python
import requests
response = requests.get('http://localhost:8000/health')
print(response.json())
```
**Expected:** `{'status': 'healthy', 'app': 'MASUKA V2', ...}`

---

### Check GPU
```bash
!nvidia-smi
```
**Expected:** Tesla T4 with ~14.7 GB VRAM

---

## 🔧 Troubleshooting Commands

### Backend Not Responding
```python
# 1. Check if running
!ps aux | grep uvicorn

# 2. If not running, restart:
# Run CELL_START_BACKEND.py
```

---

### Run Diagnostics
```python
# Run this cell:
# CELL_DEBUG.py
```
**Look for:** Red ❌ marks indicate problems

---

### Fix Database Warning
```python
# Run this cell:
# CELL_FIX_DATABASE.py
```
**Only needed if:** You want clean diagnostic output

---

### Complete Reset (Nuclear Option)
```bash
# Kill everything
!pkill -f uvicorn
!pkill -f celery
!pkill -f redis
!pkill -f postgres

# Then: Runtime → Restart runtime
# Then: Run CELL1_KERNEL_RESTART.py (twice)
```

---

## 📚 API Endpoints

### Health Check
```bash
GET /health
```

### List Models
```bash
GET /api/models/
```

### Start Training
```bash
POST /api/training/start
Body: {
  "dataset_id": "uuid",
  "config": {...}
}
```

### Generate Image
```bash
POST /api/generate/
Body: {
  "prompt": "your prompt",
  "model_id": "uuid",
  ...
}
```

### API Documentation
```
https://your-url.ngrok-free.dev/docs
```

---

## 🎯 File Quick Guide

| Need To... | Use This File |
|-----------|--------------|
| Test if API works | CELL_TEST_API.py |
| See what's wrong | CELL_DEBUG.py |
| Start backend | CELL_START_BACKEND.py |
| Fix database | CELL_FIX_DATABASE.py |
| Full setup | CELL1_KERNEL_RESTART.py |
| Read docs | COLAB_QUICK_START.md |
| Troubleshoot | TROUBLESHOOTING.md |
| Session summary | SESSION_SUMMARY.md |

---

## ⚡ Critical Timing Info

**After starting backend, wait:**
- 15 seconds → PyTorch loads
- 20 seconds → Diffusers loads
- 30 seconds → **Ready for API calls** ✅

**If you get "connection refused":**
→ You're trying too early, wait 30 seconds!

---

## 🐛 Common Errors & Fixes

### "Connection refused"
**Cause:** Backend still starting
**Fix:** Wait 30 seconds, try again

### "Import Error: torch"
**Cause:** PyTorch circular import
**Fix:** Run CELL1_KERNEL_RESTART.py (twice)

### "Database authentication failed"
**Cause:** PostgreSQL peer auth
**Fix:** Run CELL_FIX_DATABASE.py (optional)

### "No GPU detected"
**Cause:** Runtime not set to GPU
**Fix:** Runtime → Change runtime type → GPU

### "Port already in use"
**Cause:** Old backend still running
**Fix:** `!pkill -f uvicorn` then restart

---

## 💾 Important Variables

```python
# Store these in Colab cells:
API_URL = "https://your-url.ngrok-free.dev"
BACKEND_PROCESS = backend_process  # From startup
CELERY_PROCESS = celery_process    # From startup
```

---

## 🎓 Pro Tips

### Keep Session Alive
```python
import time
while True:
    time.sleep(300)
    print(".", end="", flush=True)
```

### Monitor GPU Usage
```bash
!watch -n 5 nvidia-smi
```

### View Backend Logs
```bash
# If backend stores logs
!tail -f /tmp/backend.log
```

### Quick Health Check
```python
import requests
try:
    r = requests.get('http://localhost:8000/health', timeout=2)
    print("✅ Backend OK" if r.status_code == 200 else "❌ Backend Error")
except:
    print("❌ Backend Down")
```

---

## 📞 Decision Tree

```
Is something wrong?
│
├─ YES → Run CELL_DEBUG.py
│        │
│        ├─ "Backend not responding"
│        │   → Run CELL_START_BACKEND.py
│        │
│        ├─ "Import error"
│        │   → Run CELL1_KERNEL_RESTART.py (twice)
│        │
│        ├─ "Database error"
│        │   → Run CELL_FIX_DATABASE.py
│        │
│        └─ "Unknown error"
│            → Check TROUBLESHOOTING.md
│
└─ NO → You're good! Start training/generating
```

---

## 🎯 Success Checklist

Before you start working, verify:

- [ ] Backend responds to `/health`
- [ ] Ngrok tunnel is active
- [ ] Celery worker is running
- [ ] GPU shows in `nvidia-smi`
- [ ] API docs accessible at `/docs`

**All checked?** → You're ready! 🚀

---

## 📱 Quick Commands Cheat Sheet

```bash
# Status checks
curl localhost:8000/health              # Backend
redis-cli ping                          # Redis
service postgresql status               # Database
nvidia-smi                              # GPU

# Process management
ps aux | grep uvicorn                   # Backend process
ps aux | grep celery                    # Worker process
pkill -f uvicorn                        # Kill backend
pkill -f celery                         # Kill worker

# Logs
journalctl -u postgresql -f             # DB logs
tail -f /var/log/redis/redis.log       # Redis logs
```

---

## 🔗 Important URLs

**Local:**
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

**Public (via ngrok):**
- Backend: `https://magnitudinous-contrastively-katherin.ngrok-free.dev`
- API Docs: `https://magnitudinous-contrastively-katherin.ngrok-free.dev/docs`

---

## ⏱️ Typical Timings

| Operation | Duration | Notes |
|-----------|----------|-------|
| Backend startup | 15-20s | PyTorch + Diffusers loading |
| First API call | 30s | Wait after startup |
| LoRA training | 10-30min | Depends on dataset size |
| Image generation | 10-30s | Per image |
| Model download | 5-10min | First time only |

---

## 🎉 You're Ready!

Everything is set up and working. Use this card as a quick reference whenever you need to:
- ✅ Check status
- 🔧 Troubleshoot issues
- 📝 Find the right file
- ⚡ Run common commands

**Happy training!** 🚀🎨

---

*Quick Ref v1.0 | Updated: 2025-10-15*
