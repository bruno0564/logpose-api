# Pruebas de integración — Countdowns API
# Nivel: S07 (integración con base de datos)
# Diseño: S04 (particiones equivalentes + valores límite) + S08 (escenario completo)

import pytest

VALID_COUNTDOWN = {"title": "Viaje a Japón", "target_date": "2026-12-25"}
VALID_RECURRING = {"title": "Cumpleaños", "target_date": "2026-08-14", "is_recurring": True}


# ── Helpers ────────────────────────────────────────────────────────────────────

def create_countdown(client, title="Evento", target_date="2026-12-25", is_recurring=False):
    body = {"title": title, "target_date": target_date, "is_recurring": is_recurring}
    return client.post("/countdowns/", json=body).json()


# ── GET /countdowns/ ─────────────────────────────────────────────────────────────

class TestListCountdowns:
    def test_lista_vacia_devuelve_array_vacio(self, client):
        r = client.get("/countdowns/")
        assert r.status_code == 200
        assert r.json() == []

    def test_devuelve_countdowns_existentes(self, client):
        create_countdown(client, "Uno")
        create_countdown(client, "Dos")
        r = client.get("/countdowns/")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_ordenados_por_id_descendente(self, client):
        create_countdown(client, "Primero")
        create_countdown(client, "Segundo")
        titles = [c["title"] for c in client.get("/countdowns/").json()]
        assert titles == ["Segundo", "Primero"]

    def test_schema_de_countdown(self, client):
        create_countdown(client, "Evento", "2026-01-01", True)
        data = client.get("/countdowns/").json()[0]
        assert set(data.keys()) == {"id", "title", "target_date", "is_recurring"}
        assert isinstance(data["id"], int)
        assert isinstance(data["title"], str)
        assert isinstance(data["is_recurring"], bool)


# ── POST /countdowns/ ────────────────────────────────────────────────────────────

class TestCreateCountdown:
    def test_countdown_valido(self, client):
        r = client.post("/countdowns/", json=VALID_COUNTDOWN)
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "Viaje a Japón"
        assert data["target_date"] == "2026-12-25"
        assert data["is_recurring"] is False
        assert "id" in data

    def test_countdown_recurrente(self, client):
        r = client.post("/countdowns/", json=VALID_RECURRING)
        assert r.status_code == 201
        assert r.json()["is_recurring"] is True

    def test_is_recurring_por_defecto_false(self, client):
        r = client.post("/countdowns/", json={"title": "X", "target_date": "2026-05-05"})
        assert r.status_code == 201
        assert r.json()["is_recurring"] is False

    def test_schema_completo_de_respuesta(self, client):
        data = client.post("/countdowns/", json=VALID_COUNTDOWN).json()
        assert set(data.keys()) == {"id", "title", "target_date", "is_recurring"}
        assert isinstance(data["id"], int)

    def test_title_requerido(self, client):
        r = client.post("/countdowns/", json={"target_date": "2026-12-25"})
        assert r.status_code == 422

    def test_target_date_requerido(self, client):
        r = client.post("/countdowns/", json={"title": "Sin fecha"})
        assert r.status_code == 422

    def test_title_vacio_rechazado(self, client):
        r = client.post("/countdowns/", json={"title": "", "target_date": "2026-12-25"})
        assert r.status_code == 422

    def test_fecha_formato_invalido_rechazado(self, client):
        r = client.post("/countdowns/", json={"title": "X", "target_date": "25-12-2026"})
        assert r.status_code == 422

    def test_fecha_inexistente_rechazada(self, client):
        r = client.post("/countdowns/", json={"title": "X", "target_date": "2026-02-30"})
        assert r.status_code == 422

    def test_fecha_con_hora_rechazada(self, client):
        r = client.post("/countdowns/", json={"title": "X", "target_date": "2026-12-25T10:00:00"})
        assert r.status_code == 422

    def test_fecha_pasada_permitida(self, client):
        # Los contadores "hacia atrás" usan fechas pasadas: deben aceptarse.
        r = client.post("/countdowns/", json={"title": "Aniversario", "target_date": "2020-01-01"})
        assert r.status_code == 201

    def test_ids_son_unicos(self, client):
        id1 = create_countdown(client, "Uno")["id"]
        id2 = create_countdown(client, "Dos")["id"]
        assert id1 != id2


# ── PUT /countdowns/{id} ─────────────────────────────────────────────────────────

class TestUpdateCountdown:
    def test_actualizar_titulo(self, client):
        c = create_countdown(client, "Original")
        r = client.put(f"/countdowns/{c['id']}", json={"title": "Nuevo", "target_date": c["target_date"]})
        assert r.status_code == 200
        assert r.json()["title"] == "Nuevo"

    def test_actualizar_fecha(self, client):
        c = create_countdown(client, "Evento", "2026-01-01")
        r = client.put(f"/countdowns/{c['id']}", json={"title": "Evento", "target_date": "2027-01-01"})
        assert r.status_code == 200
        assert r.json()["target_date"] == "2027-01-01"

    def test_actualizar_is_recurring(self, client):
        c = create_countdown(client, "Cumple", "2026-08-14", False)
        r = client.put(f"/countdowns/{c['id']}", json={"title": "Cumple", "target_date": "2026-08-14", "is_recurring": True})
        assert r.status_code == 200
        assert r.json()["is_recurring"] is True

    def test_actualizar_countdown_inexistente_devuelve_404(self, client):
        r = client.put("/countdowns/9999", json={"title": "X", "target_date": "2026-12-25"})
        assert r.status_code == 404

    def test_fecha_invalida_en_put_rechazada(self, client):
        c = create_countdown(client)
        r = client.put(f"/countdowns/{c['id']}", json={"title": "X", "target_date": "nope"})
        assert r.status_code == 422

    def test_cambios_persisten_en_get(self, client):
        c = create_countdown(client, "Original", "2026-01-01")
        client.put(f"/countdowns/{c['id']}", json={"title": "Cambiado", "target_date": "2026-06-06", "is_recurring": True})
        data = client.get("/countdowns/").json()[0]
        assert data["title"] == "Cambiado"
        assert data["target_date"] == "2026-06-06"
        assert data["is_recurring"] is True

    def test_id_no_cambia_tras_actualizar(self, client):
        c = create_countdown(client, "Original")
        updated = client.put(f"/countdowns/{c['id']}", json={"title": "Nuevo", "target_date": "2026-12-25"}).json()
        assert updated["id"] == c["id"]


# ── DELETE /countdowns/{id} ──────────────────────────────────────────────────────

class TestDeleteCountdown:
    def test_borrar_countdown_existente(self, client):
        c = create_countdown(client)
        r = client.delete(f"/countdowns/{c['id']}")
        assert r.status_code == 204

    def test_countdown_ya_no_aparece_tras_borrar(self, client):
        c = create_countdown(client)
        client.delete(f"/countdowns/{c['id']}")
        assert client.get("/countdowns/").json() == []

    def test_borrar_countdown_inexistente_devuelve_404(self, client):
        r = client.delete("/countdowns/9999")
        assert r.status_code == 404

    def test_borrar_uno_no_afecta_a_otros(self, client):
        c1 = create_countdown(client, "Uno")
        c2 = create_countdown(client, "Dos")
        client.delete(f"/countdowns/{c1['id']}")
        rows = client.get("/countdowns/").json()
        assert len(rows) == 1
        assert rows[0]["id"] == c2["id"]


# ── Escenario completo ───────────────────────────────────────────────────────────

class TestEscenarioCompleto:
    def test_flujo_completo_crud(self, client):
        # Crear
        c = client.post("/countdowns/", json={"title": "Examen", "target_date": "2026-09-01"}).json()
        assert c["title"] == "Examen"

        # Leer
        rows = client.get("/countdowns/").json()
        assert len(rows) == 1

        # Editar (marcar como recurrente y cambiar fecha)
        updated = client.put(f"/countdowns/{c['id']}", json={"title": "Examen final", "target_date": "2026-09-15", "is_recurring": True}).json()
        assert updated["title"] == "Examen final"
        assert updated["is_recurring"] is True

        # Verificar persistencia
        rows = client.get("/countdowns/").json()
        assert rows[0]["target_date"] == "2026-09-15"

        # Borrar
        client.delete(f"/countdowns/{c['id']}")
        assert client.get("/countdowns/").json() == []

    def test_mezcla_futuros_pasados_y_recurrentes(self, client):
        create_countdown(client, "Futuro", "2099-01-01")
        create_countdown(client, "Pasado", "2000-01-01")
        create_countdown(client, "Anual", "2026-08-14", True)
        rows = client.get("/countdowns/").json()
        assert len(rows) == 3
        recurring = {c["title"]: c["is_recurring"] for c in rows}
        assert recurring["Anual"] is True
        assert recurring["Futuro"] is False
