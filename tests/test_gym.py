# Pruebas de integración — Gym API
# Endpoints: /exercises/, /routines/, /gym/routine-exercises/, /gym/sessions/, /gym/sets/
# Diseño: particiones equivalentes (S04) + escenario completo (S08)

import pytest

VALID_EXERCISE = {"name": "Press banca", "muscle_group": "Pecho", "muscle_subgroup": "Superior"}
VALID_ROUTINE  = {"name": "Rutina A"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def create_exercise(client, **kwargs):
    data = {**VALID_EXERCISE, **kwargs}
    return client.post("/exercises/", json=data).json()

def create_routine(client, **kwargs):
    data = {**VALID_ROUTINE, **kwargs}
    return client.post("/routines/", json=data).json()

def create_routine_exercise(client, routine_id, exercise_id, day=0, position=0):
    return client.post("/gym/routine-exercises/", json={
        "routine_id": routine_id, "exercise_id": exercise_id,
        "day_of_week": day, "position": position,
    }).json()

def create_session(client, date="2026-05-17", **kwargs):
    return client.post("/gym/sessions/", json={"date": date, **kwargs}).json()

def create_set(client, session_id, exercise_id, **kwargs):
    return client.post("/gym/sets/", json={
        "session_id": session_id, "exercise_id": exercise_id,
        "set_number": 1, "weight": 80.0, "reps": 8, **kwargs,
    }).json()


# ── Exercises ──────────────────────────────────────────────────────────────────

class TestExercises:
    def test_lista_vacia(self, client):
        assert client.get("/exercises/").json() == []

    def test_crear_ejercicio_completo(self, client):
        r = client.post("/exercises/", json=VALID_EXERCISE)
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Press banca"
        assert data["muscle_group"] == "Pecho"
        assert data["muscle_subgroup"] == "Superior"
        assert "id" in data

    def test_crear_ejercicio_sin_grupo_muscular(self, client):
        r = client.post("/exercises/", json={"name": "Cardio libre"})
        assert r.status_code == 201
        assert r.json()["muscle_group"] is None
        assert r.json()["muscle_subgroup"] is None

    def test_crear_ejercicio_sin_subgrupo(self, client):
        r = client.post("/exercises/", json={"name": "Dominadas", "muscle_group": "Espalda"})
        assert r.status_code == 201
        assert r.json()["muscle_subgroup"] is None

    def test_schema_completo_ejercicio(self, client):
        data = client.post("/exercises/", json=VALID_EXERCISE).json()
        assert set(data.keys()) == {"id", "name", "muscle_group", "muscle_subgroup"}
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)

    def test_lista_ordenada_por_nombre(self, client):
        client.post("/exercises/", json={"name": "Sentadilla"})
        client.post("/exercises/", json={"name": "Curl biceps"})
        client.post("/exercises/", json={"name": "Press banca"})
        names = [e["name"] for e in client.get("/exercises/").json()]
        assert names == sorted(names)

    @pytest.mark.parametrize("payload", [
        {},                       # falta name
        {"name": ""},             # name vacío — Pydantic lo acepta, pero es un caso a vigilar
        {"name": 123},            # name no es string
    ])
    def test_crear_ejercicio_invalido(self, client, payload):
        r = client.post("/exercises/", json=payload)
        assert r.status_code == 422

    def test_borrar_ejercicio_existente(self, client):
        ex_id = create_exercise(client)["id"]
        assert client.delete(f"/exercises/{ex_id}").status_code == 204

    def test_borrar_ejercicio_inexistente(self, client):
        assert client.delete("/exercises/9999").status_code == 404

    def test_borrar_elimina_de_la_lista(self, client):
        ex_id = create_exercise(client)["id"]
        client.delete(f"/exercises/{ex_id}")
        assert all(e["id"] != ex_id for e in client.get("/exercises/").json())

    def test_renombrar_ejercicio(self, client):
        ex_id = create_exercise(client)["id"]
        r = client.put(f"/exercises/{ex_id}", json={"name": "Nuevo nombre", "muscle_group": "Pecho", "muscle_subgroup": "Superior"})
        assert r.status_code == 200
        assert r.json()["name"] == "Nuevo nombre"

    def test_renombrar_ejercicio_cambia_grupo_muscular(self, client):
        ex_id = create_exercise(client)["id"]
        r = client.put(f"/exercises/{ex_id}", json={"name": "Press banca", "muscle_group": "Hombro", "muscle_subgroup": None})
        assert r.status_code == 200
        data = r.json()
        assert data["muscle_group"] == "Hombro"
        assert data["muscle_subgroup"] is None

    def test_renombrar_ejercicio_inexistente(self, client):
        r = client.put("/exercises/9999", json={"name": "X", "muscle_group": None, "muscle_subgroup": None})
        assert r.status_code == 404

    def test_renombrar_ejercicio_nombre_vacio(self, client):
        ex_id = create_exercise(client)["id"]
        r = client.put(f"/exercises/{ex_id}", json={"name": "", "muscle_group": None, "muscle_subgroup": None})
        assert r.status_code == 422

    def test_renombrar_persiste_en_lista(self, client):
        ex_id = create_exercise(client)["id"]
        client.put(f"/exercises/{ex_id}", json={"name": "Persistido", "muscle_group": None, "muscle_subgroup": None})
        exercises = client.get("/exercises/").json()
        assert any(e["name"] == "Persistido" for e in exercises)


# ── Routines ───────────────────────────────────────────────────────────────────

class TestRoutines:
    def test_lista_vacia(self, client):
        assert client.get("/routines/").json() == []

    def test_crear_rutina(self, client):
        r = client.post("/routines/", json=VALID_ROUTINE)
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Rutina A"
        assert "id" in data

    def test_schema_completo_rutina(self, client):
        data = client.post("/routines/", json=VALID_ROUTINE).json()
        assert set(data.keys()) == {"id", "name"}
        assert isinstance(data["id"], int)

    @pytest.mark.parametrize("payload", [
        {},            # falta name
        {"name": 42},  # name no es string
    ])
    def test_crear_rutina_invalida(self, client, payload):
        assert client.post("/routines/", json=payload).status_code == 422

    def test_borrar_rutina_existente(self, client):
        r_id = create_routine(client)["id"]
        assert client.delete(f"/routines/{r_id}").status_code == 204

    def test_borrar_rutina_inexistente(self, client):
        assert client.delete("/routines/9999").status_code == 404

    def test_borrar_elimina_de_la_lista(self, client):
        r_id = create_routine(client)["id"]
        client.delete(f"/routines/{r_id}")
        assert all(r["id"] != r_id for r in client.get("/routines/").json())

    def test_renombrar_rutina(self, client):
        r_id = create_routine(client)["id"]
        r = client.put(f"/routines/{r_id}", json={"name": "Rutina B"})
        assert r.status_code == 200
        assert r.json()["name"] == "Rutina B"

    def test_renombrar_rutina_inexistente(self, client):
        r = client.put("/routines/9999", json={"name": "X"})
        assert r.status_code == 404

    def test_renombrar_rutina_nombre_vacio(self, client):
        r_id = create_routine(client)["id"]
        r = client.put(f"/routines/{r_id}", json={"name": ""})
        assert r.status_code == 422

    def test_renombrar_persiste_en_lista(self, client):
        r_id = create_routine(client)["id"]
        client.put(f"/routines/{r_id}", json={"name": "Persistida"})
        routines = client.get("/routines/").json()
        assert any(r["name"] == "Persistida" for r in routines)

    def test_borrar_rutina_limpia_routine_exercises(self, client):
        ex_id = create_exercise(client)["id"]
        r_id  = create_routine(client)["id"]
        create_routine_exercise(client, r_id, ex_id)
        client.delete(f"/routines/{r_id}")
        assert client.get("/gym/routine-exercises/").json() == []

    def test_borrar_rutina_limpia_sessions_y_sets(self, client):
        ex_id = create_exercise(client)["id"]
        r_id  = create_routine(client)["id"]
        s_id  = create_session(client, routine_id=r_id, day_of_week=0)["id"]
        create_set(client, s_id, ex_id)
        client.delete(f"/routines/{r_id}")
        assert client.get("/gym/sessions/").json() == []
        assert client.get("/gym/sets/").json() == []


# ── Routine Exercises ──────────────────────────────────────────────────────────

class TestRoutineExercises:
    def test_lista_vacia(self, client):
        assert client.get("/gym/routine-exercises/").json() == []

    def test_crear_routine_exercise(self, client):
        ex_id = create_exercise(client)["id"]
        r_id  = create_routine(client)["id"]
        r = client.post("/gym/routine-exercises/", json={
            "routine_id": r_id, "exercise_id": ex_id, "day_of_week": 0, "position": 0
        })
        assert r.status_code == 201
        data = r.json()
        assert data["routine_id"]  == r_id
        assert data["exercise_id"] == ex_id
        assert data["day_of_week"] == 0

    def test_schema_completo_routine_exercise(self, client):
        ex_id = create_exercise(client)["id"]
        r_id  = create_routine(client)["id"]
        data = client.post("/gym/routine-exercises/", json={
            "routine_id": r_id, "exercise_id": ex_id, "day_of_week": 1, "position": 0
        }).json()
        assert set(data.keys()) == {"id", "routine_id", "exercise_id", "day_of_week", "position"}

    @pytest.mark.parametrize("payload", [
        {"exercise_id": 1, "day_of_week": 0, "position": 0},   # falta routine_id
        {"routine_id": 1, "day_of_week": 0, "position": 0},    # falta exercise_id
        {"routine_id": 1, "exercise_id": 1},                   # falta day_of_week
    ])
    def test_crear_routine_exercise_invalido(self, client, payload):
        assert client.post("/gym/routine-exercises/", json=payload).status_code == 422

    def test_borrar_routine_exercise_existente(self, client):
        ex_id = create_exercise(client)["id"]
        r_id  = create_routine(client)["id"]
        re_id = create_routine_exercise(client, r_id, ex_id)["id"]
        assert client.delete(f"/gym/routine-exercises/{re_id}").status_code == 204

    def test_borrar_routine_exercise_inexistente(self, client):
        assert client.delete("/gym/routine-exercises/9999").status_code == 404


# ── Sessions ───────────────────────────────────────────────────────────────────

class TestSessions:
    def test_lista_vacia(self, client):
        assert client.get("/gym/sessions/").json() == []

    def test_crear_sesion_minima(self, client):
        r = client.post("/gym/sessions/", json={"date": "2026-05-17"})
        assert r.status_code == 201
        data = r.json()
        assert data["date"] == "2026-05-17"
        assert "id" in data

    def test_crear_sesion_completa(self, client):
        r_id = create_routine(client)["id"]
        r = client.post("/gym/sessions/", json={
            "routine_id": r_id, "day_of_week": 0,
            "date": "2026-05-17", "note": "buen entreno"
        })
        assert r.status_code == 201
        data = r.json()
        assert data["routine_id"]  == r_id
        assert data["day_of_week"] == 0
        assert data["note"]        == "buen entreno"

    def test_schema_completo_sesion(self, client):
        data = create_session(client)
        assert set(data.keys()) == {"id", "routine_id", "day_of_week", "date", "note"}

    def test_falta_date(self, client):
        assert client.post("/gym/sessions/", json={}).status_code == 422

    def test_borrar_sesion_existente(self, client):
        s_id = create_session(client)["id"]
        assert client.delete(f"/gym/sessions/{s_id}").status_code == 204

    def test_borrar_sesion_inexistente(self, client):
        assert client.delete("/gym/sessions/9999").status_code == 404


# ── Sets ───────────────────────────────────────────────────────────────────────

class TestSets:
    def test_lista_sets_sesion_vacia(self, client):
        s_id = create_session(client)["id"]
        assert client.get(f"/gym/sessions/{s_id}/sets/").json() == []

    def test_crear_set(self, client):
        ex_id = create_exercise(client)["id"]
        s_id  = create_session(client)["id"]
        r = client.post("/gym/sets/", json={
            "session_id": s_id, "exercise_id": ex_id,
            "set_number": 1, "weight": 80.0, "reps": 8
        })
        assert r.status_code == 201
        data = r.json()
        assert data["weight"] == 80.0
        assert data["reps"]   == 8

    def test_schema_completo_set(self, client):
        ex_id = create_exercise(client)["id"]
        s_id  = create_session(client)["id"]
        data  = create_set(client, s_id, ex_id)
        assert set(data.keys()) == {"id", "session_id", "exercise_id", "set_number", "weight", "reps", "note"}

    def test_sets_aparecen_bajo_su_sesion(self, client):
        ex_id = create_exercise(client)["id"]
        s_id  = create_session(client)["id"]
        create_set(client, s_id, ex_id, set_number=1)
        create_set(client, s_id, ex_id, set_number=2)
        sets = client.get(f"/gym/sessions/{s_id}/sets/").json()
        assert len(sets) == 2

    def test_sets_no_aparecen_en_otra_sesion(self, client):
        ex_id = create_exercise(client)["id"]
        s1    = create_session(client, date="2026-05-17")["id"]
        s2    = create_session(client, date="2026-05-18")["id"]
        create_set(client, s1, ex_id)
        assert client.get(f"/gym/sessions/{s2}/sets/").json() == []

    @pytest.mark.parametrize("payload", [
        {"exercise_id": 1, "set_number": 1, "weight": 80.0, "reps": 8},  # falta session_id
        {"session_id": 1, "set_number": 1, "weight": 80.0, "reps": 8},   # falta exercise_id
        {"session_id": 1, "exercise_id": 1, "weight": 80.0, "reps": 8},  # falta set_number
        {"session_id": 1, "exercise_id": 1, "set_number": 1, "reps": 8}, # falta weight
        {"session_id": 1, "exercise_id": 1, "set_number": 1, "weight": 80.0}, # falta reps
    ])
    def test_crear_set_invalido(self, client, payload):
        assert client.post("/gym/sets/", json=payload).status_code == 422

    def test_borrar_set_existente(self, client):
        ex_id  = create_exercise(client)["id"]
        s_id   = create_session(client)["id"]
        set_id = create_set(client, s_id, ex_id)["id"]
        assert client.delete(f"/gym/sets/{set_id}").status_code == 204

    def test_borrar_set_inexistente(self, client):
        assert client.delete("/gym/sets/9999").status_code == 404


# ── Escenario completo (S08) ───────────────────────────────────────────────────

class TestEscenarioGym:
    def test_flujo_completo_entreno(self, client):
        # 1. Crear ejercicio y rutina
        ex_id = create_exercise(client, name="Sentadilla", muscle_group="Pierna")["id"]
        r_id  = create_routine(client, name="Rutina Pierna")["id"]

        # 2. Asignar ejercicio al lunes de la rutina
        re_id = create_routine_exercise(client, r_id, ex_id, day=0)["id"]
        res   = client.get("/gym/routine-exercises/").json()
        assert any(re["id"] == re_id for re in res)

        # 3. Crear sesión de entrenamiento
        s_id = create_session(client, date="2026-05-17", routine_id=r_id, day_of_week=0)["id"]
        assert any(s["id"] == s_id for s in client.get("/gym/sessions/").json())

        # 4. Registrar 2 series en la sesión
        set1_id = create_set(client, s_id, ex_id, set_number=1, weight=100.0, reps=5)["id"]
        set2_id = create_set(client, s_id, ex_id, set_number=2, weight=105.0, reps=4)["id"]
        sets = client.get(f"/gym/sessions/{s_id}/sets/").json()
        assert len(sets) == 2

        # 5. Borrar serie 1 y verificar que queda solo la 2
        client.delete(f"/gym/sets/{set1_id}")
        sets = client.get(f"/gym/sessions/{s_id}/sets/").json()
        assert len(sets) == 1
        assert sets[0]["id"] == set2_id

        # 6. Borrar sesión y verificar que desaparece
        client.delete(f"/gym/sessions/{s_id}")
        assert all(s["id"] != s_id for s in client.get("/gym/sessions/").json())

        # 7. Borrar routine exercise, rutina y ejercicio
        client.delete(f"/gym/routine-exercises/{re_id}")
        assert client.get("/gym/routine-exercises/").json() == []

        client.delete(f"/routines/{r_id}")
        assert client.get("/routines/").json() == []

        client.delete(f"/exercises/{ex_id}")
        assert client.get("/exercises/").json() == []
