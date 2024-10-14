from app.models import Pago, Prestamo, Grupo
from app import db
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError

class PagoService:
    def __init__(self, pago_id=None):
        self.pago_id = pago_id

    def create_pago(self, data):
        try:
            # Validate required fields
            required_fields = ['fecha_pago', 'monto_pagado', 'prestamo_id']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValueError(f"Faltan campos requeridos: {', '.join(missing_fields)}")

            # Ensure the prestamo exists
            prestamo = Prestamo.query.get(data['prestamo_id'])
            if not prestamo:
                raise ValueError("El préstamo especificado no existe.")

            # Create the Pago instance
            new_pago = Pago(
                fecha_pago=data['fecha_pago'],
                monto_pagado=data['monto_pagado'],
                prestamo_id=data['prestamo_id']
            )
            db.session.add(new_pago)
            db.session.commit()
            return new_pago
        except (ValueError, SQLAlchemyError) as e:
            db.session.rollback()
            app.logger.error(f"Error creando pago: {str(e)}")
            raise

    def get_pago(self):
        if not self.pago_id:
            raise ValueError("Pago ID no proporcionado.")

        try:
            pago = Pago.query.get(self.pago_id)
            if not pago:
                raise ValueError(f"No se encontró el pago con ID: {self.pago_id}")
            return pago
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo pago: {str(e)}")
            raise ValueError("No se pudo obtener el pago.")

    def update_pago(self, data):
        pago = self.get_pago()
        if not pago:
            return None

        try:
            pago.fecha_pago = data.get('fecha_pago', pago.fecha_pago)
            pago.monto_pagado = data.get('monto_pagado', pago.monto_pagado)
            pago.prestamo_id = data.get('prestamo_id', pago.prestamo_id)
            db.session.commit()
            return pago
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error actualizando pago: {str(e)}")
            raise ValueError("No se pudo actualizar el pago.")

    def delete_pago(self):
        pago = self.get_pago()
        if not pago:
            raise ValueError(f"No se encontró el pago con ID: {self.pago_id}")

        try:
            db.session.delete(pago)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error eliminando pago: {str(e)}")
            raise ValueError("No se pudo eliminar el pago.")

    def list_pagos(self):
        try:
            pagos = Pago.query.all()
            pagos_list = [pago.serialize() for pago in pagos]
            return pagos_list
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando pagos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de pagos.")

    @staticmethod
    def get_grupos():
        try:
            grupos = Grupo.query.all()
            grupos_list = [{'id': grupo.grupo_id, 'nombre': grupo.nombre} for grupo in grupos]
            return grupos_list
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo grupos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de grupos.")

    @staticmethod
    def get_prestamos_by_grupo(grupo_id):
        try:
            # Assuming Prestamo model has a 'grupo_id' foreign key
            prestamos = Prestamo.query.filter_by(grupo_id=grupo_id).all()
            prestamos_list = [{'id': prestamo.prestamo_id, 'monto': float(prestamo.monto_prestado)} for prestamo in prestamos]
            return prestamos_list
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo préstamos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de préstamos.")
    
    @staticmethod
    def get_pagos_by_prestamo(prestamo_id):
        try:
            pagos = Pago.query.filter_by(prestamo_id=prestamo_id).all()
            pagos_list = [pago.serialize() for pago in pagos]
            return pagos_list
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo pagos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de pagos.")