from ..database import db

class Corte(db.Model):
    __tablename__ = 'corte'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    corte_total = db.Column(db.Numeric, nullable=False)
    total_gastos = db.Column(db.Numeric, nullable=False)
    semilla = db.Column(db.Numeric, nullable=False)
    
    def serialize(self):
        return {
            'id': self.id,
            'fecha': self.fecha,
            'corte_total': float(self.corte_total),
            'total_gastos': float(self.total_gastos),
            'semilla': float(self.semilla)
        }
    