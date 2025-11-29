from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Expect some known activities to exist
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "pytest.user@example.com"

    # Ensure the participant is not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        # If already present from previous run, remove first to ensure test determinism
        client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Sign up the user
    signup_resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")

    # Verify the user appears in the participants list
    resp_after = client.get("/activities")
    participants_after = resp_after.json()[activity]["participants"]
    assert email in participants_after

    # Unregister the user
    del_resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert del_resp.status_code == 200
    assert "Unregistered" in del_resp.json().get("message", "")

    # Verify removal
    resp_final = client.get("/activities")
    participants_final = resp_final.json()[activity]["participants"]
    assert email not in participants_final
