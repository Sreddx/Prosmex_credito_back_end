from app.models import Corte
from app import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app as app
from app.constants import TIMEZONE
from datetime import datetime

class CorteService:
    def __init__(self, corte_id=None):
        self.corte_id = corte_id

    def create_corte(self, data, usuario_id):
        """
        Crea un nuevo corte, vinculando un usuario y un grupo.
        """
        try:
            new_corte = Corte(
                usuario_id=usuario_id,  # Relación con el Usuario
                fecha=datetime.now(TIMEZONE),
                corte_total=data['corte_total'],
                total_gastos=data['total_gastos'],
                semilla=data['semilla']
            )
            db.session.add(new_corte)
            db.session.commit()
            return new_corte
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error creando corte: {str(e)}")
            raise ValueError("No se pudo crear el corte.")

    def get_corte(self):
        if not self.corte_id:
            raise ValueError("Corte ID no proporcionado.")

        try:
            corte = Corte.query.get(self.corte_id)
            if not corte:
                raise ValueError(f"No se encontró el corte con ID: {self.corte_id}")
            return corte
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo corte: {str(e)}")
            raise ValueError("No se pudo obtener el corte.")

    def update_corte(self, data):
        corte = self.get_corte()
        if not corte:
            return None

        try:
            corte.corte_total = data.get('corte_total', corte.corte_total)
            corte.total_gastos = data.get('total_gastos', corte.total_gastos)
            corte.semilla = data.get('semilla', corte.semilla)

            db.session.commit()
            return corte
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error actualizando corte: {str(e)}")
            raise ValueError("No se pudo actualizar el corte.")

    def delete_corte(self):
        corte = self.get_corte()
        if not corte:
            raise ValueError(f"No se encontró el corte con ID: {self.corte_id}")

        try:
            db.session.delete(corte)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error eliminando corte: {str(e)}")
            raise ValueError("No se pudo eliminar el corte.")

    def list_cortes(self):
        try:
            cortes = Corte.query.all()
            return [corte.serialize() for corte in cortes]
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando cortes: {str(e)}")
            raise ValueError("No se pudo obtener la lista de cortes.")
