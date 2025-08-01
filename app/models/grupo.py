from app.models.cliente_aval import ClienteAval
from ..database import db
from .usuario import Usuario

class Grupo(db.Model):
    __tablename__ = 'grupos'
    grupo_id = db.Column(db.Integer, primary_key=True)
    nombre_grupo = db.Column(db.String(100))
    ruta_id = db.Column(db.Integer, db.ForeignKey('rutas.ruta_id'))
    usuario_id_titular = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    # Relaciones
    ruta = db.relationship('Ruta', backref=db.backref('grupos', lazy=True))
    usuarioTitular = db.relationship('Usuario', backref=db.backref('grupos', lazy=True))
    clientes_avales = db.relationship('ClienteAval', backref='grupo', lazy=True)

    # # Relación uno a muchos con Corte
    # cortes = db.relationship('Corte', backref='grupo', lazy=True)

    def validar_titular(self):
        if self.usuario_id_titular:
            titular = Usuario.query.get(self.usuario_id_titular)
            if titular.rol_id != 2:
                raise ValueError("El usuario asignado como titular al grupo no tiene el rol correcto.")

    def serialize(self):
        return {
            'grupo_id': self.grupo_id,
            'nombre_grupo': self.nombre_grupo,
            'ruta_id': self.ruta_id,
            'usuario_id_titular': self.usuario_id_titular
        }

    def calcular_morosidad_de_prestamos_en_grupo(self):
        """Calcula la morosidad de los préstamos en el grupo."""
        # Se obtienen los clientes del grupo, se sacan los montos restantes de cada cliente y se suman
        morosidad_total = 0
        for cliente in self.clientes_avales:
            morosidad_total += cliente.calcular_monto_restante()
        return morosidad_total
    
    @staticmethod
    def calcular_sobrante_grupo(grupo_id):
        clientes_grupo = ClienteAval.query.filter_by(grupo_id=grupo_id).all()
        total_sobrante = 0
        for cliente in clientes_grupo:
            total_sobrante -= cliente.calcular_monto_restante_utilidad()
        return float(total_sobrante)
        