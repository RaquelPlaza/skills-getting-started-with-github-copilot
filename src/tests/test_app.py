import pytest
from fastapi.testclient import TestClient
from src.app import app, activities, initial_activities
import copy

@pytest.fixture
def client():
    return TestClient(app, follow_redirects=False)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    global activities
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))

def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]

def test_signup_success(client):
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    # Verify added
    activities_response = client.get("/activities")
    assert "newstudent@mergington.edu" in activities_response.json()["Chess Club"]["participants"]

def test_signup_activity_not_found(client):
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_signup_already_signed_up(client):
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

def test_unregister_success(client):
    response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
    # Verify removed
    activities_response = client.get("/activities")
    assert "michael@mergington.edu" not in activities_response.json()["Chess Club"]["participants"]

def test_unregister_activity_not_found(client):
    response = client.delete("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_not_signed_up(client):
    response = client.delete("/activities/Chess Club/signup?email=notsigned@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"