import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "market-api"))

exec(open(os.path.join(os.path.dirname(__file__), "market-api", "app", "main.py")).read())
