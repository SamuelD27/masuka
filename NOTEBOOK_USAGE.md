# 📓 MASUKA V2 - Colab Notebook Usage Guide

## 🎯 The Notebook: **MASUKA_V2_COLAB.ipynb**

This is your **complete, ready-to-use Google Colab notebook** in proper `.ipynb` format.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Upload to Google Colab
1. Go to https://colab.research.google.com
2. Click **File → Upload notebook**
3. Select `MASUKA_V2_COLAB.ipynb`

**OR**

1. Open Google Drive
2. Upload `MASUKA_V2_COLAB.ipynb` to your Drive
3. Double-click to open in Colab

### Step 2: Set Runtime to GPU
1. Click **Runtime → Change runtime type**
2. Hardware accelerator: **GPU**
3. GPU type: **T4** (recommended)
4. Click **Save**

### Step 3: Run the Notebook
1. Run **Cell 1** (Setup) - Wait ~10 minutes
2. Run **Cell 2** (Test) - Verify everything works
3. Start using your API! 🎉

---

## 📋 What's in the Notebook

### 🎨 Header Section (Markdown)
- Notebook title and description
- Feature list
- Quick instructions

### 📦 Cell 1: Complete Setup (10 min)
**What it does:**
- ✅ Checks GPU
- ✅ Clones repository
- ✅ Installs PyTorch 2.4.1 + TorchVision 0.19.1
- ✅ Installs all dependencies
- ✅ Sets up PostgreSQL (with md5 auth)
- ✅ Sets up Redis
- ✅ Starts FastAPI backend
- ✅ Starts Celery worker
- ✅ Creates ngrok tunnel

**Output:** Public API URL

### 🧪 Cell 2: Test API (30 sec)
**What it does:**
- Tests all API endpoints
- Verifies services running
- Checks GPU
- Shows summary

**Output:** All ✅ checks

### 🔧 Cell 3: Utility Commands (reference)
**What it does:**
- Shows useful commands
- Restart services
- Check logs
- View status

**Output:** Command reference

### 🔍 Cell 4: Diagnostic Tool (troubleshooting)
**What it does:**
- Comprehensive health check
- Identifies problems
- Shows system status

**Output:** Diagnostic report

---

## ✅ Expected Output

### After Cell 1:
```
======================================================================
🎉 MASUKA V2 Setup Complete!
======================================================================

📡 Your Public API URL:
   https://xxxx-xxxx-xxxx.ngrok-free.dev

📚 Important Links:
   • API Documentation: https://xxxx.ngrok-free.dev/docs
   • Health Check: https://xxxx.ngrok-free.dev/health
   ...

✅ Services Running:
   • PostgreSQL (md5 auth configured)
   • Redis
   • FastAPI Backend
   • Celery Worker (GPU: Tesla T4)
   • SimpleTuner

✅ API_URL stored: https://xxxx.ngrok-free.dev
```

### After Cell 2:
```
🧪 MASUKA V2 - API Testing
======================================================================

1️⃣ Testing Health Endpoint...
  ✅ Status: healthy
  ✅ App: MASUKA V2 v2.0.0
  ✅ Mode: single-user

2️⃣ Testing Models API...
  ✅ Models API working
  ✅ Current models: 0

... (all tests pass)

📊 Test Summary
======================================================================
✅ Your MASUKA V2 API is ready to use!
```

---

## 🎯 Key Features

### 1. Form-Based Cells
Each cell has a title and description using `#@title` and `#@markdown`:
```python
#@title 🚀 CELL 1: Complete Setup (Run Once)
#@markdown This cell sets up everything...
```

This creates a nice form UI in Colab with:
- Collapsible code sections
- Clear titles and descriptions
- Easy-to-use interface

### 2. All Fixes Included
- ✅ PyTorch circular import fix
- ✅ PostgreSQL md5 auth configuration
- ✅ Proper timing (waits for backend)
- ✅ Verification in subprocess

### 3. Error Handling
- Clear error messages
- Helpful suggestions
- Exit codes on failure

### 4. Progress Indicators
- Step-by-step progress
- Emoji indicators
- Clear status messages

---

## 🔧 Customization

### Change Ngrok Token
Edit Cell 1, find:
```python
ngrok.set_auth_token("your-token-here")
```

### Change Storage Configuration
Edit Cell 1, find:
```python
env_content = """
...
# Storage (AWS S3/Cloudflare R2)
S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
...
"""
```

### Change Database Password
Edit Cell 1, find:
```python
"CREATE USER masuka WITH PASSWORD 'password123';"
```
And:
```python
DATABASE_URL=postgresql://masuka:password123@localhost:5432/masuka
```

---

## 📱 Mobile Usage

The notebook works on mobile browsers too!

1. Open Colab on mobile: https://colab.research.google.com
2. Upload or open the notebook
3. Tap the play button on each cell
4. Wait for completion

**Note:** Setup might be slower on mobile, and you can't use Colab GPU on the mobile app. Use desktop for best experience.

---

## 💾 Saving Your Work

### Save the Notebook
- **File → Save** - Saves to Google Drive
- **File → Save a copy in Drive** - Creates a backup

### Save API URL
After Cell 1 completes, save the URL:
```python
# In a new cell:
with open('/content/api_url.txt', 'w') as f:
    f.write(API_URL)

# Later, retrieve it:
with open('/content/api_url.txt', 'r') as f:
    API_URL = f.read().strip()
```

### Save Models
Models are stored in:
- `/content/models/` (temporary)
- Configure S3/R2 for permanent storage

---

## 🐛 Troubleshooting

### Problem: Cell 1 fails during PyTorch install

**Solution:**
1. Check internet connection
2. Runtime → Restart runtime
3. Run Cell 1 again

### Problem: "No GPU detected"

**Solution:**
1. Runtime → Change runtime type
2. Select **GPU**
3. Runtime → Restart runtime
4. Run Cell 1 again

### Problem: Backend not responding

**Solution:**
1. Run Cell 4 (Diagnostics)
2. Check which service failed
3. Restart failed service using Cell 3 commands

### Problem: Ngrok connection refused

**Solution:**
1. Wait 30 seconds after Cell 1 completes
2. Backend might still be initializing
3. Run Cell 2 to test

### Problem: Session disconnected

**Solution:**
1. Colab disconnects after ~90 min idle
2. Keep a cell running with:
```python
import time
while True:
    time.sleep(300)
    print(".", end="", flush=True)
```

---

## 📊 Resource Usage

**Cell 1 (Setup):**
- Time: ~10 minutes
- Disk: ~5 GB downloaded
- RAM: ~2 GB during install

**Runtime (After Setup):**
- Backend: ~1.5 GB RAM
- Celery: ~1 GB RAM
- GPU: Used during training/generation
- Total: ~3-4 GB RAM baseline

**Training:**
- GPU: ~12-14 GB VRAM (full)
- Time: 10-30 min per LoRA
- Disk: ~2-5 GB per model

---

## 🎓 Best Practices

### 1. Run in Order
Always run cells in order: 1 → 2 → 3 → 4

### 2. Wait for Completion
Don't interrupt Cell 1 - let it finish completely

### 3. Check Output
Read the output after each cell - look for ❌ errors

### 4. Save URL
Copy your ngrok URL and save it somewhere safe

### 5. Keep Session Alive
Use a keepalive cell if training for >90 minutes

### 6. Monitor GPU
Run `!nvidia-smi` periodically to check GPU usage

### 7. Clean Up
Remove old models and data to free disk space:
```python
!rm -rf /content/models/old_model_*
```

---

## 🔗 Quick Links

### Colab Resources:
- Colab Welcome: https://colab.research.google.com/notebooks/intro.ipynb
- Colab FAQ: https://research.google.com/colaboratory/faq.html
- GPU Specs: https://cloud.google.com/compute/docs/gpus

### MASUKA V2:
- GitHub: https://github.com/SamuelD27/masuka
- SimpleTuner: https://github.com/bghira/SimpleTuner
- Flux Model: https://huggingface.co/black-forest-labs/FLUX.1-dev

---

## ✅ Success Checklist

Before you start training:

- [ ] Uploaded notebook to Colab
- [ ] Set runtime to GPU (T4)
- [ ] Ran Cell 1 successfully
- [ ] Got public API URL
- [ ] Ran Cell 2 - all tests passed
- [ ] Bookmarked API URL
- [ ] Tested `/docs` endpoint
- [ ] Ready to upload training data

**All checked?** → Start training! 🚀

---

## 🎉 You're Ready!

You now have:
- ✅ A proper Jupyter notebook (.ipynb)
- ✅ Ready to upload to Colab
- ✅ All fixes applied
- ✅ Complete documentation

**Just upload and run!** 🎨

---

*Notebook Version: 1.0*
*Format: Jupyter Notebook (.ipynb)*
*Last Updated: 2025-10-15*
*Tested: Google Colab with Tesla T4 GPU*
