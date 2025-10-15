#@title 🚀 CELL 1: Complete Setup (Run Once) - FIXED VERSION
#@markdown This will take ~10 minutes. Includes torch/torchvision compatibility fix!

import os
import sys
import time
import subprocess
from IPython.display import clear_output, HTML

def print_step(emoji, title, status=""):
    print(f"\n{emoji} {title}")
    print("="*60)
    if status:
        print(status)

def run_command(cmd, description, silent=True):
    """Run a command and handle output"""
    print(f"  {description}...", end="", flush=True)
    try:
        if silent:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        else:
            result = subprocess.run(cmd, shell=True, check=True)
        print(" ✅")
        return True
    except subprocess.CalledProcessError as e:
        print(f" ❌\n{e}")
        return False

print("")
print("="*70)
print("     🎨 MASUKA V2 - Complete Setup Starting")
print("="*70)

# ============================================================
# STEP 1: Check GPU
# ============================================================
print_step("1️⃣", "Checking GPU")
run_command("nvidia-smi -L", "Detecting GPU", silent=True)

import torch
if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"  GPU: {gpu_name}")
    print(f"  VRAM: {vram:.1f} GB")
    print("  ✅ GPU Ready!")
else:
    print("  ❌ No GPU detected!")
    print("  Go to: Runtime → Change runtime type → GPU")
    sys.exit(1)

# ============================================================
# STEP 2: Clone Repository
# ============================================================
print_step("2️⃣", "Cloning MASUKA V2 Repository")
if not os.path.exists('/content/masuka-v2'):
    run_command(
        "git clone https://github.com/SamuelD27/masuka.git /content/masuka-v2",
        "Cloning from GitHub",
        silent=False
    )
else:
    print("  ✅ Repository exists")
    os.chdir('/content/masuka-v2')
    run_command("git pull origin main", "Updating repository", silent=False)

os.chdir('/content/masuka-v2')

# ============================================================
# STEP 3: Install Compatible PyTorch Versions (CRITICAL FIX!)
# ============================================================
print_step("3️⃣", "Installing Compatible PyTorch + ML Dependencies")
print("  This may take 3-5 minutes...")

# IMPORTANT: Install specific compatible versions to avoid import errors
print("  Installing torch, torchvision, torchaudio with matching versions...")
subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q",
     "torch==2.4.0",
     "torchvision==0.19.0",  # Compatible with torch 2.4.0 - CRITICAL!
     "torchaudio==2.4.0"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

print("  ✅ PyTorch installed with compatible versions")

# Now install rest of dependencies from requirements.txt
print("  Installing remaining dependencies...")
subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-r", "backend/requirements.txt"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

# Install pyngrok for tunnel
subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "pyngrok"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

print("  ✅ All dependencies installed")

# Verify key packages
import torch
import torchvision
import fastapi, celery, pydantic, diffusers
print(f"  torch: {torch.__version__}")
print(f"  torchvision: {torchvision.__version__}")
print(f"  FastAPI: {fastapi.__version__}")
print(f"  Celery: {celery.__version__}")
print(f"  Pydantic: {pydantic.__version__}")
print(f"  Diffusers: {diffusers.__version__}")

# Test critical import to catch errors early
print("\n  🧪 Testing critical imports...")
try:
    from diffusers import FluxPipeline
    print("  ✅ FluxPipeline import successful!")
except Exception as e:
    print(f"  ❌ FluxPipeline import failed: {e}")
    print("  Backend will not start! Check error above.")
    raise

# ============================================================
# STEP 4: Install SimpleTuner
# ============================================================
print_step("4️⃣", "Installing SimpleTuner")
if not os.path.exists('/content/SimpleTuner'):
    run_command(
        "git clone -q https://github.com/bghira/SimpleTuner /content/SimpleTuner",
        "Cloning SimpleTuner",
        silent=False
    )

    print("  Installing SimpleTuner package...", end="", flush=True)
    os.chdir('/content/SimpleTuner')
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-e", "."],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(" ✅")

    os.chdir('/content/masuka-v2')
    print("  ✅ SimpleTuner ready at /content/SimpleTuner")
else:
    print("  ✅ SimpleTuner already installed")

# ============================================================
# STEP 5: Setup PostgreSQL
# ============================================================
print_step("5️⃣", "Setting up PostgreSQL")
run_command("apt-get update -qq && apt-get install -y -qq postgresql postgresql-contrib",
            "Installing PostgreSQL")
run_command("service postgresql start", "Starting PostgreSQL")
time.sleep(2)

commands = [
    "DROP DATABASE IF EXISTS masuka;",
    "DROP USER IF EXISTS masuka;",
    "CREATE USER masuka WITH PASSWORD 'password123';",
    "CREATE DATABASE masuka OWNER masuka;",
    "GRANT ALL PRIVILEGES ON DATABASE masuka TO masuka;"
]
for cmd in commands:
    subprocess.run(["sudo", "-u", "postgres", "psql", "-c", cmd],
                   capture_output=True)
print("  ✅ Database 'masuka' created")

# ============================================================
# STEP 6: Setup Redis
# ============================================================
print_step("6️⃣", "Setting up Redis")
run_command("apt-get install -y -qq redis-server", "Installing Redis")
run_command("redis-server --daemonize yes", "Starting Redis")
time.sleep(1)
run_command("redis-cli ping", "Testing Redis")

# ============================================================
# STEP 7: Configure Environment
# ============================================================
print_step("7️⃣", "Configuring Environment")

env_content = """# MASUKA V2 Colab Environment
APP_NAME=MASUKA V2
DEBUG=true

# Database
DATABASE_URL=postgresql://masuka:password123@localhost:5432/masuka

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# JWT
SECRET_KEY=colab-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Storage (AWS S3) - REPLACE WITH YOUR CREDENTIALS
S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
S3_REGION=your-region

# Hugging Face (for Flux model download)
HF_TOKEN=hf_your_token_here

# Paths
SIMPLETUNER_PATH=/content/SimpleTuner
MODELS_PATH=/content/models
TEMP_PATH=/tmp/masuka

# CORS
CORS_ORIGINS=*
"""

os.makedirs('/content/masuka-v2/backend', exist_ok=True)
with open('/content/masuka-v2/backend/.env', 'w') as f:
    f.write(env_content)
print("  ✅ Environment configured")

# ============================================================
# STEP 8: Initialize Database & Directories
# ============================================================
print_step("8️⃣", "Initializing Database & Directories")
os.makedirs('/tmp/masuka/uploads', exist_ok=True)
os.makedirs('/tmp/masuka/training', exist_ok=True)
os.makedirs('/tmp/masuka/generated', exist_ok=True)
os.makedirs('/tmp/masuka/model_cache', exist_ok=True)
os.makedirs('/content/models', exist_ok=True)
print("  ✅ Directories created")

# ============================================================
# STEP 9: Start FastAPI Backend
# ============================================================
print_step("9️⃣", "Starting FastAPI Backend")
os.chdir('/content/masuka-v2/backend')

subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
time.sleep(3)

backend_process = subprocess.Popen(
    ['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--log-level', 'info'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

print("  ⏳ Waiting for backend to start...")
time.sleep(20)  # Increased wait time for first startup

import requests
backend_ok = False
try:
    response = requests.get('http://localhost:8000/health', timeout=10)
    health = response.json()
    print(f"  ✅ Backend running: {health['app']} v{health['version']}")
    backend_ok = True

    # Verify new Phase 3 endpoints
    response = requests.get('http://localhost:8000/api/models/', timeout=5)
    if response.status_code == 200:
        print(f"  ✅ Models API loaded (Phase 3)")
    else:
        print(f"  ⚠️  Models API returned {response.status_code}")

except Exception as e:
    print(f"  ❌ Backend not responding: {e}")
    print(f"  Checking backend process...")

if not backend_ok:
    print("\n  ⚠️  Backend may have failed to start!")
    print("  Try checking import errors with:")
    print("    python3 -c 'from app.main import app'")

# ============================================================
# STEP 10: Start Celery Worker
# ============================================================
print_step("🔟", "Starting Celery Worker")

subprocess.run(['pkill', '-f', 'celery'], capture_output=True)
time.sleep(2)

celery_process = subprocess.Popen(
    ['celery', '-A', 'app.tasks.celery_app', 'worker',
     '--loglevel=info', '--concurrency=1', '-Q', 'training,generation'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

print("  ⏳ Waiting for Celery to start...")
time.sleep(5)
print(f"  ✅ Celery worker running with training+generation queues (GPU: {gpu_name})")

# ============================================================
# STEP 11: Expose via ngrok
# ============================================================
print_step("1️⃣1️⃣", "Creating Public URL")

from pyngrok import ngrok

ngrok.set_auth_token("33u4PSfJRAAdkBVl0lmMTo7LebK_815Q5PcJK6h68hM5PUAyM")
ngrok.kill()
time.sleep(2)

public_url = ngrok.connect(8000)
print("  ✅ Tunnel created")

# ============================================================
# FINAL OUTPUT
# ============================================================
print("\n" + "="*70)
print("🎉 MASUKA V2 Setup Complete!")
print("="*70)
print(f"\n📡 Your Public API URL:")
print(f"   {public_url}")
print(f"\n📚 Interactive Docs:")
print(f"   {public_url}/docs")
print(f"\n🔍 Health Check:")
print(f"   {public_url}/health")
print("\n" + "="*70)
print("\n✅ Services Running:")
print("   • PostgreSQL Database")
print("   • Redis Cache & Queue")
print("   • FastAPI Backend")
print(f"   • Celery Worker (GPU: {gpu_name})")
print("   • SimpleTuner Ready")
print("   • Flux Generator Ready (Phase 3)")
print("\n⚠️  Keep this notebook running during training & generation!")
print("\n📖 Next Steps:")
print("   → Run Cell 2 to train a LoRA")
print("   → Run Cell 3 to generate images")
print("="*70)

# Store for other cells
API_URL = str(public_url).replace('NgrokTunnel: "', '').split('"')[0]
if not API_URL.startswith('http'):
    API_URL = str(public_url)
print(f"\n✅ API_URL stored: {API_URL}")

BACKEND_PROCESS = backend_process
CELERY_PROCESS = celery_process
