#!/usr/bin/env python3
"""
Create the fixed MASUKA V2 Colab notebook with proper torch/torchvision versions.
"""

import json

# Read the current notebook
with open('MASUKA_V2_Complete.ipynb', 'r') as f:
    notebook = json.load(f)

# Find Cell 1 (setup cell) and update the dependencies installation section
cell_1_code = notebook['cells'][1]['source']

# Convert list to string if needed
if isinstance(cell_1_code, list):
    cell_1_code = ''.join(cell_1_code)

# Add a step to install compatible torch versions BEFORE installing from requirements.txt
new_section = """
# ============================================================
# STEP 3: Install Compatible PyTorch Versions (CRITICAL!)
# ============================================================
print_step("3️⃣", "Installing Compatible PyTorch + ML Dependencies")
print("  This may take 3-5 minutes...")
print("  Installing torch, torchvision, torchaudio with matching versions...")

# Install specific compatible versions to avoid import errors
subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q",
     "torch==2.4.0",
     "torchvision==0.19.0",  # Compatible with torch 2.4.0
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
print("\\n  🧪 Testing critical imports...")
try:
    from diffusers import FluxPipeline
    print("  ✅ FluxPipeline import successful")
except Exception as e:
    print(f"  ❌ FluxPipeline import failed: {e}")
    print("  This will cause backend startup to fail!")
    raise
"""

# Replace the old STEP 3 section
old_step3_start = "# ============================================================\n# STEP 3: Install Dependencies"
old_step4_start = "# ============================================================\n# STEP 4: Install SimpleTuner"

# Find positions
step3_idx = cell_1_code.find(old_step3_start)
step4_idx = cell_1_code.find(old_step4_start)

if step3_idx != -1 and step4_idx != -1:
    # Replace Step 3
    new_cell_1_code = (
        cell_1_code[:step3_idx] +
        new_section +
        "\n" +
        cell_1_code[step4_idx:]
    )

    # Also update Step 4 to become Step 4 (renumbering)
    new_cell_1_code = new_cell_1_code.replace(
        "# STEP 4: Install SimpleTuner",
        "# STEP 4: Install SimpleTuner"
    )

    # Update subsequent step numbers
    for old_num in range(4, 12):
        new_num = old_num
        new_cell_1_code = new_cell_1_code.replace(
            f'print_step("{old_num}️⃣"',
            f'print_step("{new_num}️⃣"'
        )

    # Convert back to list format for notebook
    notebook['cells'][1]['source'] = new_cell_1_code.split('\n')
    notebook['cells'][1]['source'] = [line + '\n' for line in notebook['cells'][1]['source'][:-1]] + [notebook['cells'][1]['source'][-1]]

# Write the updated notebook
with open('MASUKA_V2_Complete.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("✅ Notebook updated with fixed PyTorch installation!")
print("   - torch==2.4.0")
print("   - torchvision==0.19.0 (compatible)")
print("   - torchaudio==2.4.0")
print("   - Added import verification")
