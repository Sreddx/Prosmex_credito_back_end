from ..database import db
from .usuario import Usuario
class Ruta(db.Model):
    __tablename__ = 'rutas'
    ruta_id = db.Column(db.Integer, primary_key=True)
    nombre_ruta = db.Column(db.String(100))
    usuario_id_gerente = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario_id_supervisor = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    
    
    
    def serialize(self):
        return {
            'ruta_id': self.ruta_id,
            'nombre_ruta': self.nombre_ruta,
            'usuario_id_gerente': self.usuario_id_gerente,
            'usuario_id_supervisor': self.usuario_id_supervisor
        }
        
    # Validate that the usuarioGerente has role 4 for gerente and 3 for supervisor
    def validate_gerente_supervisor(self):
        if self.usuario_id_gerente:
            gerente = Usuario.query.get(self.usuario_id_gerente)
            if gerente.rol_id != 4:
                raise ValueError("El usuario asignado como gerente no tiene el rol correcto.")
        if self.usuario_id_supervisor:
            supervisor = Usuario.query.get(self.usuario_id_supervisor)
            if supervisor.rol_id != 3:
                raise ValueError("El usuario asignado como supervisor no tiene el rol correcto.")