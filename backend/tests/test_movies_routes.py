# Unit tests for movies routes
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId

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


class TestAddMovie:
    def test_add_movie_success(self, client):
        with patch('routes.movies.movies_dal') as mock_dal, \
             patch('routes.movies.validate_movie_data') as mock_validate:
            mock_validate.return_value = (True, None)
            mock_dal.insert_one_movie.return_value = "movie_123"
            
            response = client.post('/api/movies/add', json={
                'movie_name': 'The Matrix',
                'movie_id': 1,
                'movie_description': 'A sci-fi film',
                'user_email': 'john@example.com',
                'has_watched': False
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['success'] is True
    
    def test_add_movie_no_data(self, client):
        response = client.post('/api/movies/add', json={})
        assert response.status_code == 400
    
    def test_add_movie_validation_fails(self, client):
        with patch('routes.movies.validate_movie_data') as mock_validate:
            mock_validate.return_value = (False, "Invalid movie name")
            
            response = client.post('/api/movies/add', json={
                'movie_name': '',
                'movie_id': 1
            })
            
            assert response.status_code == 400
    
    def test_add_movie_insert_fails(self, client):
        with patch('routes.movies.movies_dal') as mock_dal, \
             patch('routes.movies.validate_movie_data') as mock_validate:
            mock_validate.return_value = (True, None)
            mock_dal.insert_one_movie.return_value = ""
            
            response = client.post('/api/movies/add', json={
                'movie_name': 'The Matrix',
                'movie_id': 1,
                'user_email': 'john@example.com'
            })
            
            assert response.status_code == 500


class TestGetNotWatched:
    def test_get_not_watched_success(self, client):
        with patch('routes.movies.movies_dal') as mock_dal:
            mock_dal.find_movies_by_user.return_value = [
                {'_id': ObjectId(), 'movie_name': 'Movie1', 'has_watched': False},
                {'_id': ObjectId(), 'movie_name': 'Movie2', 'has_watched': True}
            ]
            
            response = client.get('/api/movies/not-watched?user_email=john@example.com')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['count'] == 1
    
    def test_get_not_watched_missing_email(self, client):
        response = client.get('/api/movies/not-watched')
        assert response.status_code == 400


class TestGetWatched:
    def test_get_watched_success(self, client):
        with patch('routes.movies.movies_dal') as mock_dal:
            mock_dal.find_movies_by_user.return_value = [
                {'_id': ObjectId(), 'movie_name': 'Movie1', 'has_watched': False},
                {'_id': ObjectId(), 'movie_name': 'Movie2', 'has_watched': True}
            ]
            
            response = client.get('/api/movies/watched?user_email=john@example.com')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['count'] == 1
    
    def test_get_watched_missing_email(self, client):
        response = client.get('/api/movies/watched')
        assert response.status_code == 400


class TestGetMovie:
    def test_get_movie_success(self, client):
        movie_id = str(ObjectId())
        with patch('routes.movies.movies_dal') as mock_dal:
            mock_dal.find_one_movie.return_value = {
                '_id': ObjectId(movie_id),
                'movie_name': 'The Matrix',
                'user_email': 'john@example.com'
            }
            
            response = client.get(f'/api/movies/{movie_id}?user_email=john@example.com')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_get_movie_missing_email(self, client):
        movie_id = str(ObjectId())
        response = client.get(f'/api/movies/{movie_id}')
        assert response.status_code == 400
    
    def test_get_movie_invalid_id(self, client):
        response = client.get('/api/movies/invalid?user_email=john@example.com')
        assert response.status_code == 400
    
    def test_get_movie_not_found(self, client):
        movie_id = str(ObjectId())
        with patch('routes.movies.movies_dal') as mock_dal:
            mock_dal.find_one_movie.return_value = None
            
            response = client.get(f'/api/movies/{movie_id}?user_email=john@example.com')
            
            assert response.status_code == 404


class TestRateMovie:
    def test_rate_movie_success(self, client):
        movie_id = str(ObjectId())
        with patch('routes.movies.movies_dal') as mock_dal:
            mock_dal.update_one_movie.return_value = True
            
            response = client.put(f'/api/movies/{movie_id}/rate', json={
                'user_email': 'john@example.com',
                'rating': 8.5,
                'has_watched': True
            })
            
            assert response.status_code == 200
    
    def test_rate_movie_no_data(self, client):
        movie_id = str(ObjectId())
        response = client.put(f'/api/movies/{movie_id}/rate', json={})
        assert response.status_code == 400
    
    def test_rate_movie_missing_email(self, client):
        movie_id = str(ObjectId())
        response = client.put(f'/api/movies/{movie_id}/rate', json={
            'rating': 8.5
        })
        assert response.status_code == 400
    
    def test_rate_movie_invalid_rating_high(self, client):
        movie_id = str(ObjectId())
        response = client.put(f'/api/movies/{movie_id}/rate', json={
            'user_email': 'john@example.com',
            'rating': 11
        })
        assert response.status_code == 400
    
    def test_rate_movie_invalid_rating_low(self, client):
        movie_id = str(ObjectId())
        response = client.put(f'/api/movies/{movie_id}/rate', json={
            'user_email': 'john@example.com',
            'rating': -1
        })
        assert response.status_code == 400
    
    def test_rate_movie_not_found(self, client):
        movie_id = str(ObjectId())
        with patch('routes.movies.movies_dal') as mock_dal:
            mock_dal.update_one_movie.return_value = False
            
            response = client.put(f'/api/movies/{movie_id}/rate', json={
                'user_email': 'john@example.com',
                'rating': 8.5
            })
            
            assert response.status_code == 404


class TestDeleteMovie:
    def test_delete_movie_success(self, client):
        movie_id = str(ObjectId())
        with patch('routes.movies.movies_dal') as mock_dal:
            mock_dal.delete_one_movie.return_value = True
            
            response = client.delete(f'/api/movies/{movie_id}?user_email=john@example.com')
            
            assert response.status_code == 200
    
    def test_delete_movie_missing_email(self, client):
        movie_id = str(ObjectId())
        response = client.delete(f'/api/movies/{movie_id}')
        assert response.status_code == 400
    
    def test_delete_movie_invalid_id(self, client):
        response = client.delete('/api/movies/invalid?user_email=john@example.com')
        assert response.status_code == 400
    
    def test_delete_movie_not_found(self, client):
        movie_id = str(ObjectId())
        with patch('routes.movies.movies_dal') as mock_dal:
            mock_dal.delete_one_movie.return_value = False
            
            response = client.delete(f'/api/movies/{movie_id}?user_email=john@example.com')
            
            assert response.status_code == 404

