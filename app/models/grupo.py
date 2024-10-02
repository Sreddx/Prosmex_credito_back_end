from ..database import db

class Grupo(db.Model):
    __tablename__ = 'grupos'
    grupo_id = db.Column(db.Integer, primary_key=True)
    nombre_grupo = db.Column(db.String(100))
    ruta_id = db.Column(db.Integer, db.ForeignKey('rutas.ruta_id'))
    usuario_id_titular = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    # Relationship to ruta one to many
    ruta = db.relationship('Ruta', backref=db.backref('grupos', lazy=True))