"""
Flask application factory.

Why a factory pattern?
- Allows creating app instances with different configs (dev/test/prod)
- Keeps imports clean and avoids circular dependencies
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy outside app context so models can import it
db = SQLAlchemy()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration from environment variables
    # These are set in podman-compose.yml or .env file
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
    
    # MySQL connection string format: mysql+pymysql://user:password@host:port/database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://patient_user:patient_pass@localhost:3306/patient_db'
    )
    
    # Disable modification tracking (we don't need it, saves memory)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database with app
    db.init_app(app)
    
    # Register routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

