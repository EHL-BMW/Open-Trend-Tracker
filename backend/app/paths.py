from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_DIR.parent / "data"      # gitignored
INTERNAL_DIR = DATA_DIR / "internal"        # BMW-provided files
EXTERNAL_DIR = DATA_DIR / "external"        # drop zone for the partner's data grabber
UNIFIED_DIR = DATA_DIR / "unified"          # pipeline output
RUNTIME_DIR = DATA_DIR / "runtime"          # API-generated uploads and figures
EXAMPLE_OUTPUT_DIR = BACKEND_DIR / "examples" / "plots"
TAXONOMY_FILE = BACKEND_DIR / "taxonomy.json"
