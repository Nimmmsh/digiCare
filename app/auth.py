"""
Simple authentication helpers.

Why not use Flask-Login or other auth libraries?
- This app is intentionally minimal
- Session-based auth with Flask's built-in session is sufficient
- Fewer dependencies = easier to understand and maintain
"""
from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """
    Decorator to require login for a route.
    Redirects to login page if user is not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    """
    Decorator to require specific role(s) for a route.
    Must be used AFTER @login_required.
    
    Usage:
        @login_required
        @role_required('admin', 'doctor')
        def some_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('user_role')
            if user_role not in allowed_roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user_id():
    """Get the currently logged-in user's ID from session."""
    return session.get('user_id')


def get_current_user_role():
    """Get the currently logged-in user's role from session."""
    return session.get('user_role')

