from ..database import db

class Bono(db.Model):
    __tablename__ = 'bono'
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Numeric, nullable=False)
    entrega_min = db.Column(db.Numeric, nullable=False)
    entrega_max = db.Column(db.Numeric, nullable=False)
    fallas = db.Column(db.Integer, nullable=False)
    
    
    
    def regla_bono(self, cobranza_ideal_grupo, faltas_de_grupo):
        if cobranza_ideal_grupo >= self.entrega_min and cobranza_ideal_grupo <= self.entrega_max:
            if faltas_de_grupo <= self.fallas:
                return True
            else:
                return False
        
    
    def serialize(self):
        return {
            'id': self.id,
            'monto': float(self.monto),
            'entrega_min': float(self.entrega_min),
            'entrega_max': float(self.entrega_max),
            'fallas': self.fallas
        }
    