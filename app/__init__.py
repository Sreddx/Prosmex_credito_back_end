from flask import Flask
from .database import db, init_engine, init_session, init_db
from .models import *
from .extensions import bcrypt, jwt
from flask_cors import CORS
from config import localConfig
from flask_migrate import Migrate, init as init_migration, migrate as run_migration, upgrade as apply_upgrade
import os
import subprocess

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(localConfig)
    
    # Initialize the database
    engine = init_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    session = init_session(engine)

    db.init_app(app)
    init_db(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Automatically handle migrations
    with app.app_context():
        # Check if migration folder exists, if not, initialize it
        if not os.path.exists(os.path.join(app.root_path, 'migrations')):
            try:
                init_migration()
                print("Initialized migration folder.")
            except Exception as e:
                print(f"Failed to initialize migration folder: {e}")

        # Run migrations and upgrade
        try:
            run_migration(message="Automated migration")
            print("Migration script generated.")
        except Exception as e:
            print(f"No new changes to migrate: {e}")
        
        try:
            apply_upgrade()
            print("Database upgraded successfully.")
        except Exception as e:
            print(f"Failed to upgrade the database: {e}")

    # Load initial catalog data
    with app.app_context():
        from .populate_data import populate_data
        try:
            populate_data()
        except Exception as e:
            raise ValueError(f"Error loading initial data: {str(e)}")

    CORS(app, supports_credentials=True, origins=["http://localhost:5050"], allow_headers=["Content-Type", "Authorization", "X-CSRF-TOKEN"], expose_headers=["Content-Type", "Authorization", "X-CSRF-TOKEN"])
    
    # Initialize objects of the extensions
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Import and register blueprints
    from .blueprints import auth_blueprint, user_blueprint, role_blueprint, cliente_blueprint, prestamo_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(role_blueprint)
    app.register_blueprint(cliente_blueprint)
    app.register_blueprint(prestamo_blueprint)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if 'session' in locals():
            session.remove()

    return app
