from app.models import Prestamo

from app import db

class PrestamoService:
    @staticmethod
    def create_prestamo(data):
        new_prestamo = Prestamo(
            cliente_id=data['cliente_id'],
            fecha_inicio=data['fecha_inicio'],
            monto_prestamo=data['monto_prestamo'],
            tipo_prestamo_id=data['tipo_prestamo_id'],
            titular_id=data['titular_id'],
            aval_id=data['aval_id']
        )
        db.session.add(new_prestamo)
        db.session.commit()
        return new_prestamo