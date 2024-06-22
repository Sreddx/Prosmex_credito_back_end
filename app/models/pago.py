from ..database import db

class Pago(db.Model):
    __tablename__ = 'pagos'
    pago_id = db.Column(db.Integer, primary_key=True)
    fecha_pago = db.Column(db.DateTime)
    monto_pagado = db.Column(db.Numeric)
    prestamo_id = db.Column(db.Integer, db.ForeignKey('prestamos.prestamo_id'))
