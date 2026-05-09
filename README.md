# logpose-api

Backend de **Logpose**, una app personal de life tracking. El nombre es una referencia a One Piece — el Log Pose es el instrumento de navegación que registra cada isla visitada.

## Qué es

API REST construida con FastAPI y SQLite que centraliza todos los datos de tracking. Corre en local (red doméstica) y es consumida tanto por la app de escritorio como por la app móvil.

## Stack

- **Python 3.14** + **FastAPI**
- **SQLAlchemy 2.x** (ORM)
- **SQLite** (base de datos local)
- **Pydantic v2** (validación y schemas)

## Módulos implementados

| Módulo | Endpoints | Estado |
|---|---|---|
| Peso corporal | `GET POST PUT DELETE /body-weight/` | ✅ Completo |
| Ejercicios | `GET POST PUT DELETE /exercises/` | ✅ Completo |

## Estructura

```
app/
├── main.py              — punto de entrada, CORS, creación de tablas
├── database.py          — engine, sesión, Base declarativa
├── models/
│   ├── body_weight.py
│   └── exercise.py
├── routers/
│   ├── body_weight.py
│   └── exercise.py
└── schemas/
    ├── body_weight.py
    └── exercise.py
```

## Cómo arrancar

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --reload
```

**Importante:** el comando debe escribirse en una sola línea. Si se parte, uvicorn arranca en `127.0.0.1` y el móvil no puede conectarse.

API disponible en `http://localhost:8000`. Documentación interactiva en `/docs`.

## Arquitectura general

```
[React Native / Expo]  ←→  [FastAPI + SQLite]  ←→  [React + Tauri]
        Móvil                    Este repo               Desktop
```

El servidor es descubierto automáticamente en la red local vía mDNS (`archlinux.local`). El desktop usa `localhost` al correr en el mismo equipo.
