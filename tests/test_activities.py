from pathlib import Path
import sys

import pytest

# Allow running this file directly (python tests/test_activities.py) as well as via pytest.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import app as app_module


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == expected_location


def test_get_activities_returns_seed_data(client):
    # Arrange
    expected_count = len(app_module.activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == expected_count
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_get_activities_items_have_expected_schema(client):
    # Arrange
    expected_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    for activity in data.values():
        assert set(activity.keys()) == expected_keys
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    before_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]
    after_count = len(app_module.activities[activity_name]["participants"])
    assert after_count == before_count + 1


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    before_participants = list(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert app_module.activities[activity_name]["participants"] == before_participants


def test_unregister_removes_existing_participant(client):
    # Arrange
    activity_name = "Art Studio"
    email = "maya@mergington.edu"
    before_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]
    after_count = len(app_module.activities[activity_name]["participants"])
    assert after_count == before_count - 1


def test_unregister_rejects_student_not_signed_up(client):
    # Arrange
    activity_name = "Art Studio"
    email = "not.signed.up@mergington.edu"
    before_participants = list(app_module.activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is not signed up for this activity"}
    assert app_module.activities[activity_name]["participants"] == before_participants


@pytest.mark.parametrize("method", ["post", "delete"])
def test_unknown_activity_requests_return_404_and_do_not_mutate_state(client, method):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    baseline_state = {
        name: list(details["participants"])
        for name, details in app_module.activities.items()
    }

    # Act
    endpoint = f"/activities/{activity_name}/signup"
    if method == "post":
        response = client.post(endpoint, params={"email": email})
    else:
        response = client.delete(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    for name, participants in baseline_state.items():
        assert app_module.activities[name]["participants"] == participants
