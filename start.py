#!/usr/bin/env python3
"""
Easy launch script for Personal Website Creator
"""

import subprocess
import sys
import webbrowser
import time
import os

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        print("✅ Flask is installed")
        return True
    except ImportError:
        print("❌ Flask is not installed")
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")
        return True

def start_application():
    """Start the Flask application"""
    print("🚀 Starting Personal Website Creator...")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        return
    
    print("\n🌐 Launching web server on http://localhost:8080 ...")
    
    try:
        # Start Flask app in background
        process = subprocess.Popen([sys.executable, 'app.py'])
        
        # Give server time to boot
        time.sleep(3)
        print("🌐 Opening browser...")
        webbrowser.open('http://localhost:8080')
        
        # Wait for the Flask process to exit
        process.wait()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Personal Website Creator...")
        process.terminate()
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("Try running manually with: python app.py")

if __name__ == "__main__":
    print("🎨 Personal Website Creator")
    print("Transform your resume into a beautiful website!")
    print("=" * 50)
    
    start_application() 