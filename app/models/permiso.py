from ..database import db

class Permiso(db.Model):
    __tablename__ = 'permisos'
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.rol_id'), primary_key=True)
    accion_id = db.Column(db.Integer, db.ForeignKey('acciones.accion_id'), primary_key=True)
