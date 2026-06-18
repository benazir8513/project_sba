# Milestone 0 — The Egg Exists 🥚

**Status:** ✅ Complete
**Completed:** 2026-06-17
**Concepts:** Pydantic v2, Python Enums, pathlib, JSON serialisation, sys.argv, layered architecture

---

## What Was Built

The most fundamental thing: a Whimling can be created and its data persists to disk.

```bash
uv run python main.py create Zephyr   # Creates data/whimling.json
uv run python main.py status          # Reads and displays it
cat data/whimling.json                # Inspect the raw JSON
```

---

## Files Created / Modified

| File | Role | What It Is |
|------|------|-----------|
| `src/app/models/whimling.py` | Model layer | Defines what a Whimling IS (data + validation) |
| `src/app/handlers/egg.py` | Handler layer | Defines what you can DO (create, save, load) |
| `main.py` | CLI entrypoint | How a user interacts with the system |
| `pyproject.toml` | Build config | Added hatchling build system for src/ layout |
| `data/.gitkeep` | Data folder | Ensures `data/` exists in git but saves are gitignored |

### Empty package markers (required for Python to treat folders as importable packages)
- `src/__init__.py`
- `src/app/__init__.py`
- `src/app/models/__init__.py`
- `src/app/handlers/__init__.py`

---

## Architecture: The Layered Rule

The project enforces a strict one-way dependency flow:

```
main.py (CLI)
    ↓ imports
src/app/handlers/egg.py  (business logic)
    ↓ imports
src/app/models/whimling.py  (data definitions)
```

**The rule: nothing flows upward.**

- `whimling.py` imports from nothing in this project
- `egg.py` imports from `models/` only
- `main.py` imports from `handlers/` only

This is not enforced by Python itself — it's a discipline. In Milestone 3, we'll add
`import-linter` to enforce it automatically. The benefit: you can change `main.py`
without touching handlers, and you can add a new handler without touching models.

---

## Key Decisions & Why

### Decision 1: `src/` layout

The code lives in `src/app/` not directly in the project root. This is the standard
Python "src layout". Without it, `import app` might accidentally import a local folder
called `app/` rather than the installed package. The `src/` barrier prevents this.

Configured in `pyproject.toml`:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/app"]
```

After `uv sync`, the `app` package is installed into the virtual env. You import it
as `from app.models.whimling import Whimling` — no `src.` prefix.

### Decision 2: `StrEnum` over `(str, Enum)`

```python
# Old pattern (still valid, but verbose):
class WhimlingState(str, Enum):
    EGG = "egg"

# New pattern (Python 3.11+, cleaner):
from enum import StrEnum
class WhimlingState(StrEnum):
    EGG = "egg"
```

Both give `WhimlingState.EGG == "egg" → True`. `StrEnum` is the modern way.

### Decision 3: `default_factory` for mutable defaults

```python
# WRONG — dangerous:
class Whimling(BaseModel):
    egg: Egg = Egg()          # One Egg object shared by ALL Whimling instances
    created_at: datetime = datetime.now(UTC)  # Same timestamp for ALL instances

# CORRECT:
class Whimling(BaseModel):
    egg: Egg = Field(default_factory=Egg)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

The factory runs fresh each time a new `Whimling()` is created.

### Decision 4: `model_dump(mode="json")` for serialisation

Pydantic models contain Python-native types: `datetime` objects, `Enum` instances.
`json.dumps()` cannot handle these directly. `mode="json"` instructs Pydantic to
convert everything to JSON primitives first:

```python
whimling.model_dump()              # {"created_at": datetime(2026, ...), "state": <WhimlingState.EGG>}
whimling.model_dump(mode="json")   # {"created_at": "2026-06-17T14:43:09Z", "state": "egg"}
```

Always use `mode="json"` when the output goes to `json.dumps()` or a database.

### Decision 5: `model_validate()` for deserialisation

```python
# Reading back from JSON:
data = json.loads(file_content)   # raw dict, all strings
whimling = Whimling.model_validate(data)  # parses + validates
```

Pydantic v1 used `.parse_obj()`. In v2, it's `.model_validate()`. The model
automatically converts `"2026-06-17T14:43:09Z"` back to a `datetime` object,
`"egg"` back to `WhimlingState.EGG`, and validates all field constraints.

### Decision 6: `pathlib.Path` over string paths

```python
# Old way:
import os
path = os.path.join("data", "whimling.json")

# Modern way:
from pathlib import Path
SAVE_FILE = Path("data") / "whimling.json"
```

`pathlib` is object-oriented, readable, and OS-independent. Methods like
`path.exists()`, `path.read_text()`, `path.write_text()` make file I/O clean.

---

## Concepts Covered

| Concept | Where It Appears | Why It Matters |
|---------|-----------------|----------------|
| Pydantic `BaseModel` | `whimling.py` | Automatic validation, serialisation |
| `Field(ge=0, le=100)` | `Egg` model | Constraints enforced at the data layer |
| `StrEnum` | `WhimlingState` | Type-safe string enums for JSON |
| `default_factory` | `Whimling` fields | Safe mutable defaults |
| `model_dump(mode="json")` | `egg.py` / `save_whimling` | Python → JSON |
| `model_validate()` | `egg.py` / `load_whimling` | JSON → Python |
| `pathlib.Path` | `egg.py` | Modern file path handling |
| `sys.argv` | `main.py` | Raw CLI argument parsing |
| Dispatch table | `main.py` / `COMMANDS` dict | Clean command routing |
| `sys.exit(code)` | `main.py` | Proper shell exit codes |
| `FileNotFoundError` / `FileExistsError` | `egg.py` + `main.py` | Built-in exception types |

---

## The `data/whimling.json` Format

Every field maps directly to a Pydantic model field.

```json
{
  "name": "Zephyr",
  "state": "egg",
  "created_at": "2026-06-17T14:48:53.133886Z",
  "age_days": 0.0,
  "egg": {
    "warmth": 0,
    "cracks": 0,
    "is_hatched": false
  }
}
```

This file is gitignored (listed in `.gitignore` under `data/`). It's local-only save data.

---

## Things to Experiment With

These are hands-on exercises to solidify the concepts before moving on:

1. **Break the validator intentionally:**
   ```python
   # Run this in a Python shell (uv run python)
   from app.models.whimling import Egg
   Egg(warmth=200)  # Should raise ValidationError — warmth max is 100
   ```

2. **Inspect what `model_dump` gives:**
   ```python
   from app.models.whimling import Whimling
   w = Whimling(name="Test")
   print(w.model_dump())           # Python-native types
   print(w.model_dump(mode="json")) # JSON-safe types — see the difference
   ```

3. **Manually edit the save file** and reload it:
   ```bash
   # Edit data/whimling.json — change "state" to "invalid_state"
   uv run python main.py status
   # Should raise a ValidationError from model_validate()
   ```

4. **Try creating a second egg** (should be blocked):
   ```bash
   uv run python main.py create Another
   # Should print: ❌  A Whimling already exists!
   ```

---

## What Milestone 1 Builds On This

Milestone 1 (Hatching) adds:
- `warm_egg()` handler in `src/app/handlers/egg.py` — modifies and saves the existing Whimling
- `python main.py warm` command in `main.py`
- A state machine: `egg → hatchling` when conditions are met
- Introduction to `random` module (warmth increases by a random amount)

The existing `save_whimling()` / `load_whimling()` functions will be reused unchanged.
The `Egg` model fields (`warmth`, `cracks`, `is_hatched`) were already designed for this.

---

## Ruff / Lint Notes (Lessons Learned)

During implementation, ruff caught 5 issues. Each was a learning point:

| Rule | Issue | Fix |
|------|-------|-----|
| `UP042` | `class X(str, Enum)` — use `StrEnum` | `from enum import StrEnum; class X(StrEnum)` |
| `UP017` | `timezone.utc` — use `datetime.UTC` | `from datetime import UTC; datetime.now(UTC)` |
| `F401` | Imported `whimling_exists` but never used | Remove it from the import |
| `F541` | `f"plain string"` — f-prefix with no `{}` | Remove the `f` prefix |
| `I001` | Import block not sorted | `ruff check --fix` auto-fixed this |

The `datetime.UTC` fix also revealed a subtlety: `UTC` is a **module-level constant**,
not a class attribute. `from datetime import datetime; datetime.UTC` → `AttributeError`.
The correct import: `from datetime import UTC, datetime`.

