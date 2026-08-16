import sys
from pathlib import Path

# Add parent directory to sys.path to resolve root main module
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from main import app
