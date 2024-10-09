from ..database import db
from .usuario import Usuario
class Grupo(db.Model):
    __tablename__ = 'grupos'
    grupo_id = db.Column(db.Integer, primary_key=True)
    nombre_grupo = db.Column(db.String(100))
    ruta_id = db.Column(db.Integer, db.ForeignKey('rutas.ruta_id'))
    usuario_id_titular = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    # Relationship to ruta one to many
    ruta = db.relationship('Ruta', backref=db.backref('grupos', lazy=True))
    usuarioTitular = db.relationship('Usuario', backref=db.backref('grupos', lazy=True))
    
    
    # Validate that the usuarioGerente has role 4 for gerente and 3 for supervisor
    def validar_titular(self):
        if self.usuario_id_titular:
            titular = Usuario.query.get(self.usuario_id_titular)
            if titular.rol_id != 2:
                raise ValueError("El usuario asignado como totular al grupo no tiene el rol correcto.")
        
    def serialize(self):
        return {
            'grupo_id': self.grupo_id,
            'nombre_grupo': self.nombre_grupo,
            'ruta_id': self.ruta_id,
            'usuario_id_titular': self.usuario_id_titular
        }