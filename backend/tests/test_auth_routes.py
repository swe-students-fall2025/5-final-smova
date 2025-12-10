# Unit tests for auth routes
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add backend directory to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

os.environ["TESTING"] = "1"
from app import create_app


@pytest.fixture
def client():
    app = create_app('development')
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestRegister:
    def test_register_success(self, client):
        with patch('routes.auth.users_dal') as mock_dal, \
             patch('routes.auth.validate_registration_data') as mock_validate, \
             patch('routes.auth.hash_password') as mock_hash:
            mock_validate.return_value = (True, None)
            mock_dal.find_one_user.return_value = None
            mock_dal.insert_one_user.return_value = "user_123"
            mock_hash.return_value = "hashed_password"
            
            response = client.post('/api/auth/register', json={
                'fname': 'John',
                'lname': 'Doe',
                'email': 'john@example.com',
                'password': 'password123'
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['success'] is True
    
    def test_register_no_data(self, client):
        response = client.post('/api/auth/register', json={})
        assert response.status_code == 400
    
    def test_register_validation_fails(self, client):
        with patch('routes.auth.validate_registration_data') as mock_validate:
            mock_validate.return_value = (False, "Invalid email")
            
            response = client.post('/api/auth/register', json={
                'fname': 'John',
                'lname': 'Doe',
                'email': 'invalid',
                'password': 'password123'
            })
            
            assert response.status_code == 400
    
    def test_register_email_exists(self, client):
        with patch('routes.auth.users_dal') as mock_dal, \
             patch('routes.auth.validate_registration_data') as mock_validate:
            mock_validate.return_value = (True, None)
            mock_dal.find_one_user.return_value = {'email': 'john@example.com'}
            
            response = client.post('/api/auth/register', json={
                'fname': 'John',
                'lname': 'Doe',
                'email': 'john@example.com',
                'password': 'password123'
            })
            
            assert response.status_code == 409
    
    def test_register_insert_fails(self, client):
        with patch('routes.auth.users_dal') as mock_dal, \
             patch('routes.auth.validate_registration_data') as mock_validate, \
             patch('routes.auth.hash_password') as mock_hash:
            mock_validate.return_value = (True, None)
            mock_dal.find_one_user.return_value = None
            mock_dal.insert_one_user.return_value = ""
            mock_hash.return_value = "hashed_password"
            
            response = client.post('/api/auth/register', json={
                'fname': 'John',
                'lname': 'Doe',
                'email': 'john@example.com',
                'password': 'password123'
            })
            
            assert response.status_code == 500


class TestLogin:
    def test_login_success(self, client):
        with patch('routes.auth.users_dal') as mock_dal, \
             patch('routes.auth.validate_login_data') as mock_validate, \
             patch('routes.auth.verify_password') as mock_verify, \
             patch('routes.auth.generate_token') as mock_token:
            mock_validate.return_value = (True, None)
            mock_dal.find_one_user.return_value = {
                'email': 'john@example.com',
                'password': 'hashed_password',
                'fname': 'John',
                'lname': 'Doe'
            }
            mock_verify.return_value = True
            mock_token.return_value = "token123"
            
            response = client.post('/api/auth/login', json={
                'email': 'john@example.com',
                'password': 'password123'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'token' in data
    
    def test_login_no_data(self, client):
        response = client.post('/api/auth/login', json={})
        assert response.status_code == 400
    
    def test_login_validation_fails(self, client):
        with patch('routes.auth.validate_login_data') as mock_validate:
            mock_validate.return_value = (False, "Invalid email")
            
            response = client.post('/api/auth/login', json={
                'email': 'invalid',
                'password': 'password123'
            })
            
            assert response.status_code == 400
    
    def test_login_user_not_found(self, client):
        with patch('routes.auth.users_dal') as mock_dal, \
             patch('routes.auth.validate_login_data') as mock_validate:
            mock_validate.return_value = (True, None)
            mock_dal.find_one_user.return_value = None
            
            response = client.post('/api/auth/login', json={
                'email': 'john@example.com',
                'password': 'password123'
            })
            
            assert response.status_code == 401
    
    def test_login_wrong_password(self, client):
        with patch('routes.auth.users_dal') as mock_dal, \
             patch('routes.auth.validate_login_data') as mock_validate, \
             patch('routes.auth.verify_password') as mock_verify:
            mock_validate.return_value = (True, None)
            mock_dal.find_one_user.return_value = {
                'email': 'john@example.com',
                'password': 'hashed_password'
            }
            mock_verify.return_value = False
            
            response = client.post('/api/auth/login', json={
                'email': 'john@example.com',
                'password': 'wrongpassword'
            })
            
            assert response.status_code == 401


class TestVerifyToken:
    def test_verify_token_success(self, client):
        with patch('routes.auth.decode_token') as mock_decode:
            mock_decode.return_value = {'email': 'john@example.com'}
            
            response = client.get('/api/auth/verify', headers={
                'Authorization': 'Bearer token123'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_verify_token_missing(self, client):
        response = client.get('/api/auth/verify')
        assert response.status_code == 401
    
    def test_verify_token_invalid_format(self, client):
        response = client.get('/api/auth/verify', headers={
            'Authorization': 'InvalidFormat'
        })
        assert response.status_code == 401
    
    def test_verify_token_invalid(self, client):
        with patch('routes.auth.decode_token') as mock_decode:
            mock_decode.return_value = None
            
            response = client.get('/api/auth/verify', headers={
                'Authorization': 'Bearer invalidtoken'
            })
            
            assert response.status_code == 401

