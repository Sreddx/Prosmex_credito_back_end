from ..database import db

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
