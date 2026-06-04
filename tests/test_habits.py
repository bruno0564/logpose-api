# Pruebas de integración — Habits API
# Endpoints: /habits/categories, /habits/, /habits/logs
# Diseño: particiones equivalentes + escenario completo

import pytest

VALID_CATEGORY = {"name": "Productividad", "color": "#7c3aed"}
VALID_HABIT    = {"name": "Leer 1h", "goal": 30}


# ── Helpers ────────────────────────────────────────────────────────────────────

def create_category(client, **kwargs):
    data = {**VALID_CATEGORY, **kwargs}
    return client.post("/habits/categories", json=data).json()

def create_habit(client, category_id, **kwargs):
    data = {**VALID_HABIT, "category_id": category_id, **kwargs}
    return client.post("/habits/", json=data).json()

def create_log(client, habit_id, date="2026-06-04"):
    return client.post("/habits/logs", json={"habit_id": habit_id, "date": date}).json()


# ── Categories ─────────────────────────────────────────────────────────────────

class TestHabitCategories:
    def test_lista_vacia(self, client):
        assert client.get("/habits/categories").json() == []

    def test_crear_categoria_completa(self, client):
        r = client.post("/habits/categories", json=VALID_CATEGORY)
        assert r.status_code == 201
        data = r.json()
        assert data["name"]  == "Productividad"
        assert data["color"] == "#7c3aed"
        assert "id" in data

    def test_crear_categoria_color_por_defecto(self, client):
        r = client.post("/habits/categories", json={"name": "Salud"})
        assert r.status_code == 201
        assert r.json()["color"] == "#7c3aed"

    def test_schema_completo_categoria(self, client):
        data = create_category(client)
        assert set(data.keys()) == {"id", "name", "color"}
        assert isinstance(data["id"], int)

    def test_varias_categorias_en_lista(self, client):
        create_category(client, name="A")
        create_category(client, name="B")
        cats = client.get("/habits/categories").json()
        assert len(cats) == 2

    @pytest.mark.parametrize("payload", [
        {},             # falta name
        {"name": 123},  # name no es string
    ])
    def test_crear_categoria_invalida(self, client, payload):
        assert client.post("/habits/categories", json=payload).status_code == 422

    def test_actualizar_categoria(self, client):
        cat_id = create_category(client)["id"]
        r = client.put(f"/habits/categories/{cat_id}", json={"name": "Higiene", "color": "#dc2626"})
        assert r.status_code == 200
        data = r.json()
        assert data["name"]  == "Higiene"
        assert data["color"] == "#dc2626"

    def test_actualizar_categoria_inexistente(self, client):
        r = client.put("/habits/categories/9999", json={"name": "X", "color": "#000"})
        assert r.status_code == 404

    def test_actualizar_persiste_en_lista(self, client):
        cat_id = create_category(client)["id"]
        client.put(f"/habits/categories/{cat_id}", json={"name": "Actualizada", "color": "#16a34a"})
        cats = client.get("/habits/categories").json()
        assert any(c["name"] == "Actualizada" for c in cats)

    def test_borrar_categoria_existente(self, client):
        cat_id = create_category(client)["id"]
        assert client.delete(f"/habits/categories/{cat_id}").status_code == 204

    def test_borrar_categoria_inexistente(self, client):
        assert client.delete("/habits/categories/9999").status_code == 404

    def test_borrar_categoria_elimina_de_lista(self, client):
        cat_id = create_category(client)["id"]
        client.delete(f"/habits/categories/{cat_id}")
        assert all(c["id"] != cat_id for c in client.get("/habits/categories").json())

    def test_borrar_categoria_limpia_habitos(self, client):
        cat_id = create_category(client)["id"]
        create_habit(client, cat_id)
        client.delete(f"/habits/categories/{cat_id}")
        assert client.get("/habits/").json() == []

    def test_borrar_categoria_limpia_logs(self, client):
        cat_id  = create_category(client)["id"]
        hab_id  = create_habit(client, cat_id)["id"]
        create_log(client, hab_id)
        client.delete(f"/habits/categories/{cat_id}")
        assert client.get("/habits/logs").json() == []


# ── Habits ─────────────────────────────────────────────────────────────────────

class TestHabits:
    def test_lista_vacia(self, client):
        assert client.get("/habits/").json() == []

    def test_crear_habito_completo(self, client):
        cat_id = create_category(client)["id"]
        r = client.post("/habits/", json={"category_id": cat_id, "name": "Leer 1h", "goal": 30, "position": 0})
        assert r.status_code == 201
        data = r.json()
        assert data["name"]        == "Leer 1h"
        assert data["goal"]        == 30
        assert data["category_id"] == cat_id
        assert "id" in data

    def test_crear_habito_goal_por_defecto(self, client):
        cat_id = create_category(client)["id"]
        r = client.post("/habits/", json={"category_id": cat_id, "name": "Meditar"})
        assert r.status_code == 201
        assert r.json()["goal"] == 30

    def test_schema_completo_habito(self, client):
        cat_id = create_category(client)["id"]
        data = create_habit(client, cat_id)
        assert set(data.keys()) == {"id", "category_id", "name", "goal", "position"}

    def test_habito_goal_personalizado(self, client):
        cat_id = create_category(client)["id"]
        r = client.post("/habits/", json={"category_id": cat_id, "name": "Cambiar funda", "goal": 12})
        assert r.status_code == 201
        assert r.json()["goal"] == 12

    @pytest.mark.parametrize("payload", [
        {"name": "Sin cat", "goal": 30},                   # falta category_id
        {"category_id": 1, "goal": 30},                    # falta name
        {"category_id": 1, "name": "X", "goal": 0},        # goal < 1
        {"category_id": 1, "name": "X", "goal": 32},       # goal > 31
        {"category_id": 1, "name": 999, "goal": 30},       # name no es string
    ])
    def test_crear_habito_invalido(self, client, payload):
        assert client.post("/habits/", json=payload).status_code == 422

    def test_actualizar_habito(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        r = client.put(f"/habits/{hab_id}", json={"name": "Leer 30min", "goal": 20, "position": 1})
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Leer 30min"
        assert data["goal"] == 20

    def test_actualizar_habito_inexistente(self, client):
        r = client.put("/habits/9999", json={"name": "X", "goal": 30, "position": 0})
        assert r.status_code == 404

    def test_actualizar_persiste_en_lista(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        client.put(f"/habits/{hab_id}", json={"name": "Persistido", "goal": 15, "position": 0})
        habits = client.get("/habits/").json()
        assert any(h["name"] == "Persistido" for h in habits)

    def test_borrar_habito_existente(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        assert client.delete(f"/habits/{hab_id}").status_code == 204

    def test_borrar_habito_inexistente(self, client):
        assert client.delete("/habits/9999").status_code == 404

    def test_borrar_habito_elimina_de_lista(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        client.delete(f"/habits/{hab_id}")
        assert all(h["id"] != hab_id for h in client.get("/habits/").json())

    def test_borrar_habito_limpia_sus_logs(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        create_log(client, hab_id)
        client.delete(f"/habits/{hab_id}")
        assert client.get("/habits/logs").json() == []

    def test_varios_habitos_en_misma_categoria(self, client):
        cat_id = create_category(client)["id"]
        create_habit(client, cat_id, name="H1")
        create_habit(client, cat_id, name="H2")
        habits = client.get("/habits/").json()
        assert len(habits) == 2
        assert all(h["category_id"] == cat_id for h in habits)


# ── Logs ───────────────────────────────────────────────────────────────────────

class TestHabitLogs:
    def test_lista_vacia(self, client):
        assert client.get("/habits/logs").json() == []

    def test_crear_log(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        r = client.post("/habits/logs", json={"habit_id": hab_id, "date": "2026-06-04"})
        assert r.status_code == 201
        data = r.json()
        assert data["habit_id"] == hab_id
        assert data["date"]     == "2026-06-04"
        assert "id" in data

    def test_schema_completo_log(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        data = create_log(client, hab_id)
        assert set(data.keys()) == {"id", "habit_id", "date"}

    @pytest.mark.parametrize("payload", [
        {"date": "2026-06-04"},                      # falta habit_id
        {"habit_id": 1},                              # falta date
        {"habit_id": 1, "date": "04-06-2026"},        # formato de fecha incorrecto
        {"habit_id": "abc", "date": "2026-06-04"},    # habit_id no es int
    ])
    def test_crear_log_invalido(self, client, payload):
        assert client.post("/habits/logs", json=payload).status_code == 422

    def test_filtrar_logs_por_mes(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        create_log(client, hab_id, date="2026-06-01")
        create_log(client, hab_id, date="2026-06-15")
        create_log(client, hab_id, date="2026-07-01")
        logs_junio = client.get("/habits/logs?month=2026-06").json()
        assert len(logs_junio) == 2
        assert all(l["date"].startswith("2026-06") for l in logs_junio)

    def test_filtrar_mes_sin_logs(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        create_log(client, hab_id, date="2026-06-01")
        assert client.get("/habits/logs?month=2026-05").json() == []

    def test_sin_filtro_devuelve_todos(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        create_log(client, hab_id, date="2026-05-01")
        create_log(client, hab_id, date="2026-06-01")
        assert len(client.get("/habits/logs").json()) == 2

    def test_logs_ordenados_por_fecha(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        create_log(client, hab_id, date="2026-06-15")
        create_log(client, hab_id, date="2026-06-03")
        create_log(client, hab_id, date="2026-06-10")
        dates = [l["date"] for l in client.get("/habits/logs").json()]
        assert dates == sorted(dates)

    def test_borrar_log_existente(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        log_id = create_log(client, hab_id)["id"]
        assert client.delete(f"/habits/logs/{log_id}").status_code == 204

    def test_borrar_log_inexistente(self, client):
        assert client.delete("/habits/logs/9999").status_code == 404

    def test_borrar_log_elimina_de_lista(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        log_id = create_log(client, hab_id)["id"]
        client.delete(f"/habits/logs/{log_id}")
        assert client.get("/habits/logs").json() == []

    def test_dos_logs_mismo_habito_dias_distintos(self, client):
        cat_id = create_category(client)["id"]
        hab_id = create_habit(client, cat_id)["id"]
        create_log(client, hab_id, date="2026-06-01")
        create_log(client, hab_id, date="2026-06-02")
        assert len(client.get("/habits/logs").json()) == 2

    def test_logs_de_distintos_habitos(self, client):
        cat_id = create_category(client)["id"]
        h1 = create_habit(client, cat_id, name="H1")["id"]
        h2 = create_habit(client, cat_id, name="H2")["id"]
        create_log(client, h1, date="2026-06-01")
        create_log(client, h2, date="2026-06-01")
        logs = client.get("/habits/logs").json()
        assert len(logs) == 2
        assert {l["habit_id"] for l in logs} == {h1, h2}


# ── Escenario completo ─────────────────────────────────────────────────────────

class TestEscenarioHabits:
    def test_flujo_completo_tracker(self, client):
        # 1. Crear dos categorías
        cat_prod = create_category(client, name="Productividad", color="#7c3aed")["id"]
        cat_fis  = create_category(client, name="Físico",        color="#16a34a")["id"]
        cats = client.get("/habits/categories").json()
        assert len(cats) == 2

        # 2. Crear hábitos en cada categoría
        leer  = create_habit(client, cat_prod, name="Leer 1h",   goal=30)["id"]
        estud = create_habit(client, cat_prod, name="Estudiar",   goal=25)["id"]
        gym   = create_habit(client, cat_fis,  name="Gym",        goal=20)["id"]

        habits = client.get("/habits/").json()
        assert len(habits) == 3
        assert all(h["category_id"] in {cat_prod, cat_fis} for h in habits)

        # 3. Marcar días: leer los días 1-5, estudiar 3 días, gym 2 días
        for d in range(1, 6):
            create_log(client, leer,  date=f"2026-06-{d:02d}")
        for d in [1, 3, 5]:
            create_log(client, estud, date=f"2026-06-{d:02d}")
        create_log(client, gym, date="2026-06-01")
        create_log(client, gym, date="2026-06-03")

        logs_junio = client.get("/habits/logs?month=2026-06").json()
        assert len(logs_junio) == 10

        # 4. Verificar filtro por mes: julio no tiene nada
        assert client.get("/habits/logs?month=2026-07").json() == []

        # 5. Borrar un log suelto (desmarcar un día)
        log_leer_1 = next(l for l in logs_junio if l["habit_id"] == leer and l["date"] == "2026-06-01")
        client.delete(f"/habits/logs/{log_leer_1['id']}")
        assert len(client.get("/habits/logs?month=2026-06").json()) == 9

        # 6. Editar un hábito
        r = client.put(f"/habits/{estud}", json={"name": "Estudiar 2h", "goal": 20, "position": 1})
        assert r.status_code == 200
        assert r.json()["name"] == "Estudiar 2h"

        # 7. Borrar un hábito → sus logs desaparecen
        client.delete(f"/habits/{gym}")
        assert all(h["id"] != gym for h in client.get("/habits/").json())
        assert all(l["habit_id"] != gym for l in client.get("/habits/logs").json())

        # 8. Borrar una categoría entera → sus hábitos y logs desaparecen
        client.delete(f"/habits/categories/{cat_prod}")
        assert all(c["id"] != cat_prod for c in client.get("/habits/categories").json())
        assert client.get("/habits/").json() == []
        assert client.get("/habits/logs").json() == []

        # 9. Solo queda la categoría Físico (sin hábitos porque gym fue borrado)
        cats = client.get("/habits/categories").json()
        assert len(cats) == 1
        assert cats[0]["id"] == cat_fis
