"""
Pytest configuration - automatically mocks external services for unit tests
"""
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_ml_services():
    """
    Auto-mock ML services for all tests
    This prevents real API calls during unit testing
    """
    with patch('ml_client.get_movie_recommendations') as mock_rec:
        
        # Mock recommendation response (matches your expected format)
        mock_rec.return_value = (
            "Movie Name: Inception\n"
            "Runtime: 148 minutes\n"
            "Description: A thief who steals corporate secrets through dream-sharing technology."
        )
        
        yield {'recommendations': mock_rec}


@pytest.fixture
def sample_chat_message():
    """Sample chat message for testing"""
    return {
        'user_email': 'test@example.com',
        'message': 'Recommend a sci-fi movie',
        'convo_id': None
    }


@pytest.fixture
def sample_movie_data():
    """Sample movie data for testing"""
    return {
        "movie_name": "Inception",
        "movie_description": "A thief who steals corporate secrets.",
        "runtime": 148,
        "user_email": "test@example.com"
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "fname": "Test",
        "lname": "User",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }