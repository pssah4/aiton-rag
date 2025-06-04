#!/usr/bin/env python3
"""
AITON-RAG Test Suite
Complete end-to-end testing for all system components
"""

import os
import sys
import json
import time
import tempfile
import unittest
import requests
from pathlib import Path
from unittest import mock
import threading
import subprocess

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import project modules
from config import Config
from services.file_processor import FileProcessor
from services.aggregator import Aggregator
from services.file_watcher import FileWatcher
from services.actions_api import ActionsAPI
import app


class TestConfig(unittest.TestCase):
    """Test configuration management"""
    
    def test_config_initialization(self):
        """Test basic configuration setup"""
        config = Config()
        self.assertTrue(hasattr(config, 'UPLOAD_DIR'))
        self.assertTrue(hasattr(config, 'RAG_DATA_DIR'))
        self.assertTrue(hasattr(config, 'OPENAI_API_KEY'))
    
    def test_directory_creation(self):
        """Test automatic directory creation"""
        config = Config()
        self.assertTrue(os.path.exists(config.UPLOAD_DIR))
        self.assertTrue(os.path.exists(config.RAG_DATA_DIR))
        self.assertTrue(os.path.exists(config.LOG_DIR))


class TestFileProcessor(unittest.TestCase):
    """Test file processing functionality"""
    
    def setUp(self):
        self.processor = FileProcessor()
        self.test_dir = tempfile.mkdtemp()
    
    def test_supported_formats(self):
        """Test supported file format detection"""
        supported = self.processor.get_supported_formats()
        expected_formats = ['.pdf', '.docx', '.txt', '.html', '.md']
        for fmt in expected_formats:
            self.assertIn(fmt, supported)
    
    def test_text_file_processing(self):
        """Test text file processing"""
        # Create test text file
        test_file = os.path.join(self.test_dir, 'test.txt')
        test_content = "Test content for processing"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Process file
        result = self.processor.process_file(test_file)
        
        self.assertIsNotNone(result)
        self.assertIn('content', result)
        self.assertIn('metadata', result)
        self.assertEqual(result['content'].strip(), test_content)
    
    def test_duplicate_detection(self):
        """Test duplicate file detection"""
        # Create identical test files
        test_file1 = os.path.join(self.test_dir, 'test1.txt')
        test_file2 = os.path.join(self.test_dir, 'test2.txt')
        test_content = "Identical content"
        
        for file_path in [test_file1, test_file2]:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
        
        # Process both files
        result1 = self.processor.process_file(test_file1)
        result2 = self.processor.process_file(test_file2)
        
        # Second file should be detected as duplicate
        self.assertIsNotNone(result1)
        self.assertIsNone(result2)  # Should be None for duplicate


class TestAggregator(unittest.TestCase):
    """Test knowledge aggregation and API optimization"""
    
    def setUp(self):
        self.aggregator = Aggregator()
    
    @mock.patch('openai.ChatCompletion.create')
    def test_content_categorization(self, mock_openai):
        """Test content categorization"""
        # Mock OpenAI response
        mock_openai.return_value = mock.Mock()
        mock_openai.return_value.choices = [
            mock.Mock(message=mock.Mock(content='{"category": "definitions", "summary": "Test summary", "key_points": ["Point 1", "Point 2"]}'))
        ]
        
        test_content = "This is a test document about definitions."
        result = self.aggregator.categorize_content(test_content)
        
        self.assertIsInstance(result, dict)
        self.assertIn('category', result)
    
    def test_knowledge_base_structure(self):
        """Test knowledge base data structure"""
        kb = self.aggregator.get_knowledge_base()
        
        expected_categories = ['processes', 'definitions', 'analysis', 'reference']
        for category in expected_categories:
            self.assertIn(category, kb)
            self.assertIsInstance(kb[category], list)


class TestActionsAPI(unittest.TestCase):
    """Test Custom GPT Actions API"""
    
    def setUp(self):
        self.api = ActionsAPI()
        self.app = self.api.app
        self.client = self.app.test_client()
    
    def test_health_endpoint(self):
        """Test API health check"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_knowledge_base_endpoint(self):
        """Test knowledge base retrieval"""
        response = self.client.get('/api/knowledge-base')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('categories', data)
        self.assertIn('total_documents', data)
    
    def test_search_endpoint(self):
        """Test search functionality"""
        response = self.client.post('/api/search', 
                                  json={'query': 'test', 'limit': 5})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)
        self.assertIn('query', data)
    
    def test_categories_endpoint(self):
        """Test categories listing"""
        response = self.client.get('/api/categories')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('categories', data)


class TestFlaskApp(unittest.TestCase):
    """Test Flask application endpoints"""
    
    def setUp(self):
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()
    
    def test_index_page(self):
        """Test main upload page"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AITON-RAG', response.data)
    
    def test_dashboard_page(self):
        """Test dashboard page"""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_api_docs_page(self):
        """Test API documentation page"""
        response = self.client.get('/api-docs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'API', response.data)


class TestIntegration(unittest.TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.processor = FileProcessor()
        self.aggregator = Aggregator()
    
    def test_full_workflow(self):
        """Test complete file upload to API workflow"""
        # 1. Create test file
        test_file = os.path.join(self.test_dir, 'integration_test.txt')
        test_content = """
        # Test Document
        
        This is a test document for integration testing.
        
        ## Process Description
        This document describes a test process for validation.
        
        ## Definitions
        - Test: A procedure intended to establish the quality of something
        - Integration: The process of combining components
        """
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 2. Process file
        processed = self.processor.process_file(test_file)
        self.assertIsNotNone(processed)
        
        # 3. Aggregate content (mock OpenAI for testing)
        with mock.patch('openai.ChatCompletion.create') as mock_openai:
            mock_openai.return_value = mock.Mock()
            mock_openai.return_value.choices = [
                mock.Mock(message=mock.Mock(content='{"category": "processes", "summary": "Test process", "key_points": ["Point 1"]}'))
            ]
            
            aggregated = self.aggregator.process_content(processed['content'], processed['metadata'])
            self.assertIsNotNone(aggregated)
        
        # 4. Verify knowledge base update
        kb = self.aggregator.get_knowledge_base()
        self.assertIsInstance(kb, dict)


def run_server_test():
    """Test server startup and basic functionality"""
    print("🧪 Testing server startup...")
    
    try:
        # Start server in background
        server_process = subprocess.Popen([
            sys.executable, 'app.py'
        ], cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        # Test basic endpoints
        base_url = "http://localhost:5000"
        
        # Test health check
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            print("✅ Health check passed")
        except requests.exceptions.ConnectionError:
            print("❌ Server connection failed")
            return False
        
        # Test main page
        try:
            response = requests.get(base_url, timeout=5)
            assert response.status_code == 200, f"Main page failed: {response.status_code}"
            print("✅ Main page accessible")
        except Exception as e:
            print(f"❌ Main page test failed: {e}")
        
        # Test API endpoints
        try:
            response = requests.get(f"{base_url}/api/knowledge-base", timeout=5)
            assert response.status_code == 200, f"API test failed: {response.status_code}"
            print("✅ API endpoints working")
        except Exception as e:
            print(f"❌ API test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False
    
    finally:
        # Clean up server process
        if 'server_process' in locals():
            server_process.terminate()
            server_process.wait()


def main():
    """Run all tests"""
    print("🚀 AITON-RAG Test Suite")
    print("=" * 50)
    
    # Unit tests
    print("\n📋 Running unit tests...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestConfig,
        TestFileProcessor,
        TestAggregator,
        TestActionsAPI,
        TestFlaskApp,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run unit tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Server integration test
    print("\n🌐 Running server integration test...")
    server_success = run_server_test()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Unit tests: {'✅ PASSED' if result.wasSuccessful() else '❌ FAILED'}")
    print(f"Server test: {'✅ PASSED' if server_success else '❌ FAILED'}")
    
    if result.wasSuccessful() and server_success:
        print("\n🎉 All tests passed! System is ready for deployment.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
