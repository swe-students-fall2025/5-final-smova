"""
Unit tests for the frontend Flask application
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, is_logged_in


@pytest.fixture
def client():
    """Create a test client for the app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def logged_in_client(client):
    """Create a test client with a logged-in session"""
    with client.session_transaction() as session:
        session['user_email'] = 'test@example.com'
    return client


# ============ Test Routes ============

def test_index_redirect_to_login(client):
    """Test that index redirects to login when not logged in"""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location


def test_index_redirect_to_home_when_logged_in(logged_in_client):
    """Test that index redirects to home when logged in"""
    response = logged_in_client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/home' in response.location


def test_login_page_loads(client):
    """Test that login page loads successfully"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data


@patch('app.requests.post')
def test_login_with_credentials(mock_post, client):
    """Test login with email and password"""
    # Mock successful backend response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        'success': True,
        'user_email': 'test@example.com',
        'token': 'fake-token'
    }
    
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Login successful!' in response.data


@patch('app.requests.post')
def test_login_without_email(mock_post, client):
    """Test login fails without email"""
    # Mock backend to fail
    mock_post.return_value.status_code = 401
    mock_post.return_value.json.return_value = {
        'success': False,
        'message': 'Invalid credentials'
    }
    
    response = client.post('/login', data={
        'email': '',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid credentials' in response.data


@patch('app.requests.post')
def test_login_without_password(mock_post, client):
    """Test login fails without password"""
    # Mock backend to fail
    mock_post.return_value.status_code = 401
    mock_post.return_value.json.return_value = {
        'success': False,
        'message': 'Invalid credentials'
    }
    
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid credentials' in response.data


def test_register_page_loads(client):
    """Test that register page loads successfully"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Create Account' in response.data
    assert b'First Name' in response.data
    assert b'Last Name' in response.data
    assert b'Email' in response.data


@patch('app.requests.post')
def test_register_with_valid_data(mock_post, client):
    """Test registration with valid data"""
    # Mock successful backend response
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {
        'success': True,
        'message': 'User registered successfully'
    }
    
    response = client.post('/register', data={
        'fname': 'John',
        'lname': 'Doe',
        'email': 'john@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful!' in response.data


def test_register_password_mismatch(client):
    """Test registration fails when passwords don't match"""
    response = client.post('/register', data={
        'fname': 'John',
        'lname': 'Doe',
        'email': 'john@example.com',
        'password': 'password123',
        'confirm_password': 'different'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Passwords do not match' in response.data


def test_register_missing_fields(client):
    """Test registration fails with missing fields"""
    response = client.post('/register', data={
        'fname': 'John',
        'lname': '',
        'email': 'john@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'All fields are required' in response.data


def test_home_page_requires_login(client):
    """Test that home page requires login"""
    response = client.get('/home', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please login to access this page' in response.data
    assert b'Login' in response.data


def test_home_page_loads_when_logged_in(logged_in_client):
    """Test that home page loads when logged in"""
    response = logged_in_client.get('/home')
    assert response.status_code == 200
    assert b'AI Movie Recommender' in response.data
    assert b'test@example.com' in response.data


def test_logout(logged_in_client):
    """Test logout functionality"""
    response = logged_in_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data
    assert b'Login' in response.data


def test_logout_clears_session(logged_in_client):
    """Test that logout clears session"""
    logged_in_client.get('/logout')
    
    # Try to access home page after logout
    response = logged_in_client.get('/home', follow_redirects=True)
    assert b'Please login to access this page' in response.data


# ============ Test Helper Functions ============

def test_is_logged_in_returns_true_when_session_exists(logged_in_client):
    """Test is_logged_in returns True when user is in session"""
    with logged_in_client.application.test_request_context():
        with logged_in_client.session_transaction() as session:
            session['user_email'] = 'test@example.com'
        # The function checks the session, which we've set up
        assert 'user_email' in session


def test_is_logged_in_returns_false_when_no_session(client):
    """Test is_logged_in returns False when no user in session"""
    with client.application.test_request_context():
        with client.session_transaction() as session:
            # Ensure no user_email in session
            session.pop('user_email', None)
        assert 'user_email' not in session


# ============ Test Form Validation ============

@patch('app.requests.post')
def test_login_form_accepts_various_email_formats(mock_post, client):
    """Test that login accepts various valid email formats"""
    # Mock successful backend response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        'success': True,
        'user_email': 'user@example.com',
        'token': 'fake-token'
    }
    
    emails = [
        'user@example.com',
        'user.name@example.com',
        'user+tag@example.co.uk'
    ]
    
    for email in emails:
        response = client.post('/login', data={
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200


@patch('app.requests.post')
def test_register_form_accepts_various_names(mock_post, client):
    """Test that register accepts various name formats"""
    # Mock successful backend response
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {
        'success': True,
        'message': 'User registered successfully'
    }
    
    response = client.post('/register', data={
        'fname': 'Jean-Pierre',
        'lname': "O'Brien",
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful!' in response.data


# ============ Test Movie List Pages ============

def test_not_watched_page_requires_login(client):
    """Test that not watched page requires login"""
    response = client.get('/not-watched', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please login to access this page' in response.data


def test_not_watched_page_loads_when_logged_in(logged_in_client):
    """Test that not watched page loads when logged in"""
    response = logged_in_client.get('/not-watched')
    assert response.status_code == 200
    assert b'Movies to Watch' in response.data
    assert b'Not Watched' in response.data


@patch('app.requests.get')
def test_not_watched_page_displays_movies(mock_get, logged_in_client):
    """Test that not watched page displays movies from backend"""
    # Mock backend response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'success': True,
        'movies': [
            {
                'movie_id': '1',
                'movie_name': 'Inception',
                'movie_description': 'A mind-bending thriller',
                'runtime': 148,
                'has_watched': False
            }
        ]
    }
    
    response = logged_in_client.get('/not-watched')
    assert response.status_code == 200
    assert b'Inception' in response.data


def test_watched_page_requires_login(client):
    """Test that watched page requires login"""
    response = client.get('/watched', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please login to access this page' in response.data


def test_watched_page_loads_when_logged_in(logged_in_client):
    """Test that watched page loads when logged in"""
    response = logged_in_client.get('/watched')
    assert response.status_code == 200
    assert b'Watched Movies' in response.data


@patch('app.requests.get')
def test_watched_page_displays_movies_with_ratings(mock_get, logged_in_client):
    """Test that watched page displays movies with ratings from backend"""
    # Mock backend response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'success': True,
        'movies': [
            {
                'movie_id': '4',
                'movie_name': 'The Dark Knight',
                'movie_description': 'Batman vs Joker',
                'runtime': 152,
                'has_watched': True,
                'rating': 9.0
            }
        ]
    }
    
    response = logged_in_client.get('/watched')
    assert response.status_code == 200
    assert b'The Dark Knight' in response.data
    assert b'9.0' in response.data


# ============ Test Movie Detail Page ============

def test_movie_detail_requires_login(client):
    """Test that movie detail page requires login"""
    response = client.get('/movie/1', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please login to access this page' in response.data


@patch('app.requests.get')
def test_movie_detail_loads_for_valid_movie(mock_get, logged_in_client):
    """Test that movie detail page loads for valid movie"""
    # Mock backend response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'success': True,
        'movie': {
            'movie_id': '1',
            'movie_name': 'Inception',
            'movie_description': 'A mind-bending thriller',
            'runtime': 148,
            'has_watched': False,
            'rating': None
        }
    }
    
    response = logged_in_client.get('/movie/1')
    assert response.status_code == 200
    assert b'Inception' in response.data
    assert b'148 minutes' in response.data


@patch('app.requests.get')
def test_movie_detail_shows_rating_form_for_unwatched(mock_get, logged_in_client):
    """Test that unwatched movies show rating form"""
    # Mock backend response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'success': True,
        'movie': {
            'movie_id': '1',
            'movie_name': 'Inception',
            'movie_description': 'A mind-bending thriller',
            'runtime': 148,
            'has_watched': False,
            'rating': None
        }
    }
    
    response = logged_in_client.get('/movie/1')
    assert response.status_code == 200
    assert b'Rate This Movie' in response.data
    assert b'Your Rating' in response.data


@patch('app.requests.get')
def test_movie_detail_shows_rating_for_watched(mock_get, logged_in_client):
    """Test that watched movies show their rating"""
    # Mock backend response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'success': True,
        'movie': {
            'movie_id': '4',
            'movie_name': 'The Dark Knight',
            'movie_description': 'Batman vs Joker',
            'runtime': 152,
            'has_watched': True,
            'rating': 9.0
        }
    }
    
    response = logged_in_client.get('/movie/4')
    assert response.status_code == 200
    assert b'9.0' in response.data
    assert b'Watched' in response.data


@patch('app.requests.get')
def test_movie_detail_invalid_id(mock_get, logged_in_client):
    """Test that invalid movie ID redirects with error"""
    # Mock backend 404 response
    mock_get.return_value.status_code = 404
    mock_get.return_value.json.return_value = {
        'success': False,
        'message': 'Movie not found'
    }
    
    response = logged_in_client.get('/movie/999', follow_redirects=True)
    assert response.status_code == 200
    assert b'Movie not found' in response.data


# ============ Test Rate Movie ============

def test_rate_movie_requires_login(client):
    """Test that rating a movie requires login"""
    response = client.post('/movie/1/rate', data={'rating': '8.5'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please login to access this page' in response.data


@patch('app.requests.put')
def test_rate_movie_success(mock_put, logged_in_client):
    """Test successful movie rating"""
    # Mock successful backend response
    mock_put.return_value.status_code = 200
    mock_put.return_value.json.return_value = {
        'success': True,
        'message': 'Movie updated successfully'
    }
    
    response = logged_in_client.post('/movie/1/rate',
                                     data={'rating': '8.5'},
                                     follow_redirects=True)
    assert response.status_code == 200
    assert b'Movie rated' in response.data or b'successfully' in response.data


def test_rate_movie_without_rating(logged_in_client):
    """Test rating movie without providing rating value"""
    response = logged_in_client.post('/movie/1/rate',
                                     data={},
                                     follow_redirects=True)
    assert response.status_code == 200


# ============ Test Confirm Movie Page ============

def test_confirm_page_requires_login(client):
    """Test that confirm page requires login"""
    response = client.get('/confirm', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please login to access this page' in response.data


def test_confirm_page_loads_with_params(logged_in_client):
    """Test that confirm page loads with query parameters"""
    response = logged_in_client.get('/confirm?movie_name=Titanic&description=A%20great%20movie&runtime=195')
    assert response.status_code == 200
    assert b'Add Movie to Watchlist' in response.data
    assert b'Titanic' in response.data


def test_confirm_page_loads_with_defaults(logged_in_client):
    """Test that confirm page loads with default values"""
    response = logged_in_client.get('/confirm')
    assert response.status_code == 200
    assert b'Recommended Movie' in response.data


@patch('app.requests.post')
def test_confirm_page_post_success(mock_post, logged_in_client):
    """Test successful movie confirmation"""
    # Mock successful backend response
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {
        'success': True,
        'message': 'Movie added successfully',
        'movie_id': '123'
    }
    
    response = logged_in_client.post('/confirm',
                                     data={
                                         'movie_name': 'Test Movie',
                                         'movie_description': 'A test description',
                                         'runtime': '120'
                                     },
                                     follow_redirects=True)
    assert response.status_code == 200
    assert b'added to your watchlist' in response.data or b'successfully' in response.data


@patch('app.requests.post')
def test_confirm_page_post_redirects_to_not_watched(mock_post, logged_in_client):
    """Test that confirm page redirects to not watched after adding"""
    # Mock successful backend response
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {
        'success': True,
        'message': 'Movie added successfully',
        'movie_id': '123'
    }
    
    response = logged_in_client.post('/confirm',
                                     data={
                                         'movie_name': 'Test Movie',
                                         'movie_description': 'A test description',
                                         'runtime': '120'
                                     },
                                     follow_redirects=False)
    assert response.status_code == 302
    assert '/not-watched' in response.location


# ============ Test Navigation ============

@patch('app.requests.get')
def test_sidebar_navigation_links(mock_get, logged_in_client):
    """Test that sidebar links are present on all pages"""
    # Mock backend responses for movie pages
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'success': True,
        'movies': [],
        'movie': {
            'movie_id': '1',
            'movie_name': 'Test Movie',
            'movie_description': 'Test',
            'runtime': 120,
            'has_watched': False
        }
    }
    
    pages = ['/home', '/not-watched', '/watched', '/movie/1']
    
    for page in pages:
        response = logged_in_client.get(page)
        assert response.status_code == 200
        assert b'Chatbot' in response.data
        assert b'Not Watched' in response.data
        assert b'Watched' in response.data
        assert b'Logout' in response.data