"""
Actions API Service for AITON-RAG

REST API endpoints specifically designed for ChatGPT Custom GPT Actions integration.
Provides optimized responses for AI consumption with proper formatting and metadata.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from .aggregator import Aggregator
from .file_processor import FileProcessor
from config import Config

class ActionsAPI:
    """API service optimized for ChatGPT Custom GPT Actions."""
    
    def __init__(self, app: Flask = None):
        self.logger = logging.getLogger(__name__)
        self.aggregator = Aggregator()
        self.file_processor = FileProcessor()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the API with a Flask app."""
        self.app = app
        
        # Enable CORS for Custom GPT Actions
        CORS(app, resources={
            r"/api/*": {
                "origins": ["https://chat.openai.com", "https://chatgpt.com"],
                "methods": ["GET", "POST"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
        
        # Register API routes
        self._register_routes()
        
        # Error handlers
        self._register_error_handlers()
    
    def _register_routes(self):
        """Register all API endpoints."""
        
        @self.app.route('/api/v1/search', methods=['GET'])
        def search_knowledge():
            """Search the knowledge base with Custom GPT optimization."""
            try:
                query = request.args.get('query', '').strip()
                category = request.args.get('category', '')
                limit = min(int(request.args.get('limit', 10)), 50)  # Max 50 results
                
                if not query:
                    return jsonify({
                        "success": False,
                        "error": "Query parameter is required",
                        "usage_guidance": "Use ?query=your_search_terms to search the knowledge base"
                    }), 400
                
                # Perform search
                results = self.aggregator.search_content(
                    query=query,
                    category=category,
                    limit=limit
                )
                
                # Format response for Custom GPT Actions
                response = {
                    "success": True,
                    "query": query,
                    "category": category or "all",
                    "total_results": len(results),
                    "results": results,
                    "timestamp": datetime.now().isoformat(),
                    "actions_metadata": {
                        "response_type": "search_results",
                        "content_optimized": True,
                        "categories_available": ["processes", "definitions", "analysis", "reference"],
                        "usage_tip": "Results are pre-structured for AI consumption"
                    }
                }
                
                self.logger.info(f"Search API called: query='{query}', results={len(results)}")
                return jsonify(response)
                
            except Exception as e:
                self.logger.error(f"Search API error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/v1/knowledge-base', methods=['GET'])
        def get_knowledge_base():
            """Get the complete structured knowledge base."""
            try:
                # Get structured knowledge base
                knowledge_base = self.aggregator.get_structured_knowledge()
                
                if not knowledge_base:
                    return jsonify({
                        "success": True,
                        "message": "Knowledge base is empty",
                        "knowledge_base": {},
                        "actions_metadata": {
                            "response_type": "empty_knowledge_base",
                            "suggestion": "Upload files to populate the knowledge base"
                        }
                    })
                
                # Add metadata for Custom GPT Actions
                response = {
                    "success": True,
                    "knowledge_base": knowledge_base,
                    "timestamp": datetime.now().isoformat(),
                    "actions_metadata": {
                        "response_type": "complete_knowledge_base",
                        "content_optimized": True,
                        "total_categories": len(knowledge_base),
                        "usage_tip": "Content is pre-structured and ready for analysis"
                    }
                }
                
                self.logger.info("Knowledge base API called")
                return jsonify(response)
                
            except Exception as e:
                self.logger.error(f"Knowledge base API error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/v1/categories', methods=['GET'])
        def get_categories():
            """Get available content categories."""
            try:
                knowledge_base = self.aggregator.get_structured_knowledge()
                categories = list(knowledge_base.keys()) if knowledge_base else []
                
                response = {
                    "success": True,
                    "categories": categories,
                    "category_descriptions": {
                        "processes": "Step-by-step procedures, workflows, and methodologies",
                        "definitions": "Key terms, concepts, and their explanations",
                        "analysis": "Analytical insights, assessments, and evaluations",
                        "reference": "Reference materials, data, and factual information"
                    },
                    "timestamp": datetime.now().isoformat(),
                    "actions_metadata": {
                        "response_type": "categories_list",
                        "usage_tip": "Use these categories to filter search results"
                    }
                }
                
                return jsonify(response)
                
            except Exception as e:
                self.logger.error(f"Categories API error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/v1/files', methods=['GET'])
        def get_processed_files():
            """Get list of processed files with metadata."""
            try:
                rag_files = list(Config.RAG_DATA_DIR.glob('*.md'))
                
                files_info = []
                for file_path in rag_files:
                    try:
                        # Read file metadata from frontmatter
                        content = file_path.read_text(encoding='utf-8')
                        if content.startswith('---'):
                            frontmatter_end = content.find('---', 3)
                            if frontmatter_end > 0:
                                frontmatter = content[3:frontmatter_end].strip()
                                # Parse basic metadata
                                metadata = {}
                                for line in frontmatter.split('\n'):
                                    if ':' in line:
                                        key, value = line.split(':', 1)
                                        metadata[key.strip()] = value.strip()
                                
                                files_info.append({
                                    "filename": file_path.name,
                                    "processed_date": metadata.get('processed_date', 'unknown'),
                                    "original_file": metadata.get('original_file', 'unknown'),
                                    "file_type": metadata.get('file_type', 'unknown'),
                                    "file_hash": metadata.get('file_hash', 'unknown')
                                })
                    except Exception as e:
                        self.logger.warning(f"Could not read metadata from {file_path}: {e}")
                
                response = {
                    "success": True,
                    "total_files": len(files_info),
                    "files": files_info,
                    "timestamp": datetime.now().isoformat(),
                    "actions_metadata": {
                        "response_type": "files_list",
                        "usage_tip": "Shows all processed files in the knowledge base"
                    }
                }
                
                return jsonify(response)
                
            except Exception as e:
                self.logger.error(f"Files API error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/v1/health', methods=['GET'])
        def health_check():
            """Health check endpoint for monitoring."""
            try:
                # Check if services are working
                knowledge_base = self.aggregator.get_structured_knowledge()
                total_files = len(list(Config.RAG_DATA_DIR.glob('*.md')))
                
                response = {
                    "success": True,
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "stats": {
                        "total_processed_files": total_files,
                        "knowledge_base_categories": len(knowledge_base) if knowledge_base else 0,
                        "openai_configured": bool(Config.OPENAI_API_KEY)
                    },
                    "actions_metadata": {
                        "response_type": "health_status",
                        "api_ready": True
                    }
                }
                
                return jsonify(response)
                
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                return jsonify({
                    "success": False,
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/v1/update-knowledge-base', methods=['POST'])
        def update_knowledge_base():
            """Manually trigger knowledge base update."""
            try:
                # Update the knowledge base
                self.aggregator.update_knowledge_base()
                
                # Get updated stats
                knowledge_base = self.aggregator.get_structured_knowledge()
                total_files = len(list(Config.RAG_DATA_DIR.glob('*.md')))
                
                response = {
                    "success": True,
                    "message": "Knowledge base updated successfully",
                    "stats": {
                        "total_processed_files": total_files,
                        "knowledge_base_categories": len(knowledge_base) if knowledge_base else 0
                    },
                    "timestamp": datetime.now().isoformat(),
                    "actions_metadata": {
                        "response_type": "update_confirmation",
                        "operation": "knowledge_base_refresh"
                    }
                }
                
                self.logger.info("Knowledge base updated via API")
                return jsonify(response)
                
            except Exception as e:
                self.logger.error(f"Update knowledge base API error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
    
    def _register_error_handlers(self):
        """Register error handlers for the API."""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                "success": False,
                "error": "Endpoint not found",
                "available_endpoints": [
                    "/api/v1/search",
                    "/api/v1/knowledge-base",
                    "/api/v1/categories",
                    "/api/v1/files",
                    "/api/v1/health",
                    "/api/v1/update-knowledge-base"
                ],
                "timestamp": datetime.now().isoformat()
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                "success": False,
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            }), 500
        
        @self.app.errorhandler(405)
        def method_not_allowed(error):
            return jsonify({
                "success": False,
                "error": "Method not allowed",
                "timestamp": datetime.now().isoformat()
            }), 405

def create_actions_api(app: Flask = None) -> ActionsAPI:
    """Factory function to create an ActionsAPI instance."""
    return ActionsAPI(app)

# OpenAPI specification for Custom GPT Actions
OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "AITON-RAG Actions API",
        "description": "API for accessing structured knowledge base through ChatGPT Custom GPT Actions",
        "version": "1.0.0"
    },
    "servers": [
        {
            "url": Config.API_BASE_URL,
            "description": "AITON-RAG API Server"
        }
    ],
    "paths": {
        "/api/v1/search": {
            "get": {
                "summary": "Search knowledge base",
                "description": "Search the structured knowledge base with optional category filtering",
                "parameters": [
                    {
                        "name": "query",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Search query terms"
                    },
                    {
                        "name": "category",
                        "in": "query",
                        "required": False,
                        "schema": {
                            "type": "string",
                            "enum": ["processes", "definitions", "analysis", "reference"]
                        },
                        "description": "Filter by content category"
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "minimum": 1, "maximum": 50},
                        "description": "Maximum number of results (default: 10)"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Search results",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "results": {"type": "array"},
                                        "total_results": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/knowledge-base": {
            "get": {
                "summary": "Get complete knowledge base",
                "description": "Retrieve the entire structured knowledge base",
                "responses": {
                    "200": {
                        "description": "Complete knowledge base",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "knowledge_base": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/categories": {
            "get": {
                "summary": "Get available categories",
                "description": "List all available content categories",
                "responses": {
                    "200": {
                        "description": "Available categories"
                    }
                }
            }
        },
        "/api/v1/health": {
            "get": {
                "summary": "Health check",
                "description": "Check API and system health",
                "responses": {
                    "200": {
                        "description": "System status"
                    }
                }
            }
        }
    }
}
