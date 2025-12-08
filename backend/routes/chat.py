"""
Chat routes with ML integration
"""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from DAL import conversations_dal
from utils.validators import validate_chat_message
import logging
from datetime import datetime
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'scripts'))

try:
    from ml_client import get_movie_recommendations
    ML_ENABLED = True
except ImportError:
    ML_ENABLED = False
    logging.warning("ML client not available, using mock recommendations")

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


def get_ai_recommendation(user_message):
    """
    Get AI-powered movie recommendation
    
    Args:
        user_message (str): User's chat message
        
    Returns:
        dict: AI response with recommendation
    """
    if ML_ENABLED:
        try:
            # Use real ML client
            response = get_movie_recommendations(user_message, top_k=5)
            return {
                'response': response.text if hasattr(response, 'text') else str(response),
                'source': 'ai'
            }
        except Exception as e:
            logger.error(f"ML client error: {str(e)}")
            # Fall back to mock
    
    # Mock fallback
    return {
        'response': f"I'd recommend checking out some action movies based on your interest in '{user_message}'",
        'source': 'mock'
    }


@chat_bp.route('/message', methods=['POST'])
def send_message():
    """
    Send a chat message and get AI response
    
    Expected JSON:
        {
            "user_email": "john@example.com",
            "message": "Can you recommend a scary horror movie?",
            "convo_id": "optional_conversation_id"
        }
    
    Returns:
        200: Response with AI message
        400: Validation error
        500: Server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate input
        is_valid, error_message = validate_chat_message(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_message
            }), 400
        
        user_email = data['user_email']
        user_message = data['message']
        
        # Get or create conversation ID
        convo_id = data.get('convo_id')
        
        # Get AI-powered recommendation
        ai_result = get_ai_recommendation(user_message)
        ai_response = ai_result['response']
        
        # Create message objects
        user_msg = {
            'timestamp': datetime.utcnow(),
            'content': user_message,
            'role': 'user'
        }
        
        ai_msg = {
            'timestamp': datetime.utcnow(),
            'content': ai_response,
            'role': 'model',
            'source': ai_result['source']  # 'ai' or 'mock'
        }
        
        # Update or create conversation
        if convo_id:
            try:
                success = conversations_dal.update_one_conversation(
                    {
                        '_id': ObjectId(convo_id),
                        'user_email': user_email
                    },
                    {
                        'updated_at': datetime.utcnow()
                    }
                )
                if success:
                    conversations_dal.add_message_to_conversation(convo_id, user_msg)
                    conversations_dal.add_message_to_conversation(convo_id, ai_msg)
                else:
                    convo_id = None
            except Exception:
                convo_id = None
        
        if not convo_id:
            # Create new conversation
            convo_doc = {
                'user_email': user_email,
                'messages': [user_msg, ai_msg],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            convo_id = conversations_dal.insert_one_conversation(convo_doc)
        
        logger.info(f"Chat message processed for user {user_email} (ML: {ML_ENABLED})")
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'convo_id': convo_id,
            'ml_enabled': ML_ENABLED
        }), 200
        
    except Exception as e:
        logger.error(f"Chat message error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@chat_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """
    Get all conversations for a user
    
    Query params:
        user_email: User's email address
    
    Returns:
        200: List of conversations
        400: Missing user_email
        500: Server error
    """
    try:
        user_email = request.args.get('user_email')
        
        if not user_email:
            return jsonify({
                'success': False,
                'message': 'user_email parameter is required'
            }), 400
        
        # Find conversations for this user
        user_convos = conversations_dal.find_conversations_by_user(user_email)
        
        # Remove messages from list view and convert ObjectId
        for convo in user_convos:
            convo['_id'] = str(convo['_id'])
            convo['convo_id'] = str(convo['_id'])
            convo.pop('messages', None)
        
        logger.info(f"Retrieved {len(user_convos)} conversations for {user_email}")
        
        return jsonify({
            'success': True,
            'conversations': user_convos,
            'count': len(user_convos)
        }), 200
        
    except Exception as e:
        logger.error(f"Get conversations error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@chat_bp.route('/conversation/<convo_id>', methods=['GET'])
def get_conversation(convo_id):
    """
    Get a specific conversation with all messages
    
    Path params:
        convo_id: Conversation's ObjectId
    
    Query params:
        user_email: User's email address
    
    Returns:
        200: Conversation details with messages
        400: Missing user_email
        404: Conversation not found
        500: Server error
    """
    try:
        user_email = request.args.get('user_email')
        
        if not user_email:
            return jsonify({
                'success': False,
                'message': 'user_email parameter is required'
            }), 400
        
        # Find conversation
        try:
            convo = conversations_dal.find_one_conversation({
                '_id': ObjectId(convo_id),
                'user_email': user_email
            })
        except Exception:
            return jsonify({
                'success': False,
                'message': 'Invalid conversation ID format'
            }), 400
        
        if not convo:
            return jsonify({
                'success': False,
                'message': 'Conversation not found'
            }), 404
        
        # Convert ObjectId to string
        convo['_id'] = str(convo['_id'])
        convo['convo_id'] = str(convo['_id'])
        
        logger.info(f"Retrieved conversation {convo_id} for user {user_email}")
        
        return jsonify({
            'success': True,
            'conversation': convo
        }), 200
        
    except Exception as e:
        logger.error(f"Get conversation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500