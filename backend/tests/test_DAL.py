"""
Unit tests for the Data Access Layer (DAL)
Tests all DAL classes: users_dal, movies_dal, messages_dal, conversations_dal
"""
import os
import sys
import pytest
from datetime import datetime

# Set TESTING environment variable before importing DAL
os.environ["TESTING"] = "1"

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.DAL import (
    users_dal,
    movies_dal,
    messages_dal,
    conversations_dal,
    db_app,
    db_vector,
)


@pytest.fixture(autouse=True)
def reset_databases():
    """Reset all databases before and after each test"""
    # Clear before test
    db_app.users[:] = []
    db_app.movies[:] = []
    db_app.messages[:] = []
    db_app.conversations[:] = []
    db_vector.users[:] = []
    db_vector.movies[:] = []
    db_vector.messages[:] = []
    db_vector.conversations[:] = []
    yield
    # Cleanup after test
    db_app.users[:] = []
    db_app.movies[:] = []
    db_app.messages[:] = []
    db_app.conversations[:] = []
    db_vector.users[:] = []
    db_vector.movies[:] = []
    db_vector.messages[:] = []
    db_vector.conversations[:] = []


# ============ Users DAL Tests ============

class TestUsersDAL:
    """Test users_dal class"""
    
    def test_insert_one_user(self):
        """Test inserting a user"""
        user_data = {
            "fname": "John",
            "lname": "Doe",
            "email": "john@example.com",
            "password": "password123"
        }
        user_id = users_dal.insert_one_user(user_data)
        assert user_id != ""
        assert user_id.startswith("user_")
    
    def test_find_one_user(self):
        """Test finding a user by filter"""
        user_data = {
            "fname": "Jane",
            "lname": "Smith",
            "email": "jane@example.com",
            "password": "password456"
        }
        user_id = users_dal.insert_one_user(user_data)
        
        found_user = users_dal.find_one_user({"email": "jane@example.com"})
        assert found_user is not None
        assert found_user["email"] == "jane@example.com"
        assert found_user["fname"] == "Jane"
    
    def test_find_one_user_not_found(self):
        """Test finding a user that doesn't exist"""
        found_user = users_dal.find_one_user({"email": "nonexistent@example.com"})
        assert found_user is None
    
    def test_find_all_users(self):
        """Test finding all users"""
        users_dal.insert_one_user({"fname": "User1", "lname": "Test", "email": "user1@test.com", "password": "pass1"})
        users_dal.insert_one_user({"fname": "User2", "lname": "Test", "email": "user2@test.com", "password": "pass2"})
        
        all_users = users_dal.find_all_users()
        assert len(all_users) == 2
    
    def test_find_all_users_empty(self):
        """Test finding all users when none exist"""
        all_users = users_dal.find_all_users()
        assert len(all_users) == 0
    
    def test_update_one_user(self):
        """Test updating a user"""
        user_data = {
            "fname": "Original",
            "lname": "Name",
            "email": "original@example.com",
            "password": "oldpass"
        }
        users_dal.insert_one_user(user_data)
        
        updated = users_dal.update_one_user(
            {"email": "original@example.com"},
            {"fname": "Updated", "password": "newpass"}
        )
        assert updated is True
        
        found_user = users_dal.find_one_user({"email": "original@example.com"})
        assert found_user["fname"] == "Updated"
        assert found_user["password"] == "newpass"
    
    def test_update_one_user_not_found(self):
        """Test updating a user that doesn't exist"""
        updated = users_dal.update_one_user(
            {"email": "nonexistent@example.com"},
            {"fname": "Updated"}
        )
        assert updated is False
    
    def test_delete_one_user(self):
        """Test deleting a user"""
        user_data = {
            "fname": "Delete",
            "lname": "Me",
            "email": "delete@example.com",
            "password": "pass"
        }
        users_dal.insert_one_user(user_data)
        
        deleted = users_dal.delete_one_user({"email": "delete@example.com"})
        assert deleted is True
        
        found_user = users_dal.find_one_user({"email": "delete@example.com"})
        assert found_user is None
    
    def test_delete_one_user_not_found(self):
        """Test deleting a user that doesn't exist"""
        deleted = users_dal.delete_one_user({"email": "nonexistent@example.com"})
        assert deleted is False


# ============ Movies DAL Tests ============

class TestMoviesDAL:
    """Test movies_dal class"""
    
    def test_insert_one_movie(self):
        """Test inserting a movie"""
        movie_data = {
            "movie_name": "The Matrix",
            "movie_id": 1,
            "movie_description": "A sci-fi action film",
            "has_watched": False,
            "rating": None
        }
        movie_id = movies_dal.insert_one_movie(movie_data)
        assert movie_id != ""
        assert movie_id.startswith("movie_")
    
    def test_find_one_movie(self):
        """Test finding a movie by filter"""
        movie_data = {
            "movie_name": "Inception",
            "movie_id": 2,
            "movie_description": "A mind-bending thriller",
            "has_watched": True,
            "rating": 9
        }
        movies_dal.insert_one_movie(movie_data)
        
        found_movie = movies_dal.find_one_movie({"movie_id": 2})
        assert found_movie is not None
        assert found_movie["movie_name"] == "Inception"
        assert found_movie["rating"] == 9
    
    def test_find_one_movie_not_found(self):
        """Test finding a movie that doesn't exist"""
        found_movie = movies_dal.find_one_movie({"movie_id": 999})
        assert found_movie is None
    
    def test_find_all_movies(self):
        """Test finding all movies"""
        movies_dal.insert_one_movie({"movie_name": "Movie1", "movie_id": 10, "movie_description": "Desc1", "has_watched": False, "rating": None})
        movies_dal.insert_one_movie({"movie_name": "Movie2", "movie_id": 11, "movie_description": "Desc2", "has_watched": True, "rating": 8})
        
        all_movies = movies_dal.find_all_movies()
        assert len(all_movies) == 2
    
    def test_find_movies_by_user(self):
        """Test finding movies by user email"""
        movies_dal.insert_one_movie({
            "movie_name": "User Movie",
            "movie_id": 20,
            "movie_description": "A movie",
            "has_watched": True,
            "rating": 7,
            "user_email": "user@example.com"
        })
        movies_dal.insert_one_movie({
            "movie_name": "Other Movie",
            "movie_id": 21,
            "movie_description": "Another movie",
            "has_watched": False,
            "rating": None,
            "user_email": "other@example.com"
        })
        
        user_movies = movies_dal.find_movies_by_user("user@example.com")
        assert len(user_movies) == 1
        assert user_movies[0]["movie_name"] == "User Movie"
    
    def test_find_movies_by_user_empty(self):
        """Test finding movies by user when none exist"""
        user_movies = movies_dal.find_movies_by_user("nonexistent@example.com")
        assert len(user_movies) == 0
    
    def test_update_one_movie(self):
        """Test updating a movie"""
        movie_data = {
            "movie_name": "Original Title",
            "movie_id": 30,
            "movie_description": "Original description",
            "has_watched": False,
            "rating": None
        }
        movies_dal.insert_one_movie(movie_data)
        
        updated = movies_dal.update_one_movie(
            {"movie_id": 30},
            {"has_watched": True, "rating": 9}
        )
        assert updated is True
        
        found_movie = movies_dal.find_one_movie({"movie_id": 30})
        assert found_movie["has_watched"] is True
        assert found_movie["rating"] == 9
    
    def test_update_one_movie_not_found(self):
        """Test updating a movie that doesn't exist"""
        updated = movies_dal.update_one_movie(
            {"movie_id": 999},
            {"rating": 10}
        )
        assert updated is False
    
    def test_delete_one_movie(self):
        """Test deleting a movie"""
        movie_data = {
            "movie_name": "Delete Me",
            "movie_id": 40,
            "movie_description": "To be deleted",
            "has_watched": False,
            "rating": None
        }
        movies_dal.insert_one_movie(movie_data)
        
        deleted = movies_dal.delete_one_movie({"movie_id": 40})
        assert deleted is True
        
        found_movie = movies_dal.find_one_movie({"movie_id": 40})
        assert found_movie is None
    
    def test_delete_one_movie_not_found(self):
        """Test deleting a movie that doesn't exist"""
        deleted = movies_dal.delete_one_movie({"movie_id": 999})
        assert deleted is False


# ============ Messages DAL Tests ============

class TestMessagesDAL:
    """Test messages_dal class"""
    
    def test_insert_one_message(self):
        """Test inserting a message"""
        message_data = {
            "content": "Hello, I like action movies",
            "role": "user",
            "convo_id": 1
        }
        message_id = messages_dal.insert_one_message(message_data)
        assert message_id != ""
        assert message_id.startswith("message_")
        assert "timestamp" in message_data
    
    def test_insert_one_message_with_timestamp(self):
        """Test inserting a message with existing timestamp"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        message_data = {
            "content": "Test message",
            "role": "user",
            "convo_id": 2,
            "timestamp": timestamp
        }
        message_id = messages_dal.insert_one_message(message_data)
        assert message_id != ""
        found_message = messages_dal.find_one_message({"_id": message_id})
        assert found_message["timestamp"] == timestamp
    
    def test_find_one_message(self):
        """Test finding a message by filter"""
        message_data = {
            "content": "Find me",
            "role": "user",
            "convo_id": 3
        }
        message_id = messages_dal.insert_one_message(message_data)
        
        found_message = messages_dal.find_one_message({"convo_id": 3})
        assert found_message is not None
        assert found_message["content"] == "Find me"
    
    def test_find_one_message_not_found(self):
        """Test finding a message that doesn't exist"""
        found_message = messages_dal.find_one_message({"convo_id": 999})
        assert found_message is None
    
    def test_find_all_messages(self):
        """Test finding all messages"""
        messages_dal.insert_one_message({"content": "Message 1", "role": "user", "convo_id": 4})
        messages_dal.insert_one_message({"content": "Message 2", "role": "model", "convo_id": 4})
        
        all_messages = messages_dal.find_all_messages()
        assert len(all_messages) == 2
    
    def test_find_messages_by_convo(self):
        """Test finding messages by conversation ID"""
        # Insert messages with different timestamps
        msg1 = {"content": "First", "role": "user", "convo_id": 5, "timestamp": datetime(2024, 1, 1, 10, 0, 0)}
        msg2 = {"content": "Second", "role": "model", "convo_id": 5, "timestamp": datetime(2024, 1, 1, 10, 1, 0)}
        msg3 = {"content": "Third", "role": "user", "convo_id": 5, "timestamp": datetime(2024, 1, 1, 10, 2, 0)}
        msg4 = {"content": "Other convo", "role": "user", "convo_id": 6, "timestamp": datetime(2024, 1, 1, 11, 0, 0)}
        
        messages_dal.insert_one_message(msg1)
        messages_dal.insert_one_message(msg2)
        messages_dal.insert_one_message(msg3)
        messages_dal.insert_one_message(msg4)
        
        convo_messages = messages_dal.find_messages_by_convo(5)
        assert len(convo_messages) == 3
        assert convo_messages[0]["content"] == "First"
        assert convo_messages[1]["content"] == "Second"
        assert convo_messages[2]["content"] == "Third"
    
    def test_find_messages_by_convo_empty(self):
        """Test finding messages by conversation when none exist"""
        convo_messages = messages_dal.find_messages_by_convo(999)
        assert len(convo_messages) == 0
    
    def test_update_one_message(self):
        """Test updating a message"""
        message_data = {
            "content": "Original content",
            "role": "user",
            "convo_id": 7
        }
        messages_dal.insert_one_message(message_data)
        
        updated = messages_dal.update_one_message(
            {"convo_id": 7},
            {"content": "Updated content"}
        )
        assert updated is True
        
        found_message = messages_dal.find_one_message({"convo_id": 7})
        assert found_message["content"] == "Updated content"
    
    def test_update_one_message_not_found(self):
        """Test updating a message that doesn't exist"""
        updated = messages_dal.update_one_message(
            {"convo_id": 999},
            {"content": "Updated"}
        )
        assert updated is False
    
    def test_delete_one_message(self):
        """Test deleting a message"""
        message_data = {
            "content": "Delete me",
            "role": "user",
            "convo_id": 8
        }
        messages_dal.insert_one_message(message_data)
        
        deleted = messages_dal.delete_one_message({"convo_id": 8})
        assert deleted is True
        
        found_message = messages_dal.find_one_message({"convo_id": 8})
        assert found_message is None
    
    def test_delete_one_message_not_found(self):
        """Test deleting a message that doesn't exist"""
        deleted = messages_dal.delete_one_message({"convo_id": 999})
        assert deleted is False


# ============ Conversations DAL Tests ============

class TestConversationsDAL:
    """Test conversations_dal class"""
    
    def test_insert_one_conversation(self):
        """Test inserting a conversation"""
        conversation_data = {
            "user_email": "user@example.com",
            "convo_id": 1
        }
        convo_id = conversations_dal.insert_one_conversation(conversation_data)
        assert convo_id != ""
        assert convo_id.startswith("convo_")
        assert "messages" in conversation_data
    
    def test_insert_one_conversation_with_messages(self):
        """Test inserting a conversation with existing messages"""
        conversation_data = {
            "user_email": "user@example.com",
            "convo_id": 2,
            "messages": [{"content": "Hello", "role": "user"}]
        }
        convo_id = conversations_dal.insert_one_conversation(conversation_data)
        assert convo_id != ""
    
    def test_find_one_conversation(self):
        """Test finding a conversation by filter"""
        conversation_data = {
            "user_email": "find@example.com",
            "convo_id": 3
        }
        conversations_dal.insert_one_conversation(conversation_data)
        
        found_convo = conversations_dal.find_one_conversation({"convo_id": 3})
        assert found_convo is not None
        assert found_convo["user_email"] == "find@example.com"
    
    def test_find_one_conversation_not_found(self):
        """Test finding a conversation that doesn't exist"""
        found_convo = conversations_dal.find_one_conversation({"convo_id": 999})
        assert found_convo is None
    
    def test_find_all_conversations(self):
        """Test finding all conversations"""
        conversations_dal.insert_one_conversation({"user_email": "user1@example.com", "convo_id": 10})
        conversations_dal.insert_one_conversation({"user_email": "user2@example.com", "convo_id": 11})
        
        all_convos = conversations_dal.find_all_conversations()
        assert len(all_convos) == 2
    
    def test_find_conversations_by_user(self):
        """Test finding conversations by user email"""
        conversations_dal.insert_one_conversation({"user_email": "same@example.com", "convo_id": 20})
        conversations_dal.insert_one_conversation({"user_email": "same@example.com", "convo_id": 21})
        conversations_dal.insert_one_conversation({"user_email": "other@example.com", "convo_id": 22})
        
        user_convos = conversations_dal.find_conversations_by_user("same@example.com")
        assert len(user_convos) == 2
    
    def test_find_conversations_by_user_empty(self):
        """Test finding conversations by user when none exist"""
        user_convos = conversations_dal.find_conversations_by_user("nonexistent@example.com")
        assert len(user_convos) == 0
    
    def test_update_one_conversation(self):
        """Test updating a conversation"""
        conversation_data = {
            "user_email": "update@example.com",
            "convo_id": 30
        }
        conversations_dal.insert_one_conversation(conversation_data)
        
        updated = conversations_dal.update_one_conversation(
            {"convo_id": 30},
            {"user_email": "updated@example.com"}
        )
        assert updated is True
        
        found_convo = conversations_dal.find_one_conversation({"convo_id": 30})
        assert found_convo["user_email"] == "updated@example.com"
    
    def test_update_one_conversation_not_found(self):
        """Test updating a conversation that doesn't exist"""
        updated = conversations_dal.update_one_conversation(
            {"convo_id": 999},
            {"user_email": "updated@example.com"}
        )
        assert updated is False
    
    def test_add_message_to_conversation(self):
        """Test adding a message to a conversation"""
        conversation_data = {
            "user_email": "addmsg@example.com",
            "convo_id": 40
        }
        conversations_dal.insert_one_conversation(conversation_data)
        
        message_data = {"content": "New message", "role": "user", "timestamp": datetime.now()}
        added = conversations_dal.add_message_to_conversation(40, message_data)
        assert added is True
        
        found_convo = conversations_dal.find_one_conversation({"convo_id": 40})
        assert len(found_convo["messages"]) == 1
        assert found_convo["messages"][0]["content"] == "New message"
    
    def test_add_message_to_conversation_not_found(self):
        """Test adding a message to a conversation that doesn't exist"""
        message_data = {"content": "Test", "role": "user"}
        added = conversations_dal.add_message_to_conversation(999, message_data)
        assert added is False
    
    def test_add_multiple_messages_to_conversation(self):
        """Test adding multiple messages to a conversation"""
        conversation_data = {
            "user_email": "multi@example.com",
            "convo_id": 50
        }
        conversations_dal.insert_one_conversation(conversation_data)
        
        msg1 = {"content": "First", "role": "user", "timestamp": datetime.now()}
        msg2 = {"content": "Second", "role": "model", "timestamp": datetime.now()}
        
        conversations_dal.add_message_to_conversation(50, msg1)
        conversations_dal.add_message_to_conversation(50, msg2)
        
        found_convo = conversations_dal.find_one_conversation({"convo_id": 50})
        assert len(found_convo["messages"]) == 2
    
    def test_delete_one_conversation(self):
        """Test deleting a conversation"""
        conversation_data = {
            "user_email": "delete@example.com",
            "convo_id": 60
        }
        conversations_dal.insert_one_conversation(conversation_data)
        
        deleted = conversations_dal.delete_one_conversation({"convo_id": 60})
        assert deleted is True
        
        found_convo = conversations_dal.find_one_conversation({"convo_id": 60})
        assert found_convo is None
    
    def test_delete_one_conversation_not_found(self):
        """Test deleting a conversation that doesn't exist"""
        deleted = conversations_dal.delete_one_conversation({"convo_id": 999})
        assert deleted is False

