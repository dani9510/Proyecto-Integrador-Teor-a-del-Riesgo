import runpy
import sys
import os

root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(root, "market-api"))

runpy.run_path(
    os.path.join(root, "market-api", "app", "main.py"),
    run_name="__main__"
)
