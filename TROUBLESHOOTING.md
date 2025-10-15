# MASUKA V2 - Colab Troubleshooting Guide

## Current Issue: Backend Not Starting (Connection Refused)

### Error Message
```
dial tcp [::1]:8000: connect: connection refused
```

This means the FastAPI backend failed to start on port 8000.

---

## 🔧 Quick Fix Steps

### Option 1: Run the Debug Cell
```python
# Copy and run CELL_DEBUG.py in a new cell
# This will diagnose the exact issue
```

### Option 2: Manual Backend Start
```python
# Copy and run CELL_START_BACKEND.py in a new cell
# This will attempt to start the backend manually with detailed logs
```

---

## 🔍 Common Issues & Solutions

### 1. PyTorch/TorchVision Import Errors

**Symptoms:**
- `AttributeError: partially initialized module 'torchvision' has no attribute 'extension'`
- `RuntimeError: operator torchvision::nms does not exist`

**Solution:**
Use the kernel restart approach:
```python
# Use CELL1_KERNEL_RESTART.py
# This requires running the cell TWICE (it auto-restarts)
```

**Why this works:** Kernel restart clears all cached Python modules, preventing circular imports.

---

### 2. Backend Import Fails

**Symptoms:**
- Backend process starts but immediately crashes
- `ImportError` or `ModuleNotFoundError` in logs

**Solution:**
```python
# Test imports manually
import sys
sys.path.insert(0, '/content/masuka-v2/backend')

# Try importing
from app.main import app  # This will show the exact error
```

Common missing packages:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary redis celery
pip install diffusers transformers accelerate
```

---

### 3. Database Connection Errors

**Symptoms:**
- Backend starts but health check fails
- "could not connect to server" errors

**Solution:**
```bash
# Check PostgreSQL status
sudo service postgresql status

# Restart PostgreSQL
sudo service postgresql restart

# Test connection
PGPASSWORD=password123 psql -U masuka -d masuka -c "SELECT 1;"
```

---

### 4. CUDA/GPU Not Available

**Symptoms:**
- `torch.cuda.is_available()` returns `False`
- Training fails with "No GPU found"

**Solution:**
1. Go to: **Runtime → Change runtime type → GPU (T4)**
2. Restart runtime
3. Re-run setup cells

---

### 5. Ngrok Tunnel Shows HTML Error Page

**Symptoms:**
- API calls return HTML instead of JSON
- "Connection refused" in ngrok error page

**Solution:**
This means the backend isn't running at all. Follow these steps:

1. Run **CELL_DEBUG.py** to see what failed
2. Check if port 8000 is listening:
   ```bash
   lsof -i :8000
   ```
3. Manually start backend:
   ```bash
   cd /content/masuka-v2/backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
4. Watch the logs for errors

---

## 📝 Step-by-Step Recovery Process

### If CELL1 Failed:

1. **Don't re-run CELL1 immediately!** This can make things worse.

2. **Run diagnostics first:**
   ```python
   # Run CELL_DEBUG.py
   ```

3. **Check what's actually wrong:**
   - Import errors? → Use CELL1_KERNEL_RESTART.py
   - Database errors? → Check PostgreSQL
   - Port already in use? → Kill existing processes

4. **Start backend manually:**
   ```python
   # Run CELL_START_BACKEND.py
   ```

5. **If all else fails:**
   - Runtime → Restart runtime
   - Start fresh with CELL1_KERNEL_RESTART.py

---

## 🎯 Best Practices

### To Avoid Issues:

1. **Use CELL1_KERNEL_RESTART.py** instead of other versions
   - Most reliable
   - Requires running twice
   - Completely avoids import cache issues

2. **Don't interrupt cell execution**
   - Let each step complete fully
   - Don't stop cells mid-execution

3. **Check GPU first**
   ```bash
   nvidia-smi
   ```
   Make sure you have a GPU allocated!

4. **One cell at a time**
   - Wait for CELL1 to complete before CELL2
   - Don't run multiple setup cells in parallel

---

## 🆘 Emergency Recovery

If everything is broken and you can't figure it out:

```python
# Nuclear option: Complete reset
import subprocess
import time

# Kill everything
subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
subprocess.run(['pkill', '-f', 'celery'], capture_output=True)
subprocess.run(['pkill', '-f', 'redis'], capture_output=True)
subprocess.run(['pkill', '-f', 'postgres'], capture_output=True)

# Remove repository
subprocess.run(['rm', '-rf', '/content/masuka-v2'], capture_output=True)
subprocess.run(['rm', '-rf', '/content/SimpleTuner'], capture_output=True)

# Clean pip
subprocess.run(['pip', 'cache', 'purge'], capture_output=True)

print("✅ Cleanup complete!")
print("Now: Runtime → Restart runtime")
print("Then: Run CELL1_KERNEL_RESTART.py")
```

---

## 📞 Getting Help

If you're still stuck, provide this info:

1. **Error message** from CELL_DEBUG.py
2. **GPU type** from `nvidia-smi`
3. **Python version** from `python --version`
4. **Which cell failed** (CELL1, CELL2, etc.)
5. **Last successful step** before failure

---

## 🎓 Understanding the Architecture

```
┌─────────────────────────────────────────┐
│  Colab Notebook (Your Browser)          │
│  ├─ CELL1: Setup                        │
│  ├─ CELL2: Training                     │
│  └─ CELL3: Generation                   │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Colab VM (Google's Server)             │
│  ├─ PostgreSQL (Database)               │
│  ├─ Redis (Queue)                       │
│  ├─ FastAPI Backend (:8000)             │
│  ├─ Celery Worker (GPU tasks)           │
│  └─ SimpleTuner (LoRA training)         │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Ngrok Tunnel (Public Internet)         │
│  └─ https://xxxx.ngrok-free.dev         │
└─────────────────────────────────────────┘
```

**When you see "connection refused":**
- Ngrok tunnel is working ✅
- But FastAPI backend isn't running ❌
- Need to fix backend startup

---

## ✅ Verification Checklist

After running setup, verify:

- [ ] `nvidia-smi` shows GPU
- [ ] `lsof -i :8000` shows uvicorn
- [ ] `redis-cli ping` returns PONG
- [ ] `psql -U masuka -d masuka` connects
- [ ] `curl http://localhost:8000/health` returns JSON
- [ ] `curl <ngrok-url>/health` returns JSON

If all checks pass → You're good! 🎉

---

## 📚 File Reference

- **CELL1_KERNEL_RESTART.py** - Most reliable setup (run twice)
- **CELL1_FINAL_FIX.py** - Subprocess isolation method
- **CELL1_ULTIMATE_FIX.py** - Single-run with pip cache purge
- **CELL_DEBUG.py** - Diagnostic tool
- **CELL_START_BACKEND.py** - Manual backend start

**Recommended:** Start with CELL1_KERNEL_RESTART.py
