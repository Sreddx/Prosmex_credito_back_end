from ..database import db

class Grupo(db.Model):
    __tablename__ = 'grupos'
    grupo_id = db.Column(db.Integer, primary_key=True)
    nombre_grupo = db.Column(db.String(100))
    ruta_id = db.Column(db.Integer, db.ForeignKey('rutas.ruta_id'))
    usuario_id_lider = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'))
