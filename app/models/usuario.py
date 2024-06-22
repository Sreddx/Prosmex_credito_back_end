from ..database import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    usuario_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido_paterno = db.Column(db.String(100))
    apellido_materno = db.Column(db.String(100))
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.rol_id'))
    usuario_id_superior = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'))
