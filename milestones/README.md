# Milestones — Project SBA

> This folder contains one markdown file per milestone. Each file records:
> - **Status** (complete / in-progress / pending)
> - **What was built** — every file created or modified
> - **Key decisions** made and why
> - **Learning notes** — what concepts each piece of code teaches
> - **What to try** — manual commands to verify the milestone works
>
> **For AI agents starting a new session:** read `README.md` (project root)
> for the overall vision, then read the milestone file for the current
> milestone to understand exactly where the project stands.

---

## Milestone Status

| # | Title | Status | File |
|---|-------|--------|------|
| 0 | The Egg Exists 🥚 | ✅ Complete | [milestone_0.md](./milestone_0.md) |
| 1 | Hatching 🐣 | ⏳ Pending | — |
| 2 | Vital Signs 💓 | ⏳ Pending | — |
| 3 | Persistence Layer Swap 🗄️ | ⏳ Pending | — |
| 4 | Evolution 🦋 | ⏳ Pending | — |
| 5 | Action Log & History 📜 | ⏳ Pending | — |
| 6 | The World Expands 🌍 | ⏳ Pending | — |
| 7 | Proper CLI ⌨️ | ⏳ Pending | — |
| 8 | Testing 🧪 | ⏳ Pending | — |
| 9 | Abilities & Cooldowns ⚡ | ⏳ Pending | — |
| 10 | REST API 🌐 | ⏳ Pending | — |
| 11 | Background Simulation 🔄 | ⏳ Pending | — |
| 12 | Multi-Whimling & Relationships 👥 | ⏳ Pending | — |

---

## How to Resume Work in a New Session

1. Read `README.md` (project root) — the full project vision and roadmap
2. Read `plan/1_plan_database_connection.md` — local MongoDB setup context
3. Find the lowest-numbered **⏳ Pending** milestone in the table above
4. Read its milestone file for detailed context on what to build next
5. Check the current project file structure with `ls -la src/app/`

---

## Running the Project

```bash
# Install / sync dependencies
uv sync

# Create your egg (first time only)
uv run python main.py create YourName

# Check status
uv run python main.py status
```

## Tech Stack Summary

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.14 | Language (managed by mise) |
| uv | latest | Package manager + virtual env |
| Pydantic | v2 | Data models and validation |
| pymongo | v4+ | MongoDB driver (used from Milestone 3) |
| ruff | latest | Linting + formatting |
| pyrefly | latest | Type checking |
| MongoDB | 8.2.9 (local Homebrew) | Database (Milestone 3+) |

MongoDB connection string: `mongodb://localhost:27017/project_sba`
MongoDB is managed by Homebrew: `brew services start/stop mongodb-community`

