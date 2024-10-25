from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint, UniqueConstraint
from .cliente_aval import ClienteAval
from ..database import db
from datetime import datetime
import pytz

class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    prestamo_id = db.Column(db.Integer, primary_key=True)
    monto_prestamo = db.Column(db.Numeric, nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('America/Mexico_City')), nullable=False) #Fecha para contar semanas de prestamos es a partir del lunes de la semana de que se pidio el prestamo
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes_avales.cliente_id'), nullable=False)
    aval_id = db.Column(db.Integer, db.ForeignKey('clientes_avales.cliente_id'), nullable=True)
    tipo_prestamo_id = db.Column(db.Integer, db.ForeignKey('tipos_prestamo.tipo_prestamo_id'), nullable=False)
    completado = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.Enum('activo', 'renovado', 'liquidado', 'vencido', name='status_prestamo'), default='activo', nullable=False)
    
    
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
    # Relacion uno a muchos con la tabla de faltas
    faltas = db.relationship(
        'Falta',
        backref=db.backref('prestamo', lazy=True)
    )

    
    # Ensure that monto_prestado is greater than 0
    __table_args__ = (
        CheckConstraint('monto_prestamo > 0', name='check_monto_prestamo_positive'),
        UniqueConstraint('aval_id', name='uq_aval_id')  # Enforce unique aval_id
    )
    
    
    def verificar_completado(self):
        """Calcula si el préstamo está completo sumando los pagos."""
        monto_pagado_total = sum([float(pago.monto_pagado) for pago in self.pagos])
        if monto_pagado_total >= float(self.monto_prestamo):
            self.completado = True
        else:
            self.completado = False
        db.session.commit()
    
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
            'aval_id': self.aval_id,
            'completado': self.completado
        }
        
    # Funciones de operacion
    def calcular_cobranza_ideal(self):
        """
        Calcula la cobranza ideal semanal basada en el monto del préstamo y el porcentaje semanal del tipo de préstamo.
        """
        return float(self.monto_prestamo) * self.tipo_prestamo.porcentaje_semanal
    
    
    def verificar_pagos_semana(self, fecha_inicio_semana):
        """
        Verifica los pagos realizados en una semana específica y compara con la cobranza ideal.
        Registra una falta si los pagos no cubren la cobranza ideal.
        """
        cobranza_ideal = self.calcular_cobranza_ideal()

        # Calcular la fecha final de la semana
        fecha_final_semana = fecha_inicio_semana + timedelta(days=6)

        # Sumar los pagos realizados durante esa semana en la zona horaria de Ciudad de México
        pagos_semanales = sum(
            float(pago.monto_pagado)
            for pago in self.pagos
            if fecha_inicio_semana <= pago.fecha_pago.astimezone(TIMEZONE).date() <= fecha_final_semana
        )

        # Si los pagos no cubren la cobranza ideal, registrar una falta
        if pagos_semanales < cobranza_ideal:
            falta = Falta(fecha=datetime.now(TIMEZONE).date(), prestamo_id=self.prestamo_id)
            db.session.add(falta)
            db.session.commit()
            return False  # No se cubrió la cobranza ideal
        return True  # Se cumplió la cobranza ideal