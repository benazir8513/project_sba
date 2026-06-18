# Database Connection Guide — Project SBA

## Part 1 — The Options (with honest tradeoffs)

### Option A: JSON Files Only — No Database At All

**Use for: Milestones 0, 1, 2**

For the first three milestones, you store the Whimling's data as a JSON file (`data/whimling.json`). No database needed.

| ✅ Pros                                      | ❌ Cons                                 |
|---------------------------------------------|----------------------------------------|
| Zero setup                                  | Not scalable past a single file        |
| Easy to inspect with any text editor        | No querying, no indexes                |
| Perfect for learning serialization concepts | Can't handle multiple Whimlings easily |

This is the **planned approach for Milestones 0–2**. Keep it simple early.

---

### Option B: mongomock (In-Memory Python Mock)

**Use for: Tests only**

`mongomock` is a Python library that pretends to be MongoDB entirely in memory. It's used in tests so you don't need a
real database running.

```python
import mongomock

client = mongomock.MongoClient()
db = client["project_sba"]  # Lives in RAM, gone when script ends
```

| ✅ Pros                     | ❌ Cons                                        |
|----------------------------|-----------------------------------------------|
| No server needed           | Data disappears when process ends             |
| Fast for tests             | Not a real database — some features differ    |
| Already in your work stack | Only suitable for testing, not the actual app |

**Use this in your `pytest` tests (Milestone 8), not in the real app.**

---

### Option C: Docker Container via Colima

**General approach at work**

You have Colima installed — it's a lightweight VM that lets Docker containers run on macOS without Docker Desktop. You
could run MongoDB in a container.

```bash
colima start
docker run -d --name project-sba-mongo -p 27017:27017 mongo:8
```

| ✅ Pros                                                       | ❌ Cons                                                           |
|--------------------------------------------------------------|------------------------------------------------------------------|
| Fully isolated — completely separate from your local install | Colima is currently stopped                                      |
| Can pin exact MongoDB version                                | Requires starting Colima before every session                    |
| Mirrors what teams do in production-like setups              | More moving parts for the same result                            |
| Good learning experience for Docker                          | Port conflict with your existing local MongoDB (both want 27017) |

**Not recommended right now** — you already have MongoDB running locally, and adding a container creates a port conflict
and extra complexity for no benefit at this stage.

---

### Option D: Your Existing Local MongoDB ⭐ RECOMMENDED

**Use for: Milestones 3+**

You already have `mongodb-community` v8.2.9 installed via Homebrew, running as a background service at
`localhost:27017`. It's already running. Creating a new database called `project_sba` takes zero effort — you just use
that name in your connection string and MongoDB creates it automatically the first time you write data.

| ✅ Pros                                        | ❌ Cons                                                                |
|-----------------------------------------------|-----------------------------------------------------------------------|
| Already installed and running                 | Lives alongside work databases (completely isolated, but same server) |
| Zero setup — works immediately                | You need to remember it auto-starts on login                          |
| No port conflicts                             | —                                                                     |
| Connect via Compass with no new configuration | —                                                                     |
| `pymongo` connects to it with one line        | —                                                                     |

**This is the correct choice.** The section below is the full step-by-step for using it.

---

## Part 2 — The Full Setup (Option D — Step by Step)

### Step 1: Verify MongoDB is Running

```bash
brew services list | grep mongodb
```

Expected output:

```
mongodb-community  started  yourname  ~/Library/LaunchAgents/homebrew.mxcl.mongodb-community.plist
```

The `started` status means it's running. **If it ever shows `stopped`**, start it with:

```bash
brew services start mongodb-community
```

To stop it (saves resources when not working on the project):

```bash
brew services stop mongodb-community
```

---

### Step 2: Verify You Can Connect

```bash
mongosh --eval "db.adminCommand('ping')" --quiet
```

Expected output: `{ ok: 1 }`

That's it. Your server is live.

---

### Step 3: Understand the Connection String

A **connection string** is the address your code uses to find the database server. For your local setup:

```
mongodb://localhost:27017/project_sba
```

Breaking it down:

- `mongodb://` — protocol (like `https://` for web requests)
- `localhost` — your own machine
- `27017` — the port MongoDB listens on
- `/project_sba` — the database name to use

**You don't need to create the database first.** MongoDB is lazy — it creates the database (`project_sba`) and any
collections automatically the moment you first write a document. If the database doesn't exist yet, that's fine.

---

### Step 4: See It in MongoDB Compass

Your Compass already connects to `localhost:27017`. All your databases show up in the left panel. Once you start the
project and write your first document, a new `project_sba` database will appear there automatically alongside the work
databases.

You can also create it manually via Compass: click the `+` next to "Databases" and name it `project_sba`.

---

### Step 5: Connect From Python

This is how `pymongo` connects:

```python
from pymongo import MongoClient

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Select (or auto-create) the project_sba database
db = client["project_sba"]

# Select (or auto-create) the whimlings collection
whimlings = db["whimlings"]

# Insert a test document
whimlings.insert_one({"name": "Lumis", "state": "egg"})

# Read it back
doc = whimlings.find_one({"name": "Lumis"})
print(doc)
# {'_id': ObjectId('...'), 'name': 'Lumis', 'state': 'egg'}
```

The `project_sba` database and `whimlings` collection are created automatically on first write.

---

### Step 6: Verify Isolation From Work Databases

Run this to confirm `project_sba` is completely separate:

```bash
mongosh project_sba --eval "db.getCollectionNames()" --quiet
```

This connects specifically to `project_sba` — it cannot see anything in `onex-config` or any other database.

---

### Step 7: Environment Variable (Best Practice)

Never hardcode the connection string in code. Store it as an environment variable and read it in Python:

In `.env.local` (already gitignored via `.envrc` — add this):

```
MONGODB_URI=mongodb://localhost:27017/project_sba
```

In Python:

```python
import os
from pymongo import MongoClient

uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/project_sba")
client = MongoClient(uri)
db = client.get_default_database()  # Reads database name from the URI
```

The `get_default_database()` call reads the database name from the URI (`project_sba`), so you never hardcode it
anywhere in source code.

---

## Part 3 — How This Fits the Project Milestones

| Milestone                  | Storage Used                                                             | Database Needed? |
|----------------------------|--------------------------------------------------------------------------|------------------|
| 0 — The Egg Exists         | JSON file (`data/whimling.json`)                                         | ❌ No             |
| 1 — Hatching               | JSON file                                                                | ❌ No             |
| 2 — Vital Signs            | JSON file                                                                | ❌ No             |
| 3 — Persistence Swap       | You introduce the repository pattern and add MongoDB as a second backend | ✅ Yes            |
| 4+ — All future milestones | MongoDB (via repository)                                                 | ✅ Yes            |

The project is designed so you don't need MongoDB until Milestone 3. By then, you'll have built the business logic first
and learned why having an abstraction layer (the repository pattern) makes swapping the storage backend painless.

---

## Part 4 — The Infrastructure Module (Where the Connection Lives)

In the project's architecture, the database connection belongs in `src/app/infrastructure/database/connection.py`. This
file will be implemented in Milestone 3, but here's what it will look like:

```python
# src/app/infrastructure/database/connection.py
import os
from pymongo import MongoClient
from pymongo.database import Database

_client: MongoClient | None = None


def get_client() -> MongoClient:
    """Return a singleton MongoClient. Created once, reused."""
    global _client
    if _client is None:
        uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/project_sba")
        _client = MongoClient(uri)
    return _client


def get_db() -> Database:
    """Return the project database."""
    return get_client().get_default_database()
```

This pattern (a singleton client) is standard. MongoDB clients are expensive to create, so you create one and reuse it.
In tests, you'll replace this with `mongomock`.

---

## Part 5 — Quick Reference Card

```bash
# Check if MongoDB is running
brew services list | grep mongodb

# Start MongoDB
brew services start mongodb-community

# Stop MongoDB (optional, saves memory)
brew services stop mongodb-community

# Open a shell to your project's database
mongosh project_sba

# List collections in the project database
mongosh project_sba --eval "db.getCollectionNames()" --quiet

# Delete ALL project data (nuclear reset — use with care)
mongosh project_sba --eval "db.dropDatabase()" --quiet
```

```
Connection string:    mongodb://localhost:27017/project_sba
Database name:        project_sba
Server address:       localhost:27017
MongoDB version:      8.2.9
Managed by:           Homebrew (brew services)
Auto-starts on login: Yes
```

---