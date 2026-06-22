# Milestone 1 — Hatching 🐣

**Status:** ✅ Complete
**Completed:** 2026-06-19
**Concepts:** State machines, `random`, tuple unpacking, `model_copy`, clamping with `min()`/`max()`, guard clauses

---

## What Was Built

The egg can now be warmed until it hatches. Repeated `warm` calls increase warmth; once
warmth hits 80 cracks appear; once cracks hit 10 the Whimling transitions to `hatchling` state.

```bash
uv run python main.py create Zephyr   # Start fresh
uv run python main.py warm            # Repeat ~14 times
uv run python main.py status          # See your newborn Whimling
```

---

## Files Created / Modified

| File | Change | What It Is |
|------|--------|-----------|
| `src/app/handlers/egg.py` | Added `warm_egg()` + `import random` | Business logic for warming/hatching |
| `main.py` | Added `cmd_warm()`, updated `cmd_status()`, added `"warm"` to dispatch table | CLI entrypoint |
| `milestones/milestone_1.md` | Created | This file |

---

## The Full `warm_egg()` Logic

```
call warm_egg()
   │
   ├─ load_whimling() from disk
   │
   ├─ Guard: is state == EGG? → if not, raise ValueError
   │
   ├─ warmth_gained = random.randint(5, 15)
   ├─ new_warmth    = min(old_warmth + warmth_gained, 100)   ← clamp to 100
   │
   ├─ if new_warmth >= 80:
   │     new_cracks = min(old_cracks + 1, 10)               ← clamp to 10
   │
   ├─ if new_cracks >= 10:
   │     is_hatched = True
   │     new_state  = HATCHLING
   │
   ├─ Build updated Egg + Whimling via model_copy(update={...})
   │
   ├─ save_whimling(updated)
   │
   └─ return (updated_whimling, warmth_gained, just_hatched)
```

---

## Key Concepts & Decisions

### Concept 1: State Machine (simple version)

A **state machine** is a model of a system that can be in exactly one of a finite set
of states at any time, with well-defined rules for which transitions are allowed.

```
     warm (warmth < 80)
         ↙
   ┌───────────┐      warm (cracks >= 10)    ┌────────────┐
   │    EGG    │  ─────────────────────────▶ │ HATCHLING  │
   └───────────┘                             └────────────┘
         ↖
     warm (warmth >= 80, cracks++)
```

The guard clause at the top of `warm_egg()` enforces the machine:

```python
if whimling.state != WhimlingState.EGG:
    raise ValueError(...)
```

Without guards, you could call `warm_egg()` on a hatchling — that makes no sense in the
game world. Guards make impossible states actually impossible in code.

> 📖 **Deep dive:** See [`plan/2_plan_state_machine.md`](../plan/2_plan_state_machine.md)
> for the full state machine pattern — three levels of implementation (guard clauses →
> transition table → FSM class/library), a lifecycle diagram of all Whimling states,
> and hands-on exercises. The transition table (Level 2) is introduced in Milestone 2
> when the `dormant` state and multiple events (feed/play/rest/tick) make guards alone
> insufficient.

---

### Concept 2: `random.randint(a, b)` — both ends inclusive

```python
import random
random.randint(5, 15)  # could return 5, 6, 7, …, 14, or 15
```

This is **unlike** `range(5, 15)` which excludes the upper bound (returns 5–14).
`randint` is inclusive on both ends. Always double-check which you need.

---

### Concept 3: Clamping with `min()` / `max()`

When you have a value with a legal range (0–100), you clamp it after every mutation:

```python
# Don't let warmth exceed 100:
new_warmth = min(old_warmth + gained, 100)

# Don't let cracks exceed 10:
new_cracks = min(old_cracks + 1, 10)

# General pattern:
clamped = max(lower_bound, min(value, upper_bound))
```

Clamping at the *handler* level means the Pydantic model's `ge`/`le` constraints act
as a safety net, not the first line of defence. If you somehow passed `warmth=200` to
the `Egg` model, Pydantic would catch it — but by clamping first you never get there.

---

### Concept 4: `model_copy(update={...})` — immutable-friendly updates

```python
# ❌ Direct mutation — bypasses Pydantic validation:
whimling.state = WhimlingState.HATCHLING   # Works, but no validation run

# ✅ model_copy — produces a new instance, runs validation:
updated = whimling.model_copy(update={"state": WhimlingState.HATCHLING})
```

`model_copy` leaves the original object untouched and gives you a validated new one.
This is especially important if you ever pass the original object elsewhere — you don't
want to surprise callers with a mutated object.

Note: for the nested `Egg`, you need to pass a *new* `Egg` object, not a dict:

```python
new_egg = Egg(warmth=new_warmth, cracks=new_cracks, is_hatched=True)
updated = whimling.model_copy(update={"egg": new_egg, "state": WhimlingState.HATCHLING})
```

---

### Concept 5: Returning a tuple — multiple return values

```python
def warm_egg() -> tuple[Whimling, int, bool]:
    ...
    return updated, warmth_gained, just_hatched
```

Python functions can return multiple values packed as a tuple. The caller unpacks them:

```python
w, gained, just_hatched = warm_egg()
```

This is cleaner than a dict (`{"whimling": ..., "gained": ...}`) for small, stable
return shapes. Use a dataclass or dict when you have more than ~3 values.

---

### Concept 6: Guard clauses — fail fast, fail clearly

```python
def warm_egg() -> ...:
    whimling = load_whimling()
    if whimling.state != WhimlingState.EGG:  # ← guard clause
        raise ValueError(...)
    # ... happy path continues below
```

A **guard clause** is an early return (or raise) that handles an invalid condition at
the top of the function. The alternative — wrapping everything in `if/else` — makes the
happy path deeply nested and hard to read. Guards keep the happy path flat.

---

## Concepts Covered

| Concept | Where It Appears | Why It Matters |
|---------|-----------------|----------------|
| State machine | `warm_egg()` guard + state transition | Enforces valid transitions; prevents impossible states |
| `random.randint(a, b)` | warmth increase | Inclusive on both ends; introduces non-determinism |
| `min()` / `max()` clamping | warmth and cracks | Keep values within legal range before model sees them |
| `model_copy(update={...})` | building `updated` Whimling | Safe, validated field updates without direct mutation |
| Tuple return values | `warm_egg()` return | Multiple return values; clean caller unpacking |
| Guard clauses | top of `warm_egg()` | Fail fast, flat happy path, clear error messages |
| `ValueError` | guard raise | Right exception for "invalid argument/state" errors |

---

## What the Data Looks Like After Hatching

```json
{
  "name": "Zephyr",
  "state": "hatchling",
  "created_at": "2026-06-19T07:01:16.000000Z",
  "age_days": 0.0,
  "egg": {
    "warmth": 100,
    "cracks": 10,
    "is_hatched": true
  }
}
```

The `egg` sub-object is kept even after hatching — it's a historical record. In
Milestone 2, the `Stats` model (hunger, happiness, energy, health) will be added
alongside it.

---

## Things to Experiment With

1. **Verify the guard works:**
   ```bash
   # After hatching, try to warm again — should print a warning:
   uv run python main.py warm
   # ⚠️   Zephyr is already a hatchling — there's nothing to warm anymore!
   ```

2. **Inspect randomness:**
   ```python
   # In a Python shell (uv run python):
   import random
   [random.randint(5, 15) for _ in range(10)]  # See the spread
   ```

3. **Try model_copy yourself:**
   ```python
   from app.models.whimling import Whimling, Egg, WhimlingState
   w = Whimling(name="Test")
   print(w.state)               # egg
   w2 = w.model_copy(update={"state": WhimlingState.HATCHLING})
   print(w.state, w2.state)     # egg  hatchling — original untouched!
   ```

4. **Break the clamping intentionally** (to understand why it's needed):
   ```python
   from app.models.whimling import Egg
   Egg(warmth=101)  # ValidationError — Pydantic catches it
   Egg(warmth=min(101, 100))  # Works — clamping prevents the error
   ```

---

## What Milestone 2 Builds On This

Milestone 2 (Vital Signs) adds:
- A `Stats` model (`hunger`, `happiness`, `energy`, `health`) to `whimling.py`
- The `Whimling` model gets a `stats: Stats` field (only populated post-hatch)
- Handlers: `feed()`, `play()`, `rest()`, and a `tick()` time-passage function
- All new CLI commands: `python main.py feed`, `play`, `rest`
- The `status` command will show stats when the Whimling is a hatchling or beyond

The existing `save_whimling()` / `load_whimling()` continue to work unchanged.

