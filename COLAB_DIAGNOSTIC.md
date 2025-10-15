# 🔍 Diagnostic Cell for Backend Issues

Run this cell in Colab to diagnose why the backend isn't running:

```python
#@title 🔍 Diagnostic: Check Backend Status

import subprocess
import requests
import time
import os

print("="*70)
print("🔍 MASUKA V2 Backend Diagnostic")
print("="*70)

# 1. Check if uvicorn process is running
print("\n1️⃣ Checking for uvicorn process...")
result = subprocess.run(['pgrep', '-f', 'uvicorn'], capture_output=True, text=True)
if result.stdout.strip():
    print(f"✅ Found uvicorn process: PID {result.stdout.strip()}")
else:
    print("❌ No uvicorn process found!")
    print("   Backend is not running.")

# 2. Check if port 8000 is listening
print("\n2️⃣ Checking if port 8000 is listening...")
result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
if ':8000' in result.stdout:
    print("✅ Port 8000 is listening")
else:
    print("❌ Port 8000 is NOT listening")
    print("   Backend did not bind to port 8000")

# 3. Try to connect locally
print("\n3️⃣ Testing local connection to localhost:8000...")
try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    print(f"✅ Backend is responding!")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except requests.exceptions.ConnectionError:
    print("❌ Connection refused - backend is not running")
except Exception as e:
    print(f"❌ Error: {e}")

# 4. Check backend logs
print("\n4️⃣ Checking recent backend logs...")
if 'BACKEND_PROCESS' in globals():
    print("Reading from BACKEND_PROCESS...")
    # Try to read some output
    try:
        import select
        if select.select([BACKEND_PROCESS.stdout], [], [], 0)[0]:
            output = BACKEND_PROCESS.stdout.read(2000)
            print(output)
    except:
        print("Could not read from process")
else:
    print("⚠️  BACKEND_PROCESS variable not found")
    print("   Backend may have crashed during startup")

# 5. Check for Python errors in backend directory
print("\n5️⃣ Testing backend imports...")
os.chdir('/content/masuka-v2/backend')
result = subprocess.run(
    ['python3', '-c', 'from app.main import app; print("✅ Imports OK")'],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print(result.stdout)
else:
    print("❌ Import error!")
    print(result.stderr)

# 6. Check if all Phase 3 dependencies are installed
print("\n6️⃣ Checking Phase 3 dependencies...")
missing = []
for pkg in ['torch', 'diffusers', 'transformers', 'accelerate']:
    result = subprocess.run(
        ['python3', '-c', f'import {pkg}; print("✅ {pkg}")'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        missing.append(pkg)
        print(f"❌ {pkg} - NOT INSTALLED")
    else:
        print(result.stdout.strip())

if missing:
    print(f"\n⚠️  Missing packages: {', '.join(missing)}")
    print("   Run: pip install torch diffusers transformers accelerate")

print("\n" + "="*70)
print("📋 Summary:")
print("="*70)

# Provide recommendation
if result.stdout.strip() and ':8000' in result.stdout:
    print("✅ Backend appears to be running normally")
    print("   Issue might be with ngrok tunnel")
elif missing:
    print("❌ Missing dependencies - need to install Phase 3 packages")
else:
    print("❌ Backend is not running")
    print("\n💡 Recommended action:")
    print("   1. Check the error output above")
    print("   2. Try restarting the backend (see below)")

print("="*70)
```

After running this, if the backend is not running, use this cell to restart it:

```python
#@title 🔄 Restart Backend with Error Logging

import subprocess
import time
import os
import sys

print("🔄 Restarting FastAPI Backend...\n")

# Kill any existing backend
print("⏹️  Killing old processes...")
subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
time.sleep(3)

# Navigate to backend
os.chdir('/content/masuka-v2/backend')

# Check Python path
print(f"Python: {sys.executable}")
print(f"Working dir: {os.getcwd()}\n")

# Start backend with visible output
print("▶️  Starting backend (showing startup logs)...\n")
print("="*70)

# Start in foreground temporarily to see errors
result = subprocess.run(
    [sys.executable, '-m', 'uvicorn', 'app.main:app',
     '--host', '0.0.0.0', '--port', '8000', '--log-level', 'debug'],
    timeout=10,
    capture_output=True,
    text=True
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print("="*70)

if result.returncode != 0:
    print(f"\n❌ Backend failed to start (exit code {result.returncode})")
    print("\nTroubleshooting:")
    print("1. Check the error messages above")
    print("2. Verify all imports work: python3 -c 'from app.main import app'")
    print("3. Check if Phase 3 dependencies are installed")
else:
    print("\n⚠️  Backend started but timed out (this is normal)")
    print("Now starting in background...\n")

    # Start in background
    backend_process = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'app.main:app',
         '--host', '0.0.0.0', '--port', '8000', '--log-level', 'info'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print("⏳ Waiting for backend to initialize...")
    time.sleep(15)

    # Test
    import requests
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend is running!")
            print(f"   {response.json()}")

            # Test Phase 3 endpoints
            response = requests.get('http://localhost:8000/api/models/', timeout=5)
            print(f"\n✅ /api/models/ endpoint: {response.status_code}")

            BACKEND_PROCESS = backend_process
        else:
            print(f"⚠️  Backend responded with {response.status_code}")
    except Exception as e:
        print(f"❌ Backend still not responding: {e}")
```

---

## Common Issues and Fixes

### Issue 1: Missing Phase 3 Dependencies

**Symptoms:** Import errors for `torch`, `diffusers`, `transformers`

**Fix:**
```python
import subprocess
subprocess.run(['pip', 'install', '-q', 'torch==2.4.0', 'diffusers==0.30.0',
                'transformers==4.44.0', 'accelerate==0.33.0',
                'safetensors==0.4.4', 'pillow==10.4.0'])
```

### Issue 2: Import Error in app.main

**Symptoms:** `ModuleNotFoundError` or `ImportError`

**Fix:** Check which module is failing:
```python
import sys
sys.path.insert(0, '/content/masuka-v2/backend')

# Test each import
try:
    from app.config import settings
    print("✅ config")
except Exception as e:
    print(f"❌ config: {e}")

try:
    from app.models import Base, engine
    print("✅ models")
except Exception as e:
    print(f"❌ models: {e}")

try:
    from app.api import generation, models
    print("✅ api modules")
except Exception as e:
    print(f"❌ api modules: {e}")
```

### Issue 3: Database Connection Error

**Symptoms:** `could not connect to server` or PostgreSQL errors

**Fix:**
```python
import subprocess
subprocess.run(['service', 'postgresql', 'start'])
import time
time.sleep(3)

# Recreate database if needed
commands = [
    "DROP DATABASE IF EXISTS masuka;",
    "DROP USER IF EXISTS masuka;",
    "CREATE USER masuka WITH PASSWORD 'password123';",
    "CREATE DATABASE masuka OWNER masuka;",
]
for cmd in commands:
    subprocess.run(['sudo', '-u', 'postgres', 'psql', '-c', cmd],
                   capture_output=True)
```

### Issue 4: Port Already in Use

**Symptoms:** `Address already in use`

**Fix:**
```python
import subprocess
subprocess.run(['pkill', '-9', '-f', 'uvicorn'])
subprocess.run(['pkill', '-9', '-f', 'python.*app.main'])
import time
time.sleep(3)
# Then restart backend
```

---

Run the diagnostic cell first and share the output!
