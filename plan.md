# Python Learning Roadmap — Personal Project Plan

> **Goal:** Improve as a Python developer by building a personal project that mirrors your work stack (AWS Lambda + MongoDB + `uv` + `mise` + pre-commit hooks) — fully local, zero AWS cost.

## Actual Work Stack (from `pyproject.toml`)

| Concern | Library | Notes |
|---|---|---|
| Lambda utilities | `aws-lambda-powertools` | Logging, tracing, event parsing — learn this well |
| Database ODM | `pymongo` | Direct MongoDB driver — work is switching to this from mongoengine |
| Data validation | `pydantic` v2 | Used for validating Lambda `event` payloads |
| Linting + formatting | `ruff` | Replaces both `flake8` and `black` — one tool |
| Type checking | `pyrefly` | Meta's type checker (alternative to `mypy`) |
| Test DB | `mongomock` | In-memory MongoDB for tests — no Docker needed in tests |
| Import architecture | `import-linter` | Enforces layer boundaries (e.g. core can't import api) |
| Build backend | `hatchling` | Used by `uv` to build/package the project |

---

## Phase 1 — Foundation & Tooling Setup *(Week 1–2)*

**Goal:** Reproduce your work environment locally. Understand every tool you use day-to-day.

### Set Up
- Create `.tool-versions` (asdf/mise format — matches work convention) pinning Python, uv, pre-commit
- Bootstrap the project with `uv init`, configure `pyproject.toml` modeled after work
- Run `mise install` to install all pinned tools
- Init a git repo and install `pre-commit` hooks:
  - `ruff` hook (lint + format) fetched directly by pre-commit from its registry
  - Also add `ruff` to `pyproject.toml` dev deps so you can run `uv run ruff` manually
- Add a `scripts/` folder with a `setup.sh` that automates full local bootstrap

> **Note:** `pre-commit` itself lives in `.tool-versions` (managed by mise), NOT in `pyproject.toml`.
> `ruff` lives in both: `pyproject.toml` dev deps (for `uv run ruff`) AND referenced in `.pre-commit-config.yaml`.

### Learn
- How `mise` and `uv` interact (`.mise.toml` → Python version, `uv` → packages)
- How `pre-commit` hooks work and why they exist
- Python project structure: `src/` layout vs flat layout, `__init__.py`, modules
- What `pyproject.toml` sections mean: `[project]`, `[dependency-groups]`, `[build-system]`, `[tool.ruff]`, etc.
- Why `ruff` replaces both `flake8`/`isort`/`black` and what the lint rule codes mean (E, F, UP, B, SIM, I)

### Mini-Project
A `hello_lambda.py` — a plain Python function with the exact signature of a Lambda handler (`def handler(event, context)`), callable locally via a simple `run.py` script. No framework yet.

### Target Folder Layout
```
project_sba/
├── .mise.toml
├── .pre-commit-config.yaml
├── pyproject.toml
├── scripts/
│   └── setup.sh
├── src/
│   └── handlers/
│       └── hello.py
└── tests/
```

---

## Phase 2 — Python Core & MongoDB *(Week 3–5)*

**Goal:** Write real Python (not just boilerplate), talk to a local MongoDB, understand async vs sync.

### Set Up
- Run MongoDB locally via Docker (`docker-compose.yml` with a `mongo` service) — no Atlas, no fees
- Add `pymongo` as a dependency via `uv add pymongo`
- Write a `db/` module that encapsulates connection logic (mirrors how work backends will do it)

### Learn
- Python type hints thoroughly — functions, dicts, dataclasses, `TypedDict`
- `pydantic` v2 for data validation (extremely common in Lambda backends — validates incoming `event` payloads)
- MongoDB basics: collections, documents, insert/find/update/delete, indexes
- Python error handling patterns: custom exceptions, try/except structure in handlers

### Mini-Project
A **personal book tracker** — Lambda handlers to add, list, update, and delete books. Each handler validates its input with Pydantic, reads/writes to local MongoDB. Invoke each handler by running:
```bash
python run.py '{"action": "add", ...}'
```

---

## Phase 3 — Lambda Simulation & Testing *(Week 6–8)*

**Goal:** Make local execution feel real — simulate Lambda's invocation model without any AWS cost.

### Set Up
- Use [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) with `sam local invoke` — runs your handler in a Docker container that mirrors the Lambda runtime exactly (free, local only)
- Alternatively (simpler): build a lightweight `local_invoke.py` that constructs a fake `event`/`context` and calls your handler — no Docker needed
- Add a `template.yaml` (SAM) or `local_invoke.py` depending on chosen approach
- Wire MongoDB Docker container into the same `docker-compose.yml` so everything starts with one command: `docker-compose up`

### Learn
- How Lambda's execution model works: cold starts, handler lifecycle, environment variables
- How to read config/secrets from environment variables (`os.environ`) — same pattern as real Lambdas using AWS SSM/Secrets Manager
- Python `logging` module configured properly (Lambda uses stdout; structured JSON logs are best practice)
- Writing unit tests with `pytest` — mock MongoDB calls, test handler logic in isolation

### Mini-Project
Extend the book tracker — add a **"recommendations" handler** that queries MongoDB and returns books by genre. Write `pytest` tests for it. Invoke it via SAM local or your invoker script with a JSON event payload.

---

## Phase 4 — Work-Ready Patterns *(Week 9–12)*

**Goal:** Implement the patterns you actually see at work — multiple handlers, shared utilities, CI-like checks.

### Set Up
- Structure for multiple handlers in `src/handlers/` (each a separate file = separate Lambda in real life)
- A `src/shared/` module for reusable logic (DB client singleton, logging setup, common Pydantic models)
- Add a `Makefile` with targets: `make test`, `make lint`, `make invoke HANDLER=books`
- Add `mongomock` or `pytest-mongo` for in-memory MongoDB in tests (no Docker needed when running tests)

### Learn
- Dependency injection patterns in Python (pass DB client into handlers vs. global singleton — and the tradeoffs)
- Python packaging internals: why `src/` layout prevents import bugs, how `uv` resolves deps
- Structuring shell scripts properly: `set -euo pipefail`, argument parsing, exit codes
- How pre-commit hooks can run `pytest` or `mypy` on staged files (connect tooling to habits)

### Mini-Project
Build a **small event-driven expense tracker** — handlers for `log_expense`, `get_summary`, `delete_expense`. Shared Pydantic models, shared DB module, full test coverage, invokable via SAM local or scripts. At this point your personal project is a near-identical local mirror of a real work Lambda service.

---

## Work Stack → Local Equivalent

| Work Tool | Local Equivalent | Notes |
|---|---|---|
| AWS Lambda | SAM `local invoke` or `local_invoke.py` | Free, Docker-based or pure Python |
| MongoDB Atlas/cluster | `mongo` Docker container | `docker-compose up` |
| `mise` | `.mise.toml` in project root | Pin Python version exactly |
| `uv` | `uv init` + `uv add` | Replaces pip/venv entirely |
| Pre-commit hooks | `.pre-commit-config.yaml` | `ruff` (lint + format), `pyrefly` (type check) |
| Shell automation | `scripts/setup.sh`, `Makefile` | One command to boot everything |

---

## Resources

| Phase | Resources |
|---|---|
| Phase 1 | [uv docs](https://docs.astral.sh/uv/), [mise docs](https://mise.jdx.dev/), [pre-commit docs](https://pre-commit.com/) |
| Phase 2 | [pymongo docs](https://pymongo.readthedocs.io/en/stable/tutorial.html), [Pydantic v2 docs](https://docs.pydantic.dev/latest/), [aws-lambda-powertools docs](https://docs.powertools.aws.dev/lambda/python/latest/) |
| Phase 3 | [SAM CLI local invoke](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-invoke.html), [pytest docs](https://docs.pytest.org/), *Effective Python* (Brett Slatkin) |
| Phase 4 | *Architecture Patterns with Python* (Percival & Gregory), [mongomock](https://github.com/mongomock/mongomock) |

---

## Tips

1. **SAM vs. plain invoker?** A plain `local_invoke.py` is simpler and sufficient for Phase 1–2. Switch to SAM in Phase 3 when you want the true Lambda runtime container.
2. **Pick a domain you care about.** Book tracker and expense tracker are just examples — pick something you'll actually use (recipe manager, workout log, budget tracker) so motivation stays high.
3. **`ruff` replaces `black`.** Your work project does not use `black` — `ruff format` handles formatting. Don't add both.

