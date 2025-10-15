#!/usr/bin/env python3
"""
Helper script to fix dependency conflicts in Colab
Run this in the notebook instead of pip install -r requirements.txt
"""

import subprocess
import sys

def install_package(package):
    """Install a package without showing all output"""
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: {package} - {e}")
        return False

print("📦 Installing MASUKA V2 dependencies (Colab-optimized)...\n")

# Core packages that need specific versions
packages = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.31.1", 
    "pydantic>=2.11.0",
    "pydantic-settings>=2.5.2",
    "python-multipart>=0.0.18",
    "sqlalchemy==2.0.25",
    "psycopg2-binary==2.9.9",
    "alembic==1.13.1",
    "redis==5.0.1",
    "celery==5.3.6",
    "flower==2.0.1",
    "kombu==5.3.5",
    "boto3>=1.34.34",
    "python-dotenv==1.0.0",
    "pyyaml==6.0.1",
    "pyngrok"
]

success_count = 0
for pkg in packages:
    pkg_name = pkg.split(">=")[0].split("==")[0]
    print(f"  Installing {pkg_name}...", end="")
    if install_package(pkg):
        print(" ✅")
        success_count += 1
    else:
        print(" ❌")

print(f"\n✅ Installed {success_count}/{len(packages)} packages successfully")

# Verify key imports
print("\n🔍 Verifying installation...")
try:
    import fastapi
    import celery
    import redis
    import boto3
    import pydantic
    print(f"  ✅ FastAPI: {fastapi.__version__}")
    print(f"  ✅ Celery: {celery.__version__}")
    print(f"  ✅ Pydantic: {pydantic.__version__}")
    print(f"  ✅ boto3: {boto3.__version__}")
    print("\n🎉 All dependencies ready!")
except ImportError as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)
