"""
Egg handlers — business logic for Milestone 0 (The Egg Exists).

LEARNING NOTE — what this file teaches:
  - The difference between pure functions and functions with side effects:
      pure function:  takes input, returns output, touches nothing else
      side effect:    reads/writes a file, prints to screen, calls a DB
    create_egg() has a side effect (writes a file). That's fine — but it's
    important to *know* which category a function falls into.
  - pathlib.Path: Python's modern path handling. Prefer it over os.path
    or string concatenation. Path("data") / "whimling.json" is readable
    and works on all operating systems.
  - Pydantic v2 serialisation:
      model_dump(mode="json") → gives a plain dict with JSON-safe types
        (datetime → ISO string, Enum → its string value, etc.)
      model_validate(data) → builds a model from a raw dict, running all
        validators. Replaces Pydantic v1's .parse_obj().
  - Standard Python exceptions: FileNotFoundError, FileExistsError are
    built into Python — no imports needed. Always raise the most specific
    built-in exception before reaching for custom ones.

ARCHITECTURE NOTE:
  This file ONLY contains logic about eggs and Whimling creation.
  It also holds the JSON persistence for now (Milestones 0–2).
  In Milestone 3, the JSON save/load logic moves to a dedicated
  JsonFileRepository class, and these handlers will accept a repository
  parameter instead of doing file I/O directly.
"""

import json
from pathlib import Path
from typing import Any

from app.models.whimling import Egg, Whimling, WhimlingState

# ---------------------------------------------------------------------------
# Storage paths
# All paths are relative to where Python is invoked (the project root).
# ---------------------------------------------------------------------------
DATA_DIR: Path = Path("data")
SAVE_FILE: Path = DATA_DIR / "whimling.json"


# ---------------------------------------------------------------------------
# Persistence helpers (will move to JsonFileRepository in Milestone 3)
# ---------------------------------------------------------------------------


def _ensure_data_dir() -> None:
    """Create data/ if it doesn't exist. exist_ok=True means no error if it does."""
    DATA_DIR.mkdir(exist_ok=True)


def save_whimling(whimling: Whimling) -> None:
    """
    Serialise the Whimling to disk as a JSON file.

    model_dump(mode="json") is critical here. Without mode="json":
      - datetime fields stay as Python datetime objects → json.dumps() raises TypeError
      - Enum fields stay as Enum instances → json.dumps() raises TypeError
    With mode="json", Pydantic converts everything to JSON-safe primitives first.
    """
    _ensure_data_dir()
    data: dict[str, Any] = whimling.model_dump(mode="json")
    SAVE_FILE.write_text(json.dumps(data, indent=2))


def load_whimling() -> Whimling:
    """
    Load the Whimling from disk and validate it back into a model.

    model_validate() does two things:
      1. Parses the raw dict from JSON
      2. Runs all Pydantic validators (field types, ge/le constraints, etc.)
    If the file contains invalid data (corrupted JSON, wrong types), Pydantic
    raises a ValidationError with a clear message about what failed.
    """
    if not whimling_exists():
        raise FileNotFoundError(f"No save file found at '{SAVE_FILE}'. Run `python main.py create` first to bring your Whimling into existence.")
    data: dict[str, Any] = json.loads(SAVE_FILE.read_text())
    return Whimling.model_validate(data)


def whimling_exists() -> bool:
    """Return True if a save file already exists on disk."""
    return SAVE_FILE.exists()


# ---------------------------------------------------------------------------
# Business logic
# ---------------------------------------------------------------------------


def create_egg(name: str) -> Whimling:
    """
    Task 0.3 — Create a brand-new Whimling in egg state and persist it.

    Business rules enforced here:
      - Only one Whimling can exist at a time (for now).
        Raises FileExistsError if a save file already exists.

    Returns the newly created Whimling so the caller (main.py) can display it.
    """
    if whimling_exists():
        raise FileExistsError("A Whimling already exists! Use `python main.py status` to check on it.")

    whimling: Whimling = Whimling(name=name, state=WhimlingState.EGG, egg=Egg())
    save_whimling(whimling)
    return whimling
