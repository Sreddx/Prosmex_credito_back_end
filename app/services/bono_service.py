from app.models import Bono
from app import db
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError

class BonoService:
    def __init__(self, bono_id=None):
        self.bono_id = bono_id

    def create_bono(self, data):
        try:
            new_bono = Bono(
                monto=data['monto'],
                entrega_min=data['entrega_min'],
                entrega_max=data['entrega_max'],
                fallas=data['fallas']
            )
            db.session.add(new_bono)
            db.session.commit()
            return new_bono
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error creando bono: {str(e)}")
            raise ValueError("No se pudo crear el bono.")

    def get_bono(self):
        if not self.bono_id:
            raise ValueError("Bono ID no proporcionado.")

        try:
            bono = Bono.query.get(self.bono_id)
            if not bono:
                raise ValueError(f"No se encontró el bono con ID: {self.bono_id}")
            return bono
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo bono: {str(e)}")
            raise ValueError("No se pudo obtener el bono.")

    def update_bono(self, data):
        bono = self.get_bono()
        if not bono:
            return None

        try:
            bono.monto = data.get('monto', bono.monto)
            bono.entrega_min = data.get('entrega_min', bono.entrega_min)
            bono.entrega_max = data.get('entrega_max', bono.entrega_max)
            bono.fallas = data.get('fallas', bono.fallas)

            db.session.commit()
            return bono
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error actualizando bono: {str(e)}")
            raise ValueError("No se pudo actualizar el bono.")

    def delete_bono(self):
        bono = self.get_bono()
        if not bono:
            raise ValueError(f"No se encontró el bono con ID: {self.bono_id}")

        try:
            db.session.delete(bono)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error eliminando bono: {str(e)}")
            raise ValueError("No se pudo eliminar el bono.")

    def list_bonos(self):
        try:
            bonos = Bono.query.all()
            return [bono.serialize() for bono in bonos]
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando bonos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de bonos.")
        
    