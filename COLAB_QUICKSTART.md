# 🚀 MASUKA V2 - Colab Quick Start Guide

## Complete LoRA Training & Image Generation in 3 Cells!

---

## 📖 Notebook: `MASUKA_V2_Complete.ipynb`

This notebook provides a **complete end-to-end workflow** for training Flux LoRAs and generating images, all in Google Colab with GPU acceleration.

---

## 🎯 What You'll Do

1. **Cell 1** - Setup environment (~10 min)
2. **Cell 2** - Train a LoRA (~30-60 min)
3. **Cell 3** - Generate images (~1 min per image)

---

## 📝 Prerequisites

### 1. Google Colab Setup
- Go to [Google Colab](https://colab.research.google.com/)
- Upload or open: `MASUKA_V2_Complete.ipynb`
- **Enable GPU**: Runtime → Change runtime type → **T4 GPU**
  - For faster training: Choose **A100 GPU** (if available)

### 2. Required Accounts
- **AWS Account** - For S3 storage (models and images saved here)
- **Hugging Face Account** - For Flux model download (optional HF token)
- **ngrok Account** - For public API access (token in notebook)

### 3. Training Images
- **15-25 images** of your subject (person, object, style)
- **JPG or PNG** format
- **1024x1024** resolution recommended (will be resized)
- **Consistent subject** across images

---

## 🚀 Step-by-Step Guide

### Step 1: Setup (Cell 1)

**What it does:**
- Installs all dependencies (FastAPI, Celery, torch, diffusers, SimpleTuner)
- Sets up PostgreSQL database
- Starts Redis for task queue
- Launches FastAPI backend
- Starts Celery worker (training + generation queues)
- Creates ngrok tunnel for public API access

**Time:** ~10 minutes

**How to run:**
1. Click on Cell 1
2. Press the ▶️ Play button
3. Wait for "🎉 MASUKA V2 Setup Complete!"
4. **Copy your API URL** from the output

**Expected output:**
```
🎉 MASUKA V2 Setup Complete!
======================================================================

📡 Your Public API URL:
   https://xxxx-xx-xx-xx-xx.ngrok-free.app

📚 Interactive Docs:
   https://xxxx-xx-xx-xx-xx.ngrok-free.app/docs

✅ Services Running:
   • PostgreSQL Database
   • Redis Cache & Queue
   • FastAPI Backend
   • Celery Worker (GPU: Tesla T4)
   • SimpleTuner Ready
   • Flux Generator Ready (Phase 3)

✅ API_URL stored: https://xxxx-xx-xx-xx-xx.ngrok-free.app
```

**Troubleshooting:**
- If Cell 1 fails, check GPU is enabled
- If services don't start, re-run Cell 1
- Check logs for specific errors

---

### Step 2: Train LoRA (Cell 2)

**What it does:**
- Uploads your training images
- Creates dataset with trigger word
- Starts Flux LoRA training
- Monitors progress in real-time
- Uploads trained model to S3

**Time:** 30-60 min (T4) or 15-30 min (A100)

**Parameters:**
- `dataset_name` - Name for your dataset (e.g., "John Doe Portrait")
- `trigger_word` - Word to activate LoRA (e.g., "TOK", "myface")
- `learning_rate` - 0.0001 (default, recommended)
- `training_steps` - 2000 (default, 1500-3000 works well)

**How to run:**
1. Configure parameters in Cell 2
2. Press ▶️ Play button
3. Click "Choose Files" when prompted
4. Select 15-25 images from your computer
5. Wait for upload and training to start
6. Watch progress bar automatically

**Expected output:**
```
📤 Upload Your Training Images
==============================================================
Click 'Choose Files' and select 15-25 images...

✅ Received 20 files
📦 Creating dataset...
✅ Dataset: 123e4567-e89b-12d3-a456-426614174000
📤 Uploading to server...
✅ Uploaded 20 images

🚀 Starting training...
==============================================================
✅ Training Started!
==============================================================
Session ID: 456e7890-a12b-34c5-d678-901234567890
Status: pending
Task ID: abc123...

⏱️  Estimated Time: 45-60 minutes (T4) or 20-30 minutes (A100)

📊 Monitoring Training Progress...

======================================================================
🎨 John Doe Portrait - v1
======================================================================

Status: 🔄 TRAINING

Progress: 45.2% (904/2,000 steps)
[█████████████████████████░░░░░░░░░░░░░░░] 45.2%

Loss: 0.083421

Elapsed: 22.5m | ETA: 27.3m

======================================================================

⏳ Updating in 10 seconds...
```

**Completion:**
```
🎉 Training Completed!
✅ Model uploaded to S3

📦 Session ID: 456e7890-a12b-34c5-d678-901234567890

💡 Next: Run Cell 3 to generate images with this LoRA!
```

**Tips:**
- **Use clear, consistent images** for best results
- **Trigger word** should be unique (avoid common words)
- **2000 steps** is a good starting point
- Training continues even if you stop monitoring

---

### Step 3: Generate Images (Cell 3)

**What it does:**
- Lists all trained models
- Generates images with Flux + LoRA
- Displays images inline in notebook
- Saves images to S3

**Time:**
- First generation: 10-15 min (Flux model download)
- Subsequent: ~1 min per image

**Parameters:**
- `prompt` - What you want to generate (e.g., "photo of TOK person standing in field")
- `negative_prompt` - What to avoid (e.g., "blurry, low quality")
- `use_lora` - True to use trained LoRA, False for base Flux
- `lora_weight` - 0.0-1.0 (0.8 recommended, higher = stronger effect)
- `num_images` - 1-4 images per generation
- `num_inference_steps` - 10-100 (30 recommended, higher = better quality)
- `guidance_scale` - 1.0-20.0 (3.5 recommended for Flux)
- `width` / `height` - 512-2048 (1024 recommended)
- `seed` - For reproducible results (optional)

**How to run:**
1. Configure parameters in Cell 3
2. Press ▶️ Play button
3. Wait for generation to complete
4. Images will display automatically

**Expected output:**
```
Using API: https://xxxx-xx-xx-xx-xx.ngrok-free.app

📋 Fetching available models...

✅ Found 1 model(s):

1. John Doe Portrait - v1 (v1.0)
   ID: 789e0123-b45c-67d8-e901-234567890abc
   Type: flux_image
   Trigger: TOK
   Size: 142 MB

🎯 Using model: John Doe Portrait - v1

======================================================================
🎨 Starting Image Generation
======================================================================

📝 Prompt: photo of TOK person standing in a field, professional photography
🚫 Negative: blurry, low quality, distorted

⚙️  Settings:
   Images: 2
   Steps: 30
   Guidance: 3.5
   Size: 1024x1024
   LoRA Weight: 0.8

🚀 Submitting generation job...

✅ Generation job created!
📋 Job ID: 012e3456-c78d-90e1-f234-567890abcdef
🔄 Task ID: xyz789...

======================================================================
⏳ Generating images...
======================================================================

💡 First generation takes 10-15 min (Flux model download)
   Subsequent generations: ~1 min per image

🔄 Polling for completion...

[65s] Check #7: processing...
```

**Completion:**
```
======================================================================
🎉 Generation Complete!
======================================================================

⏱️  Total time: 73.2 seconds (1.2 minutes)

✅ Generated 2 image(s):

Image 1:
  URL: https://masuka-v2.s3.ap-southeast-1.amazonaws.com/generated/...

[Image displays here]

Image 2:
  URL: https://masuka-v2.s3.ap-southeast-1.amazonaws.com/generated/...

[Image displays here]

======================================================================

💡 Images saved to S3 bucket: masuka-v2/generated/

📋 Job ID: 012e3456-c78d-90e1-f234-567890abcdef

✨ Generate more images by running this cell again!
======================================================================
```

**Tips:**
- **Include trigger word** in prompt (e.g., "TOK person")
- **First generation is slow** - Flux downloads once (10GB)
- **Experiment with LoRA weight** - 0.6-0.9 usually works best
- **Higher steps = better quality** - But slower (try 28-50)
- **Use seed** for variations of same image

---

## 💡 Pro Tips

### Training Best Practices
1. **Image quality matters** - Use high-res, clear images
2. **Variety is good** - Different angles, lighting, expressions
3. **Consistent subject** - Same person/object across all images
4. **Caption quality** - SimpleTuner auto-captions, but quality images help
5. **Steps** - 1500-3000 typical, 2000 is safe default

### Generation Best Practices
1. **Use trigger word** - Essential for LoRA to work
2. **Start with LoRA 0.8** - Then adjust up/down
3. **Negative prompts help** - List what you don't want
4. **Guidance 3.5** - Flux works well with lower guidance
5. **Steps 28-50** - Sweet spot for quality vs speed

### Troubleshooting

**Training stuck at "pending":**
- Check Celery worker is running (see Cell 1 output)
- Re-run Cell 1 if needed

**Generation taking forever:**
- First time: Flux model downloads (10-15 min)
- Check Celery logs in Cell 1 for errors
- OOM? Reduce `num_images` or `width`/`height`

**Images look wrong:**
- Adjust `lora_weight` (try 0.6-0.9)
- Include trigger word in prompt
- Try more `num_inference_steps`

**"Model not found":**
- Wait for Cell 2 to complete fully
- Check `/api/models/` endpoint in docs

---

## 📊 Resource Usage

### GPU Requirements
- **Minimum:** T4 (15GB VRAM)
- **Recommended:** A100 (40GB VRAM)
- **Training:** ~12GB VRAM usage
- **Generation:** ~14GB VRAM usage

### Storage Requirements
- **SimpleTuner:** ~5GB
- **Flux Model:** ~10GB (cached)
- **LoRA Output:** ~140MB per model
- **Generated Images:** ~2MB per 1024x1024 image

### Time Estimates

**Training (2000 steps):**
- T4: 45-60 minutes
- A100: 15-25 minutes

**Generation:**
- First time: 10-15 min (model download)
- With model cached: 45-90 sec per image
- Steps 30, 1024x1024, A100

---

## 🔗 Useful Links

**API Documentation:**
- Interactive docs: `{API_URL}/docs`
- Health check: `{API_URL}/health`
- Models list: `{API_URL}/api/models/`

**Endpoints:**
- Training: `POST /api/training/flux`
- Generation: `POST /api/generate/image`
- Models: `GET /api/models/`

**GitHub:**
- Repository: https://github.com/SamuelD27/masuka
- Issues: https://github.com/SamuelD27/masuka/issues

---

## 🎉 You're Ready!

1. Open `MASUKA_V2_Complete.ipynb` in Google Colab
2. Enable GPU (T4 or A100)
3. Run Cell 1 (Setup)
4. Run Cell 2 (Train)
5. Run Cell 3 (Generate)

**Have fun creating!** 🎨

---

**Created by MASUKA V2** | Phase 3 Complete ✅
