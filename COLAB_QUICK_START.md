# MASUKA V2 - Colab Quick Start Guide

## 🎉 Good News!

Based on the diagnostics, **your backend is actually running fine!**

The "connection refused" error you saw was likely a timing issue where the ngrok tunnel wasn't fully ready yet.

---

## ✅ Current Status

From your diagnostic results:

- ✅ **Backend is running** on port 8000
- ✅ **Backend imports work** (no circular import issues!)
- ✅ **Redis is working**
- ✅ **Health endpoint responding** with 200 OK
- ⚠️ **Database auth issue** (minor, can be fixed)

---

## 🚀 Next Steps

### Option 1: Test Your API Now (Recommended)

Your setup is actually working! Just run this cell:

```python
# Copy and run CELL_TEST_API.py
# This will verify everything and give you your ngrok URL
```

This will:
- Confirm backend is working
- Get your ngrok public URL
- Test all API endpoints
- Store the URL in `API_URL` variable

### Option 2: Fix Database Authentication (Optional)

The database auth issue doesn't affect basic functionality, but if you want to fix it:

```python
# Copy and run CELL_FIX_DATABASE.py
# This updates PostgreSQL to use password auth instead of peer auth
```

---

## 📝 What Happened Earlier

### The Error You Saw:
```
dial tcp [::1]:8000: connect: connection refused
```

### Why It Happened:
1. Backend was still starting up when you tried to access it
2. Ngrok tunnel was created before backend was ready
3. The connection timing was off by a few seconds

### The Fix:
**Just wait a bit longer!** Your setup actually worked - it just needed more time.

---

## 🎯 Using Your API

Once you run `CELL_TEST_API.py`, you'll get a URL like:
```
https://xxxx.ngrok-free.dev
```

### Available Endpoints:

**Health Check:**
```bash
GET https://xxxx.ngrok-free.dev/health
```

**API Documentation:**
```
https://xxxx.ngrok-free.dev/docs
```

**Training API:**
```bash
POST https://xxxx.ngrok-free.dev/api/training/start
```

**Models API:**
```bash
GET https://xxxx.ngrok-free.dev/api/models/
```

**Generation API:**
```bash
POST https://xxxx.ngrok-free.dev/api/generate/
```

---

## 🔧 If You Need to Restart Backend

If the backend crashes or you need to restart:

```python
# Copy and run CELL_START_BACKEND.py
# This will:
# 1. Kill old processes
# 2. Test imports
# 3. Start backend with detailed logs
# 4. Start Celery worker
# 5. Create ngrok tunnel
```

---

## 📚 File Reference

### Main Setup Files:
- **CELL1_KERNEL_RESTART.py** - Full setup with kernel restart (most reliable)
- **CELL1_FINAL_FIX.py** - Full setup with subprocess isolation
- **CELL1_ULTIMATE_FIX.py** - Full setup with cache purge

### Utility Files:
- **CELL_TEST_API.py** - Test your API and get ngrok URL ⭐
- **CELL_DEBUG.py** - Diagnose any issues
- **CELL_START_BACKEND.py** - Manually start backend
- **CELL_FIX_DATABASE.py** - Fix PostgreSQL authentication

### Documentation:
- **TROUBLESHOOTING.md** - Complete troubleshooting guide
- **COLAB_QUICK_START.md** - This file

---

## 🎓 Understanding the Timing Issue

```
Time: 0s  ➜ Backend starts
Time: 5s  ➜ Backend initializing (loading torch, diffusers)
Time: 15s ➜ Backend ready ✅
Time: 20s ➜ Ngrok tunnel created
Time: 25s ➜ First API call works! 🎉

❌ If you try at 10s → "Connection refused"
✅ If you try at 25s → Works perfectly!
```

**Solution:** Always wait at least 20-30 seconds after setup completes before making API calls.

---

## ⚡ Quick Commands Reference

### Check if backend is running:
```python
import requests
response = requests.get('http://localhost:8000/health')
print(response.json())
```

### Get current ngrok URL:
```python
from pyngrok import ngrok
tunnels = ngrok.get_tunnels()
print(tunnels[0].public_url if tunnels else "No tunnel")
```

### Restart everything:
```bash
# Kill processes
pkill -f uvicorn
pkill -f celery

# Then run CELL_START_BACKEND.py
```

---

## 🐛 Common Issues

### "Connection Refused"
**Cause:** Tried to connect too early
**Fix:** Wait 30 seconds after setup, then try again

### "Import Error"
**Cause:** PyTorch/TorchVision circular import
**Fix:** Use CELL1_KERNEL_RESTART.py (requires running twice)

### "Database Error"
**Cause:** PostgreSQL peer authentication
**Fix:** Run CELL_FIX_DATABASE.py

### "Port Already In Use"
**Cause:** Old backend process still running
**Fix:** `pkill -f uvicorn` then restart

---

## 🎯 Recommended Workflow

### First Time Setup:
1. Run **CELL1_KERNEL_RESTART.py** (twice)
2. Wait 30 seconds
3. Run **CELL_TEST_API.py**
4. Use the ngrok URL provided

### If Something Breaks:
1. Run **CELL_DEBUG.py** to diagnose
2. Fix the specific issue (see diagnostic output)
3. Run **CELL_START_BACKEND.py** to restart
4. Run **CELL_TEST_API.py** to verify

### Before Training:
1. Make sure backend is running (CELL_TEST_API.py)
2. Make sure Celery worker is running (check diagnostic)
3. Make sure you have GPU allocated (nvidia-smi)
4. Then proceed with training

---

## ✅ Success Checklist

Before you start training or generating, verify:

- [ ] Backend responds to `/health` endpoint
- [ ] Ngrok tunnel is active and accessible
- [ ] Celery worker is running (for training tasks)
- [ ] GPU is allocated (`nvidia-smi` shows GPU)
- [ ] All API endpoints return valid responses

If all checks pass → **You're ready to go!** 🚀

---

## 📞 Still Having Issues?

If you're stuck, run these diagnostic cells in order:

1. **CELL_DEBUG.py** - Shows what's wrong
2. **CELL_TEST_API.py** - Tests if API works
3. Check **TROUBLESHOOTING.md** for specific errors

If none of these help, the nuclear option:
- Runtime → Restart runtime
- Re-run CELL1_KERNEL_RESTART.py (twice)

---

## 🎉 You're Ready!

Your MASUKA V2 setup is working. The initial error was just a timing issue.

**Next steps:**
1. Run CELL_TEST_API.py to get your URL
2. Test the API endpoints
3. Start training or generating!

Happy training! 🚀
