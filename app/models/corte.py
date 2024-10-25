from ..database import db
from datetime import datetime
from app.constants import TIMEZONE

class Corte(db.Model):
    __tablename__ = 'corte'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    # grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.grupo_id'), nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=lambda: datetime.now(TIMEZONE), nullable=False)
    corte_total = db.Column(db.Numeric, nullable=False)
    total_gastos = db.Column(db.Numeric, nullable=False)
    semilla = db.Column(db.Numeric, nullable=False)

    

    def serialize(self):
        return {
            'id': self.id,
            'fecha_inicio': self.fecha_inicio,
            'corte_total': float(self.corte_total),
            'total_gastos': float(self.total_gastos),
            'semilla': float(self.semilla),
            'usuario_id': self.usuario_id,
            'grupo_id': self.grupo_id
        }
