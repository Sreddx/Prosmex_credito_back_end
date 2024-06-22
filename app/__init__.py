from flask import Flask
from .database import db, init_engine, init_session, init_db
from .models import *
from config import localConfig



def create_app():
    app = Flask(__name__)
    
    
    app.config.from_object(localConfig)  

    # Initialize the database
    engine = init_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    session = init_session(engine)

    db.init_app(app)
    init_db(app)  

    # Import and register blueprints
    from .blueprints.auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if 'session' in locals():
            session.remove()

    return app
