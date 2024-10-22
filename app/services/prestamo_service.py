from app.models import Prestamo, TipoPrestamo
from app.services import usuario_service
from app import db
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError

class PrestamoService:
    def __init__(self, prestamo_id=None):
        self.prestamo_id = prestamo_id
   
    @staticmethod
    def __check_override_monto_prestamo(monto_prestamo, user):
        user_role = usuario_service.UsuarioService.get_user_rol_by_user_id(user.id)
        if monto_prestamo<=5000:
            return True
        elif monto_prestamo>=5000 and user_role == 6:
            return True
        else:
            return False
            
    def create_prestamo(self, data, user):
        monto_prestamo = data['monto_prestamo']
        if self.__check_override_monto_prestamo(monto_prestamo, user):
            try:
                
                new_prestamo = Prestamo(
                    cliente_id=data['cliente_id'],
                    fecha_inicio=data['fecha_inicio'],
                    monto_prestamo=data['monto_prestamo'],
                    tipo_prestamo_id=data['tipo_prestamo_id'],
                    aval_id=data['aval_id']
                )
                db.session.add(new_prestamo)
                db.session.commit()
                return new_prestamo
            except SQLAlchemyError as e:
                db.session.rollback()
                app.logger.error(f"Error creando préstamo: {str(e)}")
                raise ValueError("No se pudo crear el préstamo.")
        else:
            raise ValueError("No tienes permisos para realizar agregar un prestamo mayor a 5000.")
                

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
            lista_obj_prestamos = Prestamo.query.all()
            prestamos = []
            for prestamo in lista_obj_prestamos:
                prestamos.append({
                    'prestamo_id': prestamo.prestamo_id,
                    'cliente_id': prestamo.titular.cliente_id,
                    'cliente_nombre': prestamo.titular.nombre + " " + prestamo.titular.apellido_paterno + " " + prestamo.titular.apellido_materno,  
                    'fecha_inicio': prestamo.fecha_inicio,
                    'monto_prestamo': prestamo.monto_prestamo,
                    'tipo_prestamo_id': prestamo.tipo_prestamo_id,
                    'tipo_prestamo_nombre': prestamo.tipo_prestamo.nombre,  
                    'aval_id': prestamo.aval.cliente_id,
                    'aval_nombre': prestamo.aval.nombre + " " + prestamo.aval.apellido_paterno + " " + prestamo.aval.apellido_materno 
                })
            return prestamos
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando préstamos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de préstamos.")
    def list_tipos_prestamo(self):
        try:
            tipos_prestamo = TipoPrestamo.query.all()
            tipos = []
            for tipo in tipos_prestamo:
                tipos.append({
                    'tipo_prestamo_id': tipo.tipo_prestamo_id,
                    'nombre': tipo.nombre
                })
            return tipos
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando tipos de préstamo: {str(e)}")
            raise ValueError("No se pudo obtener la lista de tipos de préstamo.")
