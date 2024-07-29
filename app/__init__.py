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
    
    # Load initial catalog data
    with app.app_context():
        from .populate_data import populate_data
        populate_data()


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
