"""
Egg handlers — business logic for Milestones 0 & 1 (The Egg Exists / Hatching).

LEARNING NOTE — what this file teaches:
  - The difference between pure functions and functions with side effects:
      pure function:  takes input, returns output, touches nothing else
      side effect:    reads/writes a file, prints to screen, calls a DB
    create_egg() and warm_egg() both have side effects (write a file).
    That's fine — but it's important to *know* which category a function
    falls into.
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
  - random.randint(a, b): returns a random integer N such that a <= N <= b.
    Both ends are *inclusive* — unlike range() which excludes the upper bound.
  - model_copy(update={...}): Pydantic v2's way to produce a new model
    instance with specific fields changed. It is immutable-friendly — the
    original object is untouched, you get a fresh one back.
  - State machine pattern: a finite set of states (egg/hatchling/…) with
    rules for which transitions are allowed. warm_egg() implements the
    egg → hatchling transition when cracks reach 10.

ARCHITECTURE NOTE:
  This file ONLY contains logic about eggs and Whimling creation.
  It also holds the JSON persistence for now (Milestones 0–2).
  In Milestone 3, the JSON save/load logic moves to a dedicated
  JsonFileRepository class, and these handlers will accept a repository
  parameter instead of doing file I/O directly.
"""

import json
import random
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


# ---------------------------------------------------------------------------
# Milestone 1 — Hatching logic
# ---------------------------------------------------------------------------


def warm_egg() -> tuple[Whimling, int, bool]:
    """
    Tasks 1.1 / 1.2 / 1.3 — Warm the egg, crack it, and hatch it.

    LEARNING: State machine pattern
    --------------------------------
    A state machine is a model of a system that can be in exactly one state
    at a time, with well-defined rules for which transitions are allowed.

    Here the states are: EGG → HATCHLING (→ more states in later milestones)
    The rules:
      - You can only warm an egg that is in EGG state.
      - Warmth increases by a random 5–15 each call.
      - When warmth reaches 80, cracks appear (one crack per warm call).
      - When cracks reach 10, the egg hatches → state becomes HATCHLING.

    LEARNING: random.randint(a, b)
    --------------------------------
    Both a and b are inclusive, unlike range(a, b) which excludes b.
    random.randint(5, 15) → could return 5, 6, 7, …, 14, or 15.

    LEARNING: model_copy(update={...})
    --------------------------------
    Pydantic v2 models are mutable by default, but mutating fields directly
    bypasses validation. model_copy(update={...}) is the safe way to produce
    a modified copy — validation runs on the updated fields, and you always
    work with a fresh object rather than mutating state in place.

    Returns:
      (updated_whimling, warmth_gained, just_hatched)
      The tuple lets main.py print a meaningful message without re-reading
      the file or re-computing anything.

    Raises:
      FileNotFoundError — if no save file exists yet.
      ValueError        — if the Whimling is not in egg state.
    """
    whimling: Whimling = load_whimling()

    # Guard: can only warm an egg
    if whimling.state != WhimlingState.EGG:
        raise ValueError(f"{whimling.name} is already a {whimling.state.value} — there's nothing to warm anymore!")

    # Task 1.1 — Increase warmth by a random amount, clamp to 100
    # min() prevents warmth from ever exceeding the model's le=100 constraint.
    warmth_gained: int = random.randint(5, 15)
    new_warmth: int = min(whimling.egg.warmth + warmth_gained, 100)

    # Task 1.2 — Once warmth hits 80, each warm call adds a crack
    new_cracks: int = whimling.egg.cracks
    if new_warmth >= 80:
        # min() prevents cracks from exceeding the model's le=10 constraint.
        new_cracks = min(new_cracks + 1, 10)

    # Task 1.3 — 10 cracks = hatched!
    just_hatched: bool = new_cracks >= 10 and not whimling.egg.is_hatched
    is_hatched: bool = new_cracks >= 10
    new_state: WhimlingState = WhimlingState.HATCHLING if is_hatched else WhimlingState.EGG

    # Build the updated Egg and Whimling using model_copy — safe, validated,
    # and leaves the original whimling object untouched (good practice).
    new_egg: Egg = Egg(warmth=new_warmth, cracks=new_cracks, is_hatched=is_hatched)
    updated_whimling: Whimling = whimling.model_copy(update={"egg": new_egg, "state": new_state})

    save_whimling(updated_whimling)
    return updated_whimling, warmth_gained, just_hatched
