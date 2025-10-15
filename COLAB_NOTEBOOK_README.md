# MASUKA V2 - Google Colab Notebook Guide

## 🎯 Single Definitive Notebook

This is the **complete, tested, and fixed** notebook for running MASUKA V2 on Google Colab.

**File:** `MASUKA_V2_COLAB_NOTEBOOK.py`

---

## 📋 What's Inside

The notebook contains **4 cells** that do everything:

### **Cell 1: Complete Setup** (10 minutes)
- ✅ Checks GPU availability
- ✅ Clones/updates repository
- ✅ Installs PyTorch 2.4.1 (no circular imports!)
- ✅ Installs all dependencies
- ✅ Sets up PostgreSQL (with proper md5 auth)
- ✅ Sets up Redis
- ✅ Configures environment
- ✅ Starts FastAPI backend
- ✅ Starts Celery worker
- ✅ Creates ngrok tunnel
- ✅ Provides public API URL

### **Cell 2: Test API** (30 seconds)
- Tests all API endpoints
- Verifies services are running
- Checks GPU availability
- Provides quick links

### **Cell 3: Utility Commands** (reference)
- Quick commands for common tasks
- Restart services
- Check logs
- View status

### **Cell 4: Diagnostic Tool** (troubleshooting)
- Comprehensive health check
- Identifies problems
- Shows system status

---

## 🚀 How to Use

### Step 1: Create New Colab Notebook
1. Go to https://colab.research.google.com
2. Click **File → New Notebook**
3. Name it: "MASUKA_V2_Setup"

### Step 2: Set Runtime to GPU
1. Click **Runtime → Change runtime type**
2. Select **GPU** (preferably T4)
3. Click **Save**

### Step 3: Copy Cells
1. Open `MASUKA_V2_COLAB_NOTEBOOK.py`
2. Copy **Cell 1** (lines 16-371)
3. Paste into first Colab cell
4. Copy **Cell 2** (lines 376-503)
5. Paste into second Colab cell
6. Copy **Cell 3** (lines 508-546)
7. Paste into third Colab cell
8. Copy **Cell 4** (lines 551-680)
9. Paste into fourth Colab cell

### Step 4: Run Setup
1. Run **Cell 1** only
2. Wait ~10 minutes
3. Look for: `🎉 MASUKA V2 Setup Complete!`
4. Note your **public API URL**

### Step 5: Verify
1. Run **Cell 2**
2. Check for all ✅ marks
3. Visit the API docs link

---

## ✅ What's Fixed

### 1. PyTorch Circular Import
**Problem:** `AttributeError: partially initialized module 'torchvision'`

**Solution:**
- Uninstall existing torch before install
- Clear pip cache
- Install specific compatible versions (2.4.1 + 0.19.1)
- Verify in subprocess to avoid cache conflicts

### 2. Database Authentication
**Problem:** `FATAL: Peer authentication failed for user "masuka"`

**Solution:**
- Automatically configures pg_hba.conf for md5 auth
- Uses TCP/IP connection (localhost:5432)
- Restarts PostgreSQL after config change

### 3. Timing Issues
**Problem:** "Connection refused" when accessing too early

**Solution:**
- Waits 20 seconds after backend start
- Tests backend before creating tunnel
- Provides clear feedback during startup

### 4. CUDA Warnings
**Problem:** Multiple "Unable to register" warnings

**Solution:**
- These are harmless TensorFlow/PyTorch conflicts
- Don't affect functionality
- Can be safely ignored

---

## 📊 Expected Output

### Cell 1 Success:
```
======================================================================
🎉 MASUKA V2 Setup Complete!
======================================================================

📡 Your Public API URL:
   https://xxxx.ngrok-free.dev

📚 Important Links:
   • API Documentation: https://xxxx.ngrok-free.dev/docs
   ...

✅ Services Running:
   • PostgreSQL (md5 auth configured)
   • Redis
   • FastAPI Backend
   • Celery Worker (GPU: Tesla T4)
   • SimpleTuner
```

### Cell 2 Success:
```
🧪 MASUKA V2 - API Testing
...
1️⃣ Testing Health Endpoint...
  ✅ Status: healthy
  ✅ App: MASUKA V2 v2.0.0
  ✅ Mode: single-user

2️⃣ Testing Models API...
  ✅ Models API working
  ✅ Current models: 0
...
```

---

## 🔧 Troubleshooting

### If Cell 1 Fails:

**1. Check GPU:**
```python
!nvidia-smi
```
Make sure you see a GPU listed.

**2. Run Cell 4 (Diagnostics):**
This will show exactly what's wrong.

**3. Common Issues:**

| Error | Solution |
|-------|----------|
| No GPU detected | Runtime → Change runtime type → GPU |
| Import error | Restart runtime, run Cell 1 again |
| Port already in use | `!pkill -f uvicorn` then run Cell 1 |
| Database error | Check Cell 4 diagnostics output |

---

## 📝 Configuration

### Environment Variables

The notebook creates a `.env` file with these settings:

```bash
# You can modify these after setup:

# Storage (Cloudflare R2 or AWS S3)
S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_ENDPOINT_URL=https://your-account.r2.cloudflarestorage.com

# Hugging Face (for Flux model downloads)
HF_TOKEN=hf_your_token_here
```

**To update:**
1. After Cell 1 completes
2. Run:
```python
# Edit .env file
with open('/content/masuka-v2/backend/.env', 'a') as f:
    f.write('\nHF_TOKEN=hf_your_actual_token\n')

# Restart backend to apply changes
!pkill -f uvicorn
!cd /content/masuka-v2/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

---

## 🎓 Understanding the Stack

```
┌─────────────────────────────────────────┐
│  Google Colab Notebook                   │
│  • Cell 1: Setup (10 min)               │
│  • Cell 2: Test (30 sec)                │
│  • Cell 3: Utils (reference)            │
│  • Cell 4: Diagnostics                  │
└─────────────────────────────────────────┘
              ↓ Creates
┌─────────────────────────────────────────┐
│  Google Colab VM                         │
│  • GPU: Tesla T4 (14-15 GB VRAM)        │
│  • CPU: 2 cores                         │
│  • RAM: 12.7 GB                         │
│  • Disk: ~70 GB free                    │
└─────────────────────────────────────────┘
              ↓ Runs
┌─────────────────────────────────────────┐
│  MASUKA V2 Services                      │
│  ├─ PostgreSQL (Database)               │
│  ├─ Redis (Queue)                       │
│  ├─ FastAPI Backend (:8000)             │
│  ├─ Celery Worker (GPU tasks)           │
│  └─ SimpleTuner (LoRA training)         │
└─────────────────────────────────────────┘
              ↓ Exposed via
┌─────────────────────────────────────────┐
│  Ngrok Tunnel                           │
│  https://xxxx.ngrok-free.dev            │
└─────────────────────────────────────────┘
              ↓ Accessible from
┌─────────────────────────────────────────┐
│  Public Internet                        │
│  • Web apps                             │
│  • Mobile apps                          │
│  • API clients                          │
└─────────────────────────────────────────┘
```

---

## 💡 Pro Tips

### 1. Keep Session Alive
Colab disconnects after ~90 minutes of inactivity.

**Solution:** Run this in a cell:
```python
import time
while True:
    time.sleep(300)  # Every 5 minutes
    print(".", end="", flush=True)
```

### 2. Save Your URL
Store the ngrok URL for reuse:
```python
# After Cell 1 completes
API_URL = "https://xxxx.ngrok-free.dev"

# Use in API calls
import requests
response = requests.post(f"{API_URL}/api/training/start", json={...})
```

### 3. Monitor GPU Usage
```python
# Run this to watch GPU in real-time
!watch -n 2 nvidia-smi
```

### 4. Check Backend Logs
If something's wrong:
```python
# View last 50 lines of backend logs
!ps aux | grep uvicorn  # Get PID
!cat /proc/<PID>/fd/1 | tail -50
```

---

## 📚 API Endpoints

Once setup is complete, these endpoints are available:

### Health Check
```bash
GET /health
```

### Models
```bash
GET /api/models/              # List all models
GET /api/models/{id}          # Get model details
DELETE /api/models/{id}       # Delete model
```

### Datasets
```bash
POST /api/datasets/           # Create dataset
GET /api/datasets/            # List datasets
POST /api/datasets/{id}/upload # Upload images
```

### Training
```bash
POST /api/training/start      # Start training
GET /api/training/status      # Check status
POST /api/training/cancel     # Cancel training
```

### Generation
```bash
POST /api/generate/           # Generate image
GET /api/generate/history     # View history
```

### Documentation
```bash
GET /docs                     # Interactive API docs
GET /openapi.json             # OpenAPI specification
```

---

## 🎯 Next Steps After Setup

### 1. Test the API
Visit the `/docs` endpoint to see interactive documentation.

### 2. Upload Training Data
Prepare 10-30 images of your subject:
- Same subject in different poses/lighting
- High quality (1024x1024 or larger)
- Diverse backgrounds and angles

### 3. Create a Dataset
```python
import requests

# Create dataset
response = requests.post(
    f"{API_URL}/api/datasets/",
    json={
        "name": "My Subject",
        "description": "Training data for my custom LoRA"
    }
)
dataset_id = response.json()['id']

# Upload images
files = []
for image_path in image_paths:
    files.append(
        ('files', open(image_path, 'rb'))
    )

response = requests.post(
    f"{API_URL}/api/datasets/{dataset_id}/upload",
    files=files
)
```

### 4. Start Training
```python
response = requests.post(
    f"{API_URL}/api/training/start",
    json={
        "dataset_id": dataset_id,
        "model_name": "my_lora_v1",
        "trigger_word": "mysubject",
        "steps": 1000,
        "learning_rate": 0.0001
    }
)
```

### 5. Generate Images
After training completes:
```python
response = requests.post(
    f"{API_URL}/api/generate/",
    json={
        "prompt": "mysubject walking in a park, sunset lighting",
        "model_id": "your-trained-model-id",
        "num_inference_steps": 28,
        "guidance_scale": 3.5
    }
)

image_url = response.json()['image_url']
```

---

## ⚠️ Important Notes

### Session Persistence
- Colab sessions are temporary
- Models/data are lost when runtime disconnects
- Use S3/R2 storage for persistence
- Save model checkpoints to cloud storage

### GPU Limitations
- Free Colab: Limited GPU time (~12 hours/day)
- Colab Pro: More GPU time + better GPUs
- GPU timeout after 12 hours continuous use
- Save checkpoints frequently

### Ngrok Limitations
- Free ngrok URLs are temporary
- URL changes if tunnel reconnects
- Limited to 40 connections/minute
- Consider ngrok paid plan for production

### Storage Limitations
- Colab disk: ~70 GB free space
- Temporary storage only
- Use cloud storage (S3/R2) for models
- Clean up old files regularly

---

## 🔗 Resources

- **MASUKA V2 GitHub:** https://github.com/SamuelD27/masuka
- **SimpleTuner:** https://github.com/bghira/SimpleTuner
- **Flux Model:** https://huggingface.co/black-forest-labs/FLUX.1-dev
- **Colab Docs:** https://colab.research.google.com/notebooks/intro.ipynb
- **FastAPI Docs:** https://fastapi.tiangolo.com/

---

## ✅ Success Checklist

Before you start training, verify:

- [ ] Cell 1 completed without errors
- [ ] Got "🎉 MASUKA V2 Setup Complete!" message
- [ ] Public API URL is accessible
- [ ] Cell 2 shows all ✅ checks
- [ ] `/docs` endpoint loads successfully
- [ ] GPU shows in `nvidia-smi`
- [ ] All services running (Cell 4 shows ✅)

**All checked?** → You're ready to train! 🚀

---

## 📞 Support

If you encounter issues:

1. **Run Cell 4 (Diagnostics)** - Shows what's wrong
2. **Check this README** - Solutions for common issues
3. **Restart runtime** - Often fixes transient issues
4. **Check GitHub Issues** - See if others had same problem

---

## 🎉 You're Ready!

This notebook provides everything you need to:
- ✅ Train custom LoRA models
- ✅ Generate images with Flux
- ✅ Manage models and datasets
- ✅ All with a simple public API

**Happy training!** 🎨🚀

---

*Notebook Version: 1.0*
*Last Updated: 2025-10-15*
*Tested on: Google Colab (Tesla T4 GPU)*
