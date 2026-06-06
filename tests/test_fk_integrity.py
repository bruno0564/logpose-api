# Pruebas de integridad referencial (FK).
# Verifican dos cosas a la vez:
#   1. Que las FK están activas en el entorno de test (paridad con producción).
#   2. Que crear un hijo apuntando a un padre inexistente devuelve 400, no 500.

class TestForeignKeyViolations:
    def test_routine_exercise_con_routine_inexistente(self, client):
        ex = client.post("/exercises/", json={"name": "Press"}).json()
        res = client.post("/gym/routine-exercises/", json={
            "routine_id": 99999, "exercise_id": ex["id"], "day_of_week": 0, "position": 0,
        })
        assert res.status_code == 400

    def test_set_con_session_inexistente(self, client):
        ex = client.post("/exercises/", json={"name": "Press"}).json()
        res = client.post("/gym/sets/", json={
            "session_id": 99999, "exercise_id": ex["id"],
            "set_number": 1, "weight": 80.0, "reps": 8,
        })
        assert res.status_code == 400

    def test_session_con_routine_inexistente(self, client):
        res = client.post("/gym/sessions/", json={"date": "2026-06-06", "routine_id": 99999})
        assert res.status_code == 400

    def test_habit_con_categoria_inexistente(self, client):
        res = client.post("/habits/", json={"category_id": 99999, "name": "Leer"})
        assert res.status_code == 400

    def test_habit_log_con_habit_inexistente(self, client):
        res = client.post("/habits/logs", json={"habit_id": 99999, "date": "2026-06-06"})
        assert res.status_code == 400

    def test_task_item_con_lista_inexistente(self, client):
        res = client.post("/tasks/items", json={"list_id": 99999, "title": "Comprar"})
        assert res.status_code == 400


class TestCalendarDaysOfWeekValidation:
    def test_days_of_week_invalido_rechazado(self, client):
        res = client.post("/calendar/", json={"title": "Evento", "days_of_week": "lunes"})
        assert res.status_code == 422

    def test_days_of_week_valido_aceptado(self, client):
        res = client.post("/calendar/", json={"title": "Evento", "days_of_week": "0,2,4"})
        assert res.status_code == 201

    def test_days_of_week_none_aceptado(self, client):
        res = client.post("/calendar/", json={"title": "Evento"})
        assert res.status_code == 201
