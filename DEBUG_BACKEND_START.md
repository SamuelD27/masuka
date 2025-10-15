# Debugging Backend Startup Failure

## Issue:
Backend fails to start with "Connection refused" error after 20 second wait.

## Likely Causes:

### 1. **Import Error**
The backend may be failing to import due to:
- Missing dependencies
- Circular imports
- Module not found errors

### 2. **Database Connection Error**
The backend may fail if:
- PostgreSQL isn't ready
- Database URL is incorrect
- Tables can't be created

### 3. **Port Already in Use**
- Old uvicorn process still running
- Port 8000 is occupied

### 4. **Environment File Issues**
- .env file has syntax errors
- Missing required variables

---

## Diagnostic Commands:

### Check if backend process started:
```bash
ps aux | grep uvicorn
```

### Check backend logs:
```bash
# Get PID first
pgrep -f uvicorn

# Then read stdout/stderr
cat /proc/<PID>/fd/1  # stdout
cat /proc/<PID>/fd/2  # stderr
```

### Test import manually:
```bash
cd /content/masuka-v2/backend
python3 -c "from app.main import app; print('OK')"
```

### Check port:
```bash
lsof -i :8000
```

---

## Fixes to Implement:

### 1. **Add Better Error Capture**
```python
# Start backend with visible output first
backend_process = subprocess.Popen(
    ['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,  # Separate stderr
    text=True
)

# Wait and check for errors
time.sleep(5)
if backend_process.poll() is not None:
    # Process died
    stdout, stderr = backend_process.communicate()
    print(f"❌ Backend crashed!")
    print(f"STDOUT: {stdout}")
    print(f"STDERR: {stderr}")
    sys.exit(1)
```

### 2. **Test Import Before Starting**
```python
# Test if app can be imported
print("  🔍 Testing backend import...")
test_import = subprocess.run(
    ['python3', '-c', 'import sys; sys.path.insert(0, \"/content/masuka-v2/backend\"); from app.main import app; print(\"OK\")'],
    capture_output=True,
    text=True,
    cwd='/content/masuka-v2/backend'
)

if test_import.returncode != 0:
    print(f"  ❌ Backend import failed!")
    print(f"  Error: {test_import.stderr}")
    sys.exit(1)
print("  ✅ Backend import successful")
```

### 3. **Increase Wait Time & Add Progress**
```python
# Wait with progress indicator
print("  ⏳ Waiting for backend to start...")
for i in range(6):  # 30 seconds total
    time.sleep(5)
    try:
        response = requests.get('http://localhost:8000/health', timeout=2)
        if response.status_code == 200:
            print(f"  ✅ Backend ready after {(i+1)*5} seconds!")
            break
    except:
        print(f"     Attempt {i+1}/6...", end="\\r")
        continue
else:
    # Failed after all attempts
    print(f"\\n  ❌ Backend did not start after 30 seconds")
```

### 4. **Check Database First**
```python
# Verify database is ready before starting backend
print("  🔍 Verifying database connection...")
result = subprocess.run(
    ['psql', '-U', 'masuka', '-d', 'masuka', '-h', 'localhost', '-c', 'SELECT 1;'],
    capture_output=True,
    text=True,
    env={'PGPASSWORD': 'password123'}
)

if result.returncode != 0:
    print(f"  ⚠️ Database not ready: {result.stderr}")
    print(f"  Waiting 5 more seconds...")
    time.sleep(5)
```

---

## Updated Cell 1 (Backend Start Section):

```python
# =============================================================================
# STEP 9: Start FastAPI Backend
# =============================================================================
print_step("9️⃣", "Starting FastAPI Backend")
os.chdir('/content/masuka-v2/backend')

# Kill any existing process
subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
time.sleep(3)

# Verify database is ready
print("  🔍 Verifying database connection...")
result = subprocess.run(
    ['psql', '-U', 'masuka', '-d', 'masuka', '-h', 'localhost', '-c', 'SELECT 1;'],
    capture_output=True,
    text=True,
    env={'PGPASSWORD': 'password123'}
)
if result.returncode == 0:
    print("  ✅ Database ready")
else:
    print("  ⚠️ Database not ready, waiting...")
    time.sleep(5)

# Test backend import
print("  🔍 Testing backend import...")
test_import = subprocess.run(
    [sys.executable, '-c',
     'import sys; sys.path.insert(0, "/content/masuka-v2/backend"); from app.main import app; print("OK")'],
    capture_output=True,
    text=True,
    cwd='/content/masuka-v2/backend'
)

if test_import.returncode != 0:
    print(f"  ❌ Backend import failed!")
    print(f"  Error: {test_import.stderr}")
    print("\\n  Most common causes:")
    print("  1. Missing dependencies (torch, diffusers)")
    print("  2. Database connection issues")
    print("  3. Import errors in backend code")
    sys.exit(1)
print("  ✅ Backend import successful")

# Start backend
print("  🚀 Starting backend process...")
backend_process = subprocess.Popen(
    ['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--log-level', 'info'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait and check if process is alive
time.sleep(3)
if backend_process.poll() is not None:
    # Process died immediately
    stdout, stderr = backend_process.communicate()
    print(f"  ❌ Backend crashed immediately!")
    print(f"\\n  Error output:")
    print(stderr[-500:] if len(stderr) > 500 else stderr)  # Last 500 chars
    sys.exit(1)

# Wait for backend to be ready
print("  ⏳ Waiting for backend to start...")
backend_ok = False
for i in range(8):  # 40 seconds total
    time.sleep(5)
    try:
        response = requests.get('http://localhost:8000/health', timeout=3)
        if response.status_code == 200:
            health = response.json()
            print(f"  ✅ Backend running: {health['app']} v{health['version']} (after {(i+1)*5}s)")
            backend_ok = True
            break
    except:
        print(f"     Attempt {i+1}/8...", end="\\r")
        continue

if not backend_ok:
    print(f"\\n  ❌ Backend did not start after 40 seconds")
    print("\\n  Checking process status...")
    if backend_process.poll() is not None:
        stdout, stderr = backend_process.communicate()
        print(f"  Process exited with code: {backend_process.poll()}")
        print(f"\\n  Last error output:")
        print(stderr[-500:] if len(stderr) > 500 else stderr)
    else:
        print(f"  Process is still running but not responding")
        print(f"  Try waiting longer or check logs with:")
        print(f"  !cat /proc/$(pgrep -f uvicorn)/fd/2")
    sys.exit(1)
```

---

## Testing Steps:

1. **Test database connection:**
   ```bash
   PGPASSWORD=password123 psql -U masuka -d masuka -h localhost -c "SELECT 1;"
   ```

2. **Test backend import:**
   ```bash
   cd /content/masuka-v2/backend
   python3 -c "from app.main import app; print('OK')"
   ```

3. **Test backend start manually:**
   ```bash
   cd /content/masuka-v2/backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   Watch for errors in output.

4. **Check logs:**
   ```bash
   # After backend starts
   tail -f /proc/$(pgrep -f uvicorn)/fd/2
   ```

---

## Most Likely Issue:

Based on your earlier diagnostics showing the backend WAS working, this is probably:

1. **Timing issue** - Backend needs more time to import diffusers/torch
2. **Environment variables** - The condensed .env string might have formatting issues
3. **Working directory** - Backend needs to be run from correct location

## Quick Fix:

Increase wait time to 40 seconds and add better error reporting!
