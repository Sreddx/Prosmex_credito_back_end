from ..database import db

class Permiso(db.Model):
    __tablename__ = 'permisos'
    id = db.Column(db.Integer, primary_key=True)  # Adding primary key
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.rol_id'), nullable=False)
    accion_id = db.Column(db.Integer, db.ForeignKey('acciones.accion_id'), nullable=False)
