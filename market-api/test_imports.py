"""Test script to verify pandas and all dependencies work correctly."""
import sys

print("Python version:", sys.version)
print("Python executable:", sys.executable)

print("\n1. Testing pandas import...")
try:
    import pandas as pd
    print(f"   ✅ pandas version: {pd.__version__}")
except Exception as e:
    print(f"   ❌ pandas failed: {e}")

print("\n2. Testing numpy import...")
try:
    import numpy as np
    print(f"   ✅ numpy version: {np.__version__}")
except Exception as e:
    print(f"   ❌ numpy failed: {e}")

print("\n3. Testing basic DataFrame creation...")
try:
    import pandas as pd
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    print(f"   ✅ DataFrame created: {df.shape}")
except Exception as e:
    print(f"   ❌ DataFrame failed: {e}")

print("\n4. Testing main.py imports...")
try:
    sys.path.insert(0, r'C:\Users\maria\riesgos\Proyecto-Integrador-Teor-a-del-Riesgo\market-api')
    from main import app
    print(f"   ✅ FastAPI app loaded: {app.title}")
except Exception as e:
    print(f"   ❌ main.py imports failed: {e}")

print("\n5. Testing all module imports...")
modules_to_test = [
    ("data.api_data", "get_data"),
    ("modules.returns", "calculate_returns"),
    ("modules.technical", "compute_indicators"),
    ("modules.garch", "compute_garch"),
    ("modules.capm", "compute_capm"),
    ("modules.var", "compute_var"),
    ("services.sheets", "save_to_sheets"),
]

for module_path, func_name in modules_to_test:
    try:
        module = __import__(module_path, fromlist=[func_name])
        func = getattr(module, func_name)
        print(f"   ✅ {module_path}.{func_name}")
    except Exception as e:
        print(f"   ❌ {module_path}.{func_name}: {e}")

print("\n✅ All tests completed!")
