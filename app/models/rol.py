from ..database import db

class Rol(db.Model):
    __tablename__ = 'roles'
    rol_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    permisos = db.relationship('Permiso', backref='rol', lazy='dynamic')
