"""
Tests for the Mergington High School Activities API.
Each test uses the AAA (Arrange-Act-Assert) pattern for clarity.
"""


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_redirects_to_index(self, client):
        # Arrange
        expected_redirect_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert expected_redirect_url in response.headers["location"]


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities(self, client):
        # Arrange
        # No special setup needed - activities are populated by fixture

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_activity_has_required_fields(self, client):
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"

    def test_participants_is_list(self, client):
        # Arrange
        # No special setup needed

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_adds_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_email_fails(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_multiple_students(self, client):
        # Arrange
        activity_name = "Basketball Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]

        # Act
        for email in emails:
            client.post(f"/activities/{activity_name}/signup?email={email}")
        
        response = client.get("/activities")

        # Assert
        activities = response.json()
        for email in emails:
            assert email in activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"

    def test_unregister_removes_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_registered_fails(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"  # Not registered

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_nonexistent_activity_fails(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_then_signup_again(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email in activities[activity_name]["participants"]
