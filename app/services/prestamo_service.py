from app.models import Prestamo
from app import db
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError

class PrestamoService:
    def __init__(self, prestamo_id=None):
        self.prestamo_id = prestamo_id

    def create_prestamo(self, data):
        try:
            # 
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
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error creando préstamo: {str(e)}")
            raise ValueError("No se pudo crear el préstamo.")

    def get_prestamo(self):
        if not self.prestamo_id:
            raise ValueError("Prestamo ID no proporcionado.")

        try:
            prestamo = Prestamo.query.get(self.prestamo_id)
            if not prestamo:
                raise ValueError(f"No se encontró el préstamo con ID: {self.prestamo_id}")
            return prestamo
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo préstamo: {str(e)}")
            raise ValueError("No se pudo obtener el préstamo.")

    def update_prestamo(self, data):
        prestamo = self.get_prestamo()
        if not prestamo:
            return None

        try:
            prestamo.cliente_id = data.get('cliente_id', prestamo.cliente_id)
            prestamo.fecha_inicio = data.get('fecha_inicio', prestamo.fecha_inicio)
            prestamo.monto_prestamo = data.get('monto_prestamo', prestamo.monto_prestamo)
            prestamo.tipo_prestamo_id = data.get('tipo_prestamo_id', prestamo.tipo_prestamo_id)
            prestamo.titular_id = data.get('titular_id', prestamo.titular_id)
            prestamo.aval_id = data.get('aval_id', prestamo.aval_id)

            db.session.commit()
            return prestamo
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error actualizando préstamo: {str(e)}")
            raise ValueError("No se pudo actualizar el préstamo.")

    def delete_prestamo(self):
        prestamo = self.get_prestamo()
        if not prestamo:
            raise ValueError(f"No se encontró el préstamo con ID: {self.prestamo_id}")

        try:
            db.session.delete(prestamo)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error eliminando préstamo: {str(e)}")
            raise ValueError("No se pudo eliminar el préstamo.")

    def list_prestamos(self):
        try:
            return Prestamo.query.all()
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando préstamos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de préstamos.")
