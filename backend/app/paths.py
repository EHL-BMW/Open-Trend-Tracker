import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
DATA_DIR = ROOT_DIR / "data"      # gitignored
INTERNAL_DIR = DATA_DIR / "internal"        # BMW-provided files
EXTERNAL_DIR = DATA_DIR / "external"        # drop zone for the partner's data grabber
UNIFIED_DIR = DATA_DIR / "unified"          # pipeline output
RUNTIME_DIR = DATA_DIR / "runtime"          # API-generated uploads and figures
EXAMPLE_OUTPUT_DIR = BACKEND_DIR / "examples" / "plots"
TAXONOMY_FILE = BACKEND_DIR / "taxonomy.json"

def reload_env_secrets() -> None:
    """Reload local secrets from backend/.env or root .env into os.environ."""
    for env_path in (BACKEND_DIR / ".env", ROOT_DIR / ".env"):
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip("'\"")


# Initial load at import time
reload_env_secrets()


def get_openai_api_key() -> str | None:
    """Return OpenAI API key from os.environ or freshly reloaded from .env."""
    key = os.getenv("OPENAI_API_KEY")
    if key and key.strip() and key.strip() != "your_openai_api_key_here":
        return key.strip().strip("'\"")
    reload_env_secrets()
    key = os.getenv("OPENAI_API_KEY")
    if key and key.strip() and key.strip() != "your_openai_api_key_here":
        return key.strip().strip("'\"")
    return None


def get_openai_model() -> str:
    """Return configured model or default to gpt-4o-mini."""
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()


