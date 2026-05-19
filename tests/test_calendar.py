# Pruebas de integración — Calendar API
# Nivel: S07 (integración con base de datos)
# Diseño: S04 (particiones equivalentes + valores límite) + S08 (escenario completo)

import pytest

VALID_EVENT = {
    "title": "Reunión de equipo",
    "date": "2025-06-15",
    "start_time": "10:00",
    "end_time": "11:00",
    "recurrence": "none",
    "days_of_week": None,
    "notes": "Traer portátil",
    "color": "#7c3aed",
}

VALID_EVENT_MINIMAL = {
    "title": "Evento sin detalles",
    "recurrence": "none",
}

VALID_EVENT_WEEKLY = {
    "title": "Gym",
    "recurrence": "weekly",
    "days_of_week": "0,2,4",
    "color": "#16a34a",
}

VALID_EVENT_DAILY = {
    "title": "Meditación",
    "recurrence": "daily",
    "start_time": "07:00",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def create_event(client, **kwargs):
    body = {"title": "Evento de prueba", "recurrence": "none"}
    body.update(kwargs)
    return client.post("/calendar/", json=body).json()


# ── GET /calendar/ ─────────────────────────────────────────────────────────────

class TestListEvents:
    def test_lista_vacia_devuelve_array_vacio(self, client):
        r = client.get("/calendar/")
        assert r.status_code == 200
        assert r.json() == []

    def test_devuelve_eventos_existentes(self, client):
        create_event(client, title="Evento 1")
        create_event(client, title="Evento 2")
        r = client.get("/calendar/")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_ordenados_por_id_ascendente(self, client):
        create_event(client, title="Primero")
        create_event(client, title="Segundo")
        titles = [e["title"] for e in client.get("/calendar/").json()]
        assert titles == ["Primero", "Segundo"]

    def test_schema_de_evento(self, client):
        create_event(client, **VALID_EVENT)
        data = client.get("/calendar/").json()[0]
        expected_keys = {"id", "title", "date", "start_time", "end_time", "recurrence", "days_of_week", "notes", "color"}
        assert set(data.keys()) == expected_keys
        assert isinstance(data["id"], int)
        assert isinstance(data["title"], str)


# ── POST /calendar/ ────────────────────────────────────────────────────────────

class TestCreateEvent:
    def test_evento_completo(self, client):
        r = client.post("/calendar/", json=VALID_EVENT)
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "Reunión de equipo"
        assert data["date"] == "2025-06-15"
        assert data["start_time"] == "10:00"
        assert data["end_time"] == "11:00"
        assert data["recurrence"] == "none"
        assert data["notes"] == "Traer portátil"
        assert data["color"] == "#7c3aed"
        assert "id" in data

    def test_evento_minimal(self, client):
        r = client.post("/calendar/", json=VALID_EVENT_MINIMAL)
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "Evento sin detalles"
        assert data["date"] is None
        assert data["start_time"] is None
        assert data["end_time"] is None
        assert data["notes"] is None

    def test_evento_semanal(self, client):
        r = client.post("/calendar/", json=VALID_EVENT_WEEKLY)
        assert r.status_code == 201
        data = r.json()
        assert data["recurrence"] == "weekly"
        assert data["days_of_week"] == "0,2,4"

    def test_evento_diario(self, client):
        r = client.post("/calendar/", json=VALID_EVENT_DAILY)
        assert r.status_code == 201
        assert r.json()["recurrence"] == "daily"

    def test_title_requerido(self, client):
        r = client.post("/calendar/", json={"date": "2025-06-15"})
        assert r.status_code == 422

    def test_body_vacio_rechazado(self, client):
        r = client.post("/calendar/", json={})
        assert r.status_code == 422

    def test_ids_son_unicos(self, client):
        id1 = create_event(client, title="Evento 1")["id"]
        id2 = create_event(client, title="Evento 2")["id"]
        assert id1 != id2

    def test_multiples_eventos_mismo_titulo(self, client):
        r1 = client.post("/calendar/", json={"title": "Duplicado", "recurrence": "none"})
        r2 = client.post("/calendar/", json={"title": "Duplicado", "recurrence": "none"})
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["id"] != r2.json()["id"]

    @pytest.mark.parametrize("recurrence", ["monthly", "DAILY", "weekly_custom", "", "nunca"])
    def test_recurrencia_invalida_rechazada(self, client, recurrence):
        r = client.post("/calendar/", json={"title": "X", "recurrence": recurrence})
        assert r.status_code == 422


# ── PUT /calendar/{event_id} ───────────────────────────────────────────────────

class TestUpdateEvent:
    def test_actualizar_titulo(self, client):
        ev = create_event(client, title="Original")
        r = client.put(f"/calendar/{ev['id']}", json={"title": "Actualizado", "recurrence": "none"})
        assert r.status_code == 200
        assert r.json()["title"] == "Actualizado"

    def test_actualizar_fecha(self, client):
        ev = create_event(client, title="Evento", date="2025-01-01")
        r = client.put(f"/calendar/{ev['id']}", json={"title": "Evento", "recurrence": "none", "date": "2025-12-31"})
        assert r.status_code == 200
        assert r.json()["date"] == "2025-12-31"

    def test_cambiar_recurrencia(self, client):
        ev = create_event(client, title="Evento", recurrence="none")
        r = client.put(f"/calendar/{ev['id']}", json={"title": "Evento", "recurrence": "daily"})
        assert r.status_code == 200
        assert r.json()["recurrence"] == "daily"

    def test_actualizar_evento_inexistente_devuelve_404(self, client):
        r = client.put("/calendar/9999", json={"title": "X", "recurrence": "none"})
        assert r.status_code == 404

    def test_schema_de_respuesta(self, client):
        ev = create_event(client)
        data = client.put(f"/calendar/{ev['id']}", json={"title": "T", "recurrence": "none"}).json()
        expected_keys = {"id", "title", "date", "start_time", "end_time", "recurrence", "days_of_week", "notes", "color"}
        assert set(data.keys()) == expected_keys

    def test_id_no_cambia_tras_actualizar(self, client):
        ev = create_event(client)
        updated = client.put(f"/calendar/{ev['id']}", json={"title": "Nuevo", "recurrence": "none"}).json()
        assert updated["id"] == ev["id"]

    @pytest.mark.parametrize("recurrence", ["monthly", "DAILY", "weekly_custom", ""])
    def test_recurrencia_invalida_en_put(self, client, recurrence):
        ev = create_event(client)
        r = client.put(f"/calendar/{ev['id']}", json={"title": "X", "recurrence": recurrence})
        assert r.status_code == 422

    def test_cambios_persisten_en_get(self, client):
        ev = create_event(client, title="Original")
        client.put(f"/calendar/{ev['id']}", json={"title": "Cambiado", "recurrence": "none", "date": "2025-09-01"})
        events = client.get("/calendar/").json()
        assert events[0]["title"] == "Cambiado"
        assert events[0]["date"] == "2025-09-01"


# ── DELETE /calendar/{event_id} ────────────────────────────────────────────────

class TestDeleteEvent:
    def test_borrar_evento_existente(self, client):
        ev = create_event(client)
        r = client.delete(f"/calendar/{ev['id']}")
        assert r.status_code == 204

    def test_evento_ya_no_aparece_tras_borrar(self, client):
        ev = create_event(client)
        client.delete(f"/calendar/{ev['id']}")
        assert client.get("/calendar/").json() == []

    def test_borrar_evento_inexistente_devuelve_404(self, client):
        r = client.delete("/calendar/9999")
        assert r.status_code == 404

    def test_borrar_uno_no_afecta_a_otros(self, client):
        ev1 = create_event(client, title="Evento 1")
        ev2 = create_event(client, title="Evento 2")
        client.delete(f"/calendar/{ev1['id']}")
        events = client.get("/calendar/").json()
        assert len(events) == 1
        assert events[0]["id"] == ev2["id"]


# ── Escenario completo ─────────────────────────────────────────────────────────

class TestEscenarioCompleto:
    def test_flujo_completo_crud(self, client):
        # Crear
        ev = client.post("/calendar/", json={
            "title": "Dentista", "date": "2025-07-10",
            "start_time": "09:00", "recurrence": "none",
        }).json()
        assert ev["title"] == "Dentista"

        # Leer
        events = client.get("/calendar/").json()
        assert len(events) == 1

        # Editar
        updated = client.put(f"/calendar/{ev['id']}", json={
            "title": "Dentista (confirmado)", "date": "2025-07-10",
            "start_time": "09:30", "recurrence": "none",
        }).json()
        assert updated["title"] == "Dentista (confirmado)"
        assert updated["start_time"] == "09:30"

        # Verificar persistencia
        assert client.get("/calendar/").json()[0]["title"] == "Dentista (confirmado)"

        # Borrar
        client.delete(f"/calendar/{ev['id']}")
        assert client.get("/calendar/").json() == []

    def test_mezcla_de_recurrencias(self, client):
        create_event(client, title="Una vez", recurrence="none", date="2025-08-01")
        create_event(client, title="Diario", recurrence="daily")
        create_event(client, title="Semanal", recurrence="weekly", days_of_week="1,3")
        events = client.get("/calendar/").json()
        assert len(events) == 3
        recs = {e["title"]: e["recurrence"] for e in events}
        assert recs["Una vez"] == "none"
        assert recs["Diario"] == "daily"
        assert recs["Semanal"] == "weekly"

    def test_evento_sin_hora_tiene_campos_none(self, client):
        ev = create_event(client, title="Todo el día", date="2025-05-20")
        data = client.get("/calendar/").json()[0]
        assert data["start_time"] is None
        assert data["end_time"] is None
