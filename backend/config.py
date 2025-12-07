"""
Configuration management for the backend API
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    ENV = os.getenv('FLASK_ENV', 'development')
    
    # MongoDB
    # Supports both local (mongodb://localhost:27017/movie_app) 
    # and Docker Compose (mongodb://mongo:27017/movie_app)
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/movie_app')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    
    # API
    API_PORT = int(os.getenv('API_PORT', 5001))
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    
    # LLM/AI (to be figured out)
    
    # Testing
    TESTING = False
    
    # CORS - Updated for new frontend port 8000
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8000,http://localhost:5000').split(',')
    
    # Weaviate (Vector Database)
    WEAVIATE_URL = os.getenv('WEAVIATE_URL', 'http://localhost:8080')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/movie_app_test'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}