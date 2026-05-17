# Pruebas de integración — Body Weight API
# Nivel: S07 (integración con base de datos)
# Diseño: S04 (particiones equivalentes + valores límite) + S08 (escenario completo)

import pytest
from datetime import date

VALID_ENTRY = {"weight": 75.5, "date": "2026-05-17", "note": "después de entrenar"}
VALID_ENTRY_NO_NOTE = {"weight": 80.0, "date": "2026-05-16"}


# ── GET /body-weight/ ──────────────────────────────────────────────────────────

class TestListEntries:
    def test_lista_vacia_devuelve_array_vacio(self, client):
        r = client.get("/body-weight/")
        assert r.status_code == 200
        assert r.json() == []

    def test_lista_devuelve_entradas_existentes(self, client):
        client.post("/body-weight/", json=VALID_ENTRY)
        r = client.get("/body-weight/")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_lista_ordenada_por_fecha_descendente(self, client):
        # 5 fechas desordenadas — el resultado debe estar exactamente en orden descendente
        dates = ["2026-05-01", "2026-05-17", "2026-03-15", "2026-04-30", "2026-05-10"]
        for d in dates:
            client.post("/body-weight/", json={"weight": 75.0, "date": d})
        returned = [e["date"] for e in client.get("/body-weight/").json()]
        assert returned == sorted(dates, reverse=True)


# ── POST /body-weight/ ─────────────────────────────────────────────────────────

class TestCreateEntry:
    def test_entrada_valida_completa(self, client):
        r = client.post("/body-weight/", json=VALID_ENTRY)
        assert r.status_code == 201
        data = r.json()
        assert data["weight"] == 75.5
        assert data["date"] == "2026-05-17"
        assert data["note"] == "después de entrenar"
        assert "id" in data

    def test_entrada_valida_sin_nota(self, client):
        r = client.post("/body-weight/", json=VALID_ENTRY_NO_NOTE)
        assert r.status_code == 201
        assert r.json()["note"] is None

    def test_schema_completo_de_respuesta(self, client):
        # Verifica que la respuesta tiene exactamente los campos esperados con los tipos correctos
        data = client.post("/body-weight/", json=VALID_ENTRY).json()
        assert set(data.keys()) == {"id", "weight", "date", "note"}
        assert isinstance(data["id"], int)
        assert isinstance(data["weight"], float)
        assert isinstance(data["note"], str)
        date.fromisoformat(data["date"])  # lanza ValueError si el formato no es ISO 8601

    @pytest.mark.parametrize("payload", [
        {"date": "2026-05-17"},                              # falta weight
        {"weight": 75.5},                                    # falta date
        {"weight": "pesado", "date": "2026-05-17"},          # weight no es número
        {"weight": 75.5, "date": "17-05-2026"},              # formato de fecha incorrecto
        {"weight": -10.0, "date": "2026-05-17"},             # peso negativo
        {"weight": 0.0, "date": "2026-05-17"},               # peso cero
        {"weight": -0.001, "date": "2026-05-17"},            # límite inferior negativo
    ])
    def test_entrada_invalida_devuelve_422(self, client, payload):
        assert client.post("/body-weight/", json=payload).status_code == 422


# ── PUT /body-weight/{id} ──────────────────────────────────────────────────────

class TestUpdateEntry:
    def test_actualizar_entrada_existente(self, client):
        entry_id = client.post("/body-weight/", json=VALID_ENTRY).json()["id"]
        r = client.put(f"/body-weight/{entry_id}", json={"weight": 78.0, "date": "2026-05-18"})
        assert r.status_code == 200
        data = r.json()
        assert data["weight"] == 78.0
        assert data["date"] == "2026-05-18"
        assert data["note"] is None

    def test_actualizar_con_nota(self, client):
        entry_id = client.post("/body-weight/", json=VALID_ENTRY_NO_NOTE).json()["id"]
        r = client.put(f"/body-weight/{entry_id}", json={"weight": 80.0, "date": "2026-05-16", "note": "nueva nota"})
        assert r.status_code == 200
        assert r.json()["note"] == "nueva nota"

    def test_actualizar_entrada_inexistente(self, client):
        r = client.put("/body-weight/9999", json={"weight": 78.0, "date": "2026-05-18"})
        assert r.status_code == 404

    @pytest.mark.parametrize("payload", [
        {"weight": -5.0, "date": "2026-05-17"},   # peso negativo en edición
        {"weight": 0.0, "date": "2026-05-17"},    # peso cero en edición
    ])
    def test_actualizar_con_peso_invalido_devuelve_422(self, client, payload):
        entry_id = client.post("/body-weight/", json=VALID_ENTRY).json()["id"]
        assert client.put(f"/body-weight/{entry_id}", json=payload).status_code == 422


# ── DELETE /body-weight/{id} ───────────────────────────────────────────────────

class TestDeleteEntry:
    def test_borrar_entrada_existente(self, client):
        entry_id = client.post("/body-weight/", json=VALID_ENTRY).json()["id"]
        assert client.delete(f"/body-weight/{entry_id}").status_code == 204

    def test_borrar_elimina_de_la_lista(self, client):
        entry_id = client.post("/body-weight/", json=VALID_ENTRY).json()["id"]
        client.delete(f"/body-weight/{entry_id}")
        assert all(e["id"] != entry_id for e in client.get("/body-weight/").json())

    def test_borrar_entrada_inexistente(self, client):
        assert client.delete("/body-weight/9999").status_code == 404


# ── Escenario completo (S08 — prueba de sistema) ───────────────────────────────

class TestEscenarioCRUD:
    def test_flujo_completo_crear_leer_editar_borrar(self, client):
        # Crear
        r = client.post("/body-weight/", json=VALID_ENTRY)
        assert r.status_code == 201
        entry_id = r.json()["id"]

        # Leer — aparece en lista
        entries = client.get("/body-weight/").json()
        assert any(e["id"] == entry_id for e in entries)

        # Editar
        r = client.put(f"/body-weight/{entry_id}", json={"weight": 80.0, "date": "2026-05-18", "note": "editado"})
        assert r.status_code == 200
        assert r.json()["weight"] == 80.0

        # Verificar edición en lista
        entry = next(e for e in client.get("/body-weight/").json() if e["id"] == entry_id)
        assert entry["weight"] == 80.0
        assert entry["note"] == "editado"

        # Borrar
        assert client.delete(f"/body-weight/{entry_id}").status_code == 204

        # Verificar que desapareció
        assert all(e["id"] != entry_id for e in client.get("/body-weight/").json())
