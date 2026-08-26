from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_list_meetings_endpoint():
    response = client.get("/meetings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_ask_endpoint():
    payload = {
        "question": "Why did we choose PostgreSQL instead of MongoDB three months ago?"
    }
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "reasons" in data
    assert "sources" in data
