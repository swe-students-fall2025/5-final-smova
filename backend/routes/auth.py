"""
Authentication routes
Handles user registration, login, and token verification
"""
from flask import Blueprint, request, jsonify
from DAL import users_dal
from utils.auth_helpers import hash_password, verify_password, generate_token, decode_token
from utils.validators import validate_registration_data, validate_login_data
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Expected JSON:
        {
            "fname": "John",
            "lname": "Doe",
            "email": "john@example.com",
            "password": "password123"
        }
    
    Returns:
        201: Registration successful
        400: Validation error
        409: Email already exists
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
        is_valid, error_message = validate_registration_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_message
            }), 400
        
        # Check if user already exists
        existing_user = users_dal.find_one_user({'email': data['email']})
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email already exists'
            }), 409
        
        # Hash password
        hashed_password = hash_password(data['password'])
        
        # Create user document
        user_doc = {
            'fname': data['fname'],
            'lname': data['lname'],
            'email': data['email'],
            'password': hashed_password
        }
        
        # Insert user
        user_id = users_dal.insert_one_user(user_doc)
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Failed to create user'
            }), 500
        
        logger.info(f"New user registered: {data['email']}")
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user
    
    Expected JSON:
        {
            "email": "john@example.com",
            "password": "password123"
        }
    
    Returns:
        200: Login successful with token
        400: Validation error
        401: Invalid credentials
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
        is_valid, error_message = validate_login_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_message
            }), 400
        
        # Find user
        user = users_dal.find_one_user({'email': data['email']})
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
        
        # Verify password
        if not verify_password(data['password'], user['password']):
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
        
        # Generate JWT token
        token = generate_token(user['email'])
        
        logger.info(f"User logged in: {data['email']}")
        
        return jsonify({
            'success': True,
            'user_email': user['email'],
            'token': token,
            'user': {
                'fname': user['fname'],
                'lname': user['lname'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """
    Verify JWT token validity
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Token valid
        401: Token invalid or missing
    """
    try:
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid token format'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing'
            }), 401
        
        payload = decode_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'message': 'Token is invalid or expired'
            }), 401
        
        return jsonify({
            'success': True,
            'email': payload['email']
        }), 200
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500