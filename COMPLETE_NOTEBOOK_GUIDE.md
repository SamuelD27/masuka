# 🎨 MASUKA V2 - Complete Notebook Guide

## 🎉 **NEW: Training & Generation Cells Added!**

The notebook now includes **everything you need** for a complete LoRA training workflow!

---

## 📓 **Notebook:** MASUKA_V2_COLAB.ipynb

### ✅ What's Included:

**Setup & Verification (Cells 1-4):**
- Cell 1: Complete setup (~10 min)
- Cell 2: API testing
- Cell 3: Utility commands
- Cell 4: Diagnostics

**Training & Generation (Cells 5-7):** ⭐ **NEW!**
- Cell 5: Upload images & create dataset
- Cell 6: Train LoRA model
- Cell 7: Generate images

---

## 🚀 **Complete Workflow**

### Step 1: Setup (Cell 1)
**Time:** ~10 minutes

**What it does:**
- Installs PyTorch, dependencies
- Sets up database, Redis
- Starts backend, Celery
- Creates public API URL

**Output:**
```
🎉 MASUKA V2 Setup Complete!
📡 Your Public API URL: https://xxxx.ngrok-free.dev
```

---

### Step 2: Test (Cell 2)
**Time:** ~30 seconds

**What it does:**
- Tests all API endpoints
- Verifies services
- Checks GPU

**Output:**
```
✅ Your MASUKA V2 API is ready!
```

---

### Step 3: Upload Images (Cell 5) ⭐ NEW
**Time:** ~2-5 minutes

**Configuration:**
```python
dataset_name = "My Custom LoRA"
trigger_word = "mysubject"
dataset_description = "Training data..."
```

**What it does:**
1. Opens file picker
2. You select 10-30 images
3. Creates dataset via API
4. Uploads images

**Requirements:**
- 10-30 images minimum
- Same subject, different poses/angles
- High quality (1024x1024+)
- Diverse backgrounds/lighting

**Output:**
```
🎉 Dataset Ready!
Dataset ID: xxx-xxx-xxx
Images: 25
```

---

### Step 4: Train LoRA (Cell 6) ⭐ NEW
**Time:** ~10-30 minutes (depends on steps)

**Configuration:**
```python
model_name = "my_lora_v1"
training_steps = 1000
learning_rate = 0.0001
batch_size = 1
```

**What it does:**
1. Starts training with your dataset
2. Monitors progress every 30 seconds
3. Shows status updates
4. Completes when done

**During training:**
```
⏳ Progress updates:
   Status: training - Progress: 25.0%
   Status: training - Progress: 50.0%
   Status: training - Progress: 75.0%
   Status: completed - Progress: 100.0%
```

**Output:**
```
🎉 Training Complete!
Model ID: yyy-yyy-yyy
```

---

### Step 5: Generate Images (Cell 7) ⭐ NEW
**Time:** ~10-30 seconds per image

**Configuration:**
```python
prompt = "mysubject in a garden, sunset"
use_trained_lora = True
num_inference_steps = 28
guidance_scale = 3.5
width = 1024
height = 1024
num_images = 1
```

**What it does:**
1. Generates images with your trained LoRA
2. Downloads and displays in notebook
3. Saves to `/content/generated_image_N.png`

**Output:**
```
🎉 Generation Complete!
📸 Image 1: [displayed in notebook]
Saved to: /content/generated_image_1.png
```

---

## 🎯 **Key Features**

### Cell 5 (Upload):
- ✅ **File picker UI** - Easy image selection
- ✅ **Automatic upload** - No manual API calls
- ✅ **Progress tracking** - See upload status
- ✅ **Form inputs** - Configure via UI

### Cell 6 (Training):
- ✅ **Real-time monitoring** - Live progress updates
- ✅ **Configurable params** - Steps, LR, batch size
- ✅ **Error handling** - Catches and reports failures
- ✅ **Status tracking** - Shows training state

### Cell 7 (Generation):
- ✅ **Image display** - Shows in notebook
- ✅ **Auto download** - Saves locally
- ✅ **Batch generation** - Multiple images
- ✅ **LoRA or base** - Use trained model or base Flux

---

## 💡 **Tips for Best Results**

### Training Images:
```
✅ Good:
- 15-25 images
- Same subject, different poses
- Diverse backgrounds
- Good lighting variety
- High quality (1024x1024+)

❌ Bad:
- Too few images (<10)
- All same pose/angle
- Same background
- Low resolution
- Blurry/dark images
```

### Trigger Word:
```
✅ Good examples:
- "ohwx" (short, unique)
- "johnperson"
- "mycar2024"
- "bluehouse"

❌ Bad examples:
- "the" (too common)
- "person" (generic)
- "beautiful" (ambiguous)
```

### Training Steps:
```
- 500-800: Quick test (5-10 min)
- 1000-1500: Good results (10-20 min)
- 2000-3000: Best quality (20-40 min)
- 4000+: Diminishing returns
```

### Generation:
```
Prompt structure:
"[trigger_word] [doing what] [where], [style/quality]"

Example:
"mysubject walking in a park, sunset lighting, highly detailed, 4k"
```

---

## 📊 **Expected Timing**

| Step | Time | Notes |
|------|------|-------|
| Cell 1: Setup | ~10 min | First run only |
| Cell 2: Test | ~30 sec | Quick verification |
| Cell 5: Upload | ~2-5 min | Depends on # images |
| Cell 6: Train | ~10-30 min | Depends on steps |
| Cell 7: Generate | ~15 sec/img | Per image |
| **Total** | **~30-50 min** | For complete workflow |

---

## 🔧 **Configuration Guide**

### Cell 5 Parameters:

```python
dataset_name = "My Custom LoRA"
# The name for your dataset
# Choose something descriptive

trigger_word = "mysubject"
# The word to activate your LoRA
# Use in prompts when generating
# Should be unique and short

dataset_description = "Training data for..."
# Optional description
# Helps you remember what it's for
```

### Cell 6 Parameters:

```python
model_name = "my_lora_v1"
# Name for your trained model

training_steps = 1000
# Number of training iterations
# More = better quality but slower
# Typical: 1000-2000

learning_rate = 0.0001
# How fast the model learns
# Too high = unstable
# Too low = slow learning
# Default 0.0001 works well

batch_size = 1
# How many images per step
# Keep at 1 for Colab (memory)
```

### Cell 7 Parameters:

```python
prompt = "mysubject in a garden..."
# Your generation prompt
# Include trigger_word for trained LoRA

use_trained_lora = True
# True: Use your trained model
# False: Use base Flux model

num_inference_steps = 28
# Quality/speed tradeoff
# 20-30: Good balance
# 50+: Maximum quality (slower)

guidance_scale = 3.5
# How closely to follow prompt
# 2.0-4.0: Natural results
# 5.0+: Very literal (can be weird)

width = 1024
height = 1024
# Output image size
# 1024x1024: Standard
# 512x512: Faster, lower quality

num_images = 1
# How many images to generate
# Each takes ~15 seconds
```

---

## 🐛 **Troubleshooting**

### Problem: Upload fails
**Solution:**
- Check image file sizes (not too large)
- Ensure images are valid JPG/PNG
- Try smaller batch (10-15 images first)

### Problem: Training fails
**Solution:**
- Run Cell 4 (diagnostics)
- Check GPU is available
- Verify dataset was created (Cell 5 output)
- Check backend logs in Cell 3

### Problem: Generation is slow
**Solution:**
- Reduce `num_inference_steps` to 20
- Use smaller image size (512x512)
- Normal: 10-30 sec per image
- Check GPU isn't being used elsewhere

### Problem: Generated images don't look right
**Solution:**
- Include trigger_word in prompt
- Try different guidance_scale (2.0-5.0)
- Train longer (more steps)
- Use more diverse training images
- Experiment with prompts

---

## 📸 **Example Workflow**

### Complete Example:

**1. Upload (Cell 5):**
```python
dataset_name = "John Portrait"
trigger_word = "johnface"
# Select 20 photos of John
# Different poses, lighting, backgrounds
```

**2. Train (Cell 6):**
```python
model_name = "john_lora_v1"
training_steps = 1500
# Wait ~20 minutes
```

**3. Generate (Cell 7):**
```python
prompt = "johnface as a superhero, flying through city, dramatic lighting"
use_trained_lora = True
num_inference_steps = 28
# Wait ~15 seconds
# Image appears in notebook!
```

**Result:** High-quality image of John as a superhero! 🎨

---

## 🎓 **Best Practices**

### DO:
- ✅ Upload 15-25 high-quality images
- ✅ Use a unique trigger word
- ✅ Train for 1000-2000 steps
- ✅ Include trigger word in prompts
- ✅ Experiment with different prompts
- ✅ Save generated images you like

### DON'T:
- ❌ Upload <10 images (too few)
- ❌ Use generic trigger words
- ❌ Overtrain (4000+ steps)
- ❌ Forget trigger word in prompts
- ❌ Expect perfection on first try
- ❌ Let Colab session disconnect during training

---

## 💾 **Saving Your Work**

### Save Models:
Models are stored in database but temporary in Colab. To persist:

```python
# After training, download model:
import requests
response = requests.get(f"{API_URL}/api/models/{MODEL_ID}/download")
with open(f'{model_name}.safetensors', 'wb') as f:
    f.write(response.content)

# Download to your computer:
from google.colab import files
files.download(f'{model_name}.safetensors')
```

### Save Images:
```python
# Images are saved to /content/generated_image_N.png
# Download them:
from google.colab import files
files.download('/content/generated_image_1.png')
```

---

## 🎉 **You're Ready!**

You now have a **complete LoRA training pipeline** in one notebook:

1. **Setup** ✅
2. **Upload** ✅
3. **Train** ✅
4. **Generate** ✅

**All with easy-to-use form interfaces!**

Just upload the notebook to Colab and start creating! 🚀🎨

---

*Complete Notebook Version: 2.0*
*Includes: Training & Generation*
*Last Updated: 2025-10-15*
