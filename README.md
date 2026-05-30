# logpose-api

Backend de **Logpose**, una app personal de life tracking. El nombre es una referencia a One Piece — el Log Pose es el instrumento de navegación que registra cada isla visitada.

## Qué es

API REST que actúa como capa de sincronización para las apps de escritorio y móvil. Las apps funcionan offline-first (los datos se guardan localmente en SQLite) y usan estos endpoints para sincronizar en segundo plano cuando hay conexión.

## Stack

- **Python 3.14** + **FastAPI**
- **SQLAlchemy 2.x** con la nueva API `Mapped` / `mapped_column`
- **SQLite** (base de datos local, sin dependencias externas)
- **Pydantic v2** (validación de schemas)
- **pytest** + **httpx** (220 tests de integración)

## Módulos

| Módulo | Endpoints | Descripción |
|---|---|---|
| Body Weight | `/body-weight/` | Registro diario de peso corporal |
| Ejercicios | `/exercises/` | Catálogo de ejercicios con grupo y subgrupo muscular |
| Rutinas | `/routines/` | Rutinas semanales de entrenamiento |
| Gym | `/gym/routine-exercises/` `/gym/sessions/` `/gym/sets/` | Ejercicios por día, sesiones de entreno y series |
| Calendario | `/calendar/` | Eventos con recurrencia (`none` / `daily` / `weekly`) |
| Tareas | `/tasks/lists` `/tasks/items` | Listas de tareas con items y estado completado |
| Diario | `/journal/` | Entrada diaria — una por día, con detección de duplicados (409) |
| Frases | `/quotes/` | Frases motivacionales con autor opcional |

Todos los módulos implementan CRUD completo con borrados en cascada donde corresponde (borrar una rutina limpia sus sesiones y series; borrar un ejercicio limpia sus routine_exercises y sets).

## Arquitectura de sincronización

```
[React Native / Expo]           [React + Tauri]
       Móvil          ←──────→  Desktop
          ↕           sincroniza  ↕
    SQLite local                SQLite local
          ↕                       ↕
     [FastAPI + SQLite]  ←── este repo
```

Cada registro en las apps tiene tres campos de control: `server_id` (id en el servidor, null si no se ha sincronizado), `synced` (0/1) y `pending_delete` (1 si está marcado para borrar del servidor). El ciclo de sync es: push deletes → push unsynced → pull server → prune stale.

## Tests

```bash
pytest
```

220 tests de integración organizados por módulo. Cada test usa una base de datos SQLite en memoria aislada (fixture `client` en `conftest.py`). Cubren particiones equivalentes, valores límite y escenarios de sistema completos (flujo CRUD de principio a fin).

## Estructura

```
app/
├── main.py          — punto de entrada: routers, CORS, creación de tablas
├── database.py      — engine SQLite, sesión, Base declarativa, PRAGMA foreign_keys=ON
├── models/          — modelos SQLAlchemy (un archivo por tabla)
├── schemas/         — schemas Pydantic (Create / Update / Read)
└── routers/         — endpoints FastAPI (un router por módulo)
tests/
├── conftest.py      — fixture client con SQLite en memoria
└── test_*.py        — tests de integración por módulo
```

## Cómo arrancar

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --reload
```

API en `http://localhost:8000`. Documentación interactiva en `http://localhost:8000/docs`.

`--host 0.0.0.0` es necesario para que el móvil pueda conectarse desde la misma red local.
