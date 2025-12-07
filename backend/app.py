"""
Backend API Server for Movie Recommendation System
Main Flask application
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from routes.auth import auth_bp
from routes.movies import movies_bp
from routes.chat import chat_bp
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='development'):
    """
    Application factory
    
    Args:
        config_name (str): Configuration name
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    logger.info("Application initialized")
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(chat_bp)
    
    logger.info("All routes registered successfully")
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'movie-backend-api',
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        """API information endpoint"""
        return jsonify({
            'name': 'Movie Recommendation API',
            'version': '1.0.0',
            'endpoints': {
                'auth': {
                    'register': 'POST /api/auth/register',
                    'login': 'POST /api/auth/login',
                    'verify': 'GET /api/auth/verify'
                },
                'movies': {
                    'add': 'POST /api/movies/add',
                    'not_watched': 'GET /api/movies/not-watched?user_email=<email>',
                    'watched': 'GET /api/movies/watched?user_email=<email>',
                    'get': 'GET /api/movies/<movie_id>?user_email=<email>',
                    'rate': 'PUT /api/movies/<movie_id>/rate',
                    'delete': 'DELETE /api/movies/<movie_id>?user_email=<email>'
                },
                'chat': {
                    'message': 'POST /api/chat/message',
                    'conversations': 'GET /api/chat/conversations?user_email=<email>',
                    'conversation': 'GET /api/chat/conversation/<convo_id>?user_email=<email>'
                }
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'success': False,
            'message': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors"""
        return jsonify({
            'success': False,
            'message': 'Method not allowed'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    return app


if __name__ == '__main__':
    # Create app
    app = create_app('development')
    
    # Run server
    host = app.config['API_HOST']
    port = app.config['API_PORT']
    
    logger.info(f"Starting server on {host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=True
    )