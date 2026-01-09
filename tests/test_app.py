"""Tests for FastAPI activities endpoints."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that get_activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Basketball" in data
        assert "Soccer" in data

    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)

    def test_get_activities_returns_participants(self, client):
        """Test that activities include initial participants."""
        response = client.get("/activities")
        data = response.json()
        
        assert "james@mergington.edu" in data["Basketball"]["participants"]
        assert "lucas@mergington.edu" in data["Soccer"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup adds participant to the activity."""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Basketball/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball"]["participants"]

    def test_signup_to_nonexistent_activity(self, client):
        """Test signup to a non-existent activity returns 404."""
        response = client.post(
            "/activities/NonExistent/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_already_registered_student(self, client):
        """Test that already registered students get 400 error."""
        response = client.post(
            "/activities/Basketball/signup?email=james@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_multiple_students(self, client):
        """Test that multiple students can sign up for the same activity."""
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        
        for email in emails:
            response = client.post(f"/activities/Soccer/signup?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        
        for email in emails:
            assert email in data["Soccer"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client):
        """Test successful unregister from an activity."""
        email = "james@mergington.edu"
        response = client.delete(
            f"/activities/Basketball/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from the activity."""
        email = "james@mergington.edu"
        client.delete(f"/activities/Basketball/unregister?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Basketball"]["participants"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from a non-existent activity returns 404."""
        response = client.delete(
            "/activities/NonExistent/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_student_not_registered(self, client):
        """Test that unregistering a non-registered student returns 400."""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_then_signup_again(self, client):
        """Test that a student can sign up again after unregistering."""
        email = "james@mergington.edu"
        
        # Unregister
        client.delete(f"/activities/Basketball/unregister?email={email}")
        
        # Sign up again
        response = client.post(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 200
        
        # Verify participant is registered again
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
