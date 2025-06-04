#!/usr/bin/env python3
"""
AITON-RAG Environment Setup & Validation Script
Prepares the environment and validates all system components
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import tempfile
import shutil


class EnvironmentSetup:
    """Environment setup and validation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.success_count = 0
        self.total_checks = 0
    
    def log(self, message, status="info"):
        """Log messages with status"""
        icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}
        print(f"{icons.get(status, 'ℹ️')} {message}")
    
    def run_command(self, command, description, check_return=True):
        """Run shell command with logging"""
        self.log(f"Running: {description}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                cwd=self.project_root
            )
            
            if check_return and result.returncode != 0:
                self.log(f"Command failed: {result.stderr}", "error")
                return False
            
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            
            return True
            
        except Exception as e:
            self.log(f"Command error: {e}", "error")
            return False
    
    def check_python_version(self):
        """Check Python version compatibility"""
        self.total_checks += 1
        self.log("Checking Python version...")
        
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.log(f"Python {version.major}.{version.minor}.{version.micro} - Compatible", "success")
            self.success_count += 1
            return True
        else:
            self.log(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+", "error")
            return False
    
    def install_dependencies(self):
        """Install Python dependencies"""
        self.total_checks += 1
        self.log("Installing Python dependencies...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.log("requirements.txt not found", "error")
            return False
        
        success = self.run_command(
            "pip install -r requirements.txt",
            "Installing dependencies from requirements.txt"
        )
        
        if success:
            self.success_count += 1
            self.log("Dependencies installed successfully", "success")
        
        return success
    
    def create_directories(self):
        """Create necessary directories"""
        self.total_checks += 1
        self.log("Creating project directories...")
        
        directories = [
            "uploads",
            "rag_data",
            "logs",
            "temp"
        ]
        
        try:
            for directory in directories:
                dir_path = self.project_root / directory
                dir_path.mkdir(exist_ok=True)
                self.log(f"Directory created/verified: {directory}")
            
            self.success_count += 1
            self.log("All directories created successfully", "success")
            return True
            
        except Exception as e:
            self.log(f"Directory creation failed: {e}", "error")
            return False
    
    def create_env_file(self):
        """Create .env file template"""
        self.total_checks += 1
        self.log("Setting up environment configuration...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        # Create .env.example with template
        env_template = """# AITON-RAG Environment Configuration
# Copy this file to .env and fill in your values

# OpenAI Configuration (Required for aggregation)
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
FLASK_SECRET_KEY=your_secret_key_here
API_BASE_URL=http://localhost:5000

# File Processing
MAX_FILE_SIZE_MB=100
DELETE_AFTER_PROCESSING=false

# Directories (relative to project root)
UPLOAD_DIR=uploads
RAG_DATA_DIR=rag_data
LOG_DIR=logs

# Development/Production
FLASK_ENV=development
DEBUG=true
"""
        
        try:
            # Create example file
            with open(env_example, 'w') as f:
                f.write(env_template)
            
            # Create .env if it doesn't exist
            if not env_file.exists():
                with open(env_file, 'w') as f:
                    f.write(env_template)
                self.log(".env file created - Please configure your API keys", "warning")
            else:
                self.log(".env file already exists", "info")
            
            self.success_count += 1
            self.log("Environment configuration setup complete", "success")
            return True
            
        except Exception as e:
            self.log(f"Environment file creation failed: {e}", "error")
            return False
    
    def validate_imports(self):
        """Validate that all imports work"""
        self.total_checks += 1
        self.log("Validating project imports...")
        
        test_imports = [
            "import flask",
            "import openai", 
            "import python_docx",
            "import PyPDF2",
            "import markdown",
            "import tkinter",
            "from pathlib import Path",
            "import asyncio",
            "import aiofiles",
            "from werkzeug.utils import secure_filename"
        ]
        
        failed_imports = []
        
        for import_statement in test_imports:
            try:
                exec(import_statement)
            except ImportError as e:
                failed_imports.append(f"{import_statement}: {e}")
        
        if failed_imports:
            self.log("Import validation failed:", "error")
            for failure in failed_imports:
                self.log(f"  - {failure}", "error")
            return False
        else:
            self.success_count += 1
            self.log("All imports validated successfully", "success")
            return True
    
    def validate_config(self):
        """Validate configuration loading"""
        self.total_checks += 1
        self.log("Validating configuration...")
        
        try:
            sys.path.insert(0, str(self.project_root))
            from config import Config
            
            config = Config()
            
            # Check essential attributes
            required_attrs = [
                'UPLOAD_DIR', 'RAG_DATA_DIR', 'LOG_DIR',
                'SUPPORTED_FORMATS', 'MAX_FILE_SIZE'
            ]
            
            for attr in required_attrs:
                if not hasattr(config, attr):
                    self.log(f"Missing config attribute: {attr}", "error")
                    return False
            
            self.success_count += 1
            self.log("Configuration validation successful", "success")
            return True
            
        except Exception as e:
            self.log(f"Configuration validation failed: {e}", "error")
            return False
    
    def test_file_processing(self):
        """Test basic file processing functionality"""
        self.total_checks += 1
        self.log("Testing file processing...")
        
        try:
            sys.path.insert(0, str(self.project_root))
            from services.file_processor import FileProcessor
            
            processor = FileProcessor()
            
            # Test with temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("Test content for processing validation")
                temp_file = f.name
            
            try:
                result = processor.process_file(temp_file)
                if result and 'content' in result and 'metadata' in result:
                    self.success_count += 1
                    self.log("File processing test successful", "success")
                    return True
                else:
                    self.log("File processing returned invalid result", "error")
                    return False
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            self.log(f"File processing test failed: {e}", "error")
            return False
    
    def create_run_script(self):
        """Create convenient run script"""
        self.total_checks += 1
        self.log("Creating run scripts...")
        
        # Main run script
        run_script = """#!/usr/bin/env python3
\"\"\"
AITON-RAG Application Launcher
Starts the complete AITON-RAG system
\"\"\"

import os
import sys
import threading
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def start_web_server():
    \"\"\"Start Flask web server\"\"\"
    from app import app
    app.run(host='0.0.0.0', port=5000, debug=False)

def start_desktop_ui():
    \"\"\"Start desktop UI\"\"\"
    from ui.desktop_ui import DesktopUI
    ui = DesktopUI()
    ui.run()

def main():
    \"\"\"Main launcher with options\"\"\"
    print("🚀 AITON-RAG System Launcher")
    print("=" * 40)
    print("1. Web Server Only")
    print("2. Desktop UI Only") 
    print("3. Both (Recommended)")
    print("4. Test Mode")
    
    choice = input("\\nSelect option (1-4): ").strip()
    
    if choice == "1":
        print("🌐 Starting web server...")
        start_web_server()
    elif choice == "2":
        print("🖥️  Starting desktop UI...")
        start_desktop_ui()
    elif choice == "3":
        print("🔄 Starting both web server and desktop UI...")
        # Start web server in background thread
        server_thread = threading.Thread(target=start_web_server, daemon=True)
        server_thread.start()
        time.sleep(2)  # Give server time to start
        print("🌐 Web server started at http://localhost:5000")
        print("🖥️  Starting desktop UI...")
        start_desktop_ui()
    elif choice == "4":
        print("🧪 Running tests...")
        os.system("python test_aiton_rag.py")
    else:
        print("Invalid option selected")

if __name__ == '__main__':
    main()
"""
        
        try:
            with open(self.project_root / "run.py", 'w') as f:
                f.write(run_script)
            
            # Make executable on Unix systems
            if os.name != 'nt':
                os.chmod(self.project_root / "run.py", 0o755)
            
            self.success_count += 1
            self.log("Run script created successfully", "success")
            return True
            
        except Exception as e:
            self.log(f"Run script creation failed: {e}", "error")
            return False
    
    def generate_summary_report(self):
        """Generate setup summary report"""
        self.log("\n" + "="*60)
        self.log("AITON-RAG Environment Setup Summary")
        self.log("="*60)
        
        success_rate = (self.success_count / self.total_checks) * 100 if self.total_checks > 0 else 0
        
        self.log(f"Completed: {self.success_count}/{self.total_checks} checks ({success_rate:.1f}%)")
        
        if self.success_count == self.total_checks:
            self.log("🎉 Environment setup completed successfully!", "success")
            self.log("\nNext steps:")
            self.log("1. Configure your OpenAI API key in .env file")
            self.log("2. Run: python run.py")
            self.log("3. Access web interface at http://localhost:5000")
            return True
        else:
            self.log("⚠️  Some setup steps failed. Please review the output above.", "warning")
            return False
    
    def run_full_setup(self):
        """Run complete environment setup"""
        self.log("🛠️  AITON-RAG Environment Setup")
        self.log("="*50)
        
        setup_steps = [
            self.check_python_version,
            self.install_dependencies,
            self.create_directories,
            self.create_env_file,
            self.validate_imports,
            self.validate_config,
            self.test_file_processing,
            self.create_run_script
        ]
        
        for step in setup_steps:
            if not step():
                self.log(f"Setup step failed: {step.__name__}", "error")
                # Continue with other steps even if one fails
        
        return self.generate_summary_report()


def main():
    """Main setup function"""
    setup = EnvironmentSetup()
    return setup.run_full_setup()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
