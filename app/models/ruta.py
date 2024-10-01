from ..database import db

class Ruta(db.Model):
    __tablename__ = 'rutas'
    ruta_id = db.Column(db.Integer, primary_key=True)
    nombre_ruta = db.Column(db.String(100))
    usuario_id_gerente = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario_id_supervisor = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
