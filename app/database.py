from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

db = SQLAlchemy()

def init_engine(uri):
    """Create database engine."""
    engine = create_engine(uri, echo=False, pool_pre_ping=True)
    return engine

def init_session(engine):
    """Initialize a new scoped session."""
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return scoped_session(session_factory)

def init_db(app):
    """Initialize the database with the app context."""
    with app.app_context():
        db.create_all()  # Optionally create tables here if needed


