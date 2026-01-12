"""Tests for the FastAPI activities application."""

import pytest


class TestGetActivities:
    """Test the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that all activities are returned."""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        assert "Basketball Team" in activities
        assert "Soccer Club" in activities
        assert "Chess Club" in activities
        assert len(activities) == 9

    def test_get_activities_includes_participant_count(self, client, reset_activities):
        """Test that activities include participant information."""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=new@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up new@mergington.edu" in data["message"]

    def test_signup_persists_participant(self, client, reset_activities):
        """Test that participant is persisted after signup."""
        client.post(
            "/activities/Basketball%20Team/signup?email=new@mergington.edu"
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert "new@mergington.edu" in activities["Basketball Team"]["participants"]

    def test_signup_for_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test signup for nonexistent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_duplicate_signup_returns_400(self, client, reset_activities):
        """Test that duplicate signup returns 400 error."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_increments_participant_count(self, client, reset_activities):
        """Test that signup increments participant count."""
        response_before = client.get("/activities")
        basketball_before = response_before.json()["Basketball Team"]
        count_before = len(basketball_before["participants"])
        
        client.post(
            "/activities/Basketball%20Team/signup?email=new@mergington.edu"
        )
        
        response_after = client.get("/activities")
        basketball_after = response_after.json()["Basketball Team"]
        count_after = len(basketball_after["participants"])
        
        assert count_after == count_before + 1


class TestRemoveParticipant:
    """Test the DELETE /activities/{activity_name}/delete endpoint."""

    def test_remove_participant_success(self, client, reset_activities):
        """Test successful removal of a participant."""
        response = client.delete(
            "/activities/Chess%20Club/delete?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Removed michael@mergington.edu" in data["message"]

    def test_remove_participant_persists(self, client, reset_activities):
        """Test that participant removal is persisted."""
        client.delete(
            "/activities/Chess%20Club/delete?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_remove_nonexistent_participant_returns_400(self, client, reset_activities):
        """Test removing non-existent participant returns 400."""
        response = client.delete(
            "/activities/Chess%20Club/delete?email=nonexistent@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "Participant not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test removing from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent%20Club/delete?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_decrements_participant_count(self, client, reset_activities):
        """Test that removal decrements participant count."""
        response_before = client.get("/activities")
        chess_before = response_before.json()["Chess Club"]
        count_before = len(chess_before["participants"])
        
        client.delete(
            "/activities/Chess%20Club/delete?email=michael@mergington.edu"
        )
        
        response_after = client.get("/activities")
        chess_after = response_after.json()["Chess Club"]
        count_after = len(chess_after["participants"])
        
        assert count_after == count_before - 1


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root_redirects_to_static(self, client, reset_activities):
        """Test that root endpoint redirects to static index."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
