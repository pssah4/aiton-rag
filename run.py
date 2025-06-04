#!/usr/bin/env python3
"""
AITON-RAG Application Launcher
Starts the complete AITON-RAG system
"""

import os
import sys
import threading
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def start_web_server():
    """Start Flask web server"""
    from app import app
    app.run(host='0.0.0.0', port=5000, debug=False)

def start_desktop_ui():
    """Start desktop UI"""
    from ui.desktop_ui import DesktopUI
    ui = DesktopUI()
    ui.run()

def main():
    """Main launcher with options"""
    print("🚀 AITON-RAG System Launcher")
    print("=" * 40)
    print("1. Web Server Only")
    print("2. Desktop UI Only") 
    print("3. Both (Recommended)")
    print("4. Test Mode")
    
    choice = input("\nSelect option (1-4): ").strip()
    
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
