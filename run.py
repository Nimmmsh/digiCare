"""
Application entry point.

This file is the main entry point for running the Flask application.
It can be run directly with Python or used by the container.

Usage:
    python run.py
    
Or with Flask CLI:
    flask run
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Debug mode is on for development.
    # In production, use a proper WSGI server like gunicorn.
    # Host 0.0.0.0 allows connections from outside the container.
    app.run(host='0.0.0.0', port=5000, debug=True)

