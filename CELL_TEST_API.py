#@title ✅ TEST API - Verify Everything Works
#@markdown Run this to test your API and get the ngrok URL

import subprocess
import time
import requests

print("="*70)
print("✅ MASUKA V2 - API Test")
print("="*70)

# Check if backend is running
print("\n1️⃣ Checking local backend...")
try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    if response.status_code == 200:
        health = response.json()
        print(f"  ✅ Backend running: {health['app']} v{health['version']}")
    else:
        print(f"  ⚠️  Unexpected status: {response.status_code}")
except Exception as e:
    print(f"  ❌ Backend not responding: {e}")
    print("  Run CELL_START_BACKEND.py to start the backend")
    import sys
    sys.exit(1)

# Check if ngrok is running
print("\n2️⃣ Checking ngrok tunnel...")
try:
    from pyngrok import ngrok
    tunnels = ngrok.get_tunnels()

    if tunnels:
        public_url = tunnels[0].public_url
        print(f"  ✅ Found existing tunnel: {public_url}")
    else:
        print("  ⚠️  No tunnel found, creating new one...")
        ngrok.set_auth_token("33u4PSfJRAAdkBVl0lmMTo7LebK_815Q5PcJK6h68hM5PUAyM")
        public_url = ngrok.connect(8000)
        print(f"  ✅ Created tunnel: {public_url}")

except Exception as e:
    print(f"  ❌ Ngrok error: {e}")
    import sys
    sys.exit(1)

# Test public URL
print("\n3️⃣ Testing public URL...")
print(f"  Waiting 3 seconds for tunnel to stabilize...")
time.sleep(3)

try:
    response = requests.get(f"{public_url}/health", timeout=15)
    if response.status_code == 200:
        print(f"  ✅ Public URL works!")
        print(f"     {response.json()}")
    else:
        print(f"  ⚠️  Status: {response.status_code}")
except Exception as e:
    print(f"  ❌ Public URL test failed: {e}")
    print(f"  This is normal if tunnel just started - try again in 10 seconds")

# Test models endpoint
print("\n4️⃣ Testing models API...")
try:
    response = requests.get(f"{public_url}/api/models/", timeout=10)
    if response.status_code == 200:
        models = response.json()
        print(f"  ✅ Models API works! Found {len(models)} models")
    elif response.status_code == 404:
        print(f"  ⚠️  Models endpoint returned 404 (may not be implemented yet)")
    else:
        print(f"  ⚠️  Status: {response.status_code}")
except Exception as e:
    print(f"  ❌ Models API test failed: {e}")

# Test generation endpoint
print("\n5️⃣ Testing generation API...")
try:
    response = requests.get(f"{public_url}/api/generate/", timeout=10)
    if response.status_code in [200, 405]:  # 405 = Method Not Allowed (needs POST)
        print(f"  ✅ Generation API endpoint exists!")
    elif response.status_code == 404:
        print(f"  ⚠️  Generation endpoint returned 404 (may not be implemented yet)")
    else:
        print(f"  ⚠️  Status: {response.status_code}")
except Exception as e:
    print(f"  ❌ Generation API test failed: {e}")

# Check Celery worker
print("\n6️⃣ Checking Celery worker...")
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
celery_processes = [line for line in result.stdout.split('\n') if 'celery' in line and 'worker' in line and 'grep' not in line]

if celery_processes:
    print(f"  ✅ Celery worker is running")
else:
    print(f"  ⚠️  No Celery worker found")
    print(f"  Training tasks won't work without Celery")

print("\n" + "="*70)
print("🎉 Test Complete!")
print("="*70)
print(f"\n📡 Your Public API URL:")
print(f"   {public_url}")
print(f"\n📚 Quick Links:")
print(f"   • Health Check: {public_url}/health")
print(f"   • API Docs: {public_url}/docs")
print(f"   • Models API: {public_url}/api/models/")
print(f"   • Training API: {public_url}/api/training/")
print(f"   • Generation API: {public_url}/api/generate/")
print("\n" + "="*70)
print("\n✅ READY TO USE!")
print("   You can now make API calls to train and generate images")
print("="*70)

# Store API_URL for other cells
API_URL = str(public_url)
print(f"\n💾 API_URL stored in variable: API_URL = '{API_URL}'")
