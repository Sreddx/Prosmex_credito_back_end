from ..database import db
from sqlalchemy.orm import validates

class ClienteAval(db.Model):
    __tablename__ = 'clientes_avales'
    titular_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido_paterno = db.Column(db.String(100))
    apellido_materno = db.Column(db.String(100))
    colonia = db.Column(db.String(100))
    cp = db.Column(db.String(5))
    codigo_ine = db.Column(db.String(18))
    estado_civil = db.Column(db.Enum('casado', 'divorciado', 'viudo', 'soltero', name='estado_civil_types'))
    num_hijos = db.Column(db.Integer)
    propiedad = db.Column(db.Enum('casa_propia', 'rentada', 'prestada', name='tipo_propiedad'))
    es_aval = db.Column(db.Boolean)
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

    def serialize(self):
        return {
            'titular_id': self.titular_id,
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