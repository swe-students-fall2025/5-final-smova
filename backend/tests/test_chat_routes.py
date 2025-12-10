# Unit tests for chat routes
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


class TestSendMessage:
    def test_send_message_success_new_convo(self, client):
        with patch('routes.chat.validate_chat_message') as mock_validate, \
             patch('routes.chat.get_ai_recommendation') as mock_ai, \
             patch('routes.chat.conversations_dal') as mock_dal:
            mock_validate.return_value = (True, None)
            mock_ai.return_value = {'response': 'Here are some recommendations', 'source': 'mock'}
            mock_dal.insert_one_conversation.return_value = "convo_123"
            
            response = client.post('/api/chat/message', json={
                'user_email': 'john@example.com',
                'message': 'I like action movies',
                'content': 'I like action movies',
                'role': 'user',
                'convo_id': 1
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'response' in data
    
    def test_send_message_existing_convo(self, client):
        convo_id = str(ObjectId())
        with patch('routes.chat.validate_chat_message') as mock_validate, \
             patch('routes.chat.get_ai_recommendation') as mock_ai, \
             patch('routes.chat.conversations_dal') as mock_dal:
            mock_validate.return_value = (True, None)
            mock_ai.return_value = {'response': 'Here are some recommendations', 'source': 'mock'}
            mock_dal.update_one_conversation.return_value = True
            
            response = client.post('/api/chat/message', json={
                'user_email': 'john@example.com',
                'message': 'I like action movies',
                'content': 'I like action movies',
                'role': 'user',
                'convo_id': convo_id
            })
            
            assert response.status_code == 200
    
    def test_send_message_no_data(self, client):
        response = client.post('/api/chat/message', json={})
        assert response.status_code == 400
    
    def test_send_message_validation_fails(self, client):
        with patch('routes.chat.validate_chat_message') as mock_validate:
            mock_validate.return_value = (False, "Invalid content")
            
            response = client.post('/api/chat/message', json={
                'user_email': 'john@example.com',
                'content': '',
                'role': 'user',
                'convo_id': 1
            })
            
            assert response.status_code == 400
    
    def test_send_message_convo_update_fails(self, client):
        convo_id = str(ObjectId())
        with patch('routes.chat.validate_chat_message') as mock_validate, \
             patch('routes.chat.get_ai_recommendation') as mock_ai, \
             patch('routes.chat.conversations_dal') as mock_dal:
            mock_validate.return_value = (True, None)
            mock_ai.return_value = {'response': 'Here are some recommendations', 'source': 'mock'}
            mock_dal.update_one_conversation.return_value = False
            mock_dal.insert_one_conversation.return_value = "convo_123"
            
            response = client.post('/api/chat/message', json={
                'user_email': 'john@example.com',
                'message': 'I like action movies',
                'content': 'I like action movies',
                'role': 'user',
                'convo_id': convo_id
            })
            
            assert response.status_code == 200


class TestGetConversations:
    def test_get_conversations_success(self, client):
        with patch('routes.chat.conversations_dal') as mock_dal:
            mock_dal.find_conversations_by_user.return_value = [
                {'_id': ObjectId(), 'user_email': 'john@example.com', 'messages': []},
                {'_id': ObjectId(), 'user_email': 'john@example.com', 'messages': []}
            ]
            
            response = client.get('/api/chat/conversations?user_email=john@example.com')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['count'] == 2
    
    def test_get_conversations_missing_email(self, client):
        response = client.get('/api/chat/conversations')
        assert response.status_code == 400


class TestGetConversation:
    def test_get_conversation_success(self, client):
        convo_id = str(ObjectId())
        with patch('routes.chat.conversations_dal') as mock_dal:
            mock_dal.find_one_conversation.return_value = {
                '_id': ObjectId(convo_id),
                'user_email': 'john@example.com',
                'messages': [
                    {'content': 'Hello', 'role': 'user'},
                    {'content': 'Hi there', 'role': 'model'}
                ]
            }
            
            response = client.get(f'/api/chat/conversation/{convo_id}?user_email=john@example.com')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_get_conversation_missing_email(self, client):
        convo_id = str(ObjectId())
        response = client.get(f'/api/chat/conversation/{convo_id}')
        assert response.status_code == 400
    
    def test_get_conversation_invalid_id(self, client):
        response = client.get('/api/chat/conversation/invalid?user_email=john@example.com')
        assert response.status_code == 400
    
    def test_get_conversation_not_found(self, client):
        convo_id = str(ObjectId())
        with patch('routes.chat.conversations_dal') as mock_dal:
            mock_dal.find_one_conversation.return_value = None
            
            response = client.get(f'/api/chat/conversation/{convo_id}?user_email=john@example.com')
            
            assert response.status_code == 404

