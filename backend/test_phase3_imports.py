#!/usr/bin/env python3
"""
Quick import test for Phase 3 implementation.
Run this to verify all new modules can be imported without errors.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all Phase 3 imports."""
    print("Testing Phase 3 imports...")

    try:
        print("✓ Importing base_generator...")
        from app.generators.base_generator import BaseGenerator

        print("✓ Importing flux_generator...")
        from app.generators.flux_generator import FluxGenerator

        print("✓ Importing model_service...")
        from app.services.model_service import model_service

        print("✓ Importing generation schemas...")
        from app.schemas.generation import GenerationRequest, GenerationResponse, GenerationJobResponse

        print("✓ Importing model schemas...")
        from app.schemas.model import ModelResponse

        print("✓ Importing generation API...")
        from app.api import generation

        print("✓ Importing models API...")
        from app.api import models

        print("✓ Importing generation tasks...")
        from app.tasks.generation_tasks import generate_image

        print("✓ Importing updated asset model...")
        from app.models.asset import GeneratedAsset

        print("\n✅ All imports successful!")
        print("\nPhase 3 implementation appears to be correct.")
        return True

    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
