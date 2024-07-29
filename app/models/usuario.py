from ..database import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellido_paterno = db.Column(db.String(255), nullable=False)
    apellido_materno = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.rol_id'))
    
    # Relationship
    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))
