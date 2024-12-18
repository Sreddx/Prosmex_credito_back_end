from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint, UniqueConstraint
from .falta import Falta
from ..database import db
from datetime import datetime, timedelta
from app.constants import TIMEZONE
import pytz

class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    prestamo_id = db.Column(db.Integer, primary_key=True)
    monto_prestamo = db.Column(db.Numeric, nullable=False)
    monto_prestamo_real = db.Column(db.Numeric, nullable=True)
    monto_utilidad = db.Column(db.Numeric, nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=lambda: datetime.now(TIMEZONE), nullable=False) #Fecha para contar semanas de prestamos es a partir del lunes de la semana de que se pidio el prestamo
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes_avales.cliente_id'), nullable=False)
    aval_id = db.Column(db.Integer, db.ForeignKey('clientes_avales.cliente_id'), nullable=True)
    tipo_prestamo_id = db.Column(db.Integer, db.ForeignKey('tipos_prestamo.tipo_prestamo_id'), nullable=False)
    completado = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.Enum('activo', 'renovado', 'liquidado', 'vencido', name='status_prestamo'), default='activo', nullable=False)
    renovacion = db.Column(db.Boolean, default=False, nullable=False)
    semana_activa = db.Column(db.Integer, default=0, nullable=False)
    
    
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
        # UniqueConstraint('aval_id', name='uq_aval_id')  # Enforce unique aval_id
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verificar_si_es_renovacion()
        
    def verificar_si_es_renovacion(self):
        """
        Verifica si el préstamo es una renovación.
        """
        prestamo_anterior = Prestamo.query.filter_by(cliente_id=self.cliente_id, status='activo').first()
        
        if prestamo_anterior and prestamo_anterior.semana_activa >= 9:
            self.renovacion = True
            self.completar_prestamo_anterior_restar_monto_faltante_monto_prestamo_actual(prestamo_anterior)
    
    def completar_prestamo_anterior_restar_monto_faltante_monto_prestamo_actual(self, prestamo_anterior):
        """
        Completa el préstamo anterior y resta el monto faltante al monto del préstamo actual.
        """
        if not prestamo_anterior:
            raise ValueError("No se encontró un préstamo anterior.")
        if prestamo_anterior.completado:
            raise ValueError("El préstamo anterior ya está completado.")
        
        monto_faltante = prestamo_anterior.monto_utilidad - prestamo_anterior.calcular_monto_pagado()
        prestamo_anterior.completado = True
        self.monto_prestamo_real = float(self.monto_prestamo) - float(monto_faltante)
        db.session.commit()
    
    def actualizar_semana_activa(self, cubre_cobranza):
        if cubre_cobranza:
            self.semana_activa += 1
            db.session.commit()
    
    def verificar_completado(self):
        """Calcula si el préstamo está completo sumando los pagos."""
        monto_pagado_total = sum([float(pago.monto_pagado) for pago in self.pagos])
        if monto_pagado_total >= self.monto_utilidad or self.semana_activa == self.tipo_prestamo.numero_semanas:
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

    @validates('aval_id')
    def validate_aval_id(self, key, aval_id):
        from app.models.cliente_aval import ClienteAval
        # Get the group of the cliente
        cliente = ClienteAval.query.get(self.cliente_id)
        if not cliente:
            raise ValueError(f"Cliente con ID {self.cliente_id} no encontrado.")

        # Check if the aval has a loan in the same group for a different client
        existing_prestamo = (
            Prestamo.query
            .join(ClienteAval, Prestamo.aval_id == ClienteAval.cliente_id)
            .filter(ClienteAval.grupo_id == cliente.grupo_id)
            .filter(Prestamo.aval_id == aval_id)
            .filter(Prestamo.cliente_id != self.cliente_id)  # Ensure it's for a different client
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
            'monto_utilidad': self.monto_utilidad,
            'tipo_prestamo_id': self.tipo_prestamo_id,
            'aval_id': self.aval_id,
            'completado': self.completado,
            'status': self.status,
            'renovacion': self.renovacion,
            'semana_activa': self.semana_activa,
            'monto_pagado': self.calcular_monto_pagado(),
            'monto_restante': self.calcular_monto_restante()
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
    
    
    def verificar_pago_cubre_cobranza_ideal(self, pago):
        cobranza_ideal = self.calcular_cobranza_ideal()
        try:
            if pago.monto_pagado < cobranza_ideal:
                falta = Falta(fecha=datetime.now(TIMEZONE).date(), prestamo_id=self.prestamo_id, monto_abonado=pago.monto_pagado)
                db.session.add(falta)
                db.session.commit()
                return False
            return True
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"No se pudo verificar el pago: {str(e)}")
        
    def calcular_monto_pagado(self):
        """Calcula el monto total pagado por el cliente."""
        monto_pagado = sum([pago.monto_pagado for pago in self.pagos]) if self.pagos else 0
        return monto_pagado
    
    def calcular_monto_restante(self):
        """Calcula el monto restante por pagar del cliente."""
        monto_restante = self.monto_prestamo- self.calcular_monto_pagado()
        return monto_restante

