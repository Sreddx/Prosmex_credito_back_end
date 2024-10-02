from app.models import Grupo
from app import db
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError

class GrupoService:
    def __init__(self, grupo_id=None):
        self.grupo_id = grupo_id

    def create_grupo(self, data):
        try:
            new_grupo = Grupo(
                nombre=data['nombre'],
                descripcion=data['descripcion']
            )
            db.session.add(new_grupo)
            db.session.commit()
            return new_grupo
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error creando grupo: {str(e)}")
            raise ValueError("No se pudo crear el grupo.")

    def get_grupo(self):
        if not self.grupo_id:
            raise ValueError("Grupo ID no proporcionado.")

        try:
            grupo = Grupo.query.get(self.grupo_id)
            if not grupo:
                raise ValueError(f"No se encontró el grupo con ID: {self.grupo_id}")
            return grupo
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo grupo: {str(e)}")
            raise ValueError("No se pudo obtener el grupo.")

    def update_grupo(self, data):
        grupo = self.get_grupo()
        if not grupo:
            return None

        try:
            grupo.nombre = data.get('nombre', grupo.nombre)
            grupo.descripcion = data.get('descripcion', grupo.descripcion)

            db.session.commit()
            return grupo
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error actualizando grupo: {str(e)}")
            raise ValueError("No se pudo actualizar el grupo.")

    def delete_grupo(self):
        grupo = self.get_grupo()
        if not grupo:
            raise ValueError(f"No se encontró el grupo con ID: {self.grupo_id}")

        try:
            db.session.delete(grupo)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error eliminando grupo: {str(e)}")
            raise ValueError("No se pudo eliminar el grupo.")

    def list_grupos(self):
        try:
            lista_obj_grupos = Grupo.query.all()
            grupos = []
            for grupo in lista_obj_grupos:
                grupos.append({
                    'grupo_id': grupo.grupo_id,
                    'nombre': grupo.nombre,
                    'titualr': grupo.usuarioTitular,
                    'ruta': grupo.ruta.nombre_ruta
                })
            return grupos
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando grupos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de grupos.")
