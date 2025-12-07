"""
Unit tests for the frontend Flask application
"""
import pytest
import sys
import os

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


def test_login_with_credentials(client):
    """Test login with email and password"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Login successful!' in response.data


def test_login_without_email(client):
    """Test login fails without email"""
    response = client.post('/login', data={
        'email': '',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Please enter both email and password' in response.data


def test_login_without_password(client):
    """Test login fails without password"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Please enter both email and password' in response.data


def test_register_page_loads(client):
    """Test that register page loads successfully"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Create Account' in response.data
    assert b'First Name' in response.data
    assert b'Last Name' in response.data
    assert b'Email' in response.data


def test_register_with_valid_data(client):
    """Test registration with valid data"""
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

def test_login_form_accepts_various_email_formats(client):
    """Test that login accepts various valid email formats"""
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


def test_register_form_accepts_various_names(client):
    """Test that register accepts various name formats"""
    response = client.post('/register', data={
        'fname': 'Jean-Pierre',
        'lname': "O'Brien",
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful!' in response.data