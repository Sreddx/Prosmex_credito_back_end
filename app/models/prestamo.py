from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint, UniqueConstraint
from .cliente_aval import ClienteAval
from ..database import db
class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    prestamo_id = db.Column(db.Integer, primary_key=True)
    monto_prestamo = db.Column(db.Numeric, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes_avales.cliente_id'), nullable=False)
    aval_id = db.Column(db.Integer, db.ForeignKey('clientes_avales.cliente_id'), nullable=True)
    tipo_prestamo_id = db.Column(db.Integer, db.ForeignKey('tipos_prestamo.tipo_prestamo_id'), nullable=False)

    
    # Relaciones
    titular = db.relationship(
        'ClienteAval',
        foreign_keys=[cliente_id],
        backref=db.backref('prestamos_como_titular', lazy=True),
        overlaps="prestamos_como_aval"
    )
    aval = db.relationship(
        'ClienteAval',
        foreign_keys=[aval_id],
        backref=db.backref('prestamos_como_aval', lazy=True),
        overlaps="prestamos_como_titular"
    )
    tipo_prestamo = db.relationship(
        'TipoPrestamo',
        backref=db.backref('prestamos', lazy=True)
    )
    pagos = db.relationship(
        'Pago',
        backref=db.backref('prestamo', lazy=True)
    )

    
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

    # Validation to ensure the aval has not been used in another loan within the same group
    @validates('aval_id')
    def validate_aval_id(self, key, aval_id):
        # Get the group of the cliente
        cliente = ClienteAval.query.get(self.cliente_id)
        if not cliente:
            raise ValueError(f"Cliente con ID {self.cliente_id} no encontrado.")

        # Check if the aval already has a loan in the same group
        existing_prestamo = (
            Prestamo.query
            .join(ClienteAval, Prestamo.aval_id == ClienteAval.cliente_id)
            .filter(ClienteAval.grupo_id == cliente.grupo_id)
            .filter(Prestamo.aval_id == aval_id)
            .filter(Prestamo.prestamo_id != self.prestamo_id)  # Exclude the current loan (if updating)
            .first()
        )
        
        if existing_prestamo:
            raise ValueError(f"El aval con ID {aval_id} ya está asignado a otro préstamo en el grupo del cliente.")
        
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
