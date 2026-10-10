from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_DIR.parent / "data"      # raw internal files live here (gitignored)
EXTERNAL_DIR = DATA_DIR / "external"        # drop zone for the partner's data grabber
UNIFIED_DIR = DATA_DIR / "unified"          # pipeline output
TAXONOMY_FILE = BACKEND_DIR / "taxonomy.json"
