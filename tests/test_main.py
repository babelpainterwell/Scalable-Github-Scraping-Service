from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

fake_db = {

}

def test_get_user_projects():
    response = client.get("/users/username/projects")
    assert response.status_code == 200
    assert response.json() == []

def test_get_most_recent_users():
    response = client.get("/users/recent/5")
    assert response.status_code == 200
    assert response.json() == []

def test_get_most_starred_projects():
    response = client.get("/projects/most-starred/5")
    assert response.status_code == 200
    assert response.json() == []

def test_get_user_projects_not_found():
    response = client.get("/users/username/projects")
    assert response.status_code == 404
    assert response.json() == {"detail": "Resource not found."}

def test_get_most_recent_users_not_found():
    response = client.get("/users/recent/5")
    assert response.status_code == 404
    assert response.json() == {"detail": "Resource not found."}

def test_get_most_starred_projects_not_found():
    response = client.get("/projects/most-starred/5")
    assert response.status_code == 404
    assert response.json() == {"detail": "Resource not found."}

def test_get_user_projects_internal_server_error():
    response = client.get("/users/username/projects")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}

def test_get_most_recent_users_internal_server_error():
    response = client.get("/users/recent/5")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}

def test_get_most_starred_projects_internal_server_error():
    response = client.get("/projects/most-starred/5")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}

def test_get_user_projects_external_api_error():
    response = client.get("/users/username/projects")
    assert response.status_code == 503
    assert response.json() == {"detail": "External API error."}

def test_get_most_recent_users_external_api_error():
    response = client.get("/users/recent/5")
    assert response.status_code == 503
    assert response.json() == {"detail": "External API error."}

def test_get_most_starred_projects_external_api_error():
    response = client.get("/projects/most-starred/5")
    assert response.status_code == 503
    assert response.json() == {"detail": "External API error."}

