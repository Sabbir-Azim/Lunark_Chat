"""Runtime-aware paths for local, container, and Vercel deployments."""

import os
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
IS_VERCEL = os.getenv("VERCEL") == "1"

configured_runtime_dir = os.getenv("LUNARKCHAT_RUNTIME_DIR")

if configured_runtime_dir:
    RUNTIME_DIR = Path(configured_runtime_dir)
elif IS_VERCEL:
    # A Vercel Function's deployed files are read-only. /tmp is the only
    # writable location and may be discarded between function instances.
    RUNTIME_DIR = Path("/tmp/lunarkchat")
else:
    RUNTIME_DIR = PROJECT_DIR

DATA_DIR = RUNTIME_DIR / "data"
UPLOADS_DIR = RUNTIME_DIR / "uploads"
CHROMA_DIR = RUNTIME_DIR / "chroma_db"
TEMPLATE_DIR = PROJECT_DIR / "templates"

CHAT_DATABASE_PATH = DATA_DIR / "chatbot_memory.db"
CHECKPOINT_DATABASE_PATH = DATA_DIR / "langgraph_checkpoints.sqlite"

for directory in (DATA_DIR, UPLOADS_DIR, CHROMA_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def sqlite_url(path: Path) -> str:
    """Return a SQLAlchemy SQLite URL for relative or absolute paths."""
    return f"sqlite:///{path.as_posix()}"
