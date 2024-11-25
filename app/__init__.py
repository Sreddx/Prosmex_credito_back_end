from flask import Flask
from .database import db, init_engine, init_session, init_db
from .models import *
from .extensions import bcrypt, jwt
from flask_cors import CORS
from config import localConfig
from flask_migrate import Migrate, migrate as run_migration, upgrade as apply_upgrade
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services import verificar_pagos_semanal
from app.constants import TIMEZONE
import os


def iniciar_cronjobs(app):
    """
    Configura el cronjob que ejecuta la función de verificar_pagos_semanal cada domingo a las 00:00 horas.
    """
    scheduler = BackgroundScheduler(timezone=TIMEZONE)

    # Configurar el cronjob para los domingos a las 00:00
    trigger = CronTrigger(day_of_week='sun', hour=0, minute=0)

    # Agregar el trabajo al scheduler
    scheduler.add_job(func=verificar_pagos_semanal, trigger=trigger)
    scheduler.start()
    print("Cronjob 'verificar_pagos_semanal' registrado para ejecutarse cada domingo a las 00:00.")
    print("Trabajos programados:", scheduler.get_jobs())

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(localConfig)
    print(app.config)
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
        # Run migrations and upgrade if the migration folder exists and is not empty
        if os.path.exists(os.path.join(app.root_path, 'migrations')):
            try:
                # Run migrations to detect changes
                run_migration(message="Automated migration")
                print("Migration script generated.")
            except Exception as e:
                print(f"No new changes to migrate: {e}")
            
            try:
                # Apply any pending migrations
                apply_upgrade()
                print("Database upgraded successfully.")
            except Exception as e:
                print(f"Failed to upgrade the database: {e}")
        else:
            print("Migration directory does not exist. Initialize it manually if needed.")

    # Load initial catalog data
    with app.app_context():
        from .populate_data import populate_data
        try:
            populate_data()
        except Exception as e:
            raise ValueError(f"Error loading initial data: {str(e)}")

    CORS(app, supports_credentials=True, origins=["*"], allow_headers=["Content-Type", "Authorization", "X-CSRF-TOKEN"], expose_headers=["Content-Type", "Authorization", "X-CSRF-TOKEN"])
    
    # Initialize objects of the extensions
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Import and register blueprints
    from .blueprints import auth_blueprint, user_blueprint, role_blueprint, cliente_blueprint, prestamo_blueprint, grupos_blueprint, rutas_blueprint, pagos_blueprint, reporte_blueprint, cortes_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(role_blueprint)
    app.register_blueprint(cliente_blueprint)
    app.register_blueprint(prestamo_blueprint)
    app.register_blueprint(grupos_blueprint)
    app.register_blueprint(rutas_blueprint)
    app.register_blueprint(pagos_blueprint)
    app.register_blueprint(reporte_blueprint)
    app.register_blueprint(cortes_blueprint)

    
    
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if 'session' in locals():
            session.remove()

    return app
