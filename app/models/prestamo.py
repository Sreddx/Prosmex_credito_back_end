from ..database import db
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint, UniqueConstraint

class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    
    prestamo_id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes_avales.titular_id'))
    fecha_inicio = db.Column(db.DateTime)
    monto_prestamo = db.Column(db.Numeric)
    tipo_prestamo_id = db.Column(db.Integer, db.ForeignKey('tipos_prestamo.tipo_prestamo_id'))
    aval_id = db.Column(db.Integer, db.ForeignKey('clientes_avales.titular_id'))  # Checar si es aval
    
    # Relationships many-to-one
    cliente = db.relationship('ClienteAval', foreign_keys=[cliente_id])
    tipo_prestamo = db.relationship('TipoPrestamo', foreign_keys=[tipo_prestamo_id])
    aval = db.relationship('ClienteAval', foreign_keys=[aval_id])
    
    # Ensure that monto_prestado is greater than 0
    __table_args__ = (
        CheckConstraint('monto_prestamo > 0', name='check_monto_prestamo_positive'),
        UniqueConstraint('aval_id', name='uq_aval_id')  # Enforce unique aval_id
    )
    
    # Validation for monto_prestamo > 0
    @validates('monto_prestamo')
    def validate_monto_prestamo(self, key, value):
        if value <= 0:
            raise ValueError("El monto del préstamo debe ser mayor que 0.")
        return value

    # Validation to prevent repeated aval_id between loans
    @validates('aval_id')
    def validate_aval_id(self, key, aval_id):
        existing_prestamo = Prestamo.query.filter_by(aval_id=aval_id).first()
        if existing_prestamo:
            raise ValueError(f"El aval con ID {aval_id} ya está asociado a otro préstamo.")
        return aval_id

    def serialize(self):
        return {
            'prestamo_id': self.prestamo_id,
            'cliente_id': self.cliente_id,
            'fecha_inicio': self.fecha_inicio,
            'monto_prestamo': self.monto_prestamo,
            'tipo_prestamo_id': self.tipo_prestamo_id,
            'aval_id': self.aval_id
        }
