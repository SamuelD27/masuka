#!/usr/bin/env python3
"""Test if all imports work correctly"""

import sys
import traceback

print("Testing imports...")

# Test 1: Basic imports
try:
    from app.config import settings
    print("✅ Config imports OK")
except Exception as e:
    print(f"❌ Config failed: {e}")
    traceback.print_exc()

# Test 2: Model imports
try:
    from app.models import Base, engine
    from app.models.training import TrainingSession
    from app.models.model import Model
    from app.models.asset import GeneratedAsset
    from app.models.dataset import Dataset
    print("✅ Model imports OK")
except Exception as e:
    print(f"❌ Model imports failed: {e}")
    traceback.print_exc()

# Test 3: Schema imports
try:
    from app.schemas.dataset import DatasetCreate, DatasetResponse
    from app.schemas.training import TrainingRequest, TrainingResponse
    print("✅ Schema imports OK")
except Exception as e:
    print(f"❌ Schema imports failed: {e}")
    traceback.print_exc()

# Test 4: API router imports
try:
    from app.api import datasets, training, progress
    print("✅ API router imports OK")
    print(f"   datasets.router: {datasets.router}")
    print(f"   training.router: {training.router}")
    print(f"   progress.router: {progress.router}")
except Exception as e:
    print(f"❌ API router imports failed: {e}")
    traceback.print_exc()

# Test 5: Services
try:
    from app.services.storage_service import storage_service
    print("✅ Storage service imports OK")
except Exception as e:
    print(f"❌ Storage service failed: {e}")
    traceback.print_exc()

# Test 6: Celery tasks
try:
    from app.tasks.celery_app import celery_app
    print("✅ Celery app imports OK")
except Exception as e:
    print(f"❌ Celery app failed: {e}")
    traceback.print_exc()

print("\n" + "="*60)
print("Import test complete!")
