import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    # Save the initial state
    initial_state = copy.deepcopy(activities)
    
    yield
    
    # Restore the initial state after the test
    activities.clear()
    activities.update(initial_state)
