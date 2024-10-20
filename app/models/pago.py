from datetime import datetime
import pytz
from ..database import db
from .prestamo import Prestamo

class Pago(db.Model):
    __tablename__ = 'pagos'
    pago_id = db.Column(db.Integer, primary_key=True)
    fecha_pago = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('America/Mexico_City')), nullable=False)
    monto_pagado = db.Column(db.Numeric, nullable=False)
    prestamo_id = db.Column(db.Integer, db.ForeignKey('prestamos.prestamo_id'), nullable=False)

    def serialize(self):
        prestamo = Prestamo.query.get(self.prestamo_id)
        if not prestamo:
            raise ValueError(f"No se encontró el préstamo con ID: {self.prestamo_id}")
        return {
            'id': self.pago_id,
            'fecha_pago': self.fecha_pago,
            'monto_pagado': str(self.monto_pagado),
            'prestamo': prestamo.serialize()
        }
