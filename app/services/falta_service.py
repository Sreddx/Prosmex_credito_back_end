from app.models import Falta, Prestamo
from app import db
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError

class FaltaService:
    def __init__(self, falta_id=None):
        self.falta_id = falta_id

    def create_falta(self, data):
        try:
            new_falta = Falta(
                fecha=data['fecha'],
                prestamo_id=data['prestamo_id']
            )
            db.session.add(new_falta)
            db.session.commit()
            return new_falta
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error creando falta: {str(e)}")
            raise ValueError("No se pudo crear la falta.")

    def get_falta(self):
        if not self.falta_id:
            raise ValueError("Falta ID no proporcionado.")

        try:
            falta = Falta.query.get(self.falta_id)
            if not falta:
                raise ValueError(f"No se encontró la falta con ID: {self.falta_id}")
            return falta
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo falta: {str(e)}")
            raise ValueError("No se pudo obtener la falta.")

    def update_falta(self, data):
        falta = self.get_falta()
        if not falta:
            return None

        try:
            falta.fecha = data.get('fecha', falta.fecha)
            falta.prestamo_id = data.get('prestamo_id', falta.prestamo_id)

            db.session.commit()
            return falta
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error actualizando falta: {str(e)}")
            raise ValueError("No se pudo actualizar la falta.")

    def delete_falta(self):
        falta = self.get_falta()
        if not falta:
            raise ValueError(f"No se encontró la falta con ID: {self.falta_id}")

        try:
            db.session.delete(falta)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error eliminando falta: {str(e)}")
            raise ValueError("No se pudo eliminar la falta.")

    def list_faltas(self):
        try:
            faltas = Falta.query.all()
            return [falta.serialize() for falta in faltas]
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando faltas: {str(e)}")
            raise ValueError("No se pudo obtener la lista de faltas.")
