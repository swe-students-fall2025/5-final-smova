"""
Configuration settings for the Flask application
"""
import os


class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    
    # API
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5001))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8000,http://localhost:5000').split(',')
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017/movie_app')
    
    # Weaviate
    WEAVIATE_URL = os.getenv('WEAVIATE_URL', 'http://weaviate:8080')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/movie_app_test'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}