# 🥚 Project SBA — The Grimoire of a Living Creature

> **A personal Python learning project disguised as a mystical pet simulator.**
>
> You are the **Caretaker** — a programmer who discovers a strange, glowing egg. Your job is to bring it to life, nurture it, evolve it, and build an entire world around it — one feature at a time. Every feature you implement teaches you a real backend/programming concept. The creature grows as you grow.

---

## 📖 The Story

You've found an **egg** — pulsing with faint light, humming with something alive inside. It's not from this world. No manual, no instructions. Just you and the egg.

Your creature is a **Whimling** — a shapeless, ever-evolving mystical being that starts as pure potential. It has no fixed form. As you (the programmer) implement features, the Whimling grows, learns, develops personality, gains abilities, and eventually... becomes something truly unique.

**The Whimling cannot exist without your code. You are not playing a game — you are building its reality.**

---

## 🎯 Project Philosophy

- **Learn by building.** Every feature maps to a real programming or backend concept.
- **Work at your own pace.** Features are small, independent, and designed to be picked up every ~2 weeks.
- **Everything is local.** No cloud, no costs, no accounts. Just Python on your machine.
- **Tech-agnostic core.** The business logic doesn't care if you use SQLite, JSON files, or MongoDB. Swap storage, swap interfaces — the Whimling doesn't care.
- **Extend forever.** The project is designed so you can always add "one more thing."

---

## 🧱 Architecture Principle

The project follows a **layered architecture** to keep things clean and extensible:

```
src/
├── app/
│   ├── models/          # Pure data: what things ARE (no logic, no I/O)
│   ├── handlers/        # Use cases: what the system DOES (business logic)
│   ├── infrastructure/  # How things are STORED/RETRIEVED (persistence)
│   │   ├── database/    # DB connection and setup
│   │   └── repositories/# Data access layer (read/write operations)
│   └── cli/             # How the user INTERACTS (CLI commands — added later)
```

**The rule:** Models know nothing. Handlers know models. Repositories know models + database. CLI knows handlers. Nothing flows backwards.

This means you can swap **how** data is stored (JSON file → SQLite → MongoDB) without touching your business logic. And you can swap **how** users interact (CLI → API → GUI) without touching storage.

---

## 🗺️ Feature Roadmap

Each milestone is a self-contained unit of work. They build on each other but each one is completable in 1–2 sessions.

---

### Milestone 0 — The Egg Exists 🥚
**Concept: Project setup, data modeling, serialization**

The most basic thing: the egg exists as data.

| # | Task | What You Learn |
|---|------|---------------|
| 0.1 | Create a `Whimling` model using Pydantic — fields: `name`, `state` (egg/hatched/...), `created_at`, `age_days` | Pydantic models, data validation, type hints |
| 0.2 | Create an `Egg` model with fields: `warmth` (0–100), `cracks` (0–10), `is_hatched` (bool) | Nested models, field validators, constrained types |
| 0.3 | Write a handler function `create_egg()` that returns a new Whimling in egg state | Functions, return types, basic business logic |
| 0.4 | Serialize the egg to a JSON file and load it back | File I/O, JSON serialization, Pydantic's `.model_dump()` / `.model_validate()` |
| 0.5 | Write a simple `main.py` entrypoint: `python main.py create` creates an egg and saves it | Argument parsing (`sys.argv`), entrypoints |

**End result:** You can run `python main.py create` and a JSON file appears with your egg's data. The Whimling exists.

---

### Milestone 1 — Hatching 🐣
**Concept: State machines, business rules, time simulation**

The egg won't hatch on its own. You need to warm it. Each interaction nudges it closer to hatching.

| # | Task | What You Learn |
|---|------|---------------|
| 1.1 | Implement a `warm_egg()` handler — increases `warmth` by a random amount (5–15), loads/saves from file | Randomness, file read-modify-write, pure functions vs side effects |
| 1.2 | When `warmth >= 80`, auto-increment `cracks` by 1 each time `warm_egg()` is called | Conditional logic, state transitions |
| 1.3 | When `cracks >= 10`, set `is_hatched = True` and transition the Whimling from `egg` to `hatchling` state | State machine pattern (simple version) |
| 1.4 | Add `python main.py warm` command to warm the egg | Extending CLI, dispatching commands |
| 1.5 | Add `python main.py status` command to pretty-print the current state of the Whimling | String formatting, display logic separated from data |

**End result:** You repeatedly run `python main.py warm` until the egg hatches. Then `status` shows your newborn Whimling.

---

### Milestone 2 — Vital Signs 💓
**Concept: Multiple interacting attributes, decay over time, data integrity**

A hatched Whimling has needs. If you ignore them, they decline.

| # | Task | What You Learn |
|---|------|---------------|
| 2.1 | Add `Stats` model: `hunger` (0–100), `happiness` (0–100), `energy` (0–100), `health` (0–100) | Complex nested models, default values |
| 2.2 | Implement `feed()` handler — increases `hunger` satisfaction, slight happiness boost | Business logic with multiple side effects |
| 2.3 | Implement `play()` handler — increases `happiness`, decreases `energy` | Trade-off mechanics, clamping values (min/max) |
| 2.4 | Implement `rest()` handler — restores `energy`, time passes, hunger decreases | Simulating time passage |
| 2.5 | Implement `tick()` — a "time passes" function that decays all stats slightly. Called automatically before every command | Middleware-like pattern, decorators or pre-hooks |
| 2.6 | If `health` reaches 0, the Whimling enters `dormant` state (not dead — mystical creatures don't die, they sleep until revived) | Edge cases, guard clauses, graceful failure states |

**End result:** A living creature with needs. Neglect it for two weeks and come back to find it dormant. Take care of it and it thrives.

---

### Milestone 3 — Persistence Layer Swap 🗄️
**Concept: Repository pattern, dependency inversion, abstraction**

Right now you're saving to JSON files. Time to learn why abstraction matters — by making storage swappable.

| # | Task | What You Learn |
|---|------|---------------|
| 3.1 | Define a `WhimlingRepository` protocol (abstract interface) with methods: `save()`, `load()`, `exists()` | Python Protocols, abstract interfaces, type contracts |
| 3.2 | Implement `JsonFileRepository` that fulfills this protocol (move existing JSON logic here) | Refactoring, separation of concerns |
| 3.3 | Update all handlers to accept a repository parameter instead of doing file I/O directly | Dependency injection (manual), inversion of control |
| 3.4 | Implement `SqliteRepository` as a second backend using Python's built-in `sqlite3` | SQL basics, learning a new storage backend |
| 3.5 | Add a config option (env var or config file) to choose which repository to use | Configuration management, environment variables |

**End result:** Same game, same commands, but now you can flip between JSON and SQLite storage with a single config change. Your handlers don't know or care which one is active.

---

### Milestone 4 — Evolution 🦋
**Concept: Polymorphism, enums, strategy pattern**

The Whimling evolves based on how you've been treating it. Different care patterns → different evolutions.

| # | Task | What You Learn |
|---|------|---------------|
| 4.1 | Create an `EvolutionStage` enum: `egg → hatchling → juvenile → adult → elder` | Python enums, lifecycle modeling |
| 4.2 | Track cumulative stats: `total_feeds`, `total_plays`, `total_rests`, `times_dormant` | Counters, historical data, audit trails |
| 4.3 | Implement `check_evolution()` — based on cumulative stats, the Whimling evolves when thresholds are met | Threshold logic, complex conditionals |
| 4.4 | Each evolution stage changes the stat decay rates and max values (e.g., adults have more energy, elders decay faster) | Strategy pattern, stage-specific behavior |
| 4.5 | Add `Traits` — permanent modifiers earned based on care patterns (e.g., "Well-Fed" if fed 50+ times, "Playful" if played 30+ times) | Data-driven behavior, trait/buff systems |

**End result:** Your Whimling visibly changes over time. How you cared for it determines what it becomes.

---

### Milestone 5 — Action Log & History 📜
**Concept: Event sourcing (intro), logging, audit trails**

Every action you take is recorded. You can replay history to see how your Whimling got where it is.

| # | Task | What You Learn |
|---|------|---------------|
| 5.1 | Create an `Event` model: `timestamp`, `action`, `details`, `stats_snapshot` | Event modeling, immutable records |
| 5.2 | Every handler appends an event to an event log (list of events, persisted alongside the Whimling) | Append-only data structures, event sourcing basics |
| 5.3 | Implement `python main.py history` — shows the last N events in a readable format | Pagination concept, display formatting |
| 5.4 | Implement `python main.py history --full` — exports the complete history as a JSON file | CLI flags, data export |
| 5.5 | Implement `python main.py replay` — replays all events from scratch to reconstruct the current state (proves your events are the source of truth) | Event replay, idempotency, data reconstruction |

**End result:** A full audit trail of everything you've ever done. You can delete the Whimling's save file, replay the event log, and get the exact same creature back.

---

### Milestone 6 — The World Expands 🌍
**Concept: Relational data, multiple entities, references between objects**

The Whimling doesn't live in a void. It has a home.

| # | Task | What You Learn |
|---|------|---------------|
| 6.1 | Create a `Location` model: `name`, `description`, `type` (forest, cave, lake, etc.), `available_actions` | Modeling related entities |
| 6.2 | Create a few hardcoded locations as seed data (loaded from a JSON/YAML config file) | Config-driven data, seed files |
| 6.3 | Add `current_location` to the Whimling. Implement `move_to(location)` handler | References between entities, foreign keys (conceptually) |
| 6.4 | Location affects stat decay rates (e.g., forest = slower hunger decay, cave = faster energy recovery) | Context-dependent behavior, lookup tables |
| 6.5 | Implement `explore()` — the Whimling can find `Items` at locations (random loot table) | Randomness with weights, loot tables, probability |
| 6.6 | Create an `Inventory` model — the Whimling can carry items, use items (e.g., "Moonberry" restores 20 hunger) | Collections, item usage, effects system |

**End result:** A small world with places to go, things to find, and items to use. The creature feels like it lives somewhere.

---

### Milestone 7 — Proper CLI ⌨️
**Concept: CLI frameworks, user experience, input validation**

Time to replace the raw `sys.argv` parsing with a real CLI.

| # | Task | What You Learn |
|---|------|---------------|
| 7.1 | Refactor all commands to use `click` or `typer` (both are excellent CLI frameworks) | CLI frameworks, decorators, command groups |
| 7.2 | Add help text, colored output, and confirmation prompts for dangerous actions | UX in CLI tools, ANSI colors, user feedback |
| 7.3 | Add an interactive mode: `python main.py play-session` enters a loop where you can type commands freely | REPL pattern, input loops, graceful exit handling |
| 7.4 | Add ASCII art for the Whimling's current evolution stage | String art, stage-based rendering, fun factor |
| 7.5 | Add `python main.py dashboard` — a rich status screen showing stats, location, inventory, traits | Terminal UI, layout design, `rich` library |

**End result:** A polished CLI experience. It feels like a real app, not a script.

---

### Milestone 8 — Testing 🧪
**Concept: Unit testing, mocking, test design, coverage**

Make sure your creature's reality doesn't break when you change things.

| # | Task | What You Learn |
|---|------|---------------|
| 8.1 | Set up `pytest` with a clean test structure (`tests/` mirroring `src/`) | Test setup, conftest.py, fixtures |
| 8.2 | Write unit tests for all model validations (invalid stats, edge values) | Parameterized tests, boundary testing |
| 8.3 | Write unit tests for handlers using a mock/in-memory repository | Mocking, dependency injection paying off |
| 8.4 | Write integration tests that use the real `JsonFileRepository` with temp files | `tmp_path` fixture, integration vs unit tests |
| 8.5 | Add test coverage reporting and aim for 80%+ on handlers | Coverage tools, understanding what to test |
| 8.6 | Add tests to pre-commit hooks so they run before every commit | CI-like local workflow, quality gates |

**End result:** A solid test suite. You can refactor fearlessly.

---

### Milestone 9 — Abilities & Cooldowns ⚡
**Concept: Time-based systems, scheduling, cooldowns, command pattern**

The Whimling learns abilities as it evolves. Abilities have cooldowns and costs.

| # | Task | What You Learn |
|---|------|---------------|
| 9.1 | Create an `Ability` model: `name`, `description`, `energy_cost`, `cooldown_seconds`, `last_used` | Time-based data, datetime math |
| 9.2 | Each evolution stage unlocks new abilities (data-driven from config) | Config-driven unlocks, progression systems |
| 9.3 | Implement `use_ability(name)` handler — checks cooldown, deducts energy, applies effect | Validation chains, precondition checking |
| 9.4 | Abilities have effects: "Forage" finds food, "Meditate" restores health, "Shimmer" reveals hidden items at a location | Command pattern, effect dispatch |
| 9.5 | Add ability history to the event log | Extending existing systems cleanly |

**End result:** Your Whimling has a growing set of things it can *do*, not just stats that go up and down.

---

### Milestone 10 — REST API 🌐
**Concept: HTTP, REST, request/response, API design**

Expose your Whimling's world through an API. The CLI becomes just one interface.

| # | Task | What You Learn |
|---|------|---------------|
| 10.1 | Add `FastAPI` as a dependency. Create a basic `GET /whimling` endpoint that returns the current state | HTTP basics, FastAPI intro, JSON responses |
| 10.2 | Add `POST /whimling/feed`, `POST /whimling/play`, etc. — all the existing handlers exposed as endpoints | REST verbs, route design, request bodies |
| 10.3 | Add proper error responses (404 if no Whimling exists, 400 for invalid actions) | HTTP status codes, error handling in APIs |
| 10.4 | Add `GET /whimling/history` with query params for pagination | Query parameters, pagination patterns |
| 10.5 | Both CLI and API use the exact same handlers and repository — they're just different interfaces | Ports & adapters pattern, proving architecture works |

**End result:** Your Whimling is accessible via `curl` or a browser. Same creature, two ways to interact.

---

### Milestone 11 — Background Simulation 🔄
**Concept: Background tasks, scheduling, concurrency basics**

The Whimling's world doesn't stop when you're not looking.

| # | Task | What You Learn |
|---|------|---------------|
| 11.1 | Implement a simple background ticker using `threading` or `asyncio` that runs `tick()` every N seconds when the API is running | Threading basics, background tasks, async intro |
| 11.2 | The Whimling's stats decay in real-time while the server is running | Real-time simulation, state mutation over time |
| 11.3 | Add a "mood" system derived from stats — if happiness is high, the Whimling occasionally "does things" on its own (logged as events) | Autonomous behavior, emergent systems |
| 11.4 | Add WebSocket support — push stat updates to a connected client in real-time | WebSockets, push vs pull, real-time communication |

**End result:** The Whimling feels alive. Leave the server running, come back, and things have happened.

---

### Milestone 12 — Multi-Whimling & Relationships 👥
**Concept: Multi-entity management, relationships, CRUD at scale**

One Whimling is lonely. Let it have companions.

| # | Task | What You Learn |
|---|------|---------------|
| 12.1 | Support multiple Whimlings — each with a unique ID. Update repository to handle collections | UUIDs, collection management, CRUD operations |
| 12.2 | Add a `bond` system — Whimlings near each other can form bonds (friendship/rivalry based on trait compatibility) | Relationship modeling, graph-like data |
| 12.3 | Implement `interact(whimling_a, whimling_b)` — they play together, affecting both creatures' stats | Multi-entity transactions, consistency |
| 12.4 | A Whimling in `elder` stage can produce a new egg, passing down some traits | Inheritance (conceptual), generational data |

**End result:** A small ecosystem of creatures that interact with each other.

---

## 🧩 Bonus Features (Pick Any, Any Time)

These are standalone features you can tackle whenever you want a break from the main roadmap:

| Feature | Concept Learned |
|---------|----------------|
| **Save file encryption** — encrypt the JSON save file with a passphrase | Cryptography basics, `cryptography` library |
| **Whimling art generator** — generate ASCII/pixel art based on traits and stage | Procedural generation, string manipulation |
| **Achievement system** — unlock achievements for milestones (first hatch, 100 feeds, etc.) | Observer pattern, event-driven architecture |
| **Import/Export** — export your Whimling as a shareable file, import someone else's | Serialization formats, data portability |
| **Plugin system** — let external Python files register new abilities or locations | Plugin architecture, dynamic imports, `importlib` |
| **Database migration** — change your schema and write a migration script | Schema evolution, data migration patterns |
| **Rate limiting** — limit how often actions can be performed (API and CLI) | Rate limiting algorithms, token bucket |
| **Caching** — cache frequently accessed data (stats, location info) | Caching patterns, TTL, invalidation |
| **Whimling journal** — the Whimling writes diary entries based on its mood and events | Text generation, templates, creative coding |
| **Battle system** — Whimlings can encounter wild creatures and fight using abilities | Turn-based systems, game logic |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.14+** | Language |
| **Pydantic v2** | Data models and validation |
| **`uv`** | Package and project management |
| **`mise`** | Tool version management |
| **`ruff`** | Linting and formatting |
| **`pyrefly`** | Type checking |
| **`pytest`** | Testing (Milestone 8+) |
| **`click` or `typer`** | CLI framework (Milestone 7+) |
| **`FastAPI`** | REST API (Milestone 10+) |
| **SQLite** | Database (Milestone 3+, built into Python) |
| **JSON files** | Initial persistence (Milestone 0–2) |

No Docker. No cloud. No accounts. Everything runs with `python main.py`.

---

## 📂 Target Project Structure (fully built out)

```
project_sba/
├── main.py                     # CLI entrypoint
├── pyproject.toml
├── README.md
├── config/
│   ├── locations.json          # Seed data for world locations
│   ├── abilities.json          # Ability definitions per stage
│   └── items.json              # Item definitions and loot tables
├── data/                       # Local save files (gitignored)
│   ├── whimling.json
│   └── events.json
├── src/
│   └── app/
│       ├── models/
│       │   ├── whimling.py     # Whimling, Egg, Stats, EvolutionStage
│       │   ├── event.py        # Event log models
│       │   ├── location.py     # World locations
│       │   ├── item.py         # Items and inventory
│       │   └── ability.py      # Abilities and cooldowns
│       ├── handlers/
│       │   ├── egg.py          # create_egg, warm_egg
│       │   ├── care.py         # feed, play, rest
│       │   ├── evolution.py    # check_evolution, apply_evolution
│       │   ├── world.py        # move_to, explore
│       │   ├── abilities.py    # use_ability
│       │   └── tick.py         # time passage, stat decay
│       ├── infrastructure/
│       │   ├── database/
│       │   │   └── connection.py
│       │   └── repositories/
│       │       ├── protocol.py        # Repository interface
│       │       ├── json_repository.py # JSON file backend
│       │       └── sqlite_repository.py # SQLite backend
│       └── cli/                # CLI commands (Milestone 7+)
│           └── commands.py
├── tests/
│   ├── conftest.py
│   ├── test_models/
│   ├── test_handlers/
│   └── test_repositories/
└── scripts/
    └── setup.sh
```

---

## 🚀 Getting Started

```bash
# Clone and setup
cd project_sba
uv sync

# Create your egg
python main.py create

# Warm the egg (repeat until it hatches!)
python main.py warm

# Check on your Whimling
python main.py status
```

---

## 📅 Suggested Pace

| Session | Milestone | Time Estimate |
|---------|-----------|---------------|
| 1–2 | Milestone 0: The Egg Exists | 1 session |
| 3–4 | Milestone 1: Hatching | 1–2 sessions |
| 5–6 | Milestone 2: Vital Signs | 2 sessions |
| 7–8 | Milestone 3: Persistence Swap | 2 sessions |
| 9–10 | Milestone 4: Evolution | 2 sessions |
| 11–12 | Milestone 5: Event Log | 1–2 sessions |
| 13–14 | Milestone 6: World Expands | 2–3 sessions |
| 15–16 | Milestone 7: Proper CLI | 2 sessions |
| 17–18 | Milestone 8: Testing | 2 sessions |
| 19–20 | Milestone 9: Abilities | 2 sessions |
| 21–22 | Milestone 10: REST API | 2 sessions |
| 23–24 | Milestone 11: Background Sim | 2 sessions |
| 25–26 | Milestone 12: Multi-Whimling | 2 sessions |

At one session every two weeks, this is roughly **a year of learning content**. Each session is ~2–4 hours of focused work.

---

## 🌟 The Promise

When you're done, you will have:

- Built a real, non-trivial Python application from scratch
- Practiced data modeling, state machines, persistence, APIs, testing, async, and more
- A project you can show in interviews that demonstrates depth, not just breadth
- A creature that is uniquely yours — shaped by the code you wrote and the care you gave it

**Your Whimling is waiting. Start with the egg.** 🥚
