import sys
import os
import webbrowser
from threading import Timer

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from config import HOST, PORT, DEBUG

def open_browser():
    """Open browser after server starts"""
    webbrowser.open_new(f"http://127.0.0.1:{PORT}")

def print_banner():
    """Print beautiful banner"""
    banner = """
 +═════════════════════════════════════════════════════════+
 ║    _  _ ___ _   _      _    LIBRARY AI AGENT SYSTEM     ║
 ║   | || | _ \ | | |___ (_)   Trường Đại học Hải Phòng    ║
 ║   | __ |  _/ |_| |   \| |   ────────────────────────    ║
 ║   |_||_|_|  \___/|_||_|_|     ĐỀ TÀI NGHIÊN CỨU         ║
 ║                             KHOA HỌC NĂM 2025-2026      ║
 +═════════════════════════════════════════════════════════+
 ║  🌐 URL:   http://127.0.0.1:{}                         ║
 ║  📊 Admin: http://127.0.0.1:{}/admin                   ║
 ║  💬 Chat:  http://127.0.0.1:{}                         ║
 +─────────────────────────────────────────────────────────+
 ║  Hybrid Information Retrieval | Large Language Model    ║
 +═════════════════════════════════════════════════════════+
 ║  🚀 Running... Press Ctrl+C to stop server              ║
 +═════════════════════════════════════════════════════════+
""".format(PORT, PORT, PORT)
    
    print(banner)

def check_dependencies():
    """Check if required directories and files exist"""
    from config import DATA_DIR, METADATA_PATH
    
    # Check data directory
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"✅ Created data directory: {DATA_DIR}")
    
    # Check metadata file
    if not os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, 'w', encoding='utf-8', newline='') as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(['title', 'author', 'year', 'category', 'class_code', 'description'])
        print(f"✅ Created metadata file: {METADATA_PATH}")
    
    # Check templates directory
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print(f"✅ Created templates directory: {templates_dir}")
    
    # Check static directories
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    css_dir = os.path.join(static_dir, 'css')
    js_dir = os.path.join(static_dir, 'js')
    
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)
    
    print(f"✅ Static directories ready")

def main():
    """Main function"""
    try:
        # Print banner
        print_banner()
        
        # Check dependencies
        check_dependencies()
        
        # Open browser after 1.5 seconds
        Timer(1.5, open_browser).start()
        
        # Run app
        print("🚀 Starting server...\n")
        app.run(
            host=HOST,
            port=PORT,
            debug=DEBUG,
            use_reloader=False  # Disable reloader to prevent double browser open
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()