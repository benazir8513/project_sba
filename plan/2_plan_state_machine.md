# State Machine Pattern — Deep Dive

> **Purpose:** This document teaches the state machine pattern progressively,
> showing how it evolves across the project's milestones. Read this after
> completing Milestone 1 (Hatching) — you've already built a minimal FSM.

---

## Part 1 — What Is a Finite State Machine (FSM)?

A **finite state machine** is a model of computation with:

1. **A finite set of states** — the system can be in *exactly one* at any time
2. **An initial state** — where the system starts
3. **Events (inputs/triggers)** — things that happen to the system
4. **Transitions** — rules: "if in state S, and event E occurs, move to state S'"
5. **Guards (optional)** — conditions that must be true for a transition to fire
6. **Actions (optional)** — side effects that run when a transition fires

### Why programmers care

State machines appear *everywhere*:

| Domain | States | Events |
|--------|--------|--------|
| HTTP connection | idle, connecting, open, closing, closed | connect, data, close, timeout |
| Order processing | pending, paid, shipped, delivered, refunded | pay, ship, deliver, refund |
| UI button | default, hover, pressed, disabled | mouseEnter, mouseDown, click, disable |
| Game character | idle, running, jumping, attacking, dead | move, jump, attack, damage |
| Your Whimling | egg, hatchling, juvenile, adult, elder, dormant | warm, feed, play, rest, tick |

Without a state machine, you end up with tangled `if/elif/else` chains spread across
many functions. With one, all transition rules live in a single, testable, documentable
place.

---

## Part 2 — The Three Levels of Implementation

State machines can be implemented with increasing sophistication. Each level is
appropriate at different project sizes.

---

### Level 1: Guard Clauses (What you have now — Milestone 1)

The simplest form: each handler checks the current state at the top and raises if
the transition isn't allowed.

```python
def warm_egg(whimling: Whimling) -> Whimling:
    if whimling.state != WhimlingState.EGG:
        raise ValueError("Can only warm an egg")
    # ... do the warming logic ...
    if should_hatch:
        return whimling.model_copy(update={"state": WhimlingState.HATCHLING})
    return whimling
```

**Pros:** Minimal code, easy to understand, no extra abstractions.
**Cons:** Transition rules are scattered across many handler functions. Hard to answer
"what transitions are possible from state X?" without reading all handlers.

**When it's enough:** ≤ 3 states, ≤ 5 events. (Milestones 0–1.)

---

### Level 2: Transition Table (Recommended for Milestones 2–4)

A centralised data structure that defines *all* allowed transitions in one place.
Handlers consult the table before acting.

```python
# src/app/handlers/transitions.py

from app.models.whimling import WhimlingState

# Format: (current_state, event) → allowed target state(s)
# If a (state, event) pair is missing → that event is illegal in that state.

ALLOWED_TRANSITIONS: dict[tuple[WhimlingState, str], set[WhimlingState]] = {
    # Milestone 1
    (WhimlingState.EGG, "warm"):       {WhimlingState.EGG, WhimlingState.HATCHLING},

    # Milestone 2 — care actions only work on living Whimlings
    (WhimlingState.HATCHLING, "feed"):  {WhimlingState.HATCHLING},
    (WhimlingState.HATCHLING, "play"):  {WhimlingState.HATCHLING},
    (WhimlingState.HATCHLING, "rest"):  {WhimlingState.HATCHLING},
    (WhimlingState.HATCHLING, "tick"):  {WhimlingState.HATCHLING, WhimlingState.DORMANT},

    # Milestone 2 — dormant recovery
    (WhimlingState.DORMANT, "revive"):  {WhimlingState.HATCHLING},

    # Milestone 4 — evolution (hatchling can become juvenile, etc.)
    (WhimlingState.HATCHLING, "evolve"): {WhimlingState.JUVENILE},
    (WhimlingState.JUVENILE, "feed"):    {WhimlingState.JUVENILE},
    (WhimlingState.JUVENILE, "play"):    {WhimlingState.JUVENILE},
    (WhimlingState.JUVENILE, "rest"):    {WhimlingState.JUVENILE},
    (WhimlingState.JUVENILE, "tick"):    {WhimlingState.JUVENILE, WhimlingState.DORMANT},
    (WhimlingState.JUVENILE, "evolve"):  {WhimlingState.ADULT},
    # ... and so on
}


def validate_transition(current: WhimlingState, event: str, target: WhimlingState) -> None:
    """
    Raise ValueError if the proposed transition is not in the table.

    Call this at the start of any handler that changes state:
        validate_transition(whimling.state, "warm", WhimlingState.HATCHLING)
    """
    key = (current, event)
    allowed = ALLOWED_TRANSITIONS.get(key)
    if allowed is None:
        raise ValueError(
            f"Event '{event}' is not valid when Whimling is in state '{current.value}'. "
            f"No transitions defined for ({current.value}, {event})."
        )
    if target not in allowed:
        raise ValueError(
            f"Transition ({current.value}) --[{event}]--> ({target.value}) is not allowed. "
            f"Valid targets: {[s.value for s in allowed]}"
        )
```

**Pros:**
- One file answers "what can happen from any state?"
- Easy to unit test exhaustively (loop over all entries)
- Easy to visualise (generate a diagram from the dict)
- Handlers stay focused on *what* to do, not *whether* it's allowed

**Cons:** Slightly more code upfront. Overkill for 2 states.

**When to adopt:** As soon as you have > 3 states or > 5 events. That's Milestone 2.

---

### Level 3: FSM Class / Library (Optional — Milestone 4+ or bonus)

A dedicated class that owns state and exposes `trigger(event)` as the only mutation
method. Can be hand-rolled or use the `transitions` library.

#### Hand-rolled (educational)

```python
from dataclasses import dataclass, field
from typing import Callable, Optional

@dataclass
class Transition:
    source: str
    event: str
    target: str
    guard: Optional[Callable[[], bool]] = None
    action: Optional[Callable[[], None]] = None

@dataclass
class StateMachine:
    state: str
    transitions: list[Transition] = field(default_factory=list)

    def trigger(self, event: str) -> None:
        for t in self.transitions:
            if t.source == self.state and t.event == event:
                if t.guard and not t.guard():
                    raise ValueError(f"Guard failed for {event}")
                if t.action:
                    t.action()
                self.state = t.target
                return
        raise ValueError(f"No transition for event '{event}' in state '{self.state}'")
```

#### Using the `transitions` library

```bash
uv add transitions
```

```python
from transitions import Machine

class WhimlingFSM:
    pass

states = ["egg", "hatchling", "juvenile", "adult", "elder", "dormant"]
transitions = [
    {"trigger": "warm",   "source": "egg",       "dest": "egg",       "conditions": "not_ready_to_hatch"},
    {"trigger": "warm",   "source": "egg",       "dest": "hatchling", "conditions": "ready_to_hatch"},
    {"trigger": "feed",   "source": "hatchling", "dest": "hatchling"},
    {"trigger": "tick",   "source": "hatchling", "dest": "dormant",   "conditions": "health_is_zero"},
    {"trigger": "revive", "source": "dormant",   "dest": "hatchling"},
    {"trigger": "evolve", "source": "hatchling", "dest": "juvenile",  "conditions": "evolution_ready"},
    # ...
]

fsm = WhimlingFSM()
machine = Machine(model=fsm, states=states, transitions=transitions, initial="egg")
fsm.warm()  # triggers the "warm" event
```

**Pros:** Callbacks (`on_enter_hatchling`, `on_exit_egg`), auto-generated diagrams,
battle-tested edge-case handling.
**Cons:** External dependency, learning curve, may feel like overkill for a learning project.

**Recommendation:** Build Level 2 by hand first so you truly understand it. Then
optionally try the library as a bonus exercise to see how a production FSM works.

---

## Part 3 — How State Machines Evolve Across Your Milestones

| Milestone | New States | New Events | FSM Level |
|-----------|-----------|------------|-----------|
| 0 | `egg` | `create` | — (no transitions yet) |
| 1 | `hatchling` | `warm` | Level 1 (guard clause) |
| 2 | `dormant` | `feed`, `play`, `rest`, `tick`, `revive` | **Level 2 (transition table)** |
| 4 | `juvenile`, `adult`, `elder` | `evolve` | Level 2 (extended table) |
| 9 | — | `use_ability` (per-state ability access) | Level 2 (abilities gated by state) |
| 11 | — | background `tick` (concurrent) | Level 2 + locking concerns |

### Milestone 2 action item

When you implement Milestone 2, **create `src/app/handlers/transitions.py`** with the
transition table (Level 2). Every new handler (`feed`, `play`, `rest`, `tick`) should
call `validate_transition()` before making changes. This single file becomes the
"source of truth" for what's allowed.

### Milestone 4 action item

Extend the transition table with evolution stages. Add a helper:

```python
def get_valid_events(state: WhimlingState) -> list[str]:
    """Return all events that are valid in the given state."""
    return [event for (s, event) in ALLOWED_TRANSITIONS if s == state]
```

Use this in the CLI `status` command to show the user what they can do next.

---

## Part 4 — State Machine Diagram (Your Whimling's Full Lifecycle)

```
                          warm (warmth < 80)
                              ↙
    ┌─────────┐   warm    ┌─────────────┐   evolve   ┌──────────┐
    │   EGG   │ ────────▶ │  HATCHLING  │ ─────────▶ │ JUVENILE │
    └─────────┘ (cracks≥10)└─────────────┘            └──────────┘
                                │    ▲                      │
                           tick │    │ revive          evolve│
                          (hp=0)│    │                      ▼
                                ▼    │                ┌──────────┐
                          ┌──────────┐   evolve      │  ADULT   │
                          │ DORMANT  │◀──────────────┐└──────────┘
                          └──────────┘  (from any     │     │
                                ▲        living state  │evolve│
                                │        when hp = 0)  │     ▼
                                │                     ┌──────────┐
                                └─────────────────────│  ELDER   │
                                     tick (hp=0)      └──────────┘
```

Key rules visible from the diagram:
- `EGG` can only transition to `HATCHLING` (via `warm`)
- Any living state can fall to `DORMANT` (via `tick` when health = 0)
- `DORMANT` can only recover to the state it fell from (via `revive`)
- Evolution is one-way: hatchling → juvenile → adult → elder (never backwards)
- You cannot feed/play/rest an egg or a dormant Whimling

---

## Part 5 — Hands-On Exercise (Do This Now)

Before moving to Milestone 2, try this small exercise to solidify the concept:

### Exercise: Draw out the transition table by hand

Open a Python shell and verify which events are legal in each state:

```bash
uv run python
```

```python
from app.models.whimling import WhimlingState

# Define the transitions you THINK should be allowed:
transitions = {
    (WhimlingState.EGG, "warm"): {WhimlingState.EGG, WhimlingState.HATCHLING},
    (WhimlingState.EGG, "feed"): None,  # Should this be allowed? (No!)
    (WhimlingState.HATCHLING, "warm"): None,  # Should this be allowed? (No!)
    (WhimlingState.HATCHLING, "feed"): {WhimlingState.HATCHLING},
}

# Now test: what happens if you try to warm a hatchling?
from app.handlers.egg import warm_egg, save_whimling, load_whimling
from app.models.whimling import Whimling, Egg

# Create a hatchling manually:
w = Whimling(name="Test", state=WhimlingState.HATCHLING, egg=Egg(warmth=100, cracks=10, is_hatched=True))
save_whimling(w)

# Try warming it:
try:
    warm_egg()
except ValueError as e:
    print(f"Guard caught it: {e}")
# ✅ The guard clause is your Level 1 state machine in action
```

### Exercise: Think about illegal states

Ask yourself: can the system ever reach a state where `is_hatched=True` but
`state=EGG`? If yes, you have a bug. If no, what prevents it?

Answer: the logic in `warm_egg()` always sets both together atomically:
```python
is_hatched = new_cracks >= 10
new_state = WhimlingState.HATCHLING if is_hatched else WhimlingState.EGG
```

This is the key insight: **a state machine prevents impossible combinations** by
ensuring state changes happen through controlled transitions, not ad-hoc field mutations.

---

## Part 6 — Vocabulary Reference

| Term | Meaning | Your Code |
|------|---------|-----------|
| **State** | A named condition the system is in | `WhimlingState.EGG` |
| **Event / Trigger** | An input that may cause a transition | Calling `warm_egg()` |
| **Transition** | A state change: (source, event) → target | `EGG --[warm]--> HATCHLING` |
| **Guard** | A boolean condition that must hold for a transition to fire | `if whimling.state != EGG: raise` |
| **Action** | A side effect that runs during a transition | `save_whimling(updated)` |
| **Deterministic** | One event in one state always leads to the same target | Your FSM is deterministic |
| **Non-deterministic** | One event could lead to multiple targets (based on guards) | `warm` stays in EGG or goes to HATCHLING depending on cracks |
| **Transition table** | A data structure listing all (state, event) → target mappings | `ALLOWED_TRANSITIONS` dict |
| **Impossible state** | A combination of fields that should never exist | `is_hatched=True, state=EGG` |
| **Dead state / sink** | A state with no outgoing transitions | `DORMANT` without `revive` would be one |

---

## Part 7 — Real-World Examples

### Example A: HTTP Request Lifecycle

```
IDLE --[send]--> PENDING --[response]--> DONE
                    │
                    └──[timeout]──> FAILED
                    └──[cancel]───> CANCELLED
```

Guards: can't `cancel` a request that's already `DONE`.

### Example B: Git Branch (simplified)

```
CLEAN --[edit file]--> DIRTY --[git add]--> STAGED --[git commit]--> CLEAN
         │                                      │
         └──[git checkout -- file]──> CLEAN     └──[git reset]──> DIRTY
```

### Example C: Traffic Light

```
RED --[timer]--> GREEN --[timer]--> YELLOW --[timer]--> RED
```

No guards needed — purely time-driven. But you still can't go GREEN → RED directly.

---

## Summary

- **Milestone 1** gave you Level 1 (guard clauses). That's real, it works, and it's
  appropriate for 2 states.
- **Milestone 2** is where you should introduce Level 2 (a transition table in
  `src/app/handlers/transitions.py`). You'll have 3 states (EGG, HATCHLING, DORMANT)
  and 6+ events. A table keeps things manageable.
- **Milestone 4** extends the table with evolution stages. The table grows but the
  pattern stays the same.
- **Level 3** (library or hand-rolled class) is optional. Try it as a bonus if you're
  curious — it's genuinely useful in production code with complex lifecycles.

The core lesson: **a state machine is a design tool that makes impossible states
impossible and documents all valid behavior in one place.**

