"""
Test suite for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Test cases for GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status code 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Drama Club",
            "Debate Team",
            "Math Club",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_valid_activity_and_email(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball Team/signup?email=student@example.com"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_nonexistent_activity_returns_404(self):
        """Test signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@example.com"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_returns_400(self):
        """Test that duplicate signups return 400 error"""
        email = "duplicate@example.com"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Soccer Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Duplicate signup should fail
        response2 = client.post(
            f"/activities/Soccer Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_adds_participant_to_activity(self):
        """Test that signup adds participant to activity's participant list"""
        email = "newstudent@example.com"
        activity_name = "Art Club"
        
        # Get initial participant count
        response_before = client.get("/activities")
        participants_before = response_before.json()[activity_name]["participants"]
        count_before = len(participants_before)
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Check updated participant count
        response_after = client.get("/activities")
        participants_after = response_after.json()[activity_name]["participants"]
        count_after = len(participants_after)
        
        assert count_after == count_before + 1
        assert email in participants_after


class TestUnregisterFromActivity:
    """Test cases for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        email = "delete_test@example.com"
        activity_name = "Drama Club"
        
        # Sign up first
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_nonexistent_participant_returns_400(self):
        """Test unregistering a participant not signed up returns 400"""
        response = client.delete(
            "/activities/Debate Team/signup?email=notregistered@example.com"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_removes_participant_from_activity(self):
        """Test that unregister removes participant from activity"""
        email = "remove_test@example.com"
        activity_name = "Math Club"
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify they're registered
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
        
        # Unregister
        client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify they're removed
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test unregister for nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Fake Club/signup?email=student@example.com"
        )
        assert response.status_code == 404


class TestRoot:
    """Test cases for root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
