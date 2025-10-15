#@title 🚀 MANUAL START - Start Backend Only
#@markdown Use this if the backend failed to start in CELL 1

import subprocess
import time
import os
import sys

print("="*70)
print("🚀 Starting MASUKA V2 Backend Manually")
print("="*70)

# Change to backend directory
os.chdir('/content/masuka-v2/backend')

# Kill any existing processes
print("\n1️⃣ Killing existing processes...")
subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
subprocess.run(['pkill', '-f', 'celery'], capture_output=True)
time.sleep(2)
print("  ✅ Cleaned up old processes")

# Test imports first
print("\n2️⃣ Testing critical imports...")
test_script = """
import sys
sys.path.insert(0, '/content/masuka-v2/backend')

print("Testing imports...")
try:
    import torch
    print(f"  ✅ torch: {torch.__version__}")

    import torchvision
    print(f"  ✅ torchvision: {torchvision.__version__}")

    from diffusers import FluxPipeline
    print(f"  ✅ diffusers.FluxPipeline")

    import fastapi
    print(f"  ✅ fastapi: {fastapi.__version__}")

    import celery
    print(f"  ✅ celery: {celery.__version__}")

    from app.main import app
    print(f"  ✅ app.main imported successfully!")

    print("\\n✅ ALL IMPORTS SUCCESSFUL!")

except Exception as e:
    print(f"\\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""

with open('/tmp/test_imports.py', 'w') as f:
    f.write(test_script)

result = subprocess.run([sys.executable, '/tmp/test_imports.py'],
                       capture_output=True, text=True)

print(result.stdout)

if result.returncode != 0:
    print("\n❌ Import test failed!")
    print("STDERR:", result.stderr)
    print("\n💡 Try running CELL1_FINAL_FIX.py again to reinstall dependencies")
    sys.exit(1)

# Start backend
print("\n3️⃣ Starting FastAPI backend...")
print("  This will run in the background...")

backend_process = subprocess.Popen(
    ['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--log-level', 'info'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd='/content/masuka-v2/backend'
)

print("  ⏳ Waiting 15 seconds for startup...")
time.sleep(15)

# Check if it's running
import requests
backend_ok = False

for attempt in range(3):
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"\n  ✅ Backend is running!")
            print(f"     App: {health['app']}")
            print(f"     Version: {health['version']}")
            backend_ok = True
            break
    except Exception as e:
        print(f"  Attempt {attempt + 1}/3 failed: {e}")
        if attempt < 2:
            time.sleep(5)

if not backend_ok:
    print("\n  ❌ Backend failed to start!")
    print("\n  Checking process output...")

    # Try to read process output
    backend_process.poll()
    if backend_process.returncode is not None:
        print(f"  Process exited with code: {backend_process.returncode}")

    print("\n  💡 Try running the debug cell (CELL_DEBUG.py) for more info")
    sys.exit(1)

# Start Celery
print("\n4️⃣ Starting Celery worker...")
celery_process = subprocess.Popen(
    ['celery', '-A', 'app.tasks.celery_app', 'worker',
     '--loglevel=info', '--concurrency=1', '-Q', 'training,generation'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd='/content/masuka-v2/backend'
)

time.sleep(3)
print("  ✅ Celery worker started")

# Setup ngrok tunnel
print("\n5️⃣ Creating ngrok tunnel...")
from pyngrok import ngrok

ngrok.set_auth_token("33u4PSfJRAAdkBVl0lmMTo7LebK_815Q5PcJK6h68hM5PUAyM")
ngrok.kill()
time.sleep(2)

public_url = ngrok.connect(8000)
print("  ✅ Tunnel created")

# Test public URL
print("\n6️⃣ Testing public URL...")
time.sleep(2)

try:
    response = requests.get(f"{public_url}/health", timeout=10)
    if response.status_code == 200:
        print("  ✅ Public URL is working!")
    else:
        print(f"  ⚠️  Got status code: {response.status_code}")
except Exception as e:
    print(f"  ❌ Public URL test failed: {e}")

print("\n" + "="*70)
print("🎉 Backend Started Successfully!")
print("="*70)
print(f"\n📡 Your Public API URL:")
print(f"   {public_url}")
print(f"\n📚 Interactive Docs:")
print(f"   {public_url}/docs")
print(f"\n🔍 Health Check:")
print(f"   {public_url}/health")
print("\n" + "="*70)
print("\n⚠️  Keep this notebook running!")
print("="*70)

# Store for other cells
API_URL = str(public_url)
BACKEND_PROCESS = backend_process
CELERY_PROCESS = celery_process

print(f"\n✅ API_URL stored: {API_URL}")
