# --- run.py ---
from app import create_app

# Create the Flask app instance using the factory function
app = create_app()

if __name__ == '__main__':
    # Run the Flask development server
    # debug=True enables auto-reloading and detailed error pages (uses FLASK_ENV from .env)
    # host='0.0.0.0' makes the server accessible on your network (use '127.0.0.1' for local only)
    # port=5000 is the default Flask port
    app.run(host='0.0.0.0', port=5000)
    # Note: For production, use a proper WSGI server like Gunicorn or Waitress.
