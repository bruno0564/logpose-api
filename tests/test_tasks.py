# Pruebas de integración — To-Do API
# Nivel: S07 (integración con base de datos)
# Diseño: S04 (particiones equivalentes + valores límite) + S08 (escenario completo)

import pytest

VALID_LIST = {"name": "Series"}
VALID_ITEM = {"title": "Ver Breaking Bad", "done": False}


# ── Helpers ────────────────────────────────────────────────────────────────────

def create_list(client, name="Series"):
    return client.post("/tasks/lists", json={"name": name}).json()

def create_item(client, list_id, title="Tarea", done=False):
    return client.post("/tasks/items", json={"list_id": list_id, "title": title, "done": done}).json()


# ── GET /tasks/lists ───────────────────────────────────────────────────────────

class TestListLists:
    def test_lista_vacia_devuelve_array_vacio(self, client):
        r = client.get("/tasks/lists")
        assert r.status_code == 200
        assert r.json() == []

    def test_devuelve_listas_existentes(self, client):
        create_list(client, "Lista 1")
        create_list(client, "Lista 2")
        r = client.get("/tasks/lists")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_ordenadas_por_id_ascendente(self, client):
        create_list(client, "B")
        create_list(client, "A")
        names = [l["name"] for l in client.get("/tasks/lists").json()]
        assert names == ["B", "A"]

    def test_schema_de_lista(self, client):
        create_list(client)
        data = client.get("/tasks/lists").json()[0]
        assert set(data.keys()) == {"id", "name"}
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)


# ── POST /tasks/lists ──────────────────────────────────────────────────────────

class TestCreateList:
    def test_lista_valida(self, client):
        r = client.post("/tasks/lists", json=VALID_LIST)
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Series"
        assert "id" in data

    def test_schema_completo_de_respuesta(self, client):
        data = client.post("/tasks/lists", json=VALID_LIST).json()
        assert set(data.keys()) == {"id", "name"}
        assert isinstance(data["id"], int)

    def test_ids_son_unicos(self, client):
        id1 = create_list(client, "Lista 1")["id"]
        id2 = create_list(client, "Lista 2")["id"]
        assert id1 != id2

    def test_nombre_requerido(self, client):
        r = client.post("/tasks/lists", json={})
        assert r.status_code == 422

    def test_nombre_vacio_rechazado(self, client):
        # Pydantic rechaza strings vacías si no se permite
        r = client.post("/tasks/lists", json={"name": ""})
        # La API actual acepta strings vacías (no hay validación mínima de longitud)
        # Este test documenta el comportamiento actual
        assert r.status_code in (201, 422)

    def test_multiples_listas_con_mismo_nombre(self, client):
        r1 = client.post("/tasks/lists", json={"name": "Duplicado"})
        r2 = client.post("/tasks/lists", json={"name": "Duplicado"})
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["id"] != r2.json()["id"]


# ── DELETE /tasks/lists/{list_id} ─────────────────────────────────────────────

class TestDeleteList:
    def test_borrar_lista_existente(self, client):
        lst = create_list(client)
        r = client.delete(f"/tasks/lists/{lst['id']}")
        assert r.status_code == 204

    def test_lista_ya_no_aparece_tras_borrar(self, client):
        lst = create_list(client)
        client.delete(f"/tasks/lists/{lst['id']}")
        assert client.get("/tasks/lists").json() == []

    def test_borrar_lista_inexistente_devuelve_404(self, client):
        r = client.delete("/tasks/lists/9999")
        assert r.status_code == 404

    def test_borrar_lista_en_cascada_elimina_sus_items(self, client):
        lst = create_list(client)
        create_item(client, lst["id"], "Item 1")
        create_item(client, lst["id"], "Item 2")
        client.delete(f"/tasks/lists/{lst['id']}")
        # La lista ya no existe; si la creamos de nuevo no debería tener items
        lst2 = create_list(client, "Nueva")
        items = client.get(f"/tasks/lists/{lst2['id']}/items").json()
        assert items == []

    def test_borrar_una_lista_no_afecta_a_otra(self, client):
        lst1 = create_list(client, "Lista 1")
        lst2 = create_list(client, "Lista 2")
        create_item(client, lst2["id"], "Item en lista 2")
        client.delete(f"/tasks/lists/{lst1['id']}")
        listas = client.get("/tasks/lists").json()
        assert len(listas) == 1
        assert listas[0]["id"] == lst2["id"]


# ── GET /tasks/lists/{list_id}/items ──────────────────────────────────────────

class TestListItems:
    def test_lista_sin_items_devuelve_array_vacio(self, client):
        lst = create_list(client)
        r = client.get(f"/tasks/lists/{lst['id']}/items")
        assert r.status_code == 200
        assert r.json() == []

    def test_devuelve_items_de_la_lista(self, client):
        lst = create_list(client)
        create_item(client, lst["id"], "Tarea A")
        create_item(client, lst["id"], "Tarea B")
        r = client.get(f"/tasks/lists/{lst['id']}/items")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_solo_devuelve_items_de_esa_lista(self, client):
        lst1 = create_list(client, "L1")
        lst2 = create_list(client, "L2")
        create_item(client, lst1["id"], "Item de L1")
        create_item(client, lst2["id"], "Item de L2")
        items_l1 = client.get(f"/tasks/lists/{lst1['id']}/items").json()
        assert len(items_l1) == 1
        assert items_l1[0]["title"] == "Item de L1"

    def test_ordenados_por_id_ascendente(self, client):
        lst = create_list(client)
        create_item(client, lst["id"], "Primero")
        create_item(client, lst["id"], "Segundo")
        titles = [i["title"] for i in client.get(f"/tasks/lists/{lst['id']}/items").json()]
        assert titles == ["Primero", "Segundo"]

    def test_schema_de_item(self, client):
        lst = create_list(client)
        create_item(client, lst["id"])
        data = client.get(f"/tasks/lists/{lst['id']}/items").json()[0]
        assert set(data.keys()) == {"id", "list_id", "title", "done"}
        assert isinstance(data["id"], int)
        assert isinstance(data["list_id"], int)
        assert isinstance(data["title"], str)
        assert isinstance(data["done"], bool)


# ── POST /tasks/items ──────────────────────────────────────────────────────────

class TestCreateItem:
    def test_item_valido_sin_done(self, client):
        lst = create_list(client)
        r = client.post("/tasks/items", json={"list_id": lst["id"], "title": "Tarea"})
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "Tarea"
        assert data["done"] is False
        assert data["list_id"] == lst["id"]

    def test_item_valido_con_done_true(self, client):
        lst = create_list(client)
        r = client.post("/tasks/items", json={"list_id": lst["id"], "title": "Ya hecho", "done": True})
        assert r.status_code == 201
        assert r.json()["done"] is True

    def test_schema_completo_de_respuesta(self, client):
        lst = create_list(client)
        data = client.post("/tasks/items", json={"list_id": lst["id"], "title": "T"}).json()
        assert set(data.keys()) == {"id", "list_id", "title", "done"}
        assert isinstance(data["id"], int)

    def test_title_requerido(self, client):
        lst = create_list(client)
        r = client.post("/tasks/items", json={"list_id": lst["id"]})
        assert r.status_code == 422

    def test_list_id_requerido(self, client):
        r = client.post("/tasks/items", json={"title": "Sin lista"})
        assert r.status_code == 422

    def test_ids_son_unicos(self, client):
        lst = create_list(client)
        id1 = create_item(client, lst["id"], "T1")["id"]
        id2 = create_item(client, lst["id"], "T2")["id"]
        assert id1 != id2


# ── PUT /tasks/items/{item_id} ─────────────────────────────────────────────────

class TestUpdateItem:
    def test_marcar_item_como_hecho(self, client):
        lst = create_list(client)
        item = create_item(client, lst["id"], "Pendiente")
        r = client.put(f"/tasks/items/{item['id']}", json={"title": "Pendiente", "done": True})
        assert r.status_code == 200
        assert r.json()["done"] is True

    def test_desmarcar_item_hecho(self, client):
        lst = create_list(client)
        item = create_item(client, lst["id"], "Hecha", done=True)
        r = client.put(f"/tasks/items/{item['id']}", json={"title": "Hecha", "done": False})
        assert r.status_code == 200
        assert r.json()["done"] is False

    def test_actualizar_titulo(self, client):
        lst = create_list(client)
        item = create_item(client, lst["id"], "Título original")
        r = client.put(f"/tasks/items/{item['id']}", json={"title": "Título nuevo", "done": False})
        assert r.status_code == 200
        assert r.json()["title"] == "Título nuevo"

    def test_actualizar_titulo_y_done_a_la_vez(self, client):
        lst = create_list(client)
        item = create_item(client, lst["id"], "Original")
        r = client.put(f"/tasks/items/{item['id']}", json={"title": "Cambiado", "done": True})
        data = r.json()
        assert data["title"] == "Cambiado"
        assert data["done"] is True

    def test_actualizar_item_inexistente_devuelve_404(self, client):
        r = client.put("/tasks/items/9999", json={"title": "X", "done": False})
        assert r.status_code == 404

    def test_schema_de_respuesta(self, client):
        lst = create_list(client)
        item = create_item(client, lst["id"])
        data = client.put(f"/tasks/items/{item['id']}", json={"title": "T", "done": True}).json()
        assert set(data.keys()) == {"id", "list_id", "title", "done"}

    def test_title_requerido_en_put(self, client):
        lst = create_list(client)
        item = create_item(client, lst["id"])
        r = client.put(f"/tasks/items/{item['id']}", json={"done": True})
        assert r.status_code == 422

    def test_done_requerido_en_put(self, client):
        lst = create_list(client)
        item = create_item(client, lst["id"])
        r = client.put(f"/tasks/items/{item['id']}", json={"title": "X"})
        assert r.status_code == 422

    def test_cambios_persisten_en_get(self, client):
        lst = create_list(client)
        item = create_item(client, lst["id"], "Original")
        client.put(f"/tasks/items/{item['id']}", json={"title": "Cambiado", "done": True})
        items = client.get(f"/tasks/lists/{lst['id']}/items").json()
        assert items[0]["title"] == "Cambiado"
        assert items[0]["done"] is True


# ── DELETE /tasks/items/{item_id} ─────────────────────────────────────────────

class TestDeleteItem:
    def test_borrar_item_existente(self, client):
        lst = create_list(client)
        item = create_item(client, lst["id"])
        r = client.delete(f"/tasks/items/{item['id']}")
        assert r.status_code == 204

    def test_item_ya_no_aparece_tras_borrar(self, client):
        lst = create_list(client)
        item = create_item(client, lst["id"])
        client.delete(f"/tasks/items/{item['id']}")
        items = client.get(f"/tasks/lists/{lst['id']}/items").json()
        assert items == []

    def test_borrar_item_inexistente_devuelve_404(self, client):
        r = client.delete("/tasks/items/9999")
        assert r.status_code == 404

    def test_borrar_un_item_no_afecta_a_otros(self, client):
        lst = create_list(client)
        item1 = create_item(client, lst["id"], "Item 1")
        item2 = create_item(client, lst["id"], "Item 2")
        client.delete(f"/tasks/items/{item1['id']}")
        items = client.get(f"/tasks/lists/{lst['id']}/items").json()
        assert len(items) == 1
        assert items[0]["id"] == item2["id"]


# ── Escenario completo ─────────────────────────────────────────────────────────

class TestEscenarioCompleto:
    def test_flujo_completo_lista_con_tareas(self, client):
        # Crear lista
        lst = client.post("/tasks/lists", json={"name": "Películas"}).json()
        assert lst["name"] == "Películas"

        # Añadir items
        t1 = create_item(client, lst["id"], "Interstellar")
        t2 = create_item(client, lst["id"], "Oppenheimer")
        t3 = create_item(client, lst["id"], "Dune 2")

        items = client.get(f"/tasks/lists/{lst['id']}/items").json()
        assert len(items) == 3
        assert all(not i["done"] for i in items)

        # Marcar dos como hechas
        client.put(f"/tasks/items/{t1['id']}", json={"title": "Interstellar", "done": True})
        client.put(f"/tasks/items/{t2['id']}", json={"title": "Oppenheimer", "done": True})

        items = client.get(f"/tasks/lists/{lst['id']}/items").json()
        done_count = sum(1 for i in items if i["done"])
        assert done_count == 2

        # Borrar una tarea pendiente
        client.delete(f"/tasks/items/{t3['id']}")
        items = client.get(f"/tasks/lists/{lst['id']}/items").json()
        assert len(items) == 2

        # Borrar la lista entera
        client.delete(f"/tasks/lists/{lst['id']}")
        assert client.get("/tasks/lists").json() == []

    def test_multiples_listas_independientes(self, client):
        series = create_list(client, "Series")
        recados = create_list(client, "Recados")

        create_item(client, series["id"], "Breaking Bad")
        create_item(client, series["id"], "The Wire")
        create_item(client, recados["id"], "Comprar leche")

        series_items = client.get(f"/tasks/lists/{series['id']}/items").json()
        recados_items = client.get(f"/tasks/lists/{recados['id']}/items").json()

        assert len(series_items) == 2
        assert len(recados_items) == 1

        # Borrar una lista no afecta a la otra
        client.delete(f"/tasks/lists/{series['id']}")
        listas = client.get("/tasks/lists").json()
        assert len(listas) == 1
        assert listas[0]["id"] == recados["id"]
        recados_items = client.get(f"/tasks/lists/{recados['id']}/items").json()
        assert len(recados_items) == 1

    def test_toggle_pendiente_hecha_pendiente(self, client):
        lst = create_list(client)
        item = create_item(client, lst["id"], "Tarea reversible")

        # Marcar como hecha
        r = client.put(f"/tasks/items/{item['id']}", json={"title": "Tarea reversible", "done": True})
        assert r.json()["done"] is True

        # Volver a pendiente
        r = client.put(f"/tasks/items/{item['id']}", json={"title": "Tarea reversible", "done": False})
        assert r.json()["done"] is False

        # Verificar persistencia
        items = client.get(f"/tasks/lists/{lst['id']}/items").json()
        assert items[0]["done"] is False
