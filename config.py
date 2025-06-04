"""
AITON-RAG Configuration Module
Zentrale Konfiguration für die gesamte Anwendung
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Base Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    UPLOAD_DIR = DATA_DIR / "uploads"  # Updated name for consistency
    RAG_DATA_DIR = DATA_DIR / "rag"   # Updated name for consistency
    KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
    LOG_DIR = BASE_DIR / "logs"       # Updated name for consistency
    
    # Create directories if they don't exist
    for directory in [DATA_DIR, UPLOAD_DIR, RAG_DATA_DIR, KNOWLEDGE_BASE_DIR, LOG_DIR]:
        directory.mkdir(exist_ok=True)
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'aiton-rag-dev-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API Configuration
    API_KEY = os.getenv('API_KEY', 'aiton-rag-default-api-key')
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    API_VERSION = os.getenv('ACTIONS_API_VERSION', '1.0')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4o'
    OPENAI_MAX_TOKENS = 4000
    
    # File Processing Configuration
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB
    SUPPORTED_EXTENSIONS = os.getenv(
        'SUPPORTED_EXTENSIONS', 
        '.pdf,.docx,.txt,.html,.md,.csv'
    ).split(',')
    
        # Logging Configuration
    LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
    LOG_FILE = LOG_DIR / 'aiton-rag.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Custom GPT Actions Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
    
    # File Processing Configuration
    DELETE_AFTER_PROCESSING = os.getenv('DELETE_AFTER_PROCESSING', 'False').lower() == 'true'
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required but not set")
        
        if not cls.OPENAI_API_KEY.startswith('sk-'):
            raise ValueError("OPENAI_API_KEY appears to be invalid")
        
        return True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # More secure settings for production
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    @classmethod
    def validate_config(cls):
        super().validate_config()
        if cls.SECRET_KEY == 'aiton-rag-dev-key-change-in-production':
            raise ValueError("SECRET_KEY must be changed for production")

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    # Use temporary directories for testing
    UPLOADS_DIR = Config.BASE_DIR / "test_data" / "uploads"
    RAG_DIR = Config.BASE_DIR / "test_data" / "rag"
    KNOWLEDGE_BASE_DIR = Config.BASE_DIR / "test_data" / "knowledge_base"

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration based on environment"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config_class = config_map.get(config_name, DevelopmentConfig)
    config_class.validate_config()
    
    return config_class
