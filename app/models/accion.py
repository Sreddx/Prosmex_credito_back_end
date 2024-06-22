from ..database import db

class Accion(db.Model):
    __tablename__ = 'acciones'
    accion_id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255))
