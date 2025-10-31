# --- app/__init__.py ---
from flask import Flask, render_template
from config import Config

def create_app(config_class=Config):
    """Factory function to create the Flask app instance."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions here if needed (e.g., db, login_manager)

    # Import and register blueprints
    from app.blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.blueprints.data_entry import bp as data_entry_bp
    app.register_blueprint(data_entry_bp, url_prefix='/data_entry')

    from app.blueprints.clinician import bp as clinician_bp
    app.register_blueprint(clinician_bp, url_prefix='/clinician')

    from app.blueprints.patient import bp as patient_bp
    app.register_blueprint(patient_bp, url_prefix='/patient')

    # A simple route for the home page
    @app.route('/')
    def index():
        return render_template('index.html', title='EHR Demonstrator Home')

    # Add other top-level routes or error handlers if needed

    return app
