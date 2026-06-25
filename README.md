# logpose-api

Backend for **Logpose**, a personal life-tracking app. The name is a One Piece reference — the Log Pose is the navigation instrument that records every island you visit.

## What it is

A REST API that acts as the sync layer for the desktop and mobile apps. The apps are offline-first (data is stored locally in SQLite) and use these endpoints to sync in the background when there's a connection.

## Stack

- **Python 3.14** + **FastAPI**
- **SQLAlchemy 2.x** with the new `Mapped` / `mapped_column` API
- **SQLite** (local database, no external dependencies)
- **Pydantic v2** (schema validation)
- **pytest** + **httpx** (343 integration tests)

## Modules

| Module | Endpoints | Description |
|---|---|---|
| Body Weight | `/body-weight/` | Daily body-weight log |
| Exercises | `/exercises/` | Exercise catalogue with muscle group and subgroup |
| Routines | `/routines/` | Weekly training routines |
| Gym | `/gym/routine-exercises/` `/gym/sessions/` `/gym/sets/` | Exercises per day, training sessions and sets |
| Calendar | `/calendar/` | Events with recurrence (`none` / `daily` / `weekly`) |
| Tasks | `/tasks/lists` `/tasks/items` | Task lists with items and completed state |
| Journal | `/journal/` | Daily entry — one per day, with duplicate detection (409) |
| Quotes | `/quotes/` | Motivational quotes with optional author |
| Habits | `/habits/categories` `/habits/` `/habits/logs` | Habits grouped by colour category, with per-weekday scheduling and daily completion logs |
| Countdowns | `/countdowns/` | Countdowns to a target date (days/hours left), with optional yearly recurrence |

All modules implement full CRUD with cascading deletes where appropriate (deleting a routine clears its sessions and sets; deleting an exercise clears its routine_exercises and sets).

## Sync architecture

```
[React Native / Expo]           [React + Tauri]
       Mobile         ←──────→  Desktop
          ↕            syncs      ↕
    local SQLite                local SQLite
          ↕                       ↕
     [FastAPI + SQLite]  ←── this repo
```

Each record in the apps has three control fields: `server_id` (id on the server, null if not yet synced), `synced` (0/1) and `pending_delete` (1 if marked for deletion on the server). The sync cycle is: push deletes → push unsynced → pull server → prune stale.

## Tests

```bash
pytest
```

343 integration tests organised by module. Each test uses an isolated in-memory SQLite database (the `client` fixture in `conftest.py`). They cover equivalence partitions, boundary values and full end-to-end scenarios (complete CRUD flow).

## Structure

```
app/
├── main.py          — entry point: routers, CORS, table creation
├── database.py      — SQLite engine, session, declarative Base, PRAGMA foreign_keys=ON
├── models/          — SQLAlchemy models (one file per table)
├── schemas/         — Pydantic schemas (Create / Update / Read)
└── routers/         — FastAPI endpoints (one router per module)
tests/
├── conftest.py      — client fixture with in-memory SQLite
└── test_*.py        — integration tests per module
```

## Running it

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --reload
```

API at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

`--host 0.0.0.0` is required so the mobile app can connect from the same local network.
