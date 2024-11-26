from ..database import db
from sqlalchemy.orm import validates

class ClienteAval(db.Model):
    __tablename__ = 'clientes_avales'
    cliente_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido_paterno = db.Column(db.String(100))
    apellido_materno = db.Column(db.String(100))
    colonia = db.Column(db.String(100))
    cp = db.Column(db.String(5))
    codigo_ine = db.Column(db.String(18))
    estado_civil = db.Column(db.Enum('casado', 'divorciado', 'viudo', 'soltero', name='estado_civil_types'))
    num_hijos = db.Column(db.Integer)
    propiedad = db.Column(db.Enum('casa_propia', 'rentada', 'prestada', name='tipo_propiedad'))
    es_aval = db.Column(db.Boolean, default=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.grupo_id'))
    
    

    @validates('cp')
    def validate_cp(self, key, cp):
        if len(cp) != 5 or not cp.isdigit():
            raise ValueError("Código postal no válido.")
        return cp

    @validates('num_hijos')
    def validate_num_hijos(self, key, num_hijos):
        if num_hijos < 0:
            raise ValueError("El número de hijos no puede ser negativo.")
        return num_hijos
    def getNombreCompleto(self):
        return f'{self.nombre} {self.apellido_paterno} {self.apellido_materno}'
    def serialize(self):
        return {
            'id': self.cliente_id,
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'apellido_materno': self.apellido_materno,
            'colonia': self.colonia,
            'cp': self.cp,
            'codigo_ine': self.codigo_ine,
            'estado_civil': self.estado_civil,
            'num_hijos': self.num_hijos,
            'propiedad': self.propiedad,
            'es_aval': self.es_aval,
            'grupo_id': self.grupo_id
        }
        
        
    # Calculos referentes a prestamos de cliente
    def calcular_monto_prestado(self):
        """Calcula el monto total prestado al cliente."""
        monto_prestado = sum([prestamo.monto_prestamo for prestamo in self.prestamos_como_titular]) if self.prestamos_como_titular else 0
        return monto_prestado
    
    def calcular_monto_pagado(self):
        """Calcula el monto total pagado por el cliente."""
        # Get all prestamos from cliente and sum all monto pagos for each prestamo
        monto_pagado = sum([prestamo.calcular_monto_pagado() for prestamo in self.prestamos_como_titular]) if self.prestamos_como_titular else 0
        return monto_pagado
    def calcular_monto_restante(self):
        """Calcula el monto restante por pagar del cliente."""
        monto_restante = self.calcular_monto_prestado() - self.calcular_monto_pagado()
        return monto_restante
    
    def calcular_adeudo_cliente(self):
        """Calcula el adeudo total del cliente."""
        adeudo = sum([prestamo.calcular_monto_restante() for prestamo in self.prestamos_como_titular]) if self.prestamos_como_titular else 0
        return adeudo
    
    def calcular_adeudo_cliente_sin_adeudo_prestamo_actual(self):
        """Calcula el adeudo total del cliente sin considerar el adeudo del prestamo actual."""
        adeudo = sum([prestamo.calcular_monto_restante() for prestamo in self.prestamos_como_titular[:-1]]) if self.prestamos_como_titular else 0
        return adeudo
    
    def calcular_prestamo_papel(self):
        """Calcula el monto papel prestado al cliente."""
        prestamo_papel = self.prestamos_como_titular[-1].monto_prestamo if self.prestamos_como_titular else 0
        return prestamo_papel
    
    def calcular_prestamo_real(self):
        """Calcula el monto real prestado al cliente."""
        prestamo_papel = self.calcular_prestamo_papel() 
        prestamo_real = prestamo_papel - self.calcular_adeudo_cliente_sin_adeudo_prestamo_actual()
        return prestamo_real