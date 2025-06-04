"""
AITON-RAG Main Application

Flask application that integrates file processing, knowledge base management,
and Custom GPT Actions API with a web interface for file uploads.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pathlib import Path
import threading
from datetime import datetime

from config import Config
from services.file_processor import FileProcessor
from services.aggregator import Aggregator
from services.file_watcher import FileWatcher
from services.actions_api import ActionsAPI, OPENAPI_SPEC

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_DIR / 'aiton-rag.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Application factory function."""
    app = Flask(__name__)
    
    # Configuration
    app.config.update(
        SECRET_KEY=Config.SECRET_KEY,
        MAX_CONTENT_LENGTH=Config.MAX_FILE_SIZE,
        UPLOAD_FOLDER=str(Config.UPLOAD_DIR)
    )
    
    # Initialize services
    file_processor = FileProcessor()
    aggregator = Aggregator()
    file_watcher = FileWatcher()
    actions_api = ActionsAPI(app)
    
    # Ensure directories exist
    Config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    Config.RAG_DATA_DIR.mkdir(parents=True, exist_ok=True)
    Config.KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Start file watcher in background
    def start_file_watcher():
        try:
            file_watcher.process_existing_files()
            file_watcher.start()
            logger.info("File watcher started successfully")
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
    
    # Start file watcher in a separate thread
    watcher_thread = threading.Thread(target=start_file_watcher, daemon=True)
    watcher_thread.start()
    
    # Routes
    @app.route('/')
    def index():
        """Main upload interface."""
        try:
            # Get some stats for the dashboard
            total_files = len(list(Config.RAG_DATA_DIR.glob('*.md')))
            knowledge_base = aggregator.get_structured_knowledge()
            total_categories = len(knowledge_base) if knowledge_base else 0
            
            stats = {
                'total_files': total_files,
                'total_categories': total_categories,
                'watcher_running': file_watcher.is_running(),
                'openai_configured': bool(Config.OPENAI_API_KEY)
            }
            
            return render_template('index.html', stats=stats)
            
        except Exception as e:
            logger.error(f"Error loading index page: {e}")
            return render_template('index.html', stats={}, error=str(e))
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        """Handle file upload via web interface."""
        try:
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(url_for('index'))
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('index'))
            
            if file:
                # Secure the filename
                filename = secure_filename(file.filename)
                if not filename:
                    flash('Invalid filename', 'error')
                    return redirect(url_for('index'))
                
                # Check file extension
                allowed_extensions = {'.pdf', '.docx', '.txt', '.html', '.md', '.htm'}
                file_ext = Path(filename).suffix.lower()
                
                if file_ext not in allowed_extensions:
                    flash(f'Unsupported file type: {file_ext}', 'error')
                    return redirect(url_for('index'))
                
                # Save file to upload directory
                file_path = Config.UPLOAD_DIR / filename
                
                # Handle duplicate filenames
                counter = 1
                original_path = file_path
                while file_path.exists():
                    stem = original_path.stem
                    suffix = original_path.suffix
                    file_path = Config.UPLOAD_DIR / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                file.save(str(file_path))
                
                flash(f'File uploaded successfully: {file_path.name}', 'success')
                logger.info(f"File uploaded via web interface: {file_path}")
                
                return redirect(url_for('index'))
                
        except Exception as e:
            logger.error(f"Upload error: {e}")
            flash(f'Upload failed: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    @app.route('/api/upload', methods=['POST'])
    def api_upload():
        """API endpoint for file upload."""
        try:
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No file provided'
                }), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            filename = secure_filename(file.filename)
            if not filename:
                return jsonify({
                    'success': False,
                    'error': 'Invalid filename'
                }), 400
            
            # Check file extension
            allowed_extensions = {'.pdf', '.docx', '.txt', '.html', '.md', '.htm'}
            file_ext = Path(filename).suffix.lower()
            
            if file_ext not in allowed_extensions:
                return jsonify({
                    'success': False,
                    'error': f'Unsupported file type: {file_ext}',
                    'supported_types': list(allowed_extensions)
                }), 400
            
            # Save file
            file_path = Config.UPLOAD_DIR / filename
            
            # Handle duplicates
            counter = 1
            original_path = file_path
            while file_path.exists():
                stem = original_path.stem
                suffix = original_path.suffix
                file_path = Config.UPLOAD_DIR / f"{stem}_{counter}{suffix}"
                counter += 1
            
            file.save(str(file_path))
            
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'filename': file_path.name,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"API upload error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard with system status and file management."""
        try:
            # Get processed files
            rag_files = list(Config.RAG_DATA_DIR.glob('*.md'))
            
            files_info = []
            for file_path in rag_files[:20]:  # Limit to 20 most recent
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if content.startswith('---'):
                        frontmatter_end = content.find('---', 3)
                        if frontmatter_end > 0:
                            frontmatter = content[3:frontmatter_end].strip()
                            metadata = {}
                            for line in frontmatter.split('\n'):
                                if ':' in line:
                                    key, value = line.split(':', 1)
                                    metadata[key.strip()] = value.strip()
                            
                            files_info.append({
                                'filename': file_path.name,
                                'original_file': metadata.get('original_file', 'unknown'),
                                'processed_date': metadata.get('processed_date', 'unknown'),
                                'file_type': metadata.get('file_type', 'unknown')
                            })
                except Exception as e:
                    logger.warning(f"Could not read metadata from {file_path}: {e}")
            
            # Get knowledge base stats
            knowledge_base = aggregator.get_structured_knowledge()
            
            stats = {
                'total_files': len(rag_files),
                'total_categories': len(knowledge_base) if knowledge_base else 0,
                'knowledge_base': knowledge_base,
                'watcher_running': file_watcher.is_running(),
                'openai_configured': bool(Config.OPENAI_API_KEY),
                'recent_files': files_info
            }
            
            return render_template('dashboard.html', stats=stats)
            
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            return render_template('dashboard.html', stats={}, error=str(e))
    
    @app.route('/api-docs')
    def api_docs():
        """API documentation for Custom GPT Actions."""
        return render_template('api_docs.html', spec=OPENAPI_SPEC)
    
    @app.route('/openapi.json')
    def openapi_spec():
        """OpenAPI specification in JSON format."""
        return jsonify(OPENAPI_SPEC)
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        try:
            # Basic health checks
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'components': {
                    'file_watcher': file_watcher.is_running(),
                    'openai_configured': bool(Config.OPENAI_API_KEY),
                    'upload_dir': Config.UPLOAD_DIR.exists(),
                    'rag_dir': Config.RAG_DATA_DIR.exists(),
                    'knowledge_base_dir': Config.KNOWLEDGE_BASE_DIR.exists()
                }
            }
            
            # Check if any critical components are down
            if not all(health_status['components'].values()):
                health_status['status'] = 'degraded'
            
            return jsonify(health_status)
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Serve static files."""
        return send_from_directory('static', filename)
    
    # Error handlers
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            'success': False,
            'error': f'File too large. Maximum size: {Config.MAX_FILE_SIZE / 1024 / 1024:.1f}MB'
        }), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    # Cleanup function
    def cleanup():
        """Cleanup function called on app shutdown."""
        try:
            file_watcher.stop()
            logger.info("Application cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    # Register cleanup
    import atexit
    atexit.register(cleanup)
    
    return app

# Create the Flask app instance
app = create_app()

def main():
    """Main entry point."""
    logger.info("Starting AITON-RAG application")
    logger.info(f"Upload directory: {Config.UPLOAD_DIR}")
    logger.info(f"RAG data directory: {Config.RAG_DATA_DIR}")
    logger.info(f"OpenAI configured: {bool(Config.OPENAI_API_KEY)}")
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()
