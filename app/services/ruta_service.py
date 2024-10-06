# app/services/ruta_service.py

from app.models import Ruta, Usuario
from app import db
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError

class RutaService:
    def __init__(self, ruta_id=None):
        self.ruta_id = ruta_id

    def create_ruta(self, data):
        try:
            new_ruta = Ruta(
                nombre_ruta=data['nombre_ruta'],
                usuario_id_gerente=data.get('usuario_id_gerente'),
                usuario_id_supervisor=data.get('usuario_id_supervisor')
            )
            new_ruta.validate_gerente_supervisor()
            db.session.add(new_ruta)
            db.session.commit()
            return new_ruta
        except ValueError as e:
            db.session.rollback()
            app.logger.error(f"Validation error: {str(e)}")
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error creating ruta: {str(e)}")
            raise ValueError("No se pudo crear la ruta.")

    def get_ruta(self):
        if not self.ruta_id:
            raise ValueError("Ruta ID no proporcionado.")

        try:
            ruta = Ruta.query.get(self.ruta_id)
            if not ruta:
                raise ValueError(f"No se encontró la ruta con ID: {self.ruta_id}")
            return ruta
        except SQLAlchemyError as e:
            app.logger.error(f"Error fetching ruta: {str(e)}")
            raise ValueError("No se pudo obtener la ruta.")

    def update_ruta(self, data):
        ruta = self.get_ruta()
        if not ruta:
            return None

        try:
            ruta.nombre_ruta = data.get('nombre_ruta', ruta.nombre_ruta)
            ruta.usuario_id_gerente = data.get('usuario_id_gerente', ruta.usuario_id_gerente)
            ruta.usuario_id_supervisor = data.get('usuario_id_supervisor', ruta.usuario_id_supervisor)
            ruta.validate_gerente_supervisor()
            db.session.commit()
            return ruta
        except ValueError as e:
            db.session.rollback()
            app.logger.error(f"Validation error: {str(e)}")
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error updating ruta: {str(e)}")
            raise ValueError("No se pudo actualizar la ruta.")

    def delete_ruta(self):
        ruta = self.get_ruta()
        if not ruta:
            raise ValueError(f"No se encontró la ruta con ID: {self.ruta_id}")

        try:
            db.session.delete(ruta)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error deleting ruta: {str(e)}")
            raise ValueError("No se pudo eliminar la ruta.")

    def list_rutas(self):
        try:
            rutas = Ruta.query.all()
            rutas_list = [ruta.serialize() for ruta in rutas]
            return rutas_list
        except SQLAlchemyError as e:
            app.logger.error(f"Error listing rutas: {str(e)}")
            raise ValueError("No se pudo obtener la lista de rutas.")
