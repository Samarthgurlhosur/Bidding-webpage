"""
Wrapper script to run the Flask app with Python 3.13 compatibility fixes.
"""
import sys

# Apply Python 3.13 SQLAlchemy fix BEFORE any other imports
if sys.version_info >= (3, 13):
    import typing
    
    # Define TypingOnly if it doesn't exist
    if not hasattr(typing, 'TypingOnly'):
        class TypingOnly:
            pass
        
        typing.TypingOnly = TypingOnly

# Now import and run the app
from app import app

if __name__ == '__main__':
    print("🏆 Starting Bidding System Server...")
    print("📍 Access the application at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server.\n")
    app.run(debug=True)
