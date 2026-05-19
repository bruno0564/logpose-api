# Pruebas de integración — Journal API
# Nivel: S07 (integración con base de datos)
# Diseño: S04 (particiones equivalentes + valores límite) + S08 (escenario completo)

import pytest

VALID_ENTRY = {"date": "2026-05-19", "content": "Hoy ha sido un buen día."}
VALID_ENTRY_EMPTY_CONTENT = {"date": "2026-05-20", "content": ""}


# ── Helpers ────────────────────────────────────────────────────────────────────

def create_entry(client, date="2026-05-19", content="Entrada de prueba"):
    return client.post("/journal/", json={"date": date, "content": content}).json()


# ── GET /journal/ ──────────────────────────────────────────────────────────────

class TestListEntries:
    def test_lista_vacia_devuelve_array_vacio(self, client):
        r = client.get("/journal/")
        assert r.status_code == 200
        assert r.json() == []

    def test_devuelve_entradas_existentes(self, client):
        create_entry(client, "2026-05-18")
        create_entry(client, "2026-05-19")
        r = client.get("/journal/")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_ordenadas_por_fecha_descendente(self, client):
        create_entry(client, "2026-05-17", "Primero")
        create_entry(client, "2026-05-19", "Tercero")
        create_entry(client, "2026-05-18", "Segundo")
        dates = [e["date"] for e in client.get("/journal/").json()]
        assert dates == ["2026-05-19", "2026-05-18", "2026-05-17"]

    def test_schema_de_entrada(self, client):
        create_entry(client)
        data = client.get("/journal/").json()[0]
        assert set(data.keys()) == {"id", "date", "content"}
        assert isinstance(data["id"], int)
        assert isinstance(data["date"], str)
        assert isinstance(data["content"], str)


# ── POST /journal/ ─────────────────────────────────────────────────────────────

class TestCreateEntry:
    def test_entrada_valida_con_contenido(self, client):
        r = client.post("/journal/", json=VALID_ENTRY)
        assert r.status_code == 201
        data = r.json()
        assert data["date"] == "2026-05-19"
        assert data["content"] == "Hoy ha sido un buen día."
        assert "id" in data

    def test_entrada_valida_sin_contenido(self, client):
        r = client.post("/journal/", json=VALID_ENTRY_EMPTY_CONTENT)
        assert r.status_code == 201
        assert r.json()["content"] == ""

    def test_content_tiene_valor_por_defecto_vacio(self, client):
        r = client.post("/journal/", json={"date": "2026-05-19"})
        assert r.status_code == 201
        assert r.json()["content"] == ""

    def test_schema_completo_de_respuesta(self, client):
        data = client.post("/journal/", json=VALID_ENTRY).json()
        assert set(data.keys()) == {"id", "date", "content"}
        assert isinstance(data["id"], int)

    def test_date_requerida(self, client):
        r = client.post("/journal/", json={"content": "Sin fecha"})
        assert r.status_code == 422

    def test_date_formato_invalido(self, client):
        r = client.post("/journal/", json={"date": "19-05-2026", "content": "Mal formato"})
        assert r.status_code == 422

    def test_date_formato_invalido_texto(self, client):
        r = client.post("/journal/", json={"date": "hoy", "content": "Texto"})
        assert r.status_code == 422

    def test_body_vacio_rechazado(self, client):
        r = client.post("/journal/", json={})
        assert r.status_code == 422

    def test_ids_son_unicos(self, client):
        id1 = create_entry(client, "2026-05-18")["id"]
        id2 = create_entry(client, "2026-05-19")["id"]
        assert id1 != id2

    def test_fecha_duplicada_rechazada(self, client):
        client.post("/journal/", json={"date": "2026-05-19", "content": "Primera"})
        r = client.post("/journal/", json={"date": "2026-05-19", "content": "Duplicada"})
        assert r.status_code in (400, 409, 422, 500)


# ── PUT /journal/{entry_id} ────────────────────────────────────────────────────

class TestUpdateEntry:
    def test_actualizar_contenido(self, client):
        e = create_entry(client)
        r = client.put(f"/journal/{e['id']}", json={"content": "Contenido actualizado"})
        assert r.status_code == 200
        assert r.json()["content"] == "Contenido actualizado"

    def test_actualizar_a_contenido_vacio(self, client):
        e = create_entry(client, content="Texto inicial")
        r = client.put(f"/journal/{e['id']}", json={"content": ""})
        assert r.status_code == 200
        assert r.json()["content"] == ""

    def test_fecha_no_cambia_tras_actualizar(self, client):
        e = create_entry(client)
        updated = client.put(f"/journal/{e['id']}", json={"content": "Nuevo"}).json()
        assert updated["date"] == e["date"]

    def test_id_no_cambia_tras_actualizar(self, client):
        e = create_entry(client)
        updated = client.put(f"/journal/{e['id']}", json={"content": "Nuevo"}).json()
        assert updated["id"] == e["id"]

    def test_actualizar_entrada_inexistente_devuelve_404(self, client):
        r = client.put("/journal/9999", json={"content": "X"})
        assert r.status_code == 404

    def test_schema_de_respuesta(self, client):
        e = create_entry(client)
        data = client.put(f"/journal/{e['id']}", json={"content": "Nuevo"}).json()
        assert set(data.keys()) == {"id", "date", "content"}

    def test_cambios_persisten_en_get(self, client):
        e = create_entry(client)
        client.put(f"/journal/{e['id']}", json={"content": "Persistido"})
        entries = client.get("/journal/").json()
        assert entries[0]["content"] == "Persistido"


# ── DELETE /journal/{entry_id} ─────────────────────────────────────────────────

class TestDeleteEntry:
    def test_borrar_entrada_existente(self, client):
        e = create_entry(client)
        r = client.delete(f"/journal/{e['id']}")
        assert r.status_code == 204

    def test_entrada_ya_no_aparece_tras_borrar(self, client):
        e = create_entry(client)
        client.delete(f"/journal/{e['id']}")
        assert client.get("/journal/").json() == []

    def test_borrar_entrada_inexistente_devuelve_404(self, client):
        r = client.delete("/journal/9999")
        assert r.status_code == 404

    def test_borrar_una_no_afecta_a_otras(self, client):
        e1 = create_entry(client, "2026-05-18")
        e2 = create_entry(client, "2026-05-19")
        client.delete(f"/journal/{e1['id']}")
        entries = client.get("/journal/").json()
        assert len(entries) == 1
        assert entries[0]["id"] == e2["id"]


# ── Escenario completo ─────────────────────────────────────────────────────────

class TestEscenarioCompleto:
    def test_flujo_completo_crud(self, client):
        # Crear
        e = client.post("/journal/", json={"date": "2026-05-19", "content": "Día tranquilo."}).json()
        assert e["content"] == "Día tranquilo."

        # Leer
        entries = client.get("/journal/").json()
        assert len(entries) == 1

        # Editar
        updated = client.put(f"/journal/{e['id']}", json={"content": "Día tranquilo. Añado más."}).json()
        assert updated["content"] == "Día tranquilo. Añado más."

        # Verificar persistencia
        entries = client.get("/journal/").json()
        assert entries[0]["content"] == "Día tranquilo. Añado más."

        # Borrar
        client.delete(f"/journal/{e['id']}")
        assert client.get("/journal/").json() == []

    def test_multiples_entradas_orden_descendente(self, client):
        for i in range(1, 6):
            create_entry(client, f"2026-05-{i:02d}", f"Día {i}")
        dates = [e["date"] for e in client.get("/journal/").json()]
        assert dates == sorted(dates, reverse=True)

    def test_una_entrada_por_dia(self, client):
        client.post("/journal/", json={"date": "2026-05-19", "content": "Primera escritura"})
        r = client.post("/journal/", json={"date": "2026-05-19", "content": "Segunda escritura"})
        assert r.status_code != 201
        assert len(client.get("/journal/").json()) == 1
