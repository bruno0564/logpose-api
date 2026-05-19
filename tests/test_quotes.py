# Pruebas de integración — Quotes API
# Nivel: S07 (integración con base de datos)
# Diseño: S04 (particiones equivalentes + valores límite) + S08 (escenario completo)

import pytest

VALID_QUOTE = {"text": "El progreso, no la perfección.", "author": "James Clear"}
VALID_QUOTE_NO_AUTHOR = {"text": "Un día a la vez."}


# ── Helpers ────────────────────────────────────────────────────────────────────

def create_quote(client, text="Frase de prueba", author=None):
    body = {"text": text}
    if author:
        body["author"] = author
    return client.post("/quotes/", json=body).json()


# ── GET /quotes/ ───────────────────────────────────────────────────────────────

class TestListQuotes:
    def test_lista_vacia_devuelve_array_vacio(self, client):
        r = client.get("/quotes/")
        assert r.status_code == 200
        assert r.json() == []

    def test_devuelve_quotes_existentes(self, client):
        create_quote(client, "Frase 1")
        create_quote(client, "Frase 2")
        r = client.get("/quotes/")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_ordenadas_por_id_descendente(self, client):
        create_quote(client, "Primera")
        create_quote(client, "Segunda")
        texts = [q["text"] for q in client.get("/quotes/").json()]
        assert texts == ["Segunda", "Primera"]

    def test_schema_de_quote(self, client):
        create_quote(client, "Frase", "Autor")
        data = client.get("/quotes/").json()[0]
        assert set(data.keys()) == {"id", "text", "author"}
        assert isinstance(data["id"], int)
        assert isinstance(data["text"], str)


# ── POST /quotes/ ──────────────────────────────────────────────────────────────

class TestCreateQuote:
    def test_quote_valida_con_autor(self, client):
        r = client.post("/quotes/", json=VALID_QUOTE)
        assert r.status_code == 201
        data = r.json()
        assert data["text"] == "El progreso, no la perfección."
        assert data["author"] == "James Clear"
        assert "id" in data

    def test_quote_valida_sin_autor(self, client):
        r = client.post("/quotes/", json=VALID_QUOTE_NO_AUTHOR)
        assert r.status_code == 201
        assert r.json()["author"] is None

    def test_schema_completo_de_respuesta(self, client):
        data = client.post("/quotes/", json=VALID_QUOTE).json()
        assert set(data.keys()) == {"id", "text", "author"}
        assert isinstance(data["id"], int)

    def test_text_requerido(self, client):
        r = client.post("/quotes/", json={"author": "Alguien"})
        assert r.status_code == 422

    def test_body_vacio_rechazado(self, client):
        r = client.post("/quotes/", json={})
        assert r.status_code == 422

    def test_texto_vacio_rechazado(self, client):
        r = client.post("/quotes/", json={"text": ""})
        assert r.status_code == 422

    def test_ids_son_unicos(self, client):
        id1 = create_quote(client, "Frase 1")["id"]
        id2 = create_quote(client, "Frase 2")["id"]
        assert id1 != id2

    def test_autor_null_explícito(self, client):
        r = client.post("/quotes/", json={"text": "Sin autor", "author": None})
        assert r.status_code == 201
        assert r.json()["author"] is None

    def test_multiples_quotes_con_mismo_texto(self, client):
        r1 = client.post("/quotes/", json={"text": "Duplicado"})
        r2 = client.post("/quotes/", json={"text": "Duplicado"})
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["id"] != r2.json()["id"]


# ── PUT /quotes/{quote_id} ─────────────────────────────────────────────────────

class TestUpdateQuote:
    def test_actualizar_texto(self, client):
        q = create_quote(client, "Original")
        r = client.put(f"/quotes/{q['id']}", json={"text": "Actualizado"})
        assert r.status_code == 200
        assert r.json()["text"] == "Actualizado"

    def test_actualizar_autor(self, client):
        q = create_quote(client, "Frase", "Autor viejo")
        r = client.put(f"/quotes/{q['id']}", json={"text": "Frase", "author": "Autor nuevo"})
        assert r.status_code == 200
        assert r.json()["author"] == "Autor nuevo"

    def test_actualizar_texto_y_autor_a_la_vez(self, client):
        q = create_quote(client, "Original", "Viejo")
        r = client.put(f"/quotes/{q['id']}", json={"text": "Nuevo texto", "author": "Nuevo autor"})
        data = r.json()
        assert data["text"] == "Nuevo texto"
        assert data["author"] == "Nuevo autor"

    def test_quitar_autor(self, client):
        q = create_quote(client, "Frase", "Autor")
        r = client.put(f"/quotes/{q['id']}", json={"text": "Frase", "author": None})
        assert r.status_code == 200
        assert r.json()["author"] is None

    def test_actualizar_quote_inexistente_devuelve_404(self, client):
        r = client.put("/quotes/9999", json={"text": "X"})
        assert r.status_code == 404

    def test_text_requerido_en_put(self, client):
        q = create_quote(client)
        r = client.put(f"/quotes/{q['id']}", json={"author": "Solo autor"})
        assert r.status_code == 422

    def test_schema_de_respuesta(self, client):
        q = create_quote(client)
        data = client.put(f"/quotes/{q['id']}", json={"text": "T", "author": "A"}).json()
        assert set(data.keys()) == {"id", "text", "author"}

    def test_cambios_persisten_en_get(self, client):
        q = create_quote(client, "Original")
        client.put(f"/quotes/{q['id']}", json={"text": "Cambiado", "author": "Nuevo"})
        quotes = client.get("/quotes/").json()
        assert quotes[0]["text"] == "Cambiado"
        assert quotes[0]["author"] == "Nuevo"

    def test_id_no_cambia_tras_actualizar(self, client):
        q = create_quote(client, "Original")
        updated = client.put(f"/quotes/{q['id']}", json={"text": "Nuevo"}).json()
        assert updated["id"] == q["id"]


# ── DELETE /quotes/{quote_id} ──────────────────────────────────────────────────

class TestDeleteQuote:
    def test_borrar_quote_existente(self, client):
        q = create_quote(client)
        r = client.delete(f"/quotes/{q['id']}")
        assert r.status_code == 204

    def test_quote_ya_no_aparece_tras_borrar(self, client):
        q = create_quote(client)
        client.delete(f"/quotes/{q['id']}")
        assert client.get("/quotes/").json() == []

    def test_borrar_quote_inexistente_devuelve_404(self, client):
        r = client.delete("/quotes/9999")
        assert r.status_code == 404

    def test_borrar_una_quote_no_afecta_a_otras(self, client):
        q1 = create_quote(client, "Frase 1")
        q2 = create_quote(client, "Frase 2")
        client.delete(f"/quotes/{q1['id']}")
        quotes = client.get("/quotes/").json()
        assert len(quotes) == 1
        assert quotes[0]["id"] == q2["id"]


# ── Escenario completo ─────────────────────────────────────────────────────────

class TestEscenarioCompleto:
    def test_flujo_completo_crud(self, client):
        # Crear
        q = client.post("/quotes/", json={"text": "El camino es la meta.", "author": "Confucio"}).json()
        assert q["text"] == "El camino es la meta."

        # Leer
        quotes = client.get("/quotes/").json()
        assert len(quotes) == 1

        # Editar
        updated = client.put(f"/quotes/{q['id']}", json={"text": "El viaje es la recompensa.", "author": "Proverbio chino"}).json()
        assert updated["text"] == "El viaje es la recompensa."

        # Verificar persistencia
        quotes = client.get("/quotes/").json()
        assert quotes[0]["text"] == "El viaje es la recompensa."

        # Borrar
        client.delete(f"/quotes/{q['id']}")
        assert client.get("/quotes/").json() == []

    def test_multiples_quotes_orden_descendente(self, client):
        texts = ["Primera", "Segunda", "Tercera"]
        for t in texts:
            create_quote(client, t)
        returned = [q["text"] for q in client.get("/quotes/").json()]
        assert returned == list(reversed(texts))

    def test_quotes_con_y_sin_autor(self, client):
        create_quote(client, "Sin autor")
        create_quote(client, "Con autor", "Platón")
        quotes = client.get("/quotes/").json()
        autores = {q["text"]: q["author"] for q in quotes}
        assert autores["Sin autor"] is None
        assert autores["Con autor"] == "Platón"
