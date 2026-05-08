# Python Learning Roadmap — Personal Project Plan (Revised)

> **Goal:** Improve as a Python developer by building a personal project that mirrors your work stack (AWS Lambda + MongoDB + Terraform + `uv` + `mise` + pre-commit hooks) — using AWS Free Tier only.

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
| Infrastructure | `terraform` | Infrastructure as Code — all AWS resources defined in `tf/` |

---

## Phase 1 — Foundation & Tooling Setup *(Week 1–2)*

**Goal:** Reproduce your work environment locally. Understand every tool you use day-to-day. Get an AWS account ready.

### Set Up
- Create `.mise.toml` pinning Python, Terraform, uv, pre-commit
- Bootstrap the project with `uv init`, configure `pyproject.toml` modeled after work
- Run `mise install` to install all pinned tools (including Terraform)
- Init a git repo and install `pre-commit` hooks:
  - `ruff` hook (lint + format) fetched directly by pre-commit from its registry
  - Also add `ruff` to `pyproject.toml` dev deps so you can run `uv run ruff` manually
- Add a `scripts/` folder with a `setup.sh` that automates full local bootstrap
- **Create your AWS account** — follow [2_AWS.md](./2_AWS.md) Sections 1–5
- **Set up billing alerts immediately** — $0 budget alarm so you never get surprised
- **Install AWS CLI** and configure it with your IAM user credentials

> **Note:** `pre-commit` itself lives in `.mise.toml` (managed by mise), NOT in `pyproject.toml`.
> `ruff` lives in both: `pyproject.toml` dev deps (for `uv run ruff`) AND referenced in `.pre-commit-config.yaml`.
> `terraform` is pinned in `.mise.toml` — the `tf/` folder is already excluded from ruff and pyrefly in `pyproject.toml`.

### Learn
- How `mise` and `uv` interact (`.mise.toml` → Python + Terraform versions, `uv` → packages)
- How `pre-commit` hooks work and why they exist
- Python project structure: `src/` layout vs flat layout, `__init__.py`, modules
- What `pyproject.toml` sections mean: `[project]`, `[dependency-groups]`, `[build-system]`, `[tool.ruff]`, etc.
- Why `ruff` replaces both `flake8`/`isort`/`black` and what the lint rule codes mean (E, F, UP, B, SIM, I)
- **AWS basics:** What IAM is, regions, the Free Tier model (always-free vs. 12-month-free)
- **Terraform basics:** What IaC is, provider/resource/data concepts, `init`/`plan`/`apply` workflow

### Mini-Project
A `hello_lambda.py` — a plain Python function with the exact signature of a Lambda handler (`def handler(event, context)`), callable locally via a simple `run.py` script. No framework yet.

### Target Folder Layout
```
project_sba/
├── .mise.toml              ← Python + Terraform pinned here
├── .pre-commit-config.yaml
├── pyproject.toml
├── plan/
│   ├── 1_plan.md
│   └── 2_AWS.md
├── scripts/
│   └── setup.sh
├── src/
│   └── handlers/
│       └── hello.py
├── tf/                     ← Terraform code lives here
│   └── (created in Phase 2)
└── tests/
```

---

## Phase 2 — Python Core, MongoDB & First Terraform *(Week 3–5)*

**Goal:** Write real Python, talk to a local MongoDB, and deploy your first Lambda to real AWS via Terraform.

### Set Up
- Run MongoDB locally via Docker (`docker-compose.yml` with a `mongo` service) — no Atlas, no fees
- Add `pymongo` as a dependency via `uv add pymongo`
- Write a `db/` module that encapsulates connection logic
- **Scaffold the `tf/` folder structure** — see [2_AWS.md](./2_AWS.md) Section 7
- **Write your first Terraform config** — provider setup with local state
- **Deploy a "hello world" Lambda** to real AWS (`tf/1_lambda/`)

### Learn
- Python type hints thoroughly — functions, dicts, dataclasses, `TypedDict`
- `pydantic` v2 for data validation (validates incoming `event` payloads)
- MongoDB basics: collections, documents, insert/find/update/delete, indexes
- Python error handling patterns: custom exceptions, try/except structure in handlers
- **Terraform HCL syntax:** resources, variables, outputs, data sources
- **AWS Lambda internals:** execution role, handler path, deployment packages (zip)
- **Terraform workflow:** `terraform init` → `plan` → `apply` → `destroy`

### Mini-Project
A **personal book tracker** — Lambda handlers to add, list, update, and delete books. Each handler validates its input with Pydantic, reads/writes to local MongoDB. Test locally first:
```bash
python run.py '{"action": "add", ...}'
```
Then deploy the handler to real AWS Lambda via Terraform and invoke it:
```bash
aws lambda invoke --function-name book-tracker --payload '{"action": "list"}' output.json
```

### Target `tf/` Layout
```
tf/
├── README.md               ← Explains each module and dependencies
├── 0_backend/              ← Provider config, (later: S3 state backend)
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
└── 1_lambda/               ← Lambda function + IAM role
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

---

## Phase 3 — Real Lambda Deployment & Testing *(Week 6–8)*

**Goal:** Deploy and invoke real Lambdas on AWS. Write proper tests. Keep everything free tier.

### Set Up
- Deploy Lambda handlers to AWS via Terraform (`tf/1_lambda/`)
- Wire up CloudWatch Logs for Lambda (free tier: 5GB ingestion/month)
- Add `pytest` and `mongomock` for testing
- Create a `local_invoke.py` for quick local testing without AWS round-trips

### Learn
- How Lambda's execution model works: cold starts, handler lifecycle, environment variables
- How to read config/secrets from environment variables (`os.environ`) — same pattern as real Lambdas using AWS SSM/Secrets Manager
- Python `logging` module configured properly (Lambda uses stdout; structured JSON logs are best practice)
- Writing unit tests with `pytest` — mock MongoDB calls, test handler logic in isolation
- **Terraform state management:** Understand local state vs. S3 backend (reference the S3 backend pattern from `scripts/init_terraform.sh`)
- **`terraform plan` as a safety net:** Always review before `apply`

### Mini-Project
Extend the book tracker — add a **"recommendations" handler** that queries MongoDB and returns books by genre. Write `pytest` tests for it. Deploy to AWS and invoke via CLI with a JSON event payload.

---

## Phase 4 — Work-Ready Patterns *(Week 9–12)*

**Goal:** Implement the patterns you actually see at work — multiple handlers, shared utilities, CI-like checks, production Terraform practices.

### Set Up
- Structure for multiple handlers in `src/handlers/` (each a separate file = separate Lambda in real life)
- A `src/shared/` module for reusable logic (DB client singleton, logging setup, common Pydantic models)
- Add a `Makefile` with targets: `make test`, `make lint`, `make deploy`, `make invoke HANDLER=books`
- Add `mongomock` or `pytest-mongo` for in-memory MongoDB in tests
- **Upgrade Terraform state to S3 backend** — mirrors the work pattern in `scripts/init_terraform.sh`
- **Add `trivy` scanning** for Terraform security (mirrors `scripts/check_terraform.sh`)
- **Set up IAM least-privilege policies** — each Lambda gets only the permissions it needs

### Learn
- Dependency injection patterns in Python (pass DB client into handlers vs. global singleton — and the tradeoffs)
- Python packaging internals: why `src/` layout prevents import bugs, how `uv` resolves deps
- Structuring shell scripts properly: `set -euo pipefail`, argument parsing, exit codes
- How pre-commit hooks can run `pytest` or `pyrefly` on staged files (connect tooling to habits)
- **Terraform modules:** Extract reusable patterns (e.g., a Lambda module that creates function + role + logs)
- **Infrastructure security scanning** with `trivy` (already referenced in your `check_terraform.sh`)

### Mini-Project
Build a **small event-driven expense tracker** — handlers for `log_expense`, `get_summary`, `delete_expense`. Shared Pydantic models, shared DB module, full test coverage, deployed to AWS via Terraform. At this point your personal project is a near-identical mirror of a real work Lambda service.

---

## Work Stack → Local/AWS Equivalent

| Work Tool | Your Project Equivalent | Notes |
|---|---|---|
| AWS Lambda | Real AWS Lambda (Free Tier) | 1M requests/month free for 12 months |
| MongoDB Atlas/cluster | `mongo` Docker container (local) | `docker-compose up` |
| Terraform | `tf/` folder with numbered modules | Deployed via `terraform apply` |
| `mise` | `.mise.toml` in project root | Pin Python + Terraform versions |
| `uv` | `uv init` + `uv add` | Replaces pip/venv entirely |
| Pre-commit hooks | `.pre-commit-config.yaml` | `ruff` (lint + format), `pyrefly` (type check) |
| Shell automation | `scripts/setup.sh`, `Makefile` | One command to boot everything |
| AWS CLI | `brew install awscli` | Invoke Lambdas, check logs |
| Trivy | `scripts/check_terraform.sh` | Security scan Terraform configs |

---

## Resources

| Phase | Resources |
|---|---|
| Phase 1 | [uv docs](https://docs.astral.sh/uv/), [mise docs](https://mise.jdx.dev/), [pre-commit docs](https://pre-commit.com/), [AWS Free Tier](https://aws.amazon.com/free/) |
| Phase 2 | [pymongo docs](https://pymongo.readthedocs.io/en/stable/tutorial.html), [Pydantic v2 docs](https://docs.pydantic.dev/latest/), [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs), [Terraform Getting Started](https://developer.hashicorp.com/terraform/tutorials/aws-get-started) |
| Phase 3 | [AWS Lambda docs](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html), [pytest docs](https://docs.pytest.org/), *Effective Python* (Brett Slatkin) |
| Phase 4 | *Architecture Patterns with Python* (Percival & Gregory), [mongomock](https://github.com/mongomock/mongomock), [Terraform Modules](https://developer.hashicorp.com/terraform/language/modules) |

---

## Tips

1. **Always check Free Tier limits** before creating any AWS resource. Set up a $0 billing alarm on day one.
2. **`terraform destroy` is your friend.** When you're done experimenting, destroy resources to avoid any charges.
3. **Pick a domain you care about.** Book tracker and expense tracker are just examples — pick something you'll actually use.
4. **`ruff` replaces `black`.** Your work project does not use `black` — `ruff format` handles formatting. Don't add both.
5. **Terraform folders are independent.** Each `tf/X_name/` folder is its own root module — you `cd` into it and run `terraform init/plan/apply` independently. The numeric prefix just suggests a logical first-time setup order.
6. **Start with local Terraform state.** Don't set up S3 backend until Phase 4 — it's an unnecessary complexity when learning.

