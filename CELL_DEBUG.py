#@title 🔍 DEBUG CELL - Check Backend Status
#@markdown Run this to diagnose backend issues

import subprocess
import requests
import time

print("="*70)
print("🔍 MASUKA V2 - Backend Diagnostic")
print("="*70)

# Check if backend process is running
print("\n1️⃣ Checking if uvicorn is running...")
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
uvicorn_processes = [line for line in result.stdout.split('\n') if 'uvicorn' in line and 'grep' not in line]

if uvicorn_processes:
    print("  ✅ Found uvicorn processes:")
    for proc in uvicorn_processes:
        print(f"     {proc}")
else:
    print("  ❌ No uvicorn process found!")

# Check if port 8000 is listening
print("\n2️⃣ Checking if port 8000 is listening...")
result = subprocess.run(['lsof', '-i', ':8000'], capture_output=True, text=True)
if result.stdout.strip():
    print("  ✅ Port 8000 is in use:")
    print(result.stdout)
else:
    print("  ❌ Port 8000 is NOT listening!")

# Try to connect to backend
print("\n3️⃣ Testing backend connection...")
try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    print(f"  ✅ Backend responded: {response.status_code}")
    if response.status_code == 200:
        print(f"     {response.json()}")
except Exception as e:
    print(f"  ❌ Backend not responding: {e}")

# Check backend logs if process exists
print("\n4️⃣ Checking for backend errors...")
print("  Attempting to test import manually...")

test_script = """
import sys
sys.path.insert(0, '/content/masuka-v2/backend')

try:
    from app.main import app
    print("✅ Backend app imported successfully!")
except Exception as e:
    print(f"❌ Failed to import app: {e}")
    import traceback
    traceback.print_exc()
"""

with open('/tmp/test_backend.py', 'w') as f:
    f.write(test_script)

result = subprocess.run(['python3', '/tmp/test_backend.py'],
                       capture_output=True, text=True,
                       cwd='/content/masuka-v2/backend')

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)

# Check if environment file exists
print("\n5️⃣ Checking environment configuration...")
import os
if os.path.exists('/content/masuka-v2/backend/.env'):
    print("  ✅ .env file exists")
else:
    print("  ❌ .env file missing!")

# Check database connection
print("\n6️⃣ Checking database...")
result = subprocess.run(['psql', '-U', 'masuka', '-d', 'masuka', '-c', 'SELECT 1;'],
                       capture_output=True, text=True, env={'PGPASSWORD': 'password123'})
if result.returncode == 0:
    print("  ✅ Database connection OK")
else:
    print(f"  ❌ Database connection failed: {result.stderr}")

# Check Redis
print("\n7️⃣ Checking Redis...")
result = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True)
if 'PONG' in result.stdout:
    print("  ✅ Redis is running")
else:
    print("  ❌ Redis not responding")

print("\n" + "="*70)
print("🏁 Diagnostic Complete")
print("="*70)
print("\n💡 Next steps:")
print("   If backend isn't running, check the import test above")
print("   Common issues:")
print("   - Missing dependencies (torch, diffusers)")
print("   - Import errors in app.main")
print("   - Database connection issues")
print("="*70)
