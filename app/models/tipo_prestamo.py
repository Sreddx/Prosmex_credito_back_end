from ..database import db

class TipoPrestamo(db.Model):
    __tablename__ = 'tipos_prestamo'
    nombre = db.Column(db.String(50))
    tipo_prestamo_id = db.Column(db.Integer, primary_key=True)
    numero_semanas = db.Column(db.Integer)
    porcentaje_semanal = db.Column(db.Float)
    incumplimientos_tolerados = db.Column(db.Integer)
    pena_incumplimiento = db.Column(db.Numeric)
    limite_penalizaciones = db.Column(db.Integer)
