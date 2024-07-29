from ..database import db

class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    prestamo_id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes_avales.titular_id'))
    fecha_inicio = db.Column(db.DateTime)
    monto_prestamo = db.Column(db.Numeric)
    tipo_prestamo_id = db.Column(db.Integer, db.ForeignKey('tipos_prestamo.tipo_prestamo_id'))
    titular_id = db.Column(db.Integer, db.ForeignKey('clientes_avales.titular_id'))
    aval_id = db.Column(db.Integer, db.ForeignKey('clientes_avales.titular_id'))