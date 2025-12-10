"""
Movie routes
Handles movie CRUD operations
"""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from ..DAL import movies_dal
from .utils.validators import validate_movie_data
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

movies_bp = Blueprint('movies', __name__, url_prefix='/api/movies')


@movies_bp.route('/add', methods=['POST'])
def add_movie():
    """
    Add a new movie to user's list
    
    Expected JSON:
        {
            "movie_name": "Inception",
            "movie_description": "A thief who steals corporate secrets...",
            "user_email": "john@example.com",
            "has_watched": false,
            "rating": null,
            "runtime": 148
        }
    
    Returns:
        201: Movie added successfully
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
        is_valid, error_message = validate_movie_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_message
            }), 400
        
        # Create movie document
        movie_doc = {
            'movie_name': data['movie_name'],
            'movie_description': data['movie_description'],
            'user_email': data['user_email'],
            'has_watched': data.get('has_watched', False),
            'rating': data.get('rating'),
            'runtime': data.get('runtime'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert movie
        movie_id = movies_dal.insert_one_movie(movie_doc)
        if not movie_id:
            return jsonify({
                'success': False,
                'message': 'Failed to add movie'
            }), 500
        
        logger.info(f"Movie added for user {data['user_email']}: {data['movie_name']}")
        
        return jsonify({
            'success': True,
            'message': 'Movie added successfully',
            'movie_id': movie_id
        }), 201
        
    except Exception as e:
        logger.error(f"Add movie error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@movies_bp.route('/not-watched', methods=['GET'])
def get_not_watched():
    """
    Get all unwatched movies for a user
    
    Query params:
        user_email: User's email address
    
    Returns:
        200: List of unwatched movies
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
        
        # Find unwatched movies for this user
        all_movies = movies_dal.find_movies_by_user(user_email)
        unwatched_movies = [m for m in all_movies if not m.get('has_watched', False)]
        
        # Convert ObjectId to string
        for movie in unwatched_movies:
            movie['_id'] = str(movie['_id'])
            movie['movie_id'] = str(movie['_id'])
        
        logger.info(f"Retrieved {len(unwatched_movies)} unwatched movies for {user_email}")
        
        return jsonify({
            'success': True,
            'movies': unwatched_movies,
            'count': len(unwatched_movies)
        }), 200
        
    except Exception as e:
        logger.error(f"Get unwatched movies error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@movies_bp.route('/watched', methods=['GET'])
def get_watched():
    """
    Get all watched movies for a user
    
    Query params:
        user_email: User's email address
    
    Returns:
        200: List of watched movies
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
        
        # Find watched movies for this user
        all_movies = movies_dal.find_movies_by_user(user_email)
        watched_movies = [m for m in all_movies if m.get('has_watched', False)]
        
        # Convert ObjectId to string
        for movie in watched_movies:
            movie['_id'] = str(movie['_id'])
            movie['movie_id'] = str(movie['_id'])
        
        logger.info(f"Retrieved {len(watched_movies)} watched movies for {user_email}")
        
        return jsonify({
            'success': True,
            'movies': watched_movies,
            'count': len(watched_movies)
        }), 200
        
    except Exception as e:
        logger.error(f"Get watched movies error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@movies_bp.route('/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    """
    Get a specific movie by ID
    
    Path params:
        movie_id: Movie's ObjectId
    
    Query params:
        user_email: User's email address (for authorization)
    
    Returns:
        200: Movie details
        400: Invalid movie ID or missing user_email
        404: Movie not found
        500: Server error
    """
    try:
        user_email = request.args.get('user_email')
        
        if not user_email:
            return jsonify({
                'success': False,
                'message': 'user_email parameter is required'
            }), 400
        
        # Find movie
        try:
            movie = movies_dal.find_one_movie({
                '_id': ObjectId(movie_id),
                'user_email': user_email
            })
        except Exception:
            return jsonify({
                'success': False,
                'message': 'Invalid movie ID format'
            }), 400
        
        if not movie:
            return jsonify({
                'success': False,
                'message': 'Movie not found'
            }), 404
        
        # Convert ObjectId to string
        movie['_id'] = str(movie['_id'])
        movie['movie_id'] = str(movie['_id'])
        
        logger.info(f"Retrieved movie {movie_id} for user {user_email}")
        
        return jsonify({
            'success': True,
            'movie': movie
        }), 200
        
    except Exception as e:
        logger.error(f"Get movie error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@movies_bp.route('/<movie_id>/rate', methods=['PUT'])
def rate_movie(movie_id):
    """
    Rate a movie and mark as watched
    
    Path params:
        movie_id: Movie's ObjectId
    
    Expected JSON:
        {
            "user_email": "john@example.com",
            "rating": 8.5,
            "has_watched": true
        }
    
    Returns:
        200: Movie updated
        400: Validation error
        404: Movie not found
        500: Server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        user_email = data.get('user_email')
        if not user_email:
            return jsonify({
                'success': False,
                'message': 'user_email is required'
            }), 400
        
        # Validate rating
        rating = data.get('rating')
        if rating is not None:
            try:
                rating = float(rating)
                if rating < 0 or rating > 10:
                    return jsonify({
                        'success': False,
                        'message': 'Rating must be between 0 and 10'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'Rating must be a number'
                }), 400
        
        # Update movie
        try:
            update_data = {
                'rating': rating,
                'has_watched': data.get('has_watched', True),
                'updated_at': datetime.utcnow()
            }
            
            success = movies_dal.update_one_movie(
                {
                    '_id': ObjectId(movie_id),
                    'user_email': user_email
                },
                update_data
            )
        except Exception:
            return jsonify({
                'success': False,
                'message': 'Invalid movie ID format'
            }), 400
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Movie not found or no changes made'
            }), 404
        
        logger.info(f"Movie {movie_id} rated by user {user_email}")
        
        return jsonify({
            'success': True,
            'message': 'Movie updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Rate movie error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@movies_bp.route('/<movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    """
    Delete a movie
    
    Path params:
        movie_id: Movie's ObjectId
    
    Query params:
        user_email: User's email address
    
    Returns:
        200: Movie deleted
        400: Missing user_email
        404: Movie not found
        500: Server error
    """
    try:
        user_email = request.args.get('user_email')
        
        if not user_email:
            return jsonify({
                'success': False,
                'message': 'user_email parameter is required'
            }), 400
        
        # Delete movie
        try:
            success = movies_dal.delete_one_movie({
                '_id': ObjectId(movie_id),
                'user_email': user_email
            })
        except Exception:
            return jsonify({
                'success': False,
                'message': 'Invalid movie ID format'
            }), 400
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Movie not found'
            }), 404
        
        logger.info(f"Movie {movie_id} deleted by user {user_email}")
        
        return jsonify({
            'success': True,
            'message': 'Movie deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete movie error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500