from app.models import Grupo, Ruta, Usuario
from app import db
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError

class GrupoService:
    def __init__(self, grupo_id=None):
        self.grupo_id = grupo_id

    def create_grupo(self, data):
        try:
            # Check if ruta and usuario exist before creating the grupo
            ruta_to_insert = Ruta.query.get(data['ruta_id'])
            if not ruta_to_insert:
                raise ValueError(f"No se encontró la ruta con ID: {data['ruta_id']}")
            usuario_to_insert = Usuario.query.get(data['usuario_id_titular'])
            if not usuario_to_insert:
                raise ValueError(f"No se encontró el usuario con ID: {data['usuario_id_titular']}")
            
            new_grupo = Grupo(
                nombre_grupo=data['nombre_grupo'],
                ruta_id=data['ruta_id'],
                usuario_id_titular=data['usuario_id_titular']
            )
            new_grupo.validar_titular()
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
            
            grupo.nombre_grupo = data.get('nombre_grupo', grupo.nombre_grupo)
            grupo.usuario_id_titular = data.get('usuario_id_titular', grupo.usuario_id_titular)
            grupo.ruta_id = data.get('ruta_id', grupo.ruta_id)
            grupo.validar_titular()
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
            
            return lista_obj_grupos
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando grupos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de grupos.")
