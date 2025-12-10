"""
Chat routes with ML integration
"""
from flask import Blueprint, request, jsonify
from bson import ObjectId
import logging
from datetime import datetime
import sys
from ml_client import get_movie_recommendations

import os

from ..DAL import conversations_dal
from .utils.validators import validate_chat_message

logger = logging.getLogger(__name__)



chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


def get_ai_recommendation(user_message: str) -> dict:
    """
    Get AI-powered movie recommendation

    Args:
        user_message (str): User's chat message

    Returns:
        dict: {
            'response': str,
            'source': 'ai' | 'mock'
        }
    """
    response = get_movie_recommendations(user_message, top_k=5)
    return {
        'response': response,
        'source': 'ai'
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
                'message': 'No data provided',
                'error_code': 'NO_DATA'
            }), 400
        

        # Validate input
        is_valid, error_message = validate_chat_message(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_message,
                'error_code': 'VALIDATION_ERROR'
            }), 400

        user_email = data['user_email']
        user_message = data['message']
        convo_id = data.get('convo_id')  # may be None or a string

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
                # Try to update existing conversation
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
                    # convo_id is valid format but no matching convo; treat as new
                    convo_id = None
            except Exception:
                # Invalid ObjectId format or DAL error; treat as new conversation
                logger.exception("Error updating existing conversation; will create new one")
                convo_id = None

        if not convo_id:
            # Create new conversation
            convo_doc = {
                'user_email': user_email,
                'messages': [user_msg, ai_msg],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }

            inserted_id = conversations_dal.insert_one_conversation(convo_doc)
            # Ensure we always return a string
            convo_id = str(inserted_id)

        logger.info(f"Chat message processed for user {user_email} )")

        return jsonify({
            'success': True,
            'response': ai_response,
            'convo_id': convo_id,
        }), 200

    except Exception:
        logger.exception("Chat message error")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
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
                'message': 'user_email parameter is required',
                'error_code': 'MISSING_USER_EMAIL'
            }), 400

        # Find conversations for this user
        user_convos = conversations_dal.find_conversations_by_user(user_email)

        # Remove messages from list view and convert ObjectId
        for convo in user_convos:
            convo_id = str(convo['_id'])
            convo['_id'] = convo_id
            convo['convo_id'] = convo_id
            convo.pop('messages', None)

        logger.info(f"Retrieved {len(user_convos)} conversations for {user_email}")

        return jsonify({
            'success': True,
            'conversations': user_convos,
            'count': len(user_convos)
        }), 200

    except Exception:
        logger.exception("Get conversations error")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@chat_bp.route('/conversation/<convo_id>', methods=['GET'])
def get_conversation(convo_id):
    """
    Get a specific conversation with all messages

    Path params:
        convo_id: Conversation's ObjectId (string)

    Query params:
        user_email: User's email address

    Returns:
        200: Conversation details with messages
        400: Missing user_email or invalid convo_id
        404: Conversation not found
        500: Server error
    """
    try:
        user_email = request.args.get('user_email')

        if not user_email:
            return jsonify({
                'success': False,
                'message': 'user_email parameter is required',
                'error_code': 'MISSING_USER_EMAIL'
            }), 400

        # Find conversation
        try:
            convo = conversations_dal.find_one_conversation({
                '_id': ObjectId(convo_id),
                'user_email': user_email
            })
        except Exception:
            logger.exception("Invalid conversation ID format")
            return jsonify({
                'success': False,
                'message': 'Invalid conversation ID format',
                'error_code': 'INVALID_CONVO_ID'
            }), 400

        if not convo:
            return jsonify({
                'success': False,
                'message': 'Conversation not found',
                'error_code': 'CONVO_NOT_FOUND'
            }), 404

        # Convert ObjectId to string
        convo_id_str = str(convo['_id'])
        convo['_id'] = convo_id_str
        convo['convo_id'] = convo_id_str

        # NOTE: if your messages contain datetimes, make sure your JSON encoder can
        # handle them, or convert to isoformat here.

        logger.info(f"Retrieved conversation {convo_id} for user {user_email}")

        return jsonify({
            'success': True,
            'conversation': convo
        }), 200

    except Exception:
        logger.exception("Get conversation error")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        }), 500
