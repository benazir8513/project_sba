"""
Whimling models — the data layer.

LEARNING NOTE — what this file teaches:
  - Pydantic v2: how to define data models with validation built in
  - Python Enums: how to represent a fixed set of string values safely
  - Field constraints: ge/le enforce value ranges at the model level so
    no other code ever has to check "is hunger between 0 and 100?"
  - default_factory: why you must use a factory for mutable defaults
    (datetime.now, Egg()) instead of a plain default value

ARCHITECTURE NOTE:
  This file is the *only* place that defines what a Whimling IS.
  It has no imports from handlers/ or infrastructure/ — it knows nothing
  about how data is saved or what the CLI does. This is intentional.
  The rule: models flow in one direction only — handlers import models,
  not the other way around.
"""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class WhimlingState(StrEnum):
    """
    All possible lifecycle states of a Whimling.

    StrEnum (Python 3.11+) replaces the old `(str, Enum)` pattern.
    It achieves the same thing — values are plain strings — but more explicitly.
    WhimlingState.EGG == "egg"  → True
    JSON serialisation gives "egg" not "<WhimlingState.EGG: 'egg'>"
    """

    EGG = "egg"
    HATCHLING = "hatchling"
    JUVENILE = "juvenile"
    ADULT = "adult"
    ELDER = "elder"
    DORMANT = "dormant"  # Not dead — mystical creatures never die, they sleep


class Egg(BaseModel):
    """
    The physical state of the egg before it hatches.

    Field constraints:
      ge=0  → greater than or equal to 0  (no negative warmth)
      le=100 → less than or equal to 100  (warmth can't exceed 100)
    Pydantic raises a ValidationError immediately if you violate these.
    """

    warmth: int = Field(default=0, ge=0, le=100)
    cracks: int = Field(default=0, ge=0, le=10)
    is_hatched: bool = False


class Whimling(BaseModel):
    """
    The core creature model. Represents the Whimling at every stage of its life.

    WHY default_factory and not a plain default?
      Bad:   created_at: datetime = datetime.now(timezone.utc)
        → datetime.now() runs ONCE at class definition time (import time).
          Every Whimling would share the exact same timestamp.
      Good:  created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
        → The lambda runs each time a new Whimling() is created.

    Same logic applies to `egg: Egg = Field(default_factory=Egg)`.
    Without default_factory, all Whimlings would share one Egg object —
    mutating one would mutate all of them.
    """

    name: str
    state: WhimlingState = WhimlingState.EGG
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    age_days: float = 0.0
    egg: Egg = Field(default_factory=Egg)




