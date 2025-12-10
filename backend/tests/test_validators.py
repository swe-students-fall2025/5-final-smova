# Unit tests for validators.py
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.utils.validators import (
    validate_registration_data,
    validate_login_data,
    validate_chat_message,
    validate_movie_data,
)


class TestValidateRegistrationData:
    def test_validate_registration_data_valid(self):
        data = {
            "fname": "John",
            "lname": "Doe",
            "email": "john@example.com",
            "password": "password123"
        }
        result = validate_registration_data(data)
        assert result is True
    
    def test_validate_registration_data_missing_fname(self):
        data = {
            "lname": "Doe",
            "email": "john@example.com",
            "password": "password123"
        }
        result = validate_registration_data(data)
        assert result is False
    
    def test_validate_registration_data_empty_fname(self):
        data = {
            "fname": "",
            "lname": "Doe",
            "email": "john@example.com",
            "password": "password123"
        }
        result = validate_registration_data(data)
        assert result is False
    
    def test_validate_registration_data_missing_email(self):
        data = {
            "fname": "John",
            "lname": "Doe",
            "password": "password123"
        }
        result = validate_registration_data(data)
        assert result is False
    
    def test_validate_registration_data_invalid_email(self):
        data = {
            "fname": "John",
            "lname": "Doe",
            "email": "notanemail",
            "password": "password123"
        }
        result = validate_registration_data(data)
        assert result is False
    
    def test_validate_registration_data_short_password(self):
        data = {
            "fname": "John",
            "lname": "Doe",
            "email": "john@example.com",
            "password": "12345"
        }
        result = validate_registration_data(data)
        assert result is False


class TestValidateLoginData:
    def test_validate_login_data_valid(self):
        data = {
            "email": "user@example.com",
            "password": "password123"
        }
        result = validate_login_data(data)
        assert result is True
    
    def test_validate_login_data_missing_email(self):
        data = {
            "password": "password123"
        }
        result = validate_login_data(data)
        assert result is False
    
    def test_validate_login_data_invalid_email(self):
        data = {
            "email": "notanemail",
            "password": "password123"
        }
        result = validate_login_data(data)
        assert result is False
    
    def test_validate_login_data_missing_password(self):
        data = {
            "email": "user@example.com"
        }
        result = validate_login_data(data)
        assert result is False


class TestValidateChatMessage:
    def test_validate_chat_message_valid(self):
        data = {
            "content": "Hello, I like action movies",
            "role": "user",
            "convo_id": 1
        }
        result = validate_chat_message(data)
        assert result is True
    
    def test_validate_chat_message_role_model(self):
        data = {
            "content": "Here are some recommendations",
            "role": "model",
            "convo_id": 2
        }
        result = validate_chat_message(data)
        assert result is True
    
    def test_validate_chat_message_missing_content(self):
        data = {
            "role": "user",
            "convo_id": 1
        }
        result = validate_chat_message(data)
        assert result is False
    
    def test_validate_chat_message_empty_content(self):
        data = {
            "content": "",
            "role": "user",
            "convo_id": 1
        }
        result = validate_chat_message(data)
        assert result is False
    
    def test_validate_chat_message_invalid_role(self):
        data = {
            "content": "Hello",
            "role": "admin",
            "convo_id": 1
        }
        result = validate_chat_message(data)
        assert result is False
    
    def test_validate_chat_message_missing_convo_id(self):
        data = {
            "content": "Hello",
            "role": "user"
        }
        result = validate_chat_message(data)
        assert result is False
    
    def test_validate_chat_message_convo_id_none(self):
        data = {
            "content": "Hello",
            "role": "user",
            "convo_id": None
        }
        result = validate_chat_message(data)
        assert result is False


class TestValidateMovieData:
    def test_validate_movie_data_valid(self):
        data = {
            "movie_name": "The Matrix",
            "movie_id": 1,
            "movie_description": "A sci-fi action film",
            "has_watched": True,
            "rating": 8.5
        }
        result = validate_movie_data(data)
        assert result is True
    
    def test_validate_movie_data_minimal_valid(self):
        data = {
            "movie_name": "The Matrix",
            "movie_id": 1
        }
        result = validate_movie_data(data)
        assert result is True
    
    def test_validate_movie_data_missing_movie_name(self):
        data = {
            "movie_id": 1
        }
        result = validate_movie_data(data)
        assert result is False
    
    def test_validate_movie_data_empty_movie_name(self):
        data = {
            "movie_name": "",
            "movie_id": 1
        }
        result = validate_movie_data(data)
        assert result is False
    
    def test_validate_movie_data_missing_movie_id(self):
        data = {
            "movie_name": "The Matrix"
        }
        result = validate_movie_data(data)
        assert result is False
    
    def test_validate_movie_data_movie_id_none(self):
        data = {
            "movie_name": "The Matrix",
            "movie_id": None
        }
        result = validate_movie_data(data)
        assert result is False
    
    def test_validate_movie_data_movie_description_non_string(self):
        data = {
            "movie_name": "The Matrix",
            "movie_id": 1,
            "movie_description": 123
        }
        result = validate_movie_data(data)
        assert result is False
    
    def test_validate_movie_data_has_watched_non_boolean(self):
        data = {
            "movie_name": "The Matrix",
            "movie_id": 1,
            "has_watched": "true"
        }
        result = validate_movie_data(data)
        assert result is False
    
    def test_validate_movie_data_rating_invalid(self):
        data = {
            "movie_name": "The Matrix",
            "movie_id": 1,
            "rating": "notanumber"
        }
        result = validate_movie_data(data)
        assert result is False
