from app.models import Calculation
from app.calculation_factory import CalculationFactory


def test_create_calculation_record(db_session):
    result = CalculationFactory.create("Add", 3, 4)
    calc = Calculation(a=3, b=4, type="Add", result=result)

    db_session.add(calc)
    db_session.commit()

    saved = db_session.query(Calculation).filter_by(id=calc.id).first()
    assert saved is not None
    assert saved.a == 3
    assert saved.b == 4
    assert saved.result == 7
    assert saved.type == "Add"


def test_divide_record_stores_correct_result(db_session):
    result = CalculationFactory.create("Divide", 10, 2)
    calc = Calculation(a=10, b=2, type="Divide", result=result)

    db_session.add(calc)
    db_session.commit()

    saved = db_session.query(Calculation).filter_by(id=calc.id).first()
    assert saved.result == 5


def test_multiple_calculations_persist_independently(db_session):
    calc1 = Calculation(a=1, b=1, type="Add", result=CalculationFactory.create("Add", 1, 1))
    calc2 = Calculation(a=9, b=3, type="Sub", result=CalculationFactory.create("Sub", 9, 3))

    db_session.add_all([calc1, calc2])
    db_session.commit()

    all_records = db_session.query(Calculation).all()
    assert len(all_records) == 2
def test_add_calculation_via_api(client, auth_headers):
    response = client.post(
        "/calculations/",
        json={"a": 5, "b": 3, "type": "Add"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["result"] == 8
    assert data["type"] == "Add"


def test_read_calculation_by_id(client, auth_headers):
    create_response = client.post(
        "/calculations/",
        json={"a": 10, "b": 4, "type": "Sub"},
        headers=auth_headers,
    )
    calc_id = create_response.json()["id"]

    response = client.get(f"/calculations/{calc_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["result"] == 6


def test_read_nonexistent_calculation_returns_404(client, auth_headers):
    response = client.get("/calculations/999999", headers=auth_headers)
    assert response.status_code == 404


def test_browse_returns_only_current_user_calculations(client, auth_headers):
    client.post("/calculations/", json={"a": 1, "b": 1, "type": "Add"}, headers=auth_headers)
    client.post("/calculations/", json={"a": 2, "b": 2, "type": "Add"}, headers=auth_headers)

    response = client.get("/calculations/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_edit_calculation_updates_result(client, auth_headers):
    create_response = client.post(
        "/calculations/",
        json={"a": 2, "b": 3, "type": "Multiply"},
        headers=auth_headers,
    )
    calc_id = create_response.json()["id"]

    response = client.put(
        f"/calculations/{calc_id}",
        json={"b": 5},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["a"] == 2
    assert data["b"] == 5
    assert data["result"] == 10


def test_edit_calculation_to_divide_by_zero_rejected(client, auth_headers):
    create_response = client.post(
        "/calculations/",
        json={"a": 10, "b": 2, "type": "Divide"},
        headers=auth_headers,
    )
    calc_id = create_response.json()["id"]

    response = client.put(
        f"/calculations/{calc_id}",
        json={"b": 0},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_delete_calculation_removes_record(client, auth_headers):
    create_response = client.post(
        "/calculations/",
        json={"a": 7, "b": 1, "type": "Add"},
        headers=auth_headers,
    )
    calc_id = create_response.json()["id"]

    delete_response = client.delete(f"/calculations/{calc_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/calculations/{calc_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_unauthenticated_request_rejected(client):
    response = client.get("/calculations/")
    assert response.status_code == 401


def test_user_cannot_access_another_users_calculation(client, auth_headers):
    create_response = client.post(
        "/calculations/",
        json={"a": 5, "b": 5, "type": "Add"},
        headers=auth_headers,
    )
    calc_id = create_response.json()["id"]

    other_user_payload = {
        "username": "otheruser",
        "email": "otheruser@example.com",
        "password": "anotherpassword123",
    }
    client.post("/users/register", json=other_user_payload)
    login_response = client.post(
        "/users/login",
        json={
            "username": other_user_payload["username"],
            "password": other_user_payload["password"],
        },
    )
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    response = client.get(f"/calculations/{calc_id}", headers=other_headers)
    assert response.status_code == 404
