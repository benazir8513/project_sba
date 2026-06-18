"""
main.py — CLI entrypoint for Project SBA: The Grimoire of a Living Creature.

LEARNING NOTE — what this file teaches:
  - sys.argv: the raw list of strings the user typed on the command line.
      sys.argv[0] → always the script name ("main.py")
      sys.argv[1:] → everything the user typed after it
  - Dispatch table pattern: instead of a long if/elif/elif chain, a dict
    maps command name → function. Adding a new command means adding one
    dict entry and one function — nothing else changes.
  - sys.exit(code): exit code 0 = success, non-zero = error. The shell
    uses this. `make` uses this. CI systems use this. Always be explicit.

HOW TO RUN:
  uv run python main.py <command> [args]

CURRENT COMMANDS (Milestone 0):
  create [name]  — Create a new egg (default name: Lumis)
  status         — Show the current state of your Whimling

FUTURE COMMANDS will be added here as milestones progress.
In Milestone 7, this whole file gets replaced with a `typer` CLI,
but the dispatch pattern here teaches you what frameworks do under the hood.
"""

import sys
from collections.abc import Callable

from app.handlers.egg import create_egg, load_whimling
from app.models.whimling import Whimling

# ---------------------------------------------------------------------------
# Command implementations
# ---------------------------------------------------------------------------


def cmd_create(args: list[str]) -> None:
    """Create a new Whimling egg. Optionally pass a name as the first argument."""
    name: str = args[0] if args else "Lumis"
    try:
        whimling: Whimling = create_egg(name)
        print(f"\n🥚  A new egg has appeared — {whimling.name} has entered the world.\n")
        print(f"   State   : {whimling.state.value}")
        print(f"   Warmth  : {whimling.egg.warmth}/100")
        print(f"   Cracks  : {whimling.egg.cracks}/10")
        print(f"   Created : {whimling.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("\n   Run `python main.py warm` to start warming the egg.\n")
    except FileExistsError as e:
        print(f"\n❌  {e}\n")
        sys.exit(1)


def cmd_status(args: list[str]) -> None:
    """Print the current state of the Whimling."""
    # args is unused for now — kept for consistency with the dispatch signature
    _ = args
    try:
        w: Whimling = load_whimling()
    except FileNotFoundError as e:
        print(f"\n❌  {e}\n")
        sys.exit(1)

    print(f"\n✨  {w.name}")
    print(f"   State   : {w.state.value}")
    if w.state == w.state.EGG:
        print(f"   Warmth  : {w.egg.warmth}/100")
        print(f"   Cracks  : {w.egg.cracks}/10")
        print(f"   Hatched : {w.egg.is_hatched}")
    print(f"   Age     : {w.age_days:.1f} days")
    print(f"   Born    : {w.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")


# ---------------------------------------------------------------------------
# Dispatch table — maps command name → handler function
# Every function has the same signature: (args: list[str]) -> None
# ---------------------------------------------------------------------------
COMMANDS: dict[str, Callable[[list[str]], None]] = {
    "create": cmd_create,
    "status": cmd_status,
}

USAGE = """
Usage: python main.py <command> [args]

Commands:
  create [name]   Create a new egg (default name: Lumis)
  status          Show the current state of your Whimling
""".strip()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    args: list[str] = sys.argv[1:]  # Drop the script name at index 0

    if not args:
        print(f"\n{USAGE}\n")
        sys.exit(0)

    command: str
    rest: list[str]
    command, *rest = args  # Unpack: first item is the command, rest are its args

    if command not in COMMANDS:
        print(f"\n❌  Unknown command: '{command}'\n\n{USAGE}\n")
        sys.exit(1)

    COMMANDS[command](rest)


if __name__ == "__main__":
    main()
